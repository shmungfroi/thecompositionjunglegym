/* Mock-only: reference markup for picker18.css (window.P18), written inside the live app page.
   Placeholder ladder: the 18 one-line descriptions are Fable's, to test the layout; the real ones come from the 0.50 ladder register. */
window.P18=(()=>{
 const WHAT={1:'so and mi · two bars of 2/4, crotchets',2:'adds la · two bars, crotchets and quavers',3:'mi re do · two bars, steps only',4:'do re mi so la · four bars of 2/4',5:'adds low la and low so · four bars',6:'adds high do · four bars of 4/4',
  7:'adds fa · four bars of 2/4, do to la',8:'adds ti · the whole major scale',9:'four bars of 3/4 with dotted minims',10:'la minor · four bars, steps and thirds',11:'four bars of 6/8, steps and thirds',12:'dotted rhythms, leaps of a 4th and 5th',
  13:'eight bars of 4/4, leaps up to a 6th',14:'eight bars of 3/4 with dotted rhythms',15:'harmonic minor · adds si',16:'eight bars of 6/8 in the minor',17:'one chromatic note: fi or ta',18:'eight bars that move to the dominant'};
 const BANDS=[4,5,6].map((s,i)=>({stage:s,rungs:[1,2,3,4,5,6].map(n=>n+i*6)})),stageOf=n=>4+Math.floor((n-1)/6);
 const lab=(n,o)=>`Rung ${n}, Stage ${stageOf(n)}: ${WHAT[n]}${o.done.includes(n)?', 8 of the last 10 reached':''}${n===o.sug?', suggested next':''}`;
 /* A · one row, all rungs */
 function a(o){const open=o.open||stageOf(o.cur);
  const tabs=BANDS.map(b=>{const z=b.rungs,isO=open===b.stage,sg=z.includes(o.sug)&&!isO;
   return`<button class="el-bandtab${isO?' open':''}${z.includes(o.cur)?' cur':''}${sg?' sug':''}" data-band="${b.stage}" aria-expanded="${isO}" aria-controls="p18band${b.stage}" aria-label="Stage ${b.stage}, rungs ${z[0]} to ${z[5]}${z.includes(o.cur)?', rung '+o.cur+' in use':''}${sg?', holds the suggested rung':''}"><small>Stage ${b.stage}</small><b>${z[0]}–${z[5]}</b></button>`}).join('');
  const bands=BANDS.map(b=>`<div class="el-band${b.rungs.includes(o.cur)?' cur':''}${open===b.stage?' open':''}" id="p18band${b.stage}" role="group" aria-label="Stage ${b.stage}"><span class="el-bandlab">Stage ${b.stage}</span>${b.rungs.map(n=>
   `<button data-earlv="${n}" aria-pressed="${n===o.cur}" aria-label="${lab(n,o)}" title="${WHAT[n]}" class="${n===o.cur?'on':''}${o.done.includes(n)?' done':''}${n===o.sug?' sug':''}">${n}</button>`).join('')}</div>`).join('');
  return`<div class="el-rp r18" role="group" aria-label="Rung"><div class="el-stagetabs">${tabs}</div>${bands}</div>`}
 /* B · Stage menus (menu button pattern: button aria-haspopup="menu", popup role="menu", rows role="menuitemradio") */
 const CHEV='<svg class="chev" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1.5 3.5 5 7l3.5-3.5"/></svg>';
 function b(o){let h='';BANDS.forEach((bd,i)=>{const z=bd.rungs,cur=z.includes(o.cur),nd=z.filter(n=>o.done.includes(n)).length,sg=z.includes(o.sug),isO=o.open===bd.stage;
   h+=`<button class="el-smb${cur?' cur':''}" id="p18b${bd.stage}" aria-haspopup="menu" aria-expanded="${isO}" aria-controls="p18m${bd.stage}" aria-label="Stage ${bd.stage}, ${cur?'on rung '+o.cur:'rungs '+z[0]+' to '+z[5]}, ${nd} of 6 reached${sg?', holds the suggested rung':''}"><span class="st">Stage ${bd.stage}</span><span class="v">${cur?'Rung '+o.cur:z[0]+'–'+z[5]}</span><span class="pips" aria-hidden="true">${z.map(n=>`<i class="${n===o.cur?'on':n===o.sug?'sug':o.done.includes(n)?'done':''}"></i>`).join('')}</span>${CHEV}</button>`;
   h+=`<div class="el-smm" id="p18m${bd.stage}" role="menu" aria-labelledby="p18b${bd.stage}" style="${i===2?'right:0':i===1?'left:50%;margin-left:-196px':'left:0'}"${isO?'':' hidden'}><div class="hd" aria-hidden="true"><span>Stage ${bd.stage} · rungs ${z[0]}–${z[5]}</span><span>${nd} of 6 reached</span></div>${z.map(n=>{const dn=o.done.includes(n),c=n===o.cur,s=n===o.sug;
    return`<button class="el-smi${dn?' done':''}${s?' sug':''}" role="menuitemradio" aria-checked="${c}" tabindex="-1" data-earlv="${n}" aria-label="${lab(n,o)}"><span class="n">${n}</span><span class="d">${WHAT[n]}</span><span class="m">${c?'in use':s?'suggested':dn?'reached':''}</span></button>`}).join('')}</div>`});
  return`<div class="el-sm" role="group" aria-label="Rung, by Stage">${h}</div>`}
 function head(kind,o){const hd=document.querySelector('#earCard .el-head'),row=hd.querySelector('.el-rungrow');hd.classList.add('long');
  row.innerHTML=(kind==='a'?a(o):b(o))+`<p class="el-rungline" data-notm><span><b>Rung ${o.cur} of 18</b> · Stage ${stageOf(o.cur)} · ${WHAT[o.cur]}</span>${MK.last10(o.last)}</p>`;
  const t=document.querySelector('#earCard .el-tag');if(t)t.textContent='Stage 6 · rung '+o.cur+' of 18'}
 return{a,b,head,WHAT}})();
