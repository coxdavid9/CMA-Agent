import React from 'react';
import plan from '../../data/part1_curriculum.json';
export default function CurriculumPlan({catalog,busy,onStart}){
 const built=new Map(catalog.map(l=>[l.id,l])),total=plan.subtopics.reduce((n,t)=>n+t.lessons.length,0),available=plan.subtopics.reduce((n,t)=>n+t.lessons.filter(l=>built.has(l.id)).length,0);
 return <details className="card curriculum-plan"><summary>Part 1 course build checklist · {available} of {total} proposed lessons available</summary><p>{plan.scope}</p><p>Availability describes content built, not your learning progress. Lesson results and recall dates are shown separately.</p>{plan.subtopics.map(t=><details key={t.id}><summary>{t.id} · {t.title} · {t.lessons.filter(l=>built.has(l.id)).length}/{t.lessons.length} available</summary><ul>{t.lessons.map(l=><li key={l.id}>{built.has(l.id)?<><button disabled={busy} className="text-button" onClick={()=>onStart(built.get(l.id))}>{l.title}</button> · Available · {built.get(l.id).status}</>:<>{l.title} · Planned</>}</li>)}</ul></details>)}</details>
}
