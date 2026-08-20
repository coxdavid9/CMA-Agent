import streamlit as st
from datetime import date
from cma_agent.engine import choose_question, grade, stats, plan, save_goal, recent

st.set_page_config(page_title="CMA Agent", page_icon="📘", layout="wide")
st.title("📘 CMA Agent")
st.caption("Your personal CMA study coach")

if "question" not in st.session_state:
    st.session_state.question = None
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "selected" not in st.session_state:
    st.session_state.selected = None

practice, dashboard, study = st.tabs(["Practice", "Dashboard", "Study Plan"])

with st.sidebar:
    st.header("Practice Settings")
    part = st.selectbox("CMA Part", ["Both", "Part 1", "Part 2"])
    difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    domain = st.selectbox("Domain", ["All"] + [
        "External Financial Reporting Decisions", "Planning, Budgeting, and Forecasting",
        "Performance Management", "Cost Management", "Internal Controls", "Technology and Analytics",
        "Financial Statement Analysis", "Corporate Finance", "Business Decision Analysis",
        "Enterprise Risk Management", "Capital Investment Decisions", "Professional Ethics"])

with practice:
    st.subheader("Adaptive Practice")
    if st.button("🎯 Give Me a Question", type="primary", use_container_width=True):
        st.session_state.question = choose_question(part, domain, difficulty)
        st.session_state.submitted = False
        st.session_state.selected = None
        st.rerun()

    q = st.session_state.question
    if q:
        st.markdown(f"**{q['part']} · {q['domain']} · {q['difficulty']}**")
        st.markdown(f"### {q['question']}")
        answer = st.radio("Select your answer", list(q["choices"].keys()), format_func=lambda x: f"{x}. {q['choices'][x]}", key="answer")
        if not st.session_state.submitted and st.button("Submit Answer", type="primary", use_container_width=True):
            ok, graded = grade(q["id"], answer)
            st.session_state.submitted = True
            st.session_state.selected = answer
            st.session_state.result = (ok, graded)
            st.rerun()
        if st.session_state.submitted:
            ok, graded = st.session_state.result
            if ok: st.success("✅ Correct!")
            else: st.error(f"❌ Incorrect. Correct answer: {graded['answer']}")
            st.markdown("### Explanation")
            st.write(graded["explanation"])
            if graded.get("calculation"):
                st.markdown("### Calculation")
                st.code(graded["calculation"])
            if st.button("Next Question →", type="primary", use_container_width=True):
                st.session_state.question = choose_question(part, domain, difficulty)
                st.session_state.submitted = False
                st.rerun()
    else:
        st.info("Choose your settings and start a practice question.")

with dashboard:
    s = stats()
    a,b,c = st.columns(3)
    a.metric("Questions Attempted", s["attempted"])
    b.metric("Accuracy", f"{s['accuracy']}%")
    c.metric("Question Bank", s["question_bank_size"])
    st.subheader("Mastery by Domain")
    for row in s["mastery"]:
        icon = {"New":"⚪", "Learning":"🟡", "Weak":"🔴", "Mastered":"🟢"}[row["status"]]
        st.write(f"{icon} **{row['domain']}** — {row['status']}")
    st.subheader("Recent Attempts")
    history = recent()
    if history: st.dataframe(history, use_container_width=True)
    else: st.info("No practice history yet.")

with study:
    st.subheader("Personalized Study Plan")
    with st.form("goal_form"):
        target = st.date_input("Target exam date", value=date.today())
        goal_part = st.selectbox("Part", ["Part 1", "Part 2", "Both"])
        minutes = st.number_input("Daily study minutes", min_value=10, max_value=240, value=30, step=5)
        if st.form_submit_button("Save Goal", type="primary"):
            save_goal(target.isoformat(), goal_part, int(minutes))
            st.success("Study goal saved.")
    p = plan()
    if "message" not in p:
        x,y = st.columns(2)
        x.metric("Days Remaining", p["days_remaining"])
        y.metric("Daily Minutes", p["daily_minutes"])
        st.markdown("### Focus Areas")
        for topic in p["focus_topics"]: st.write(f"🎯 {topic}")
        st.markdown("### Suggested Session")
        for item in p["session"]: st.write(f"• {item}")
    else:
        st.info("Save your exam target and daily study time to generate a plan.")
