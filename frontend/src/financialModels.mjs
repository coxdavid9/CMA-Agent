// Original teaching examples. Ledger events are additive and ungraded.
export const FINANCIAL = {
  "statement-links": {
    "story": "You are closing a small service-and-inventory business. The owner sees cash in the bank and wants to call it profit. Follow the entries before making that judgment.",
    "takeaway": "The statements tell different parts of one story. They must reconcile, but their totals need not be the same.",
    "initial": {
      "cash": 0,
      "receivables": 0,
      "inventory": 0,
      "capital": 0,
      "profit": 0,
      "dividends": 0,
      "operating": 0,
      "financing": 0
    },
    "labels": {
      "cash": "Cash",
      "receivables": "Receivables",
      "inventory": "Inventory",
      "capital": "Contributed capital",
      "profit": "Net income",
      "dividends": "Dividends",
      "operating": "Operating cash flow",
      "financing": "Financing cash flow"
    },
    "events": [
      [
        "Owner invests $10,000",
        {
          "cash": 10000,
          "capital": 10000,
          "financing": 10000
        },
        "Cash and contributed capital rise together. There is no customer revenue.",
        "Assets $10,000 = liabilities $0 + equity $10,000"
      ],
      [
        "Buy inventory for $3,000 cash",
        {
          "cash": -3000,
          "inventory": 3000,
          "operating": -3000
        },
        "Exchange one asset for another. No goods have been sold, so there is no cost of goods sold yet.",
        "Cash $7,000 + inventory $3,000 = equity $10,000"
      ],
      [
        "Sell on account for $5,000; goods cost $2,000",
        {
          "receivables": 5000,
          "inventory": -2000,
          "profit": 3000
        },
        "Record revenue and release the cost of sold inventory. Cash has not arrived.",
        "Revenue $5,000 − cost of goods sold $2,000 = profit $3,000"
      ],
      [
        "Collect $3,000 of the receivable",
        {
          "cash": 3000,
          "receivables": -3000,
          "operating": 3000
        },
        "Cash replaces receivables. Revenue was already recognized on sale.",
        "Receivables $5,000 − collection $3,000 = $2,000"
      ],
      [
        "Pay $1,000 for this month's rent",
        {
          "cash": -1000,
          "profit": -1000,
          "operating": -1000
        },
        "This month's consumed service reduces both current profit and cash.",
        "Profit $3,000 − rent $1,000 = $2,000"
      ],
      [
        "Pay a $500 dividend",
        {
          "cash": -500,
          "dividends": 500,
          "financing": -500
        },
        "A distribution reduces retained earnings, not net income.",
        "Retained earnings $2,000 − $500 = $1,500; assets $11,500 = equity $11,500"
      ]
    ],
    "discussion": "After collecting the receivable, should we record another $3,000 of revenue?",
    "choices": [
      [
        "Yes, because the bank increased.",
        "Cash changed, but the sale was already earned. Recording revenue again would double-count the same performance."
      ],
      [
        "No, the collection replaces an asset.",
        "Exactly. Cash rises and receivables fall equally. Profit and total assets do not change at collection."
      ]
    ],
    "recap": "The final income statement shows $2,000 profit. Equity includes $10,000 contributed capital plus $1,500 retained earnings. Cash is $8,500 because operating cash was −$1,000 and financing cash was $9,500.",
    "limits": "One period, no taxes, liabilities, beginning balances, or other transactions. Consolidation and integrated reporting are separate planned lessons."
  },
  "accrual-timing": {
    "story": "At month-end you have a customer advance, unpaid earned revenue, and an insurance payment. The bank transactions alone cannot tell you the month's profit.",
    "takeaway": "Ask what was delivered or consumed, then identify the balance left for a future period.",
    "initial": {
      "cash": 10000,
      "receivables": 0,
      "prepaid": 0,
      "unearned": 0,
      "revenue": 0,
      "expense": 0
    },
    "labels": {
      "cash": "Cash",
      "receivables": "Receivables",
      "prepaid": "Prepaid insurance",
      "unearned": "Unearned revenue",
      "revenue": "Recognized revenue",
      "expense": "Recognized expense"
    },
    "events": [
      [
        "Receive a $3,600 service advance",
        {
          "cash": 3600,
          "unearned": 3600
        },
        "There is an obligation to provide service. Cash arrives before revenue is earned.",
        "Cash +$3,600; liability +$3,600; revenue $0"
      ],
      [
        "Deliver $1,200 of the promised service",
        {
          "unearned": -1200,
          "revenue": 1200
        },
        "Reduce the obligation as performance is satisfied.",
        "Unearned $3,600 − $1,200 = $2,400"
      ],
      [
        "Perform another $2,500 service on account",
        {
          "receivables": 2500,
          "revenue": 2500
        },
        "Earned but uncollected revenue creates a receivable.",
        "Revenue $1,200 + $2,500 = $3,700"
      ],
      [
        "Collect $1,000 from that receivable",
        {
          "cash": 1000,
          "receivables": -1000
        },
        "Collection changes the type of asset, not the period's earnings.",
        "Receivables $2,500 − $1,000 = $1,500"
      ],
      [
        "Pay $2,400 for future insurance",
        {
          "cash": -2400,
          "prepaid": 2400
        },
        "An unconsumed benefit is an asset at payment.",
        "Cash −$2,400; prepaid asset +$2,400"
      ],
      [
        "Consume $200 of the insurance coverage",
        {
          "prepaid": -200,
          "expense": 200
        },
        "Recognize only the portion used in this period.",
        "Prepaid $2,200; profit $3,700 − $200 = $3,500"
      ]
    ],
    "discussion": "Does the $2,400 insurance payment all reduce this month's profit?",
    "choices": [
      [
        "Yes, we paid it this month.",
        "The payment purchases future coverage. Expense follows consumption, so only $200 belongs in this period."
      ],
      [
        "Only the $200 used this month.",
        "Right. The remaining $2,200 is a prepaid asset. This separates the bank movement from period expense."
      ]
    ],
    "recap": "Cash ends at $12,200, while profit is $3,500. Receivables, prepaid coverage, and unearned revenue explain why the amounts differ.",
    "limits": "The service is earned in the amounts given, coverage is consumed as stated, and there are no other transactions. This is a timing lesson, not all expense-recognition exceptions."
  },
  "cash-flow-bridge": {
    "story": "Your month shows $5,000 profit, but the owner asks where the cash went. Prepare a bridge that separates operating timing, equipment spending, and borrowing.",
    "takeaway": "Adjust profit for timing and noncash items, then classify the other cash movements separately.",
    "initial": {
      "operating": 5000,
      "investing": 0,
      "financing": 0,
      "change": 5000
    },
    "labels": {
      "operating": "Operating cash flow bridge",
      "investing": "Investing cash flow",
      "financing": "Financing cash flow",
      "change": "Net cash change"
    },
    "events": [
      [
        "Add back $1,000 depreciation",
        {
          "operating": 1000,
          "change": 1000
        },
        "Depreciation reduced profit without a current cash payment. Undo that reduction when reconciling profit to cash.",
        "$5,000 + $1,000 = $6,000"
      ],
      [
        "Receivables increased $2,000",
        {
          "operating": -2000,
          "change": -2000
        },
        "Some recognized revenue is still uncollected. Subtract the increase.",
        "$6,000 − $2,000 = $4,000"
      ],
      [
        "Inventory increased $500",
        {
          "operating": -500,
          "change": -500
        },
        "More cost remains in inventory instead of flowing through expense. This ties up operating cash, holding other factors constant.",
        "$4,000 − $500 = $3,500"
      ],
      [
        "Operating payables increased $800",
        {
          "operating": 800,
          "change": 800
        },
        "Some operating purchases remain unpaid. Add this source of supplier financing within operating activities.",
        "$3,500 + $800 = $4,300 CFO"
      ],
      [
        "Buy equipment for $4,000 cash",
        {
          "investing": -4000,
          "change": -4000
        },
        "Equipment acquisition is investing. Do not subtract it again inside operating cash flow.",
        "$4,300 operating − $4,000 investing = $300"
      ],
      [
        "Borrow $3,000 cash",
        {
          "financing": 3000,
          "change": 3000
        },
        "Borrowing is financing, not revenue. With $2,000 opening cash, ending cash is $5,300.",
        "$4,300 − $4,000 + $3,000 = $3,300 cash increase"
      ]
    ],
    "discussion": "Did the depreciation addback put $1,000 into the bank?",
    "choices": [
      [
        "Yes, the addback is a receipt.",
        "No receipt occurred. The addback removes a noncash expense already subtracted in profit."
      ],
      [
        "No, it reverses a noncash deduction.",
        "Correct. Counting it as a receipt would confuse a reconciliation adjustment with an actual bank transaction."
      ]
    ],
    "recap": "CFO is $4,300. Net cash increases $3,300 after investing and financing. Opening cash of $2,000 therefore becomes $5,300.",
    "limits": "All working-capital changes arise from operations; no acquisitions, disposals, foreign exchange, or other noncash balance changes. Interest and tax classification exceptions are outside this example."
  },
  "revenue-delivery": {
    "story": "A customer pays $6,000 upfront for a service contract. It has one performance obligation satisfied over time, because the customer receives and consumes benefits as you work. Measured completion tracks delivery faithfully.",
    "takeaway": "Identify the promise and its satisfaction before deciding how much of the payment is revenue.",
    "initial": {
      "cash": 0,
      "revenue": 0,
      "unearned": 0
    },
    "labels": {
      "cash": "Cash received",
      "revenue": "Cumulative earned revenue",
      "unearned": "Remaining contract liability"
    },
    "events": [
      [
        "Receive the $6,000 advance",
        {
          "cash": 6000,
          "unearned": 6000
        },
        "The five steps are: identify the contract, identify the performance obligation, determine the price, allocate it, recognize revenue as the obligation is satisfied. Here all $6,000 goes to one obligation.",
        "Cash $6,000 = liability $6,000; revenue $0"
      ],
      [
        "Deliver the first 25% of service",
        {
          "revenue": 1500,
          "unearned": -1500
        },
        "Recognize the measured performance actually delivered, not the full advance.",
        "$6,000 × 25% = $1,500 earned; $4,500 unearned"
      ],
      [
        "Deliver another 25% of service",
        {
          "revenue": 1500,
          "unearned": -1500
        },
        "At 50% completion, cumulative revenue is $3,000. Only the additional $1,500 belongs to this step.",
        "$6,000 × 50% = $3,000 cumulative revenue"
      ],
      [
        "Complete the remaining 50%",
        {
          "revenue": 3000,
          "unearned": -3000
        },
        "The obligation is fully satisfied. The entire price is now earned, without any new cash collection.",
        "Revenue $6,000; remaining liability $0"
      ]
    ],
    "discussion": "Would an invoice by itself prove that the entire $6,000 is earned?",
    "choices": [
      [
        "Yes, invoicing creates earned revenue.",
        "Billing documents a right to payment, but performance determines revenue recognition. Examine the contract and delivery."
      ],
      [
        "No, we need evidence of satisfied performance.",
        "Correct. This contract supports over-time recognition; another contract may require a point-in-time control transfer."
      ]
    ],
    "recap": "The customer paid once. Revenue was earned in stages. At each stage, cash remains $6,000 while the contract liability becomes earned revenue.",
    "limits": "A valid contract, one obligation, fixed price, and reliable performance measure are assumed. Multiple obligations, variable consideration, modifications, and point-in-time recognition still need separate lessons."
  },
  "inventory-measurement": {
    "story": "In a periodic system, buy 100 units at $10 and 100 units at $14. Sell 150 units at $20. Compare cost assignment before doing the valuation check.",
    "takeaway": "A margin change can come from cost assignment as well as selling price and purchasing performance.",
    "initial": {
      "available": 0,
      "revenue": 0,
      "fifoCogs": 0,
      "fifoInventory": 0,
      "averageCogs": 0,
      "averageInventory": 0
    },
    "labels": {
      "available": "Goods available at cost",
      "revenue": "Sales revenue",
      "fifoCogs": "FIFO expense including write-down",
      "fifoInventory": "FIFO ending inventory",
      "averageCogs": "Average expense including write-down",
      "averageInventory": "Average ending inventory"
    },
    "events": [
      [
        "Buy the first 100 units at $10",
        {
          "available": 1000,
          "fifoInventory": 1000,
          "averageInventory": 1000
        },
        "Purchase cost is an asset until units are sold or written down.",
        "100 × $10 = $1,000"
      ],
      [
        "Buy another 100 units at $14",
        {
          "available": 1400,
          "fifoInventory": 1400,
          "averageInventory": 1400
        },
        "Periodic weighted-average cost is total cost divided by total units available.",
        "$2,400 ÷ 200 = $12 per unit"
      ],
      [
        "Sell 150 units at $20",
        {
          "revenue": 3000,
          "fifoCogs": 1700,
          "fifoInventory": -1700,
          "averageCogs": 1800,
          "averageInventory": -1800
        },
        "FIFO assigns 100 old units and 50 new units to cost of goods sold. Average assigns $12 to each sold unit.",
        "FIFO COGS $1,700, inventory $700; average COGS $1,800, inventory $600"
      ],
      [
        "Check remaining units against NRV of $13 each",
        {
          "fifoCogs": 50,
          "fifoInventory": -50
        },
        "FIFO inventory cost $700 exceeds $650 NRV, so recognize $50 loss. Average cost $600 is already below $650, so there is no write-down.",
        "FIFO profit $3,000 − $1,750 = $1,250; average profit $3,000 − $1,800 = $1,200"
      ]
    ],
    "discussion": "Can we write weighted-average inventory up from $600 to the $650 NRV?",
    "choices": [
      [
        "Yes, use the current higher amount.",
        "Lower of cost and NRV caps this inventory at cost. It does not create an upward revaluation."
      ],
      [
        "No, retain the lower $600 cost.",
        "Correct. FIFO needs a $50 write-down, but weighted average remains at $600. The same NRV can affect the two cost bases differently."
      ]
    ],
    "recap": "Before valuation, FIFO gross profit is $1,300 and average gross profit $1,200. After the FIFO $50 loss, profit becomes $1,250. Both methods still reconcile the original $2,400 between expense and ending inventory.",
    "limits": "Periodic FIFO and weighted average, no beginning inventory, freight, returns, taxes, or prior write-down. The LIFO/retail lower-of-cost-or-market rule and inventory errors are planned separately."
  },
  "receivable-allowance": {
    "story": "Gross receivables are $10,000 and the allowance already has a $200 credit balance. The exercise gives a required expected loss estimate of 5% of gross receivables. Do not record the full target as a new expense.",
    "takeaway": "The required ending balance and this period's adjustment are different amounts.",
    "initial": {
      "gross": 10000,
      "allowance": 200,
      "net": 9800,
      "expense": 0,
      "cash": 0
    },
    "labels": {
      "gross": "Gross receivables",
      "allowance": "Allowance credit balance",
      "net": "Net receivables",
      "expense": "Loss expense recognized",
      "cash": "Cash collected"
    },
    "events": [
      [
        "Set required ending allowance to $500",
        {
          "allowance": 300,
          "net": -300,
          "expense": 300
        },
        "The target is $10,000 × 5% = $500. Only $300 is missing from the existing $200 credit balance.",
        "Adjustment $500 − $200 = $300; net receivables $9,500"
      ],
      [
        "Write off a $400 uncollectible balance",
        {
          "gross": -400,
          "allowance": -400
        },
        "Reduce both gross receivables and the allowance by $400. Net receivables and loss expense do not change at write-off.",
        "$9,600 gross − $100 allowance = $9,500 net"
      ],
      [
        "Collect $2,000 from another customer",
        {
          "gross": -2000,
          "net": -2000,
          "cash": 2000
        },
        "Collection replaces a receivable with cash. It does not earn revenue again or create another loss.",
        "$7,600 gross − $100 allowance = $7,500 net; cash +$2,000"
      ]
    ],
    "discussion": "When the $400 balance is written off, should we record another $400 loss expense?",
    "choices": [
      [
        "Yes, the customer has now failed to pay.",
        "Under the allowance method, the expected loss was already estimated. The write-off uses the allowance; it does not record the same loss again."
      ],
      [
        "No, reduce receivables and the allowance together.",
        "Correct. Gross and allowance fall equally, so net receivables stay at $9,500 at that instant."
      ]
    ],
    "recap": "The estimate created $300 expense. The write-off used $400 allowance without another expense. Collection later changed receivables into cash.",
    "limits": "The loss rate is supplied, not derived. Assume the remaining $100 allowance is appropriate after the write-off; a real reporting-date estimate must be reassessed. Recoveries and factoring are planned separately."
  }
};
export function financialState(id,count){const m=FINANCIAL[id];if(!m)throw new Error('Unknown financial lesson');const n=Math.max(0,Math.min(m.events.length,Math.trunc(Number(count)||0)));return m.events.slice(0,n).reduce((s,e)=>{for(const [k,v] of Object.entries(e[1]))s[k]+=v;return s},{...m.initial})}
