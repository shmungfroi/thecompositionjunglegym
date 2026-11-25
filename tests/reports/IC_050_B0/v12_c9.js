// V12: climb 9 minor-key dominant voicing by level. Prints JSON for the music21 check.
const {load}=require('./harness.js');const R=load(process.argv[2]||'index.html');const out=[];
const keys=R.get('C9KEYS').filter(k=>k.mode==='min');
for(const lv of [1,2,3,4,5,6,7]){R.run(`S.level=${lv}`);for(const key of keys){R.ctx.__k=key;
  const L=R.run(`c9List('iiø7 V7 i7 i7',__k)`);const V=L[1];
  for(const st of ['A','B']){const vo=R.run(`c9Voice(c9List('iiø7 V7 i7 i7',__k),'rootless',${JSON.stringify(st)})`);const v=vo[1];
   out.push({lv,key:key.k,start:st,root:V.root,kind:V.kind,sym:R.run(`c9Sym(c9List('iiø7 V7 i7 i7',__k)[1],'rootless')`),form:v.form,notes:(v.up||[]).map(n=>n.name+(n.oct!==undefined?n.oct:'')),midi:(v.up||[]).map(n=>n.midi),bass:v.bass&&v.bass.name,ext:R.run(`c9Form('7b9').ext`),degs:R.run(`c9Form('7b9').${v.form||st}`)})}}}
// major-key dominant must be unaffected
R.run('S.level=5');R.ctx.__k={k:0,mode:'maj'};const M=R.run(`c9Voice(c9List('ii7 V7 Imaj7 Imaj7',__k),'rootless','A')`);
console.log(JSON.stringify({rows:out,majCheck:M.map(v=>({rn:v.ch.rn,kind:v.ch.kind,form:v.form,notes:(v.up||[]).map(n=>n.name)})),vkeys:Object.keys(M[1])}));
