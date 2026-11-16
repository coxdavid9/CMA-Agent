// Original teaching examples. Explorations are ungraded and deliberately scoped.
export const SCENARIOS={
  "absorption-variable": {
    "pages": [
      "The situation",
      "Watch the cost move",
      "Explore inventory and profit",
      "Talk through the explanation",
      "Bring it together"
    ],
    "storyTitle": "“Profit improved. Did we sell more—or just build stock?”",
    "story": [
      "You are reconciling two income reports for the same plant and month. Sales, prices, cash flows, and production costs are identical. Absorption income is $1,000 higher than variable-costing income.",
      "The month starts with 400 units in inventory. Production is 1,200 units and sales are 1,000, leaving 600 units. Fixed manufacturing overhead is $6,000 for the month, or $5 per unit at normal capacity. Beginning inventory carries the same $5 fixed rate. There are no overhead variances.",
      "The difference is when fixed manufacturing overhead becomes an expense. Some of it is waiting in inventory under absorption costing."
    ],
    "takeaway": "Follow the fixed manufacturing cost from inventory to expense. Higher reported profit does not itself mean more cash or more customer demand.",
    "steps": [
      {
        "title": "Variable costing expenses the fixed total now",
        "text": "All $6,000 of this month's fixed manufacturing overhead is a period expense. Variable manufacturing costs still enter inventory; it is the fixed manufacturing cost treatment that differs.",
        "calculation": "Fixed manufacturing overhead expense under variable costing = $6,000"
      },
      {
        "title": "Absorption costing carries fixed overhead in inventory",
        "text": "Beginning inventory contains $2,000 of fixed overhead (400 × $5). Add the current $6,000. Ending inventory contains $3,000 (600 × $5), which has not yet become an expense.",
        "calculation": "$2,000 beginning + $6,000 added − $3,000 ending = $5,000 expensed"
      },
      {
        "title": "Reconcile the change, not the whole ending balance",
        "text": "Absorption expenses $5,000 instead of $6,000, so its income is $1,000 higher. The $3,000 ending balance is not the income difference: $2,000 was already in beginning inventory.",
        "calculation": "(600 ending units − 400 beginning units) × $5 = $1,000 higher absorption income"
      }
    ],
    "explorerTitle": "Change sales. Watch inventory and the income difference.",
    "explorerIntro": "Production stays at 1,200 units, beginning inventory at 400, and fixed manufacturing overhead at $6,000 ($5/unit). Selling price is $30, variable manufacturing cost $12/unit, and period selling/administrative cost $2,000. Both inventory layers have identical unit costs; there are no overhead variances.",
    "controls": [
      {
        "key": "sales",
        "label": "Units sold",
        "min": 600,
        "max": 1600,
        "step": 100
      }
    ],
    "defaults": {
      "sales": 1000
    },
    "presets": [
      {
        "label": "Build inventory",
        "values": {
          "sales": 1000
        }
      },
      {
        "label": "Inventory unchanged",
        "values": {
          "sales": 1200
        }
      },
      {
        "label": "Sell down inventory",
        "values": {
          "sales": 1600
        }
      }
    ],
    "discussion": "A manager points to the $3,000 fixed overhead in ending inventory and calls it the profit improvement. How would you explain the difference?",
    "choices": [
      {
        "key": "change",
        "label": "Compare ending inventory with beginning inventory; only the net change explains the income difference.",
        "heading": "Yes—reconcile the movement, not the ending balance.",
        "text": "Fixed overhead in inventory rose from $2,000 to $3,000. The net $1,000 deferral explains the higher absorption income."
      },
      {
        "key": "ending",
        "label": "All $3,000 in ending inventory is this month's profit improvement.",
        "heading": "Part of that balance was already deferred last month.",
        "text": "Beginning inventory already carried $2,000. Subtract it from the $3,000 ending amount to find this month's net deferral: $1,000."
      },
      {
        "key": "cash",
        "label": "The higher absorption income means we collected an extra $1,000.",
        "heading": "A change in expense timing does not create a cash receipt.",
        "text": "The same operations and cash flows are being reported under two cost treatments. Inventory can hold fixed manufacturing cost without creating a new customer payment."
      },
      {
        "key": "unsure",
        "label": "I still don't see why inventory affects income.",
        "heading": "An unsold unit can hold a cost instead of expensing it yet.",
        "text": "Under absorption costing, each unit holds $5 of fixed manufacturing overhead until it sells. Building 200 net units postpones $1,000 of expense. Variable costing expenses the full fixed total now."
      }
    ],
    "formula": "Absorption income − variable income = (ending units − beginning units) × fixed manufacturing overhead per unit",
    "recap": [
      "Use the inventory change, not ending inventory alone. This shortcut assumes a constant fixed overhead rate and no complicating overhead variances.",
      "Building inventory makes absorption income higher. Selling down inventory reverses the direction. Neither effect proves better cash flow or stronger demand."
    ],
    "limits": "Selling and administrative costs do not enter manufacturing inventory. A changed overhead rate or overhead variance needs a fuller reconciliation."
  },
  "special-order": {
    "pages": [
      "The situation",
      "Build the decision bridge",
      "Explore price and capacity",
      "Talk through the decision",
      "Bring it together"
    ],
    "storyTitle": "“The order is below full cost. Should we reject it?”",
    "story": [
      "A customer offers $18 each for a one-time order of 500 units. Variable manufacturing cost is $14 per unit. The cost report also allocates $6 per unit of existing fixed manufacturing cost, so reported full cost is $20.",
      "The order needs a new $1,000 setup payment. A $900 design payment was made last month and cannot be recovered. There is idle capacity, no effect on regular sales, and no tax or other cash-flow effects in this example.",
      "Comparing $18 with $20 mixes costs that will change with costs the company will incur anyway."
    ],
    "takeaway": "Compare accepting with rejecting. Relevant amounts are future amounts that differ between those alternatives.",
    "steps": [
      {
        "title": "Find the new contribution",
        "text": "Accepting creates $9,000 of revenue and $7,000 of variable cost. Neither occurs if the order is rejected.",
        "calculation": "500 × ($18 − $14) = $2,000 additional contribution"
      },
      {
        "title": "Subtract costs caused by this order",
        "text": "The new $1,000 setup is incremental. The existing fixed total will not change, so its $6/unit allocation is excluded. The unrecoverable past $900 payment is sunk.",
        "calculation": "$2,000 contribution − $1,000 setup = $1,000 incremental profit"
      },
      {
        "title": "Check what the capacity could earn elsewhere",
        "text": "Idle capacity sacrifices no regular sales in this example. If all 500 units instead displaced regular sales earning $10 contribution per unit, that lost $5,000 would be an opportunity cost.",
        "calculation": "With displacement: $1,000 − (500 × $10) = −$4,000"
      }
    ],
    "explorerTitle": "Change the order. Then change the capacity assumption.",
    "explorerIntro": "Variable cost stays $14/unit, new setup $1,000, and unchanged allocated fixed cost $6/unit. If capacity is constrained, every order unit displaces a regular unit earning $10 contribution. Ignore taxes and other effects; the past $900 design payment is sunk.",
    "controls": [
      {
        "key": "units",
        "label": "Order units",
        "min": 100,
        "max": 1000,
        "step": 100
      },
      {
        "key": "price",
        "label": "Special price per unit",
        "min": 12,
        "max": 30,
        "step": 1
      }
    ],
    "defaults": {
      "units": 500,
      "price": 18,
      "constrained": false
    },
    "presets": [
      {
        "label": "Profitable with idle capacity",
        "values": {
          "units": 500,
          "price": 18,
          "constrained": false
        }
      },
      {
        "label": "Break-even order",
        "values": {
          "units": 500,
          "price": 16,
          "constrained": false
        }
      },
      {
        "label": "Displace regular sales",
        "values": {
          "units": 500,
          "price": 18,
          "constrained": true
        }
      }
    ],
    "discussion": "Someone says, “Fixed costs never matter in a special-order decision.” Which explanation is closest to yours?",
    "choices": [
      {
        "key": "incremental",
        "label": "A fixed cost matters if accepting the order changes it; the new setup matters even though the existing fixed total does not.",
        "heading": "Exactly—the test is whether the amount changes.",
        "text": "The new $1,000 setup differs between accepting and rejecting. The unchanged fixed-cost allocation does not. Fixed versus variable is not the final relevance test."
      },
      {
        "key": "all",
        "label": "Every allocated fixed cost belongs in the decision because it is in the cost report.",
        "heading": "An allocation does not create an additional cash outflow.",
        "text": "The existing fixed total is the same either way. Including its allocation would obscure the order's actual incremental effect."
      },
      {
        "key": "none",
        "label": "Exclude the setup because it is a fixed payment.",
        "heading": "The setup is fixed in amount but caused by this order.",
        "text": "Rejecting avoids the $1,000 payment. That makes it relevant. A fixed cost can be incremental."
      },
      {
        "key": "unsure",
        "label": "I am unsure which costs to keep.",
        "heading": "Build two columns: accept and reject.",
        "text": "Keep future differences: order revenue, variable costs, new setup, and any lost alternative contribution. Exclude unchanged totals and unrecoverable past payments."
      }
    ],
    "formula": "Incremental profit = order revenue − incremental unit costs − new fixed costs − opportunity cost",
    "recap": [
      "With idle capacity the example adds $1,000. With displaced regular sales it loses $4,000. The capacity assumption can reverse the decision.",
      "A positive number supports acceptance financially under the assumptions; also check quality, customer pricing expectations, and effects on ongoing business."
    ],
    "limits": "Avoid treating spare capacity as free when another profitable use would be displaced. Ignore a past payment only when it is genuinely unrecoverable."
  },
  "cash-cycle": {
    "pages": [
      "The situation",
      "Follow the cash timing",
      "Explore the operating cycle",
      "Talk through the timing",
      "Bring it together"
    ],
    "storyTitle": "“We made a profit. Why is cash still tight?”",
    "story": [
      "A business holds inventory for an average of 45 days before selling it. Customers then take an average of 30 days to pay. Supplier payments occur after an average of 20 days.",
      "Sales can appear in profit before customers pay. Inventory can use cash before it becomes a cost of sales. Profit and cash are following different timing.",
      "The cash conversion cycle connects those waiting periods. It is a number of days, not a dollar cash balance."
    ],
    "takeaway": "Ask how long operations tie up cash, and how much of that time suppliers finance.",
    "steps": [
      {
        "title": "Count the wait through inventory and collections",
        "text": "The operating cycle combines time holding inventory with time collecting receivables after the sale.",
        "calculation": "45 inventory days + 30 receivable days = 75 operating-cycle days"
      },
      {
        "title": "Allow for supplier financing",
        "text": "The business has an average 20-day payment delay from suppliers. That finances part of the 75-day operating wait, so payable days are subtracted.",
        "calculation": "75 operating-cycle days − 20 payable days = 55 cash-conversion-cycle days"
      },
      {
        "title": "Change timing without inventing profit",
        "text": "If collections improve from 30 to 20 days, the cycle shortens by ten days. With sales and other conditions unchanged, less cash is tied up in receivables; the improvement does not require higher reported profit.",
        "calculation": "45 + 20 − 20 = 45 days"
      }
    ],
    "explorerTitle": "Move the three waiting periods.",
    "explorerIntro": "Treat these as steady-state average days. Hold other business conditions constant. Payment-day changes here represent agreed supplier terms, not an instruction to pay bills late.",
    "controls": [
      {
        "key": "inventory",
        "label": "Inventory days",
        "min": 0,
        "max": 90,
        "step": 5
      },
      {
        "key": "receivables",
        "label": "Receivable days",
        "min": 0,
        "max": 90,
        "step": 5
      },
      {
        "key": "payables",
        "label": "Payable days",
        "min": 0,
        "max": 120,
        "step": 5
      }
    ],
    "defaults": {
      "inventory": 45,
      "receivables": 30,
      "payables": 20
    },
    "presets": [
      {
        "label": "Original cycle",
        "values": {
          "inventory": 45,
          "receivables": 30,
          "payables": 20
        }
      },
      {
        "label": "Faster collections",
        "values": {
          "inventory": 45,
          "receivables": 20,
          "payables": 20
        }
      },
      {
        "label": "Supplier-funded cycle",
        "values": {
          "inventory": 20,
          "receivables": 15,
          "payables": 50
        }
      },
      {
        "label": "Zero-day cash cycle",
        "values": {
          "inventory": 20,
          "receivables": 15,
          "payables": 35
        }
      }
    ],
    "discussion": "Why do payable days reduce the cycle instead of increasing it?",
    "choices": [
      {
        "key": "finance",
        "label": "Supplier credit lets us hold onto cash for part of the operating wait.",
        "heading": "Yes—suppliers finance part of the wait.",
        "text": "Inventory and collection days delay receiving cash. Payable days delay paying cash. That is why they enter with opposite signs."
      },
      {
        "key": "expense",
        "label": "A payable is an expense, so subtracting it reduces profit.",
        "heading": "This formula measures days, not profit.",
        "text": "Subtracting payable days represents delayed cash payment. It does not subtract an expense from an income statement."
      },
      {
        "key": "late",
        "label": "The goal is always to pay suppliers as late as possible.",
        "heading": "Cash timing is only one part of the decision.",
        "text": "Losing discounts, damaging supply relationships, or breaching terms can outweigh a shorter cycle. Use agreed terms and evaluate the trade-offs."
      },
      {
        "key": "unsure",
        "label": "I still mix up what each period means.",
        "heading": "Separate waiting to receive cash from waiting to pay it.",
        "text": "Inventory and receivables keep you waiting for customer cash. Supplier credit lets you wait before paying suppliers, offsetting part of that gap."
      }
    ],
    "formula": "Cash conversion cycle = inventory days + receivable days − payable days",
    "recap": [
      "A shorter cycle generally ties up cash for fewer days, holding other conditions constant. It is not automatically the best business policy at any cost.",
      "A negative cycle can mean customers pay before suppliers are paid on average. It does not guarantee a large cash balance or eliminate liquidity risk."
    ],
    "limits": "These are average timing measures. You need volumes, balances, seasonality, and payment details to estimate dollars of cash released."
  },
  "npv": {
    "pages": [
      "The situation",
      "Bring the dollars to the same date",
      "Explore return and timing",
      "Talk through the comparison",
      "Bring it together"
    ],
    "storyTitle": "“The equipment saves $7,700. Is a $6,000 purchase worth it?”",
    "story": [
      "An equipment purchase costs $6,000 today. It produces one incremental $7,700 cash receipt exactly one year later. The required return is 10%.",
      "There are no other receipts, taxes, salvage proceeds, working-capital changes, or other cash flows in this starter example.",
      "The tempting calculation is $7,700 minus $6,000. But those dollars occur at different dates. First express them at the same date."
    ],
    "takeaway": "Discount the future cash to today's value before comparing it with today's investment.",
    "steps": [
      {
        "title": "Understand what the required return asks for",
        "text": "At a 10% required return, $6,000 invested today would need to become $6,600 in one year. A future receipt must compensate for that wait and required return.",
        "calculation": "$6,000 × 1.10 = $6,600 required after one year"
      },
      {
        "title": "Translate the future receipt into today's dollars",
        "text": "Divide the $7,700 future cash by 1.10. The resulting $7,000 is its present value at the required return. This is discounting, not subtracting a 10% expense.",
        "calculation": "$7,700 ÷ 1.10 = $7,000 present value"
      },
      {
        "title": "Subtract the amount invested today",
        "text": "The initial $6,000 payment is already at time zero. Do not discount it again. The project has $1,000 of value above the required return under the stated cash-flow assumptions.",
        "calculation": "$7,000 present value − $6,000 initial investment = $1,000 NPV"
      }
    ],
    "explorerTitle": "Change the wait and required return.",
    "explorerIntro": "There is one receipt at the end of the selected year and no receipts in the intervening years. The initial payment is today. No taxes, salvage, working-capital changes, or other cash flows are included.",
    "controls": [
      {
        "key": "investment",
        "label": "Investment today",
        "min": 4000,
        "max": 10000,
        "step": 500
      },
      {
        "key": "receipt",
        "label": "Single future receipt",
        "min": 4000,
        "max": 12000,
        "step": 100
      },
      {
        "key": "rate",
        "label": "Required return (%)",
        "min": 0,
        "max": 30,
        "step": 1
      },
      {
        "key": "years",
        "label": "Years until receipt",
        "min": 1,
        "max": 5,
        "step": 1
      }
    ],
    "defaults": {
      "investment": 6000,
      "receipt": 7700,
      "rate": 10,
      "years": 1
    },
    "presets": [
      {
        "label": "Original investment",
        "values": {
          "investment": 6000,
          "receipt": 7700,
          "rate": 10,
          "years": 1
        }
      },
      {
        "label": "Exactly meets required return",
        "values": {
          "investment": 6000,
          "receipt": 6600,
          "rate": 10,
          "years": 1
        }
      },
      {
        "label": "Wait three years",
        "values": {
          "investment": 6000,
          "receipt": 7700,
          "rate": 10,
          "years": 3
        }
      },
      {
        "label": "Zero required return",
        "values": {
          "investment": 6000,
          "receipt": 7700,
          "rate": 0,
          "years": 1
        }
      }
    ],
    "discussion": "A colleague reports a $1,700 NPV by subtracting the $6,000 payment from the $7,700 receipt. What needs to change?",
    "choices": [
      {
        "key": "discount",
        "label": "Discount the future receipt first, then subtract the payment already made at time zero.",
        "heading": "Yes—compare dollars at the same date.",
        "text": "At 10%, the one-year receipt is worth $7,000 today. Subtracting $6,000 gives $1,000 NPV, not the $1,700 undiscounted difference."
      },
      {
        "key": "both",
        "label": "Discount both the receipt and the initial payment by one year.",
        "heading": "Today's payment is already in today's dollars.",
        "text": "Only the future receipt needs translating back. Discounting the time-zero payment would move it to the wrong date."
      },
      {
        "key": "profit",
        "label": "Use accounting profit instead of cash receipts.",
        "heading": "NPV uses incremental cash flows.",
        "text": "Accounting expenses such as depreciation can change profit without being cash outflows. Tax effects may matter in a fuller model, but this example explicitly excludes taxes."
      },
      {
        "key": "unsure",
        "label": "I am unsure what the discount rate actually does.",
        "heading": "It gives us a common date for comparison.",
        "text": "A 10% required return makes $7,700 next year equivalent to $7,000 today: $7,000 × 1.10 = $7,700. NPV then compares that value with the $6,000 investment today."
      }
    ],
    "formula": "NPV = future receipt ÷ (1 + required return)^years − initial investment",
    "recap": [
      "Positive NPV supports accepting an independent project under the modeled assumptions. Zero NPV exactly meets the required return; negative NPV falls short.",
      "A positive NPV does not guarantee the cash flows or prove profit will be positive every year. For real projects, identify all incremental cash flows and use an appropriate discount rate."
    ],
    "limits": "This is one future receipt, not an annuity. Multiple cash flows need separate discounting, including taxes, salvage, and working-capital effects where relevant."
  }
};

