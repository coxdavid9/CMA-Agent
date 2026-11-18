import React, {useEffect, useState} from 'react';

const labels = {concept:"Didn't know it", formula:"Formula", calc:"Math slip",
  misread:"Misread the question", time:"Ran out of time", unknown:"Not sure"};

export function ErrorCause({api, attemptId}) {
  const [cause, setCause] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  if (!attemptId) return null;
  async function tag(value) {
    setBusy(true);
    setError('');
    try {
      await api('/api/attempts/'+attemptId+'/error-cause', {
        method:'POST', body:JSON.stringify({cause:value})
      });
      setCause(value);
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  return <div className="card"><b>What caused the miss? (Optional)</b>
    <div className="actions">{Object.entries(labels).map(([value,label]) =>
      <button key={value} disabled={busy} aria-pressed={cause===value} onClick={()=>tag(value)}>{label}</button>)}</div>
    {cause && <small role="status">Saved: {labels[cause]}</small>}
    {error && <p role="alert">{error}</p>}
  </div>;
}

export function StudyMetrics({api, part}) {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  useEffect(()=>{
    let active = true;
    setData(null);
    setError('');
    api('/api/readiness?part='+encodeURIComponent(part)).then(next=>{
      if (active) setData(next);
    }).catch(e=>{ if (active) setError(e.message); });
    return ()=>{ active = false; };
  },[api,part]);
  if (error) return <p role="alert">{error}</p>;
  if (!data) return <p>Loading study profile…</p>;
  const score = data.first_attempt_accuracy;
  const pct = value => value === null ? '—' : value+'%';
  return <div className="card">
    <h3>{part} study profile</h3>
    <h4>First-try score · {pct(score)}</h4>
    <p>{score===null ? 'Answer a fresh question to start.' :
      (score<65?'building':score<75?'close':'ready zone')+' · '+data.first_attempt_count+' first attempts'}</p>
    <p>{data.total_attempts.toLocaleString()} of 2,000 practice attempts · Fresh questions left: {data.fresh_remaining}</p>
    <p>All attempts (includes repeats) · {pct(data.overall_accuracy)}</p>
    {data.repeat_accuracy!==null && <p>Repeat accuracy · {pct(data.repeat_accuracy)}</p>}
    <h4>Why I'm missing questions</h4>
    {data.errors.length ? <ul>{data.errors.map(row=><li key={row.domain+row.error_cause}>
      {row.domain} · {labels[row.error_cause]} · {row.count}</li>)}</ul> : <p>No misses tagged yet.</p>}
    <h4>Pace by domain</h4>
    <p>MCQ time budget averages 108 seconds per question.</p>
    {data.pace.length ? <ul>{data.pace.map(row=><li key={row.domain}>
      {row.domain} · {Math.round(row.average_seconds)}s ({row.count} timed answers)
      {row.average_seconds>108 && ' · Above time budget'}</li>)}</ul> : <p>No pace recorded yet.</p>}
  </div>;
}
