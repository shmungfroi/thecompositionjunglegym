"""Fable's verification renders of the 0.49 ladder UI, from the real app (049-int), at 1366x768 and 390x844.
Run: python3 tests/reports/checks/fable_ladderui/shots.py <repo dir> [scene ...]
Each scene writes <name>_<w>.png (the screen as it opens on the desk) and <name>_<w>_card.png (the whole Ear Lab card),
and a line of measurements into metrics.json. One browser, one page at a time."""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright

PRE = "(()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='ear';EAR.all=false;EAR.st={};EAR.rd={};EAR.reached={};room('ear')})()"
STUB = "window.earPlay=()=>{};window.elPlay=()=>{}"
SEED = "(s)=>{let a=s>>>0;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}"

# melody: o = {l, mod, want (js on q), frac, edit (js: (T,q)=>list of {s,t}), mut (bool), chk, rd (last-10 marks), part}
MEL = """(o)=>{EAR.mod=o.mod||'home';const want=o.want?new Function('q','return '+o.want):null;let q,ok=false;
 if(o.rd){EAR.rd={mel:{[o.l]:o.rd}};EAR.reached={mel:o.reached||[]}}else{EAR.rd={};EAR.reached={}}
 for(let t=0;t<800;t++){EAR.drill='mel';EAR.lvl.mel=o.l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();q=EAR.q;if(!want||want(q)){ok=true;break}}
 if(!ok)return{err:'no item for '+o.want};
 const parts=q.l===11?['mel','bass']:['mel'];const log=[];
 for(const part of parts){if(q.l===11&&EAR.part!==part)document.querySelector(`[data-earpart="${part}"]`).click();
  let T=ladTruthEntries(q,part).map((e,j)=>({s:e.s,t:e.t,idx:j+1}));
  if(q.l===9&&o.mod==='move'&&q.readings&&part==='mel')T.forEach(e=>{if(e.idx>q.pivot)e.s=q.readings.move[e.idx]});
  if(o.edit&&part==='mel')T=new Function('T','q','return '+o.edit)(T,q)||T;
  const frac=part==='bass'?(o.bfrac===undefined?o.frac:o.bfrac):o.frac,n=Math.floor(T.length*frac);
  for(let j=0;j<n;j++){const e=T[j];if(e.s===null){document.querySelector(`[data-rest="${e.t}"]`).click();continue}
   const lb=document.querySelector(`[data-len="${e.t}"]`);if(!lb||lb.getAttribute('aria-disabled')==='true'){log.push('len '+e.t+' not live at '+j);break}
   if(lb.getAttribute('aria-checked')!=='true')lb.click();
   const rb=document.querySelector(`[data-earsol="${e.s}"]`);if(!rb){log.push('no row '+e.s);break}rb.click();
   if(q.l===9&&o.mod==='move'&&o.mut!==false&&q.readings&&e.idx===(o.mutAt||q.pivot)&&part==='mel'){const m=document.querySelector('[data-earmut]');if(m&&!m.disabled)m.click();else log.push('no mut')}}}
 if(o.backTo){document.querySelector(`[data-earpart="${o.backTo}"]`).click()}
 if(o.chk){if(!earFull(q))log.push('not full');else earCheck()}
 return{l:q.l,metre:q.metre,anac:q.anac,kind:q.kind,a:q.a.join(' '),res:EAR.res&&EAR.res.kind,log}}"""

