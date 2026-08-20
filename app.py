import streamlit as st
from datetime import date
from cma_agent.engine import choose_question, choose_followup, grade, learning_feedback, learning_snapshot, stats, plan, save_goal, get_preferences, save_preferences, save_resume_question, clear_resume_question, get_question, goal

st.set_page_config(page_title='CMA Agent', page_icon='📘', layout='wide', initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{max-width:1180px;padding-top:1.8rem}.hero{padding-bottom:14px}.hero h1{font-size:2.35rem;margin:0;letter-spacing:-1px}.hero p,.muted{color:#667085}.card{border:1px solid #e4e7ec;border-radius:16px;padding:20px;background:#fff;margin:10px 0}.question{background:#f8fafc}.meta{font-size:.82rem;color:#667085;font-weight:650;margin-bottom:10px}.qtext{font-size:1.25rem;line-height:1.55;font-weight:650}.stat{border:1px solid #e4e7ec;border-radius:14px;padding:16px;background:#fff}.label{font-size:.8rem;color:#667085;font-weight:650}.value{font-size:1.75rem;font-weight:750;color:#101828}.section{font-size:1.25rem;font-weight:700;margin:24px 0 8px}
</style>''', unsafe_allow_html=True)

prefs=get_preferences()
initial_q=get_question(prefs.get('resume_question_id')) if prefs.get('resume_question_id') else None
for k,v in {'question':initial_q,'submitted':False,'selected':None,'confidence_value':0,'result':None,'part_setting':prefs['part'],'difficulty_setting':prefs['difficulty'],'domain_setting':prefs['domain']}.items():
    if k not in st.session_state: st.session_state[k]=v

st.markdown('<div class="hero"><h1>📘 CMA Agent</h1><p>Your personal CMA learning coach — practice, learn, and retest.</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown('### Practice Settings')
    part=st.selectbox('CMA Part',['Both','Part 1','Part 2'],key='part_setting')
    difficulty=st.selectbox('Difficulty',['All','Easy','Medium','Hard'],key='difficulty_setting')
    p1=['External Financial Reporting Decisions','Planning, Budgeting, and Forecasting','Performance Management','Cost Management','Internal Controls','Technology and Analytics']
    p2=['Financial Statement Analysis','Corporate Finance','Business Decision Analysis','Enterprise Risk Management','Capital Investment Decisions','Professional Ethics']
    opts=['All']+(p1 if part=='Part 1' else p2 if part=='Part 2' else p1+p2)
    if st.session_state.domain_setting not in opts: st.session_state.domain_setting='All'
    domain=st.selectbox('Domain',opts,key='domain_setting')
    save_preferences(part,difficulty,domain)
    st.caption('✓ Settings saved automatically')
    if st.session_state.question:
        st.divider(); st.caption('Current session'); st.write(f"**{st.session_state.question['domain']}**"); st.caption('Question saved — you can close the app and resume later.')

practice,dashboard,study=st.tabs(['Practice','Dashboard','Study Plan'])

with practice:
    st.markdown('<div class="section">Adaptive Practice</div>',unsafe_allow_html=True)
    st.markdown('<div class="muted">The goal is to learn the concept behind the question, not just improve the score.</div>',unsafe_allow_html=True)
    q=st.session_state.question
    if q is None:
        if st.button('🎯 Start Practice',type='primary',use_container_width=True):
            q=choose_question(part,domain,difficulty); st.session_state.question=q; st.session_state.submitted=False; st.session_state.selected=None; st.session_state.confidence_value=0; st.session_state.result=None; save_resume_question(q['id']); st.rerun()
    else:
        st.markdown(f'<div class="card question"><div class="meta">{q["part"]} · {q["domain"]} · {q["difficulty"]}</div><div class="qtext">{q["question"]}</div></div>',unsafe_allow_html=True)
        answer=st.radio('Your answer',list(q['choices'].keys()),format_func=lambda x:f"{x}. {q['choices'][x]}",key=f"answer_{q['id']}",disabled=st.session_state.submitted)
        confidence=st.radio('How sure are you?',[1,2,3],format_func=lambda x:{1:'🔴 Not sure',2:'🟡 Somewhat sure',3:'🟢 Very sure'}[x],horizontal=True,label_visibility='visible',key=f"confidence_{q['id']}",disabled=st.session_state.submitted)
        st.session_state.confidence_value=confidence
        if not st.session_state.submitted:
            if st.button('Submit Answer',type='primary',use_container_width=True):
                ok,graded=grade(q['id'],answer,confidence); st.session_state.submitted=True; st.session_state.selected=answer; st.session_state.confidence_value=confidence; st.session_state.result=(ok,graded); st.rerun()
        else:
            ok,graded=st.session_state.result; fb=learning_feedback(q['id'],st.session_state.selected,st.session_state.confidence_value)
            st.markdown('<div class="card"><div class="meta">🧠 COACH REVIEW</div>',unsafe_allow_html=True)
            if ok: st.success('Correct — now make sure you know why.')
            else: st.error(f"Incorrect. Correct answer: **{graded['answer']}**")
            st.markdown(f"**{fb['diagnosis']}**")
            st.write(fb['advice'])
            st.markdown('**The concept**'); st.write(fb['explanation'])
            if fb.get('calculation'): st.markdown('**Calculation**'); st.code(fb['calculation'])
            st.markdown('**Remember**'); st.success(fb['takeaway'])
            st.markdown('</div>',unsafe_allow_html=True)
            if not ok: st.caption("Don't immediately move on. The next question should prove you can apply the concept.")
            c1,c2=st.columns(2)
            with c1:
                if st.button('🎯 Practice This Concept',type='primary',use_container_width=True):
                    nxt=choose_followup(q['id'],st.session_state.selected,part,difficulty); st.session_state.question=nxt; st.session_state.submitted=False; st.session_state.selected=None; st.session_state.confidence_value=0; st.session_state.result=None; save_resume_question(nxt['id']); st.rerun()
            with c2:
                if st.button('Next Mixed Question',use_container_width=True):
                    nxt=choose_question(part,domain,difficulty,exclude=[q['id']]); st.session_state.question=nxt; st.session_state.submitted=False; st.session_state.selected=None; st.session_state.confidence_value=0; st.session_state.result=None; save_resume_question(nxt['id']); st.rerun()
            if st.button('✓ Finish Session',use_container_width=True):
                st.session_state.question=None; st.session_state.submitted=False; st.session_state.selected=None; st.session_state.result=None; clear_resume_question(); st.rerun()

with dashboard:
    s=stats(); snap=learning_snapshot()
    st.markdown('<div class="section">Your CMA Progress</div>',unsafe_allow_html=True)
    a,b,c=st.columns(3)
    a.markdown(f'<div class="stat"><div class="label">Accuracy</div><div class="value">{s["accuracy"]}%</div></div>',unsafe_allow_html=True)
    b.markdown(f'<div class="stat"><div class="label">Questions Completed</div><div class="value">{s["attempted"]}</div></div>',unsafe_allow_html=True)
    c.markdown(f'<div class="stat"><div class="label">Question Bank</div><div class="value">{s["question_bank_size"]}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="section">What To Study Next</div>',unsafe_allow_html=True)
    if snap['weak_domains']:
        for t in snap['weak_domains']: st.markdown(f'<div class="card"><strong>🔴 {t}</strong><br><span class="muted">Below your current learning threshold — prioritize this area.</span></div>',unsafe_allow_html=True)
    elif snap['fragile_domains']:
        for t in snap['fragile_domains']: st.markdown(f'<div class="card"><strong>🟡 {t}</strong><br><span class="muted">You are getting these right, but confidence is still fragile.</span></div>',unsafe_allow_html=True)
    else: st.info('Keep practicing. The coach will identify priorities as your history grows.')
    st.markdown('<div class="section">Mastery by Domain</div>',unsafe_allow_html=True)
    icons={'New':'⚪','Learning':'🟡','Weak':'🔴','Mastered':'🟢'}; bars={'New':0,'Learning':.6,'Weak':.35,'Mastered':1}
    for row in s['mastery']:
        st.write(f"{icons[row['status']]} **{row['domain']}** · {row['status']}"); st.progress(bars[row['status']])
    with st.expander('Recent mistakes'):
        if snap['recent_misses']:
            for m in snap['recent_misses']: st.write(f"• **{m['domain']}** · confidence {m['confidence']}/3")
        else: st.write('No missed questions yet.')

with study:
    st.markdown('<div class="section">Your Study Plan</div>',unsafe_allow_html=True)
    g=goal()
    with st.form('goal_form'):
        target=st.date_input('Target exam date',value=date.fromisoformat(g['target_date']) if g else date.today())
        parts=['Part 1','Part 2','Both']; gp=st.selectbox('Part',parts,index=parts.index(g['part']) if g else 0)
        mins=st.number_input('Daily study minutes',min_value=10,max_value=240,value=int(g['daily_minutes']) if g else 30,step=5)
        if st.form_submit_button('Save Study Goal',type='primary'): save_goal(target.isoformat(),gp,int(mins)); st.success('Study goal saved.'); st.rerun()
    p=plan()
    if 'message' not in p:
        a,b=st.columns(2); a.markdown(f'<div class="stat"><div class="label">Days Remaining</div><div class="value">{p["days_remaining"]}</div></div>',unsafe_allow_html=True); b.markdown(f'<div class="stat"><div class="label">Daily Target</div><div class="value">{p["daily_minutes"]} min</div></div>',unsafe_allow_html=True)
        st.markdown('<div class="section">Focus Areas</div>',unsafe_allow_html=True)
        for t in p['focus_topics']: st.markdown(f'<div class="card">🎯 <strong>{t}</strong></div>',unsafe_allow_html=True)
        st.markdown('<div class="section">Suggested Session</div>',unsafe_allow_html=True)
        for item in p['session']: st.write(f'• {item}')
    else: st.info('Set your exam target and daily study time to generate a plan.')
