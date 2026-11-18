import React,{useEffect,useState} from 'react';
import {cardTypes} from './FormulaDrill';

export default function FormulaStats({api,part}) {
  const [data,setData]=useState(null);
  const [error,setError]=useState('');
  useEffect(()=>{
    let active=true;
    setData(null);
    setError('');
    api('/api/formulas/stats?part='+encodeURIComponent(part))
      .then(stats=>{if(active)setData(stats);})
      .catch(e=>{if(active)setError(e.message);});
    return ()=>{active=false;};
  },[api,part]);
  return <section className="card">
    <h3>Formula drill · {part}</h3>
    {error && <p role="alert">{error}</p>}
    {!data && !error && <p>Loading formula stats…</p>}
    {data && (data.total_attempts===0
      ? <p>No formula drills yet — your stats will appear here.</p>
      : <>
        <p>{data.total_attempts} attempts · {data.accuracy}% correct</p>
        <p>{data.cards_seen} of {data.total_cards} cards seen · {data.due_now} due now · {data.mastered} mastered</p>
        <ul>{Object.entries(cardTypes).map(([kind,label])=>{
          const row=data.by_type[kind];
          return <li key={kind}>{label} · {row.accuracy===null?'No attempts':
            row.correct+' of '+row.attempts+' correct ('+row.accuracy+'%)'}</li>;
        })}</ul>
      </>)}
  </section>;
}
