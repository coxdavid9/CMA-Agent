"""Server-timed practice sets. Answers are revealed only upon finalization."""
import json
import random
import time
import uuid

from cma_agent import engine


def connect():
    c = engine.db()
    c.execute("CREATE TABLE IF NOT EXISTS timed_sets(id TEXT PRIMARY KEY, state TEXT)")
    c.commit()
    return c


def start(part):
    bank = [q for q in engine.QUESTIONS if q["part"] == part and not q.get("is_case")]
    ids = [q["id"] for q in random.sample(bank, 25)]
    set_id = str(uuid.uuid4())
    now = time.time()
    state = {"ids": ids, "deadline": now + 2700, "shown": now, "answers": []}
    c = connect()
    try:
        c.execute("INSERT INTO timed_sets VALUES(?,?)", (set_id, json.dumps(state)))
        c.commit()
    finally:
        c.close()
    return public(set_id, state)


def public(set_id, state):
    result = {"id": set_id, "deadline": state["deadline"], "total": len(state["ids"]),
              "index": len(state["answers"])}
    if "results" in state:
        result["results"] = state["results"]
        result["score"] = sum(item["correct"] for item in state["results"])
    else:
        q = engine.get_question(state["ids"][result["index"]])
        result["question"] = {key: q[key] for key in ("id", "question", "choices", "domain")}
    return result


def advance(set_id, question_id=None, selected=None, finish=False):
    c = connect()
    try:
        if not engine.DATABASE_URL:
            c.execute("BEGIN IMMEDIATE")
        suffix = " FOR UPDATE" if engine.DATABASE_URL else ""
        row = c.execute("SELECT state FROM timed_sets WHERE id=?" + suffix, (set_id,)).fetchone()
        if not row:
            raise KeyError(set_id)
        state = json.loads(row["state"])
        if "results" in state:
            return public(set_id, state)
        now = time.time()
        index = len(state["answers"])
        if not finish and now < state["deadline"] and question_id == state["ids"][index]:
            q = engine.get_question(question_id)
            if selected not in q["choices"]:
                raise ValueError("Select a valid answer")
            state["answers"].append([selected, round(max(0, now - state["shown"]), 1)])
            state["shown"] = now
        if finish or now >= state["deadline"] or len(state["answers"]) == len(state["ids"]):
            results = []
            for i, qid in enumerate(state["ids"]):
                q = engine.get_question(qid)
                answer, elapsed = state["answers"][i] if i < len(state["answers"]) else ("", None)
                correct, attempt_id = engine.insert_attempt(c, q, answer, 0, set_id, elapsed_seconds=elapsed)
                results.append({"question": q["question"], "choices": q["choices"], "selected": answer,
                                "answer": q["answer"], "explanation": q.get("explanation", ""),
                                "elapsed_seconds": elapsed, "correct": correct, "attempt_id": attempt_id})
            state["results"] = results
        c.execute("UPDATE timed_sets SET state=? WHERE id=?", (json.dumps(state), set_id))
        c.commit()
        return public(set_id, state)
    finally:
        c.close()
