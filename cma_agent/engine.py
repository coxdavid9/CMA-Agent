import json, os, random, sqlite3, uuid
from pathlib import Path
from datetime import date, datetime, timedelta
ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/"data"
QUESTIONS=json.loads((DATA/"questions.json").read_text(encoding="utf-8"))
CASES=json.loads((DATA/"cases.json").read_text(encoding="utf-8"))
DB=Path(os.getenv("CMA_DB_PATH",str(DATA/"study.db")))
SESSION_TIMEOUT_MINUTES=30


def _dict_row(row, columns):
 return dict(zip(columns, row)) if row else None


def db():
 url=os.getenv("TURSO_DATABASE_URL")
 token=os.getenv("TURSO_AUTH_TOKEN")
 if url and token:
  import libsql_experimental as libsql
  c=libsql.connect(database=url, auth_token=token)
 else:
  c=sqlite3.connect(DB)
  c.row_factory=sqlite3.Row
 c.execute("CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,ts TEXT,question_id TEXT,part TEXT,domain TEXT,difficulty TEXT,selected TEXT,correct INTEGER,confidence INTEGER)")
 c.execute("CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY CHECK(id=1),target_date TEXT,part TEXT,daily_minutes INTEGER)")
 c.execute("CREATE TABLE IF NOT EXISTS study_plans(id INTEGER PRIMARY KEY AUTOINCREMENT,created_at TEXT,target_date TEXT,part TEXT,daily_minutes INTEGER)")
 c.execute("CREATE TABLE IF NOT EXISTS preferences(id INTEGER PRIMARY KEY CHECK(id=1),part TEXT,difficulty TEXT,domain TEXT)")
 c.execute("CREATE TABLE IF NOT EXISTS session_state(id INTEGER PRIMARY KEY CHECK(id=1),session_id TEXT,last_activity TEXT)")
 cols={r[1] for r in c.execute("PRAGMA table_info(preferences)").fetchall()}
 if "resume_question_id" not in cols:c.execute("ALTER TABLE preferences ADD COLUMN resume_question_id TEXT")
 cols={r[1] for r in c.execute("PRAGMA table_info(attempts)").fetchall()}
 if "session_id" not in cols:c.execute("ALTER TABLE attempts ADD COLUMN session_id TEXT")
 c.commit(); return c


def get_or_start_session():
 c=db(); now=datetime.now(); r=c.execute("SELECT session_id,last_activity FROM session_state WHERE id=1").fetchone()
 if not r or not r[1] or now-datetime.fromisoformat(r[1])>timedelta(minutes=SESSION_TIMEOUT_MINUTES):
  sid=str(uuid.uuid4()); c.execute("INSERT OR REPLACE INTO session_state(id,session_id,last_activity) VALUES(1,?,?)",(sid,now.isoformat(timespec="seconds")))
 else:
  sid=r[0]; c.execute("UPDATE session_state SET last_activity=? WHERE id=1",(now.isoformat(timespec="seconds"),))
 c.commit(); c.close(); return sid


def start_new_session():
 c=db(); sid=str(uuid.uuid4()); now=datetime.now(); c.execute("INSERT OR REPLACE INTO session_state(id,session_id,last_activity) VALUES(1,?,?)",(sid,now.isoformat(timespec="seconds"))); c.commit(); c.close(); return sid


def session_stats(session_id):
 c=db(); r=c.execute("SELECT COUNT(*) n,COALESCE(SUM(correct),0) correct FROM attempts WHERE session_id=?",(session_id,)).fetchone(); misses=c.execute("SELECT domain,COUNT(*) n FROM attempts WHERE session_id=? AND correct=0 GROUP BY domain ORDER BY n DESC",(session_id,)).fetchall(); result={"attempted":r[0],"correct":r[1],"accuracy":round(r[1]/r[0]*100,1) if r[0] else 0,"miss_domains":[x[0] for x in misses]}; c.close(); return result


def get_preferences():
 c=db(); r=c.execute("SELECT part,difficulty,domain,resume_question_id FROM preferences WHERE id=1").fetchone(); result=_dict_row(r,["part","difficulty","domain","resume_question_id"]) or {"part":"Both","difficulty":"All","domain":"All","resume_question_id":None}; c.close(); return result


def save_preferences(part,difficulty,domain):
 c=db()
 r=c.execute("SELECT id,resume_question_id FROM preferences WHERE id=1").fetchone()
 if r:c.execute("UPDATE preferences SET part=?,difficulty=?,domain=? WHERE id=1",(part,difficulty,domain))
 else:c.execute("INSERT INTO preferences(id,part,difficulty,domain,resume_question_id) VALUES(1,?,?,?,NULL)",(part,difficulty,domain))
 c.commit(); c.close()


def save_resume_question(question_id):
 c=db(); c.execute("UPDATE preferences SET resume_question_id=? WHERE id=1",(question_id,)); c.commit(); c.close()


def clear_resume_question():
 c=db(); c.execute("UPDATE preferences SET resume_question_id=NULL WHERE id=1"); c.commit(); c.close()


def get_question(question_id): return next((q for q in QUESTIONS if q["id"]==question_id),None)


