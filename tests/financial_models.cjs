const assert=require('node:assert/strict');
const fs=require('node:fs');
(async()=>{
 const {FINANCIAL,financialState:s}=await import('../frontend/src/financialModels.mjs');
 const {relatedLessons}=await import('../frontend/src/practiceTeaching.mjs');
 const metadata=JSON.parse(fs.readFileSync('data/financial_lessons.json','utf8'));
 assert.deepEqual(Object.keys(FINANCIAL).sort(),metadata.map(l=>l.id).sort());
 for(const id of Object.keys(FINANCIAL)){
  const m=FINANCIAL[id];
  for(let n=0;n<=m.events.length;n++){
   const v=s(id,n);
   for(const k of Object.keys(m.labels))assert.ok(Number.isFinite(v[k]),id+' '+k);
   if(id==='statement-links'){
    assert.equal(v.cash+v.receivables+v.inventory,v.capital+v.profit-v.dividends);
    assert.equal(v.cash,v.operating+v.financing);
   }
   if(id==='accrual-timing')assert.equal(v.cash+v.receivables+v.prepaid,v.unearned+10000+v.revenue-v.expense);
   if(id==='cash-flow-bridge')assert.equal(v.change,v.operating+v.investing+v.financing);
   if(id==='revenue-delivery')assert.equal(v.cash,v.revenue+v.unearned);
   if(id==='inventory-measurement'){
    assert.equal(v.available,v.fifoInventory+v.fifoCogs);
    assert.equal(v.available,v.averageInventory+v.averageCogs);
   }
   if(id==='receivable-allowance')assert.equal(v.net,v.gross-v.allowance);
  }
  assert.deepEqual(s(id,-5),m.initial);
  assert.deepEqual(s(id,999),s(id,m.events.length));
 }
 assert.deepEqual(s('statement-links',6),{cash:8500,receivables:2000,inventory:1000,capital:10000,profit:2000,dividends:500,operating:-1000,financing:9500});
 assert.equal(s('accrual-timing',6).revenue-s('accrual-timing',6).expense,3500);
 assert.equal(s('cash-flow-bridge',6).operating,4300);
 assert.equal(s('cash-flow-bridge',6).change,3300);
 assert.equal(s('revenue-delivery',2).revenue,1500);
 assert.equal(s('inventory-measurement',3).fifoCogs,1700);
 assert.equal(s('inventory-measurement',4).fifoInventory,650);
 assert.equal(s('inventory-measurement',4).averageInventory,600);
 assert.equal(s('receivable-allowance',1).net,s('receivable-allowance',2).net);
 assert.equal(s('receivable-allowance',3).expense,300);
 const ids={'statement-links':'P1Q-029','accrual-timing':'P1Q-003','cash-flow-bridge':'P1Q-004','revenue-delivery':'V3-1-01-004','inventory-measurement':'V3-1-01-007','receivable-allowance':'P1Q-010'};
 for(const [id,qid] of Object.entries(ids))assert.ok(relatedLessons({id:qid,part:'Part 1'},metadata).some(l=>l.id===id));
 assert.deepEqual(relatedLessons({id:'P1Q-019',part:'Part 1',skills:['Asset valuation']},metadata),[],'Depreciation must not link to inventory teaching');
 assert.deepEqual(relatedLessons({id:'P1Q-010',part:'Part 2'},metadata),[]);
 console.log('Six financial workshops: balanced entries, cash bridges, inventory reconciliation, revenue timing, write-off neutrality and precise question links passed');
})().catch(e=>{console.error(e);process.exit(1)});
