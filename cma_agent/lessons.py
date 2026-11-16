"""Original, deterministic teaching content and server-graded guided practice.

Lesson outcomes are deliberately narrower than syllabus mastery. No external LLM,
API key, or new paid service is required. All answers stay on the server.
"""
from datetime import datetime, timedelta, timezone
import json
import math
import random
import uuid

from cma_agent import engine, financial_lessons

SOURCE = "https://www.imanet.org/ima-certifications/cma-certification/prepare"
LESSONS = [
    {
        "id": "flexible-budget", "title": "Separate volume from spending",
        "part": "Part 1", "domain": "Performance Management", "minutes": 18,
        "teaching_version": "reasoning-first",
        "outcomes": ["P1.C.1.e", "P1.C.1.g"],
        "skills": ["Flexible budget performance", "Standard cost and variances"],
        "purpose": "Explain a cost overrun without blaming the team for producing more.",
        "concept": "A static budget uses planned output. A flexible budget asks what costs should have been at actual output. Compare actual costs with that flexible budget to isolate spending and efficiency effects from volume.",
        "formula": "Flexible cost budget = actual units × budget variable cost per unit + budget fixed cost",
        "connection": "In a monthly close review, a higher total cost may simply reflect higher output. Reset the comparison to actual activity before recommending action. The same logic applies to service calls, meals, or deliveries.",
        "trap": "Flex the variable costs, not the fixed total, within the relevant range. For costs, actual above flexible budget is unfavorable.",
    },
    {
        "id": "absorption-variable", "title": "Why inventory changes profit",
        "part": "Part 1", "domain": "Cost Management", "minutes": 18,
        "teaching_version": "reasoning-first",
        "outcomes": ["P1.D.1.f", "P1.D.1.g", "P1.D.1.h"],
        "skills": ["Absorption and variable costing"],
        "purpose": "Reconcile profit when production and sales move in different directions.",
        "concept": "Variable costing expenses all fixed manufacturing overhead in the period. Absorption costing assigns it to production; the portion in unsold units stays in inventory until those units are sold. This timing difference changes profit even when sales are identical.",
        "formula": "Absorption income − variable income = inventory unit increase × fixed manufacturing overhead rate (constant rate assumed)",
        "connection": "A plant can report higher absorption profit by building inventory. That does not mean customers bought more or cash improved. Reconcile the inventory effect before celebrating the margin change.",
        "trap": "Only fixed manufacturing overhead causes this reconciliation. Selling and administrative costs do not enter manufacturing inventory. A falling inventory reverses the direction.",
    },
    {
        "id": "special-order", "title": "Decide what actually changes",
        "part": "Part 2", "domain": "Business Decision Analysis", "minutes": 18,
        "teaching_version": "reasoning-first",
        "outcomes": ["P2.C.2.a", "P2.C.2.b", "P2.C.2.h"],
        "skills": ["Special orders", "Relevant costs and revenues", "Sunk and opportunity costs"],
        "purpose": "Evaluate a one-time order without letting allocated costs distort the decision.",
        "concept": "A relevant amount is future and differs between the alternatives. With idle capacity and no effect on regular sales, a special order adds its revenue and incremental costs. Existing fixed costs do not become incremental just because accounting allocates them per unit.",
        "formula": "Incremental profit = order units × (special price − incremental unit cost) − order-specific fixed cost − opportunity cost",
        "connection": "For an order below the usual price, build an accept-versus-reject bridge. Then check capacity, customer pricing expectations, quality, and effects on regular business before making a recommendation.",
        "trap": "Idle capacity matters. If the order displaces regular sales, lost contribution is an opportunity cost. A past design payment is sunk; a new setup payment is relevant.",
    },
    {
        "id": "cash-cycle", "title": "Find where cash gets tied up",
        "part": "Part 2", "domain": "Corporate Finance", "minutes": 15,
        "teaching_version": "reasoning-first",
        "outcomes": ["P2.B.4.a", "P2.B.4.gg"],
        "skills": ["Working capital management"],
        "purpose": "Connect inventory, collections, and supplier payments to cash pressure.",
        "concept": "The cash conversion cycle measures how long operations tie up cash: inventory waits to sell, receivables wait to be collected, and supplier credit finances part of that wait. Shortening the cycle generally releases cash, holding other factors constant.",
        "formula": "Cash conversion cycle = days inventory outstanding + days sales outstanding − days payables outstanding",
        "connection": "A profitable business can still run short of cash when stock piles up or customers pay slowly. This is a useful bridge between a P&L discussion and the cash questions a small-business owner asks.",
        "trap": "Subtract payable days because supplier credit delays the cash outflow. Paying suppliers later may help cash but can lose discounts or damage relationships; shorter is not automatically better at any cost.",
    },
    {
        "id": "npv", "title": "Turn future savings into today's value",
        "part": "Part 2", "domain": "Capital Investment Decisions", "minutes": 18,
        "teaching_version": "reasoning-first",
        "outcomes": ["P2.E.2.a", "P2.E.2.b", "P2.E.2.c"],
        "skills": ["Net present value", "Time value of money"],
        "purpose": "Decide whether future cash benefits compensate for the money invested today.",
        "concept": "A future dollar is worth less than a dollar today when the required return is positive. Discount each incremental cash flow to today, then subtract the initial investment. A positive NPV means the project exceeds that required return under the stated assumptions.",
        "formula": "NPV = sum of cash flow at time t ÷ (1 + required return)^t − initial investment",
        "connection": "When comparing an equipment purchase with continuing the current process, start with incremental cash savings and their timing. Accounting depreciation is not itself a cash outflow, though its tax effect can matter.",
        "trap": "Discount cash flows, not accounting profit. Do not discount the time-zero payment again. These starter examples assume one year, no taxes, no working-capital changes, and no salvage value.",
    },
]
LESSONS = financial_lessons.LESSONS + LESSONS
BY_ID = {lesson["id"]: lesson for lesson in LESSONS}


