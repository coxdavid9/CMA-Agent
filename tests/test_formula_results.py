from pathlib import Path

from cma_agent import engine, formulas


def test_batches_keep_due_reviews_first_and_exclude_served_cards(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "DB", tmp_path / "batches.db")
    c = formulas.connect()
    c.execute("INSERT INTO formula_state(formula_id,due_at,streak) VALUES(?,?,?)",
              ("FORM-06", "2000-01-01", 1))
    c.commit()
    c.close()
    first = formulas.due("Part 1", limit=2)
    assert [card["id"] for card in first] == ["FORM-06", "FORM-42"]
    served = [card["id"] for card in first]
    second = formulas.due("Part 1", limit=2, exclude=served)
    assert [card["id"] for card in second] == ["FORM-43", "FORM-44"]
    assert len(formulas.due("Part 1")) == 50


def test_attempt_sources_and_stats_endpoint(tmp_path, monkeypatch):
    (Path(__file__).parents[1] / "frontend/dist").mkdir(exist_ok=True)
    from fastapi.testclient import TestClient
    from api import app

    monkeypatch.setattr(engine, "DB", tmp_path / "results.db")
    client = TestClient(app)
    assert client.get("/api/formulas/stats").json()["accuracy"] is None
    assert len(client.get("/api/formulas/due").json()) == 50
    batch = client.get("/api/formulas/due", params=[("limit", 2), ("exclude", "FORM-42")]).json()
    assert [card["id"] for card in batch] == ["FORM-43", "FORM-44"]

    formulas.answer("FORM-42", "wrong")
    formulas.grade("FORM-42", True)
    formulas.answer("FORM-43", "200")
    formulas.grade("FORM-06", True)
    formulas.grade("FORM-01", False)  # Part 2
    c = formulas.connect()
    rows = c.execute("SELECT formula_id,correct,source FROM formula_attempts ORDER BY id").fetchall()
    assert [tuple(row) for row in rows] == [
        ("FORM-42", 0, "answer"), ("FORM-42", 1, "override"),
        ("FORM-43", 1, "answer"), ("FORM-06", 1, "self"), ("FORM-01", 0, "self"),
    ]
    c.execute("UPDATE formula_state SET due_at=?, streak=3 WHERE formula_id=?",
              ("2000-01-01", "FORM-06"))
    c.commit()
    c.close()

    stats = client.get("/api/formulas/stats?part=Part%201").json()
    assert stats["total_attempts"] == 4
    assert stats["accuracy"] == 75
    assert (stats["cards_seen"],stats["total_cards"],stats["due_now"],stats["mastered"]) == (3,50,1,1)
    assert stats["by_type"]["cloze_type"] == {"attempts":2,"correct":1,"accuracy":50}
    assert stats["by_type"]["numeric"] == {"attempts":1,"correct":1,"accuracy":100}
    assert stats["by_type"]["reveal"] == {"attempts":1,"correct":1,"accuracy":100}
    assert stats["by_type"]["cloze_pick"]["accuracy"] is None


def test_reset_archives_progress_once_and_preserves_settings(tmp_path, monkeypatch):
    from cma_agent.reset_history import reset_once

    monkeypatch.setattr(engine, "DB", tmp_path / "reset.db")
    engine.save_preferences("Part 2", "All", "All")
    engine.save_resume_question("resume-test")
    formulas.grade("FORM-06", False)
    assert reset_once("test")["formula_attempts"] == 1
    assert formulas.stats("Part 1")["total_attempts"] == 0
    assert engine.get_preferences()["part"] == "Part 2"
    assert engine.get_preferences()["resume_question_id"] is None
    formulas.grade("FORM-06", True)
    assert reset_once("test") is None
    assert formulas.stats("Part 1")["total_attempts"] == 1


def test_extra_practice_can_restart_when_all_cards_are_scheduled(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "DB", tmp_path / "restart.db")
    part = "Part 1"
    c = formulas.connect()
    for key, card in formulas.CARDS.items():
        if card["part"] == part:
            c.execute("INSERT INTO formula_state(formula_id,due_at) VALUES(?,?)",
                      (key, "2099-01-01"))
    c.commit()
    c.close()
    assert formulas.due(part) == []
    batch = formulas.due(part, include_future=True)
    assert len(batch) == 50
    assert formulas.due(part, include_future=True, exclude=[card["id"] for card in batch]) == []
