// R7: a 0.49 cjg_ear record under 4a4f458: same internal rungs, same data back; what each internal number now means.
const {load}=require('./harness.js');const [nf,of]=process.argv.slice(2);
const saved={drill:'mel',lvl:{mel:5,rhy:10,cad:2,metre:3,qual:2,bass:3,blind:2},st:{mel:{ok:5,n:9,best:3,shown:1,skipped:0,nearly:0}},letters:false,all:false,rhy:{pulse:true},names:'k',mod:'home',rd:{mel:{5:[1,1,0,1],12:[1]},rhy:{10:[1,0]},cad:{2:[1,1,1],3:[1]}},reached:{mel:[1,2,3,4,5,6],rhy:[1,2],cad:[1,2]}};
for(const [f,ls] of [[of,{cjg_stage:'6'}],[nf,{cjg_stage:'6'}],[nf,{cjg_stage:'4'}]]){const R=load(f,{...ls,cjg_ear:JSON.stringify(saved)});const E=R.get('EAR');
  console.log(f.split('/').pop(),JSON.stringify(ls),'level',R.get('S').level,'| lvl',JSON.stringify(E.lvl),'| earLvl()',R.run('earLvl()'));
  R.run('earSave()');const b=JSON.parse(R.store.cjg_ear);console.log('   re-saved lvl/rd/reached/st identical:',JSON.stringify([b.lvl,b.rd,b.reached,b.st])===JSON.stringify([saved.lvl,saved.rd,saved.reached,saved.st]));
  for(const d of ['mel','cad']){R.run(`EAR.drill='${d}'`);console.log('   ',d,'current internal',R.run('earLvl()'),typeof R.ctx.rn==='function'||true?('place '+(f===nf?R.run(`rn('${d}',earLvl())`):'n/a')):'' )}}
const N=load(nf,{cjg_level:'3'}),O=load(of,{});
// same generator behind every internal number 1-12 mel / 1-3 cad, seeded: compare old and new item streams where content is meant to be unchanged
const gen=(R,d,l,n)=>R.run(`(()=>{let s=77;const r=()=>{s=(s*16807)%2147483647;return s/2147483647};const o=[];for(let i=0;i<${n};i++){const q=${d==='mel'?`ladGenMel(${l},r)`:`earGen('cad',${l},r)`};o.push(${d==='mel'?'q.id':"q.a+'|'+q.key.k+q.key.mode+'|'+q.rns.join(' ')+'|'+q.ch.join(';')"})}return o})()`);
for(const l of [1,2,3,4,6,7,8,9,10,11]){const a=gen(O,'mel',l,60),b=gen(N,'mel',l,60);console.log('mel internal',l,'same seeded stream as 0.49:',JSON.stringify(a)===JSON.stringify(b))}
for(const l of [1,3]){const a=gen(O,'cad',l,200),b=gen(N,'cad',l,200);console.log('cad internal',l,'same seeded stream as 0.49:',JSON.stringify(a)===JSON.stringify(b))}
console.log('first rung by level (new):',JSON.stringify([1,2,3,4,5,6,7].map(l=>{N.run(`lvlSet(${l})`);return [l,N.run("earFirstRung('mel')"),N.run("earFirstRung('cad')")]})));
try{console.log('readiness text after 10 right at mel 5:',N.run("ladRdState({mel:{5:[1,1,1,1,1,1,1,1,1,1]}},'mel',5,[5]).text"));console.log('after mel 13:',N.run("ladRdState({mel:{13:[1,1,1,1,1,1,1,1,1,1]}},'mel',13,[13]).text"))}catch(e){console.log('ladRdState',e.message)}
