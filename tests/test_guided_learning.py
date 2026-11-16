from datetime import datetime, timedelta
import importlib
import json
from pathlib import Path
import random

import pytest
from cma_agent import engine, lessons, adaptive, skills, coverage


@pytest.fixture
def isolated_db(tmp_path, monkeypatch):
    monkeypatch.setattr(engine, 'DB', tmp_path/'learning.db')
    monkeypatch.setattr(engine, 'DATABASE_URL', None)
    return tmp_path/'learning.db'


def private_state(run):
    c = engine.db()
    row = c.execute('SELECT state FROM lesson_runs WHERE id=?', (run['run_id'],)).fetchone()
    c.close()
    return json.loads(row['state'])


def finish(run, help_on_check=False, wrong_on_check=False):
    while run.get('teaching_step',5)<5:
        run=lessons.act(run['run_id'],run['index'],'teach_next',str(run['teaching_step']))
    while not run['done']:
        state = private_state(run)
        task = state['tasks'][run['index']]
        independent = run['index'] >= run['guided_count']
        if independent and help_on_check:
            run = lessons.act(run['run_id'], run['index'], 'hint')
        answer = str(task['answer'])
        if independent and wrong_on_check:
            answer = '9999999' if task['type']=='number' else next(k for k in task['choices'] if k != task['answer'])
        run = lessons.act(run['run_id'], run['index'], 'answer', answer)
        assert run['feedback']
        run = lessons.act(run['run_id'], run['index'], 'next')
    return run


@pytest.mark.parametrize('lesson_id', list(lessons.BY_ID))
def test_all_lessons_grade_resume_and_require_delayed_recall(isolated_db, monkeypatch, lesson_id):
    run = lessons.start(lesson_id)
    assert run == lessons.start(lesson_id)
    if run.get('teaching_step',5)<5:
        assert 'task' not in run
    else:
        assert not {'answer','explanation','wrong','hints'} & set(run['task'])
    done = finish(run)
    assert done['outcome']=='Independent check passed'
    assert done['independent_correct']==2
    again = lessons.start(lesson_id)
    assert again['mode']=='lesson'  # same-day repetition is not delayed retention
    assert private_state(again)['tasks'][3]['prompt'] != private_state(run)['tasks'][3]['prompt']
    finish(again)
    monkeypatch.setattr(lessons, '_now', lambda: datetime.now()+timedelta(days=2))
    recall = lessons.start(lesson_id)
    assert recall['mode']=='recall'
    assert recall['guided_count']==0
    assert finish(recall)['outcome']=='Recall confirmed'


def test_help_and_incorrect_answers_never_pass_independent_check(isolated_db):
    done = finish(lessons.start('special-order'), help_on_check=True)
    assert done['outcome']=='Needs reinforcement'
    assert done['independent_correct']==0
    done = finish(lessons.start('special-order'), wrong_on_check=True)
    assert done['outcome']=='Needs reinforcement'
    assert done['independent_correct']==0


def test_invalid_numbers_stale_requests_and_resubmission(isolated_db):
    run = lessons.start('cash-cycle')
    for step in range(5):
        run=lessons.act(run['run_id'],0,'teach_next',str(step))
    run = lessons.act(run['run_id'],0,'answer','dpo')
    # Correctness cannot be changed after the solution is shown.
    replay = lessons.act(run['run_id'],0,'answer','dio')
    assert replay==run
    run = lessons.act(run['run_id'],0,'next')
    stale = lessons.act(run['run_id'],0,'next')
    assert stale==run
    for invalid in ('NaN','inf','hello',''):
        with pytest.raises(ValueError):lessons.act(run['run_id'],1,'answer',invalid)
    assert len(private_state(run)['results'])==1
    hinted = lessons.act(run['run_id'],1,'hint')
    assert hinted['assisted']
    assert lessons.start('cash-cycle')['assisted']  # reload/device resumption


