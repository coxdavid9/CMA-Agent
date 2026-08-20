import json, os, random, sqlite3
from pathlib import Path
from datetime import date, datetime

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
QUESTIONS = json.loads((DATA / "questions.json").read_text(encoding="utf-8"))
CASES = json.loads((DATA / "cases.json").read_text(encoding="utf-8"))
DB = Path(os.getenv("CMA_DB_PATH", str(DATA / "study.db")))


def db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS attempts(
      id INTEGER PRIMARY KEY, ts TEXT, question_id TEXT, part TEXT,
      domain TEXT, difficulty TEXT, selected TEXT, correct INTEGER, confidence INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS goals(
      id INTEGER PRIMARY KEY CHECK(id=1), target_date TEXT, part TEXT, daily_minutes INTEGER
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS preferences(
      id INTEGER PRIMARY KEY CHECK(id=1), part TEXT, difficulty TEXT, domain TEXT
    )""")
    c.commit()
    return c


def get_preferences():
    c = db()
    r = c.execute("SELECT part, difficulty, domain FROM preferences WHERE id=1").fetchone()
    result = dict(r) if r else {"part": "Both", "difficulty": "All", "domain": "All"}
    c.close()
    return result


def save_preferences(part, difficulty, domain):
    c = db()
    c.execute("INSERT OR REPLACE INTO preferences(id, part, difficulty, domain) VALUES(1,?,?,?)", (part, difficulty, domain))
    c.commit()
    c.close()


def domains(part="Both"):
    p1 = ["External Financial Reporting Decisions", "Planning, Budgeting, and Forecasting", "Performance Management", "Cost Management", "Internal Controls", "Technology and Analytics"]
    p2 = ["Financial Statement Analysis", "Corporate Finance", "Business Decision Analysis", "Enterprise Risk Management", "Capital Investment Decisions", "Professional Ethics"]
    return p1 if part == "Part 1" else p2 if part == "Part 2" else p1 + p2


def _question_history(conn):
    rows = conn.execute("SELECT question_id, COUNT(*) AS attempts, SUM(correct) AS correct, MAX(id) AS last_id FROM attempts GROUP BY question_id").fetchall()
    return {r["question_id"]: dict(r) for r in rows}


def question_status(question_id, conn=None):
    owns = conn is None; conn = conn or db()
    rows = conn.execute("SELECT correct FROM attempts WHERE question_id=? ORDER BY id DESC LIMIT 5", (question_id,)).fetchall()
    if owns: conn.close()
    if not rows: return "New"
    results = [int(r["correct"]) for r in rows]; attempts = len(results)
    if attempts >= 3 and sum(results[:3]) == 3: return "Mastered"
    if results[0] == 0 or sum(results) / attempts < 0.67: return "Weak"
    return "Learning"


def topic_status(domain, conn=None):
    owns = conn is None; conn = conn or db()
    rows = conn.execute("SELECT correct FROM attempts WHERE domain=? ORDER BY id DESC LIMIT 10", (domain,)).fetchall()
    if owns: conn.close()
    if not rows: return "New"
    results = [int(r["correct"]) for r in rows]
    if len(results) >= 5 and sum(results[:5]) / 5 >= 0.85: return "Mastered"
    if results[0] == 0 or sum(results) / len(results) < 0.70: return "Weak"
    return "Learning"


def choose_question(part="Both", domain="All", difficulty="All", exclude=None, review_mode=False):
    exclude = set(exclude or []); conn = db()
    filtered = [q for q in QUESTIONS if q["id"] not in exclude and (part == "Both" or q["part"] == part) and (domain == "All" or q["domain"] == domain) and (difficulty == "All" or q["difficulty"] == difficulty)]
    if not filtered: filtered = [q for q in QUESTIONS if q["id"] not in exclude and (part == "Both" or q["part"] == part)]
    history = _question_history(conn); buckets = {"New": [], "Learning": [], "Weak": [], "Mastered": []}
    for q in filtered: buckets[question_status(q["id"], conn)].append(q)
    pool = (buckets["Weak"] or buckets["Learning"] or buckets["New"] or buckets["Mastered"] or filtered) if review_mode else (buckets["New"] or buckets["Weak"] or buckets["Learning"] or buckets["Mastered"] or filtered)
    domain_rows = conn.execute("SELECT domain, AVG(correct) AS pct, COUNT(*) AS n FROM attempts GROUP BY domain").fetchall()
    domain_scores = {r["domain"]: (float(r["pct"]), int(r["n"])) for r in domain_rows}; weighted = []
    for q in pool:
        pct, _ = domain_scores.get(q["domain"], (0.5, 0)); attempts = int(history.get(q["id"], {}).get("attempts", 0)); status = question_status(q["id"], conn)
        weight = {"New": 5.0, "Weak": 4.0, "Learning": 2.0, "Mastered": 0.25}[status]; weight *= max(0.5, 1.5 - pct); weight *= 1.0 / (1.0 + attempts * 0.15)
        weighted.extend([q] * max(1, int(weight * 10)))
    chosen = random.choice(weighted or pool); conn.close(); return chosen


def choose_followup(question_id, selected, part="Both", difficulty="All"):
    source = next(q for q in QUESTIONS if q["id"] == question_id)
    candidates = [q for q in QUESTIONS if q["id"] != question_id and q["part"] == source["part"] and q["domain"] == source["domain"] and (difficulty == "All" or q["difficulty"] == difficulty)]
    if not candidates: candidates = [q for q in QUESTIONS if q["id"] != question_id and q["part"] == source["part"] and (difficulty == "All" or q["difficulty"] == difficulty)]
    if not candidates: return choose_question(part, "All", difficulty, exclude=[question_id], review_mode=True)
    conn = db(); history = _question_history(conn); scored = []
    for q in candidates:
        h = history.get(q["id"], {}); attempts = int(h.get("attempts", 0)); correct = int(h.get("correct", 0)); score = 10 if attempts == 0 else 7 if correct / max(1, attempts) < 0.67 else 2
        scored.append((score + random.random(), q))
    conn.close(); return max(scored, key=lambda x: x[0])[1]


def learning_feedback(question_id, selected, confidence):
    q = next(q for q in QUESTIONS if q["id"] == question_id); correct = selected.upper() == q["answer"]; confidence = int(confidence or 0)
    if correct and confidence <= 2: diagnosis, advice = "Correct, but fragile", "You got it right, but low confidence suggests this concept needs another recall check."
    elif correct: diagnosis, advice = "Solid understanding", "You appear comfortable with this concept. We can spend less time here and move to weaker areas."
    elif confidence >= 4: diagnosis, advice = "Likely concept/application gap", "You were confident but missed it. That usually means the rule or its application needs attention."
    else: diagnosis, advice = "Likely knowledge gap", "Low confidence plus an incorrect answer suggests this is a good candidate for a short concept review."
    return {"correct": correct, "diagnosis": diagnosis, "advice": advice, "takeaway": q.get("explanation") or "Review the explanation and identify the rule that determines the correct answer.", "correct_answer": q["answer"], "explanation": q.get("explanation", ""), "calculation": q.get("calculation")}


def learning_snapshot(domain="All"):
    c = db(); where = "" if domain == "All" else "WHERE domain=?"; args = () if domain == "All" else (domain,)
    rows = c.execute(f"SELECT question_id, correct, confidence, domain FROM attempts {where} ORDER BY id DESC LIMIT 50", args).fetchall(); weak = []; fragile = []
    for d in domains("Both"):
        drows = [r for r in rows if r["domain"] == d]
        if not drows: continue
        pct = sum(int(r["correct"]) for r in drows) / len(drows); low_conf_correct = sum(1 for r in drows if int(r["correct"]) == 1 and int(r["confidence"] or 0) <= 2)
        if pct < 0.70: weak.append((pct, d))
        if low_conf_correct >= 2: fragile.append((low_conf_correct, d))
    recent_misses = [dict(r) for r in rows if int(r["correct"]) == 0][:5]; c.close(); weak.sort(); fragile.sort(reverse=True)
    return {"weak_domains": [d for _, d in weak[:3]], "fragile_domains": [d for _, d in fragile[:3]], "recent_misses": recent_misses}


def grade(question_id, selected, confidence=0):
    q = next(q for q in QUESTIONS if q["id"] == question_id); correct = int(selected.upper() == q["answer"]); c = db()
    c.execute("INSERT INTO attempts (ts, question_id, part, domain, difficulty, selected, correct, confidence) VALUES(?,?,?,?,?,?,?,?)", (datetime.now().isoformat(timespec="seconds"), question_id, q["part"], q["domain"], q["difficulty"], selected.upper(), correct, int(confidence or 0)))
    c.commit(); c.close(); return correct, q


def stats():
    c = db(); n = c.execute("SELECT COUNT(*) n FROM attempts").fetchone()["n"]; k = c.execute("SELECT COALESCE(SUM(correct),0) n FROM attempts").fetchone()["n"]
    rows = c.execute("SELECT part, domain, COUNT(*) n, SUM(correct) correct, ROUND(AVG(correct)*100,1) pct FROM attempts GROUP BY part, domain").fetchall(); mastery = [{"domain": d, "status": topic_status(d, c)} for d in domains("Both")]
    question_counts = {"New": 0, "Learning": 0, "Weak": 0, "Mastered": 0}
    for q in QUESTIONS: question_counts[question_status(q["id"], c)] += 1
    result = {"attempted": n, "correct": k, "accuracy": round(k / n * 100, 1) if n else 0, "by_domain": [dict(r) for r in rows], "mastery": mastery, "question_status_counts": question_counts, "question_bank_size": len(QUESTIONS)}; c.close(); return result


def recent(limit=25):
    c = db(); rows = c.execute("SELECT * FROM attempts ORDER BY id DESC LIMIT ?", (limit,)).fetchall(); result = [dict(r) for r in rows]; c.close(); return result


def save_goal(target_date, part, daily_minutes):
    c = db(); c.execute("INSERT OR REPLACE INTO goals VALUES(1,?,?,?)", (target_date, part, daily_minutes)); c.commit(); c.close()


def goal():
    c = db(); r = c.execute("SELECT * FROM goals WHERE id=1").fetchone(); result = dict(r) if r else None; c.close(); return result


def plan():
    g = goal()
    if not g: return {"message": "Set an exam target date first."}
    s = stats(); days = max(1, (date.fromisoformat(g["target_date"]) - date.today()).days); allowed = domains(g["part"]); weak = [r["domain"] for r in sorted(s["by_domain"], key=lambda x: x["pct"]) if r["domain"] in allowed]; focus = weak[:3] or allowed[:3]; m = g["daily_minutes"]
    return {"days_remaining": days, "daily_minutes": m, "part": g["part"], "focus_topics": focus, "session": [f"{max(5, m//3)} min concept review", f"{max(10, m//2)} min adaptive practice", f"{max(5, m//6)} min error review"]}


def reset():
    c = db(); c.execute("DELETE FROM attempts"); c.commit(); c.close()