RHY = """(o)=>{const want=o.want?new Function('q','return '+o.want):null;let q,ok=false;EAR.rd={};EAR.reached={};if(o.names)EAR.names=o.names;
 for(let t=0;t<800;t++){EAR.drill='rhy';EAR.lvl.rhy=o.l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();q=EAR.q;if(!want||want(q)){ok=true;break}}
 if(!ok)return{err:'no item'};const log=[];let A=q.a.slice();if(o.edit)A=new Function('A','q','return '+o.edit)(A,q)||A;
 const n=Math.floor(A.length*o.frac);
 for(let j=0;j<n;j++){const b=document.querySelector(`.el-tile[data-earcell="${A[j]}"]`);if(!b||b.disabled){log.push(A[j]+(b?' disabled':' missing'));break}b.click()}
 if(q.drums&&o.drums!==0){const T=ladDrumOns(q.drums);let k=0;for(const key of['kick','snare'])for(const t of T[key]){k++;if(o.drumSkip&&k===o.drumSkip)continue;const b=document.querySelector(`[data-eardrum="${key}:${t}"]`);if(b)b.click();else log.push('drum '+key+t)}}
 if(o.chk){if(earFull(q))earCheck();else log.push('not full')}
 return{l:q.l,metre:q.metre,a:q.a.join(' '),res:EAR.res&&EAR.res.kind,log}}"""

SWAP = "{di:'ra',ra:'di',ri:'me',me:'ri',fi:'se',se:'fi',si:'le',le:'si',li:'te',te:'li'}"
# one rhythm slip (two quavers written as one crotchet) and one wrong note later on
SLIP = """(()=>{const out=[];let done=false,pos=q.anac?-q.anac:0;for(let j=0;j<T.length;j++){const e=T[j];
  if(!done&&j>3&&e.t===210&&T[j+1]&&T[j+1].t===210&&((pos%420)+420)%420===0){out.push({s:e.s,t:420,idx:e.idx});pos+=420;j++;done=true;continue}out.push(e);pos+=e.t}
 const k=1,alt=['d','r','m','s','l'].find(x=>x!==out[k].s&&x!==out[k-1].s&&document.querySelector(`[data-earsol="${x}"]`));out[k]={...out[k],s:alt};return out})()"""

SCENES = {
 # name: (kind, opts, seed)
 'picker_long_header': ('mel', dict(l=6, frac=0, rd=[1,1,0,1,1,1,1,1,1], reached=[4,5]), 11),
 'pal_r6_24': ('mel', dict(l=6, want="q.metre==='2/4'&&!q.anac", frac=.55), 3),
 'pal_r6_68': ('mel', dict(l=6, want="q.metre==='6/8'&&q.anac", frac=.55), 5),
 'res_r6': ('mel', dict(l=6, want="q.metre==='2/4'&&!q.anac&&q.cells.flat().filter(k=>k==='e2').length>=2", frac=1, edit=SLIP, chk=1), 7),
 'a2_r7': ('mel', dict(l=7, want="q.aug2&&q.aug2.length", frac=1, edit="T.map((e,j)=>e.idx===q.aug2[0]+1?{...e,s:e.s.replace('si','s')}:e)", chk=1), 9),
 'a2_r7_entry': ('mel', dict(l=7, want="q.aug2&&q.aug2.length", frac=.4), 9),
 'mut_r9_MV': ('mel', dict(l=9, mod='move', want="q.readings&&q.kind==='M-V'", frac=.75), 13),
 'mut_r9_mv_was_ri': ('mel', dict(l=9, mod='move', want="q.readings&&q.kind==='m-v'", frac=.75), 15),
 'mut_r9_before': ('mel', dict(l=9, mod='move', want="q.readings&&q.kind==='M-V'", frac=.3, mut=False), 13),
 'res_r9_move': ('mel', dict(l=9, mod='move', want="q.readings&&q.kind==='M-V'", frac=1, chk=1), 13),
 'res_r9_move_missing': ('mel', dict(l=9, mod='move', want="q.readings&&q.kind==='M-V'", frac=1, chk=1, mut=False), 13),
 'res_r9_move_late': ('mel', dict(l=9, mod='move', want="q.readings&&q.kind==='M-V'&&q.pivotWindow[1]+3<q.notes.length-2", frac=1, chk=1, mutAt=-1, edit="(()=>{T.forEach(e=>{if(e.idx===q.pivotWindow[1]+3)e.late=1});return T})()"), 13),
 'res_r9_home': ('mel', dict(l=9, mod='home', want="q.readings&&q.kind==='M-V'", frac=1, chk=1, edit="T.map((e,j)=>j===T.length-4?{...e,s:e.s==='r'?'m':'r'}:e)"), 13),
 'nearly_r10': ('mel', dict(l=10, want="q.chrom&&q.chrom.length", frac=1, chk=1, edit="(()=>{const M=%s;const j=q.chrom[0];return T.map((e,k)=>e.idx===j?{...e,s:e.s.replace(/^[a-z]+/,m=>M[m]||m)}:e)})()" % SWAP), 17),
 'lad_r10_entry': ('mel', dict(l=10, frac=.4), 17),
 'two_r11_mel': ('mel', dict(l=11, frac=.5, bfrac=0), 19),
 'two_r11_bass': ('mel', dict(l=11, frac=1, bfrac=.5), 19),
 'res_r11': ('mel', dict(l=11, frac=1, bfrac=1, chk=1, edit="T.map((e,j)=>j===4?{...e,s:e.s==='m'?'r':'m'}:e)"), 19),
 'pal_r12': ('mel', dict(l=12, frac=.4), 21),
 'rhy_r9_sept': ('rhy', dict(l=9, want="q.a.some(k=>/7|sep/i.test(k))", frac=.9), 23),
 'rhy_r9_sept_kk': ('rhy', dict(l=9, want="q.a.some(k=>/7|sep/i.test(k))", frac=.9, names='kk'), 23),
 'rhy_r9_result': ('rhy', dict(l=9, want="q.a.some(k=>/7|sep/i.test(k))", frac=1, chk=1, edit="(()=>{const B=A.slice();const j=B.findIndex(k=>k==='q');if(j>=0)B[j]='e2';return B})()"), 23),
 'rhy_r9_78_result': ('rhy', dict(l=9, want="q.metre==='7/8'", frac=1, chk=1), 27),
 'rhy_r4_result': ('rhy', dict(l=4, frac=1, chk=1), 29),
 'rhy_r10_lanes': ('rhy', dict(l=10, frac=.6, drums=0), 25),
 'rhy_r10_result': ('rhy', dict(l=10, frac=1, chk=1, drumSkip=2), 25),
}

