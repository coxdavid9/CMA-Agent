# CMA Coach content-trust audit — September 30, 2026

Source: `c1e25e5c26254bcabae3b5faa8190c81772035a0`.

Every one of the 752 source MCQs and all eight items in four cases was included. Equivalent variants were grouped, their keyed choice text was checked for agreement, and each distinct task was reviewed for the eight requested quality dimensions. This is an assistant editorial audit, not an independent subject-matter certification.

## Result

- **332 active MCQs, eight case items. No questions added.**
- **392 duplicates retired; 28 weak distinct items quarantined.** Original text and source filenames remain in `data/audit/original_questions.json`; each original ID has a disposition in `content_review.json`. Duplicate IDs whose canonical task was itself quarantined have no active canonical target.
- Numerical variants with changed inputs remain when they require a fresh solve. Rule identification and a concrete application can both remain. Similarity is a review signal, not proof of a duplicate.
- 96 MCQs and seven case items have executable numerical checks. Formula results, rounding, option values, and favorable/unfavorable or gain/loss direction are checked. The two-product case includes separate calculations.
- Key positions were balanced within domains (87 A, 85 B, 81 C, 79 D overall). Previous letter-based attempt records cannot be treated as evidence for reordered choices.
- Unsupported Hard labels were removed. The current material is foundational recall and basic application, not a sufficient source of difficult exam-level practice.

## Confirmed corrections

| Original ID | Problem | Result |
| --- | --- | --- |
| V3-1-04-010 and cosmetic variants | Make keyed despite $38 make versus $35 buy | Buy; $3 savings |
| V3-2-09-007 and variants | Buying described as saving $4 despite higher buy cost | Making saves $4; explanation corrected |
| P1Q-010 | Keyed text reduced net receivables; explanation said unchanged | Gross receivable and allowance both decrease; net unchanged |
| P1Q-014 | Buying equipment and collecting receivables both valid | One valid asset-swap choice |
| P1Q-005 | Dividend timing and capitalized depreciation made effects ambiguous | Explicit current-period income effect and office equipment |
| P1Q-132 | Negative processing benefit omitted from choices | Ask for $2 reduction; executable calculation |
| V3-2-07-004 / V3-2-08-007 | Two correct numerical choices | Distinct distractors |
| V3-1-02-004 | Duplicate wrong choice | Distinct distractors |
| P1-015 | Two incompatible duty combinations; unsupported greatest-risk ranking | Test cash custody and reconciliation specifically |
| P1Q-025 | Sales could include cash sales | Net credit sales specified |
| P1Q-126 / P1Q-096 | Inventory and transfer-capacity assumptions missing | Beginning inventory, allocation, capacity, displacement specified |
| P1Q-185 / P1Q-165 / P1Q-163 | Overgeneralized shipment trigger, PO protection, and segregation | Contract control-transfer assumption and precise control purpose |
| P2-016 / V3-2-12-007 / V3-2-12-034 | Standards called principles; confidentiality framed as ending | Correct standard terminology and disclosure conditions |
| CASE-001 / CASE-003 | Wrong domain; idle and constrained capacity conflicted | Product mix in Part 2; variance evaluation in Performance Management |
| Numerous source questions | Off-topic distractors, cosmetic context, wrong domain, incidental keyword credit | Distractors revised, context removed, explicit reviewed skills |

## Coverage and usefulness

These are our product's named skill groups, anchored to the IMA outline; a group with questions is **not** proof that every official learning outcome within it is covered. Counts exclude case items to keep standalone depth visible.

| Domain | Distinct MCQs | CMA domain weight | Named groups represented |
| --- | ---: | ---: | ---: |
| External Financial Reporting Decisions | 38 | 15% | 7/11 |
| Planning, Budgeting, and Forecasting | 46 | 20% | 6/9 |
| Performance Management | 37 | 20% | 7/9 |
| Cost Management | 30 | 15% | 8/11 |
| Internal Controls | 40 | 15% | 8/9 |
| Technology and Analytics | 36 | 15% | 10/11 |
| Financial Statement Analysis | 23 | 20% | 6/8 |
| Corporate Finance | 12 | 20% | 5/10 |
| Business Decision Analysis | 36 | 25% | 7/8 |
| Enterprise Risk Management | 11 | 10% | 4/8 |
| Capital Investment Decisions | 14 | 10% | 7/9 |
| Professional Ethics | 9 | 15% | 7/10 |

Highest-priority deficits are advanced calculations and integrated applications. Corporate Finance and Professional Ethics are especially thin after removing repetition. There is no coverage of several named groups, and some represented groups still contain only definitions. The bank should supplement exam preparation; its accuracy percentages do not establish exam readiness.

The next editorial work should replace quarantined items with substantive tasks targeting specific gaps, rather than a numerical growth target. Priority topics: cash-flow valuation and financing risk; ethics decisions with competing duties; multi-part standard-cost analysis; inventory-process mathematics and allocation; complex financial-reporting measurement. See the machine-generated coverage artifact for missing/thin groups.

## Runtime and history

- Both application paths use one source loader; malformed supplements and duplicate IDs no longer disappear silently. Audited questions are consolidated into `questions.json`; former supplement files are empty.
- Explicit skill labels replace keyword inference. Explanation mentions cannot award additional skill coverage.
- Legacy attempts remain in lifetime history. New attempts carry a bank revision; reviewed question/domain mastery and skill priorities use that revision only. Retired IDs and old answer letters do not earn current mastery. Historical reports remain historical.
- Browser question cache is versioned so it cannot restore old choices after this audit.
- A 100-question set now requires enough reviewed items in every domain. Part 2 is blocked with a useful message because it cannot yet satisfy those proportions; mixed practice remains available. Part 1 can supply its MCQ proportions. Existing short cases are labeled practice exercises, not full replicas of the exam case section.
- No data deletion or fabricated replacement questions.

## Validation and review

PR checks run bank validation, the full pytest suite (including previously skipped function-style skill tests), Python compilation, and a frontend build. Near-duplicate candidates and coverage are exported as a CI artifact and listed for editorial review.

Schema, arithmetic, choice uniqueness, part/skill validity, and reviewed-content consistency can be automated. A changed explanation or question must update the editorial ledger. Semantic correctness, ambiguity, plausibility, and exam difficulty still require editorial judgment; a green check alone does not certify them.

Reproduce with:

```sh
python tools/validate_question_bank.py
python tools/validate_question_bank.py --report
python -m pytest -q
```

## References

- [IMA current preparation resources](https://www.imaglobal.org/certifications/cma/how-to)
- [Content Specification Outline](https://www.imaglobal.org/assets/static/cma-content-specification-outlines-2024.Cr1Ox4aS.pdf)
- [Learning Outcome Statements](https://www.imaglobal.org/assets/static/cma-learning-outcome-statements-2024.HDHHOjUF.pdf)
- [IMA Statement of Ethical Professional Practice](https://www.imaglobal.org/pages/statement-of-ethics)

References guide domain and terminology review. Original bank content was corrected rather than copying exam questions.
