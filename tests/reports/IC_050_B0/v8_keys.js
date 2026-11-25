// V8: draw many melodic dictation questions per internal rung; tally keys (do pitch class) and compare with the band of the RUNG's level (table 2).
// Also: legacy earGenMel, cadence rung 2 mode/keys, listening drills' key pools (0.49 C3: all 12 keys kept).
const {load}=require('./harness.js');const R=load(process.argv[2]||'index.html');
function rng(seed){let s=seed>>>0;return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296}}
const ACC={0:0,7:1,2:2,9:3,4:4,11:5,6:6,1:-5,8:-4,3:-3,10:-2,5:-1};const NM=['C','D♭','D','E♭','E','F','F♯','G','A♭','A','B♭','B'];
const band=lv=>lv<=1?1:lv>=5?99:lv;const ES=R.get('EARSTAGE'),SL=R.get('EARSLOT');let fails=0;
for(const SLV of [1,5,7]){R.run(`S.level=${SLV}`);console.log(`\n=== ladGenMel, learner level ${SLV} (keys must follow the RUNG's level) ===`);
 for(let l=1;l<=12;l++){const dos=new Map(),modes=new Map(),vars=new Map();R.ctx.__r=rng(1000+l+SLV);let err=0;const N=l===12?400:1200;
  for(let i=0;i<N;i++){let q;try{q=R.run(`ladGenMel(${l},__r)`)}catch(e){err++;if(err===1)console.log('  gen error',e.message);continue}
   if(!q||!q.key)continue;const d=q.key.do!==undefined?q.key.do:q.key.k;dos.set(d,(dos.get(d)||0)+1);const mm=(q.modeName||q.mode)+'';modes.set(mm,(modes.get(mm)||0)+1);const v=q.info&&q.info.var;if(v)vars.set(v,(vars.get(v)||0)+1)}
  const lv=ES.mel[l-1],mx=Math.max(...[...dos.keys()].map(k=>Math.abs(ACC[k])));const ok=mx<=band(lv)&&(lv>1||true);if(!ok)fails++;
  console.log(` internal ${String(l).padStart(2)} place ${String(SL.mel[l-1]).padStart(2)} L${lv}: do = ${[...dos.keys()].sort((a,b)=>Math.abs(ACC[a])-Math.abs(ACC[b])).map(k=>NM[k]+'('+ACC[k]+')').join(' ')} | max acc ${mx} vs band ${band(lv)===99?'all':band(lv)} ${ok?'OK':'** OUT OF BAND **'} | ${dos.size} keys | modes ${JSON.stringify([...modes])} ${vars.size?'vars '+JSON.stringify([...vars]):''}${err?' errors '+err:''}`)}}
console.log('\n=== legacy earGenMel(l) (l=1..3) by learner level ===');
for(const SLV of [1,3,5]){R.run(`S.level=${SLV}`);for(let l=1;l<=3;l++){const ks=new Map();R.ctx.__r=rng(77+l);for(let i=0;i<600;i++){const q=R.run(`earGenMel(${l},__r)`);const k=q.key.k+':'+q.key.mode;ks.set(k,(ks.get(k)||0)+1)}
  console.log(` S.level ${SLV} l=${l}: ${[...ks.keys()].map(k=>{const[a,m]=k.split(':');return NM[a]+(m==='min'?'m':'')+'('+ACC[m==='min'?(+a+3)%12:+a]+')'}).join(' ')}`)}}
console.log('\n=== is legacy earGenMel reachable? earGen1 source (mel branch) ===');console.log(String(R.get('earGen1')).slice(0,700));
console.log('\n=== listening-only drills: keys drawn (S.level=1, should still be all keys per 0.49 C3) ===');R.run('S.level=1');
for(const [d,ls] of [['cad',[1,2,3]],['bass',[1,2,3]],['qual',[1,2,3]]]){for(const l of ls){const ks=new Set(),md=new Map();R.ctx.__r=rng(31+l);let e=0;for(let i=0;i<3000;i++){let q;try{q=R.run(`earGen${d[0].toUpperCase()+d.slice(1)}(${l},__r)`)}catch(x){e++;continue}
   if(d==='qual')ks.add(q.root);else{ks.add(q.key.k+(q.key.mode==='min'?'m':''));md.set(q.key.mode,(md.get(q.key.mode)||0)+1)}}
  console.log(` ${d} internal ${l}: ${ks.size} distinct keys/roots: ${[...ks].sort().join(' ')} ${JSON.stringify([...md])}${e?' errors '+e:''}`)}}
console.log('\nV8 out-of-band rungs:',fails);
