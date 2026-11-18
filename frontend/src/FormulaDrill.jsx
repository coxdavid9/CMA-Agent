import React,{useEffect,useState} from 'react';

export const cardTypes = {
  numeric:'Typed calculation',
  cloze_pick:'Pick the term',
  cloze_type:'Type the term',
  reveal:'Flip cards (self-graded)'
};

export default function FormulaDrill({api,part}) {
  const [cards,setCards]=useState([]);
  const [index,setIndex]=useState(0);
  const [phase,setPhase]=useState('start');
  const [seen,setSeen]=useState([]);
  const [answers,setAnswers]=useState([]);
  const [exhausted,setExhausted]=useState(false);
  const [revealed,setRevealed]=useState(false);
  const [response,setResponse]=useState('');
  const [result,setResult]=useState(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const card=cards[index];
  const kind=card?.type || 'reveal';

  function clearCard() {
    setRevealed(false);
    setResponse('');
    setResult(null);
    setError('');
  }

  async function fetchBatch(excluded) {
    setBusy(true);
    setError('');
    const query=new URLSearchParams({part,limit:'50'});
    excluded.forEach(id=>query.append('exclude',id));
    try {
      const batch=await api('/api/formulas/due?'+query);
      clearCard();
      setCards(batch);
      setIndex(0);
      setExhausted(batch.length===0);
      setPhase(batch.length?'drill':'summary');
    } catch(e) { setError(e.message); }
    finally { setBusy(false); }
  }

  useEffect(()=>{
    if (phase==='drill' && card) setSeen(ids=>ids.includes(card.id)?ids:[...ids,card.id]);
  },[card,phase]);

  function next() {
    if (index+1===cards.length) {
      fetchBatch(seen);
    } else {
      clearCard();
      setIndex(i=>i+1);
    }
  }

  function record(verdict) {
    setResult(verdict);
    setAnswers(entries=>[...entries,{id:card.id,kind,front:card.front,...verdict}]);
  }

  function override() {
    grade(true,()=>{
      setResult({...result,correct:true,overridden:true});
      setAnswers(entries=>entries.map(entry=>entry.id===card.id?{...entry,correct:true}:entry));
    });
  }

  function done() {
    clearCard();
    setAnswers([]);
    setSeen([]);
    setCards([]);
    setIndex(0);
    setExhausted(false);
    setPhase('start');
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
  const grade=(correct,onSuccess=()=>record({correct,back:card.back,example:card.example}))=>send('grade',{correct},onSuccess);
  const submit=value=>send('answer',{response:value},record);
  return <section>
    <h2>Formula drill · {part}</h2>
    {error && <p role="alert">{error}</p>}
    {phase==='start' && <button className="primary" disabled={busy} onClick={()=>fetchBatch([])}>
      {busy?'Loading cards…':'Start formula drill'}
    </button>}
    {phase==='summary' && <SessionSummary answers={answers} exhausted={exhausted}
      busy={busy} onContinue={()=>fetchBatch(seen)} onDone={done}/>}
    {phase==='drill' && card && <article className="card">
      <div className="actions">
        <p>Card {seen.length} · {card.domain}</p>
        <button disabled={busy||!answers.length} onClick={()=>setPhase('summary')}>End session</button>
      </div>
      <h3>{card.front}</h3>
      {kind==='reveal' && !result && (!revealed
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
            <button disabled={busy} onClick={override}>
              I had it right
            </button>}
          <button className="primary" disabled={busy} onClick={next}>
            {busy?'Loading…':'Next card'}
          </button>
        </div>
      </>}
    </article>}
  </section>;
}


function SessionSummary({answers,exhausted,busy,onContinue,onDone}) {
  const correct=answers.filter(entry=>entry.correct).length;
  const misses=answers.filter(entry=>!entry.correct);
  const percent=answers.length?Math.round(100*correct/answers.length):0;
  return <div className="card">
    <h3>Session results</h3>
    {exhausted && <p>You’re caught up — no more cards due or new.</p>}
    <p><strong>{correct} of {answers.length} correct ({percent}%)</strong></p>
    <ul>{Object.entries(cardTypes).map(([type,label])=>{
      const group=answers.filter(entry=>entry.kind===type);
      return <li key={type}>{label} · {group.filter(entry=>entry.correct).length} of {group.length} correct</li>;
    })}</ul>
    {!!misses.length && <><h4>Review missed cards</h4>
      <ul>{misses.map(entry=><li key={entry.id}><b>{entry.front}</b><p>{entry.back}</p></li>)}</ul></>}
    <div className="actions">
      <button className="primary" disabled={busy} onClick={onContinue}>Keep going</button>
      <button disabled={busy} onClick={onDone}>Done</button>
    </div>
  </div>;
}
