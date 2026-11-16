import React,{useState} from 'react';
import {SCENARIOS,calculateScenario,normalizeScenario} from './scenarioModels.mjs';
const money=(value,digits=0)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',minimumFractionDigits:digits,maximumFractionDigits:digits}).format(value);
const num=value=>Number(value).toLocaleString('en-US');
function readValues(id,runId){try{return normalizeScenario(id,JSON.parse(localStorage.getItem('cma-explorer-'+id+'-'+runId)))}catch{return normalizeScenario(id,null)}}
function Table({caption,rows}){return <div className="budget-table"><table><caption>{caption}</caption><tbody>{rows.map(([label,value,testId])=><tr key={label}><th scope="row">{label}</th><td data-testid={testId}>{value}</td></tr>)}</tbody></table></div>}
function Exploration({id,runId}){
 const scenario=SCENARIOS[id];
 const [values,setValues]=useState(()=>readValues(id,runId));
 const v=values,r=calculateScenario(id,v);
 function change(next){const normalized=normalizeScenario(id,next);setValues(normalized);try{localStorage.setItem('cma-explorer-'+id+'-'+runId,JSON.stringify(normalized))}catch{}}
 return <div className="scenario-explorer">
  <div className="card"><h3>{scenario.explorerTitle}</h3><p>{scenario.explorerIntro}</p>
   {scenario.controls.map(c=><div key={c.key}><label htmlFor={'scenario-'+id+'-'+c.key}>{c.label}: <b>{['investment','receipt','price'].includes(c.key)?money(v[c.key]):num(v[c.key])}</b></label><input id={'scenario-'+id+'-'+c.key} type="range" min={c.min} max={c.max} step={c.step} value={v[c.key]} onChange={e=>change({...v,[c.key]:Number(e.target.value)})}/></div>)}
   {id==='special-order'&&<div className="explorer-presets" role="group" aria-label="Capacity assumption"><button aria-pressed={!v.constrained} onClick={()=>change({...v,constrained:false})}>Idle capacity</button><button aria-pressed={v.constrained} onClick={()=>change({...v,constrained:true})}>Displaces regular sales</button></div>}
   <div className="explorer-presets" role="group" aria-label="Explore examples">{scenario.presets.map(p=><button key={p.label} onClick={()=>change(p.values)}>{p.label}</button>)}</div>
  </div>
  <div className="scenario-live" aria-live="polite" aria-atomic="true">
   {id==='absorption-variable'&&<>
    <Table caption="Trace inventory and reconcile income" rows={[
     ['Beginning inventory',num(r.beginning)+' units'],['Production',num(r.production)+' units'],['Sales',num(v.sales)+' units'],
     ['Ending inventory',num(r.ending)+' units',id+'-ending'],['Inventory change',num(r.change)+' units',id+'-change'],
     ['Variable-costing income',money(r.variableIncome),id+'-variable'],['Absorption-costing income',money(r.absorptionIncome),id+'-absorption'],
     ['Absorption minus variable income',money(r.difference),id+'-difference']]}/>
    <div className="teaching-takeaway"><b>{r.change>0?'Inventory increased: absorption income is higher.':r.change<0?'Inventory decreased: variable-costing income is higher.':'Inventory is unchanged: incomes agree.'}</b><p>{r.change>0?num(r.change)+' net added units defer '+money(r.difference)+' of fixed manufacturing overhead.':r.change<0?'Selling '+num(-r.change)+' units from beginning inventory releases '+money(-r.difference)+' of previously deferred fixed manufacturing overhead.':'No net fixed manufacturing overhead is added to or released from inventory.'}</p><p>Both methods describe the same sales and cash flows. Changing sales changes both incomes; their difference comes from fixed overhead timing.</p><p className="bridge-equation">({num(r.ending)} ending − {num(r.beginning)} beginning) × $5 = {money(r.difference)}</p></div>
   </>}
   {id==='special-order'&&<>
    <Table caption="Accept minus reject: incremental amounts" rows={[
     ['Order revenue',money(r.revenue)],['Less incremental variable costs',money(r.variable)],['Less new setup',money(r.setup)],
     ['Less lost regular contribution',money(r.opportunity),id+'-opportunity'],['Incremental profit',money(r.profit),id+'-profit']]}/>
    <div className="teaching-takeaway"><b>{r.profit>0?'Financial benefit under these assumptions.':r.profit<0?'Financial loss under these assumptions.':'Financially break-even under these assumptions.'}</b><p>{v.constrained?'All order units displace regular sales: '+num(v.units)+' × $10 = '+money(r.opportunity)+' of lost contribution.':'Capacity is idle and regular sales do not change, so opportunity cost is $0 here.'}</p><p>The {money(r.excludedAllocation)} allocation of unchanged fixed cost and the past $900 design payment stay excluded. The new $1,000 setup stays included.</p><p>A positive result supports acceptance financially; customer expectations, quality, and long-term effects still need judgment.</p></div>
   </>}
   {id==='cash-cycle'&&<>
    <Table caption="Separate the operating wait from supplier financing" rows={[
     ['Inventory days',num(v.inventory)],['Plus receivable days',num(v.receivables)],['Operating cycle',num(r.operating)+' days'],
     ['Less payable days',num(v.payables)],['Cash conversion cycle',num(r.cycle)+' days',id+'-cycle']]}/>
    <div className="teaching-takeaway"><b>{r.cycle<0?'Supplier financing exceeds the operating wait.':r.cycle===0?'The average operating wait is fully offset.':'Operations leave a cash timing gap.'}</b><p>{r.cycle<0?'On these averages, customer cash arrives '+num(-r.cycle)+' days before suppliers are paid.':r.cycle===0?'On these averages, collection and supplier-payment timing line up.':'Inventory and collections take '+num(r.operating)+' days, while suppliers finance '+num(r.supplier)+' days. The remaining gap is '+num(r.cycle)+' days.'}</p><p>This is timing, not a dollar forecast or a guarantee of cash availability. Agreed terms, discounts, supply continuity, and seasonal peaks still matter.</p></div>
   </>}
   {id==='npv'&&<>
    <Table caption="Express future cash in today's dollars" rows={[
     ['Payment today',money(v.investment)],['One receipt after '+v.years+(v.years===1?' year':' years'),money(v.receipt)],
     ['Required return',v.rate+'%'],['Discount factor',r.factor.toFixed(4)],
     ['Present value of receipt',money(r.present,2),id+'-present'],['Net present value',money(r.npv,2),id+'-npv']]}/>
    <div className="teaching-takeaway"><b>{r.npv>0?'The project exceeds the required return in this model.':r.npv<0?'The project falls short of the required return in this model.':'The project exactly meets the required return.'}</b><p>{v.rate===0?'With a zero required return, no time-value discount is applied.':v.years>1?'The single receipt waits '+v.years+' years, so discount for all '+v.years+' years. There are no intervening receipts.':'Discount the one-year receipt before comparing it with the payment today.'}</p><p className="bridge-equation">{money(v.receipt)} ÷ (1 + {v.rate}/100)^{v.years} − {money(v.investment)} = {money(r.npv,2)}</p><p>The undiscounted cash difference is {money(r.nominal)}. NPV accounts for the modeled timing and required return; it is not a guarantee that the receipt will occur.</p></div>
   </>}
   <p className="review-note">{scenario.limits}</p>
  </div>
 </div>
}