def _number(prompt, answer, explanation, hints, wrong=None, tolerance=0.01):
    return {"type": "number", "prompt": prompt, "answer": answer,
            "explanation": explanation, "hints": hints, "wrong": wrong or {}, "tolerance": tolerance}


def _choice(prompt, choices, answer, explanation, hints):
    return {"type": "choice", "prompt": prompt, "choices": choices, "answer": answer,
            "explanation": explanation, "hints": hints}


def build_tasks(lesson_id, rng=None):
    r = rng or random.SystemRandom()
    if lesson_id in financial_lessons.IDS:
        return financial_lessons.build_tasks(lesson_id, r, _number, _choice)
    if lesson_id == "flexible-budget":
        units, rate, fixed = r.randrange(8, 17)*100, r.randrange(4, 10), r.randrange(3, 8)*1000
        budget = units*rate+fixed
        over = r.randrange(2, 8)*100
        base = f"At actual output of {units:,} units, budget variable cost is ${rate} per unit and budget fixed cost is ${fixed:,}. Actual total cost is ${budget+over:,}. Output is within the relevant range."
        guided = [
            _choice(base+" Which output belongs in the flexible budget?", {"actual": "Actual output", "planned": "Planned output"}, "actual", "Use actual output so the comparison holds activity constant.", ["We want the budget for what was actually produced."]),
            _number("What is the flexible total cost budget, in dollars?", budget, f"{units:,} × ${rate} + ${fixed:,} = ${budget:,}.", ["Multiply actual units by the variable rate.", "Then add the unchanged fixed total."], {str(units*rate): "You calculated variable cost only. Add fixed cost once."}),
            _number("How many dollars unfavorable is actual cost versus that flexible budget?", over, f"Actual ${budget+over:,} − flexible ${budget:,} = ${over:,} unfavorable.", ["Compare actual with flexible, not static, cost."]),
        ]
        u2, f2, v2 = units+300, fixed+1000, rate+1
        delta = over+200
        checks = [_number(f"Fresh situation: actual output {u2:,}, budget variable cost ${v2}/unit, budget fixed cost ${f2:,}, actual cost ${u2*v2+f2+delta:,}. Enter the unfavorable flexible-budget cost variance in dollars.", delta, f"Flexible = {u2:,} × {v2} + {f2:,} = {u2*v2+f2:,}; actual less flexible = ${delta:,}.", ["Reset the budget to actual output, then compare costs."]), _choice("Actual cost exceeds static budget only because output increased. Actual cost equals flexible budget. What does that establish?", {"volume": "The total difference is explained by volume; there is no net flexible-budget cost variance.", "waste": "The team necessarily wasted resources.", "fixed": "Fixed cost per unit must remain constant."}, "volume", "At actual activity, actual and budget cost agree. Individual offsetting variances could still exist.", ["Hold output constant before evaluating spending."])]
    elif lesson_id == "absorption-variable":
        made, sold, rate = r.randrange(12, 20)*100, r.randrange(6, 10)*100, r.randrange(3, 9)
        increase, diff = made-sold, (made-sold)*rate
        base = f"A company starts with no inventory, makes {made:,} units, and sells {sold:,}. Fixed manufacturing overhead is applied at ${rate}/unit. All production is within normal capacity; there are no overhead variances."
        guided = [_number(base+" How many units remain in inventory?", increase, f"{made:,} − {sold:,} = {increase:,} units.", ["Beginning inventory + production − sales = ending inventory."]), _number("How much fixed manufacturing overhead stays in ending inventory under absorption costing?", diff, f"{increase:,} units × ${rate} = ${diff:,}.", ["Multiply unsold units by the fixed manufacturing overhead rate."]), _choice("Which method reports higher income here?", {"absorption": "Absorption", "variable": "Variable", "same": "They are equal"}, "absorption", f"Absorption defers ${diff:,}; variable costing expenses it now. Absorption income is higher by that amount.", ["Which method keeps some fixed manufacturing cost out of current expense?"])]
        sold2, rate2 = made-200, rate+2
        checks = [_number(f"Fresh situation: no beginning inventory, production {made:,}, sales {sold2:,}, constant fixed manufacturing overhead rate ${rate2}/unit. No overhead variances. How much higher is absorption income than variable income?", 200*rate2, f"Inventory rises 200 units. 200 × ${rate2} = ${200*rate2:,} deferred.", ["Only the inventory change times the fixed manufacturing rate reconciles income."]), _choice("Now inventory decreases, with the same fixed manufacturing overhead rate in beginning inventory and current production. Which income is higher?", {"variable": "Variable costing income", "absorption": "Absorption costing income", "same": "Always equal"}, "variable", "Absorption releases prior fixed manufacturing overhead from inventory into expense, so absorption income is lower.", ["Selling old inventory releases previously deferred overhead."])]
    elif lesson_id == "special-order":
        units, price, cost, setup = r.randrange(5, 15)*100, r.randrange(25, 40), r.randrange(12, 22), r.randrange(2, 5)*100
        profit = units*(price-cost)-setup
        base = f"An order for {units:,} units pays ${price}/unit. Incremental cost is ${cost}/unit plus a new ${setup:,} setup. Capacity is idle; regular sales and existing fixed costs do not change. Allocated existing fixed cost is $8/unit. Ignore tax and long-term effects."
        guided = [_choice(base+" Which cost should be excluded from the incremental calculation?", {"allocated": "The $8/unit allocation of unchanged fixed costs", "setup": "The new setup payment", "variable": "Incremental unit cost"}, "allocated", "The fixed total is identical with or without the order. The allocation does not change that.", ["Relevant costs must differ between accepting and rejecting."]), _number("What is the order's contribution before the new setup cost?", units*(price-cost), f"{units:,} × (${price} − ${cost}) = ${units*(price-cost):,}.", ["Use special-order revenue less incremental unit costs."]), _number("What is the incremental profit after setup?", profit, f"${units*(price-cost):,} − ${setup:,} = ${profit:,}.", ["Subtract the new setup once, not per unit."], {str(units*(price-cost)): "You stopped at contribution. The new setup is also incremental."})]
        units2, price2, cost2, setup2 = units+200, price+3, cost+1, setup+100
        checks = [_number(f"Fresh order: {units2:,} units at ${price2}, incremental unit cost ${cost2}, new setup ${setup2:,}. Idle capacity, no lost sales, no tax or other effects. Enter incremental profit.", units2*(price2-cost2)-setup2, f"{units2:,} × ({price2} − {cost2}) − {setup2} = ${units2*(price2-cost2)-setup2:,}.", ["Build accept minus reject cash flows."]), _choice("The order now displaces profitable regular sales. What changes?", {"opportunity": "Include the contribution lost on displaced regular sales.", "ignore": "Ignore the displaced sales because their price is historical.", "allocated": "Replace incremental cost with allocated full cost."}, "opportunity", "Scarce capacity has an opportunity cost: contribution sacrificed on the best alternative use.", ["What would accepting prevent you from earning?"])]
    elif lesson_id == "cash-cycle":
        dio, dso, dpo = r.randrange(35, 66), r.randrange(25, 46), r.randrange(15, 31)
        cycle = dio+dso-dpo
        guided = [_choice(f"Inventory days {dio}, receivable days {dso}, payable days {dpo}. Which component reduces the cash conversion cycle?", {"dpo": "Payable days", "dio": "Inventory days", "dso": "Receivable days"}, "dpo", "Suppliers finance part of the operating cycle by allowing payment later.", ["Which balance lets you delay paying cash?"]), _number("Calculate the cash conversion cycle in days.", cycle, f"{dio} + {dso} − {dpo} = {cycle} days.", ["Add inventory and receivable days, then subtract payable days."], {str(dio+dso+dpo): "Payable days are financing, so subtract them."}), _number("Collections improve by 5 days; everything else stays constant. What is the new cycle?", cycle-5, f"Reducing receivable days by 5 reduces the cycle from {cycle} to {cycle-5} days.", ["Faster collections mean fewer days waiting for cash."])]
        checks = [_number(f"Fresh business: inventory days {dio+7}, receivable days {dso+3}, payable days {dpo+4}. Calculate the cycle in days.", cycle+6, f"{dio+7} + {dso+3} − {dpo+4} = {cycle+6} days.", ["Inventory + receivables − payables."]), _choice("Collections become slower while sales and other cycle components stay constant. What is the likely cash effect?", {"tied": "More cash is tied up in receivables; the cycle lengthens.", "released": "Cash is released immediately.", "profit": "Profit necessarily increases."}, "tied", "Waiting longer for the same sales proceeds delays cash without necessarily changing reported profit.", ["Separate recognizing revenue from collecting it."])]
    else:
        investment, cash, percent = r.randrange(7, 12)*1000, r.randrange(12, 16)*1000, r.choice([8,10,12])
        pv = cash/(1+percent/100)
        npv = pv-investment
        base = f"Pay ${investment:,} today and receive one cash inflow of ${cash:,} exactly one year later. Required return {percent}%. No taxes, salvage, working-capital changes, or other cash flows."
        guided = [_choice(base+" What should be discounted?", {"future": "The future cash receipt", "today": "The initial payment at time zero", "neither": "Neither amount"}, "future", "The initial payment is already in today's dollars. Bring the future receipt back one year.", ["Which amount is not already at time zero?"]), _number("Enter the present value of the receipt, rounded to the nearest dollar.", pv, f"${cash:,} ÷ (1 + {percent/100}) = ${pv:,.2f}.", ["Divide by one plus the required return.", "For one year, the denominator is not raised beyond power 1."], tolerance=0.51), _number("Enter NPV, rounded to the nearest dollar.", npv, f"${pv:,.2f} − ${investment:,} = ${npv:,.2f}.", ["Subtract the time-zero investment from present value."], {str(round(pv)): "Present value is only the benefits. Subtract the investment to get net present value."}, tolerance=0.51)]
        inv2, cash2 = investment+2000, cash+1000
        npv2 = cash2/(1+percent/100)-inv2
        checks = [_number(f"Fresh project: pay ${inv2:,} now; receive ${cash2:,} in one year. Required return {percent}%; no other cash flows or tax. Enter NPV to the nearest dollar (use a minus sign if negative).", npv2, f"{cash2:,} ÷ (1 + {percent/100}) − {inv2:,} = ${npv2:,.2f}.", ["Discount the receipt and subtract the initial payment."], tolerance=0.51), _choice("For an independent project with reliable estimated cash flows and the appropriate discount rate, what does positive NPV mean?", {"accept": "It is expected to earn more than the required return, supporting acceptance.", "profit": "Accounting profit must be positive in every year.", "cash": "There is no estimation risk."}, "accept", "Positive NPV indicates value above the required return under the assumptions. It does not eliminate risk or guarantee annual accounting profit.", ["NPV compares value today with the investment required."])]
    return {"context": base if lesson_id != "cash-cycle" else f"Inventory {dio} days · Receivables {dso} days · Payables {dpo} days", "guided": guided, "check": checks}


