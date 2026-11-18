from pathlib import Path

import pytest

from cma_agent import engine, formulas


@pytest.mark.parametrize("response,expected", [
    ("$ 1,000.00 %", True), ("1,010", True), ("990", True),
    ("1009.999", True), ("1010.001", False), ("989.999", False),
])
def test_numeric_relative_tolerance(response, expected):
    assert formulas.check_answer({"type":"numeric","answer":1000}, response) is expected


@pytest.mark.parametrize("key,response,tolerance,expected", [
    (0, "0.02", .02, True), (0, "0.0201", .02, False),
    (.001, ".002", .001, True), (.001, ".0021", .001, False),
])
def test_absolute_tolerance(key, response, tolerance, expected):
    card = {"type":"numeric","answer":key,"tolerance_abs":tolerance}
    assert formulas.check_answer(card, response) is expected


def test_cloze_normalization():
    card = {"type":"cloze_type","accept":["actual price","actual price per unit"]}
    assert formulas.check_answer(card, " Actual PRICE-per unit! ")
    assert formulas.check_answer(card, "ACTUAL PRICE")
    assert not formulas.check_answer(card, "standard price")


def test_due_answer_and_override(tmp_path, monkeypatch):
    (Path(__file__).parents[1] / "frontend/dist").mkdir(exist_ok=True)
    from fastapi.testclient import TestClient
    from api import app

    monkeypatch.setattr(engine, "DB", tmp_path / "active.db")
    client = TestClient(app)
    cards = client.get("/api/formulas/due?limit=10").json()
    assert len(cards) == 10
    assert all(card["type"] != "reveal" for card in cards)
    for card in cards:
        assert not {"answer", "accept", "back", "example"} & card.keys()
        if card["type"] == "cloze_pick":
            assert len(set(card["options"])) == 4
            assert card["options"][0] != formulas.CARDS[card["id"]]["answer"]
    typed = next(card for card in cards if card["type"] == "cloze_type")
    pick = next(card for card in cards if card["type"] == "cloze_pick")
    missed = client.post("/api/formulas/answer", json={"formula_id":typed["id"],"response":"wrong"}).json()
    assert missed == {"correct":False,"allow_override":True,"back":formulas.CARDS[typed["id"]]["back"],
                      "example":formulas.CARDS[typed["id"]]["example"]}
    hit = client.post("/api/formulas/answer", json={"formula_id":pick["id"],
                      "response":formulas.CARDS[pick["id"]]["answer"]}).json()
    assert hit["correct"] and not hit["allow_override"]
    c = engine.db()
    times = {r["formula_id"]:r["due_at"] for r in c.execute("SELECT formula_id,due_at FROM formula_state").fetchall()}
    c.close()
    assert times[typed["id"]] < times[pick["id"]]
    payload = {"formula_id":typed["id"],"correct":True}
    assert client.post("/api/formulas/grade",json=payload).json()["streak"] == 1
    assert client.post("/api/formulas/grade",json=payload).status_code == 422
