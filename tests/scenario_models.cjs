const assert=require('node:assert/strict');
(async()=>{
 const {SCENARIOS,calculateScenario:c,normalizeScenario:n}=await import('../frontend/src/scenarioModels.mjs');
 assert.equal(Object.keys(SCENARIOS).length,4);
 assert.equal(c('absorption-variable',{sales:1000}).difference,1000);
 assert.equal(c('absorption-variable',{sales:1200}).difference,0);
 assert.equal(c('absorption-variable',{sales:1600}).difference,-2000);
 for(let sales=600;sales<=1600;sales+=100){
  const r=c('absorption-variable',{sales});
  assert.equal(r.ending,1600-sales);
  // Independent inventory-cost reconciliation, including beginning inventory.
  const fixedExpense=400*5+6000-r.ending*5;
  assert.equal(r.difference,6000-fixedExpense);
  assert.equal(r.variableIncome,sales*30-sales*12-6000-2000);
  assert.equal(r.absorptionIncome,sales*30-sales*12-fixedExpense-2000);
 }
 assert.equal(c('special-order',{units:500,price:18,constrained:false}).profit,1000);
 assert.equal(c('special-order',{units:500,price:16,constrained:false}).profit,0);
 assert.equal(c('special-order',{units:500,price:18,constrained:true}).profit,-4000);
 for(let units=100;units<=1000;units+=100)for(let price=12;price<=30;price++){
  const idle=c('special-order',{units,price,constrained:false});
  const limited=c('special-order',{units,price,constrained:true});
  assert.equal(idle.profit,units*price-units*14-1000);
  assert.equal(idle.profit-limited.profit,units*10);
  assert.equal(idle.excludedAllocation,units*6);
 }
 assert.equal(c('cash-cycle',{inventory:45,receivables:30,payables:20}).cycle,55);
 assert.equal(c('cash-cycle',{inventory:20,receivables:15,payables:35}).cycle,0);
 assert.equal(c('cash-cycle',{inventory:20,receivables:15,payables:50}).cycle,-15);
 for(let i=0;i<=90;i+=5)for(let d=0;d<=90;d+=5)for(let p=0;p<=120;p+=5)
  assert.equal(c('cash-cycle',{inventory:i,receivables:d,payables:p}).cycle,i+d-p);
 const base={investment:6000,receipt:7700,rate:10,years:1};
 assert.ok(Math.abs(c('npv',base).npv-1000)<1e-8);
 assert.equal(c('npv',{...base,receipt:6600}).npv,0);
 assert.ok(Math.abs(c('npv',{...base,years:3}).npv+214.87603305785)<1e-7);
 assert.equal(c('npv',{...base,rate:0}).npv,1700);
 for(let years=1;years<=5;years++)for(let rate=0;rate<=30;rate++){
  const result=c('npv',{...base,rate,years});
  // Discount one period at a time, independently of exponent implementation.
  let present=base.receipt;for(let t=0;t<years;t++)present/=1+rate/100;
  assert.ok(Math.abs(result.present-present)<1e-7);
  assert.ok(Math.abs(result.npv-(present-base.investment))<1e-7);
 }
 assert.ok(c('npv',{...base,years:2}).npv<c('npv',base).npv);
 assert.ok(c('npv',{...base,rate:20}).npv<c('npv',base).npv);
 for(const [id,s] of Object.entries(SCENARIOS)){
  assert.equal(s.pages.length,5);assert.equal(s.steps.length,3);assert.equal(s.choices.length,4);
  const values=n(id,{...s.defaults,[s.controls[0].key]:Infinity});
  assert.equal(values[s.controls[0].key],s.defaults[s.controls[0].key]);
  assert.ok(s.formula&&s.limits&&s.takeaway);
 }
 console.log('Four scenario models: arithmetic, signs, inventory reconciliation, opportunity cost, negative cash cycles, discount timing, boundaries and teaching content passed');
})().catch(e=>{console.error(e);process.exit(1)});