def test_content_arithmetic_across_parameter_ranges():
    for seed in range(100):
        for lesson in lessons.LESSONS:
            built=lessons.build_tasks(lesson['id'], random.Random(seed))
            assert len(built['guided'])==3 and len(built['check'])==2
            for task in built['guided']+built['check']:
                assert task['hints'] and task['explanation']
                if task['type']=='number':
                    assert isinstance(task['answer'], (int,float))
                else:
                    assert task['answer'] in task['choices']
        # Independent arithmetic oracle for each lesson's first numeric check.
        import re
        for lesson_id in lessons.BY_ID:
            task=lessons.build_tasks(lesson_id,random.Random(seed))['check'][0]
            n=[float(x.replace(',','')) for x in re.findall(r'\d[\d,]*(?:\.\d+)?',task['prompt'])]
            if lesson_id=='flexible-budget':expected=n[3]-(n[0]*n[1]+n[2])
            elif lesson_id=='absorption-variable':expected=(n[0]-n[1])*n[2]
            elif lesson_id=='special-order':expected=n[0]*(n[1]-n[2])-n[3]
            elif lesson_id=='cash-cycle':expected=n[0]+n[1]-n[2]
            else:expected=n[1]/(1+n[2]/100)-n[0]
            assert task['answer']==pytest.approx(expected)


def test_assisted_practice_not_mastery_and_early_review(isolated_db):
    q=engine.QUESTIONS[0]
    for _ in range(6):
        engine.grade(q['id'],q['answer'],3,'test',hint_level=2)
        skills.record_attempt(q,True,3,2)
    assert engine.question_status(q['id'])=='New'
    assert not adaptive.mastery_by_domain()
    snap=skills.snapshot()
    assert snap['priorities'][0]['status']!='Strong'
    assert snap['priorities'][0]['independent_attempts']==0
    adaptive.record_result(q['id'],True,3,hint_level=2)
    c=engine.db()
    state=c.execute('SELECT * FROM review_state WHERE question_id=?',(q['id'],)).fetchone()
    c.close()
    assert state['streak']==0
    assert state['interval_days']<=0.5
    engine.grade(q['id'],q['answer'],3,'test',hint_level=0)
    assert engine.question_status(q['id'])=='Learning'


def test_crosswalk_transparent_and_complete_at_subtopic_level():
    result=coverage.report()
    assert len(result['subtopics'])==41
    assert not result['unmapped_questions']
    assert result['question_count']==408
    assert 'Individual lettered' in result['scope']
    assert all(row['outcome_audit']=='Pending individual-outcome review' for row in result['subtopics'])
    for lesson in lessons.LESSONS:
        assert all(any(o.startswith(t['id']+'.') for t in result['subtopics']) for o in lesson['outcomes'])


def test_legacy_sqlite_migration_preserves_history(isolated_db):
    import sqlite3
    c=sqlite3.connect(isolated_db)
    c.execute('CREATE TABLE attempts(id INTEGER PRIMARY KEY,ts TEXT,question_id TEXT,part TEXT,domain TEXT,difficulty TEXT,selected TEXT,correct INTEGER,confidence INTEGER)')
    c.execute("INSERT INTO attempts VALUES(1,'2026-10-01','old','Part 1','Cost Management','Easy','A',1,3)")
    c.commit();c.close()
    c=engine.db()
    assert c.execute('SELECT correct,hint_level FROM attempts WHERE id=1').fetchone()['correct']==1
    assert c.execute('SELECT hint_level FROM attempts WHERE id=1').fetchone()['hint_level']==0
    c.close()


def test_lesson_api_and_existing_modes(isolated_db):
    from fastapi.testclient import TestClient
    (Path(__file__).parents[1]/'frontend/dist').mkdir(exist_ok=True)
    api=importlib.import_module('api')
    client=TestClient(api.app)
    assert client.get('/api/lessons?part=Part%202').status_code==200
    assert len(client.get('/api/lessons?part=Part%202').json()['lessons'])==3
    assert client.get('/api/coverage').json()['question_count']==408
    assert client.post('/api/lessons/start',json={'lesson_id':'unknown'}).status_code==400
    run=client.post('/api/lessons/start',json={'lesson_id':'flexible-budget'}).json()
    for step in range(5):
        run=client.post('/api/lessons/action',json={'run_id':run['run_id'],'index':0,'action':'teach_next','answer':str(step)}).json()
    response=client.post('/api/lessons/action',json={'run_id':run['run_id'],'index':0,'action':'answer','answer':'actual'})
    assert response.status_code==200 and response.json()['feedback']['correct']
    assert client.get('/api/dashboard').status_code==200
    assert client.get('/api/study-plan').status_code==200
    q=client.post('/api/question',json={'part':'Part 1'}).json()
    graded=client.post('/api/grade',json={'question_id':q['id'],'selected':q['answer'],'confidence':3,'hint_level':2})
    assert graded.status_code==200 and graded.json()['feedback']['assisted']
    exam=client.post('/api/exam/start',json={'part':'Part 1'}).json()
    assert len(exam['mcq_questions'])==100
    assert all('answer' not in q for q in exam['mcq_questions'])
    assert client.post('/api/exam/start',json={'part':'Part 2'}).status_code==400