MEASURE = """()=>{const R=s=>{const e=document.querySelector('#earMain '+s);if(!e)return null;const r=e.getBoundingClientRect();return[Math.round(r.width),Math.round(r.height)]};
 const small=[];[...document.querySelectorAll('#earMain *')].forEach(e=>{if(e instanceof SVGElement||!e.offsetParent)return;const t=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());if(!t)return;const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<10.95&&e.getBoundingClientRect().width)small.push((e.className||e.tagName)+':'+e.textContent.trim().slice(0,14)+':'+fs)});
 document.querySelectorAll('#earMain svg text').forEach(t=>{const sv=t.closest('svg'),w=sv.getBoundingClientRect().width;if(!w)return;const vb=sv.viewBox.baseVal,sc=vb&&vb.width?w/vb.width:1,fs=parseFloat(getComputedStyle(t).fontSize)*sc;if(fs<10.9&&t.getBoundingClientRect().width)small.push('svg:'+t.textContent.slice(0,10)+':'+fs.toFixed(1))});
 const tg=[];document.querySelectorAll('#earMain button, #earMain a, #earMain input, #earMain label.el-chk').forEach(b=>{if(!b.offsetParent)return;const r=b.getBoundingClientRect();if(r.width<1)return;if(r.height<43.5||r.width<43.5)tg.push((b.className||b.tagName)+':'+b.textContent.trim().slice(0,12)+':'+Math.round(r.width)+'x'+Math.round(r.height))});
 return{over:document.documentElement.scrollWidth-innerWidth,head:R('.el-head'),rp:R('.el-rp'),pal:R('.el-pal'),len:R('.el-len'),hold:R('.melhold'),score:R('.melfr'),lad:R('.earlad'),step:R('.earstep'),half:R('.earhalf .earstep'),mut:R('.el-mut'),set:R('.grp.set'),ans:R('.el-answer'),res:R('.el-result'),gap:R('.el-gap'),card:R('.el-card')||R(''),small:small.slice(0,8),under44:tg.slice(0,12)}}"""

