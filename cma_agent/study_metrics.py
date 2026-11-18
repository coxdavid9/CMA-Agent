from cma_agent import engine

CAUSES = ("concept", "formula", "calc", "misread", "time", "unknown")


def first_attempts(part, rows):
    bank = {q["id"] for q in engine.QUESTIONS if q["part"] == part and not q.get("is_case")}
    first, repeats = {}, []
    for row in rows:
        if row["question_id"] in bank:
            if row["question_id"] in first:
                repeats.append(row)
            else:
                first[row["question_id"]] = row
    return bank, first, repeats


def profile(part):
    c = engine.db()
    try:
        rows = c.execute("SELECT * FROM attempts WHERE part=? ORDER BY ts,id", (part,)).fetchall()
        bank, first, repeats = first_attempts(part, rows)
        def accuracy(items):
            return round(100 * sum(row["correct"] for row in items) / len(items), 1) if items else None

        errors = c.execute("""SELECT domain,error_cause,COUNT(*) AS count FROM attempts
            WHERE part=? AND correct=0 AND error_cause IS NOT NULL
            GROUP BY domain,error_cause ORDER BY domain,error_cause""", (part,)).fetchall()
        pace = c.execute("""SELECT domain,AVG(elapsed_seconds) AS average_seconds,COUNT(*) AS count
            FROM attempts WHERE part=? AND elapsed_seconds IS NOT NULL
            GROUP BY domain ORDER BY domain""", (part,)).fetchall()
    finally:
        c.close()
    return {"first_attempt_accuracy": accuracy(list(first.values())), "first_attempt_count": len(first),
            "repeat_accuracy": accuracy(repeats), "fresh_remaining": len(bank - first.keys()),
            "total_attempts": len(rows), "overall_accuracy": accuracy(rows),
            "errors": [dict(row) for row in errors], "pace": [dict(row) for row in pace]}


def set_cause(attempt_id, cause):
    c = engine.db()
    try:
        row = c.execute("UPDATE attempts SET error_cause=? WHERE id=? AND correct=0 RETURNING id",
                        (cause, attempt_id)).fetchone()
        c.commit()
        return row is not None
    finally:
        c.close()
