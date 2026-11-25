const {load}=require('./harness.js');const r=load(process.argv[2]||'index.html');
const g=n=>{try{return r.get(n)}catch(e){return 'ERR '+e.message}};
console.log('EARSLOT',JSON.stringify(g('EARSLOT')));console.log('EARSTAGE',JSON.stringify(g('EARSTAGE')));console.log('EDR',JSON.stringify(g('EDR')));
for(const d of Object.keys(g('EARSLOT'))){console.log('##',d);const n=g('EARSLOT')[d].length;for(let l=1;l<=n;l++){let what='';try{what=r.run(`earRungWhat(${JSON.stringify(d)},${l})`)}catch(e){what='ERR '+e.message}
  let nw='';try{nw=d==='mel'?g('LMNEW')[l]:d==='rhy'?g('LRNEWTXT')[l]:''}catch(e){}
  console.log(`  internal ${l} -> place ${g('EARSLOT')[d][l-1]} (Level ${g('EARSTAGE')[d][l-1]}) rn()=${r.run(`rn(${JSON.stringify(d)},${l})`)} | what: ${String(what).replace(/<[^>]+>/g,'')} | new: ${nw||''}`)}}
