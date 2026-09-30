"""Validate all sources and emit editorial/coverage candidates for review."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cma_agent.question_bank import DATA, load_questions, validate_bank, coverage, near_duplicates

questions = load_questions()
cases = json.loads((DATA / "cases.json").read_text(encoding="utf-8"))
audit = json.loads((DATA / "audit" / "content_review.json").read_text(encoding="utf-8"))
errors = validate_bank(questions, cases, audit)
if errors:
    print("\n".join(errors))
    raise SystemExit(1)
report = {"mcqs": len(questions), "case_questions": sum(len(c["questions"]) for c in cases),
          "coverage": coverage(questions), "near_duplicate_candidates": near_duplicates(questions)}
if "--pairs" in sys.argv:
    print(json.dumps(report["near_duplicate_candidates"]))
elif "--report" in sys.argv:
    print(json.dumps(report, indent=2))
else:
    print(f"PASS: {report['mcqs']} MCQs and {report['case_questions']} case items; all reviewed and validated")
