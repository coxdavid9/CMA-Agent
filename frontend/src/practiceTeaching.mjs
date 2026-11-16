// Exact reviewed skill links; a shared domain alone is not a lesson match.
export const TEACHING_KEY='cma-practice-teaching-v1';
export const PANEL_KEY='cma-practice-teaching-panel-v1';
export const DRAFT_KEY='cma-practice-draft-v1';
const links={
 'flexible-budget':['Flexible budget performance','Flexible budgeting'],
 'absorption-variable':['Absorption and variable costing'],
 'special-order':['Special orders','Relevant costs and revenues','Sunk and opportunity costs'],
 'cash-cycle':['Working capital management'],
 'npv':['Net present value']
};
const flexibleQuestions=new Set(['P1X-029','P1Q-045','P1Q-061','P1Q-064','P1Q-069','P1Q-074','P1Q-110','P1Q-109','V3-1-02-010']);
export function relatedLessons(question,catalog){
 if(!question||question.is_case)return [];
 const skills=new Set(question.skills||[]);
 return catalog.filter(l=>l.part===question.part&&(l.id!=='flexible-budget'||flexibleQuestions.has(question.id))&&(links[l.id]||[]).some(s=>skills.has(s)));
}
export function readSaved(key,fallback){try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}}
export function writeSaved(key,value){try{localStorage.setItem(key,JSON.stringify(value))}catch{}}
export function usedTeaching(id){return !!readSaved(TEACHING_KEY,{})[id]}
export function markTeaching(id){const data=readSaved(TEACHING_KEY,{});data[id]=true;writeSaved(TEACHING_KEY,data)}
export function resetTeaching(id){for(const key of [TEACHING_KEY,PANEL_KEY]){const data=readSaved(key,{});delete data[id];writeSaved(key,data)}}
