// R2: colour chords / Oracle deck by level; migrated learners (old Stage 5 -> L4, Stage 6 -> L5) compared with 0.49.
const {load}=require('./harness.js');const N=load(process.argv[2],{cjg_level:'5'}),O=load(process.argv[3],{});
const key=c=>c.num+'|'+c.root+'|'+(c.q&&c.q.k!==undefined?c.q.k:c.q);
function decks(R,lv,sev,k,mode,isNew){if(isNew)R.run(`lvlSet(${lv})`);else R.run(`S.level=${lv}`);R.run(`K.k=${k};K.mode='${mode}';O.sev=${sev};`);return R.run('deck()').map(key)}
let lost={},n=0;
for(const [os,nl] of [[5,4],[6,5]])for(const mode of ['maj','min'])for(let k=0;k<12;k++)for(const sev of [false,true]){
  const a=decks(O,os,sev,k,mode,false),b=new Set(decks(N,nl,sev,k,mode,true));n++;
  for(const x of a)if(!b.has(x)){const t=`Stage ${os} -> L${nl} ${mode} sev=${sev}: ${x.split('|')[0]}`;lost[t]=(lost[t]||0)+1}}
console.log('deck comparisons',n);console.log('LOST (count = keys of 12):');for(const t in lost)console.log('  ',t,lost[t]);if(!Object.keys(lost).length)console.log('   none');
// colourRomans by level
for(const mode of ['maj','min']){for(let l=1;l<=7;l++)console.log('new colourRomans',mode,'L'+l,JSON.stringify(N.run(`colourRomans({k:0,mode:'${mode}'},false,${l})`)));
  for(const s of [4,5,6])console.log('old colourRomans',mode,'Stage'+s,JSON.stringify(O.run(`colourRomans({k:0,mode:'${mode}'},false,${s})`)))}
// sevenths in deck by level (C major)
for(let l=1;l<=7;l++){const d=decks(N,l,true,0,'maj',true);console.log('L'+l,'O.sev on -> deck has sevenths:',d.some(x=>/7/.test(x.split('|')[0])),'| size',d.length)}
for(const s of [4,5,6]){const d=decks(O,s,true,0,'maj',false);console.log('old Stage'+s,'O.sev on -> sevenths:',d.some(x=>/7/.test(x.split('|')[0])),'| size',d.length)}
