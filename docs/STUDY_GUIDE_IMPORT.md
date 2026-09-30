# Study guide import — September 30, 2026

Source: user-supplied `CMA Part 1 study guide.md`. Comparison base: `544c9e91302b98592344f0390a6d0e763804dfce` (332 MCQs and eight case items).

## Result

- Reviewed all 120 MCQs against the active bank and one another; added 76, excluded 44 equivalent tasks. Current bank: **408 MCQs plus eight case items**.
- Different wording, letters, units, or numerical inputs alone did not qualify a repeated task for this import. Existing questions and option order were retained.
- New tasks include cumulative-average learning curves, inverse production budgeting, operating leverage, weighted sales mix, overhead variance decomposition, EVA, FIFO/weighted-average equivalent units, service-department allocation, joint-cost allocation methods, EPS, bond measurement, lease reporting, IFRS comparisons, fraud schemes, SDLC, and EDI.
- New rule identification and application may share a broad skill, but must require different knowledge or reasoning. Weighted-average and FIFO equivalent units use the same physical inputs but measure different period work; both remain.
- All 76 have reviewed explanations and explicit skills; 27 have executable arithmetic checks, including direction checks. New keys are balanced 19 each A/B/C/D. Existing mastery/history and choice order are preserved.
- Source headings are not authoritative CMA mappings. CVP questions and financial-analysis ratios/EPS are assigned to Part 2; IT controls are assigned to Internal Controls. No change to the Part 2 simulation coverage restriction: Corporate Finance and Ethics are still insufficient.
- Twelve open-ended essay prompts were **not imported** into the automatically graded engine, which supports MCQs and short cases with MCQ items. They remain in the supplied guide. No fabricated multiple-choice conversions or essay grades were introduced.

`data/audit/study_guide_import.json` records the source hash, every original MCQ, every decision, duplicate canonical IDs, and edited status. `content_review.json` covers all active questions. The earlier content-trust report describes its original audit snapshot; this document records the subsequent import.

## Corrections before import

| Source | Correction |
| --- | --- |
| B-9 | Specify cumulative-average learning-curve model, not incremental unit time |
| B-17 | Specify unit sales mix, constant mix, and per-unit contribution margins |
| D-2 / D-3 / D-17 | Supply all data, method, no-spoilage assumptions; remove dependency on another question |
| D-5 | Use **final** selling prices less separable processing costs for relative NRV; original split-off wording did not support that calculation |
| D-12 | Original explanation conflated relative NRV with constant gross-margin NRV. Supply final sales and separable costs; correct allocated joint cost is **$28,000**, versus $30,000 under relative NRV |
| D-6 / D-9 / D-18 | Specify accounting method and throughput/constraint assumptions rather than universal claims |
| A-1 / A-2 / A-4 | Standalone EPS/bond inputs and measurement assumptions; diluted EPS is $2.445652 before rounding |
| A-3 | Exact discount factors reconcile the displayed bond price; rounded factors in the guide did not match displayed intermediate values |
| A-10 / A-17 | State U.S. GAAP and lease prepayment/incentive/cost/amortization assumptions |
| A-11 / A-15 / A-19 | Present obligation, all development recognition criteria, and revaluation exceptions clarified |
| E-3 | SOX 404(b) exemptions acknowledged rather than implying all accelerated issuers require attestation |
| E-12 | Correct the keyed COSO component to **Control activities** for review of operating performance; monitoring evaluates controls themselves |
| F-16 / F-17 / F-20 | Remove invoice input/output ambiguity, specify unapproved developer changes, and replace implausible distractors |
| Several explanations | Remove stale answer-letter references after ordering new choices |

## Duplicate review and validation

The import ledger points excluded exact and semantic repeats to an active canonical ID. Examples: C-1 equals P1X-028 even though quantities are described in different units; B-1 repeats the first-budget rule; F-12 repeats E-17 within the guide. Repeated break-even, variance, ROI, residual-income, budget, visualization, and analytics-classification tasks were excluded even when their inputs differ.

No new pair crosses the existing same-domain/same-skill 0.80 text-similarity threshold. A broader cross-domain 0.65 screen was also reviewed: inverse production budgeting versus forward production; inventory days versus inventory turnover; COSO component count versus component identification; two unrelated generic stem matches. Text similarity is an editorial signal, not proof of equivalence. Semantic review is not independent subject-matter certification.

Regression checks cover all 120 dispositions, valid duplicate targets, unique imported stems, standalone inputs, correct Part 2 mapping, corrected joint allocations/COSO key, financial rounding, signed currency parsing, and over/underapplied overhead direction. Standard PR checks validate the entire active bank, run tests/compilation, and build the frontend before merge.

## Primary references used for nuanced accounting/control review

- [IMA Learning Outcome Statements](https://www.imaglobal.org/assets/static/cma-learning-outcome-statements-2024.HDHHOjUF.pdf)
- [IAS 2 Inventories](https://www.ifrs.org/issued-standards/list-of-standards/ias-2-inventories/)
- [IAS 37 Provisions](https://www.ifrs.org/issued-standards/list-of-standards/ias-37-provisions-contingent-liabilities-and-contingent-assets/)
- [IAS 38 Intangible Assets](https://www.ifrs.org/issued-standards/list-of-standards/ias-38-intangible-assets/)
- [IAS 16 PPE](https://www.ifrs.org/issued-standards/list-of-standards/ias-16-property-plant-and-equipment/)
- [FASB ASC 842 implementation text, ASU 2016-02](https://storage.fasb.org/ASU%202016-02_Section%20A.pdf)
- [SEC Financial Reporting Manual, Topic 1](https://www.sec.gov/about/divisions-offices/division-corporation-finance/financial-reporting-manual/frm-topic-1)
- [PCAOB AS 2201](https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201)
