import json
from datetime import datetime

from cma_agent.engine import domains, learning_snapshot, stats, goal, recent


def build_study_profile():
    s = stats()
    snap = learning_snapshot()
    g = goal()

    by_domain = {row["domain"]: row for row in s.get("by_domain", [])}
    domain_profile = []
    for domain in domains("Both"):
        row = by_domain.get(domain)
        if not row:
            domain_profile.append({"domain": domain, "status": "New", "attempted": 0, "accuracy": None})
            continue
        accuracy = float(row.get("pct") or 0)
        if accuracy >= 85:
            status = "Strong"
        elif accuracy >= 70:
            status = "Developing"
        else:
            status = "Needs Review"
        domain_profile.append({
            "domain": domain,
            "status": status,
            "attempted": int(row.get("n") or 0),
            "accuracy": accuracy,
        })

    recent_attempts = recent(20)
    confidence_misses = [
        {"domain": r.get("domain"), "confidence": r.get("confidence")}
        for r in recent_attempts
        if int(r.get("correct") or 0) == 0
    ][:10]

    return {
        "profile_version": 1,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "purpose": "CMA Study Mode handoff",
        "overall": {
            "questions_completed": s.get("attempted", 0),
            "accuracy": s.get("accuracy", 0),
            "question_bank_size": s.get("question_bank_size", 0),
        },
        "current_plan": g,
        "priority_topics": {
            "weak_domains": snap.get("weak_domains", []),
            "fragile_domains": snap.get("fragile_domains", []),
            "recent_misses": snap.get("recent_misses", []),
        },
        "domain_profile": domain_profile,
        "recent_miss_confidence": confidence_misses,
        "study_mode_guidance": [
            "teach_weak_topics_before drilling them",
            "use one question at a time",
            "prefer reasoning and concept recall over answer memorization",
            "reinforce low-confidence correct answers",
            "use follow-up questions after misses",
        ],
    }


def study_profile_json():
    return json.dumps(build_study_profile(), indent=2, default=str)
