/* Mock-only: the scenes build_ui.py renders. Placeholder melodies and rhythms, written to test the layout; the real items come from the ladder register's generators. */
(()=>{
const GIVEN='#c9b98f',GOLDHI='#f0d48a',RED=()=>getComputedStyle(document.documentElement).getPropertyValue('--red').trim();
/* "e:d! e:r q:m" -> notes. ! given · * wrong pitch · ~ the other spelling · @G read in G · |text under the note */
const B=(str,len,x={})=>Object.assign({len,notes:str?str.split(' ').map(t=>{const [h,un]=t.split('|'),m=h.match(/^([a-z]+):([a-z]+[,']*)([!*~]*)(?:@(\w+))?$/),n={d:m[1],s:m[2]};
  if(m[3].includes('!'))n.col=GIVEN;if(m[3].includes('*')){n.col=RED();n.tcol=RED()}if(m[3].includes('~')){n.near=1;n.tcol=GOLDHI}if(m[4])n.do=m[4];if(un){n.under=un.replace(/_/g,' ');n.ucol=GOLDHI}return n}):[]},x);
const ST={n:23,ok:17,streak:3,best:6,shown:1,skipped:0};
const ask=t=>{const a=document.querySelector('#earCard .el-ask');if(a)a.innerHTML=t};
const oldLad=(range,mode,last,lock)=>{const q={range,mode,key:{k:5,mode:'maj'}},sv=EAR.ans;EAR.ans=last?[last]:[];const h=earMelLadderHTML(q,!!lock,false);EAR.ans=sv;return h};
const noStage=()=>{const e=document.querySelector('#earCard .el-stage');if(e)e.remove();const b=document.querySelector('#earDock [data-eardock=check]');if(b){b.textContent='Next →';b.disabled=false;b.dataset.eardock='next'}};
/* phones: the stave is drawn bare (no inset frame), which gives it 34 px more width and 32 px less height inside the held block */
const draw=o=>{const el=document.getElementById('earMel');el.classList.toggle('bare',innerWidth<761);return MK.score(el,o)};
const ASK='The key chord plays first, then two clicks count you in. The first note is given. Choose a length, then tap each note.';
const S={};

/* 1. palette entry, rung 6, 2/4: seven notes written, the marker inside beat 1 of bar 3 (a single quaver: only a quaver can follow) */
S.pal_r6_24=ph=>{MK.tally(ST);ask(ASK);
 MK.head({drill:'mel',cur:6,done:[1,2,3,4,5],stage:6,what:'Stage 5 · four bars with leaps to any note; an upbeat in some',last:[1,1,0,1,1,1,0,1,null,null]});
 const T=[B('e:d! e:r q:m',8),B('q:s e:m e:r',8),B('e:d',8,{caret:2}),B('',8,{end:'end'})];
 MK.deskLen({label:'Bar 3 of 4 · in beat 1',map:[{t:'1–2',st:['so','so']},{t:'3–4',st:['',''],on:1}],pal:{lens:['e','q','h'],len:'e',off:['q','h'],why:{q:'a crotchet cannot start inside a beat',h:'does not fit this bar'}},ladder:oldLad([-3,7],'maj','d'),aria:'Written so far: do re mi, so mi re, do'});
 draw({key:'F',sig:'2/4',sys:ph?[{tag:'bar 3',sig:true,bars:[T[2],T[3]]}]:[{tag:'bar 1',sig:true,bars:[T[0],T[1]]},{tag:'bar 3',bars:[T[2],T[3]]}]})};

/* 2. palette entry, rung 6, 6/8 with a quaver upbeat: the marker on beat 2 of bar 2 */
S.pal_r6_68=ph=>{MK.tally(ST);ask('The key chord plays first, then one bar of clicks counts you in. The melody starts on the upbeat. The first note is given. Choose a length, then tap each note.');
 MK.head({drill:'mel',cur:6,done:[1,2,3,4,5],stage:6,what:'Stage 5 · four bars with leaps to any note; an upbeat in some',last:[1,1,0,1,1,1,0,1,null,null]});
 const T=[B('e:s,!',2),B('q:d e:m qd:s',12),B('e:l e:s e:f',12,{caret:6}),B('',12),B('',10,{end:'end'})];
 MK.deskLen({label:'Bar 2 of 4 · beat 2',map:[{t:'1–2',st:['so',''],on:1},{t:'3–4',st:['','']}],pal:{lens:['e','q','qd','hd'],len:'q',off:['hd'],why:{hd:'a dotted minim fills a whole bar: only from beat 1'}},ladder:oldLad([-3,7],'maj','f'),aria:'Written so far: low so; do mi so; la so fa'});
 draw({key:'F',sig:'6/8',sys:ph?[{tag:'upbeat · bar 1',sig:true,bars:[T[0],T[1],T[2]]}]:[{tag:'upbeat · bar 1',sig:true,bars:[T[0],T[1],T[2]]},{tag:'bar 3',bars:[T[3],T[4]]}]})};

/* 3. the reveal at rung 6: a rhythm slip in bar 2 (one crotchet for two quavers) and a wrong note in bar 3 (la for so) */
S.res_r6=ph=>{noStage();MK.tally({n:24,ok:17,streak:0,best:6,shown:1,skipped:0});ask(ASK);
 MK.head({drill:'mel',cur:6,done:[1,2,3,4,5],stage:6,what:'Stage 5 · four bars with leaps to any note; an upbeat in some',last:[1,1,0,1,1,1,0,1,0,null]});
 const T=[B('e:d! e:r q:m',8,{names:[[0,'ti-ti'],[4,'ta']]}),B('q:s e:m e:r',8,{names:[[0,'ta'],[4,'ti-ti']]}),B('e:d e:m e:s e:m',8,{names:[[0,'ti-ti'],[4,'ti-ti']]}),B('q:r q:d',8,{end:'end',names:[[0,'ta'],[4,'ta']]})];
 const Y=[B('e:d! e:r q:m',8),B('q:s q:m',8,{rules:[[4,8]]}),B('e:d e:m e:l* e:m',8),B('q:r q:d',8,{end:'end'})];
 const pair=(a,b,sig)=>[{label:`You wrote · bars ${a+1}–${b+1}`,sig,tight:true,bars:[Y[a],Y[b]]},{label:`The melody · bars ${a+1}–${b+1}`,lcol:'#c9a24a',sig,names:true,bars:[T[a],T[b]]}];
 MK.deskRes({label:'Melody · 4 bars of 2/4',map:[{t:'1–2',st:['ok','bad'],on:1,say:'a rhythm slip in bar 2'},{t:'3–4',st:['bad','ok'],say:'a wrong note in bar 3'}],key:MK.markKey(),ladder:oldLad([-3,7],'maj',null,true),
  aria:'You wrote: do re mi; so mi; do mi la mi; re do. The melody: do re mi; so mi re; do mi so mi; re do.',
  result:MK.resultHTML({kind:'bad',parts:[{k:'bad',t:'Rhythm',v:'7 of 8',u:'beats'},{k:'bad',t:'Solfa',v:'10 of 12',u:'notes'}],
   teach:'Bar 2, beat 2 is two quavers, mi re: you wrote one crotchet. In bar 3 the third note is so, the top of do–mi–so: you wrote la.',
   replays:[{v:'frag',o:'2',t:'Hear bar 2: yours, then the answer'},{v:'all',t:'Hear it all with the hand signs'}]})});
 draw({key:'F',sig:'2/4',sys:ph?pair(0,1,true):[...pair(0,1,true),...pair(2,3,false)]})};

/* 4. rung 7, harmonic minor: the melody steps fa to si (an augmented 2nd); the student wrote so */
S.a2_r7=ph=>{noStage();MK.tally({n:12,ok:7,streak:0,best:4,shown:0,skipped:1});ask(ASK.replace('two clicks','three clicks'));
 MK.head({drill:'mel',cur:7,done:[1,2,3,4,5,6],stage:6,what:'Stage 5 · the harmonic and melodic minor: si, and fi',last:[1,0,1,1,0,1,1,0,null,null]});
 const T=[B('q:l,! q:d q:m',12,{names:[[0,'ta'],[4,'ta'],[8,'ta']]}),B('q:f q:si q:l',12,{names:[[0,'ta'],[4,'ta'],[8,'ta']],brk:[0,1,'augmented 2nd']}),B('q:m e:r e:d q:t,',12,{names:[[0,'ta'],[4,'ti-ti'],[8,'ta']]}),B('hd:l,',12,{end:'end',names:[[0,'ta-a-a']]})];
 const Y=[B('q:l,! q:d q:m',12),B('q:f q:s* q:l',12),B('q:m e:r e:d q:t,',12),B('hd:l,',12,{end:'end'})];
 const pair=(a,b,sig)=>[{label:`You wrote · bars ${a+1}–${b+1}`,sig,tight:true,bars:[Y[a],Y[b]]},{label:`The melody · bars ${a+1}–${b+1}`,lcol:'#c9a24a',sig,names:true,bars:[T[a],T[b]]}];
 MK.deskRes({label:'Melody · 4 bars of 3/4',map:[{t:'1–2',st:['ok','bad'],on:1,say:'a wrong note in bar 2'},{t:'3–4',st:['ok','ok']}],key:MK.markKey(),
  ladder:MK.ladHTML({lo:-5,hi:9,chr:['si','fi'],home:'l',homeOct:-1,a2:true,a2on:true,lock:true}),
  aria:'You wrote: low la, do, mi; fa, so, la; mi, re do, low ti; low la. The melody: low la, do, mi; fa, si, la; mi, re do, low ti; low la.',
  result:MK.resultHTML({kind:'bad',parts:[{k:'ok',t:'Rhythm',v:'right'},{k:'bad',t:'Solfa',v:'10 of 11',u:'notes'}],
   teach:'Bar 2: you wrote so; it was raised: si. From fa up to si is three semitones, an augmented 2nd. That is wider than a tone, so the step sounds almost like a leap: the sound of the harmonic minor.',
   pic:MK.gapHTML(),replays:[{v:'frag',o:'2',t:'Hear fa to si, then fa to so'},{v:'all',t:'Hear it all with the hand signs'}]})});
 draw({key:'F',sig:'3/4',sys:ph?pair(0,1,true):[...pair(0,1,true),...pair(2,3,false)]})};

/* 5. rung 9 under "Move do (mutation)", after the pivot: C major to G major, the mutation marked on the G that ends bar 4 */
S.mut_r9=ph=>{MK.tally({n:6,ok:4,streak:2,best:3,shown:0,skipped:0});
 ask(ASK+' Where the key changes, mark the mutation.<span class="el-gloss" data-notm><b>Mutation:</b> renaming the notes so the new key’s home becomes do.</span>');
 MK.head({drill:'mel',cur:9,done:[1,2,3,4,5,6,7,8],stage:6,what:'Stage 6 · eight bars; the key changes once',last:[1,1,0,1,1,0,null,null,null,null]});
 MK.setting({cap:'Solfa',aria:'Solfa when the key changes',attr:'data-eardo',on:'move',opts:[['home','Keep home do','The dominant stays so; its new note is fi'],['move','Move do (mutation)','Renaming the notes so the new key’s home becomes do']]});
 const T=[B('q:d! e:m e:s',8),B('q:l q:s',8),B('e:m e:r e:d e:r',8),B('q:m q:s|s_=_d',8),B('q:d@G e:t,@G e:d@G',8),B('q:r@G',8,{caret:4}),B('',8),B('',8,{end:'end'})];
 const sy=(a,sig)=>({tag:'bar '+(a+1),sig,bars:[T[a],T[a+1]]});
 MK.deskLen({label:'Bar 6 of 8 · beat 2',map:[{t:'1–2',st:['so','so']},{t:'3–4',st:['so','so']},{t:'5–6',st:['so',''],on:1},{t:'7–8',st:['','']}],
  pal:{lens:['e','q','qd','h'],len:'q',off:['qd','h'],why:{qd:'a dotted crotchet starts on beat 1',h:'does not fit this bar'}},mut:MK.mutHTML({set:'bar 4'}),
  ladder:MK.ladHTML({lo:-5,hi:12,chr:['si'],home:'d',shift:7,last:'r'}),aria:'Written so far, bars 1 to 4 in the home key: do mi so, la so, mi re do re, mi so. Mutation on the last note: so equals do. Then do, low ti, do, re.'});
 draw({key:'C',sig:'2/4',sys:ph?[sy(4,true)]:[sy(0,true),sy(2),sy(4),sy(6)]})};

/* 6. rhythm rung 9: 5/4 grouped 3 + 2, a septuplet (3 + 4) written on beat 2 of bar 1; names setting on "Kodály names" */
S.rhy_r9=ph=>{MK.tally({n:8,ok:5,streak:1,best:3,shown:0,skipped:0});ask('Five clicks count you in, grouped 3 + 2. Then four bars play on one note. Write what you hear.');
 const tag=document.querySelector('#earCard .el-tag');if(tag)tag.textContent='Stage 4–6';
 MK.head({drill:'rhy',cur:9,done:[1,2,3,4,5,6,7,8],stage:6,what:'Stage 6 · four bars of 5/4 or 7/8; quintuplets and septuplets',last:[1,0,1,1,0,1,1,null,null,null]});
 MK.setting({cap:'Names',aria:'Rhythm names',attr:'data-earnames',on:'k',opts:[['k','Kodály names'],['kk','Kodály with konnakol tuplets','Triplets are named ta-ki-ta']]});
 MK.rhyDesk({label:'Your rhythm · 6 of 20 beats',sig:[5,4],beats:5,grp:[3,2],bars:[['q','q7a','q','h'],['e2'],[],[]],cur:1,names:'k',off:[],
  fams:[['One beat',['q','e2','qr','s4','es2','s2e','tk','esr','rse']],['Two beats',['h','dq','syn']],['Tuplets',['tri','q5','q7a','q7b']]]})};

/* 7. the seven-cell palette (melody rung 12): six lengths and the crotchet rest */
S.pal7_r12=ph=>{MK.tally({n:3,ok:2,streak:1,best:2,shown:0,skipped:0});ask(ASK.replace('two clicks','three clicks'));
 MK.head({drill:'mel',cur:12,done:[1,2,3,4,5,6,7,8,9,10,11],stage:6,what:'Stage 6 · a phrase from a real piece',last:[1,0,1,null,null,null,null,null,null,null]});
 const T=[B('q:d! q:m q:s',12),B('qd:l e:s q:m',12),B('',12,{caret:0}),B('',12,{end:'end'})];
 MK.deskLen({label:'Bar 3 of 4 · beat 1',map:[{t:'1–2',st:['so','so']},{t:'3–4',st:['',''],on:1}],pal:{lens:['s','e','q','qd','h','hd','qr'],len:'e',off:[]},ladder:oldLad([-3,7],'maj','m'),aria:'Written so far: do mi so; la so mi'});
 draw({key:'F',sig:'3/4',sys:ph?[{tag:'bar 3',sig:true,bars:[T[2],T[3]]}]:[{tag:'bar 1',sig:true,bars:[T[0],T[1]]},{tag:'bar 3',bars:[T[2],T[3]]}]})};

/* 8. the chromatic ladders: rung 7 (raised notes only), rung 8 (te and fi), rung 10 (all twelve) */
S.lad_chr=ph=>{MK.tally(ST);const card=document.getElementById('earCard');card.querySelectorAll(':scope>:not(.el-head)').forEach(e=>e.remove());
 MK.head({drill:'mel',cur:10,done:[1,2,3,4,5,6,7,8,9],stage:6,what:'Stage 6 · chromatic passing and neighbour notes',last:[1,0,1,1,null,null,null,null,null,null]});
 const col=(cap,h)=>`<div class="melentry" style="grid-area:auto"><div class="el-lbl" data-notm style="margin:0 0 10px">${cap}</div>${h}</div>`;
 const L7=MK.ladHTML({lo:-5,hi:9,chr:['si','fi'],home:'l',homeOct:-1,a2:true}),L8=MK.ladHTML({lo:-5,hi:12,chr:['te','fi'],home:'d'}),L10=MK.ladHTML({lo:-5,hi:12,chr:['di','ri','fi','si','li','ra','me','se','le','te'],home:'d',last:'fi'});
 card.insertAdjacentHTML('beforeend',`<div class="meldesk" style="grid-template-columns:${ph?'minmax(0,1fr)':'repeat(3,minmax(0,1fr))'};grid-template-areas:none;gap:14px 22px;margin-top:18px">${ph?col('Rung 10 · all twelve notes',L10):col('Rung 7 · minor with si and fi',L7)+col('Rung 8 · te and fi',L8)+col('Rung 10 · all twelve notes',L10)}</div>`)};
window.SCN=S})();
