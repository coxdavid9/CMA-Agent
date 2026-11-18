import React,{useEffect,useState} from 'react';

export default function FormulaDrill({api,part}) {
  const [cards,setCards]=useState(null);
  const [index,setIndex]=useState(0);
  const [revealed,setRevealed]=useState(false);
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
  async function grade(correct) {
    setBusy(true);
    setError('');
    try {
      await api('/api/formulas/grade',{method:'POST',body:JSON.stringify({formula_id:card.id,correct})});
      setRevealed(false);
      setIndex(index+1);
    } catch(e) { setError(e.message); }
    finally { setBusy(false); }
  }
  return <section>
    <h2>Formula drill · {part}</h2>
    {error && <p role="alert">{error}</p>}
    {!cards && !error && <p>Loading formulas…</p>}
    {cards && !card && <p>{index ? 'Session complete. Review more due cards by reopening Formula drill.' : 'No formulas due right now.'}</p>}
    {card && <article className="card">
      <p>{index+1} of {cards.length} · {card.domain}</p>
      <h3>{card.front}</h3>
      {!revealed ? <button onClick={()=>setRevealed(true)}>Reveal formula</button> : <>
        <p className="lesson-formula">{card.back}</p><p>{card.example}</p>
        <div className="actions"><button disabled={busy} onClick={()=>grade(true)}>Got it</button>
          <button disabled={busy} onClick={()=>grade(false)}>Missed it</button></div>
      </>}
    </article>}
  </section>;
}
