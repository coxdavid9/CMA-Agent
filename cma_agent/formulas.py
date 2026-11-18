import json
import unicodedata
from datetime import timedelta

from cma_agent import adaptive, engine
from cma_agent.numeric import parse_number, within_tolerance

CARDS = {card["id"]: card for card in json.loads((engine.DATA / "formulas.json").read_text())}


def connect():
    c = engine.db()
    c.execute("""CREATE TABLE IF NOT EXISTS formula_state(
        formula_id TEXT PRIMARY KEY, due_at TEXT, interval_days REAL, streak INTEGER,
        last_correct INTEGER, updated_at TEXT)""")
    c.commit()
    return c


def due(part):
    c = connect()
    try:
        rows = c.execute("SELECT formula_id,due_at FROM formula_state ORDER BY due_at,formula_id").fetchall()
    finally:
        c.close()
    now = adaptive._now().isoformat(timespec="seconds")
    scheduled = {row["formula_id"]: row["due_at"] for row in rows}
    new_cards = sorted(
        (key for key in CARDS if key not in scheduled),
        key=lambda key: CARDS[key].get("type", "reveal") == "reveal",
    )
    eligible = [CARDS[key] for key in [*scheduled, *new_cards]
                if key in CARDS and CARDS[key]["part"] == part and scheduled.get(key, "") <= now]
    return [public_card(card) for card in eligible[:10]]


def public_card(card):
    if card.get("type", "reveal") == "reveal":
        return card
    fields = ("id", "part", "domain", "front", "type", "options", "content_revision")
    return {key: card[key] for key in fields if key in card}


def normalize(response):
    text = unicodedata.normalize("NFKC", response).casefold()
    return "".join(char for char in text if char.isalnum())


def check_answer(card, response):
    kind = card.get("type", "reveal")
    if kind == "numeric":
        value = parse_number(response)
        key = card["answer"]
        tolerance = card.get("tolerance", .01) * abs(key)
        if key == 0 or (abs(key) < 1 and "tolerance_abs" in card):
            tolerance = card.get("tolerance_abs", .01)
        return within_tolerance(value, key, tolerance)
    if kind == "cloze_type":
        normalized = normalize(response)
        if not normalized:
            raise ValueError("Enter the missing part of the formula.")
        return normalized in {normalize(item) for item in card["accept"]}
    if kind == "cloze_pick":
        if response not in card["options"]:
            raise ValueError("Choose one of the listed options.")
        return response == card["answer"]
    raise ValueError("Use the reveal controls for this card.")


def answer(formula_id, response):
    card = CARDS[formula_id]
    correct = check_answer(card, response)
    _schedule(formula_id, correct)
    return {"correct": correct, "back": card["back"], "example": card["example"],
            "allow_override": card["type"] == "cloze_type"}


def grade(formula_id, correct):
    kind = CARDS[formula_id].get("type", "reveal")
    override = kind == "cloze_type" and correct
    if kind != "reveal" and not override:
        raise ValueError("Submit an answer for this card.")
    return _schedule(formula_id, correct, override=override)


def _schedule(formula_id, correct, override=False):
    c = connect()
    try:
        if not engine.DATABASE_URL:
            c.execute("BEGIN IMMEDIATE")
        lock = " FOR UPDATE" if engine.DATABASE_URL else ""
        c.execute("INSERT INTO formula_state(formula_id,interval_days,streak) VALUES(?,0,0) "
                  "ON CONFLICT(formula_id) DO NOTHING", (formula_id,))
        row = c.execute("SELECT interval_days,streak,last_correct FROM formula_state WHERE formula_id=?" + lock,
                        (formula_id,)).fetchone()
        if override and row["last_correct"] != 0:
            raise ValueError("Submit an incorrect typed answer before overriding it.")
        interval, streak = adaptive.review_interval(correct, 1, 0, row["interval_days"], row["streak"])
        now = adaptive._now()
        due_at = (now + timedelta(days=interval)).isoformat(timespec="seconds")
        c.execute("UPDATE formula_state SET due_at=?,interval_days=?,streak=?,last_correct=?,updated_at=? "
                  "WHERE formula_id=?", (due_at, interval, streak, int(correct),
                                         now.isoformat(timespec="seconds"), formula_id))
        c.commit()
        return {"due_at": due_at, "interval_days": interval, "streak": streak}
    finally:
        c.close()
