from cma_agent import skills


def test_confident_wrong_calculation_is_application_gap():
    q = {"calculation": "CM = sales - variable costs"}
    kind, coaching = skills.diagnose(q, False, 3)
    assert kind == "calculation_application_gap"
    assert "setup" in coaching.lower()


def test_low_confidence_correct_is_not_mastered_signal():
    q = {"calculation": None}
    kind, _ = skills.diagnose(q, True, 1)
    assert kind == "confidence_gap"


def test_unsure_wrong_concept_is_knowledge_gap():
    q = {"calculation": None}
    kind, _ = skills.diagnose(q, False, 1)
    assert kind == "knowledge_gap"
