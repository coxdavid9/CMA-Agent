from collections import Counter
import random

from cma_agent import engine, exam_mix, formulas


def test_exam_mix_shares_and_weak_domain(tmp_path, monkeypatch):
    from pathlib import Path
    (Path(__file__).parents[1] / "frontend/dist").mkdir(exist_ok=True)
    from api import _BLUEPRINT
    monkeypatch.setattr(engine, "DB", tmp_path / "mix.db")
    part = "Part 1"
    blueprint = _BLUEPRINT[part]
    weighted = exam_mix.weights(part, blueprint)
    rng = random.Random(930)
    counts = Counter(exam_mix.draw(weighted, rng) for _ in range(500))
    for domain, share in blueprint.items():
        assert abs(counts[domain] / 5 - share) < 5
    weak, strong = list(blueprint)[:2]
    for domain, correct_count in [(weak, 3), (strong, 9)]:
        questions = [q for q in engine.QUESTIONS if q["part"] == part and q["domain"] == domain and not q.get("is_case")]
        for i, q in enumerate(questions[:10]):
            engine.grade(q["id"], q["answer"] if i < correct_count else "")
    tilted = exam_mix.weights(part, blueprint)
    assert tilted[weak] / blueprint[weak] > tilted[strong] / blueprint[strong]


def test_formula_review_schedule_and_domains(tmp_path, monkeypatch):
    from pathlib import Path
    (Path(__file__).parents[1] / "frontend/dist").mkdir(exist_ok=True)
    from api import _BLUEPRINT
    monkeypatch.setattr(engine, "DB", tmp_path / "formula.db")
    for card in formulas.CARDS.values():
        assert card["domain"] in _BLUEPRINT[card["part"]]
    # Exercise the legacy flip-card grading path independently of active-card priority.
    monkeypatch.setattr(formulas, "CARDS", {cid: card for cid, card in formulas.CARDS.items()
                                          if card.get("type", "reveal") == "reveal"})
    cards = formulas.due("Part 1", limit=10)
    assert len(cards) == 10
    hit = formulas.grade(cards[0]["id"], True)
    miss = formulas.grade(cards[1]["id"], False)
    assert hit["interval_days"] == 1
    assert miss["interval_days"] == .25
    assert miss["due_at"] < hit["due_at"]
    assert cards[0] not in formulas.due("Part 1", limit=10)
