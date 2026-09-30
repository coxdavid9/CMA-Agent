import copy
import importlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cma_agent import adaptive, engine, skills
from cma_agent.question_bank import (
    DATA, REVISION, arithmetic, case_questions, coverage,
    load_questions, validate_bank, validate_question,
)


class BankIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = load_questions()
        cls.cases = json.loads((DATA / "cases.json").read_text(encoding="utf-8"))
        cls.audit = json.loads((DATA / "audit" / "content_review.json").read_text(encoding="utf-8"))
        cls.by_id = {q["id"]: q for q in cls.questions}

    def test_all_source_questions_and_case_items_are_valid_and_reviewed(self):
        self.assertEqual(validate_bank(self.questions, self.cases, self.audit), [])
        original = json.loads((DATA / "audit" / "original_questions.json").read_text(encoding="utf-8"))
        self.assertEqual(set(self.audit["dispositions"]), {q["id"] for q in original})
        self.assertEqual({qid for qid, row in self.audit["dispositions"].items() if row["status"] == "active"},
                         {q["id"] for q in self.questions})

    def test_wrong_keys_and_duplicate_correct_values_are_rejected(self):
        q = copy.deepcopy(self.by_id["P1Q-009"])
        q["answer"] = next(key for key in q["choices"] if key != q["answer"])
        self.assertTrue(validate_question(q))
        q = copy.deepcopy(self.by_id["P1Q-009"])
        other = next(key for key in q["choices"] if key != q["answer"])
        q["choices"][other] = q["choices"][q["answer"]]
        q["numeric_check"]["choice_values"][other] = q["numeric_check"]["choice_values"][q["answer"]]
        self.assertTrue(validate_question(q))

    def test_same_magnitude_wrong_variance_direction_is_rejected(self):
        q = copy.deepcopy(self.by_id["P1-009"])
        q["answer"] = next(k for k, text in q["choices"].items() if text == "$10,000 favorable")
        self.assertTrue(validate_question(q))

    def test_arbitrary_code_and_bad_arithmetic_are_rejected(self):
        with self.assertRaises(ValueError):
            arithmetic("__import__('os').system('true')")
        q = copy.deepcopy(self.by_id["P1Q-009"])
        q["calculation"] = "520000/400000=9"
        self.assertTrue(validate_question(q))

    def test_editorial_changes_require_a_fresh_review(self):
        changed = copy.deepcopy(self.questions)
        changed[0]["explanation"] += " Changed."
        self.assertTrue(validate_bank(changed, self.cases, self.audit))
        changed = copy.deepcopy(self.questions)
        changed[0]["skills"] = ["Unknown skill"]
        self.assertTrue(validate_question(changed[0]))

    def test_confirmed_accounting_and_decision_errors_are_corrected(self):
        make_buy = self.by_id["V3-1-04-010"]
        self.assertEqual(make_buy["choices"][make_buy["answer"]], "Buy the product")
        writeoff = self.by_id["P1Q-010"]
        self.assertIn("net receivables are unchanged", writeoff["choices"][writeoff["answer"]])
        benefit = self.by_id["V3-2-09-007"]
        self.assertIn("Making saves", benefit["explanation"])
        process = self.by_id["P1Q-132"]
        self.assertEqual(arithmetic(process["numeric_check"]["expression"]), 2)
        asset_swap = self.by_id["P1Q-014"]
        self.assertNotIn("Collecting an accounts receivable", asset_swap["choices"].values())

    def test_incidental_explanation_words_do_not_credit_unexamined_skills(self):
        q = copy.deepcopy(self.by_id["P1-009"])
        q["explanation"] += " Related topics include balanced scorecard and transfer pricing."
        self.assertEqual(adaptive.skill_labels_for_question(q), ["Standard cost and variances"])
        self.assertEqual(adaptive._concept_labels(q), {"Standard cost and variances"})

    def test_coverage_exposes_missing_skills_and_case_mapping_is_valid(self):
        rows = {r["domain"]: r for r in coverage(self.questions)}
        skill = next(s for s in rows["Corporate Finance"]["skills"] if s["skill"] == "Risk and return")
        self.assertEqual(skill["status"], "missing")
        combined = case_questions(self.cases)
        first = next(q for q in combined if q["id"] == "CASE-001-Q1")
        self.assertEqual((first["part"], first["domain"]), ("Part 2", "Business Decision Analysis"))

    def test_loader_rejects_duplicate_ids_and_malformed_supplements(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "questions.json").write_text(json.dumps([self.questions[0]]))
            supplement = root / "questions_part1_test.json"
            supplement.write_text(json.dumps([self.questions[0]]))
            with self.assertRaises(ValueError):
                load_questions(root)
            supplement.write_text("invalid JSON")
            with self.assertRaises(ValueError):
                load_questions(root)


class RevisionAndApiTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.db_patch = patch.object(engine, "DB", Path(self.directory.name) / "study.db")
        self.db_patch.start()
        self.url_patch = patch.object(engine, "DATABASE_URL", None)
        self.url_patch.start()

    def tearDown(self):
        self.url_patch.stop()
        self.db_patch.stop()
        self.directory.cleanup()

    def test_legacy_history_is_preserved_but_not_credited_as_reviewed_mastery(self):
        conn = engine.db()
        q = next(q for q in engine.QUESTIONS if q["id"] == "P1-009")
        for _ in range(5):
            conn.execute("INSERT INTO attempts(question_id,domain,correct,confidence) VALUES(?,?,?,?)",
                         (q["id"], q["domain"], 1, 3))
        conn.commit()
        self.assertNotIn(q["id"], adaptive._question_statuses(conn))
        conn.close()
        self.assertEqual(engine.stats()["attempted"], 5)
        engine.grade(q["id"], q["answer"], 3, "audit-test")
        conn = engine.db()
        self.assertEqual(conn.execute("SELECT bank_revision FROM attempts ORDER BY id DESC LIMIT 1").fetchone()[0],
                         REVISION)
        self.assertEqual(adaptive._question_statuses(conn)[q["id"]], "Learning")
        conn.close()
        skills.record_attempt(q, True, 3)
        self.assertEqual(skills.snapshot()["skills_tracked"], 1)

    def test_api_retains_bank_and_hides_solutions_in_exam_payloads(self):
        async def empty_app(scope, receive, send):
            pass
        with patch("fastapi.staticfiles.StaticFiles", return_value=empty_app):
            api = importlib.import_module("api")
        self.assertEqual(len([q for q in engine.QUESTIONS if not q.get("is_case")]), len(load_questions()))
        regular = next(q for q in engine.QUESTIONS if q.get("numeric_check") and not q.get("is_case"))
        public = api._public_exam_question(regular)
        self.assertFalse({"answer", "explanation", "calculation", "numeric_check"} & set(public))
        selected = api._exam_questions("Part 1")
        self.assertEqual(len(selected), 100)
        for domain, target in api._BLUEPRINT["Part 1"].items():
            self.assertEqual(sum(q["domain"] == domain for q in selected), target)
        with self.assertRaises(api.HTTPException) as context:
            api._exam_questions("Part 2")
        self.assertIn("Use mixed practice", context.exception.detail)


if __name__ == "__main__":
    unittest.main()
