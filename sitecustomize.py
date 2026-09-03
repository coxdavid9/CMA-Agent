"""Runtime hook for CMA Coach's exam takeaway."""

def _patch_learning_feedback():
    try:
        import cma_agent.engine as engine
    except Exception:
        return

    original = engine.learning_feedback

    def learning_feedback(question_id, selected, confidence):
        result = original(question_id, selected, confidence)
        q = engine.get_question(question_id)
        if not q:
            return result
        choices = q.get("choices") or {}
        answer = q.get("answer", "")
        choice_text = choices.get(answer, answer)
        if q.get("calculation"):
            result["takeaway"] = f"**Exam cue:** {choice_text}. Identify the formula first, then substitute the numbers."
        else:
            result["takeaway"] = f"**Exam cue:** **{answer}. {choice_text}** — focus on the defining fact the question is testing."
        return result

    engine.learning_feedback = learning_feedback

_patch_learning_feedback()
