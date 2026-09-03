import streamlit as st

from cma_agent.study_profile import build_study_profile, study_profile_json

st.set_page_config(page_title="CMA Study Profile", page_icon="🧠", layout="wide")

st.title("🧠 CMA Study Profile")
st.caption("A compact handoff from CMA Coach to your ChatGPT Study Mode session.")

profile = build_study_profile()
overall = profile["overall"]

c1, c2, c3 = st.columns(3)
c1.metric("Questions Completed", overall["questions_completed"])
c2.metric("Overall Accuracy", f'{overall["accuracy"]}%')
c3.metric("Question Bank", overall["question_bank_size"])

st.divider()
st.subheader("Priority Areas")
weak = profile["priority_topics"]["weak_domains"]
fragile = profile["priority_topics"]["fragile_domains"]

if weak:
    st.markdown("**Needs review**")
    for topic in weak:
        st.write(f"🔴 {topic}")
if fragile:
    st.markdown("**Correct, but low confidence**")
    for topic in fragile:
        st.write(f"🟡 {topic}")
if not weak and not fragile:
    st.info("Not enough history yet to identify priority areas.")

st.subheader("Performance by Domain")
for row in profile["domain_profile"]:
    accuracy = "—" if row["accuracy"] is None else f'{row["accuracy"]:.1f}%'
    st.write(f'**{row["domain"]}** · {row["status"]} · {accuracy} · {row["attempted"]} attempts')

st.subheader("Recent Misses")
misses = profile["priority_topics"]["recent_misses"]
if misses:
    for miss in misses:
        st.write(f'• {miss["domain"]} · confidence {miss.get("confidence", "—")}/3')
else:
    st.write("No recent misses recorded.")

st.divider()
st.subheader("Use With ChatGPT Study Mode")
st.write("Download the profile below and attach it to this CMA Study chat. I can use it to target lessons, explanations, and practice toward your actual weak areas.")

st.download_button(
    "⬇️ Download Study Profile",
    data=study_profile_json(),
    file_name="cma_study_profile.json",
    mime="application/json",
    use_container_width=True,
)

with st.expander("Preview handoff data"):
    st.json(profile)
