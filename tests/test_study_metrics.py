from cma_agent import engine, study_metrics, timed


def test_first_score_and_error_profile(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "DB", tmp_path / "test.db")
    q = next(q for q in engine.QUESTIONS if q["part"] == "Part 1" and not q.get("is_case"))
    wrong = next(key for key in q["choices"] if key != q["answer"])
    _, _, miss = engine.grade(q["id"], wrong, elapsed_seconds=110, include_id=True)
    _, _, hit = engine.grade(q["id"], q["answer"], elapsed_seconds=90, include_id=True)
    engine.grade(q["id"], q["answer"])
    assert study_metrics.set_cause(miss, "misread")
    assert not study_metrics.set_cause(hit, "calc")
    data = study_metrics.profile("Part 1")
    assert data["first_attempt_accuracy"] == 0
    assert data["repeat_accuracy"] == 100
    assert data["total_attempts"] == 3
    assert data["first_attempt_count"] == 1
    assert data["pace"][0]["average_seconds"] == 100
    assert data["errors"] == [{"domain": q["domain"], "error_cause": "misread", "count": 1}]


def test_timed_expiry_and_idempotent_results(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "DB", tmp_path / "test.db")
    monkeypatch.setattr(timed.time, "time", lambda: 1000)
    run = timed.start("Part 1")
    assert set(run["question"]) == {"id", "question", "choices", "domain"}
    q = engine.get_question(run["question"]["id"])
    next_run = timed.advance(run["id"], q["id"], q["answer"])
    assert next_run["index"] == 1 and "results" not in next_run
    monkeypatch.setattr(timed.time, "time", lambda: 3700)
    done = timed.advance(run["id"])
    assert done["score"] == 1
    assert len(done["results"]) == 25
    assert done["results"][1]["selected"] == ""
    assert timed.advance(run["id"], finish=True) == done
    assert study_metrics.profile("Part 1")["total_attempts"] == 25
