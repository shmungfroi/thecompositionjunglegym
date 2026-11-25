// R6: generate Ear Lab items for the split rungs (and neighbours) with a seeded RNG; JSON out for r6_ear.py
const {load}=require('./harness.js');const R=load(process.argv[2],{cjg_level:'5'});const N=+(process.argv[3]||5000);
const out=R.run(`(()=>{const mk=s0=>{let s=s0;return()=>{s=(s*16807)%2147483647;return s/2147483647}};const o={cad:[],mel:[],meta:{}};
 for(const l of [1,2,3,4]){const r=mk(1000+l);for(let i=0;i<${N};i++){const c=earGen('cad',l,r);o.cad.push({l,cl:c.l,rung:c.rung,a:c.a,sub:c.sub||'',md:c.key.mode,k:c.key.k,rns:c.rns,ch:c.ch,opts:c.opts})}}
 for(const l of [1,2,3,4,5,6,7,8,9,10,11,13]){const r=mk(2000+l);for(let i=0;i<${N};i++){const q=ladGenMel(l,r);o.mel.push({l,cl:q.l,rung:q.rung,id:q.id,do:q.key.do,mode:q.mode,sol:q.a,nw:q.new,v:String((q.info&&(q.info.kind||q.info.var||q.info.tune))||''),home:(q.info&&q.info.home)||0,midi:q.midi,metre:q.metre||'',n:q.n})}}
 o.meta={EARSLOT,EARSTAGE,LADSTG,LADKEYS,byPlace:Object.fromEntries(Object.keys(EARSLOT).map(d=>[d,earByPlace(d)])),next:Object.fromEntries(Object.keys(EARSLOT).map(d=>[d,EARSLOT[d].map((p,i)=>earNextRung(d,i+1))])),
   first:null,cadKeys:{maj2:earCadKeys(2,'maj'),min2:earCadKeys(2,'min')},base:[earBase('mel',13),earBase('cad',4),earBase('mel',5),earBase('cad',2)]};
 return JSON.stringify(o)})()`);
require('fs').writeFileSync(process.argv[4],out);console.log('written',out.length);
