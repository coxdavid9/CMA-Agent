import streamlit as st
from datetime import date

from cma_agent.engine import (
    choose_question,
    choose_followup,
    grade,
    learning_feedback,
    learning_snapshot,
    stats,
    plan,
    save_goal,
    get_preferences,
    save_preferences,
    save_resume_question,
    clear_resume_question,
    get_question,
    goal,
    goal_history,
    get_or_start_session,
    start_new_session,
    session_stats,
)
from cma_agent.question_utils import clean_question

st.set_page_config(page_title="CMA Coach", page_icon="📘", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
.block-container { max-width:1180px; padding-top:1.5rem; padding-bottom:3rem; }
.hero { padding:8px 0 18px; }
.hero h1 { font-size:2.45rem; margin:0; letter-spacing:-1.2px; }
.hero p { color:#667085; margin:5px 0 0; font-size:1.02rem; }
.eyebrow { color:#475467; font-size:.78rem; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
.section { font-size:1.22rem; font-weight:750; margin:24px 0 8px; }
.muted { color:#667085; }
.card { border:1px solid #e4e7ec; border-radius:16px; padding:20px; background:#fff; margin:10px 0; }
.question { background:#f8fafc; border-left:5px solid #344054; padding:24px; }
.meta { font-size:.82rem; color:#667085; font-weight:700; margin-bottom:12px; }
.qtext { font-size:1.34rem; line-height:1.55; font-weight:650; color:#101828; }
.stat { border:1px solid #e4e7ec; border-radius:15px; padding:17px; background:#fff; min-height:92px; }
.label { font-size:.78rem; color:#667085; font-weight:700; text-transform:uppercase; letter-spacing:.04em; }
.value { font-size:1.75rem; font-weight:800; color:#101828; margin-top:3px; }
.coach { border:1px solid #d0d5dd; border-radius:16px; padding:22px; background:#fff; margin-top:18px; }
.takeaway { border-radius:12px; padding:13px 15px; background:#f0f9ff; border:1px solid #b9e6fe; line-height:1.45; }
.session-pill { display:inline-block; border:1px solid #d0d5dd; border-radius:999px; padding:5px 10px; color:#475467; font-size:.78rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# Only initialize the persistent session once per browser session.
# Previously this hit Supabase on every Streamlit rerun, including widget changes.
if "session_id" not in st.session_state:
    st.session_state.session_id = get_or_start_session()

prefs = get_preferences()

for key, value in {
    "question": get_question(prefs.get("resume_question_id")) if prefs.get("resume_question_id") else None,
    "submitted": False,
    "selected": None,
    "confidence_value": 0,
    "result": None,
    "part_setting": prefs["part"],
    "difficulty_setting": prefs["difficulty"],
    "domain_setting": prefs["domain"],
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown('<div class="hero"><div class="eyebrow">Adaptive CMA Study</div><h1>📘 CMA Coach</h1><p>Your personal CMA learning coach — practice, learn, and improve.</p></div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### Practice Settings")
    part = st.selectbox("CMA Part", ["Both", "Part 1", "Part 2"], key="part_setting")
    difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"], key="difficulty_setting")
    p1 = ["External Financial Reporting Decisions", "Planning, Budgeting, and Forecasting", "Performance Management", "Cost Management", "Internal Controls", "Technology and Analytics"]
    p2 = ["Financial Statement Analysis", "Corporate Finance", "Business Decision Analysis", "Enterprise Risk Management", "Capital Investment Decisions", "Professional Ethics"]
    opts = ["All"] + (p1 if part == "Part 1" else p2 if part == "Part 2" else p1 + p2)
    if st.session_state.domain_setting not in opts:
        st.session_state.domain_setting = "All"
    domain = st.selectbox("Domain", opts, key="domain_setting")
    settings_changed = part != prefs["part"] or difficulty != prefs["difficulty"] or domain != prefs["domain"]
    if settings_changed:
        clear_resume_question()
        st.session_state.question = None
        st.session_state.submitted = False
        st.session_state.selected = None
        st.session_state.confidence_value = 0
        st.session_state.result = None
        save_preferences(part, difficulty, domain)
    st.caption("✓ Settings saved automatically")
    if st.session_state.question:
        st.divider()
        st.caption("Current question")
        st.write(f"**{st.session_state.question['domain']}**")
        st.caption("Your session resets after 30 minutes of inactivity.")

practice, dashboard, study = st.tabs(["Practice", "Dashboard", "Study Plan"])

with practice:
    st.markdown('<div class="section">Adaptive Practice</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">The goal is to learn the concept behind the question, not just improve the score.</div>', unsafe_allow_html=True)
    current = session_stats(st.session_state.session_id)
    st.markdown(f'<span class="session-pill">Session · {current["attempted"]} answered</span>', unsafe_allow_html=True)

    q = st.session_state.question
    if q is None:
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.info("Choose your settings, then start a practice session.")
        if st.button("🎯 Start Practice", type="primary", use_container_width=True):
            q = choose_question(part, domain, difficulty)
            st.session_state.question = q
            st.session_state.submitted = False
            st.session_state.selected = None
            st.session_state.confidence_value = 0
            st.session_state.result = None
            save_resume_question(q["id"])
            st.rerun()

    if q is not None:
        st.markdown(f'<div class="card question"><div class="meta">{q["part"]} · {q["domain"]} · {q["difficulty"]}</div><div class="qtext">{clean_question(q["question"])}</div></div>', unsafe_allow_html=True)
        if not st.session_state.submitted:
            with st.form(f"answer_form_{q['id']}"):
                answer = st.radio("Your answer", list(q["choices"].keys()), format_func=lambda x: f"{x}. {q['choices'][x]}")
                confidence = st.radio("How sure are you?", [1, 2, 3], format_func=lambda x: {1:"🔴 Not sure", 2:"🟡 Somewhat sure", 3:"🟢 Very sure"}[x], horizontal=True)
                submitted = st.form_submit_button("Submit Answer", type="primary", use_container_width=True)
            if submitted:
                ok, graded = grade(q["id"], answer, confidence, st.session_state.session_id)
                st.session_state.submitted = True
                st.session_state.selected = answer
                st.session_state.confidence_value = confidence
                st.session_state.result = (ok, graded)
                st.rerun()
        else:
            ok, graded = st.session_state.result
            fb = learning_feedback(q["id"], st.session_state.selected, st.session_state.confidence_value)
            st.markdown('<div class="coach"><div class="meta">🧠 COACH REVIEW</div>', unsafe_allow_html=True)
            if ok:
                st.success("Correct — now make sure you know why.")
            else:
                st.error(f"Incorrect. Correct answer: **{graded['answer']}**")
            st.markdown(f"**{fb['diagnosis']}**")
            st.write(fb["advice"])
            st.markdown("**The concept**")
            st.write(fb["explanation"])
            if fb.get("calculation"):
                st.markdown("**Calculation**")
                st.code(fb["calculation"])
            st.markdown("**Remember**")
            st.markdown(f'<div class="takeaway">{fb["takeaway"]}</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            if not ok:
                st.caption("Don't immediately move on. The next question should prove you can apply the concept.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🎯 Practice This Concept", type="primary", use_container_width=True):
                    nxt = choose_followup(q["id"], st.session_state.selected, part, difficulty)
                    st.session_state.question = nxt
                    st.session_state.submitted = False
                    st.session_state.selected = None
                    st.session_state.confidence_value = 0
                    st.session_state.result = None
                    save_resume_question(nxt["id"])
                    st.rerun()
            with c2:
                if st.button("Next Mixed Question", use_container_width=True):
                    nxt = choose_question(part, domain, difficulty, exclude=[q["id"]])
                    st.session_state.question = nxt
                    st.session_state.submitted = False
                    st.session_state.selected = None
                    st.session_state.confidence_value = 0
                    st.session_state.result = None
                    save_resume_question(nxt["id"])
                    st.rerun()

with dashboard:
    s = stats()
    snap = learning_snapshot()
    current = session_stats(st.session_state.session_id)
    st.markdown('<div class="section">Current Session</div>', unsafe_allow_html=True)
    a, b = st.columns(2)
    a.markdown(f'<div class="stat"><div class="label">Questions This Session</div><div class="value">{current["attempted"]}</div></div>', unsafe_allow_html=True)
    b.markdown(f'<div class="stat"><div class="label">Session Accuracy</div><div class="value">{current["accuracy"]}%</div></div>', unsafe_allow_html=True)
    st.caption("Session resets automatically after 30 minutes of inactivity.")
    if st.button("↻ Start New Session Now", use_container_width=True):
        st.session_state.session_id = start_new_session()
        st.session_state.question = None
        st.session_state.submitted = False
        st.session_state.selected = None
        st.session_state.confidence_value = 0
        st.session_state.result = None
        clear_resume_question()
        st.rerun()
    st.markdown('<div class="section">Historical Progress</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3)
    a.markdown(f'<div class="stat"><div class="label">Lifetime Accuracy</div><div class="value">{s["accuracy"]}%</div></div>', unsafe_allow_html=True)
    b.markdown(f'<div class="stat"><div class="label">Questions Completed</div><div class="value">{s["attempted"]}</div></div>', unsafe_allow_html=True)
    c.markdown(f'<div class="stat"><div class="label">Question Bank</div><div class="value">{s["question_bank_size"]}</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="section">What To Study Next</div>', unsafe_allow_html=True)
    if snap["weak_domains"]:
        for topic in snap["weak_domains"]:
            st.markdown(f'<div class="card"><strong>🔴 {topic}</strong><br><span class="muted">Below your current learning threshold — prioritize this area.</span></div>', unsafe_allow_html=True)
    elif snap["fragile_domains"]:
        for topic in snap["fragile_domains"]:
            st.markdown(f'<div class="card"><strong>🟡 {topic}</strong><br><span class="muted">You are getting these right, but confidence is still fragile.</span></div>', unsafe_allow_html=True)
    else:
        st.info("Keep practicing. The coach will identify priorities as your history grows.")
    st.markdown('<div class="section">Mastery by Domain</div>', unsafe_allow_html=True)
    icons = {"New":"⚪", "Learning":"🟡", "Weak":"🔴", "Mastered":"🟢"}
    bars = {"New":0.0, "Learning":0.6, "Weak":0.35, "Mastered":1.0}
    for row in s["mastery"]:
        st.write(f"{icons[row['status']]} **{row['domain']}** · {row['status']}")
        st.progress(bars[row["status"]])
    with st.expander("Recent mistakes"):
        if snap["recent_misses"]:
            for miss in snap["recent_misses"]:
                st.write(f"• **{miss['domain']}** · confidence {miss['confidence']}/3")
        else:
            st.write("No missed questions yet.")

with study:
    st.markdown('<div class="section">Current Study Plan</div>', unsafe_allow_html=True)
    g = goal()
    if g:
        st.info(f"📅 Exam target: **{g['target_date']}** · **{g['part']}** · **{g['daily_minutes']} minutes/day**")
    with st.form("goal_form"):
        target = st.date_input("Target exam date", value=date.fromisoformat(g["target_date"]) if g else date.today(), key="study_target_date")
        parts = ["Part 1", "Part 2", "Both"]
        gp = st.selectbox("Part", parts, index=parts.index(g["part"]) if g else 0, key="study_part")
        mins = st.number_input("Daily study minutes", min_value=10, max_value=240, value=int(g["daily_minutes"]) if g else 30, step=5, key="study_minutes")
        if st.form_submit_button("Save Study Goal", type="primary"):
            save_goal(target.isoformat(), gp, int(mins))
            st.success("Current study plan saved.")
            st.rerun()
    p = plan()
    if "message" not in p:
        a, b = st.columns(2)
        a.markdown(f'<div class="stat"><div class="label">Days Remaining</div><div class="value">{p["days_remaining"]}</div></div>', unsafe_allow_html=True)
        b.markdown(f'<div class="stat"><div class="label">Daily Target</div><div class="value">{p["daily_minutes"]} min</div></div>', unsafe_allow_html=True)
        st.markdown('<div class="section">Focus Areas</div>', unsafe_allow_html=True)
        for topic in p["focus_topics"]:
            st.markdown(f'<div class="card">🎯 <strong>{topic}</strong></div>', unsafe_allow_html=True)
        st.markdown('<div class="section">Suggested Session</div>', unsafe_allow_html=True)
        for item in p["session"]:
            st.write(f"• {item}")
    else:
        st.info("Set your exam target and daily study time to generate a plan.")
    history = goal_history()
    st.markdown('<div class="section">Historical Study Plans</div>', unsafe_allow_html=True)
    if history:
        for item in history:
            st.markdown(f'<div class="card"><strong>📚 {item["target_date"]} · {item["part"]} · {item["daily_minutes"]} min/day</strong><br><span class="muted">{item["created_at"]}</span></div>', unsafe_allow_html=True)
    else:
        st.caption("No previous study plans saved yet.")
