const {chromium}=require('../frontend/node_modules/playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const {SCENARIOS}=await import('../frontend/src/scenarioModels.mjs');
 const browser=await chromium.launch({headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:960}});
 const page=await context.newPage(),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 fs.mkdirSync('ui-artifacts',{recursive:true});
 const catalog=(await (await fetch('http://127.0.0.1:8000/api/lessons')).json()).lessons;
 const configs=[
  {id:'absorption-variable',result:'difference',values:['$1,000','$0','-$2,000'],keyboard:'$3,000'},
  {id:'special-order',result:'profit',values:['$1,000','$0','-$4,000'],keyboard:'-$600'},
  {id:'cash-cycle',result:'cycle',values:['55 days','45 days','-15 days','0 days'],keyboard:'10 days'},
  {id:'npv',result:'npv',values:['$1,000.00','$0.00','-$214.88','$1,700.00'],keyboard:'$3,000.00'}
 ];
 const actions=[];page.on('request',r=>{if(r.url().endsWith('/api/lessons/action')&&r.method()==='POST')actions.push(r.postDataJSON().action)});
 await page.goto('http://127.0.0.1:8000');
 for(const config of configs){
  const id=config.id,s=SCENARIOS[id],lesson=catalog.find(l=>l.id===id);
  const card=()=>page.locator('.lesson-card').filter({has:page.getByRole('heading',{name:lesson.title,exact:true})}).getByRole('button');
  await card().click();
  await page.getByRole('heading',{name:s.storyTitle,exact:true}).waitFor();
  assert.equal(await page.getByRole('button',{name:'Check this step',exact:true}).count(),0);
  const before=actions.filter(a=>a==='answer').length;
  await page.getByRole('button',{name:'Show me the reasoning',exact:true}).click();
  assert.equal(await page.getByRole('button',{name:'Let me explore',exact:true}).isEnabled(),false);
  for(let i=0;i<2;i++)await page.getByRole('button',{name:'Show the next reasoning step',exact:true}).click();
  await page.getByRole('heading',{name:s.steps[2].title,exact:true}).waitFor();
  await page.getByRole('button',{name:'Let me explore',exact:true}).click();
  const result=()=>page.getByTestId(id+'-'+config.result);
  for(let i=0;i<s.presets.length;i++){
   await page.getByRole('button',{name:s.presets[i].label,exact:true}).click();
   assert.equal(await result().innerText(),config.values[i],id+' preset '+s.presets[i].label);
  }
  await page.getByRole('button',{name:s.presets[0].label,exact:true}).click();
  await page.getByRole('slider').first().press('Home');
  assert.equal(await result().innerText(),config.keyboard,id+' keyboard control');
  await page.screenshot({path:'ui-artifacts/'+id+'-desktop-explorer.png',fullPage:true});
  await page.reload();
  await card().click();
  await page.getByRole('heading',{name:s.explorerTitle,exact:true}).waitFor();
  assert.equal(await result().innerText(),config.keyboard,id+' persists after reload');
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:'ui-artifacts/'+id+'-mobile-explorer.png',fullPage:true});
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,id+' mobile overflow');
  await page.getByRole('button',{name:'Talk through the idea',exact:true}).click();
  await page.getByRole('button',{name:s.choices[1].label,exact:true}).click();
  await page.getByRole('heading',{name:s.choices[1].heading,exact:true}).waitFor();
  await page.getByRole('button',{name:'Connect the idea to the formula',exact:true}).click();
  await page.getByText(s.formula,{exact:true}).waitFor();
  assert.equal(actions.filter(a=>a==='answer').length,before,id+' teaching creates no graded answers');
  await page.getByRole('button',{name:'Guide my first calculation',exact:true}).click();
  await page.getByRole('button',{name:'Check this step',exact:true}).waitFor();
  if(await page.getByRole('radio').count())await page.getByRole('radio').first().check();
  else await page.getByLabel('Your number',{exact:true}).fill('0');
  await page.getByRole('button',{name:'Check this step',exact:true}).click();
  await page.locator('.coach').waitFor();
  await page.getByRole('button',{name:'← Lessons · progress saved',exact:true}).click();
  await page.setViewportSize({width:1280,height:960});
 }
 await context.close();
 const ids={"absorption-variable":"P1X-037","special-order":"P2-008","cash-cycle":"P2-004","npv":"P2-005"};
 // All four same workshops are available as read-only question support.
 for(const [id,questionId] of Object.entries(ids)){
  const q=await (await fetch('http://127.0.0.1:8000/api/question/'+questionId)).json();
  const ctx=await browser.newContext({viewport:{width:390,height:844}});
  await ctx.addInitScript(q=>{
   localStorage.setItem('cma-coach-current-question-reviewed-2026-09-30',JSON.stringify(q));
   localStorage.setItem('cma-coach-preferences-v2',JSON.stringify({part:q.part,difficulty:'All',domain:'All'}));
  },q);
  const p=await ctx.newPage();p.on('pageerror',e=>errors.push(e.message));
  let touchedLearn=false;
  p.on('request',r=>{if(r.url().endsWith('/api/lessons/start')||r.url().endsWith('/api/lessons/action'))touchedLearn=true});
  await p.route('**/api/preferences',async route=>route.request().method()==='GET'?route.fulfill({json:{part:q.part,difficulty:'All',domain:'All',resume_question_id:q.id}}):route.continue());
  await p.goto('http://127.0.0.1:8000');
  await p.getByRole('button',{name:'Practice',exact:true}).click();
  await p.getByText(q.question,{exact:true}).waitFor();
  await p.getByRole('radio').first().check();
  await p.getByRole('button',{name:'Teach me this concept',exact:true}).click();
  await p.getByRole('heading',{name:SCENARIOS[id].storyTitle,exact:true}).waitFor();
  await p.getByRole('button',{name:'Show me the reasoning',exact:true}).click();
  for(let i=0;i<2;i++)await p.getByRole('button',{name:'Show the next reasoning step',exact:true}).click();
  await p.getByRole('button',{name:'Let me explore',exact:true}).click();
  await p.getByRole('heading',{name:SCENARIOS[id].explorerTitle,exact:true}).waitFor();
  assert.equal(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,id+' preview mobile overflow');
  await p.getByRole('button',{name:'Back to my question',exact:true}).first().click();
  assert.equal(await p.getByRole('radio').first().isChecked(),true);
  assert.equal(touchedLearn,false,id+' preview changed lesson runs');
  await ctx.close();
 }
 assert.deepEqual(errors,[]);
 await browser.close();
 console.log('All four reasoning-first lessons: worked steps, explorers, signs, keyboard input, refresh/resume, misconception feedback, grading transition, mobile layout and Practice previews passed');
})().catch(e=>{console.error(e);process.exit(1)});
