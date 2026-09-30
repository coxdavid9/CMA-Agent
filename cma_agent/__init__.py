"""Reviewed skill labels shared by practice, feedback and coverage."""


def _install_concept_coverage():
    import cma_agent.adaptive as adaptive
    import cma_agent.engine as engine
    from cma_agent.question_bank import TAXONOMY

    def labels_for_question(q):
        return [skill for skill in q.get("skills", [])
                if skill in TAXONOMY.get(q.get("domain"), [])]

    original = adaptive.mastery_by_domain

    def mastery_with_coverage(part="Both", domain="All"):
        rows = original(part, domain)
        allowed = {q["id"]: q for q in engine.QUESTIONS
                   if not q.get("is_case") and (part == "Both" or q["part"] == part)
                   and (domain == "All" or q["domain"] == domain)}
        conn = engine.db()
        attempts = conn.execute(
            "SELECT question_id,domain FROM attempts WHERE bank_revision=?",
            (engine.REVISION,),
        ).fetchall()
        conn.close()
        covered = {}
        for attempt in attempts:
            q = allowed.get(attempt["question_id"])
            if q and q["domain"] == attempt["domain"]:
                covered.setdefault(q["domain"], set()).update(labels_for_question(q))
        for row in rows:
            names = TAXONOMY.get(row["domain"], [])
            observed = covered.get(row["domain"], set())
            row["concepts_covered"] = len(observed)
            row["concepts_total"] = len(names)
            row["concept_coverage"] = [{"name": name, "covered": name in observed} for name in names]
        return rows

    adaptive.mastery_by_domain = mastery_with_coverage
    adaptive.CMA_SKILL_TAXONOMY = TAXONOMY
    adaptive.skill_labels_for_question = labels_for_question


_install_concept_coverage()
