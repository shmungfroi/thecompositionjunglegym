/* Reference behaviour for the two 18-rung pickers (mock; also inlined into the static HTML so the previews can be clicked).
   A: Stage tabs open a band on phones; Left/Right walk the rungs across bands.
   B: menu button pattern. Button: Enter, Space, Down open on the rung in use (or the first); Up opens on the last.
      Menu: Up/Down move and wrap; Home/End; Left/Right open the neighbouring Stage's menu; a digit jumps to a rung ending in it;
      Enter/Space choose, close and return focus to the button; Esc closes and returns focus; Tab or a click outside closes. */
(()=>{const $=(s,r=document)=>[...r.querySelectorAll(s)],card=document.getElementById('earCard');if(!card)return;
 const line=n=>{const b=card.querySelector('.el-rungline b');if(!b)return;const what=(card.querySelector(`[data-earlv="${n}"]`).getAttribute('aria-label').split(': ')[1]||'').split(', 8 of')[0].split(', suggested')[0];b.parentElement.innerHTML=`<b>Rung ${n} of 18</b> · Stage ${4+Math.floor((n-1)/6)} · ${what}`};
 /* ---- A ---- */
 const rp=card.querySelector('.el-rp.r18');
 if(rp){const openBand=s=>{$('.el-bandtab',rp).forEach(t=>{const o=t.dataset.band===String(s);t.classList.toggle('open',o);t.setAttribute('aria-expanded',o)});$('.el-band',rp).forEach(b=>b.classList.toggle('open',b.id==='p18band'+s))};
  rp.addEventListener('click',e=>{const t=e.target.closest('.el-bandtab');if(t)return openBand(t.dataset.band);const r=e.target.closest('[data-earlv]');if(!r)return;
   $('[data-earlv]',rp).forEach(x=>{const on=x===r;x.classList.toggle('on',on);x.setAttribute('aria-pressed',on)});$('.el-band',rp).forEach(b=>b.classList.toggle('cur',b.contains(r)));line(+r.dataset.earlv)});
  rp.addEventListener('keydown',e=>{const r=e.target.closest('[data-earlv]');if(!r||!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;const all=$('[data-earlv]',rp),i=all.indexOf(r);
   const to=all[e.key==='Home'?0:e.key==='End'?all.length-1:Math.max(0,Math.min(all.length-1,i+(e.key==='ArrowRight'?1:-1)))];e.preventDefault();if(!to.offsetParent)openBand(to.parentElement.id.slice(7));to.focus()})}
 /* ---- B ---- */
 const sm=card.querySelector('.el-sm');
 if(sm){const btns=$('.el-smb',sm),menu=b=>document.getElementById(b.getAttribute('aria-controls')),items=m=>$('.el-smi',m);
  const close=(focus)=>{btns.forEach(b=>{if(b.getAttribute('aria-expanded')==='true'){b.setAttribute('aria-expanded','false');menu(b).hidden=true;if(focus)b.focus()}})};
  const open=(b,where)=>{close(false);b.setAttribute('aria-expanded','true');const m=menu(b),it=items(m);m.hidden=false;(where==='last'?it[it.length-1]:where==='first'?it[0]:it.find(x=>x.getAttribute('aria-checked')==='true')||it[0]).focus()};
  const choose=it=>{const n=+it.dataset.earlv;$('.el-smi',sm).forEach(x=>{const c=x===it;x.setAttribute('aria-checked',c);x.querySelector('.m').textContent=c?'in use':x.classList.contains('sug')?'suggested':x.classList.contains('done')?'reached':''});
   btns.forEach(b=>{const m=menu(b),mine=m.contains(it),z=items(m).map(x=>+x.dataset.earlv);b.classList.toggle('cur',mine);b.querySelector('.v').textContent=mine?'Rung '+n:z[0]+'–'+z[5];
    $('.pips i',b).forEach((p,k)=>{const x=items(m)[k];p.className=z[k]===n?'on':x.classList.contains('sug')?'sug':x.classList.contains('done')?'done':''})});line(n);close(true)};
  sm.addEventListener('click',e=>{const b=e.target.closest('.el-smb');if(b)return b.getAttribute('aria-expanded')==='true'?close(true):open(b);const it=e.target.closest('.el-smi');if(it)choose(it)});
  sm.addEventListener('keydown',e=>{const b=e.target.closest('.el-smb'),it=e.target.closest('.el-smi'),k=e.key;
   if(b){if(k==='ArrowDown'||k==='Enter'||k===' '){e.preventDefault();open(b)}else if(k==='ArrowUp'){e.preventDefault();open(b,'last')}else if(k==='Escape')close(true);return}
   if(!it)return;const m=it.parentElement,all=items(m),i=all.indexOf(it),bi=btns.findIndex(x=>menu(x)===m);
   if(k==='ArrowDown'||k==='ArrowUp'){e.preventDefault();all[(i+(k==='ArrowDown'?1:-1)+all.length)%all.length].focus()}
   else if(k==='Home'||k==='End'){e.preventDefault();all[k==='Home'?0:all.length-1].focus()}
   else if(k==='ArrowRight'||k==='ArrowLeft'){e.preventDefault();open(btns[(bi+(k==='ArrowRight'?1:-1)+btns.length)%btns.length],'first')}
   else if(k==='Enter'||k===' '){e.preventDefault();choose(it)}
   else if(k==='Escape'){e.preventDefault();close(true)}
   else if(k==='Tab'){close(false)}
   else if(/^\d$/.test(k)){const t=all.slice(i+1).concat(all.slice(0,i+1)).find(x=>x.dataset.earlv.endsWith(k));if(t)t.focus()}});
  document.addEventListener('pointerdown',e=>{if(!sm.contains(e.target))close(false)})}
})();
