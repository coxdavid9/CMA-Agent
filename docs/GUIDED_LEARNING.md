# Guided learning

The Learn tab is now the default. Five original starter lessons connect accounting rules to financial-analysis decisions, use typed numeric responses and targeted setup hints, and separate guided learning from independent checks. One step is shown at a time. No video, LLM API key, or new paid service is required.

## Evidence and persistence
`lesson_runs` stores server-generated tasks and a serialized run state in the configured SQLite/Postgres database. Answers, explanations, and diagnostic keys are not included in public task payloads before grading. Server-side hint flags survive refreshes. Answer submissions are first-attempt only; replays cannot rewrite correctness. Step indices protect against stale requests, and per-run database locks serialize writes. Starting the same lesson resumes its unfinished run.

A session has three guided tasks and two independent checks. A due review has only the two fresh checks. Both independent checks must be correct without hints for “Independent check passed.” “Recall confirmed” additionally requires a previous independent pass and a review due at least a day later. Recall is checked again after three days; other sessions after one. This is evidence for a starter skill, not a claim of full-domain mastery. Numeric prompts vary across runs and the first numeric check cannot match the immediately previous run. Reasoning choices can repeat; broader novel-task coverage remains future work.

Practice attempts now have `hint_level` metadata. Helped responses remain in history/overall practice accuracy, but do not count toward independent question/domain mastery. Helped responses receive short review intervals. Skill strength requires breadth (five different questions) and evidence across two dates. Historical attempts recorded before hint metadata remain unknown; their original records are preserved.

## Syllabus scope
`data/syllabus_map.json` records the 41 official subtopic titles and IDs from IMA’s learning outcomes effective September 1, 2024 (verified November 16, 2026; the 2026 CBQ format change did not replace those content outcomes). Original lesson outcome references are specific. Existing question tags provide a **candidate subtopic crosswalk**, not a complete lettered-outcome audit. Coverage explicitly labels that limitation and shows gaps instead of a misleading completeness percentage. Existing reviewed MCQs and their audit ledger are unchanged.

## Validation
- Python regressions: all five lesson lifecycles, first-attempt grading, invalid input, hinted/incorrect independent checks, delayed recall vs same-day repetition, SQLite migration/history preservation, arithmetic across 100 parameter seeds, coverage invariants, and API compatibility.
- Separate disposable Postgres CI service verifies migrations from a legacy attempts/preferences schema, lesson persistence, and assisted-history queries.
- Browser CI exercises lesson intro, guided answer, refresh/resume, hints, coverage, mobile overflow, assisted practice reload, and dashboard. It uploads desktop/mobile screenshots.

## Known boundaries
Five starter lessons do not cover the full syllabus. Numeric entry is implemented in guided lessons; the case/exam UI still uses MCQs. Exam navigation, section-weighted diagnostic reporting, time carryover policy verification, and robust exam persistence remain separate work. Guided lessons use the existing personal/shared study database model; this release does not add multi-user accounts.


## Flexible-budget teaching revision (November 16, 2026)

David reported that the first lesson still felt like questions with brief explanations. The first lesson now has a separate ungraded teaching phase: an everyday cost-review problem, a fully worked $900 bridge ($600 output effect plus $300 unfavorable flexible-budget cost variance), an explorer with output and actual-cost controls, a discussion of the reasoning with feedback for different misconceptions, and a formula recap. Graded guided calculations are unavailable until that phase is complete. Teaching navigation is saved in the database and protected against duplicate/stale page moves; explorer values are saved on the current device. Teaching interactions create no attempts, correctness, or mastery evidence.

At that release, only the flexible-budget lesson used revision `guided-v2-teaching`; previous run records remained unchanged. Delayed-recall sessions still start with fresh checks. Reopening the teaching from a check records assistance. The explorer assumes a $6 variable rate and a $4,000 fixed total throughout its modeled output range; it does not identify the causes of a spending variance. Its automated browser check covers below/at/above planned volume, favorable/unfavorable/zero spending variance, reload persistence, mobile layout, and the absence of graded answers during teaching. Whether this approach helps David learn is to be evaluated through his next use, not inferred from passing software tests.


## Remaining four reasoning-first workshops (November 16, 2026)

All five starter lessons now teach before calculating. The four added workshops cover absorption versus variable costing, relevant costs/special orders, working capital/cash conversion, and NPV. Each has a concrete situation, three revealed worked steps, an ungraded parameter explorer, misconception-specific discussion (including an unsure option), and a formula recap before the existing guided and independent tasks. The same workshops open from matching Question Practice items without changing Learn runs. Full teaching can be reopened from any lesson check and counts as assistance during an independent check.

The remaining four lessons now use revision `guided-v2-teaching`, making their rebuilt paths available while preserving old v1 records. The flexible-budget lesson already used that revision, so its current progress is preserved. Teaching-page progress is stored in the existing database. Explorer values are saved on the current device. Teaching does not record correctness or establish mastery.

Model assumptions are visible in each explorer:
- Absorption: beginning inventory 400 units, production at normal capacity 1,200, constant $5 fixed manufacturing overhead rate, $6,000 current fixed overhead, $30 price, $12 variable manufacturing cost, $2,000 period selling/admin cost, and no overhead variances. Sales are bounded by available inventory. The reconciliation uses the inventory change, including releases from beginning inventory.
- Special orders: $14 incremental unit cost and $1,000 new setup; unchanged $6/unit allocation and past unrecoverable $900 payment excluded. Constrained capacity displaces $10 regular contribution per order unit. Positive, zero, and negative outcomes are shown without ignoring qualitative business effects.
- Cash cycle: average inventory/receivable/payable days, with positive/zero/negative cycles. Supplier terms are assumed agreed. Days are not presented as dollars of cash released or a liquidity guarantee.
- NPV: one future receipt, selectable timing and required return, time-zero initial payment, no intervening receipts, taxes, salvage or working-capital changes. Multiple-receipt/after-tax projects require a fuller model.

CI validates the models against independent calculations, signs and boundary cases. Browser checks cover all four full learning paths, parameter presets and keyboard controls, reload/resume, misconception feedback, grading transitions, mobile overflow, and all four Question Practice previews. These checks verify software/content arithmetic; effectiveness for David remains a learning-experience question.