def domains(part="Both"):
 p1=["External Financial Reporting Decisions","Planning, Budgeting, and Forecasting","Performance Management","Cost Management","Internal Controls","Technology and Analytics"]; p2=["Financial Statement Analysis","Corporate Finance","Business Decision Analysis","Enterprise Risk Management","Capital Investment Decisions","Professional Ethics"]; return p1 if part=="Part 1" else p2 if part=="Part 2" else p1+p2


def _question_history(conn):
 rows=conn.execute("SELECT question_id,COUNT(*) attempts,SUM(correct) correct,MAX(id) last_id FROM attempts GROUP BY question_id").fetchall(); return {r[0]:{"question_id":r[0],"attempts":r[1],"correct":r[2],"last_id":r[3]} for r in rows}


def question_status(question_id,conn=None):
 owns=conn is None; conn=conn or db(); rows=conn.execute("SELECT correct FROM attempts WHERE question_id=? ORDER BY id DESC LIMIT 5",(question_id,)).fetchall()
 if owns:conn.close()
 if not rows:return "New"
 results=[int(r[0]) for r in rows]; attempts=len(results)
 if attempts>=3 and sum(results[:3])==3:return "Mastered"
 if results[0]==0 or sum(results)/attempts<.67:return "Weak"
 return "Learning"


def topic_status(domain,conn=None):
 owns=conn is None; conn=conn or db(); rows=conn.execute("SELECT correct FROM attempts WHERE domain=? ORDER BY id DESC LIMIT 10",(domain,)).fetchall()
 if owns:conn.close()
 if not rows:return "New"
 results=[int(r[0]) for r in rows]
 if len(results)>=5 and sum(results[:5])/5>=.85:return "Mastered"
 if results[0]==0 or sum(results)/len(results)<.70:return "Weak"
 return "Learning"


def choose_question(part="Both",domain="All",difficulty="All",exclude=None,review_mode=False):
 exclude=set(exclude or []); conn=db(); filtered=[q for q in QUESTIONS if q["id"] not in exclude and (part=="Both" or q["part"]==part) and (domain=="All" or q["domain"]==domain) and (difficulty=="All" or q["difficulty"]==difficulty)]
 if not filtered:filtered=[q for q in QUESTIONS if q["id"] not in exclude and (part=="Both" or q["part"]==part)]
 history=_question_history(conn); buckets={"New":[],"Learning":[],"Weak":[],"Mastered":[]}
 for q in filtered:buckets[question_status(q["id"],conn)].append(q)
 pool=(buckets["Weak"] or buckets["Learning"] or buckets["New"] or buckets["Mastered"] or filtered) if review_mode else (buckets["New"] or buckets["Weak"] or buckets["Learning"] or buckets["Mastered"] or filtered)
 domain_rows=conn.execute("SELECT domain,AVG(correct) pct,COUNT(*) n FROM attempts GROUP BY domain").fetchall(); domain_scores={r[0]:(float(r[1]),int(r[2])) for r in domain_rows}; weighted=[]
 for q in pool:
  pct,_=domain_scores.get(q["domain"],(.5,0)); attempts=int(history.get(q["id"],{}).get("attempts",0)); status=question_status(q["id"],conn); weight={"New":5,"Weak":4,"Learning":2,"Mastered":.25}[status]; weight*=max(.5,1.5-pct); weight*=1/(1+attempts*.15); weighted.extend([q]*max(1,int(weight*10)))
 chosen=random.choice(weighted or pool); conn.close(); return chosen


def choose_followup(question_id,selected,part="Both",difficulty="All"):
 source=get_question(question_id); candidates=[q for q in QUESTIONS if q["id"]!=question_id and q["part"]==source["part"] and q["domain"]==source["domain"] and (difficulty=="All" or q["difficulty"]==difficulty)]
 if not candidates:candidates=[q for q in QUESTIONS if q["id"]!=question_id and q["part"]==source["part"] and (difficulty=="All" or q["difficulty"]==difficulty)]
 if not candidates:return choose_question(part,"All",difficulty,exclude=[question_id],review_mode=True)
 conn=db(); history=_question_history(conn); scored=[]
 for q in candidates:
  h=history.get(q["id"],{}); attempts=int(h.get("attempts",0)); correct=int(h.get("correct",0)); score=10 if attempts==0 else 7 if correct/max(1,attempts)<.67 else 2; scored.append((score+random.random(),q))
 conn.close(); return max(scored,key=lambda x:x[0])[1]


def learning_feedback(question_id,selected,confidence):
 q=get_question(question_id); correct=selected.upper()==q["answer"]; confidence=int(confidence or 0)
 if correct and confidence==1:diagnosis,advice="Correct, but fragile","You got it right, but you were unsure. This concept should come back for another recall check."
 elif correct:diagnosis,advice="Solid understanding","You appear comfortable with this concept. We can spend less time here and focus on weaker areas."
 elif confidence==3:diagnosis,advice="Likely concept/application gap","You were fairly sure but missed it. Review the rule, then prove you can apply it in a different situation."
 else:diagnosis,advice="Likely knowledge gap","You were not sure and missed it. This is a good candidate for a short concept review before moving on."
 return {"correct":correct,"diagnosis":diagnosis,"advice":advice,"takeaway":q.get("explanation") or "Review the explanation and identify the rule that determines the correct answer.","correct_answer":q["answer"],"explanation":q.get("explanation",""),"calculation":q.get("calculation")}