def _schema(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS lesson_runs (
        id TEXT PRIMARY KEY, lesson_id TEXT NOT NULL, revision TEXT NOT NULL,
        started_at TEXT NOT NULL, completed_at TEXT, due_at TEXT, state TEXT NOT NULL)""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lesson_runs_lesson ON lesson_runs(lesson_id, started_at)")
    conn.commit()


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _revision(lesson_id):
    return "guided-v2-teaching"


def _runs(conn, lesson_id):
    return conn.execute("SELECT * FROM lesson_runs WHERE lesson_id=? AND revision=? ORDER BY started_at DESC", (lesson_id, _revision(lesson_id))).fetchall()


def _public(row):
    state = json.loads(row["state"])
    tasks = state["tasks"]
    index = state["index"]
    task = tasks[index] if index < len(tasks) else None
    result = {"run_id": row["id"], "lesson_id": row["lesson_id"], "mode": state["mode"],
              "index": index, "total": len(tasks), "context": state["context"],
              "feedback": state.get("feedback"), "done": bool(row["completed_at"]),
              "due_at": row["due_at"], "outcome": state.get("outcome"),
              "guided_count": state["guided_count"], "independent_correct": state.get("independent_correct", 0)}
    if "teaching_step" in state:
        result["teaching_step"] = state["teaching_step"]
    if task and not (state.get("teaching_step", 5) < 5):
        result["task"] = {k: task[k] for k in ("type", "prompt", "choices") if k in task}
        result["hints"] = task["hints"][:state.get("hint_level", 0)]
        result["can_hint"] = state.get("hint_level", 0) < len(task["hints"])
        result["assisted"] = state.get("hint_level", 0) > 0
        result["stage"] = "Guided example" if index < state["guided_count"] else "Independent check"
    return result


def catalog(part="Both"):
    conn = engine.db()
    _schema(conn)
    result = []
    for lesson in LESSONS:
        if part != "Both" and lesson["part"] != part:
            continue
        runs = _runs(conn, lesson["id"])
        latest = runs[0] if runs else None
        state = json.loads(latest["state"]) if latest else {}
        due = bool(latest and latest["due_at"] and datetime.fromisoformat(latest["due_at"]) <= _now())
        result.append({**lesson, "status": "In progress" if latest and not latest["completed_at"] else state.get("outcome", "Not started"), "due": due, "due_at": latest["due_at"] if latest else None})
    conn.close()
    result.sort(key=lambda x: (not x["due"], x["status"] != "In progress", x["status"] != "Needs reinforcement"))
    return result


def start(lesson_id):
    if lesson_id not in BY_ID:
        raise ValueError("Unknown lesson")
    conn = engine.db()
    _schema(conn)
    if engine.DATABASE_URL:
        conn.execute("SELECT pg_advisory_xact_lock(hashtext(?))", (lesson_id,))
    else:
        conn.execute("BEGIN IMMEDIATE")
    runs = _runs(conn, lesson_id)
    latest = runs[0] if runs else None
    if latest and not latest["completed_at"]:
        conn.close()
        return _public(latest)
    recall = bool(latest and latest["due_at"] and datetime.fromisoformat(latest["due_at"]) <= _now())
    built = build_tasks(lesson_id)
    if latest:
        old = json.loads(latest["state"])
        previous_prompt = old["tasks"][old["guided_count"]]["prompt"]
        while built["check"][0]["prompt"] == previous_prompt:
            built = build_tasks(lesson_id)
    state = {"mode": "recall" if recall else "lesson", "index": 0, "hint_level": 0,
             "tasks": ([] if recall else built["guided"]) + built["check"],
             "guided_count": 0 if recall else len(built["guided"]), "context": built["context"],
             "results": [], "previous_independent": bool(latest and json.loads(latest["state"]).get("outcome") in ("Independent check passed", "Recall confirmed"))}
    if not recall:
        state["teaching_step"] = 0
    run_id = str(uuid.uuid4())
    conn.execute("INSERT INTO lesson_runs(id,lesson_id,revision,started_at,state) VALUES(?,?,?,?,?)", (run_id, lesson_id, _revision(lesson_id), _now().isoformat(timespec="microseconds"), json.dumps(state)))
    conn.commit()
    row = conn.execute("SELECT * FROM lesson_runs WHERE id=?", (run_id,)).fetchone()
    conn.close()
    return _public(row)


def act(run_id, index, action, answer=""):
    conn = engine.db()
    _schema(conn)
    # Serialize concurrent requests for a run, including across devices.
    suffix = " FOR UPDATE" if engine.DATABASE_URL else ""
    if not engine.DATABASE_URL:
        conn.execute("BEGIN IMMEDIATE")
    row = conn.execute("SELECT * FROM lesson_runs WHERE id=?"+suffix, (run_id,)).fetchone()
    if not row:
        conn.close()
        raise ValueError("Lesson session not found")
    state = json.loads(row["state"])
    if row["completed_at"] or index != state["index"]:
        conn.close()
        return _public(row)
    if action == "teach_review" and row["lesson_id"] in BY_ID:
        state["teaching_step"] = 0
        if index >= state["guided_count"] and not state.get("feedback"):
            # Reopening the worked teaching during a check is legitimate help,
            # and must not subsequently count as an unaided answer.
            state["hint_level"] = max(1, state.get("hint_level", 0))
        conn.execute("UPDATE lesson_runs SET state=? WHERE id=?", (json.dumps(state), run_id))
        conn.commit()
        updated = conn.execute("SELECT * FROM lesson_runs WHERE id=?", (run_id,)).fetchone()
        conn.close()
        return _public(updated)
    if action in ("teach_next", "teach_back"):
        current = state.get("teaching_step", 5)
        # The expected teaching page makes repeat/stale navigation idempotent.
        if str(current) != answer or current >= 5:
            conn.close()
            return _public(row)
        state["teaching_step"] = max(0, min(5, current+(1 if action == "teach_next" else -1)))
        conn.execute("UPDATE lesson_runs SET state=? WHERE id=?", (json.dumps(state), run_id))
        conn.commit()
        updated = conn.execute("SELECT * FROM lesson_runs WHERE id=?", (run_id,)).fetchone()
        conn.close()
        return _public(updated)
    if state.get("teaching_step", 5) < 5:
        conn.close()
        raise ValueError("Explore the teaching pages before starting the calculation.")
    if action in ("answer", "hint") and state.get("feedback"):
        conn.close()
        return _public(row)
    task = state["tasks"][index]
    if action == "hint" and not state.get("feedback"):
        state["hint_level"] = min(len(task["hints"]), state.get("hint_level", 0)+1)
    elif action == "answer" and not state.get("feedback"):
        if task["type"] == "number":
            try:
                value = float(str(answer).strip().replace(",", "").replace("$", ""))
            except ValueError:
                conn.close()
                raise ValueError("Enter a number, such as 1250 or -350.")
            if not math.isfinite(value):
                conn.close()
                raise ValueError("Enter a finite number.")
            correct = abs(value-task["answer"]) <= task["tolerance"]
            mistake = task.get("wrong", {}).get(str(round(value)), "Check which facts belong in the setup, then follow the worked calculation below.")
            expected = f"{task['answer']:,.0f}"
        else:
            if answer not in task["choices"]:
                conn.close()
                raise ValueError("Choose one of the listed answers.")
            correct = answer == task["answer"]
            expected = task["choices"][task["answer"]]
            mistake = "Compare the condition in your answer with the rule below."
        assisted = state.get("hint_level", 0) > 0 or index < state["guided_count"]
        state["results"].append({"correct": correct, "assisted": assisted, "independent": index >= state["guided_count"]})
        state["feedback"] = {"correct": correct, "assisted": assisted, "expected": expected, "explanation": task["explanation"], "coaching": "You set this up correctly." if correct else mistake}
    elif action == "next" and state.get("feedback"):
        state["index"] += 1
        state["feedback"] = None
        state["hint_level"] = 0
    else:
        conn.close()
        raise ValueError("Finish the current step before continuing.")
    completed_at, due_at = None, None
    if state["index"] == len(state["tasks"]):
        checks = [r for r in state["results"] if r["independent"]]
        passed = len(checks) == 2 and all(r["correct"] and not r["assisted"] for r in checks)
        state["independent_correct"] = sum(r["correct"] and not r["assisted"] for r in checks)
        state["outcome"] = "Recall confirmed" if passed and state["mode"] == "recall" and state["previous_independent"] else "Independent check passed" if passed else "Needs reinforcement"
        completed_at = _now().isoformat(timespec="seconds")
        due_at = (_now()+timedelta(days=3 if state["outcome"] == "Recall confirmed" else 1)).isoformat(timespec="seconds")
    conn.execute("UPDATE lesson_runs SET state=?,completed_at=?,due_at=? WHERE id=?", (json.dumps(state), completed_at, due_at, run_id))
    conn.commit()
    result = conn.execute("SELECT * FROM lesson_runs WHERE id=?", (run_id,)).fetchone()
    conn.close()
    return _public(result)
