import React,{useState} from 'react';

export const budgetBridge=(units,actual)=>{
 const fixed=4000,rate=6,plannedUnits=1000;
 const original=fixed+plannedUnits*rate,flexible=fixed+units*rate;
 return {fixed,rate,original,variable:units*rate,flexible,volume:flexible-original,spending:actual-flexible,total:actual-original};
};
const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
const direction=n=>n>0?'above':n<0?'below':'equal to';
const signed=n=>(n>0?'+':'')+money(n);
const pages=['The situation','Watch the reasoning','Explore without a score','Talk through the decision','Bring it together'];
function readExplorer(id){try{return JSON.parse(localStorage.getItem('cma-budget-explorer-'+id))||{units:1100,actual:10900}}catch{return {units:1100,actual:10900}}}

export default function FlexibleBudgetWorkshop({run,busy,onMove,preview=false}){
 const [explorer,setExplorer]=useState(()=>readExplorer(run.run_id));
 const [reason,setReason]=useState('');
 const [exampleStep,setExampleStep]=useState(0);
 const step=run.teaching_step;
 const b=budgetBridge(explorer.units,explorer.actual);
 function explore(next){setExplorer(next);try{localStorage.setItem('cma-budget-explorer-'+run.run_id,JSON.stringify(next))}catch{}}
 const nextNames=['Show me how to think about it','Let me explore the numbers','Talk through the decision','Connect the idea to the formula',preview?'Back to my question':'Guide my first calculation'];
 return <div className="budget-workshop">
  <div className="workshop-heading"><span className="pill">Teaching · no score</span><span>{step+1} of {pages.length} · {pages[step]}</span></div>
  <p className="workshop-promise">You are not expected to solve anything yet. We’ll build the idea before using the formula.</p>
  {step===0&&<>
   <div className="story-card"><div className="eyebrow">YOU ARE REVIEWING THE MONTH-END RESULTS</div><h3>“Costs are $900 over budget. What happened?”</h3><p>The plan was to produce <b>1,000 units</b> and spend <b>$10,000</b>. The team actually produced <b>1,100 units</b> and spent <b>$10,900</b>.</p><div className="manager-quote">“We made 100 more units. Wouldn’t you expect some extra cost?”</div><p>That is the missing piece. The original (static) budget and actual results describe <em>different amounts of work</em>. Calling the entire $900 “overspending” mixes two effects together.</p></div>
   <div className="teaching-takeaway"><b>Start with a fair comparison.</b><p>First work out what the extra output should have cost. Then ask whether actual spending was higher or lower than that expectation.</p></div>
   <p>Think of it like comparing this month’s delivery costs with a plan for fewer deliveries. More deliveries can increase total cost even when cost per delivery stays exactly on plan.</p>
  </>}
  {step===1&&<>
   <div className="card"><h3>Watch me separate the two effects.</h3><p>Budgeted variable cost is <b>$6 per unit</b>. Budgeted fixed cost is <b>$4,000 for the month</b>. We assume those relationships hold over this output range.</p><p>Variable means the <em>total</em> changes with units. Fixed means the <em>total</em> stays unchanged here—not that fixed cost per unit stays unchanged.</p></div>
   <div className="worked-step"><span>1</span><div><h3>Understand the original $10,000 plan</h3><p>1,000 units need $6,000 of variable cost. Add the $4,000 fixed total.</p><div className="lesson-formula">$6,000 variable + $4,000 fixed = $10,000</div><p>That is the budget for 1,000 units. It is not yet a fair spending benchmark for 1,100 units.</p></div></div>
   {exampleStep>=1&&<div className="worked-step"><span>2</span><div><h3>Allow for the 100 extra units</h3><p>Each extra unit should add $6. So 100 extra units explain $600 of extra cost. The $4,000 fixed total stays the same.</p><div className="lesson-formula">$10,000 original budget + $600 for extra output = $10,600</div><p><b>$10,600 is the flexible budget:</b> the original cost expectations, adjusted to the actual amount of work.</p></div></div>}
   {exampleStep>=2&&<div className="worked-step"><span>3</span><div><h3>Now compare spending at the same output</h3><p>At 1,100 units, we expected $10,600. Actual cost was $10,900. That leaves $300 above the adjusted expectation.</p><div className="budget-bridge" aria-label="900 dollar total difference is 600 dollars volume and 300 dollars unfavorable spending"><div><b>$600</b><span>Explained by extra output</span></div><div><b>$300 unfavorable</b><span>Actual above flexible budget</span></div></div><p>The $300 is worth investigating. It could combine input price, usage, or fixed-cost differences; this total alone does not tell us who caused it or why.</p></div></div>}
   {exampleStep<2&&<button className="primary" onClick={()=>setExampleStep(exampleStep+1)}>{exampleStep===0?'Show how extra output changes the budget':'Show what remains to investigate'}</button>}
  </>}
  {step===2&&<>
   <div className="card"><h3>Move the assumptions. Watch the explanation change.</h3><p>No right answer to enter. Keep the $6 variable rate and $4,000 fixed total unchanged, and explore what output and actual cost do to the comparison.</p>
    <label htmlFor="explore-output">Actual output: <b>{explorer.units.toLocaleString()} units</b></label><input id="explore-output" type="range" min="600" max="1600" step="50" value={explorer.units} onChange={e=>explore({...explorer,units:Number(e.target.value)})}/>
    <div className="explorer-presets">{[800,1000,1100,1400].map(n=><button key={n} aria-pressed={explorer.units===n} onClick={()=>explore({...explorer,units:n})}>{n.toLocaleString()} units</button>)}</div>
    <label htmlFor="explore-actual">Actual total cost: <b>{money(explorer.actual)}</b></label><input id="explore-actual" type="range" min="6000" max="15000" step="100" value={explorer.actual} onChange={e=>explore({...explorer,actual:Number(e.target.value)})}/>
    <div className="explorer-presets"><button onClick={()=>explore({...explorer,actual:b.flexible})}>Make actual equal flexible budget</button><button onClick={()=>explore({units:1100,actual:10900})}>Reset the example</button></div>
   </div>
   <div className="budget-live" aria-live="polite" aria-atomic="true"><div className="budget-table"><table><caption>Compare the same cost assumptions at different output levels</caption><thead><tr><th scope="col">Cost</th><th scope="col">Original plan<br/>1,000 units</th><th scope="col">Flexible budget<br/>{explorer.units.toLocaleString()} units</th></tr></thead><tbody><tr><th scope="row">Variable · $6/unit</th><td>$6,000</td><td>{money(b.variable)}</td></tr><tr className="fixed-row"><th scope="row">Fixed total · unchanged</th><td>$4,000</td><td>{money(b.fixed)}</td></tr><tr className="total-row"><th scope="row">Expected total</th><td>{money(b.original)}</td><td data-testid="explorer-flexible">{money(b.flexible)}</td></tr></tbody></table></div>
    <div className="budget-bridge"><div><b data-testid="explorer-volume">{signed(b.volume)}</b><span>Output effect versus original plan</span></div><div><b data-testid="explorer-spending">{signed(b.spending)}</b><span>{b.spending>0?'Unfavorable':b.spending<0?'Favorable':'No net'} flexible-budget cost variance</span></div></div>
    <div className="teaching-takeaway"><b>What this means</b><p>{explorer.units===1000?'Output matches the plan, so there is no volume effect.':explorer.units>1000?`The ${explorer.units-1000} extra units explain ${money(b.volume)} of additional expected cost.`:`Producing ${1000-explorer.units} fewer units reduces expected variable cost by ${money(-b.volume)}.`} The fixed total is still $4,000.</p><p>Actual {money(explorer.actual)} is {b.spending===0?'equal to':`${money(Math.abs(b.spending))} ${direction(b.spending)}`} the {money(b.flexible)} flexible budget.{b.spending===0?' There is no net flexible-budget cost variance, even if the original budget differs.':` That is a ${b.spending>0?'unfavorable':'favorable'} cost variance—not an explanation of its cause.`}</p><p className="bridge-equation">{money(b.original)} original + ({signed(b.volume)} output) + ({signed(b.spending)} spending) = {money(explorer.actual)} actual</p></div>
   </div>
  </>}
  {step===3&&<>
   <div className="story-card"><h3>Explain the fair comparison before doing any math.</h3><p>Return to the original example: 1,100 actual units, $10,900 actual cost, and a $10,600 flexible budget.</p><p>A manager says, “Why not just compare $10,900 with the original $10,000 budget?”</p></div>
   <div className="discussion-choices"><p>Choose the reasoning closest to yours. This is a discussion, not a scored question.</p>{[['volume','Because the original budget assumes fewer units; we need to allow for the extra work first.'],['unit','Because fixed cost per unit should stay the same.'],['excuse','Because producing more excuses any amount of extra spending.'],['unsure','I still don’t see why we change the budget.']].map(([key,label])=><button key={key} aria-pressed={reason===key} onClick={()=>setReason(key)}>{label}</button>)}</div>
   {reason&&<div className="teaching-takeaway" role="status"><h3>{reason==='volume'?'Yes—that is the purpose of the adjustment.':reason==='unit'?'Keep the fixed total unchanged, not the fixed amount per unit.':reason==='excuse'?'Extra output explains some extra cost. It does not excuse everything.':'We are changing the amount of work in the comparison, not lowering the standard.'}</h3><p>{reason==='unit'?'The same $4,000 is spread across more units, so fixed cost per unit falls. Only the variable total scales with output here.':reason==='excuse'?'The extra units justify $600 at the original $6 rate. They do not justify the remaining $300. That is why we separate the effects.':reason==='unsure'?'Imagine ordering supplies for 1,000 units, then being asked to make 1,100. The extra 100 units should use some supplies. A flexible budget allows exactly the amount the original standards permit—not whatever was actually spent.':'Holding output constant lets us ask whether actual cost met the original cost expectations at that activity level.'}</p><p>We keep the original $6 variable rate and $4,000 fixed total. At 1,100 units they imply $10,600, leaving $300 to investigate.</p><details><summary>Another way to picture it</summary><p>A plan for ten deliveries is not a fair total-cost benchmark for eleven deliveries. Allow the expected cost of delivery eleven, then investigate the remaining difference.</p></details></div>}
  </>}
  {step===4&&<>
   <div className="card"><div className="eyebrow">NOW THE FORMULA HAS A JOB</div><h3>“What should this amount of work have cost?”</h3><div className="lesson-formula">Actual units × budget variable cost per unit + budget fixed total</div><p><b>Actual units</b> makes the comparison fair. <b>Budget rates and fixed total</b> preserve the original expectations.</p><p>Then subtract the flexible budget from actual cost. For costs, positive means unfavorable; negative means favorable.</p></div>
   <div className="teaching-takeaway"><b>Your month-end explanation</b><p>“We were $900 above the original plan. Extra output explains $600. The remaining $300 is an unfavorable flexible-budget cost variance that needs investigation.”</p></div>
   <p>Next, I’ll help you calculate a different example one step at a time. You can return to this explanation whenever you need. Independent checks come later.</p>
  </>}
  <div className="workshop-navigation"><button disabled={busy||step===0} onClick={()=>onMove('teach_back')}>Back</button><button className="primary" disabled={busy||(step===1&&exampleStep<2)||(step===3&&!reason)} onClick={()=>{setReason('');setExampleStep(0);onMove('teach_next')}}>{busy?'Saving…':nextNames[step]}</button></div>
 </div>;
}
