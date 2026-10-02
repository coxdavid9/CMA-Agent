# CMA Coach Project Status

Last verified from repository: 2026-10-02

## Current state
CMA Coach is an active study system with a reviewed question bank, practice/skill engine, React/mobile UI, case features, automated integrity validation, and CI. The active bank after the September 30 study-guide import contains **408 MCQs plus eight case items**.

## Recently completed
- Commit/PR work imported 76 reviewed study-guide MCQs while excluding 44 equivalent tasks.
- The full content-trust audit retired 392 duplicates and quarantined 28 weak distinct items from the earlier source bank.
- The practice-first CMA Skill Engine and mobile-first UI were built.
- The duplicate sidebar book cover was removed.

## Verified open work
The content-trust audit explicitly identifies the next editorial work: replace quarantined/weak coverage with substantive exam-useful tasks targeting actual gaps rather than chasing a question-count target.

Highest-priority verified gaps:
- cash-flow valuation and financing risk
- ethics decisions with competing duties
- multi-part standard-cost analysis
- inventory-process mathematics and allocation
- complex financial-reporting measurement
- Corporate Finance and Professional Ethics remain especially thin
- Part 2 cannot yet satisfy the current 100-question simulation proportions

## Quality guardrails
Accuracy and CMA usefulness come before question count. New questions must pass duplicate/near-duplicate review, answer/explanation consistency, arithmetic/direction checks where applicable, plausible distractors, explicit CMA domain/skill mapping, and the existing CI validation.

## Next milestone
**Build reviewed questions for the highest-priority thin/missing skills, starting with Corporate Finance and Professional Ethics, without duplicating active tasks.** Update the audit/coverage artifacts as coverage improves.
