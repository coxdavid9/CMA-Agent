import json
from pathlib import Path

CASES = json.loads((Path(__file__).resolve().parents[1] / "data" / "cases.json").read_text())
DOMAINS = {
    "External Financial Reporting Decisions",
    "Planning, Budgeting, and Forecasting",
    "Performance Management",
    "Cost Management",
    "Internal Controls",
    "Technology and Analytics",
}

def test_imported_part1_cases_have_valid_answers_and_blueprint_domains():
    cases = [c for c in CASES if c["id"].startswith("PART1-")]
    assert len(cases) == 12
    assert {c["domain"] for c in cases} == DOMAINS
    assert sum(len(c["questions"]) for c in cases) == 26
    for case in cases:
        assert case["part"] == "Part 1"
        assert case["scenario"].strip()
        for q in case["questions"]:
            assert q["answer"] in q["choices"]
            assert len(q["choices"]) == 4
            assert len(set(q["choices"].values())) == 4
            assert q["explanation"].strip()
            assert q["skills"]
