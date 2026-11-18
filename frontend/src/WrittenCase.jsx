import React, {useEffect,useState} from 'react';

export default function WrittenCase({api, caseId, runId}) {
  const [options,setOptions] = useState([]);
  const [data,setData] = useState(null);
  const [answer,setAnswer] = useState('');
  const [model,setModel] = useState('');
  const [scores,setScores] = useState([]);
  const [result,setResult] = useState(null);
  const [busy,setBusy] = useState(false);
  const [error,setError] = useState('');

  async function request(path, body) {
    setBusy(true);
    setError('');
    try {
      return await api(path, body === undefined ? undefined : {
        method:'POST',body:JSON.stringify(body)
      });
    } catch(e) { setError(e.message); }
    finally { setBusy(false); }
  }

  async function open(id) {
    const next = await request('/api/written-cases/'+id);
    if (next) {
      setData(next);
      setAnswer('');
      setModel('');
      setScores([]);
      setResult(null);
    }
  }

  useEffect(()=>{
    if (caseId) open(caseId);
    else request('/api/written-cases').then(list=>{if(list)setOptions(list);});
  },[caseId]);

  async function reveal() {
    const response = await request('/api/written-cases/'+data.id+'/reveal/'+scores.length,{});
    if (response) setModel(response.model_answer);
  }

  async function mark(score) {
    const next = [...scores,score];
    if (next.length === data.questions.length) {
      const saved = await request('/api/written-cases/'+data.id+'/complete',{scores:next,run_id:runId});
      if (!saved) return;
      setResult(saved.score);
    }
    setScores(next);
    setModel('');
    setAnswer('');
  }

  return <section>
    <h2>{data ? data.title : 'Written case practice · Part 1'}</h2>
    {error && <p role="alert">{error}</p>}
    {!data && !caseId && options.map(option=>
      <div className="card" key={option.id}><p>{option.domain}</p>
        <button disabled={busy} onClick={()=>open(option.id)}>{option.title}</button></div>)}
    {data && result===null && <>
      <div className="case-scenario"><p>{data.scenario}</p></div>
      <div className="card"><p>Question {scores.length+1} of {data.questions.length}</p>
        <label htmlFor="written-answer">{data.questions[scores.length]}</label>
        <textarea id="written-answer" rows={4} value={answer} disabled={!!model||busy}
          onChange={e=>setAnswer(e.target.value)}/>
        {!model && <button className="primary" disabled={!answer.trim()||busy}
          onClick={reveal}>Compare with model answer</button>}
        {model && <><h3>Model answer</h3><p>{model}</p><p>How closely did your answer match?</p>
          <div className="actions">{[[1,'Correct'],[.5,'Partial'],[0,'Missed']].map(([score,label])=>
            <button key={score} disabled={busy} onClick={()=>mark(score)}>{label}</button>)}</div></>}
      </div></>}
    {result!==null && <div className="card"><h3>Case score · {result}%</h3>
      <p>{scores.filter(x=>x===1).length} correct · {scores.filter(x=>x===.5).length} partial · {scores.filter(x=>x===0).length} missed</p>
      {!caseId && <button onClick={()=>setData(null)}>Choose another case</button>}</div>}
  </section>;
}
