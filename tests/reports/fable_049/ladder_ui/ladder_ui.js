/* Ear Lab 0.49, ladder UI part 2 (Fable). Mock-only helpers: they run inside the live app page, after ../mock.js.
   Nothing here is production code, but the HTML these functions write IS the reference markup for ladder_ui.css,
   and the drawing rules (beaming, the gold marker, the marks at the reveal, the tuplet tiles) are the ones SPEC.md describes. */
/* three Bravura outlines the app does not carry yet, in ELGLY's own format (VexFlow's Bravura outline, y as stored): add them to ELGLY */
Object.assign(ELGLY,{"flag16thUp":"M392 -1146C397 -1139 402 -1057 402 -988L402 -956C402 -896 386 -837 360 -783C360 -779 359 -776 359 -770C359 -768 359 -765 360 -760C364 -752 396 -665 396 -577C396 -559 395 -543 392 -526C377 -428 340 -387 236 -275C158 -192 78 -168 53 -16C50 0 33 3 24 3C16 3 0 -1 0 -12L0 -570L7 -570C96 -573 199 -576 298 -778C331 -847 344 -917 344 -992C344 -1034 340 -1077 333 -1120C331 -1126 331 -1129 331 -1133C331 -1152 343 -1171 363 -1171C373 -1171 383 -1165 392 -1146ZM301 -661C278 -625 253 -596 223 -562C156 -484 89 -449 59 -331C58 -330 58 -328 58 -327C58 -321 66 -312 78 -312L89 -312C177 -312 255 -393 302 -464C328 -501 341 -546 341 -592C341 -602 341 -611 340 -621C337 -632 337 -647 330 -658C328 -662 318 -667 311 -667C307 -667 304 -665 301 -661Z","rest8th":"M193 154C193 207 150 251 96 251C43 251 0 207 0 154C0 124 17 98 39 81C62 65 89 56 117 56C137 56 157 60 173 66C193 72 206 78 225 88C228 89 230 89 232 89C238 89 239 84 239 76C239 72 239 66 238 60C233 39 130 -248 104 -343C104 -360 137 -361 145 -361C161 -361 181 -359 196 -347C200 -344 341 161 341 161C347 187 354 210 356 217C356 232 341 239 338 240C336 240 331 240 323 235C312 226 240 140 193 140Z","noteheadWhole":"M311 180C120 180 0 101 0 3C0 -94 82 -180 297 -180C533 -180 608 -98 608 3C608 105 445 180 311 180ZM160 91C176 141 229 148 274 148C373 148 452 42 452 -45C452 -89 433 -130 386 -141C372 -145 356 -147 341 -147C289 -147 236 -112 206 -72C177 -39 156 10 156 56C156 68 157 79 160 91Z"});
(()=>{
const IV='#ece2c8',MUTED='#9c927c',GOLD='#c9a24a',GOLDHI='#f0d48a',GIVEN='#c9b98f',NS='http://www.w3.org/2000/svg';
const tok=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();

/* ================= the duration palette ================= */
/* t = length in semiquavers. Rests are keys (one tap writes the rest); everything else is a sticky choice. */
const LEN={s:{w:'semiquaver',t:1},e:{w:'quaver',t:2},ed:{w:'dotted quaver',t:3},q:{w:'crotchet',t:4},qd:{w:'dotted crotchet',t:6},h:{w:'minim',t:8},hd:{w:'dotted minim',t:12},w:{w:'semibreve',t:16},
 qr:{w:'crotchet rest',t:4,rest:1},er:{w:'quaver rest',t:2,rest:1}};
function lenGlyph(k){const c='currentColor',base=30,top=6;let g='';
 if(k==='qr')g=elGlyph('restQuarter',12.7,20,c);
 else if(k==='er')g=elGlyph('rest8th',12.8,21.5,c);
 else if(k==='w')g=elGlyph('noteheadWhole',9.8,22,c);
 else{const dot=/d$/.test(k),flag=k==='e'||k==='ed'||k==='s',x=(34-ELHW-(flag?6:0)-(dot&&!flag?6:0))/2,sx=x+ELHW-.65;
  g=elGlyph(k==='h'||k==='hd'?'noteheadHalf':'noteheadBlack',x,base,c)+`<line x1="${sx.toFixed(2)}" y1="${base-1.5}" x2="${sx.toFixed(2)}" y2="${top}" stroke="${c}" stroke-width="1.3"/>`;
  if(flag)g+=elGlyph(k==='s'?'flag16thUp':'flag8thUp',sx-.65,top,c);
  if(dot)g+=elGlyph('augmentationDot',x+ELHW+3.2,base,c)}
 return`<svg viewBox="0 0 34 40" aria-hidden="true">${g}</svg>`}
/* o.lens: the rung's lengths for this metre, shortest first, rests last. o.len: the chosen one. o.off: lengths that cannot go at the marker. */
function palHTML(o){const off=o.off||[],n=o.lens.length;
 const cell=k=>{const L=LEN[k],dis=off.includes(k),why=dis?(o.why&&o.why[k]||'does not fit here'):'';
  return L.rest?`<button class="el-len rest" data-rest="${k}" aria-label="${L.w}${dis?', '+why:''}" title="${cap1(L.w)}${dis?': '+why:''}" aria-disabled="${dis}">${lenGlyph(k)}</button>`
   :`<button class="el-len" role="radio" data-len="${k}" aria-checked="${k===o.len}" aria-label="${L.w}${dis?', '+why:''}" title="${cap1(L.w)}${dis?': '+why:''}" aria-disabled="${dis}" tabindex="${k===o.len?0:-1}">${lenGlyph(k)}</button>`};
 return`<div class="el-palwrap"><div class="el-lbl" data-notm>Length</div><div class="el-pal${n>7?' two':''}" role="radiogroup" aria-label="Note length">${o.lens.map(cell).join('')}</div>${o.mut||''}</div>`}

/* ================= the solfa ladder, with half rungs ================= */
const DIA={0:'d',2:'r',4:'m',5:'f',7:'s',9:'l',11:'t'},SH={1:['di','do'],3:['ri','re'],6:['fi','fa'],8:['si','so'],10:['li','la']},FL={1:['ra','re'],3:['me','mi'],6:['se','so'],8:['le','la'],10:['te','ti']};
const SOLW={d:'do',r:'re',m:'mi',f:'fa',s:'so',l:'la',t:'ti'};
const mk=o=>o<0?','.repeat(-o):"'".repeat(o),md=(a,b)=>((a%b)+b)%b;
function solAt(p){const pc=md(p,12),o=Math.floor(p/12);return DIA[pc]!==undefined?DIA[pc]+mk(o):SH[pc][0]+mk(o)}     // a pitch's name, raised spelling for the chromatic ones
/* o: {lo,hi} in semitones from the home do · chr: chromatic names to show ('si','fi','te',...) · home: 'd'|'l'|'r'|'s' · shift: new do, in semitones above the old (after a mutation)
      last: the row tapped last · a2: draw the fa-si gauge · a2on: gold (the melody takes that step) · lock: the reveal · letters: {name:letter} */
function ladHTML(o){const chr=o.chr||[],sh=o.shift||0;let h='';
 for(let p=o.hi;p>=o.lo;p--){const q=p-sh,pc=md(q,12),oc=Math.floor(q/12),a2=o.a2&&p>=5&&p<=8?` a2${p===8?' a2top':p===5?' a2bot':''}`:'';
  if(DIA[pc]!==undefined){const s=DIA[pc],tx=s+mk(oc),isH=s===o.home,was=sh?solAt(p):'';
   h+=`<button class="earstep${isH?' home':''}${tx===o.last?' last':''}${a2}" data-earsol="${tx}" ${o.lock?'disabled':''} aria-label="${SOLW[s]}${oc<0?' low':oc>0?' high':''}${isH?', home note':''}${was?', was '+was:''}">${ehsign(s)}<b>${tx}</b>${o.letters?`<small>${o.letters[tx]||''}</small>`:''}${was?`<span class="was">was <b>${was}</b></span>`:''}${isH&&oc===(o.homeOct||0)?'<span class="hm">home</span>':''}${a2&&p===7?'<span class="a2lab" aria-hidden="true"><b>3 semitones</b>fa to si</span>':''}</button>`}
  else{const f=FL[pc],s=SH[pc],hasF=chr.includes(f[0]),hasS=chr.includes(s[0]);if(!hasF&&!hasS)continue;
   const btn=(nm,of,cls,word)=>{const tx=nm+mk(oc);return`<button class="earstep chr ${cls}${tx===o.last?' last':''}" data-earsol="${tx}" ${o.lock?'disabled':''} aria-label="${nm}${oc<0?' low':oc>0?' high':''}, ${word} ${of}"><b>${tx}</b><span class="of">${word} ${of}</span></button>`};
   h+=`<div class="earhalf${a2}">${hasF?btn(f[0],f[1],'fl','lowered'):''}${hasS?btn(s[0],s[1],'sh','raised'):''}</div>`}}
 return`<div class="earlad chr${o.lock?' listen':''}${o.a2on?' a2on':''}" role="group" aria-label="Solfa ladder, high to low">${h}</div>`}

/* ================= the stave: bars with rhythm, drawn in proportion to time ================= */
const KL='CDEFGAB',NAT=[0,2,4,5,7,9,11],KSIG={C:{},G:{F:1},D:{F:1,C:1},F:{B:-1},Bb:{B:-1,E:-1}};
const SOLT={d:[0,0],r:[1,2],m:[2,4],f:[3,5],s:[4,7],l:[5,9],t:[6,11],di:[0,1],ri:[1,3],fi:[3,6],si:[4,8],li:[5,10],ra:[1,1],me:[2,3],se:[4,6],le:[5,8],te:[6,10]};
function pit(sol,key){const m=sol.match(/^([a-z]+)([,']*)$/),T=SOLT[m[1]],o=(m[2].match(/'/g)||[]).length-(m[2].match(/,/g)||[]).length,kL=KL.indexOf(key[0]),kA=key.includes('b')?-1:key.includes('#')?1:0;
 const doM=60+md(NAT[kL]+kA,12),li=kL+T[0]+7*o,L=KL[md(li,7)],oct=4+Math.floor(li/7),acc=doM+T[1]+12*o-(12*(oct+1)+NAT[md(li,7)]);
 return{L,oct,acc,key:L.toLowerCase()+(acc>0?'#'.repeat(acc):'b'.repeat(-acc))+'/'+oct}}
const DUR={s:['16',0,1],e:['8',0,2],ed:['8',1,3],q:['q',0,4],qd:['q',1,6],h:['h',0,8],hd:['h',1,12],w:['w',0,16]};
/* o: {key:'F', sig:'2/4', sys:[{label|tag, sig:bool, names:bool, bars:[{len, notes:[{d,s,do,rest,col,tcol,under,ucol}], end:'end'|undefined, caret:tick, rules:[[t0,t1]], names:[[tick,'ti-ti']], brk:[i,j,'text']}]}]}
   notes: d = a LEN key, s = solfa as written, do = the key that s is read in (after a mutation), col = head colour, tcol = syllable colour, under = text in place of the syllable */
function score(el,o){el.innerHTML='';const VF=Vex.Flow,k=ENG.space('exercise')/10,U=ENG.avail(el)/k,X0=2/k,[bn,bv]=o.sig.split('/').map(Number),comp=bv===8&&bn%3===0,RED=tok('--red')||'#d15e5d';
 const probe=(sig)=>{const p=new VF.Stave(0,0,300);p.addClef('treble').addKeySignature(o.key);if(sig)p.addTimeSignature(o.sig);return p.getNoteStartX()+6};
 const geo=o.sys.map(s=>{const lbl=20/k,brk=s.bars.some(b=>b.brk)?18/k:0,above=lbl+brk+14,below=22,sol=17/k,nm=s.names?15/k:0,rl=s.bars.some(b=>b.rules&&b.rules.length)?8/k:0;return{above,below,sol,nm,rl,brk,h:above+40+below+sol+nm+rl+4/k}});
 let H=0;const tops=o.sys.map((s,i)=>{const t=H;H+=geo[i].h+(i<o.sys.length-1?(s.tight?2/k:14/k):0);return t});
 const S=ENG.open(el,'exercise',U,H),svg=S.svg;svg.setAttribute('aria-hidden','true');const post=[];
 const add=(n,a,cls)=>{const e=document.createElementNS(NS,n);for(const q in a)e.setAttribute(q,a[q]);if(cls)e.setAttribute('class',cls);post.push(e);return e};
 o.sys.forEach((s,si)=>{const G=geo[si],top=tops[si],sy=top+G.above-40,lead=probe(s.sig),tot=s.bars.reduce((a,b)=>a+Math.max(b.len,5),0),room=U-X0-2/k-lead;let x=X0;
  if(s.label)post.push(()=>ENG.txt(S,X0,top+11/k,s.label,'sec',{fill:s.lcol||MUTED,weight:400}));else if(s.tag)post.push(()=>ENG.txt(S,X0+1/k,top+11/k,s.tag,'bar',{fill:MUTED}));
  s.bars.forEach((b,j)=>{const first=j===0,w=(first?lead:0)+room*Math.max(b.len,5)/tot,stv=new VF.Stave(x,sy,w);
   if(first){stv.addClef('treble').addKeySignature(o.key);if(s.sig)stv.addTimeSignature(o.sig)}
   const xs=x+(first?lead:12),xe=x+w-(b.len<5?6:9),span=xe-xs,X=t=>xs+span*t/b.len;stv.setNoteStartX(xs);
   stv.setBegBarType(VF.Barline.type.NONE).setEndBarType(b.end==='end'?VF.Barline.type.END:VF.Barline.type.SINGLE);stv.setContext(S.ctx).draw();
   const acc=Object.assign({},KSIG[o.key]),sns=[],at=[];let t=0;
   b.notes.forEach(n=>{const [vd,dots,tk]=DUR[LEN[n.d].rest?(n.d==='qr'?'q':'e'):n.d];let sn;
    if(n.rest||LEN[n.d].rest)sn=new VF.StaveNote({keys:['b/4'],duration:vd+'r',dots});
    else{const p=pit(n.s,n.do||o.key),id=p.L+p.oct;sn=new VF.StaveNote({keys:[p.key],duration:vd,dots,auto_stem:true});
     if(p.acc!==(acc[id]!==undefined?acc[id]:(acc[p.L]||0))){sn.addModifier(new VF.Accidental({1:'#','-1':'b',0:'n',2:'##','-2':'bb'}[p.acc]),0)}acc[id]=p.acc}
    if(dots)VF.Dot.buildAndAttach([sn],{all:true});const col=n.col||IV;sn.setStyle({fillStyle:col,strokeStyle:col});sns.push(sn);at.push(t);t+=tk});
   const real=sns.length;let rest=b.len-t;while(rest>0){const g=rest>=4?4:rest>=2?2:1;sns.push(new VF.GhostNote({duration:g===4?'q':g===2?'8':'16'}));rest-=g}
   if(sns.length){const v=new VF.Voice({num_beats:bn,beat_value:bv}).setMode(VF.Voice.Mode.SOFT);v.addTickables(sns);
    const beams=VF.Beam.generateBeams(sns.slice(0,real),{groups:[comp?new VF.Fraction(3,8):new VF.Fraction(1,4)]});
    new VF.Formatter().joinVoices([v]).format([v],span);
    sns.slice(0,real).forEach((sn,i)=>{sn.setStave(stv);sn.getTickContext().setX(span*at[i]/b.len);const off=sn.getNoteHeadBeginX()-X(at[i]);if(Math.abs(off)>.05)sn.getTickContext().setX(span*at[i]/b.len-off)});
    v.draw(S.ctx,stv);beams.forEach(bm=>{const cs=[...new Set(sns.slice(0,real).filter(n=>n.getBeam()===bm).map(n=>n.getStyle()?n.getStyle().fillStyle:IV))],col=cs.length===1?cs[0]:IV;bm.setStyle({fillStyle:col,strokeStyle:col});bm.setContext(S.ctx).draw()});
    const base=top+G.above+40+G.below+12/k,hw=(sns[0].getNoteHeadEndX?sns[0].getNoteHeadEndX()-sns[0].getNoteHeadBeginX():12)/2;
    sns.slice(0,real).forEach((sn,i)=>{const n=b.notes[i];if(n.rest||LEN[n.d].rest)return;const cx=X(at[i])+hw,tx=n.under||n.s;
     post.push(()=>{const e=ENG.txt(S,cx,base,tx,'sol',{anchor:'middle',fill:n.ucol||n.tcol||n.col||IV,cls:'melsol'});if(n.near){const bb=e.getBBox(),l=document.createElementNS(NS,'line'),a={x1:bb.x,x2:bb.x+bb.width,y1:base+3.5/k,y2:base+3.5/k,stroke:GOLD,'stroke-width':1.6/k,'stroke-dasharray':`${1.6/k} ${2.6/k}`};for(const q in a)l.setAttribute(q,a[q]);svg.appendChild(l)}})});
    if(s.names)(b.names||[]).forEach(([tk,nm])=>post.push(()=>ENG.txt(S,X(tk)+1,base+G.nm,nm,'lab',{fill:MUTED,cls:'melname'})));
    (b.rules||[]).forEach(([t0,t1])=>{const y=base+G.nm+(s.names?0:0)+7/k;post.push(add('rect',{x:X(t0)-1,y,width:X(t1)-X(t0)-7,height:2/k,fill:RED},'melbeat'))});
    if(b.brk){const [i0,i1,tx]=b.brk,xa=X(at[i0])+hw,xb=X(at[i1])+hw,y=top+20/k+G.brk-3/k;post.push(add('path',{d:`M${xa} ${y+5/k}V${y}H${xb}V${y+5/k}`,fill:'none',stroke:GOLD,'stroke-width':1.3/k}));post.push(()=>ENG.txt(S,(xa+xb)/2,y-5/k,tx,'lab',{anchor:'middle',fill:GOLDHI}))}}
   if(b.caret!==undefined){const cx=X(b.caret)-(b.caret?5:3),y1=top+G.above-9,y2=top+G.above+49;post.push(add('rect',{x:cx-1/k,y:y1,width:2/k,height:y2-y1,rx:1/k,fill:GOLD},'melcaret'));post.push(add('path',{d:`M${cx-4.5/k} ${y1-6/k}h${9/k}l${-4.5/k} ${5.5/k}z`,fill:GOLD},'melcaret'))}
   x+=w})});
 ENG.finish(S);post.forEach(p=>typeof p==='function'?p():svg.appendChild(p));return S}

/* ================= desks ================= */
const UNDO='<svg viewBox="0 0 18 18" aria-hidden="true"><path d="M6.2 3.2L2.6 6.8l3.6 3.6M3 6.8h7.2a4.4 4.4 0 010 8.8H7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
function sysmap(o){if(!o.map)return'';return`<div class="el-sysmap" role="group" aria-label="Bars">${o.map.map(m=>`<button aria-pressed="${!!m.on}" aria-label="Bars ${m.t.replace('–',' to ')}${m.say?', '+m.say:''}">${m.t}<i>${m.st.map(c=>`<span class="${c}"></span>`).join('')}</i></button>`).join('')}</div>`}
/* entry: o = {label, map, pal:{lens,len,off}, ladder, full, mut, aria} */
function deskLen(o){const d=document.querySelector('.meldesk');d.className='meldesk bylen';
 d.innerHTML=`<div class="melhold"><div class="melscore${o.map?'':' one'}"><div class="lbl" data-notm role="status">${o.label}</div><div class="el-sysrow">${sysmap(o)}<button class="el-undo1" data-hist="ear:u" aria-label="Undo" title="Undo">${UNDO}</button></div><div class="melfr" id="earMel" role="img" aria-label="${o.aria||''}"></div></div>
   ${palHTML(Object.assign({mut:o.mut},o.pal))}</div>
  <div class="melentry">${o.ladder}</div>
  <div class="melacts">${earEditBtns(!!o.full)}<label class="note"><input type="checkbox" id="earLet"> show letter names</label></div>`}
/* the reveal: o = {label, map, ladder, result, key, aria} */
function deskRes(o){const d=document.querySelector('.meldesk');d.className='meldesk bylen done';
 d.innerHTML=`<div class="melres">${o.result}</div>
  <div class="melhold"><div class="melscore"><div class="lbl" data-notm>${o.label}</div>${o.map?`<div class="el-sysrow">${sysmap(o)}</div>`:''}<div class="melfr" id="earMel" role="img" aria-label="${o.aria||''}"></div>${o.key||''}</div></div>
  <div class="melentry">${o.ladder}</div>
  <div class="melacts"><label class="note"><input type="checkbox" id="earLet"> show letter names</label></div>`}
/* the result panel for rungs 4 and up: the headline reports rhythm and solfa apart. parts: [{k:'ok'|'bad'|'near', t:'Rhythm', v:'right'|'7 of 8', u:'beats'}] */
function resultHTML(o){const head=o.parts.map(p=>`<span class="pt ${p.k}">${ELICON[p.k==='ok'?'tick':p.k==='near'?'near':'cross']}<span>${p.t} ${p.v}${p.u?` <small>${p.u}</small>`:''}</span></span>`).join('');
 return earResultHTML({},{kind:o.kind,head,teach:o.teach,pic:o.pic||'',replays:o.replays}).replace('class="el-answer"','class="el-answer two"')}
const markKey=(o={})=>`<p class="el-markkey" data-notm><span><i class="p"></i>a wrong note</span><span><i class="r"></i>a beat with the wrong rhythm</span>${o.near?'<span><i class="n"></i>the other spelling</span>':''}</p>`;
/* the augmented 2nd beside a tone, one cell per semitone */
const gapHTML=()=>`<div class="el-gap" data-notm role="img" aria-label="fa to so is 2 semitones, a tone. fa to si is 3 semitones, an augmented 2nd."><span class="nm">fa to so</span><span class="gbar"><i></i><i></i></span><span class="say">2 semitones · a tone</span><span class="nm on">fa to si</span><span class="gbar on"><i></i><i></i><i></i></span><span class="say on">3 semitones · an augmented 2nd</span></div>`;
/* rung 9: the mutation button (shown only under Move do). o.set: {bar, at} once pressed */
const MUTICO='<svg viewBox="0 0 22 22" aria-hidden="true"><circle cx="8" cy="11" r="5.2" fill="none" stroke="currentColor" stroke-width="1.4" stroke-dasharray="2.2 2.2"/><circle cx="14" cy="11" r="5.2" fill="none" stroke="currentColor" stroke-width="1.4"/></svg>';
const mutHTML=o=>o&&o.set?`<button class="el-mut" data-earmut aria-pressed="true" aria-disabled="true" title="Undo takes the mutation back">${MUTICO}<span>Mutation set: so = do</span><small>${o.set}</small></button>`
 :`<button class="el-mut" data-earmut aria-pressed="false" ${o&&o.off?'disabled':''}>${MUTICO}<span>Mutation here: so = do</span></button>`;
/* settings: one more group in the listening options row. o = {cap, aria, opts:[[value,label]], on, attr} */
function setting(o){const v=document.querySelector('#earCard .el-vars');if(!v)return;
 v.insertAdjacentHTML('beforeend',`<span class="grp set"><span class="cap">${o.cap}</span><div class="el-seg" role="group" aria-label="${o.aria}">${o.opts.map(([k,t,tip])=>`<button ${o.attr}="${k}" aria-pressed="${k===o.on}"${tip?` title="${tip}"`:''}>${t}</button>`).join('')}</div></span>`)}

/* ================= rhythm: cells by the beat, tuplets, 5/4 ================= */
/* ev: [start, length, rest?] in semiquavers inside the cell · b: beats · tup: the figure · grp: how a septuplet groups · wide: how much wider its beat is drawn */
const seq=(n,d)=>Array.from({length:n},(_,i)=>[i*d,d]);
const RC={q:{n:'ta',w:'crotchet',b:1,ev:[[0,4]]},e2:{n:'ti-ti',w:'2 quavers',b:1,ev:[[0,2],[2,2]]},h:{n:'ta-a',w:'minim',b:2,ev:[[0,8]]},qr:{n:'sa',w:'crotchet rest',b:1,ev:[[0,4,1]]},
 s4:{n:'tika-tika',w:'4 semiquavers',b:1,ev:seq(4,1)},es2:{n:'ti-tika',w:'quaver, 2 semiquavers',b:1,ev:[[0,2],[2,1],[3,1]]},s2e:{n:'tika-ti',w:'2 semiquavers, quaver',b:1,ev:[[0,1],[1,1],[2,2]]},
 tk:{n:'tim-ka',w:'dotted quaver, semiquaver',b:1,ev:[[0,3],[3,1]]},esr:{n:'ti sa',w:'quaver, quaver rest',b:1,ev:[[0,2],[2,2,1]]},rse:{n:'sa ti',w:'quaver rest, quaver',b:1,ev:[[0,2,1],[2,2]]},
 dq:{n:'tam-ti',w:'dotted crotchet, quaver',b:2,ev:[[0,6],[6,2]]},syn:{n:'syn-co-pa',w:'quaver, crotchet, quaver',b:2,ev:[[0,2],[2,4],[6,2]]},
 tri:{n:'tri-o-la',kk:'ta-ki-ta',w:'triplet: 3 quavers in a beat',b:1,ev:seq(3,4/3),tup:3},
 q5:{n:'ta-da-ki-na-dom',w:'quintuplet: 5 in a beat',b:1,ev:seq(5,.8),tup:5,wide:1.3,min:62},
 q7a:{n:'ta-ki-ta\nta-ka-di-mi',w:'septuplet: 7 in a beat, grouped 3 + 4',b:1,ev:seq(7,4/7),tup:7,grp:[3,4],wide:1.75,min:84},
 q7b:{n:'ta-ka-di-mi\nta-ki-ta',w:'septuplet: 7 in a beat, grouped 4 + 3',b:1,ev:seq(7,4/7),tup:7,grp:[4,3],wide:1.75,min:84}};
/* one cell's marks. x: left edge, bw: px per beat as drawn here, top: stem top, base: notehead centre */
function cellMarks(key,x,bw,top,base,ink=IV){const C=RC[key],st=[];let o='';
 C.ev.forEach(([s,d,r])=>{const nx=x+s/4*bw+5;
  if(r){o+=elGlyph(d>=4?'restQuarter':'rest8th',nx+(d>=4?0:1),base+(d>=4?0:1.5),ink);st.push(null);return}
  const sx=nx+ELHW-.65;o+=elGlyph(d>=8?'noteheadHalf':'noteheadBlack',nx,base,ink)+`<line x1="${sx.toFixed(1)}" y1="${base-1.5}" x2="${sx.toFixed(1)}" y2="${top}" stroke="${ink}" stroke-width="1.3"/>`;
  if(d===6||d===3)o+=elGlyph('augmentationDot',nx+ELHW+3,base-4.3,ink);st.push([sx,d])});
 /* beams: runs of neighbouring notes shorter than a crotchet; a second beam where both neighbours are semiquavers or shorter, broken between a septuplet's groups */
 const runs=[];let cur=null;st.forEach((q,i)=>{if(q&&q[1]<4){if(!cur)runs.push(cur=[]);cur.push(i)}else cur=null});
 const bar=(a,b,y)=>`<rect x="${(a-.65).toFixed(1)}" y="${y}" width="${(b-a+1.3).toFixed(1)}" height="4" fill="${ink}"/>`;
 runs.forEach(R=>{if(R.length===1){const [sx,d]=st[R[0]];o+=elGlyph(d<=1?'flag16thUp':'flag8thUp',sx-.65,top,ink);return}
  o+=bar(st[R[0]][0],st[R[R.length-1]][0],top);const short=i=>st[i][1]<=1.01,cut=C.grp?C.grp[0]:-1;
  for(let j=0;j<R.length-1;j++){const a=R[j],b=R[j+1];if(short(a)&&short(b)&&j+1!==cut)o+=bar(st[a][0],st[b][0],top+6.5)}
  R.forEach((i,j)=>{if(!short(i))return;const L=j>0&&short(R[j-1])&&j!==cut,Rt=j<R.length-1&&short(R[j+1])&&j+1!==cut;if(!L&&!Rt){const sx=st[i][0];o+=j>0?bar(sx-5.5,sx,top+6.5):bar(sx,sx+5.5,top+6.5)}})});
 if(C.tup){const a=st[0][0],b=st[st.length-1][0];o+=`<text x="${((a+b)/2).toFixed(1)}" y="${top-5.5}" text-anchor="middle" font-family="'EB Garamond',Georgia,serif" font-style="italic" font-weight="500" font-size="14" fill="${ink}">${C.tup}</text>`}
 return o}
const beatW=(key,u)=>{const C=RC[key];return C&&C.wide?Math.max(4*u*C.wide,C.min+6):4*u};
/* one bar of the one-line rhythm stave. o: {cells, beats, grp:[3,2], u, sig:[5,4]|null, no, cursor, final, holes} */
function rhyBar(o){const u=o.u,X0=o.sig?34:10,top=28,base=62,sy=78,Ht=90,ws=[];let bi=0;
 o.cells.forEach(c=>{const C=RC[c];for(let j=0;j<C.b;j++)ws[bi++]=j===0?beatW(c,u):4*u});while(bi<o.beats)ws[bi++]=4*u;
 const xs=[X0];ws.forEach(w=>xs.push(xs[xs.length-1]+w));const Wd=xs[o.beats]+14;
 let s=`<svg class="el-rsvg" viewBox="0 0 ${Wd} ${Ht}" width="${Wd}" height="${Ht}" role="img" aria-label="${o.label||'Bar '+o.no}"><line x1="4" y1="${base}" x2="${Wd-6}" y2="${base}" stroke="#c9b98f" stroke-opacity=".55" stroke-width="1"/>`;
 if(o.sig)s+=elGlyph('timeSig'+o.sig[0],6,base-8.6,IV)+elGlyph('timeSig'+o.sig[1],6,base+8.6,IV);
 for(let b=0;b<o.beats;b++){const cx=xs[b]+5+ELHW/2;s+=`<g class="el-rn"><text x="${cx.toFixed(1)}" y="13" text-anchor="middle">${b+1}</text></g>`}
 /* the grouping of an irregular bar: a dashed line where the second group starts */
 let g=0;(o.grp||[]).slice(0,-1).forEach(n=>{g+=n;const gx=xs[g]-3;s+=`<line x1="${gx}" y1="4" x2="${gx}" y2="${base+17}" stroke="${MUTED}" stroke-width="1" stroke-dasharray="2 3"/>`});
 if(o.final){const ex=Wd-6;s+=`<line x1="${ex-6}" y1="${base-17}" x2="${ex-6}" y2="${base+17}" stroke="${IV}" stroke-width="1"/><rect x="${ex-3}" y="${base-17}" width="3.5" height="34" fill="${IV}"/>`}
 else s+=`<line x1="${Wd-7}" y1="${base-17}" x2="${Wd-7}" y2="${base+17}" stroke="${IV}" stroke-width="1"/>`;
 let b=0;o.cells.forEach(c=>{const C=RC[c],bw=ws[b];s+=cellMarks(c,xs[b],bw,top,base);
  C.ev.forEach(([st,d,r])=>{const xx=xs[b]+st/4*bw+2.5,ww=d/4*bw-5;s+=r?`<line x1="${(xx+1).toFixed(1)}" y1="${sy+3}" x2="${(xx+ww-1).toFixed(1)}" y2="${sy+3}" stroke="${MUTED}" stroke-width="1.5" stroke-dasharray="2 5" stroke-linecap="round"/>`:`<rect x="${xx.toFixed(1)}" y="${sy}" width="${Math.max(2,ww).toFixed(1)}" height="6" rx="3" fill="${IV}" fill-opacity=".8"/>`});b+=C.b});
 if(o.cursor&&b<o.beats){const x=xs[b];s+=`<line x1="${x+1}" y1="${top-4}" x2="${x+1}" y2="${sy+8}" stroke="${GOLD}" stroke-width="1.5" stroke-linecap="round"/><path d="M${x-3.5} ${top-9}h9l-4.5 5.5z" fill="${GOLD}"/>`}
 for(let h=b;h<o.beats;h++)s+=`<rect x="${xs[h]+3}" y="${sy+.5}" width="${ws[h]-6}" height="5" rx="2.5" fill="none" stroke="#7a6e55" stroke-width="1" stroke-dasharray="2 3"/>`;
 return s+'</svg>'}
/* one entry tile. names: 'k' (Kodaly names) or 'kk' (Kodaly with konnakol tuplets); 5- and 7-tuplets carry their konnakol names in both */
function tile(key,o={}){const C=RC[key],nm=o.names==='kk'&&C.kk?C.kk:C.n,u=14,two=nm.includes('\n'),bw=C.b*56,w=Math.max(bw,C.min?C.min+12:0,C.tup>3?(two?96:112):0),inner=C.min?C.min+2:C.b*56,x0=(w-inner)/2+(C.ev.length===1?inner/2-11:C.b===1&&!C.min?-2.5+ (C.ev.length===2&&!C.tup?0:0):0);
 return`<button class="el-tile${C.tup?' tup':''}" style="width:${w}px" data-earcell="${key}" aria-label="${C.w}, ${nm.replace('\n',' ')}" title="${cap1(C.w)}" ${o.off?`disabled`:''}><svg viewBox="1 0 ${w-2} 56" width="${w-2}" height="56" aria-hidden="true"><line x1="0" y1="44" x2="${w}" y2="44" stroke="#c9b98f" stroke-opacity=".3"/>${cellMarks(key,x0,C.min?C.min:56,C.tup?16:12,44)}</svg><small>${nm}</small></button>`}
function rhyDesk(o){const card=document.getElementById('earCard'),foot=card.querySelector('.el-foot');
 card.querySelectorAll('.el-lbl,.el-rhy,.el-tiles,.el-edit').forEach(e=>{if(!e.closest('.el-stage,.el-result'))e.remove()});
 const bars=u=>o.bars.map((c,i)=>rhyBar({cells:c,beats:o.beats,grp:o.grp,u,sig:i===0?o.sig:null,no:i+1,cursor:i===o.cur,final:i===o.bars.length-1})).join('');
 const fam=(cap,keys)=>`<div class="el-tfam" role="group" aria-label="${cap}"><span data-notm>${cap}</span><div class="el-tiles named">${keys.map(k=>tile(k,{names:o.names,off:(o.off||[]).includes(k)})).join('')}</div></div>`;
 foot.insertAdjacentHTML('beforebegin',`<div class="el-lbl" data-notm>${o.label}</div><div class="el-rhy wide"><div class="el-sys">${bars(o.u||15)}</div></div><div class="el-rhy narrow">${bars(o.un||11.5)}</div>
  <div class="el-lbl" data-notm>Add the next beat</div><div class="el-tfams">${o.fams.map(([c,k])=>fam(c,k)).join('')}</div>${earEditBtns(false)}`)}

Object.assign(MK,{LEN,lenGlyph,palHTML,ladHTML,score,deskLen,deskRes,resultHTML,markKey,gapHTML,mutHTML,setting,RC,cellMarks,rhyBar,tile,rhyDesk})})();
