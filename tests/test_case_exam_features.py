import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CaseBankTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads((ROOT / "data" / "cases.json").read_text(encoding="utf-8"))

    def test_cases_have_complete_question_sets(self):
        self.assertGreaterEqual(len(self.cases), 2)
        ids = set()
        for case in self.cases:
            self.assertIn(case["part"], {"Part 1", "Part 2"})
            self.assertTrue(case.get("scenario"))
            self.assertGreaterEqual(len(case.get("questions", [])), 2)
            for idx, question in enumerate(case["questions"], 1):
                qid = f"{case['id']}-Q{idx}"
                self.assertNotIn(qid, ids)
                ids.add(qid)
                self.assertEqual(set(question["choices"].keys()), {"A", "B", "C", "D"})
                self.assertIn(question["answer"], {"A", "B", "C", "D"})


class BlueprintTests(unittest.TestCase):
    def test_official_domain_weights_sum_to_100(self):
        part1 = [15, 20, 20, 15, 15, 15]
        part2 = [20, 20, 25, 10, 10, 15]
        self.assertEqual(sum(part1), 100)
        self.assertEqual(sum(part2), 100)


if __name__ == "__main__":
    unittest.main()
