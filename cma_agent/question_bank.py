"""Question-bank integrity checks and reviewed skill coverage (no database access)."""
from __future__ import annotations

import ast
import json
import math
import operator
import re
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
REVISION = "2026-09-30"
TAXONOMY = json.loads((DATA / "skill_taxonomy.json").read_text(encoding="utf-8"))
PART_DOMAINS = {
    "Part 1": list(TAXONOMY)[:6],
    "Part 2": list(TAXONOMY)[6:],
}
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.Pow: operator.pow}
REVIEW_FIELDS = ("id", "part", "domain", "difficulty", "question", "choices",
                 "answer", "explanation", "calculation", "skills", "numeric_check",
                 "content_revision")


def arithmetic(expression):
    """Evaluate arithmetic literals only; reject names, calls and nonfinite values."""
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            value = visit(node.operand)
            return value if isinstance(node.op, ast.UAdd) else -value
        if isinstance(node, ast.BinOp) and type(node.op) in OPS:
            left, right = visit(node.left), visit(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 20:
                raise ValueError("Exponent outside validation bounds")
            return OPS[type(node.op)](left, right)
        raise ValueError("Only arithmetic literals are permitted")
    if not isinstance(expression, str) or len(expression) > 500:
        raise ValueError("Invalid expression")
    value = visit(ast.parse(expression, mode="eval").body)
    if isinstance(value, complex) or not math.isfinite(value):
        raise ValueError("Nonfinite arithmetic result")
    return value


def stem_key(text):
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def choice_number(text):
    match = re.match(r"^\$?(-?\d[\d,]*(?:\.\d+)?)", text)
    if not match:
        return None
    value = float(match.group(1).replace(",", ""))
    if "%" in text:
        value /= 100
    if "million" in text:
        value *= 1_000_000
    return value


def load_questions(data_dir=DATA):
    """One source loader for API and Streamlit; malformed supplements fail loudly."""
    result = []
    for path in [data_dir / "questions.json", *sorted(data_dir.glob("questions_part1_*.json"))]:
        items = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(items, list):
            raise ValueError(f"{path.name}: expected a list")
        result.extend(items)
    ids = [q["id"] for q in result]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate question IDs across source files")
    return result


def case_questions(cases):
    result = []
    case_ids = set()
    for case in cases:
        if case["id"] in case_ids:
            raise ValueError("Duplicate case ID")
        case_ids.add(case["id"])
        if not case.get("scenario", "").strip() or not case.get("questions"):
            raise ValueError("Case requires scenario and questions")
        for index, item in enumerate(case["questions"], 1):
            result.append({
                **item, "id": f"{case['id']}-Q{index}", "part": case["part"],
                "domain": case["domain"], "difficulty": case.get("difficulty", "Medium"),
                "question": item["q"], "scenario": case["scenario"], "is_case": True,
                "content_revision": case["content_revision"],
            })
    return result


def reviewed_content(q):
    result = {key: q.get(key) for key in REVIEW_FIELDS}
    if q.get("is_case"):
        result["scenario"] = q["scenario"]
    return result


def validate_question(q):
    errors = []
    def require(condition, message):
        if not condition:
            errors.append(f"{q.get('id', '?')}: {message}")
    require(q.get("part") in PART_DOMAINS, "invalid part")
    require(q.get("domain") in PART_DOMAINS.get(q.get("part"), []), "part/domain mismatch")
    require(q.get("difficulty") in {"Easy", "Medium", "Hard"}, "invalid difficulty")
    for key in ("id", "question", "explanation"):
        require(isinstance(q.get(key), str) and bool(q[key].strip()), f"missing {key}")
    choices = q.get("choices", {})
    require(set(choices) == set("ABCD"), "requires four labeled choices")
    require(all(isinstance(v, str) and v.strip() for v in choices.values()), "empty choice")
    require(len({stem_key(str(v)) for v in choices.values()}) == 4, "duplicate choice text")
    require(q.get("answer") in choices, "invalid answer key")
    skills = q.get("skills", [])
    require(bool(skills) and len(skills) == len(set(skills)), "missing/duplicate explicit skills")
    require(all(s in TAXONOMY.get(q.get("domain"), []) for s in skills), "skill/domain mismatch")
    require(q.get("content_revision") == REVISION, "unreviewed content revision")
    require(not re.search(r":\s*(when|in|while|for|under|during|after|before)\b", q.get("question", ""), re.I),
            "corrupt context suffix")
    check = q.get("numeric_check")
    require(bool(check) == bool(q.get("calculation")), "calculation/check mismatch")
    if check:
        try:
            value = arithmetic(check["expression"])
            tolerance = check["tolerance"]
            require(isinstance(tolerance, (int, float)) and 0 <= tolerance <= 0.5,
                    "invalid rounding tolerance")
            values = check["choice_values"]
            require(set(values) == set("ABCD"), "numeric choice map incomplete")
            for label, text in choices.items():
                parsed = choice_number(text)
                if parsed is not None:
                    require(values.get(label) is not None and math.isclose(parsed, values[label], abs_tol=1e-9),
                            f"numeric option metadata disagrees with {label}")
            direction = None
            if check.get("positive_label"):
                direction = check["positive_label"] if value > 0 else check["negative_label"] if value < 0 else "zero"
                actual_labels = {k: (re.search(r"\b(unfavorable|favorable|gain|loss|higher|lower)\b", v).group(1)
                                    if re.search(r"\b(unfavorable|favorable|gain|loss|higher|lower)\b", v) else None)
                                 for k, v in choices.items()}
                require(actual_labels == check["choice_directions"], "direction metadata disagrees with choices")
            comparison = abs(value) if check.get("absolute") else value
            matches = [k for k, v in values.items() if v is not None
                       and math.isclose(v, comparison, rel_tol=1e-9, abs_tol=tolerance)
                       and (direction is None or check["choice_directions"].get(k) == direction)]
            require(matches == [q.get("answer")], f"computed result {value} matches {matches}, key is {q.get('answer')}")
            for equation in q["calculation"].split(";"):
                if "=" in equation:
                    left, right = equation.split("=", 1)
                    expected = float(right.strip().rstrip("%"))
                    if right.strip().endswith("%"):
                        expected /= 100
                    require(math.isclose(arithmetic(left), expected, rel_tol=1e-9, abs_tol=tolerance),
                            "displayed calculation equality is false")
        except (KeyError, TypeError, ValueError, SyntaxError, ZeroDivisionError, OverflowError) as exc:
            errors.append(f"{q.get('id')}: invalid numerical check: {exc}")
    return errors


def coverage(questions):
    rows = []
    for domain, skills in TAXONOMY.items():
        bank = [q for q in questions if q["domain"] == domain and not q.get("is_case")]
        rows.append({"domain": domain, "questions": len(bank), "skills": [
            {"skill": skill, "questions": sum(skill in q["skills"] for q in bank),
             "status": "missing" if not any(skill in q["skills"] for q in bank)
                       else "thin" if sum(skill in q["skills"] for q in bank) < 3 else "represented"}
            for skill in skills]})
    return rows


def near_duplicates(questions):
    """Editorial candidates, not automatic rejections: fresh numerical tasks can be useful."""
    result = []
    for index, left in enumerate(questions):
        for right in questions[index + 1:]:
            if left["domain"] != right["domain"] or left["skills"] != right["skills"]:
                continue
            similarity = SequenceMatcher(None, stem_key(left["question"]), stem_key(right["question"])).ratio()
            if similarity >= 0.80:
                result.append({"left": left["id"], "right": right["id"], "similarity": round(similarity, 3)})
    return result


def validate_bank(questions, cases, audit):
    combined = questions + case_questions(cases)
    errors = [error for q in combined for error in validate_question(q)]
    ids = [q["id"] for q in combined]
    if len(ids) != len(set(ids)):
        errors.append("Duplicate IDs in combined MCQ/case bank")
    seen = {}
    for q in questions:
        key = stem_key(q["question"])
        if key in seen:
            errors.append(f"Duplicate stems: {seen[key]} / {q['id']}")
        seen[key] = q["id"]
    reviewed = audit.get("reviewed", {})
    if set(reviewed) != set(ids):
        errors.append("Audit ledger does not cover every active question")
    for q in combined:
        if reviewed.get(q["id"]) != reviewed_content(q):
            errors.append(f"{q['id']}: content changed since editorial review; update review and revision")
    return errors
