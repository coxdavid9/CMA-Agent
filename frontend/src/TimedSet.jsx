import React, {useEffect, useState} from 'react';
import {ErrorCause} from './StudyMetrics';

export default function TimedSet({api, part, run, setRun, onBack}) {
  const [answer,setAnswer] = useState('');
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState('');
  const [now,setNow] = useState(Date.now()/1000);
  const left = run ? Math.max(0,Math.ceil(run.deadline-now)) : 0;
  useEffect(()=>{
    const timer=setInterval(()=>setNow(Date.now()/1000),250);
    return ()=>clearInterval(timer);
  },[]);
  async function send(path, body) {
    setBusy(true);
    setError('');
    try {
      setRun(await api(path,{method:'POST',body:JSON.stringify(body)}));
      setNow(Date.now()/1000);
      setAnswer('');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  useEffect(()=>{
    if (run && !run.results && !left && !busy && !error)
      send('/api/timed/'+run.id,{finish:true});
  },[run,left,busy,error]);
  const q=run?.question;
  return <section>
    <h2>Timed set</h2>
    <button onClick={onBack}>Back to Question Practice</button>
    {error && <p role="alert">{error}</p>}
    {!run && <div className="card"><p>{part} · 25 questions · 45 minutes</p>
      <button className="primary" disabled={busy} onClick={()=>send('/api/timed/start',{part})}>Start timed set</button></div>}
    {q && <div className="question">
      <p>Question {run.index+1} of {run.total} · {Math.floor(left/60)}:{String(left%60).padStart(2,'0')} left</p>
      <h3>{q.question}</h3>
      <fieldset><legend>Choose your answer</legend>{Object.entries(q.choices).map(([key,label])=>
        <label key={key} className="choice"><input type="radio" name="timed-answer" checked={answer===key}
          onChange={()=>setAnswer(key)}/>{label}</label>)}</fieldset>
      <div className="actions"><button className="primary" disabled={busy||!answer||!left}
        onClick={()=>send('/api/timed/'+run.id,{question_id:q.id,selected:answer})}>Submit answer</button>
        <button disabled={busy} onClick={()=>send('/api/timed/'+run.id,{finish:true})}>Finish set now</button></div>
    </div>}
    {run?.results && <div><h3>Score · {run.score}/{run.total} ({Math.round(100*run.score/run.total)}%)</h3>
      {run.results.map((item,i)=><article className="card" key={item.attempt_id}>
        <h4>{i+1}. {item.question}</h4>
        <p>{item.selected ? 'Your answer: '+item.choices[item.selected]+' · '+item.elapsed_seconds+'s' : 'Unanswered'}</p>
        <p><b>Correct answer:</b> {item.choices[item.answer]}</p><p>{item.explanation}</p>
        {!item.correct && <ErrorCause api={api} attemptId={item.attempt_id}/>}
      </article>)}
      <button onClick={()=>setRun(null)}>Set up another timed set</button>
    </div>}
  </section>;
}
