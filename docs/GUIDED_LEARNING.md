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

Only the flexible-budget lesson uses revision `guided-v2-teaching`; previous run records remain unchanged, and the other lessons keep their existing history. Delayed-recall sessions still start with fresh checks. Reopening the teaching from a check records assistance. The explorer assumes a $6 variable rate and a $4,000 fixed total throughout its modeled output range; it does not identify the causes of a spending variance. Its automated browser check covers below/at/above planned volume, favorable/unfavorable/zero spending variance, reload persistence, mobile layout, and the absence of graded answers during teaching. Whether this approach helps David learn is to be evaluated through his next use, not inferred from passing software tests.
