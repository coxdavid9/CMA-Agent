"""Independent arithmetic and curriculum integrity checks for the first reporting batch."""
import json
import random
import re
from pathlib import Path

import pytest
from cma_agent import lessons, financial_lessons

ROOT=Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("lesson_id", sorted(financial_lessons.IDS))
def test_fresh_check_arithmetic_across_examples(lesson_id):
    seen=set()
    for seed in range(100):
        tasks=lessons.build_tasks(lesson_id,random.Random(seed))
        assert len(tasks["guided"])==3 and len(tasks["check"])==2
        task=tasks["check"][0]
        seen.add(task["prompt"])
        n=[float(v.replace(",","")) for v in re.findall(r"\d[\d,]*(?:\.\d+)?",task["prompt"])]
        if lesson_id=="statement-links": expected=n[2]-n[3]-n[4]
        elif lesson_id=="accrual-timing": expected=n[0]/n[1]*(n[1]-n[2])
        elif lesson_id=="cash-flow-bridge": expected=n[0]+n[1]-n[2]-n[3]+n[4]
        elif lesson_id=="revenue-delivery": expected=n[0]*(1-n[1]/100)
        elif lesson_id=="inventory-measurement": expected=(n[0]+n[2]-n[4])*n[3]
        else: expected=n[0]*n[1]/100-n[2]
        assert task["answer"]==pytest.approx(expected),task["prompt"]
        assert float(task["answer"]).is_integer()  # UI requests whole dollars
        for t in tasks["guided"]+tasks["check"]:
            assert t["explanation"] and t["hints"]
    assert len(seen)>10


def test_course_plan_matches_official_subtopics_and_built_lessons():
    plan=json.loads((ROOT/"data/part1_curriculum.json").read_text())
    syllabus=json.loads((ROOT/"data/syllabus_map.json").read_text())
    official={t["id"] for t in syllabus["subtopics"] if t["part"]=="Part 1"}
    assert {t["id"] for t in plan["subtopics"]}==official
    units=[l for t in plan["subtopics"] for l in t["lessons"]]
    assert len(units)==55
    assert len({u["id"] for u in units})==len(units)
    built={l["id"] for l in lessons.LESSONS if l["part"]=="Part 1"}
    assert len(built)==8
    assert built <= {u["id"] for u in units}
    for t in plan["subtopics"]:
        for u in t["lessons"]:
            if u["id"] in built:
                assert any(o.startswith(t["id"]+".") for o in lessons.BY_ID[u["id"]]["outcomes"])
