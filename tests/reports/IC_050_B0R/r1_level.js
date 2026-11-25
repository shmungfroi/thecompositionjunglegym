// R1: level engine. Stored / set level always whole 1-7; valid stored level never replaced by the stage migration.
const {load}=require('./harness.js');const f=process.argv[2];let fail=0;const ok=(c,m)=>{if(!c){fail++;console.log('FAIL',m)}};
const stages=[undefined,'4','5','6','3','7','abc'];
const levels=[undefined,'','  ','abc','NaN','null','0','-3','1','2','3','4','5','6','7','8','9','99','3.5','6.49','6.5','7.4','7.6','0.4','1e3','Infinity','-Infinity','0x5',' 4 ','4abc','true'];
const MIG={4:2,5:4,6:5};let n=0;
for(const st of stages)for(const lv of levels){const ls={};if(st!==undefined)ls.cjg_stage=st;if(lv!==undefined)ls.cjg_level=lv;
  const r=load(f,ls);n++;const L=r.get('S').level;const stored=r.store.cjg_level;
  ok(Number.isInteger(L)&&L>=1&&L<=7,`S.level ${L} from ${JSON.stringify(ls)}`);
  // what should happen
  const num=(lv!==undefined&&lv.trim()!==''&&isFinite(Math.round(+lv)));
  if(num){const want=Math.min(7,Math.max(1,Math.round(+lv)));ok(L===want,`numeric stored ${lv} stage ${st}: got ${L} want ${want}`);ok(stored===String(want),`stored rewritten ${lv} -> ${stored}`);
    if(/^[1-7]$/.test(lv))ok(stored===lv&&L===+lv,`valid ${lv} kept with stage ${st}: got ${L}/${stored}`)}
  else{const want=MIG[st];if(want){ok(L===want,`migrate stage ${st} lv ${JSON.stringify(lv)}: got ${L} want ${want}`);ok(stored===String(want),'migrated value stored: '+stored)}
       else{ok(L===5,`no data default: ${L} (${JSON.stringify(ls)})`);ok(stored===lv,`nothing written when nothing to migrate: ${JSON.stringify(stored)} vs ${JSON.stringify(lv)}`)}}
  // idempotent reload
  const r2=load(f,{...r.store});ok(r2.get('S').level===L,`reload changes level ${L} -> ${r2.get('S').level} for ${JSON.stringify(ls)}`)}
console.log('load cases',n,'fail so far',fail);
// setters
const r=load(f,{cjg_level:'4',cjg_stage:'6'});
const bad=[NaN,'the cadence',undefined,null,'',' ',{}, [], 'x7', Infinity,-Infinity];   // must be ignored
for(const b of bad){for(const fn of ['lvlSet','lvlChange']){r.ctx.__b=b;try{r.run(fn+'(__b)')}catch(e){console.log('threw',fn,String(b),e.message)}const L=r.get('S').level;
  if(b===Infinity||b===-Infinity||(Array.isArray(b))){ok(Number.isInteger(L)&&L>=1&&L<=7,'range after '+fn+' '+String(b));r.run('lvlSet(4)')}
  else ok(L===4&&r.store.cjg_level==='4',`${fn}(${String(b)}) changed level to ${L}/${r.store.cjg_level}`)}}
for(const v of [-5,0,0.4,1,2.5,3,6.5,7,8,9,100,'6','9',true]){for(const fn of ['lvlSet','lvlChange']){r.run('lvlSet(4)');r.ctx.__b=v;r.run(fn+'(__b)');const L=r.get('S').level,st=r.store.cjg_level;
  const want=Math.min(7,Math.max(1,Math.round(+v)));ok(L===want&&st===String(want),`${fn}(${v}) -> ${L}/${st} want ${want}`)}}
// the reported loop: choose 6, something sets 9, reload
const a=load(f,{cjg_stage:'4',cjg_level:'6'});a.run('lvlSet(9)');const b=load(f,{...a.store});ok(b.get('S').level===7,'9 after 6 with old stage 4 -> '+b.get('S').level+' (must not be 2)');
// migrate then choose, reload
for(const st of ['4','5','6'])for(let c=1;c<=7;c++){const m=load(f,{cjg_stage:st});m.run(`lvlSet(${c})`);const m2=load(f,{...m.store});ok(m2.get('S').level===c,`stage ${st} then choose ${c} -> ${m2.get('S').level}`)}
// earStage
for(let c=1;c<=7;c++){r.run(`lvlSet(${c})`);ok(r.run('earStage()')===c,'earStage at '+c+' = '+r.run('earStage()'))}
console.log('LVN',JSON.stringify(r.get('LVN')),'LVMIG',JSON.stringify(r.get('LVMIG')));
console.log(fail?('FAILURES '+fail):'ALL PASS');
