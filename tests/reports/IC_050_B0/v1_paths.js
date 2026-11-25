// V1: floors, fallbacks and auto-jump paths at each level (no browser).
const {load}=require('./harness.js');const f=process.argv[2]||'index.html';const R=load(f);
const j=x=>JSON.stringify(x);
console.log('--- auto-jump with a hidden chord (aug 6ths are tagged l:9)');
console.log(' Q levels above 7:',j(R.get('Q').filter(q=>q.l>7).map(q=>[q.k,q.l])));
R.run("K.k=0;K.mode='maj'");
for(const rn of ['It6','Fr6','Ger6','bII:1']){let p;try{p=R.run(`parseRoman(${j(rn)},K)`)}catch(e){p='ERR '+e.message}console.log(' parseRoman',rn,'->',j(p&&{root:p.root,q:p.q,inv:p.inv}))}
console.log(' C8EX aug-6th examples:',j(R.get('C8EX').filter(x=>/It|Fr|Ger/.test(x.k)).map(x=>[x.k,x.l,x.maj,x.min])));
R.run('S.level=6');const q=R.run("parseRoman('Ger6',K)").q;R.ctx.__q=q;
R.run("if(Q.find(x=>x.k===__q).l>S.level){lvlSet(Q.find(x=>x.k===__q).l)}");
console.log(' after the Gym "open in Seed Bank" jump for',q,': S.level =',R.get('S').level,'| stored cjg_level =',R.store.cjg_level,'| earStage() =',R.run('earStage()'));
const R2=load(f,{...R.store,cjg_stage:'4'});console.log(' next visit (old cjg_stage=4 still stored): S.level =',R2.get('S').level,' stored',R2.store.cjg_level);
const R3=load(f,{...R.store});console.log(' next visit (no old stage): S.level =',R3.get('S').level);
console.log('--- climb 11 chord options by level (c11Opts for slot 0)');
for(const lv of [1,2,5,6]){R.run(`S.level=${lv}`);let n;try{n=R.run("(()=>{const key=C11.key,mel=c11Mel?c11Mel(key):null;return mel?c11Opts(0,key,mel):'no c11Mel'})()")}catch(e){n='ERR '+e.message}console.log(' L'+lv,j(n))}
console.log('--- climb 1 mode shown by level (default C1.mode=dor)');
for(const lv of [1,2,3,4,5]){R.run(`S.level=${lv};C1.mode='dor'`);const r=R.run("(()=>{const L=Math.max(S.level,1),MS=C1M.filter(m=>m.l<=L);if(!MS.find(m=>m.k===C1.mode))C1.mode='dor';const m=C1M.find(x=>x.k===C1.mode);return{offered:MS.map(m=>m.k+':'+m.l),shown:m.k+':'+m.l}})()");console.log(' L'+lv,j(r),r.offered.some(x=>x.startsWith(r.shown.split(':')[0]))?'':'<-- shown mode is not among those offered')}
console.log('--- climb 2 by level (as renderClimb2 computes it)');
for(const lv of [1,2,3,4,5,6,7]){R.run(`S.level=${lv}`);const r=R.run("(()=>{const L=Math.max(S.level,4);return{L,modes:C2M.filter(m=>m.l<=L).map(m=>m.k+':'+m.l),species:C2SP.filter(s=>s.l<=L).map(s=>s.k+':'+s.l),below:L>=5,label:L<5?'Stage 4: first species above the cantus, in three modes':L<6?'Stage 5: three species, four modes, above or below':'Stage 6: all six modes'}})()");
  console.log(' L'+lv,j(r),'above level:',[...r.modes,...r.species].filter(x=>+x.split(':')[1]>lv).join(' ')||'-')}
console.log('--- Gym / Oracle sevenths and colour chords by level');
for(const lv of [1,2,3,4,5,6,7]){R.run(`S.level=${lv};O.sev=true;G.sev=true`);const col=R.run('colourRomans(K,true,S.level)');const dk=R.run('deck().map(x=>x.q)');
  console.log(' L'+lv,'Gym sevenths on:',lv>=3,'| Oracle sevenths switch shown:',lv>=3,'| Oracle deck has 7ths:',dk.some(q=>/7/.test(q)),'| colour chords:',col.join(' ')||'none','| Oracle colour switch shown:',lv>=5)}
