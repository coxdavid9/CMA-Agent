import json

import pytest

from cma_agent import case_drill, engine, timed


def test_source_cases_preserve_legacy_bank_and_hide_model_answers():
    assert len(engine.CASES) == 17
    assert sum(c["part"] == "Part 1" for c in engine.CASES) == 14
    assert sum(len(c["questions"]) for c in engine.CASES) == 34
    assert len(case_drill.CASES) == 12
    assert sum(len(case_drill.public(cid)["questions"]) for cid in case_drill.CASES) == 46
    for cid in case_drill.CASES:
        assert "model_answer" not in json.dumps(case_drill.public(cid))
        assert case_drill.model_answer(cid, 0)


@pytest.mark.parametrize("hits", [9, 10])
def test_gate_boundary_and_case_result(tmp_path, monkeypatch, hits):
    monkeypatch.setattr(engine, "DB", tmp_path / "gate.db")
    bank = [q for q in engine.QUESTIONS if q["part"] == "Part 1" and not q.get("is_case")]
    run = timed.start("Part 1", {q["domain"]: 1 for q in bank})
    assert run["total"] == 20
    for i in range(20):
        q = engine.get_question(run["question"]["id"])
        wrong = next(key for key in q["choices"] if key != q["answer"])
        run = timed.advance(run["id"], q["id"], q["answer"] if i < hits else wrong)
    assert run["score"] == hits
    assert bool(run["gate_case_id"]) == (hits == 10)
    case_id = run["gate_case_id"]
    if case_id:
        scores = [.5] * len(case_drill.public(case_id)["questions"])
        assert case_drill.save(case_id, scores, run["id"]) == {"score": 50}
        assert case_drill.save(case_id, scores, run["id"]) == {"score": 50}
    c = engine.db()
    row = c.execute("SELECT * FROM case_attempts WHERE id=?", (run["id"],)).fetchone()
    assert row["gate_score"] == hits
    assert row["case_id"] == case_id
    assert bool(json.loads(row["sub_results"])) == (hits == 10)
    c.close()