export function calculateScenario(id,v){
 if(id==='absorption-variable'){
  const beginning=400,production=1200,fixedRate=5,ending=beginning+production-v.sales;
  const variableIncome=v.sales*(30-12)-6000-2000;
  const absorptionIncome=v.sales*(30-12-fixedRate)-2000;
  return {beginning,production,ending,change:ending-beginning,rate:fixedRate,variableIncome,absorptionIncome,difference:absorptionIncome-variableIncome};
 }
 if(id==='special-order'){
  const revenue=v.units*v.price,variable=v.units*14,setup=1000,opportunity=v.constrained?v.units*10:0;
  return {revenue,variable,setup,opportunity,profit:revenue-variable-setup-opportunity,excludedAllocation:v.units*6};
 }
 if(id==='cash-cycle')return {operating:v.inventory+v.receivables,supplier:v.payables,cycle:v.inventory+v.receivables-v.payables};
 if(id==='npv'){
  const factor=(1+v.rate/100)**v.years,present=v.receipt/factor;
  const raw=present-v.investment;
  return {factor,present,npv:Math.abs(raw)<1e-9?0:raw,nominal:v.receipt-v.investment};
 }
 throw new Error('Unknown teaching scenario');
}

export function normalizeScenario(id,saved){
 const scenario=SCENARIOS[id],result={...scenario.defaults};
 for(const control of scenario.controls){
  const candidate=saved?.[control.key];
  if(typeof candidate==='number'&&Number.isFinite(candidate))result[control.key]=Math.max(control.min,Math.min(control.max,Math.round(candidate/control.step)*control.step));
 }
 if(id==='special-order'&&typeof saved?.constrained==='boolean')result.constrained=saved.constrained;
 return result;
}
