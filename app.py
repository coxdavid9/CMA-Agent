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
    recent,
)

st.set_page_config(page_title="CMA Agent", page_icon="📘", layout="wide")
st.title("📘 CMA Agent")
st.caption("Your personal CMA learning coach — practice, learn, and retest.")

for key, default in {
    "question": None,
    "submitted": False,
    "selected": None,
    "confidence": 0,
    "result": None,
    "followup": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

practice, dashboard, study = st.tabs(["Practice", "Dashboard", "Study Plan"])

with st.sidebar:
    st.header("Practice Settings")
    part = st.selectbox("CMA Part", ["Both", "Part 1", "Part 2"])
    difficulty = st.selectbox("Difficulty", ["All", "Easy", "Medium", "Hard"])
    domain = st.selectbox("Domain", ["All"] + [
        "External Financial Reporting Decisions", "Planning, Budgeting, and Forecasting",
        "Performance Management", "Cost Management", "Internal Controls", "Technology and Analytics",
        "Financial Statement Analysis", "Corporate Finance", "Business Decision Analysis",
        "Enterprise Risk Management", "Capital Investment Decisions", "Professional Ethics"
    ])

with practice:
    st.subheader("Adaptive Practice")
    st.write("The goal is not just to get questions right. It is to learn the concepts behind them.")

    if st.button("🎯 Give Me a Question", type="primary", use_container_width=True):
        st.session_state.question = choose_question(part, domain, difficulty)
        st.session_state.submitted = False
        st.session_state.selected = None
        st.session_state.confidence = 0
        st.session_state.result = None
        st.session_state.followup = None
        st.rerun()

    q = st.session_state.question
    if q:
        st.markdown(f"**{q['part']} · {q['domain']} · {q['difficulty']}**")
        st.markdown(f"### {q['question']}")
        answer = st.radio(
            "Select your answer",
            list(q["choices"].keys()),
            format_func=lambda x: f"{x}. {q['choices'][x]}",
            key="answer",
        )

        confidence = st.radio(
            "How confident are you?",
            [1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 — Guessing",
                2: "2 — Not sure",
                3: "3 — Somewhat confident",
                4: "4 — Confident",
                5: "5 — Very confident",
            }[x],
            horizontal=True,
            key="confidence",
        )

        if not st.session_state.submitted and st.button(
            "Submit & Learn", type="primary", use_container_width=True
        ):
            ok, graded = grade(q["id"], answer, confidence)
            st.session_state.submitted = True
            st.session_state.selected = answer
            st.session_state.result = (ok, graded)
            st.rerun()

        if st.session_state.submitted:
            ok, graded = st.session_state.result
            feedback = learning_feedback(
                q["id"], st.session_state.selected, st.session_state.confidence
            )

            if ok:
                st.success("✅ Correct!")
            else:
                st.error(f"❌ Incorrect. Correct answer: {graded['answer']}")

            st.markdown("## 🧠 Coach Review")
            st.info(f"**Diagnosis: {feedback['diagnosis']}**\n\n{feedback['advice']}")

            st.markdown("### The concept")
            st.write(feedback["explanation"])

            if feedback.get("calculation"):
                st.markdown("### Calculation")
                st.code(feedback["calculation"])

            st.markdown("### Key takeaway")
            st.success(feedback["takeaway"])

            if not ok:
                st.markdown("### Your next step")
                st.write(
                    "Don't immediately move on. Try a different question from the same domain "
                    "to see whether you can apply the concept."
                )
            else:
                st.write(
                    "Because you reported your confidence, the coach can distinguish solid knowledge "
                    "from an answer you happened to get right."
                )

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎯 Give Me a Targeted Follow-up", type="primary", use_container_width=True):
                    st.session_state.followup = choose_followup(
                        q["id"], st.session_state.selected, part, difficulty
                    )
                    st.session_state.question = st.session_state.followup
                    st.session_state.submitted = False
                    st.session_state.selected = None
                    st.session_state.confidence = 0
                    st.session_state.result = None
                    st.rerun()
            with col2:
                if st.button("Next Mixed Question", use_container_width=True):
                    st.session_state.question = choose_question(part, domain, difficulty)
                    st.session_state.submitted = False
                    st.session_state.selected = None
                    st.session_state.confidence = 0
                    st.session_state.result = None
                    st.session_state.followup = None
                    st.rerun()
    else:
        st.info("Choose your settings and start a practice question.")

with dashboard:
    s = stats()
    snap = learning_snapshot()

    a, b, c = st.columns(3)
    a.metric("Questions Attempted", s["attempted"])
    b.metric("Accuracy", f"{s['accuracy']}%")
    c.metric("Question Bank", s["question_bank_size"])

    st.subheader("What You Should Work On")
    if snap["weak_domains"]:
        st.error("🔴 Priority: " + " · ".join(snap["weak_domains"]))
    else:
        st.success("No clear weak domain yet — keep building your sample.")

    if snap["fragile_domains"]:
        st.warning("🟡 Fragile knowledge: " + " · ".join(snap["fragile_domains"]))

    st.subheader("Mastery by Domain")
    for row in s["mastery"]:
        icon = {"New": "⚪", "Learning": "🟡", "Weak": "🔴", "Mastered": "🟢"}[row["status"]]
        st.write(f"{icon} **{row['domain']}** — {row['status']}")

    st.subheader("Recent Learning Signals")
    if snap["recent_misses"]:
        for miss in snap["recent_misses"][:5]:
            st.write(
                f"• **{miss['domain']}** — missed {miss['question_id']} "
                f"(confidence {miss['confidence']}/5)"
            )
    else:
        st.info("Complete a few questions and the coach will start identifying patterns.")

    st.subheader("Recent Attempts")
    history = recent()
    if history:
        st.dataframe(history, use_container_width=True)
    else:
        st.info("No practice history yet.")

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
        x, y = st.columns(2)
        x.metric("Days Remaining", p["days_remaining"])
        y.metric("Daily Minutes", p["daily_minutes"])

        st.markdown("### Focus Areas")
        for topic in p["focus_topics"]:
            st.write(f"🎯 {topic}")

        st.markdown("### Suggested Session")
        for item in p["session"]:
            st.write(f"• {item}")
    else:
        st.info("Save your exam target and daily study time to generate a plan.")
