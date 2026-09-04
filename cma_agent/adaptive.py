from datetime import datetime, timedelta
import random
import re

import cma_agent.engine as engine


def _now():
    return datetime.now()


def ensure_schema(conn):
    conn.execute(
        "CREATE TABLE IF NOT EXISTS review_state("
        "question_id TEXT PRIMARY KEY,"
        "due_at TEXT,"
        "interval_days REAL,"
        "streak INTEGER,"
        "last_correct INTEGER,"
        "last_confidence INTEGER,"
        "updated_at TEXT)"
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_review_due ON review_state(due_at)")
    conn.commit()


def record_result(question_id, correct, confidence):
    conn = engine.db()
    ensure_schema(conn)
    row = conn.execute("SELECT interval_days,streak FROM review_state WHERE question_id=?", (question_id,)).fetchone()
    previous_interval = float(row["interval_days"] or 0) if row else 0
    previous_streak = int(row["streak"] or 0) if row else 0
    now = _now()

    if not correct:
        interval = 0.25 if previous_interval == 0 else 0.5
        streak = 0
        due = now + timedelta(days=interval)
    elif int(confidence or 0) <= 1:
        interval = 1 if previous_interval == 0 else min(max(previous_interval * 1.5, 1), 7)
        streak = previous_streak + 1
        due = now + timedelta(days=interval)
    elif int(confidence or 0) == 2:
        interval = 3 if previous_interval == 0 else min(max(previous_interval * 2, 3), 21)
        streak = previous_streak + 1
        due = now + timedelta(days=interval)
    else:
        interval = 7 if previous_interval == 0 else min(max(previous_interval * 2.5, 7), 45)
        streak = previous_streak + 1
        due = now + timedelta(days=interval)

    conn.execute(
        "INSERT INTO review_state(question_id,due_at,interval_days,streak,last_correct,last_confidence,updated_at) "
        "VALUES(?,?,?,?,?,?,?) ON CONFLICT(question_id) DO UPDATE SET due_at=EXCLUDED.due_at,"
        "interval_days=EXCLUDED.interval_days,streak=EXCLUDED.streak,last_correct=EXCLUDED.last_correct,"
        "last_confidence=EXCLUDED.last_confidence,updated_at=EXCLUDED.updated_at",
        (question_id, due.isoformat(timespec="seconds"), interval, streak, int(bool(correct)), int(confidence or 0), now.isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def _filtered_questions(part, domain, difficulty, exclude):
    excluded = set(exclude or [])
    return [q for q in engine.QUESTIONS if q["id"] not in excluded
            and (part == "Both" or q["part"] == part)
            and (domain == "All" or q["domain"] == domain)
            and (difficulty == "All" or q["difficulty"] == difficulty)]


def _mastery_status(results):
    """Conservative question-level mastery status."""
    if not results:
        return "New"
    attempts = len(results)
    correct = [int(r["correct"]) for r in results]
    confidence = [int(r["confidence"] or 0) for r in results]
    if attempts < 3:
        return "Weak" if correct[0] == 0 else "Learning"
    last_five = correct[:5]
    last_five_conf = confidence[:5]
    accuracy = sum(last_five) / len(last_five)
    if len(last_five) >= 5 and all(last_five) and sum(c >= 2 for c in last_five_conf) >= 3:
        return "Mastered"
    if accuracy < 0.67 or (correct[0] == 0 and len(last_five) >= 3 and accuracy < 0.75):
        return "Weak"
    return "Learning"


def _question_statuses(conn):
    rows = conn.execute("SELECT question_id,correct,confidence FROM attempts ORDER BY id DESC").fetchall()
    recent = {}
    for row in rows:
        qid = row["question_id"]
        bucket = recent.setdefault(qid, [])
        if len(bucket) < 5:
            bucket.append({"correct": int(row["correct"]), "confidence": int(row["confidence"] or 0)})
    return {qid: _mastery_status(results) for qid, results in recent.items()}


def _topic_mastery_status(results):
    """Conservative domain-level status using both accuracy and confidence."""
    if not results:
        return "New"
    correct = [int(r["correct"]) for r in results]
    confidence = [int(r["confidence"] or 0) for r in results]
    attempts = len(correct)
    if attempts < 3:
        return "Weak" if correct[0] == 0 else "Learning"
    recent = correct[:10]
    recent_accuracy = sum(recent) / len(recent)
    last_five_accuracy = sum(correct[:5]) / min(5, attempts)
    avg_conf = sum(confidence[:min(10, attempts)]) / min(10, attempts)
    if attempts >= 8 and recent_accuracy >= 0.85 and last_five_accuracy >= 0.80 and avg_conf >= 2.0:
        return "Mastered"
    if recent_accuracy < 0.67 or (correct[0] == 0 and recent_accuracy < 0.75):
        return "Weak"
    return "Learning"


def mastery_by_domain(part="Both", domain="All"):
    allowed_questions = _filtered_questions(part, domain, "All", set())
    allowed_domains = {q["domain"] for q in allowed_questions}
    conn = engine.db()
    rows = conn.execute("SELECT domain,correct,confidence FROM attempts ORDER BY id DESC").fetchall()
    conn.close()
    grouped = {d: [] for d in allowed_domains}
    for row in rows:
        d = row["domain"]
        if d in grouped and len(grouped[d]) < 10:
            grouped[d].append({"correct": int(row["correct"]), "confidence": int(row["confidence"] or 0)})
    result = []
    for d, values in grouped.items():
        if not values:
            continue
        correct = [v["correct"] for v in values]
        result.append({"domain": d, "status": _topic_mastery_status(values), "attempts": len(values), "accuracy": round(sum(correct) / len(correct) * 100, 1)})
    return sorted(result, key=lambda x: (x["status"] != "Weak", x["accuracy"]))


def choose_question(part="Both", domain="All", difficulty="All", exclude=None):
    candidates = _filtered_questions(part, domain, difficulty, exclude)
    if not candidates:
        return engine.choose_question(part, domain, difficulty, exclude=exclude)
    conn = engine.db()
    ensure_schema(conn)
    now = _now().isoformat(timespec="seconds")
    rows = conn.execute("SELECT question_id,due_at,last_correct,last_confidence,streak FROM review_state WHERE due_at<=?", (now,)).fetchall()
    due = {r["question_id"]: dict(r) for r in rows}
    statuses = _question_statuses(conn)
    conn.close()
    due_candidates = [q for q in candidates if q["id"] in due]
    if due_candidates:
        def score(q):
            r = due[q["id"]]
            urgency = 30 if int(r["last_correct"] or 0) == 0 else 20 if int(r["last_confidence"] or 0) == 1 else 10
            return urgency + min(int(r["streak"] or 0), 10) + random.random()
        return max(due_candidates, key=score)
    by_status = {"New": [], "Weak": [], "Learning": [], "Mastered": []}
    for q in candidates:
        by_status[statuses.get(q["id"], "New")].append(q)
    pool = by_status["New"] or by_status["Weak"] or by_status["Learning"] or by_status["Mastered"] or candidates
    return random.choice(pool)


_STOPWORDS = {"a","an","and","are","as","at","be","by","for","from","has","have","how","if","in","is","it","most","of","on","or","that","the","their","this","to","was","were","what","when","which","with","would","will","than","then","each","per","generally","primarily","directly","likely","company","manager","current","actual","budgeted","standard","appropriate"}
_HIGH_VALUE_PHRASES = (
    "contribution margin", "sales volume", "volume variance", "sales mix", "price variance", "quantity variance",
    "efficiency variance", "rate variance", "flexible budget", "static budget", "break even", "relevant cost",
    "sunk cost", "opportunity cost", "capital budgeting", "net present value", "internal control",
    "segregation duties", "working capital", "current ratio", "debt to assets", "return on investment",
    "residual income", "transfer price", "standard cost", "activity based costing", "absorption costing",
    "variable costing", "cash flow", "descriptive analytics", "diagnostic analytics", "predictive analytics",
    "prescriptive analytics"
)


def _concept_tokens(q):
    """Create a lightweight fingerprint of the concept actually tested."""
    text = " ".join(str(q.get(k, "")) for k in ("question", "explanation", "calculation")).lower()
    words = re.findall(r"[a-z]{3,}", text)
    tokens = {w for w in words if w not in _STOPWORDS}
    for phrase in _HIGH_VALUE_PHRASES:
        if phrase in text:
            tokens.add(phrase)
    return tokens


def _concept_similarity(source, candidate):
    a = _concept_tokens(source)
    b = _concept_tokens(candidate)
    if not a or not b:
        return 0.0
    return len(a & b) / max(1, min(len(a), len(b)))


def _stem_key(q):
    """Normalize a stem so answer-order/difficulty variants count as the same question."""
    text = re.sub(r"[^a-z0-9 ]+", " ", str(q.get("question", "")).lower())
    return " ".join(w for w in text.split() if len(w) > 2)


def _recent_attempted_ids(conn, limit=15):
    rows = conn.execute("SELECT question_id FROM attempts ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return {r["question_id"] for r in rows}


def choose_followup(question_id, selected, part="Both", difficulty="All"):
    source = engine.get_question(question_id)
    if not source:
        return engine.choose_followup(question_id, selected, part, difficulty)

    conn = engine.db()
    ensure_schema(conn)
    history = engine._question_history(conn)
    statuses = _question_statuses(conn)
    recent_ids = _recent_attempted_ids(conn, 15)
    conn.close()

    source_stem = _stem_key(source)
    # Concept practice is intentionally domain-locked. A shared word such as
    # "budget" or "cost" is not enough to jump into another CMA domain.
    candidates = [q for q in engine.QUESTIONS if q["id"] != question_id
                  and q["part"] == source["part"]
                  and q.get("domain") == source.get("domain")
                  and (difficulty == "All" or q["difficulty"] == difficulty)
                  and _stem_key(q) != source_stem
                  and q["id"] not in recent_ids]

    # If the chosen difficulty has no fresh question, relax difficulty but keep
    # the same-part, same-domain, fresh-question requirement.
    if not candidates:
        candidates = [q for q in engine.QUESTIONS if q["id"] != question_id
                      and q["part"] == source["part"]
                      and q.get("domain") == source.get("domain")
                      and _stem_key(q) != source_stem
                      and q["id"] not in recent_ids]

    # Only if the bank is exhausted do we permit a previously seen question,
    # but still never leave the source domain during concept practice.
    if not candidates:
        candidates = [q for q in engine.QUESTIONS if q["id"] != question_id
                      and q["part"] == source["part"]
                      and q.get("domain") == source.get("domain")
                      and _stem_key(q) != source_stem]
    if not candidates:
        return engine.choose_followup(question_id, selected, part, difficulty)

    scored = []
    for q in candidates:
        similarity = _concept_similarity(source, q)
        h = history.get(q["id"], {})
        attempts = int(h.get("attempts", 0))
        correct = int(h.get("correct", 0))
        status = statuses.get(q["id"], "New")
        status_bonus = {"New": 3.0, "Weak": 2.5, "Learning": 1.0, "Mastered": 0.0}.get(status, 0.0)
        difficulty_bonus = 0.5 if q.get("difficulty") == source.get("difficulty") else 0.0
        score = similarity * 20 + difficulty_bonus + status_bonus
        if attempts:
            score += max(0, 2 - correct / max(1, attempts) * 2)
        scored.append((score + random.random() * 0.25, q, similarity))

    # Require meaningful concept overlap. If the bank has no same-domain
    # question that shares the concept fingerprint, stop the drill instead of
    # silently substituting an unrelated question.
    meaningful = [item for item in scored if item[2] >= 0.15]
    if not meaningful:
        return None
    return max(meaningful, key=lambda x: x[0])[1]


def snapshot(part="Both", domain="All"):
    candidates = _filtered_questions(part, domain, "All", set())
    if not candidates:
        return {"due_count": 0, "due_reviews": [], "next_best_action": None, "mastery_by_domain": []}
    conn = engine.db()
    ensure_schema(conn)
    now = _now().isoformat(timespec="seconds")
    rows = conn.execute("SELECT question_id,due_at,last_correct,last_confidence,streak FROM review_state WHERE due_at<=?", (now,)).fetchall()
    conn.close()
    allowed = {q["id"]: q for q in candidates}
    due = [dict(r) for r in rows if r["question_id"] in allowed]
    due.sort(key=lambda r: (0 if int(r["last_correct"] or 0) == 0 else 1 if int(r["last_confidence"] or 0) == 1 else 2, r["due_at"]))
    reviews = []
    for r in due[:5]:
        q = allowed[r["question_id"]]
        reason = "Review a missed question" if int(r["last_correct"] or 0) == 0 else "Reinforce a low-confidence correct answer"
        reviews.append({"question_id": q["id"], "domain": q["domain"], "reason": reason})
    return {"due_count": len(due), "due_reviews": reviews, "next_best_action": reviews[0] if reviews else None, "mastery_by_domain": mastery_by_domain(part, domain)}
