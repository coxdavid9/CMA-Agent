import React,{useEffect,useState} from 'react';

export default function FormulaDrill({api,part}) {
  const [cards,setCards]=useState(null);
  const [index,setIndex]=useState(0);
  const [revealed,setRevealed]=useState(false);
  const [response,setResponse]=useState("");
  const [result,setResult]=useState(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  useEffect(()=>{
    let active=true;
    api('/api/formulas/due?part='+encodeURIComponent(part))
      .then(data=>{if(active)setCards(data);})
      .catch(e=>{if(active)setError(e.message);});
    return ()=>{active=false;};
  },[api,part]);
  const card=cards?.[index];
  const kind=card?.type || 'reveal';
  function next() {
    setRevealed(false);
    setResponse('');
    setResult(null);
    setError('');
    setIndex(i=>i+1);
  }
  async function send(action, body, onSuccess) {
    setBusy(true);
    setError('');
    try {
      const data=await api('/api/formulas/'+action,{
        method:'POST',body:JSON.stringify({formula_id:card.id,...body})
      });
      onSuccess(data);
    } catch(e) { setError(e.message); }
    finally { setBusy(false); }
  }
  const grade=(correct,onSuccess=next)=>send('grade',{correct},onSuccess);
  const submit=value=>send('answer',{response:value},setResult);
  return <section>
    <h2>Formula drill · {part}</h2>
    {error && <p role="alert">{error}</p>}
    {!cards && !error && <p>Loading formulas…</p>}
    {cards && !card && <p>{index ? 'Session complete. Review more due cards by reopening Formula drill.' : 'No formulas due right now.'}</p>}
    {card && <article className="card">
      <p>{index+1} of {cards.length} · {card.domain}</p>
      <h3>{card.front}</h3>
      {kind==='reveal' && (!revealed
        ? <button onClick={()=>setRevealed(true)}>Reveal formula</button>
        : <>
          <p className="lesson-formula">{card.back}</p><p>{card.example}</p>
          <div className="actions"><button disabled={busy} onClick={()=>grade(true)}>Got it</button>
            <button disabled={busy} onClick={()=>grade(false)}>Missed it</button></div>
        </>)}
      {kind==='cloze_pick' && !result && <div className="actions">
        {card.options.map(option=><button key={option} disabled={busy}
          onClick={()=>submit(option)}>{option}</button>)}
      </div>}
      {(kind==='numeric'||kind==='cloze_type') && !result &&
        <form onSubmit={e=>{e.preventDefault();submit(response);}}>
          <label htmlFor="formula-response">{kind==='numeric'?'Your number':'Missing part'}</label>
          <input id="formula-response" type="text" className="lesson-number"
            inputMode={kind==='numeric'?'decimal':'text'} autoComplete="off" maxLength={500}
            value={response} onChange={e=>setResponse(e.target.value)} disabled={busy}/>
          <button className="primary" disabled={busy||!response.trim()}>Check answer</button>
        </form>}
      {result && <>
        <div role="status">
          <strong>{result.overridden?'Marked correct':result.correct?'Correct':'Review the formula'}</strong>
          <p className="lesson-formula">{result.back}</p><p>{result.example}</p>
        </div>
        <div className="actions">
          {!result.correct && result.allow_override &&
            <button disabled={busy} onClick={()=>grade(true,()=>setResult({...result,correct:true,overridden:true}))}>
              I had it right
            </button>}
          <button className="primary" disabled={busy} onClick={next}>
            {index+1===cards.length?'Finish session':'Next card'}
          </button>
        </div>
      </>}
    </article>}
  </section>;
}
