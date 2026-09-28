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
.hero { background:linear-gradient(120deg,#1e1b4b 0%,#312e81 55%,#4c1d95 100%); border-radius:22px; padding:28px 32px; color:#fff; margin-bottom:8px; box-shadow:0 12px 30px rgba(30,27,75,.22); position:relative; overflow:hidden; }
.hero::after { content:""; position:absolute; right:-70px; top:-70px; width:260px; height:260px; background:radial-gradient(circle,rgba(167,139,250,.35),transparent 70%); pointer-events:none; }
.hero .eyebrow { color:#c4b5fd; font-size:.75rem; font-weight:700; text-transform:uppercase; letter-spacing:.12em; }
.hero h1 { font-size:2.1rem; margin:6px 0 0; letter-spacing:-.02em; color:#fff; }
.hero p { color:#d6d0f5; margin:8px 0 0; font-size:1rem; max-width:640px; line-height:1.55; }
.hero-pills { display:flex; gap:10px; margin-top:18px; flex-wrap:wrap; position:relative; z-index:1; }
.hero-pill { background:rgba(255,255,255,.1); border:1px solid rgba(255,255,255,.16); border-radius:999px; padding:7px 15px; font-size:.82rem; font-weight:700; color:#fff; }
.section { font-size:1.22rem; font-weight:750; margin:24px 0 8px; color:#1a1d2e; }
.muted { color:#667085; }
.card { border:1px solid #e4e7ec; border-radius:16px; padding:20px; background:#fff; margin:10px 0; }
.question { background:#fff; border:1px solid #eef0f7; border-radius:22px; padding:30px; margin:14px 0; box-shadow:0 12px 34px rgba(30,27,75,.09); }
.meta { display:flex; gap:8px; margin-bottom:16px; flex-wrap:wrap; }
.tag { font-size:.72rem; font-weight:800; letter-spacing:.05em; text-transform:uppercase; padding:6px 13px; border-radius:999px; }
.tag-part { background:#f1f2f7; color:#6b7194; }
.tag-domain { background:#eef0fe; color:#4338ca; }
.tag-hard { background:#fef3e2; color:#b45309; }
.tag-medium { background:#fffbeb; color:#92400e; }
.tag-easy { background:#ecfdf5; color:#047857; }
.qtext { font-size:1.3rem; line-height:1.6; font-weight:650; color:#14172a; }
.why-line { margin-top:14px; padding:11px 15px; border-radius:12px; background:#f6f4ff; border:1px dashed #c9bdf5; font-size:.85rem; color:#5b21b6; line-height:1.5; }
.stat { border:1px solid #e9ecf4; border-radius:18px; padding:17px; background:#fff; min-height:92px; box-shadow:0 6px 18px rgba(30,27,75,.06); }
.label { font-size:.78rem; color:#667085; font-weight:700; text-transform:uppercase; letter-spacing:.04em; }
.value { font-size:1.75rem; font-weight:800; color:#101828; margin-top:3px; }
.coach { border:1px solid #e9ecf4; border-radius:20px; padding:24px; background:#fff; margin-top:18px; box-shadow:0 10px 28px rgba(30,27,75,.08); }
.takeaway { border-radius:12px; padding:13px 15px; background:#f0f9ff; border:1px solid #b9e6fe; line-height:1.45; }
.session-pill { display:inline-block; background:#fff; border:1px solid #e4e7ec; border-radius:999px; padding:7px 15px; color:#475467; font-size:.8rem; font-weight:700; box-shadow:0 1px 3px rgba(26,29,46,.05); }
div[data-testid="stRadio"] > div[role="radiogroup"] > label { background:#fff; border:1.5px solid #e8eaf3; border-radius:14px; padding:12px 16px; font-weight:600; color:#23263d; transition:border-color .15s, background .15s, box-shadow .15s; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:hover { border-color:#b9b3f0; background:#fafaff; }
div[data-testid="stRadio"] > div[role="radiogroup"] > label:has(input:checked) { border-color:#6d28d9; background:#f6f3ff; box-shadow:0 4px 14px rgba(109,40,217,.14); }
button[kind="primary"], button[data-testid="stBaseButton-primary"] { background:linear-gradient(120deg,#6d28d9,#4c1d95) !important; border:none !important; border-radius:14px !important; font-weight:800 !important; box-shadow:0 8px 22px rgba(109,40,217,.35) !important; }
button[data-baseweb="tab"] { font-weight:700 !important; color:#6b7194 !important; }
button[data-baseweb="tab"][aria-selected="true"] { color:#4338ca !important; }
[data-testid="stSidebar"] { background:#fff; }
.side-brand { display:flex; align-items:center; gap:10px; margin-bottom:14px; }
.side-mark { width:38px; height:38px; border-radius:11px; background:linear-gradient(135deg,#312e81,#6d28d9); display:flex; align-items:center; justify-content:center; color:#fff; font-weight:800; font-size:18px; box-shadow:0 4px 12px rgba(109,40,217,.35); }
.side-name { font-weight:800; font-size:16px; letter-spacing:-.02em; color:#1a1d2e; }
.side-sub { font-size:10.5px; color:#8a8fa8; font-weight:700; text-transform:uppercase; letter-spacing:.08em; }
@media (max-width:640px) { .hero { padding:22px 20px; } .hero h1 { font-size:1.7rem; } .question { padding:22px 18px; } }
</style>
""", unsafe_allow_html=True)

# Only initialize the persistent session once per browser session.
# Previously this hit Supabase on every Streamlit rerun, including widget changes.
if "session_id" not in st.session_state:
    st.session_state.session_id = get_or_start_session()

prefs = get_preferences()

# Real-data pills for the hero header (stats() already runs every rerun via the dashboard).
_perf_stats = stats()
_perf_snap = learning_snapshot()

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

_hero_pills = []
if _perf_stats["attempted"] > 0:
    _hero_pills.append(f'📊 {_perf_stats["accuracy"]}% lifetime accuracy')
if _perf_snap["weak_domains"]:
    _hero_pills.append(f'🎯 Focus: {_perf_snap["weak_domains"][0]}')
_hero_pills.append(f'📚 {_perf_stats["question_bank_size"]} questions in bank')
_hero_pills_html = "".join(f'<span class="hero-pill">{p}</span>' for p in _hero_pills)
st.markdown(
    '<div class="hero"><div class="eyebrow">Adaptive CMA Study</div><h1>CMA Coach</h1>'
    '<p>Your personal CMA learning coach — practice, learn, and improve.</p>'
    f'<div class="hero-pills">{_hero_pills_html}</div></div>',
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown('<div class="side-brand"><div class="side-mark">C</div><div><div class="side-name">CMA Coach</div><div class="side-sub">Adaptive Study</div></div></div>', unsafe_allow_html=True)
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
    st.markdown(f'<span class="session-pill">{current["attempted"]} answered this session</span>', unsafe_allow_html=True)

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
        _diff_class = {"Hard": "tag-hard", "Medium": "tag-medium", "Easy": "tag-easy"}.get(q["difficulty"], "tag-part")
        _why = ""
        if q["domain"] in _perf_snap["weak_domains"]:
            _why = f'<div class="why-line">Showing you this because <strong>{q["domain"]}</strong> is one of your weakest areas.</div>'
        elif any(m.get("domain") == q["domain"] for m in _perf_snap["recent_misses"]):
            _why = f'<div class="why-line">Showing you this because you missed a <strong>{q["domain"]}</strong> question recently — time for a rematch.</div>'
        st.markdown(
            f'<div class="card question"><div class="meta"><span class="tag tag-part">{q["part"]}</span>'
            f'<span class="tag tag-domain">{q["domain"]}</span><span class="tag {_diff_class}">{q["difficulty"]}</span></div>'
            f'<div class="qtext">{clean_question(q["question"])}</div>{_why}</div>',
            unsafe_allow_html=True,
        )
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
