"""Transparent syllabus crosswalk; never equate tag matches with LOS mastery."""
import json
from cma_agent import engine
from cma_agent.lessons import LESSONS


def report(part='Both'):
    source = json.loads((engine.DATA/'syllabus_map.json').read_text())
    rows = []
    mapped = set()
    for topic in source['subtopics']:
        if part != 'Both' and topic['part'] != part:
            continue
        qs = [q for q in engine.QUESTIONS if not q.get('is_case') and q['part'] == topic['part'] and set(q['skills']) & set(topic['skills'])]
        mapped.update(q['id'] for q in qs)
        lessons = [l for l in LESSONS if any(o.startswith(topic['id']+'.') for o in l['outcomes'])]
        rows.append({**topic, 'question_ids': [q['id'] for q in qs], 'questions': len(qs),
                     'status': 'No tagged questions' if not qs else 'Thin' if len(qs)<3 else 'Tagged practice available',
                     'lessons': [{'id': l['id'], 'title': l['title'], 'outcomes': l['outcomes']} for l in lessons],
                     'outcome_audit': 'Pending individual-outcome review'})
    eligible = [q for q in engine.QUESTIONS if not q.get('is_case') and (part == 'Both' or q['part'] == part)]
    return {**{k:v for k,v in source.items() if k!='subtopics'}, 'subtopics': rows,
            'unmapped_questions': [q['id'] for q in eligible if q['id'] not in mapped],
            'question_count': len(eligible)}
