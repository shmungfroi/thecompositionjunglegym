// R3: what climbs 1, 2, 9, 11 offer at each level (table 5). Fresh app per level.
const {load}=require('./harness.js');const f=process.argv[2];
for(let lv=1;lv<=7;lv++){const R=load(f,{cjg_level:String(lv)});const o={lv};
  // climb 1
  R.run('renderClimb1()');o.c1open=R.run('C1.mode');o.c1quiz=R.run('C1M.filter(x=>x.l<=Math.max(S.level,1)).map(x=>x.k)');
  const B=R.run('(()=>{const b=lvSplit(C1M);return{nw:b.nw.map(x=>x.k),met:b.met.map(x=>x.k),ahead:b.ahead.map(x=>x.k)}})()');o.c1bands=B;
  // picked mode stays
  R.run("C1.mode='phr';C1.pick=true;renderClimb1()");o.c1picked=R.run('C1.mode');
  // climb 2
  R.run('renderClimb2()');o.c2tier=R.run('c2Tier(Math.max(S.level,3))');o.c2pos=R.run('C2.pos');
  R.run("C2.pos='below';renderClimb2()");o.c2posAfterBelow=R.run('C2.pos');
  o.c2sp=R.run('(()=>{const b=lvSplit(C2SP);return{nw:b.nw.map(x=>x.k),met:b.met.map(x=>x.k),ahead:b.ahead.map(x=>x.k)}})()');
  o.c2modes=R.run('(()=>{const b=lvSplit(C2M);return{nw:b.nw.map(x=>x.k),met:b.met.map(x=>x.k),ahead:b.ahead.map(x=>x.k)}})()');
  o.c2set=R.run("(()=>{C2OWN={k:'own',cf:[0,1,2],fin:'D',n:'own'};const st=setTimeout;try{c2Settable()}catch(e){return 'ERR '+e.message}return C2.set.jobs.map(j=>j.join(''))})()");
  // climb 9
  R.run('renderClimb9()');o.c9open=R.run('C9.vt');
  R.run("C9.key={k:9,mode:'min'};C9.ex='min';renderClimb9()");
  o.c9minSyms=R.run("(()=>{const{L}=c9Cur();return L.map(c=>c9Sym(c,C9.vt))})()");
  o.c9rootlessSyms=R.run("(()=>{const{L}=c9Cur();return L.map(c=>c9Sym(c,'rootless'))})()");
  o.c9V=R.run("(()=>{const L=c9List('iiø7 V7 i7 i7',C9.key);const v=c9Voice(L,'rootless','A')[1];return (v.up||[]).map(n=>n.name)})()");
  o.c9Vshell=R.run("(()=>{const L=c9List('iiø7 V7 i7 i7',C9.key);const v=c9Voice(L,'shell','A')[1];return [v.bass&&v.bass.name].concat((v.up||[]).map(n=>n.name))})()");
  R.run("C9.vt='rootless';C9.vtPick=true;renderClimb9()");o.c9picked=R.run('C9.vt');
  o.c9exQuiz=R.run('C9EX.filter(x=>x.l<=Math.max(S.level,4)).map(x=>x.k)');
  // climb 11
  o.c11sets=R.run('C11VOCSET.filter(v=>v.l<=lvAt(C11VOCSET)).map(v=>v.k)');
  o.c11opts=R.run("(()=>{const key={k:0,mode:'maj'},mel=c11Mel(key);return mel.map((m,i)=>c11Opts(i,key,mel))})()");
  o.c11ver=R.run('C11V.filter(v=>v.l<=Math.max(S.level,2)).map(v=>v.k)');
  o.c11tools=R.run('(()=>{const b=lvSplit(C11TOOLS);return{nw:b.nw.map(x=>x.k),met:b.met.map(x=>x.k),ahead:b.ahead.map(x=>x.k)}})()');
  console.log(JSON.stringify(o))}
