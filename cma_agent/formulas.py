import json
from datetime import timedelta

from cma_agent import adaptive, engine

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
    eligible = [CARDS[key] for key in [*scheduled, *(key for key in CARDS if key not in scheduled)]
                if key in CARDS and CARDS[key]["part"] == part and scheduled.get(key, "") <= now]
    return eligible[:10]


def grade(formula_id, correct):
    if formula_id not in CARDS:
        raise KeyError(formula_id)
    c = connect()
    try:
        if not engine.DATABASE_URL:
            c.execute("BEGIN IMMEDIATE")
        lock = " FOR UPDATE" if engine.DATABASE_URL else ""
        c.execute("INSERT INTO formula_state(formula_id,interval_days,streak) VALUES(?,0,0) "
                  "ON CONFLICT(formula_id) DO NOTHING", (formula_id,))
        row = c.execute("SELECT interval_days,streak FROM formula_state WHERE formula_id=?" + lock,
                        (formula_id,)).fetchone()
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
