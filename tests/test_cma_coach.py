import json
import os
import tempfile
import unittest
from pathlib import Path

from cma_agent.question_utils import clean_question

ROOT = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = ROOT / "data" / "questions.json"


class QuestionBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))

    def test_question_bank_shape(self):
        self.assertEqual(len(self.questions), 500)
        ids = [q["id"] for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))
        for q in self.questions:
            self.assertIn(q["part"], {"Part 1", "Part 2"})
            self.assertIn(q["difficulty"], {"Easy", "Medium", "Hard"})
            self.assertEqual(set(q["choices"].keys()), {"A", "B", "C", "D"})
            self.assertIn(q["answer"], {"A", "B", "C", "D"})

    def test_question_cleanup_removes_known_corruption(self):
        for q in self.questions:
            cleaned = clean_question(q["question"])
            self.assertNotRegex(cleaned, r":\s*(?:when|in|while|for|under|during|after|before)\b")
            self.assertNotRegex(cleaned, r"\bis\s+(?:a|an|the)\s*:$")
            self.assertNotRegex(cleaned, r"\s+in a multi-site organization\.?$")
            self.assertFalse(cleaned.endswith(":"))

    def test_engine_can_select_and_grade(self):
        db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        db_file.close()
        os.environ["CMA_DB_PATH"] = db_file.name
        try:
            from cma_agent.engine import choose_question, grade

            for part in ("Part 1", "Part 2"):
                q = choose_question(part, "All", "All")
                self.assertEqual(q["part"], part)
                self.assertIn(q["answer"], {"A", "B", "C", "D"})
                result, graded = grade(q["id"], q["answer"], 3, "test-session")
                self.assertEqual(result, 1)
                self.assertEqual(graded["id"], q["id"])
        finally:
            try:
                os.remove(db_file.name)
            except FileNotFoundError:
                pass


if __name__ == "__main__":
    unittest.main()
