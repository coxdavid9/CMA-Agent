import React,{useState} from 'react';
import {FINANCIAL,financialState} from './financialModels.mjs';
const money=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:0}).format(n);
function Ledger({id,runId}){
 const m=FINANCIAL[id],key='cma-ledger-'+id+'-'+runId;
 const [count,setCount]=useState(()=>{try{return Math.max(0,Math.min(m.events.length,Math.trunc(Number(localStorage.getItem(key))||0)))}catch{return 0}});
 const state=financialState(id,count),event=m.events[count-1];
 function move(n){setCount(n);try{localStorage.setItem(key,String(n))}catch{}}
 return <div className="scenario-explorer"><div className="card"><h3>Post the transactions and watch the balances</h3><p>Opening balances appear first. Use each event to explain what moves and what stays unchanged. This walkthrough is ungraded.</p><div className="actions"><button disabled={count===0} onClick={()=>move(count-1)}>Undo last transaction</button><button className="primary" disabled={count===m.events.length} onClick={()=>move(count+1)}>Post next transaction</button><button onClick={()=>move(0)}>Reset walkthrough</button></div></div><div aria-live="polite" aria-atomic="true"><p>Transaction {count} of {m.events.length}</p>{event&&<div className="teaching-takeaway"><h3>{event[0]}</h3><p>{event[2]}</p><div className="lesson-formula">{event[3]}</div></div>}<div className="budget-table"><table><caption>Balances after the posted events</caption><tbody>{Object.entries(m.labels).map(([k,label])=><tr key={k}><th scope="row">{label}</th><td data-testid={'ledger-'+k}>{money(state[k])}</td></tr>)}</tbody></table></div></div></div>
}
export default function TransactionWorkshop({lesson,run,busy,onMove,preview=false}){
 const m=FINANCIAL[lesson.id],step=run.teaching_step;
 const [revealed,setRevealed]=useState(1),[reason,setReason]=useState(null);
 const pages=['The situation','Worked reasoning','Transaction walkthrough','Talk through the idea','Carry it forward'];
 function move(action){setRevealed(1);setReason(null);onMove(action)}
 return <div className="budget-workshop transaction-workshop"><div className="workshop-heading"><span className="pill">Teaching · no score</span><span>{step+1} of 5 · {pages[step]}</span></div><p className="workshop-promise">Follow the entries before answering any graded questions.</p>
 {step===0&&<><div className="story-card"><h3>{lesson.title}</h3><p>{m.story}</p><p>{lesson.connection}</p></div><div className="teaching-takeaway"><b>The idea to carry forward</b><p>{m.takeaway}</p></div></>}
 {step===1&&<><div className="card"><h3>Watch the reasoning, one entry at a time.</h3><p>No answer is needed here. Explain why each amount belongs before revealing the next event.</p></div>{m.events.slice(0,revealed).map((e,i)=><div className="worked-step" key={i}><span>{i+1}</span><div><h3>{e[0]}</h3><p>{e[2]}</p><div className="lesson-formula">{e[3]}</div></div></div>)}{revealed<m.events.length&&<button className="primary" onClick={()=>setRevealed(revealed+1)}>Show the next reasoning step</button>}</>}
 {step===2&&<Ledger key={lesson.id+run.run_id} id={lesson.id} runId={run.run_id}/>}
 {step===3&&<><div className="story-card"><h3>Explain the idea before doing the math.</h3><p>{m.discussion}</p></div><div className="discussion-choices"><p>This is an ungraded conversation prompt. Choose a view to explore its reasoning.</p>{m.choices.map(([label],i)=><button key={label} aria-pressed={reason===i} onClick={()=>setReason(i)}>{label}</button>)}</div>{reason!==null&&<div className="teaching-takeaway" role="status"><p>{m.choices[reason][1]}</p><p>{m.takeaway}</p></div>}</>}
 {step===4&&<><div className="card"><h3>{lesson.purpose}</h3><div className="lesson-formula">{lesson.formula}</div><p>{m.recap}</p></div><div className="lesson-trap"><b>Keep the scope visible</b><p>{m.limits}</p></div><p>{preview?'Return to your original question. This teaching counts as help for that attempt.':'Next: a fresh worked setup, then two independent checks. Teaching stays available if you need it.'}</p></>}
 <div className="workshop-navigation"><button disabled={busy||step===0} onClick={()=>move('teach_back')}>Back</button><button className="primary" disabled={busy||(step===1&&revealed<m.events.length)||(step===3&&reason===null)} onClick={()=>move('teach_next')}>{busy?'Saving…':step===0?'Show me the reasoning':step===1?'Let me trace the entries':step===2?'Talk through the idea':step===3?'Connect the idea to the formula':preview?'Back to my question':'Guide my first calculation'}</button></div></div>
}
