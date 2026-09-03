from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

from cma_agent.engine import (
    choose_question, choose_followup, grade, learning_feedback,
    learning_snapshot, stats, plan, save_goal, get_preferences,
    save_preferences, save_resume_question, clear_resume_question,
    get_question, goal, goal_history, get_or_start_session,
    start_new_session, session_stats,
)

app = FastAPI(title="CMA Coach API")


class Settings(BaseModel):
    part: str = "Both"
    difficulty: str = "All"
    domain: str = "All"


class GradeRequest(BaseModel):
    question_id: str
    selected: str
    confidence: int = 0
    session_id: Optional[str] = None


class QuestionRequest(BaseModel):
    part: str = "Both"
    domain: str = "All"
    difficulty: str = "All"
    exclude: list[str] = []


class FollowupRequest(BaseModel):
    question_id: str
    selected: str
    part: str = "Both"
    difficulty: str = "All"


class GoalRequest(BaseModel):
    target_date: str
    part: str
    daily_minutes: int


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/session")
def session():
    sid = get_or_start_session()
    return {"session_id": sid, "stats": session_stats(sid)}


@app.post("/api/session/new")
def new_session():
    sid = start_new_session()
    return {"session_id": sid, "stats": session_stats(sid)}


@app.get("/api/preferences")
def preferences():
    return get_preferences()


@app.post("/api/preferences")
def preferences_save(settings: Settings):
    clear_resume_question()
    save_preferences(settings.part, settings.difficulty, settings.domain)
    return get_preferences()


@app.get("/api/question/{question_id}")
def question(question_id: str):
    q = get_question(question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    return q


@app.post("/api/question")
def question_choose(request: QuestionRequest):
    q = choose_question(request.part, request.domain, request.difficulty, exclude=request.exclude)
    save_resume_question(q["id"])
    return q


@app.post("/api/followup")
def followup(request: FollowupRequest):
    q = choose_followup(request.question_id, request.selected, request.part, request.difficulty)
    save_resume_question(q["id"])
    return q


@app.post("/api/grade")
def grade_question(request: GradeRequest):
    q = get_question(request.question_id)
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")
    ok, graded = grade(request.question_id, request.selected, request.confidence, request.session_id)
    feedback = learning_feedback(request.question_id, request.selected, request.confidence)
    sid = request.session_id or get_or_start_session()
    return {"correct": bool(ok), "question": graded, "feedback": feedback, "session": session_stats(sid)}


@app.get("/api/dashboard")
def dashboard():
    return {"stats": stats(), "snapshot": learning_snapshot()}


@app.get("/api/study-plan")
def study_plan():
    return {"goal": goal(), "plan": plan(), "history": goal_history()}


@app.post("/api/study-plan")
def study_plan_save(request: GoalRequest):
    save_goal(request.target_date, request.part, request.daily_minutes)
    return {"goal": goal(), "plan": plan(), "history": goal_history()}


@app.get("/api/study-profile")
def study_profile():
    s = stats()
    snap = learning_snapshot()
    g = goal()
    return {
        "profile_version": "1.0",
        "overall": {
            "questions_completed": s["attempted"],
            "accuracy": s["accuracy"],
            "question_bank_size": s["question_bank_size"],
        },
        "current_plan": g,
        "priority_topics": {
            "weak_domains": snap["weak_domains"],
            "fragile_domains": snap["fragile_domains"],
            "recent_misses": snap["recent_misses"],
        },
        "study_mode_guidance": [
            "Teach weak topics before drilling them.",
            "Use one question at a time.",
            "Guide reasoning before revealing an answer when appropriate.",
            "Reinforce low-confidence correct answers.",
            "Use follow-up questions after misses.",
        ],
    }


app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
