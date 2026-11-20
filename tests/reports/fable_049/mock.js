/* Mock-only helpers (0.49 ladder design). Runs inside the live app page; nothing here is production code.
   The markup these functions write is the reference markup for ladder049.css. */
window.MK=(()=>{
 const MEL={bands:[{stage:4,rungs:[1,2,3,4]},{stage:5,rungs:[5,6,7,8]},{stage:6,rungs:[9,10,11,12]}]},
       RHY={bands:[{stage:4,rungs:[1,2,3]},{stage:5,rungs:[4,5,6,7]},{stage:6,rungs:[8,9,10]}]};
 function rp(o){const L=o.drill==='rhy'?RHY:MEL,stageOf=n=>L.bands.find(b=>b.rungs.includes(n)).stage,open=o.open||stageOf(o.cur),top=o.stage||6;let h='',hid=0;
  for(const b of L.bands){const a=b.rungs[0],z=b.rungs[b.rungs.length-1],isCur=b.rungs.includes(o.cur);
   if(b.stage>top&&!isCur){hid+=b.rungs.length;continue}
   const isOpen=open===b.stage,sug=b.rungs.includes(o.sug);
   h+=`<button class="el-bandtab${isOpen?' open':''}${sug?' sug':''}" data-band="${b.stage}" aria-expanded="${isOpen}" aria-label="Stage ${b.stage}, rungs ${a} to ${z}"><small>Stage ${b.stage}</small><b>${a}–${z}</b></button>`;
   h+=`<div class="el-band${isCur?' cur':''}${isOpen?' open':''}" role="group" aria-label="Stage ${b.stage}"><span class="el-bandlab">Stage ${b.stage}</span>${b.rungs.map(n=>{const dn=(o.done||[]).includes(n);
    return`<button data-earlv="${n}" aria-pressed="${n===o.cur}" aria-label="Rung ${n}, Stage ${b.stage}${dn?', 8 of the last 10 reached':''}${n===o.sug?', suggested next':''}" class="${n===o.cur?'on':''}${dn?' done':''}${n===o.sug?' sug':''}">${n}</button>`}).join('')}</div>`}
  if(hid){const st=L.bands.filter(b=>b.stage>top).map(b=>b.stage);const lab='Stage '+(st.length>1?st[0]+'–'+st[st.length-1]:st[0]),sg=o.sug&&stageOf(o.sug)>top;h+=`<button class="el-bandmore${sg?' sug':''}" data-earall aria-pressed="false" aria-label="Show ${hid} more rungs, ${lab}"><b>${hid} more</b><span class="sep"> · </span><small>${lab}</small></button>`}
  return`<div class="el-rp" role="group" aria-label="Rung">${h}</div>`}
 function last10(a){const r=a.filter(x=>x===1).length,n=a.filter(x=>x!==null).length;
  return`<span class="el-last10" role="img" aria-label="Last ${n} answers on this rung: ${r} right">Last 10 <i>${a.map(x=>`<span class="${x===1?'r':x===null?'e':''}"></span>`).join('')}</i></span>`}
 function head(o){const hd=document.querySelector('#earCard .el-head'),row=hd.querySelector('.el-rungrow'),tot=o.drill==='rhy'?10:12;hd.classList.add('long');
  row.innerHTML=rp(o)+`<p class="el-rungline" data-notm><span><b>Rung ${o.cur} of ${tot}</b> · ${o.what}</span>${last10(o.last)}</p>`}
 function tally(st){EAR.st[EAR.drill]=st;const t=document.querySelector('#earCard .el-tally');if(t)t.outerHTML=earTallyHTML(st,'')}

 /* ---- notation: systems of bars with rhythm; a note with no pitch yet is a muted slash head on the middle line ---- */
 const KEYF={'s,':'c/4','l,':'d/4','t,':'e/4',d:'f/4',r:'g/4',m:'a/4',f:'bb/4',s:'c/5',l:'d/5',t:'e/5',"d'":'f/5'};
 const TICK={h:8,q:4,'8':2,'16':1,qd:6,hd:12};
 function score(el,M,o){const VF=Vex.Flow,IV='#ece2c8',MUTED='#9c927c',GOLD='#c9a24a',GIVEN='#c9b98f',k=ENG.space('exercise')/10,U=ENG.avail(el)/k,X0=2/k,per=o.per||2,[bn,bv]=M.sig.split('/').map(Number),barT=bn*(16/bv);
  const bars=o.bars||M.bars.map((_,i)=>i),sys=[];for(let i=0;i<bars.length;i+=per)sys.push(bars.slice(i,i+per));
  const above=22/k+14,below=20,rowH=above+40+below+20/k,gap=10/k,H=sys.length*rowH+(sys.length-1)*gap,W=U;
  const S=ENG.open(el,'exercise',W,H),svg=S.svg;svg.setAttribute('aria-hidden','true');const rules=[],sols=[],carets=[],nums=[],NI=[],SO=[];let a1=0,a2=0;M.bars.forEach(b=>{NI.push(a1);SO.push(a2);a1+=b.length;a2+=b.filter(n=>!n.rest).length});
  sys.forEach((sb,ri)=>{const top=ri*(rowH+gap),sy=top+above-40;let x=X0;
   const probe=new VF.Stave(0,0,300);probe.addClef('treble').addKeySignature('F');if(sb[0]===0)probe.addTimeSignature(M.sig);const lead=probe.getNoteStartX()+4,bw=(W-X0-2/k-lead)/per;
   sb.forEach((bi,j)=>{const first=j===0,w=first?lead+bw:bw,stv=new VF.Stave(x,sy,w);
    if(first){stv.addClef('treble').addKeySignature('F');if(bi===0)stv.addTimeSignature(M.sig);stv.setNoteStartX(x+lead)}
    stv.setBegBarType(VF.Barline.type.NONE).setEndBarType(bi===M.bars.length-1?VF.Barline.type.END:VF.Barline.type.SINGLE);stv.setContext(S.ctx).draw();
    if(first)nums.push({x:x+1/k,y:top+11/k,t:'bar '+(bi+1)});
    const src=M.bars[bi],sns=[],meta=[];let used=0,ni=NI[bi],so=SO[bi];
    src.forEach(n=>{if(ni>=o.rhythm){return}
     const d=n.d,base=d.replace('d',''),dot=/d$/.test(d);let sn,col=IV;
     if(n.rest){sn=new VF.StaveNote({keys:['b/4'],duration:base+'r'});meta.push({rest:1})}
     else{const has=so<o.solfa;
      if(has){sn=new VF.StaveNote({keys:[KEYF[n.s]],duration:base,auto_stem:true});col=n.given?GIVEN:IV}
      else{sn=new VF.StaveNote({keys:['b/4'],duration:base+'s',stem_direction:1});col=MUTED}
      meta.push({has,s:n.s,col,first:so===o.solfa});so++}
     if(dot)VF.Dot.buildAndAttach([sn]);sn.setStyle({fillStyle:col,strokeStyle:col});sns.push(sn);used+=TICK[d];ni++});
    const done=ni>=o.rhythm&&used<barT;
    const real=sns.length;let rest=barT-used;const ghosts=[];while(rest>0){const g=rest>=4?4:rest>=2?2:1;const gn=new VF.GhostNote({duration:g===4?'q':g===2?'8':'16'});ghosts.push(gn);sns.push(gn);rest-=g}
    if(sns.length){const v=new VF.Voice({num_beats:bn,beat_value:bv}).setMode(VF.Voice.Mode.SOFT);v.addTickables(sns);
     const beams=VF.Beam.generateBeams(sns.slice(0,real).filter(n=>!n.isRest()),{groups:[new VF.Fraction(bv===8?3:1,bv===8?8:4)]});
     new VF.Formatter().joinVoices([v]).format([v],w-(first?lead:0)-18);v.draw(S.ctx,stv);beams.forEach((b,bi2)=>{const c=sns.slice(0,real).filter(n=>!n.isRest()&&n.getBeam()===b)[0];const col=c&&c.getStyle()?c.getStyle().fillStyle:IV;b.setStyle({fillStyle:col,strokeStyle:col});b.setContext(S.ctx).draw()});
     const base=top+above+40+below+13/k;
     sns.slice(0,real).forEach((sn,i)=>{const m=meta[i];if(m.rest)return;const xx=(sn.getNoteHeadBeginX()+sn.getNoteHeadEndX())/2;
      if(m.has)sols.push({x:xx,y:base,t:m.s,fill:m.col});else rules.push({x:xx,y:base-1/k,cur:m.first})});
     if(ghosts.length&&o.caret&&!carets.length){const gx=ghosts[0].getAbsoluteX()+4;carets.push({x:gx,y1:top+above-6,y2:top+above+46})}}
    else if(o.caret&&!carets.length){carets.push({x:x+(first?lead:10)+4,y1:top+above-6,y2:top+above+46})}
    x+=w})});
  ENG.finish(S);
  svg.querySelectorAll('g.vf-stavenote').forEach(g=>{});
  const NS='http://www.w3.org/2000/svg',mk=(n,a)=>{const e=document.createElementNS(NS,n);for(const q in a)e.setAttribute(q,a[q]);svg.appendChild(e);return e};
  nums.forEach(n=>ENG.txt(S,n.x,n.y,n.t,'bar',{fill:MUTED}));
  rules.forEach((t,i)=>{const cur=o.cursor==='solfa'&&t.cur,ww=12/k,h=(cur?2:1)/k;mk('rect',{x:t.x-ww/2,y:t.y-h+1/k,width:ww,height:h,fill:cur?GOLD:'rgba(236,226,200,.3)'})});
  sols.forEach(t=>ENG.txt(S,t.x,t.y,t.t,'sol',{anchor:'middle',fill:t.fill}));
  carets.forEach(c=>mk('rect',{x:c.x,y:c.y1,width:2/k,height:c.y2-c.y1,fill:GOLD,rx:1/k}));
  return S}
 function draw(M,o){const el=document.getElementById('earMel');o=Object.assign({rhythm:999,solfa:1},o);return score(el,M,o)}

 /* ---- the desk for melody rungs 4 and up ---- */
 function desk(o){const d=document.querySelector('.meldesk'),lad=o.ladder,M=o.M,nb=M.bars.length,per=o.per||2;
  const tiles=earCells(o.cells||2).map(kk=>earRhyTile(kk,{named:RHYNAMES,disabled:(o.off||[]).includes(kk)})).join('');
  let map='';if(nb>per){map='<div class="el-sysmap" role="group" aria-label="Bars">';for(let i=0;i<nb;i+=per){const st=(o.mapState||[])[i/per]||'';map+=`<button aria-pressed="${i===o.view}" aria-label="Bars ${i+1} to ${i+per}">${i+1}–${i+per}<i>${[0,1].map(j=>`<span class="${st==='so'?'so':st==='rh'?'rh':st==='half'&&j===0?'so':st==='half'?'rh':st==='rh1'&&j===0?'rh':''}"></span>`).join('')}</i></button>`}map+='</div>'}
  d.className='meldesk r4';
  d.innerHTML=`<div class="el-steps" role="group" aria-label="Rhythm first, then solfa">
    <button aria-pressed="${o.step===1}" class="${o.rhFull?'full':''}"><span class="n">1</span><b>Rhythm</b><small>${o.rhTxt}</small></button>
    <button aria-pressed="${o.step===2}" ${o.rhFull?'':'disabled'} class="${o.soFull?'full':''}"><span class="n">2</span><b>Solfa</b><small>${o.soTxt}</small></button></div>
   <div class="melentry">${o.step===1?`<div class="el-lbl" data-notm>Add the next beat</div><div class="el-tiles named">${tiles}</div>`:lad}</div>
   <div class="melscore"><div class="lbl" data-notm>${o.label}</div>${map}<div class="melfr" id="earMel" role="img" aria-label="${o.aria||''}"></div></div>
   <div class="melacts">${earEditBtns(!!o.full)}<label class="note"><input type="checkbox" id="earLet"> show letter names</label></div>`}
 function ladder(range,last){const q={range,mode:'maj',key:{k:5,mode:'maj'}};const sv=EAR.ans;EAR.ans=last?[last]:[];const h=earMelLadderHTML(q,false,false);EAR.ans=sv;return h}
 function sug(o){const p=document.querySelector('#earCard .el-result');if(!p)return;p.insertAdjacentHTML('beforeend',`<div class="el-sug" role="status" data-notm>
   <svg class="ico" viewBox="0 0 30 30" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" aria-hidden="true"><path d="M9 27V5M21 27V5M9 22h12M9 16h12M9 10h12"/><path d="M15 13V3m-3.2 3.2L15 3l3.2 3.2" stroke-width="1.6"/></svg>
   <p><b>${o.lead}</b> ${o.ask}<small>${o.note}</small></p>
   <div class="acts"><button class="el-btn line" data-earlv="${o.next}">Try rung ${o.next}</button><button class="el-btn" data-earstay>Stay on rung ${o.cur}</button></div></div>`)}
 function sheet(rows){const hd=document.querySelector('#earCard .el-head'),row=hd.querySelector('.el-rungrow');hd.classList.add('long');
  row.innerHTML=rows.map(r=>`<div class="el-lbl" data-notm style="margin:14px 0 8px">${r.cap}</div>`+rp(r)).join('');
  document.querySelectorAll('#earCard>:not(.el-head)').forEach(e=>e.remove())}
 return{rp,last10,head,tally,draw,desk,ladder,sug,sheet}})();
