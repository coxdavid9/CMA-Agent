"""Focused financial-reporting lessons; original examples, no answer keys in clients."""
import json
from pathlib import Path

LESSONS = json.loads((Path(__file__).resolve().parents[1]/"data/financial_lessons.json").read_text())
IDS = {row["id"] for row in LESSONS}


def build_tasks(lesson_id, r, number, choice):
    def n(prompt, answer, explanation, hint):
        return number(prompt, answer, explanation, [hint])
    def c(prompt, good, bad, explanation):
        return choice(prompt, {"reason": good, "trap": bad}, "reason", explanation,
                      ["Trace the economic event before looking at the bank."])
    if lesson_id == "statement-links":
        def facts():
            capital, revenue, expense, dividend = r.randrange(8,21)*1000, r.randrange(4,10)*1000, r.randrange(5,16)*100, r.randrange(1,5)*100
            return capital, revenue, expense, dividend
        a,b,d,e=facts()
        context=f"Beginning retained earnings are $0. Owner invests ${a:,}; services of ${b:,} are earned and collected; current rent is ${d:,}; a ${e:,} dividend is paid. No other entries."
        guided=[
            c(context+" Which event earns revenue?", "Providing the customer service", "Receiving the owner's investment", "Owner funding increases capital; customer service earns revenue."),
            n(context+" What is net income?",b-d,f"Revenue ${b:,} − rent ${d:,} = ${b-d:,}. Dividends are excluded.","Exclude owner contributions and distributions from profit."),
            n(context+" What is ending retained earnings?",b-d-e,f"Beginning $0 + profit ${b-d:,} − dividends ${e:,} = ${b-d-e:,}.","Start with profit, then subtract the distribution.")]
        a,b,d,e=facts()
        check=[n(f"Beginning retained earnings are $0. Owner invests ${a:,}; service revenue is ${b:,}; current rent expense is ${d:,}; dividends are ${e:,}. What is ending retained earnings?",b-d-e,f"${b:,} − ${d:,} − ${e:,} = ${b-d-e:,}. Capital contributions are not retained earnings.","Separate contributed capital from accumulated earnings."),
               c("A customer pays an existing receivable. What happens at collection?","Cash rises and receivables fall; no new revenue.","Both cash and revenue rise again.","The sale already created revenue. Collection exchanges assets.")]
    elif lesson_id == "accrual-timing":
        total=r.randrange(1,5)*1200; months=r.choice([3,6,12]); used=r.randrange(1,months)
        expense=total*used/months
        context=f"Pay ${total:,} for {months} equal months of future insurance. At close, {used} full months have been consumed. Assume no other changes."
        guided=[
            c(context+" What is recorded at payment?","A prepaid asset for the unconsumed coverage","The entire payment as current expense","The unconsumed coverage is a future economic benefit."),
            n(context+" What expense belongs to the elapsed months?",expense,f"${total:,} × {used}/{months} = ${expense:,.0f}.","Divide the payment by coverage months, then multiply by months used."),
            n(context+" What prepaid asset remains?",total-expense,f"${total:,} − ${expense:,.0f} = ${total-expense:,.0f}.","The unconsumed portion remains an asset.")]
        total=r.randrange(1,5)*1200; months=r.choice([3,6,12]); used=r.randrange(1,months); remaining=total*(months-used)/months
        check=[n(f"Insurance costs ${total:,} for {months} equal months. After {used} full months of coverage, what prepaid insurance asset remains?",remaining,f"${total:,} × ({months} − {used})/{months} = ${remaining:,.0f}.","Remove only consumed coverage."),
               c("A customer pays an advance for service next month. What is recorded now?","Cash and a liability increase.","Cash and earned revenue increase.","The obligation remains until the promised performance occurs.")]
    elif lesson_id == "cash-flow-bridge":
        def facts():
            return (r.randrange(10,31)*1000,r.randrange(1,6)*1000,r.randrange(1,6)*1000,r.randrange(1,6)*100,r.randrange(1,6)*100)
        ni,dep,ar,inv,ap=facts()
        context=f"Net income ${ni:,}; depreciation ${dep:,}; operating receivables increase ${ar:,}; inventory increases ${inv:,}; operating payables increase ${ap:,}. No other adjustments."
        guided=[
            c(context+" How should depreciation be treated?","Add it back to remove a noncash expense.","Subtract it as another current cash payment.","Profit already included depreciation; the reconciliation reverses its noncash effect."),
            n(context+" What is profit plus depreciation?",ni+dep,f"${ni:,} + ${dep:,} = ${ni+dep:,}.","Undo the noncash expense first."),
            n(context+" What is operating cash flow?",ni+dep-ar-inv+ap,f"${ni:,} + ${dep:,} − ${ar:,} − ${inv:,} + ${ap:,} = ${ni+dep-ar-inv+ap:,}.","Subtract operating asset increases; add operating liability increases.")]
        ni,dep,ar,inv,ap=facts()
        check=[n(f"Net income ${ni:,}, depreciation ${dep:,}, operating receivables increase ${ar:,}, inventory increases ${inv:,}, operating payables increase ${ap:,}. No other adjustments. Calculate operating cash flow.",ni+dep-ar-inv+ap,f"${ni:,} + ${dep:,} − ${ar:,} − ${inv:,} + ${ap:,} = ${ni+dep-ar-inv+ap:,}.","Reconcile profit to operating cash before considering equipment or borrowing."),
               c("A company buys equipment for cash. Where does that payment belong?","Investing cash flow","An extra subtraction within operating cash flow","Equipment acquisition is investing. Do not count it twice.")]
    elif lesson_id == "revenue-delivery":
        price=r.randrange(4,21)*1000; pct=r.choice([25,50,75]); earned=price*pct/100
        context=f"A valid single-obligation service contract has a fixed ${price:,} price, paid upfront. The customer receives benefits as work occurs, so it qualifies for over-time recognition. Measured performance is {pct}% complete."
        guided=[
            c(context+" What initially happens to the advance?","Record a contract liability until earned.","Record the whole contract price as earned revenue.","Cash precedes performance; the obligation has not yet been satisfied."),
            n(context+" What is cumulative earned revenue?",earned,f"${price:,} × {pct}% = ${earned:,.0f}.","Apply the satisfied proportion to the single allocated contract price."),
            n(context+" What contract liability remains?",price-earned,f"${price:,} − ${earned:,.0f} = ${price-earned:,.0f}.","The undelivered portion remains unearned.")]
        price=r.randrange(4,21)*1000; pct=r.choice([25,50,75]); unearned=price*(100-pct)/100
        check=[n(f"A valid single-obligation contract receives ${price:,} upfront. It qualifies for over-time recognition and measured performance is {pct}% satisfied. What contract liability remains?",unearned,f"${price:,} × (100% − {pct}%) = ${unearned:,.0f}.","Subtract earned revenue from the advance."),
               c("For this contract, what supports recognizing revenue over time?","The customer receives and consumes benefits as the service is performed.","The invoice was sent before the work began.","The performance criterion supports recognition; invoicing alone does not.")]
    elif lesson_id == "inventory-measurement":
        def facts():
            units=r.randrange(2,9)*50; low=r.randrange(6,12); high=low+r.choice([2,4])
            return units,low,high
        units,low,high=facts(); sold=units+units//2; total=units*(low+high); fifo=units*low+(sold-units)*high; avg=(low+high)/2
        context=f"Periodic inventory: buy {units} units at ${low} and {units} units at ${high}; sell {sold} units. No beginning inventory or other costs."
        guided=[
            c(context+" Which costs go to COGS first under FIFO?","The earliest purchase costs","The latest purchase costs","FIFO assigns oldest costs to units sold; physical movement need not follow that order."),
            n(context+" Calculate FIFO cost of goods sold.",fifo,f"{units} × ${low} + {sold-units} × ${high} = ${fifo:,}.","Use the entire first layer, then enough of the second layer."),
            n(context+" Calculate periodic weighted-average unit cost.",avg,f"${total:,} ÷ {2*units} = ${avg:.2f}.","Divide total cost by total units available.")]
        units,low,high=facts(); sold=units+units//2; ending=(2*units-sold)*high
        check=[n(f"Periodic FIFO: buy {units} units at ${low}, then {units} at ${high}. Sell {sold} units. No beginning inventory, other costs, or write-down. What is ending inventory cost?",ending,f"{2*units-sold} remaining units × latest cost ${high} = ${ending:,}.","The oldest costs went to COGS, leaving the newest costs in inventory."),
               c("FIFO inventory cost is $700 and NRV is $650. Under lower of cost and NRV, what happens?","Write inventory down by $50 and recognize a loss.","Keep $700 because the units have not been sold.","An unsold asset can still require a valuation loss. The lower amount is $650.")]
    elif lesson_id == "receivable-allowance":
        gross=r.randrange(10,31)*1000; rate=r.choice([2,4,5,6]); target=gross*rate/100; credit=int(target/2)
        context=f"Gross receivables are ${gross:,}. A given expected-loss estimate requires a {rate}% ending allowance. The existing allowance has a ${credit:,} credit balance. Use this supplied estimate."
        guided=[
            c(context+" What is the estimate meant to establish?","The required ending allowance balance","The new expense regardless of the existing allowance","The target balance includes the allowance already recorded."),
            n(context+" What ending allowance is required?",target,f"${gross:,} × {rate}% = ${target:,.0f}.","Calculate the target before the adjusting entry."),
            n(context+" What loss expense adjustment is needed?",target-credit,f"Target ${target:,.0f} − existing credit ${credit:,} = ${target-credit:,.0f}.","Only fill the gap between current and required allowance.")]
        gross=r.randrange(10,31)*1000; rate=r.choice([2,4,5,6]); target=gross*rate/100; credit=int(target/2)
        check=[n(f"Gross receivables ${gross:,}; supplied required expected-loss estimate {rate}%; existing allowance credit balance ${credit:,}. What additional loss expense is needed?",target-credit,f"${gross:,} × {rate}% − ${credit:,} = ${target-credit:,.0f}.","The target allowance is not the same as the adjustment."),
               c("Under the allowance method, a receivable is written off against an adequate allowance. What happens immediately?","Gross receivables and allowance fall equally; net receivables do not change.","Net receivables and profit both fall by the write-off.","The expected loss was previously estimated. The write-off uses the allowance without another expense.")]
    else:
        raise ValueError("Unknown financial lesson")
    # Avoid a positional answer cue while keeping explanations attached to the right key.
    for task in guided+check:
        if task["type"] == "choice":
            entries=list(task["choices"].items())
            r.shuffle(entries)
            task["choices"]=dict(entries)
    return {"context":context,"guided":guided,"check":check}
