"""Written practice and gate drill case results."""
import json
import uuid
from datetime import datetime

from cma_agent import engine

CASES = {c["id"]: c for c in engine.CASES if c.get("written_practice")}


def ensure_schema(c):
    c.execute("""CREATE TABLE IF NOT EXISTS case_attempts(
        id TEXT PRIMARY KEY, ts TEXT NOT NULL, case_id TEXT,
        gate_score INTEGER, sub_results TEXT NOT NULL)""")


def least_recent(c):
    rows = c.execute("SELECT case_id, MAX(ts) AS last FROM case_attempts "
                     "WHERE case_id IS NOT NULL GROUP BY case_id").fetchall()
    last = {row["case_id"]: row["last"] for row in rows}
    return min(CASES, key=lambda case_id: (last.get(case_id, ""), case_id))


def gate_result(c, run_id, score):
    ensure_schema(c)
    case_id = least_recent(c) if score >= 10 else None
    c.execute("INSERT INTO case_attempts VALUES(?,?,?,?,?)",
              (run_id, datetime.now().isoformat(timespec="microseconds"), case_id, score, "[]"))
    return case_id


def listing():
    return [{key: case[key] for key in ("id", "title", "domain")} for case in CASES.values()]


def public(case_id):
    case = CASES[case_id]
    written = case["written_practice"]
    return {"id": case_id, "title": case["title"], "scenario": written["scenario"],
            "domain": case["domain"], "questions": [q["q"] for q in written["questions"]]}


def model_answer(case_id, index):
    questions = CASES[case_id]["written_practice"]["questions"]
    if not 0 <= index < len(questions):
        raise KeyError(index)
    return questions[index]["model_answer"]


def save(case_id, scores, run_id=None):
    if len(scores) != len(CASES[case_id]["written_practice"]["questions"]) or any(
        score not in (0, .5, 1) for score in scores
    ):
        raise ValueError("Grade every question as Correct, Partial, or Missed")
    c = engine.db()
    try:
        ensure_schema(c)
        payload = json.dumps(scores)
        now = datetime.now().isoformat(timespec="microseconds")
        if run_id:
            row = c.execute("""UPDATE case_attempts SET sub_results=?,ts=?
                WHERE id=? AND case_id=? AND gate_score>=10 AND sub_results='[]' RETURNING id""",
                (payload, now, run_id, case_id)).fetchone()
            if not row:
                row = c.execute("SELECT id FROM case_attempts WHERE id=? AND case_id=? AND sub_results=?",
                                (run_id, case_id, payload)).fetchone()
                if not row:
                    raise ValueError("This gate case is unavailable or already scored")
        else:
            c.execute("INSERT INTO case_attempts VALUES(?,?,?,?,?)",
                      (str(uuid.uuid4()), now, case_id, None, payload))
        c.commit()
    finally:
        c.close()
    return {"score": round(100 * sum(scores) / len(scores), 1)}


def save_mcq(case_id, attempt_ids):
    case = next((item for item in engine.CASES if item["id"] == case_id), None)
    if not case or not case["questions"]:
        raise KeyError(case_id)
    if len(attempt_ids) != len(case["questions"]):
        raise ValueError("Answer every question in the case")
    c = engine.db()
    try:
        ensure_schema(c)
        scores = []
        for index, attempt_id in enumerate(attempt_ids, 1):
            row = c.execute("SELECT correct FROM attempts WHERE id=? AND question_id=?",
                            (attempt_id, f"{case_id}-Q{index}")).fetchone()
            if not row:
                raise ValueError("Attempt does not match the case question")
            scores.append(row["correct"])
        record_id = "mcq:" + ":".join(str(attempt_id) for attempt_id in attempt_ids)
        c.execute("INSERT INTO case_attempts VALUES(?,?,?,?,?) ON CONFLICT(id) DO NOTHING",
                  (record_id, datetime.now().isoformat(timespec="microseconds"), case_id, None, json.dumps(scores)))
        c.commit()
    finally:
        c.close()
    return {"score": round(100 * sum(scores) / len(scores), 1)}