@pytest.mark.parametrize('lesson_id', list(lessons.BY_ID))
def test_teaching_is_ungraded_resumable_and_gates_calculations(isolated_db, lesson_id):
    run=lessons.start(lesson_id)
    assert run['teaching_step']==0 and 'task' not in run
    with pytest.raises(ValueError,match='teaching pages'):
        lessons.act(run['run_id'],0,'answer','actual')
    moved=lessons.act(run['run_id'],0,'teach_next','0')
    assert moved['teaching_step']==1
    assert lessons.start(lesson_id)['teaching_step']==1
    assert lessons.act(run['run_id'],0,'teach_next','0')==moved
    back=lessons.act(run['run_id'],0,'teach_back','1')
    assert back['teaching_step']==0
    assert not private_state(back)['results']
    for step in range(5):
        run=lessons.act(run['run_id'],0,'teach_next',str(step))
    assert run['teaching_step']==5 and 'task' in run
    assert private_state(run)['results']==[]
    c=engine.db()
    assert c.execute('SELECT COUNT(*) AS n FROM attempts').fetchone()['n']==0
    c.close()


@pytest.mark.parametrize('lesson_id', list(lessons.BY_ID))
def test_old_lesson_history_is_preserved_but_revised_lesson_starts_fresh(isolated_db, lesson_id):
    c=engine.db()
    lessons._schema(c)
    old_state={'outcome':'Independent check passed','mode':'lesson','tasks':[], 'results':[]}
    c.execute('INSERT INTO lesson_runs(id,lesson_id,revision,started_at,completed_at,due_at,state) VALUES(?,?,?,?,?,?,?)',
              ('old-run',lesson_id,'guided-v1','2026-11-01','2026-11-01','2026-11-02',json.dumps(old_state)))
    c.commit();c.close()
    run=lessons.start(lesson_id)
    assert run['mode']=='lesson' and run['teaching_step']==0
    assert run['run_id']!='old-run'
    c=engine.db()
    assert c.execute('SELECT completed_at FROM lesson_runs WHERE id=?',('old-run',)).fetchone()['completed_at']=='2026-11-01'
    c.close()


@pytest.mark.parametrize('lesson_id', list(lessons.BY_ID))
def test_revisiting_teaching_during_independent_check_counts_as_help(isolated_db, lesson_id):
    run=lessons.start(lesson_id)
    for step in range(5):
        run=lessons.act(run['run_id'],0,'teach_next',str(step))
    for index in range(3):
        task=private_state(run)['tasks'][index]
        run=lessons.act(run['run_id'],index,'answer',str(task['answer']))
        run=lessons.act(run['run_id'],index,'next')
    assert run['stage']=='Independent check'
    run=lessons.act(run['run_id'],3,'teach_review')
    assert run['teaching_step']==0 and run['index']==3
    for step in range(5):
        run=lessons.act(run['run_id'],3,'teach_next',str(step))
    assert run['assisted']
    assert finish(run)['outcome']=='Needs reinforcement'



def test_all_starter_lessons_publish_teaching_version(isolated_db):
    rows=lessons.catalog()
    assert len(rows)==5
    assert all(row.get('teaching_version')=='reasoning-first' for row in rows)

def test_flexible_budget_v2_history_is_not_reset(isolated_db):
    run=lessons.start('flexible-budget')
    done=finish(run)
    catalog={row['id']:row for row in lessons.catalog()}
    assert catalog['flexible-budget']['status']=='Independent check passed'
    c=engine.db()
    assert c.execute('SELECT revision FROM lesson_runs WHERE id=?',(done['run_id'],)).fetchone()['revision']=='guided-v2-teaching'
    c.close()
