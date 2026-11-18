"""Operator-only, idempotent reset of personal study progress."""
import json
import os

from cma_agent import engine

HISTORY_TABLES = (
    "attempts", "review_state", "skill_attempts", "lesson_runs",
    "formula_state", "formula_attempts", "case_attempts", "timed_sets", "session_state",
)


def reset_once(reset_id):
    c = engine.db()
    try:
        if engine.DATABASE_URL:
            c.execute("SELECT pg_advisory_xact_lock(673516300)")
            rows = c.execute("SELECT tablename AS name FROM pg_tables WHERE schemaname=current_schema()").fetchall()
        else:
            c.execute("BEGIN IMMEDIATE")
            rows = c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        present = {row["name"] for row in rows}
        c.execute("""CREATE TABLE IF NOT EXISTS study_history_resets(
            reset_id TEXT PRIMARY KEY, archive TEXT NOT NULL)""")
        if c.execute("SELECT reset_id FROM study_history_resets WHERE reset_id=?", (reset_id,)).fetchone():
            return None

        tables = [table for table in HISTORY_TABLES if table in present]
        if engine.DATABASE_URL:
            c.execute("LOCK TABLE " + ", ".join([*tables, "preferences"]) + " IN ACCESS EXCLUSIVE MODE")
        archive = {table: [dict(row) for row in c.execute(f"SELECT * FROM {table}").fetchall()]
                   for table in tables}
        c.execute("INSERT INTO study_history_resets VALUES(?,?)",
                  (reset_id, json.dumps(archive, default=str)))
        for table in tables:
            c.execute(f"DELETE FROM {table}")
        c.execute("UPDATE preferences SET resume_question_id=NULL")
        c.commit()
        return {table: len(rows) for table, rows in archive.items()}
    finally:
        c.close()


if __name__ == "__main__":
    reset_id = os.environ.get("CMA_HISTORY_RESET_ID")
    if reset_id:
        counts = reset_once(reset_id)
        print("CMA history reset counts:", counts, flush=True)
