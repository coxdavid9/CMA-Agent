# CMA Coach Project Status

Last verified from repository: 2026-11-16

## Current state
CMA Coach is a personal study app with React/mobile UI, FastAPI, SQLite/Postgres history, adaptive practice, cases, exam practice, and a new guided-learning home.

Content inventory: **408 reviewed standalone MCQs (293 Part 1 / 115 Part 2), 16 short MCQ cases with 34 subquestions, and five original guided starter lessons.** These counts are distinct; neither a question count nor a lesson completion establishes full syllabus mastery.

## Completed
- Reviewed bank audit and study-guide import, duplicate retirement, arithmetic validation, skill tagging, and CI.
- 12 additional Part 1 case scenarios; current case responses remain MCQ only.
- Optional practice hints and teach-before-retest review (PR #12).
- Reasoning-first flexible-budget workshop: a month-end story, a fully worked cost bridge, an ungraded live budget explorer, misconception-specific discussion, and a formula recap before calculation. Previous first-lesson history is preserved under its older revision; the revised path starts fresh. Reopening teaching during an independent check counts as assistance.
- Guided lessons for flexible budgets, absorption/variable costing, special orders, working capital/cash conversion cycle, and NPV.
- Each lesson teaches a concept, guides three steps, checks a fresh numeric answer and a reasoning choice, and schedules a delayed check. Examples use varied parameters and keep answer keys on the server.
- Persistent lesson progress and hint usage. Guided/assisted checks cannot establish independent success. Initial independent success and delayed recall are separate labels; no full-topic mastery claim.
- Practice hint usage survives hiding/reload. Assisted attempts remain in history but are excluded from independent question/domain mastery, and return sooner for review. Old history without hint metadata cannot be retrospectively classified.
- Official 41-subtopic inventory with an editorial skill-tag crosswalk and five lessons mapped to specific lettered outcomes. The crosswalk explicitly does not claim a complete individual-outcome or cognitive-depth audit.
- Running correctness removed from the exam screen. Existing practice, case, exam, dashboard, and study-plan modes remain available.
- CI covers bank integrity, regressions, frontend build, browser flows/screenshots, and legacy Postgres migrations.

## Remaining / next milestone
1. Try the five-lesson path with David, then improve the actual teaching friction before expanding it.
2. Audit individual lettered IMA learning outcomes against question reasoning and depth. Tag matching is only candidate coverage; missing outcomes can exist in any tagged subtopic.
3. Add substantive Corporate Finance and Professional Ethics content. Part 2 simulation still lacks 7 Corporate Finance and 6 Ethics questions just to form one weighted 100-question set; those minima are not sufficient learning breadth.
4. Build integrated ~250-word cases and numeric/list/matching response formats. Existing short MCQ cases are not a replica of the current U.S. CBQ section.
5. Add exam review/flagging navigation, separate section diagnostics, robust timed-session persistence, and fix timeout completion totals. The current raw percentage is not an official scaled-score estimate.
6. Consider conversational explanations only after the deterministic teaching path is useful. No paid LLM dependency is required for the current lessons.

## Quality guardrails
Preserve existing reviewed questions and answer keys. New content needs arithmetic/direction checks, plausible distractors, explicit CMA mappings, and duplicate review. Do not call a bank metric or same-day repeated answer exam readiness. Review dates are in-app prompts, not push notifications.

## Practice teaching bridge (2026-11-16)
- Question Practice offers concept teaching where reviewed skill links fit an existing lesson. Flexible-budget links explicitly exclude revenue and sales-contribution variance questions outside the cost lesson's scope.
- Teaching opens inline; the current question, choice, confidence, and review stay in place and draft state survives refresh on the current device. Previewing does not create or alter Learn runs. Teaching used before grading counts as assistance; new attempts reset that support flag.
- Learn and all practice modes share the same green brand palette while retaining their layouts. Semantic success/error colors remain distinct.
