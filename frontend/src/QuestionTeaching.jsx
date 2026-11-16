import React,{useEffect,useRef,useState} from 'react';
import FlexibleBudgetWorkshop from './FlexibleBudgetWorkshop';
import {relatedLessons,readSaved,writeSaved,markTeaching,PANEL_KEY} from './practiceTeaching.mjs';

export default function QuestionTeaching({question,api,graded=false}){
 const [catalog,setCatalog]=useState(null),[error,setError]=useState(''),[panel,setPanel]=useState(()=>readSaved(PANEL_KEY,{})[question.id]||null);
 const opener=useRef(null),heading=useRef(null);
 useEffect(()=>{setPanel(readSaved(PANEL_KEY,{})[question.id]||null)},[question]);
 useEffect(()=>{let active=true;api('/api/lessons?part='+encodeURIComponent(question.part)).then(d=>{if(active){setCatalog(d.lessons);setError('')}}).catch(()=>{if(active)setError('Teaching could not load. Your question is still here.')});return()=>{active=false}},[question.id]);
 const matches=catalog?relatedLessons(question,catalog):[];
 const lesson=matches.find(l=>l.id===panel?.lessonId);
 function save(next){const data=readSaved(PANEL_KEY,{});data[question.id]=next;writeSaved(PANEL_KEY,data);setPanel(next)}
 function open(item){if(!graded)markTeaching(question.id);save({lessonId:item.id,step:0});}
 function close(){save(null);requestAnimationFrame(()=>{opener.current?.focus();document.getElementById('practice-answer')?.scrollIntoView({block:'start',behavior:'smooth'})})}
 useEffect(()=>{if(lesson)heading.current?.focus()},[lesson?.id]);
 async function retry(){setError('');try{setCatalog((await api('/api/lessons?part='+encodeURIComponent(question.part))).lessons)}catch{setError('Teaching could not load. Your question is still here.')}}
 if(error)return <div className="question-teaching"><p role="status">{error}</p><button onClick={retry}>Retry teaching</button></div>;
 if(!catalog)return <p className="review-note" role="status">Finding concept teaching…</p>;
 if(!matches.length)return <p className="review-note">A guided lesson for this specific skill is not available yet. You can still use hints and review the explanation after answering.</p>;
 return <div className="question-teaching">
  {!lesson?<><button ref={opener} className="teach-concept-button" onClick={()=>open(matches[0])} aria-expanded={false} aria-controls="question-teaching-panel">Teach me this concept</button><p className="review-note">Open related teaching without leaving this question. Help used before answering counts as supported practice.</p>{matches.length>1&&matches.slice(1).map(l=><button key={l.id} onClick={()=>open(l)}>Learn: {l.title}</button>)}</>:<section id="question-teaching-panel" className="teaching-panel learning" aria-labelledby="question-teaching-title">
   <div className="teaching-return"><span className="pill">Practice support · no lesson score</span><button onClick={close}>Back to my question</button></div>
   <h2 id="question-teaching-title" tabIndex={-1} ref={heading}>{lesson.title}</h2>
   <p>Your question and selected answer stay saved below. This teaching preview does not start or change your Learn progress.</p>
   {lesson.id==='flexible-budget'&&panel.step<5?<FlexibleBudgetWorkshop run={{run_id:'practice-help-'+question.id,teaching_step:panel.step}} busy={false} onMove={action=>save({...panel,step:Math.max(0,Math.min(5,panel.step+(action==='teach_back'?-1:1)))})}/>:<><div className="card"><div className="eyebrow">THE IDEA</div><p>{lesson.concept}</p><div className="lesson-formula">{lesson.formula}</div></div><div className="card"><h3>Connect it to your work</h3><p>{lesson.connection}</p></div><div className="lesson-trap"><b>Watch for this</b><p>{lesson.trap}</p></div>{lesson.id==='flexible-budget'&&<p>Apply the same reasoning to your original question: hold output constant, preserve the budget cost assumptions, and investigate the remaining difference.</p>}</>}
   <div className="teaching-return"><button className="primary" onClick={close}>Back to my question</button>{lesson.id==='flexible-budget'&&panel.step===5&&<button onClick={()=>save({...panel,step:0})}>Revisit the worked example</button>}</div>
  </section>}
 </div>
}
