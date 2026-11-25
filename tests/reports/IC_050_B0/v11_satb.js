// V11: every SATB rule key emitted by chordIssues/pairIssues must have a level in SATBLV; findings carry lvl/later; nothing is filtered by level.
const fs=require('fs');const {load}=require('./harness.js');const R=load(process.argv[2]||'index.html');
const html=fs.readFileSync(process.argv[2]||'index.html','utf8').split('\n');
const a=html.findIndex(l=>l.startsWith('function pairIssues')),b=html.findIndex(l=>l.startsWith('function checkSATB'));
const emitted=[...new Set(html.slice(a,b).join('\n').match(/rule:'(\w+)'/g).map(x=>x.slice(6,-1)))].sort();
const LV=R.get('SATBLV');console.log('rules emitted (lines',a+1,'-',b,'):',emitted.join(' '));
console.log('without a level in SATBLV:',emitted.filter(r=>!(r in LV)).join(' ')||'none','| SATBLV keys never emitted:',Object.keys(LV).filter(r=>!emitted.includes(r)).join(' ')||'none');
console.log('by level:',JSON.stringify([3,4,5,6,7].map(l=>[l,Object.keys(LV).filter(k=>LV[k]===l)])));
// functional: a deliberately faulty progression in C major, checked at each learner level
R.run("K.k=0;K.mode='maj'");
const list=[{root:'C',q:'',inv:0},{root:'G',q:'7',inv:0},{root:'C',q:'',inv:0}];R.ctx.__list=list;
// voices low to high (bass, tenor, alto, soprano): parallel 5ths C-G -> G-D, 7th (F) rising to G, leading note B falling, wide spacing
const S4=[[48,55,64,72],[43,62,65,71],[48,64,67,67]];R.ctx.__S4=S4;
let base=null;
for(const lv of [1,2,3,4,5,6,7]){R.run(`S.level=${lv}`);let iss;try{iss=R.run('checkSATB(__S4,__list)')}catch(e){console.log('L'+lv,'ERR',e.message);continue}
  const sig=iss.map(e=>e.rule+':'+e.sev+':'+e.at.join('-')).join(',');if(base===null)base=sig;
  console.log(`L${lv}: ${iss.length} findings; same set as L1: ${sig===base}; later: ${iss.filter(e=>e.later).map(e=>e.rule+'@'+e.lvl).join(' ')||'-'}; all carry lvl: ${iss.every(e=>typeof e.lvl==='number')}`);
  if(lv===3)iss.forEach(e=>console.log('    ',e.rule,e.sev,'lvl',e.lvl,'later',e.later,'|',e.text.replace(/<[^>]+>/g,'¦').slice(0,150)))}
