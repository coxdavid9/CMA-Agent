import json
import os
from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner, SQLiteSession, function_tool
from .engine import choose_question, grade, stats, plan, save_goal, goal, recent, CASES

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")
MEMORY_DB = os.getenv("CMA_AGENT_MEMORY_DB", str(ROOT / "data" / "agent_memory.db"))
Path(MEMORY_DB).parent.mkdir(parents=True, exist_ok=True)
SESSION=SQLiteSession("david-cma-full", MEMORY_DB)

@function_tool
def question_tool(part: str="Both", domain: str="All", difficulty: str="All") -> str:
    """Select an adaptive original CMA-style practice question."""
    q=choose_question(part,domain,difficulty)
    return json.dumps({"id":q["id"],"part":q["part"],"domain":q["domain"],"difficulty":q["difficulty"],"question":q["question"],"choices":q["choices"]})

@function_tool
def grade_tool(question_id: str, selected_answer: str, confidence: int=0) -> str:
    """Grade and record a user's answer."""
    ok,q=grade(question_id,selected_answer,confidence)
    return json.dumps({"correct":bool(ok),"correct_answer":q["answer"],"explanation":q["explanation"],"calculation":q["calculation"],"part":q["part"],"domain":q["domain"],"difficulty":q["difficulty"]})

@function_tool
def stats_tool() -> str:
    """Return overall and topic-level performance."""
    return json.dumps(stats())

@function_tool
def plan_tool() -> str:
    """Return a personalized study plan."""
    return json.dumps(plan())

@function_tool
def goal_tool(target_date: str, part: str, daily_minutes: int) -> str:
    """Save study goal."""
    save_goal(target_date,part,daily_minutes); return json.dumps(goal())

@function_tool
def history_tool(limit: int=20) -> str:
    """Return recent attempts."""
    return json.dumps(recent(limit))

@function_tool
def case_tool(case_id: str="") -> str:
    """Return an original case-based practice scenario."""
    c=next((x for x in CASES if x["id"]==case_id),CASES[0])
    return json.dumps(c)

tutor=Agent(name="CMA Tutor",instructions="Teach by active recall. Never reveal an answer before commitment. Grade with the grading tool, explain the reasoning, and diagnose misconceptions.")
analyst=Agent(name="CMA Performance Analyst",instructions="Analyze weak domains, recurring errors, confidence, and difficulty using the stats and history tools.")
planner=Agent(name="CMA Study Planner",instructions="Create a practical study plan from target date, daily time, and weak domains using the plan tool.")

coach=Agent(
 name="CMA Coach",
 instructions="""You manage a personal CMA study system. Give one question at a time. When the user answers, grade it with the grading tool and teach the reasoning. Use performance and plan tools when asked.
The current CMA has Part 1 Financial Planning, Performance, and Analytics and Part 2 Strategic Financial Management.
The English exam moves to case-based questions as the standard format beginning September/October 2026.
All questions in this project are original CMA-style practice material, never official IMA questions.
Be candid, concise, encouraging, and adaptive.""",
 tools=[question_tool,grade_tool,stats_tool,plan_tool,goal_tool,history_tool,case_tool]
)

async def ask(text):
    r=await Runner.run(coach,text,session=SESSION)
    return r.final_output
