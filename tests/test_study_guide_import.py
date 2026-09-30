"""Import completeness, duplicate decisions, and corrected source calculations."""
import copy
import json
import re
import unittest

from cma_agent.question_bank import DATA, arithmetic, choice_number, load_questions, stem_key, validate_question


class StudyGuideImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads((DATA / 'audit/study_guide_import.json').read_text())
        cls.questions = load_questions()
        cls.by_id = {q['id']: q for q in cls.questions}

    def test_every_source_mcq_has_one_traceable_import_decision(self):
        source = self.report['original_mcqs']
        decisions = self.report['dispositions']
        self.assertEqual(len(source), 120)
        self.assertEqual(len({q['source_id'] for q in source}), 120)
        self.assertEqual(set(decisions), {q['source_id'] for q in source})
        added = {d['question_id'] for d in decisions.values() if d['status'] == 'added'}
        self.assertEqual(added, {q['id'] for q in self.questions if q['id'].startswith('GUIDE-')})
        self.assertEqual(len(added), self.report['added'])
        duplicates = [d for d in decisions.values() if d['status'] == 'duplicate']
        self.assertEqual(len(duplicates), self.report['duplicates_skipped'])
        self.assertEqual(len(added) + len(duplicates), 120)
        for decision in duplicates:
            self.assertIn(decision['canonical_id'], self.by_id)
        for qid in added:
            self.assertEqual(validate_question(self.by_id[qid]), [])
            self.assertNotRegex(self.by_id[qid]['question'], r'(?i)\busing (?:the data\b|[A-F]-\d)|\bdata (?:in\b|above\b)')

    def test_imported_stems_do_not_duplicate_any_active_stem(self):
        for q in self.questions:
            if q['id'].startswith('GUIDE-'):
                matches = [other['id'] for other in self.questions if stem_key(other['question']) == stem_key(q['question'])]
                self.assertEqual(matches, [q['id']])
        # Different units and equivalent wording must not reintroduce known repeats.
        d = self.report['dispositions']
        self.assertEqual(d['C-1']['canonical_id'], 'P1X-028')
        self.assertEqual(d['B-1']['canonical_id'], 'P1X-014')
        self.assertEqual(d['F-12']['canonical_id'], d['E-17']['question_id'])

    def test_distinct_process_costing_methods_and_allocation_are_correct(self):
        checks = {'GUIDE-D-02': 9900, 'GUIDE-D-03': 9100,
                  'GUIDE-D-07': 26000, 'GUIDE-D-12': 28000}
        for qid, expected in checks.items():
            q = self.by_id[qid]
            self.assertAlmostEqual(arithmetic(q['numeric_check']['expression']), expected)
            self.assertEqual(choice_number(q['choices'][q['answer']]), expected)
        joint = self.by_id['GUIDE-D-05']
        self.assertIn('final selling price', joint['question'])
        self.assertAlmostEqual(arithmetic(joint['numeric_check']['expression']), 57142.857142857145)

    def test_rounded_financial_calculations_match_unique_key(self):
        for qid, expected in [('GUIDE-A-02', 2.4456521739130435), ('GUIDE-A-03', 924184.264611831)] :
            q = self.by_id[qid]
            self.assertAlmostEqual(arithmetic(q['numeric_check']['expression']), expected)
            self.assertEqual(validate_question(q), [])
            changed = copy.deepcopy(q)
            changed['answer'] = next(k for k in q['choices'] if k != q['answer'])
            self.assertTrue(validate_question(changed))
        self.assertEqual(choice_number('-$50,000'), -50000)

    def test_overhead_direction_and_coso_source_key_are_corrected(self):
        q = self.by_id['GUIDE-D-11']
        self.assertEqual(q['choices'][q['answer']], '$3,000 underapplied')
        changed = copy.deepcopy(q)
        changed['answer'] = next(k for k, text in changed['choices'].items() if 'overapplied' in text)
        self.assertTrue(validate_question(changed))
        coso = self.by_id['GUIDE-E-12']
        self.assertEqual(coso['choices'][coso['answer']], 'Control activities')

    def test_part_mapping_and_missing_skills_are_not_inherited_from_guide_titles(self):
        for qid in ('GUIDE-B-15','GUIDE-B-16','GUIDE-B-17','GUIDE-A-01','GUIDE-A-06'):
            self.assertEqual(self.by_id[qid]['part'], 'Part 2')
        for qid, skill in [('GUIDE-B-09','Learning curve applications'),
                          ('GUIDE-C-07','Advanced variance decomposition'),
                          ('GUIDE-D-03','Equivalent unit calculations'),
                          ('GUIDE-D-07','Service department allocation')]:
            self.assertIn(skill, self.by_id[qid]['skills'])


if __name__ == '__main__':
    unittest.main()
