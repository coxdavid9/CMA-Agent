import random
from collections import defaultdict

from cma_agent import engine, study_metrics


def weights(part, blueprint):
    c = engine.db()
    try:
        rows = c.execute("SELECT * FROM attempts WHERE part=? ORDER BY ts,id", (part,)).fetchall()
    finally:
        c.close()
    _, first, _ = study_metrics.first_attempts(part, rows)
    by_domain = defaultdict(list)
    for row in first.values():
        by_domain[row["domain"]].append(row["correct"])
    result = {}
    for domain, share in blueprint.items():
        results = by_domain[domain]
        accuracy = sum(results) / len(results) if len(results) >= 10 else .5
        result[domain] = share * (2 - accuracy)
    return result


def draw(weighted, rng=random):
    return rng.choices(list(weighted), weights=list(weighted.values()), k=1)[0]
