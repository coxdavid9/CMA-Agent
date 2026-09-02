import json, os, random, sqlite3, uuid, time
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
  return libsql.connect(database=url, auth_token=token)
 c=sqlite3.connect(DB)
 c.row_factory=sqlite3.Row
 return c