def learning_snapshot(domain="All"):
 c=db(); where="" if domain=="All" else "WHERE domain=?"; args=() if domain=="All" else (domain,); rows=c.execute(f"SELECT question_id,correct,confidence,domain FROM attempts {where} ORDER BY id DESC LIMIT 50",args).fetchall(); weak=[]; fragile=[]
 for d in domains("Both"):
  drows=[r for r in rows if r[3]==d]
  if not drows:continue
  pct=sum(int(r[1]) for r in drows)/len(drows); low=sum(1 for r in drows if int(r[1])==1 and int(r[2] or 0)==1)
  if pct<.70:weak.append((pct,d))
  if low>=2:fragile.append((low,d))
 recent_misses=[_dict_row(r,["question_id","correct","confidence","domain"]) for r in rows if int(r[1])==0][:5]; c.close(); weak.sort(); fragile.sort(reverse=True); return {"weak_domains":[d for _,d in weak[:3]],"fragile_domains":[d for _,d in fragile[:3]],"recent_misses":recent_misses}


def grade(question_id,selected,confidence=0,session_id=None):
 q=get_question(question_id); correct=int(selected.upper()==q["answer"]); c=db(); c.execute("INSERT INTO attempts(ts,question_id,part,domain,difficulty,selected,correct,confidence,session_id) VALUES(?,?,?,?,?,?,?,?,?)",(datetime.now().isoformat(timespec="seconds"),question_id,q["part"],q["domain"],q["difficulty"],selected.upper(),correct,int(confidence or 0),session_id or get_or_start_session())); c.commit(); c.close(); return correct,q


def stats():
 c=db(); n=c.execute("SELECT COUNT(*) n FROM attempts").fetchone()[0]; k=c.execute("SELECT COALESCE(SUM(correct),0) n FROM attempts").fetchone()[0]; rows=c.execute("SELECT part,domain,COUNT(*) n,SUM(correct) correct,ROUND(AVG(correct)*100,1) pct FROM attempts GROUP BY part,domain").fetchall(); mastery=[{"domain":d,"status":topic_status(d,c)} for d in domains("Both")]; counts={"New":0,"Learning":0,"Weak":0,"Mastered":0}
 for q in QUESTIONS:counts[question_status(q["id"],c)]+=1
 result={"attempted":n,"correct":k,"accuracy":round(k/n*100,1) if n else 0,"by_domain":[_dict_row(r,["part","domain","n","correct","pct"]) for r in rows],"mastery":mastery,"question_status_counts":counts,"question_bank_size":len(QUESTIONS)}; c.close(); return result


def recent(limit=25):
 c=db(); rows=c.execute("SELECT id,ts,question_id,part,domain,difficulty,selected,correct,confidence,session_id FROM attempts ORDER BY id DESC LIMIT ?",(limit,)).fetchall(); result=[_dict_row(r,["id","ts","question_id","part","domain","difficulty","selected","correct","confidence","session_id"]) for r in rows]; c.close(); return result


def save_goal(target_date,part,daily_minutes):
 c=db(); now=datetime.now().isoformat(timespec="seconds"); c.execute("INSERT OR REPLACE INTO goals(id,target_date,part,daily_minutes) VALUES(1,?,?,?)",(target_date,part,daily_minutes)); c.execute("INSERT INTO study_plans(created_at,target_date,part,daily_minutes) VALUES(?,?,?,?)",(now,target_date,part,daily_minutes)); c.commit(); c.close()


def goal():
 c=db(); r=c.execute("SELECT id,target_date,part,daily_minutes FROM goals WHERE id=1").fetchone(); result=_dict_row(r,["id","target_date","part","daily_minutes"]); c.close(); return result


def goal_history(limit=10):
 c=db(); rows=c.execute("SELECT id,created_at,target_date,part,daily_minutes FROM study_plans ORDER BY id DESC LIMIT ?",(limit,)).fetchall(); result=[_dict_row(r,["id","created_at","target_date","part","daily_minutes"]) for r in rows]; c.close(); return result


def plan():
 g=goal()
 if not g:return {"message":"Set an exam target date first."}
 s=stats(); days=max(1,(date.fromisoformat(g["target_date"])-date.today()).days); allowed=domains(g["part"]); weak=[r["domain"] for r in sorted(s["by_domain"],key=lambda x:x["pct"]) if r["domain"] in allowed]; focus=weak[:3] or allowed[:3]; m=g["daily_minutes"]; return {"days_remaining":days,"daily_minutes":m,"part":g["part"],"target_date":g["target_date"],"focus_topics":focus,"session":[f"{max(5,m//3)} min concept review",f"{max(10,m//2)} min adaptive practice",f"{max(5,m//6)} min error review"]}


def reset():
 c=db(); c.execute("DELETE FROM attempts"); c.commit(); c.close()