async def main():
    names = sys.argv[2:] or list(SCENES)
    mf = OUT / 'metrics.json'
    M = json.loads(mf.read_text()) if mf.exists() else {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in ((1366, 768), (390, 844)):
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 500 else 1)
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.route('**/*', cjg.make_route(REPO))
            await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
            await pg.evaluate(PRE); await pg.evaluate(STUB)
            for nm in names:
                kind, o, seed = SCENES[nm]
                await pg.evaluate("EAR.names='k';EAR.part='mel';EAR.sugNow=false;EAR.sugSeen={}")
                await pg.evaluate(SEED, seed)
                r = await pg.evaluate(MEL if kind == 'mel' else RHY, o)
                await pg.wait_for_timeout(350)
                await pg.evaluate("window.scrollTo(0,0)")
                m = await pg.evaluate(MEASURE); m['scene'] = r; m['errs'] = errs[:3]
                M[f'{nm}_{w}'] = m
                HIDE = "()=>{window.__h=[];document.querySelectorAll('body *').forEach(e=>{if(getComputedStyle(e).position==='fixed'&&!e.closest('#earMain')){window.__h.push([e,e.style.visibility]);e.style.visibility='hidden'}})}"
                SHOW = "()=>{(window.__h||[]).forEach(([e,v])=>e.style.visibility=v)}"
                if w < 500:
                    # the screen as the student has it: the card's head under the top bar; then the entry (held block stuck) or the result
                    await pg.evaluate("()=>{const c=document.querySelector('#earMain .el-head');scrollTo(0,c.getBoundingClientRect().top+scrollY-100)}")
                    await pg.wait_for_timeout(120); await pg.screenshot(path=str(OUT / f'{nm}_{w}.png'))
                    if o.get('chk'):
                        await pg.evaluate("()=>{const c=document.querySelector('#earResult');if(c)scrollTo(0,c.getBoundingClientRect().top+scrollY-104)}")
                        await pg.wait_for_timeout(120); await pg.screenshot(path=str(OUT / f'{nm}_{w}_result.png'))
                        await pg.evaluate("()=>{const c=document.querySelector('#earMain .melscore, #earMain .el-rhy, #earMain .el-cmp');if(c)scrollTo(0,c.getBoundingClientRect().top+scrollY-110)}")
                        await pg.wait_for_timeout(120); await pg.screenshot(path=str(OUT / f'{nm}_{w}_staves.png'))
                    else:
                        await pg.evaluate("()=>{const e=document.querySelector('#earMain .melentry, #earMain .el-tiles'),h=document.querySelector('#earMain .melhold');if(e)scrollTo(0,e.getBoundingClientRect().top+scrollY-(h?h.getBoundingClientRect().height:0)-104)}")
                        await pg.wait_for_timeout(120); await pg.screenshot(path=str(OUT / f'{nm}_{w}_entry.png'))
                    await pg.evaluate("window.scrollTo(0,0)")
                else:
                    await pg.screenshot(path=str(OUT / f'{nm}_{w}.png'))
                await pg.evaluate(HIDE)
                el = await pg.query_selector('#earMain .el-card') or await pg.query_selector('#earMain')
                await el.screenshot(path=str(OUT / f'{nm}_{w}_card.png'))
                await pg.evaluate(SHOW)
                print(nm, w, json.dumps(r, ensure_ascii=False)[:300], '| over', m['over'], '| small', m['small'][:3], '| <44', m['under44'][:4] if w < 500 else '', flush=True)
            await pg.close()
        await b.close()
    mf.write_text(json.dumps(M, indent=1, ensure_ascii=False))
asyncio.run(main())