export default function ScenarioWorkshop({lesson,run,busy,onMove,preview=false}){
 const scenario=SCENARIOS[lesson.id],step=run.teaching_step;
 const [revealed,setRevealed]=useState(1),[reason,setReason]=useState('');
 const choice=scenario.choices.find(c=>c.key===reason);
 function move(action){setReason('');setRevealed(1);onMove(action)}
 return <div className="budget-workshop scenario-workshop">
  <div className="workshop-heading"><span className="pill">Teaching · no score</span><span>{step+1} of 5 · {scenario.pages[step]}</span></div>
  <p className="workshop-promise">Build the reasoning first. Nothing on these teaching pages is graded.</p>
  {step===0&&<><div className="story-card"><div className="eyebrow">A DECISION YOU CAN RECOGNIZE</div><h3>{scenario.storyTitle}</h3>{scenario.story.map(p=><p key={p}>{p}</p>)}</div><div className="teaching-takeaway"><b>The idea to carry forward</b><p>{scenario.takeaway}</p></div></>}
  {step===1&&<><div className="card"><h3>Watch the reasoning, one step at a time.</h3><p>You do not need to enter an answer. Follow what changes, what stays fixed, and why each amount belongs.</p></div>{scenario.steps.slice(0,revealed).map((s,i)=><div className="worked-step" key={s.title}><span>{i+1}</span><div><h3>{s.title}</h3><p>{s.text}</p><div className="lesson-formula">{s.calculation}</div></div></div>)}{revealed<scenario.steps.length&&<button className="primary" onClick={()=>setRevealed(revealed+1)}>Show the next reasoning step</button>}</>}
  {step===2&&<Exploration key={lesson.id+run.run_id} id={lesson.id} runId={run.run_id}/>}
  {step===3&&<><div className="story-card"><h3>Explain the idea before doing the math.</h3><p>{scenario.discussion}</p></div><div className="discussion-choices"><p>Choose the reasoning closest to yours. This is a conversation prompt, not a scored answer.</p>{scenario.choices.map(c=><button key={c.key} aria-pressed={reason===c.key} onClick={()=>setReason(c.key)}>{c.label}</button>)}</div>{choice&&<div className="teaching-takeaway" role="status"><h3>{choice.heading}</h3><p>{choice.text}</p><p>{scenario.takeaway}</p></div>}</>}
  {step===4&&<><div className="card"><div className="eyebrow">NOW THE FORMULA HAS A PURPOSE</div><h3>{lesson.purpose}</h3><div className="lesson-formula">{scenario.formula}</div>{scenario.recap.map(p=><p key={p}>{p}</p>)}</div><div className="lesson-trap"><b>Keep the assumptions visible</b><p>{scenario.limits}</p></div><p>{preview?'Return to the original question and apply the reasoning. Using this teaching is recorded as help for that attempt.':'Next comes a different example, with a guided calculation before any independent check. You can revisit the teaching when needed.'}</p></>}
  <div className="workshop-navigation"><button disabled={busy||step===0} onClick={()=>move('teach_back')}>Back</button><button className="primary" disabled={busy||(step===1&&revealed<scenario.steps.length)||(step===3&&!reason)} onClick={()=>move('teach_next')}>{busy?'Saving…':step===0?'Show me the reasoning':step===1?'Let me explore':step===2?'Talk through the idea':step===3?'Connect the idea to the formula':preview?'Back to my question':'Guide my first calculation'}</button></div>
 </div>
}
