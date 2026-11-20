()=>{
 const W=document.documentElement.clientWidth,out={overlap:[],clipped:[],offscreen:[]};
 const vis=e=>{const s=getComputedStyle(e);return s.visibility!=='hidden'&&s.display!=='none'&&+s.opacity>0.05};
 const items=[];
 const walker=document.createTreeWalker(document.querySelector('main'),NodeFilter.SHOW_TEXT);
 let n;while(n=walker.nextNode()){const t=n.textContent.trim();if(!t)continue;const el=n.parentElement;if(!el||el.closest('script,style,.el-sr,.sr-only'))continue;
  if(el.closest('svg')&&!['text','tspan'].includes(el.tagName.toLowerCase()))continue;
  if(!el.getClientRects().length||!vis(el))continue;
  {const d=el.closest('details:not([open])');if(d&&!el.closest('summary'))continue}
  const r=document.createRange();r.selectNodeContents(n);
  // clip each line box by every ancestor that hides overflow, so text hidden inside a collapsed box is ignored
  let clip={l:-1e9,t:-1e9,r:1e9,b:1e9};for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){const s=getComputedStyle(p);if(/(hidden|clip|auto|scroll)/.test(s.overflow+s.overflowX+s.overflowY)){const R=p.getBoundingClientRect();clip={l:Math.max(clip.l,R.left),t:Math.max(clip.t,R.top),r:Math.min(clip.r,R.right),b:Math.min(clip.b,R.bottom)}}}
  for(const q of r.getClientRects()){const x1=Math.max(q.left,clip.l),y1=Math.max(q.top,clip.t),x2=Math.min(q.right,clip.r),y2=Math.min(q.bottom,clip.b);if(x2-x1<2||y2-y1<2)continue;items.push({el,t:t.slice(0,40),x1,y1,x2,y2,svg:!!el.closest('svg')})}}
 // overlaps between different elements (sweep by y)
 items.sort((a,b)=>a.y1-b.y1);
 const seen=new Set();
 for(let i=0;i<items.length;i++){const a=items[i];for(let j=i+1;j<items.length;j++){const b=items[j];if(b.y1>=a.y2)break;if(a.el===b.el||a.el.contains(b.el)||b.el.contains(a.el))continue;
  const ix=Math.min(a.x2,b.x2)-Math.max(a.x1,b.x1),iy=Math.min(a.y2,b.y2)-Math.max(a.y1,b.y1);if(ix<=1||iy<=1)continue;
  const ar=ix*iy,mn=Math.min((a.x2-a.x1)*(a.y2-a.y1),(b.x2-b.x1)*(b.y2-b.y1));if(ar<0.18*mn||ar<12)continue;
  // ignore text inside an element absolutely covering another only if one is transparent? keep all
  const k=a.t+'|'+b.t;if(seen.has(k))continue;seen.add(k);
  out.overlap.push({a:a.t,b:b.t,x:Math.round(Math.min(a.x1,b.x1)),y:Math.round(Math.min(a.y1,b.y1)+scrollY),w:Math.round(Math.max(a.x2,b.x2)-Math.min(a.x1,b.x1)),h:Math.round(Math.max(a.y2,b.y2)-Math.min(a.y1,b.y1)),svg:a.svg||b.svg,frac:+(ar/mn).toFixed(2)})}}
 // clipped text: overflow hidden/clip boxes whose text content is cut off
 document.querySelectorAll('main *').forEach(e=>{if(e.closest('svg,.el-sr,.sr-only')||!e.getClientRects().length)return;const s=getComputedStyle(e);
  const hid=/(hidden|clip)/.test(s.overflowX+s.overflowY);if(!hid)return;if(!e.textContent.trim())return;
  const cx=e.scrollWidth>e.clientWidth+2&&/(hidden|clip)/.test(s.overflowX)&&s.textOverflow!=='ellipsis',cy=e.scrollHeight>e.clientHeight+3&&/(hidden|clip)/.test(s.overflowY);
  if(cx||cy){const r=e.getBoundingClientRect();out.clipped.push({el:e.tagName+'.'+String(e.className).split(' ')[0],t:e.textContent.trim().slice(0,40),dir:(cx?'x':'')+(cy?'y':''),by:cx?e.scrollWidth-e.clientWidth:e.scrollHeight-e.clientHeight,x:Math.round(r.left),y:Math.round(r.top+scrollY),w:Math.round(r.width),h:Math.round(r.height)})}});
 // text beyond the right edge of the screen, not inside a scroller
 items.forEach(a=>{if(a.x2>W+1){let p=a.el,sc=false;while(p&&p!==document.body){const s=getComputedStyle(p);if(/(auto|scroll)/.test(s.overflowX)){sc=true;break}p=p.parentElement}if(!sc)out.offscreen.push({t:a.t,x:Math.round(a.x1),y:Math.round(a.y1+scrollY)})}});
 out.offscreen=out.offscreen.slice(0,10);
 return out}
