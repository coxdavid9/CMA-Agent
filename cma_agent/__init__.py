"""CMA Coach concept coverage support.

This package-level hook enriches the adaptive dashboard with explicit CMA
concept coverage without changing the question-bank format yet. Concepts are
mapped to the current IMA learning-outcome areas and are counted only when an
attempted question contains evidence for that concept.
"""


def _install_concept_coverage():
    import re
    import cma_agent.adaptive as adaptive
    import cma_agent.engine as engine

    taxonomy = {
        "External Financial Reporting Decisions": {
            "Financial statements": ("balance sheet", "income statement", "cash flow statement", "statement of cash flows", "statement of changes in equity"),
            "Consolidated statements": ("consolidat", "variable interest entity", "voting interest", "intracompany"),
            "Integrated reporting": ("integrated reporting", "integrated report", "six capitals", "value creation"),
            "Asset valuation": ("asset valuation", "inventory valuation", "lower of", "impairment", "depreciation"),
            "Liability valuation": ("liabilit", "bond", "lease liability", "pension obligation"),
            "Revenue recognition": ("revenue recognition", "performance obligation", "contract liability", "contract asset"),
            "Income measurement": ("income measurement", "earnings", "comprehensive income", "temporary difference"),
            "GAAP vs. IFRS": ("gaap", "ifrs", "international financial reporting"),
        },
        "Planning, Budgeting, and Forecasting": {
            "Strategic planning": ("strategic planning", "mission", "strategic goal", "external factor", "internal factor"),
            "Budgeting concepts": ("budget process", "resource allocation", "budgeting concept", "operating goal"),
            "Forecasting techniques": ("regression", "learning curve", "expected value", "forecast"),
            "Master budgeting": ("master budget", "annual business plan", "sales budget", "production budget", "cash budget"),
            "Project budgeting": ("project budget", "project budgeting"),
            "Flexible budgeting": ("flexible budget", "static budget", "budgeted activity"),
            "Budget variance analysis": ("budget variance", "planning variance", "spending variance"),
            "Pro forma and cash projections": ("pro forma", "cash flow projection", "financial projection"),
        },
        "Performance Management": {
            "Flexible budget performance": ("flexible budget", "flexible-budget"),
            "Standard cost and variances": ("standard cost", "price variance", "quantity variance", "rate variance", "efficiency variance", "volume variance"),
            "Responsibility centers": ("responsibility center", "cost center", "profit center", "investment center"),
            "Transfer pricing": ("transfer price", "transfer pricing"),
            "Segment performance": ("segment", "business unit profitability", "customer profitability", "product profitability"),
            "ROI and residual income": ("return on investment", "roi", "residual income", "investment base"),
            "Balanced scorecard": ("balanced scorecard", "critical success factor", "nonfinancial performance"),
            "Management by exception": ("management by exception", "exception reporting"),
        },
        "Cost Management": {
            "Cost behavior and cost objects": ("cost behavior", "cost object", "variable cost", "fixed cost", "mixed cost"),
            "Absorption and variable costing": ("absorption costing", "full costing", "variable costing", "direct costing"),
            "Job and process costing": ("job order", "process costing", "equivalent units"),
            "Activity-based costing": ("activity based costing", "activity-based costing", "cost driver", "abc"),
            "Overhead allocation": ("overhead", "allocation base", "service department", "plant-wide", "departmental overhead"),
            "Joint and by-product costing": ("joint cost", "by-product", "split-off"),
            "Operational efficiency": ("just-in-time", "jit", "mrp", "theory of constraints", "throughput", "capacity management"),
            "Process and quality improvement": ("value chain", "value-added", "benchmarking", "continuous improvement", "cost of quality", "activity-based management"),
        },
        "Internal Controls": {
            "COSO and control environment": ("coso", "control environment", "internal control framework"),
            "Risk assessment": ("risk assessment", "control risk", "risk management"),
            "Control activities": ("control activity", "segregation of duties", "authorization", "reconciliation", "safeguard"),
            "Internal audit": ("internal audit", "internal auditor", "assurance", "audit function"),
            "IT general controls": ("general it control", "it general control", "access control", "network control"),
            "Application and transaction controls": ("application control", "transaction control", "input control", "processing control"),
            "Business continuity and recovery": ("backup", "disaster recovery", "business continuity", "recovery procedure"),
            "Fraud and compliance": ("fraud", "sarbanes-oxley", "foreign corrupt practices", "compliance"),
        },
        "Technology and Analytics": {
            "Data governance and management": ("data governance", "data management", "data quality", "master data"),
            "Information systems and ERP": ("erp", "enterprise resource planning", "information system", "database"),
            "Data visualization": ("dashboard", "data visualization", "visualization", "power bi"),
            "Descriptive analytics": ("descriptive analytics", "descriptive analysis"),
            "Diagnostic analytics": ("diagnostic analytics", "diagnostic analysis"),
            "Predictive analytics": ("predictive analytics", "predictive analysis", "forecast model"),
            "Prescriptive analytics": ("prescriptive analytics", "prescriptive analysis", "optimization"),
            "Technology risk and data ethics": ("data ethics", "data security", "cybersecurity", "technology risk", "privacy"),
        },
        "Financial Statement Analysis": {
            "Financial ratios": ("current ratio", "quick ratio", "debt to assets", "ratio analysis"),
            "Profitability analysis": ("profit margin", "return on assets", "return on equity", "profitability"),
            "Liquidity and solvency": ("liquidity", "solvency", "working capital"),
            "Activity ratios": ("inventory turnover", "receivables turnover", "asset turnover"),
            "Common-size and trend analysis": ("common-size", "vertical analysis", "horizontal analysis", "trend analysis"),
            "Cash flow analysis": ("operating cash flow", "cash flow analysis", "free cash flow"),
            "Earnings quality": ("earnings quality", "quality of earnings", "earnings management"),
            "Financial statement effects": ("financial statement analysis", "financial statement impact"),
        },
        "Corporate Finance": {
            "Risk and return": ("risk and return", "beta", "systematic risk", "required return"),
            "Cost of capital": ("cost of capital", "wacc", "weighted average cost of capital", "cost of debt", "cost of equity"),
            "Capital structure": ("capital structure", "debt-equity", "leverage"),
            "Working capital management": ("working capital", "cash conversion cycle", "accounts receivable", "inventory management"),
            "Dividend policy": ("dividend", "payout ratio", "retained earnings"),
            "Financing decisions": ("financing", "short-term financing", "long-term financing"),
            "Foreign exchange": ("foreign exchange", "currency", "exchange rate", "hedging"),
            "Financial markets": ("capital market", "money market", "securities", "market efficiency"),
        },
        "Business Decision Analysis": {
            "Relevant costs and revenues": ("relevant cost", "relevant revenue", "avoidable cost", "unavoidable cost"),
            "Sunk and opportunity costs": ("sunk cost", "opportunity cost"),
            "Special orders": ("special order", "special pricing"),
            "Make-or-buy": ("make or buy", "make-or-buy", "buy or make"),
            "Product mix and constraints": ("product mix", "constrained resource", "limiting factor", "contribution per"),
            "Keep-or-drop decisions": ("keep or drop", "drop a segment", "discontinue"),
            "Cost-volume-profit": ("break even", "contribution margin", "operating leverage", "cvp"),
            "Pricing decisions": ("pricing", "target price", "target costing", "markup"),
        },
        "Enterprise Risk Management": {
            "ERM framework": ("enterprise risk management", "erm", "risk framework"),
            "Risk identification": ("risk identification", "identify risk", "risk register"),
            "Risk assessment and response": ("risk response", "risk assessment", "risk appetite", "risk tolerance"),
            "Strategic and operational risk": ("strategic risk", "operational risk", "business risk"),
            "Financial risk": ("financial risk", "credit risk", "liquidity risk", "market risk"),
            "Reputation and compliance risk": ("reputational risk", "compliance risk", "regulatory risk"),
            "Risk monitoring": ("risk monitoring", "monitoring controls", "key risk indicator"),
            "Scenario and sensitivity analysis": ("sensitivity analysis", "scenario analysis", "stress test"),
        },
        "Capital Investment Decisions": {
            "Time value of money": ("time value of money", "present value", "future value", "discount rate"),
            "Net present value": ("net present value", "npv"),
            "Internal rate of return": ("internal rate of return", "irr"),
            "Payback and discounted payback": ("payback period", "discounted payback"),
            "Profitability index": ("profitability index", "present value index"),
            "Cash flow estimation": ("incremental cash flow", "after-tax cash flow", "cash flow estimation"),
            "Capital rationing": ("capital rationing", "investment limit"),
            "Project risk and sensitivity": ("project risk", "sensitivity", "scenario", "certainty equivalent"),
        },
        "Professional Ethics": {
            "IMA ethical principles": ("ima statement", "ethical professional practice", "competence", "confidentiality"),
            "Integrity and credibility": ("integrity", "credibility", "professionalism"),
            "Conflict of interest": ("conflict of interest", "conflict of interest"),
            "Confidentiality and data protection": ("confidentiality", "confidential information", "data privacy"),
            "Fraudulent or misleading reporting": ("fraudulent reporting", "misleading report", "manipulation of results"),
            "Ethical decision resolution": ("resolve ethical", "ethical issue", "ethical dilemma"),
            "Independence and objectivity": ("objectivity", "independence", "bias"),
            "Legal and regulatory compliance": ("legal requirement", "regulatory", "compliance", "law"),
        },
    }

    def labels_for_question(q):
        text = " ".join(str(q.get(k, "")) for k in ("question", "explanation", "calculation")).lower()
        labels = []
        for label, keywords in taxonomy.get(q.get("domain"), {}).items():
            if any(keyword in text for keyword in keywords):
                labels.append(label)
        return labels

    original = adaptive.mastery_by_domain

    def mastery_with_coverage(part="Both", domain="All"):
        rows = original(part, domain)
        for row in rows:
            d = row["domain"]
            allowed = [q for q in engine.QUESTIONS if not q.get("is_case") and q.get("domain") == d and (part == "Both" or q.get("part") == part)]
            all_concepts = list(taxonomy.get(d, {}).keys())
            question_map = {q.get("id"): q for q in allowed}
            conn = engine.db()
            attempts = conn.execute("SELECT question_id FROM attempts WHERE domain=? ORDER BY id DESC", (d,)).fetchall()
            conn.close()
            covered = set()
            for attempt in attempts:
                q = question_map.get(attempt["question_id"]) or engine.get_question(attempt["question_id"])
                if q and not q.get("is_case"):
                    covered.update(labels_for_question(q))
            row["concepts_covered"] = len(covered)
            row["concept_coverage"] = [{"name": name, "covered": name in covered} for name in all_concepts]
            row["concepts_total"] = len(all_concepts)
        return rows

    adaptive.mastery_by_domain = mastery_with_coverage


_install_concept_coverage()
