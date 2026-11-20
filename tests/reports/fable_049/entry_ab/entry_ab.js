/* Mock-only: the desk for option (b), a length palette above the solfa ladder. Extends MK from ../mock.js. Not production code. */
MK.deskB=function(o){const d=document.querySelector('.meldesk'),M=o.M,nb=M.bars.length,per=2;
 RCELL.e1={l:'quaver',u:[[2,0]],v:[['8',0]],w:2};
 const glyph=k=>`<svg viewBox="0 0 36 38" aria-hidden="true">${elCellMarks(k,k==='e1'?4:7,14,4,31,false,'currentColor')}</svg>`;
 const pal=o.lens.map(([k,name,word])=>`<button class="el-len" role="radio" data-len="${k}" aria-checked="${k===o.len}" aria-label="${name}, ${word}${(o.off||[]).includes(k)?', does not fit this bar':''}" ${(o.off||[]).includes(k)?'disabled':''}>${glyph(k)}<small>${name}</small></button>`).join('');
 let map='<div class="el-sysmap" role="group" aria-label="Bars">';for(let i=0;i<nb;i+=per){const st=(o.mapState||[])[i/per]||'';map+=`<button aria-pressed="${i===o.view}" aria-label="Bars ${i+1} to ${i+per}">${i+1}–${i+per}<i>${[0,1].map(j=>`<span class="${st==='so'||(st==='half'&&j===0)?'so':''}"></span>`).join('')}</i></button>`}map+='</div>';
 d.className='meldesk r4 bylen';
 d.innerHTML=`<div class="el-palwrap"><div class="el-pal" role="radiogroup" aria-label="Note length"><span class="el-pallab" aria-hidden="true">Length</span>${pal}</div></div>
   <div class="melentry">${o.ladder}</div>
   <div class="melscore"><div class="lbl" data-notm>${o.label}</div>${map}<div class="melfr" id="earMel" role="img" aria-label="${o.aria||''}"></div></div>
   <div class="melacts">${earEditBtns(false)}<label class="note"><input type="checkbox" id="earLet"> show letter names</label></div>`;};
/* phones: the palette sticks under the score block, so it needs that block's height once the score is drawn (the build would keep this in step with a ResizeObserver) */
MK.palStick=function(){const d=document.querySelector('.meldesk');d.style.setProperty('--melscore-h',d.querySelector('.melscore').getBoundingClientRect().height+'px')};
