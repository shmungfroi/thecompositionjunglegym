"""Fable verification of C6, C13-C16 (0.49). Run from the repo root: python3 tests/reports/checks/fable_c6/verify.py
Writes PNGs beside this file and prints measurements."""
import sys, asyncio, pathlib, json
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
SIZES = [(1440, 900), (1366, 768), (1024, 768), (390, 844)]
ONLY = sys.argv[1:] 

LETTER = """()=>{const cv=document.createElement('canvas').getContext('2d');const out=[];
 document.querySelectorAll('.bar[data-fn],.clrn span[data-fn]').forEach(b=>{if(!b.offsetParent)return;const cs=getComputedStyle(b,'::after');cv.font='600 11px Outfit';
  const t=b.dataset.fn,w=cv.measureText(t).width+t.length*1,r=b.getBoundingClientRect(),clr=b.matches('.clrn span');
  const box={l:r.right-1-8-w,r:r.right-1-8,t:clr?r.top+3+7:r.bottom-1-5-11,b:clr?r.top+3+7+11:r.bottom-1-5};
  let hit=null;const tw=document.createTreeWalker(b,NodeFilter.SHOW_TEXT);let n;while((n=tw.nextNode())){if(!n.nodeValue.trim())continue;const rg=document.createRange();rg.selectNodeContents(n);
   for(const q of rg.getClientRects()){if(q.right>box.l-2&&q.left<box.r&&q.bottom>box.t+1&&q.top<box.b-1)hit={txt:n.nodeValue.trim(),gap:Math.round(box.l-q.right)}}}
  out.push({fn:t,fs:cs.fontSize,col:cs.color,w:Math.round(r.width),h:Math.round(r.height),hit})});
 return{n:out.length,fs:[...new Set(out.map(o=>o.fs))],hits:out.filter(o=>o.hit),fns:out.map(o=>o.fn).join(' '),
  keys:[...document.querySelectorAll('.fnkey')].filter(k=>k.offsetParent).length,grids:[...document.querySelectorAll('.bargrid,.clrn')].filter(k=>k.offsetParent).length,
  keyfs:[...new Set([...document.querySelectorAll('.fnkey,.fnkey b')].map(e=>getComputedStyle(e).fontSize))],over:document.documentElement.scrollWidth>innerWidth}}"""

async def clip(pg, name, sel, below=None, pad=10):
    r = await pg.evaluate("""([s,b])=>{const e=document.querySelector(s);if(!e)return null;e.scrollIntoView({block:'center'});const a=e.getBoundingClientRect();let bt=a.bottom;
        if(b){const n=[...document.querySelectorAll(b)].pop();if(n)bt=Math.max(bt,n.getBoundingClientRect().bottom)}return{x:a.x+scrollX,y:a.y+scrollY,w:a.width,h:bt-a.y}}""", [sel, below])
    if not r: print('MISSING', name, sel); return
    await pg.screenshot(path=str(HERE / name), full_page=True, clip={'x': max(0, r['x'] - pad), 'y': max(0, r['y'] - pad), 'width': r['w'] + 2 * pad, 'height': r['h'] + 2 * pad})

async def run(p):
    b = await cjg.launch(p)
    for w, h in SIZES:
        pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate("window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11);window.earPlay=()=>{}")
        await pg.evaluate("()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='climbs';room('climbs')}")
        await pg.wait_for_timeout(700)
        for ci in range(3, 12):
            await pg.evaluate("(i)=>{CL.open=i;renderClimbs()}", ci); await pg.wait_for_timeout(500)
            m = await pg.evaluate(LETTER); print(w, 'climb', ci + 1, json.dumps(m))
            if w in (1366, 390):
                await clip(pg, f'climb{ci+1}_{w}.png', '#climbDetail .bargrid', '#climbDetail .fnkey')
            if ci == 4:
                wm = await pg.evaluate("""()=>[...document.querySelectorAll('.wheel .wn')].map(g=>{const c=g.querySelector('circle').getBoundingClientRect(),f=g.querySelector('.f'),r=f.getBoundingClientRect(),s=g.closest('svg').getBoundingClientRect();
                  const cx=c.x+c.width/2,cy=c.y+c.height/2,rad=c.width/2;const d=Math.hypot(Math.max(r.left-cx,0),Math.min(r.bottom-cy,0));
                  return{t:f.textContent,fs:getComputedStyle(f).fontSize,gap:+(Math.hypot(r.left-cx,(r.bottom-2)-cy)-rad).toFixed(1),inSvg:r.right<=s.right+.5&&r.top>=s.top-.5}})""")
                print(w, 'wheel', json.dumps(wm))
                await clip(pg, f'wheel_{w}.png', '.wheel')
                # the "now" bar
                await pg.evaluate("()=>document.querySelectorAll('#climbDetail .bargrid .bar')[2].classList.add('now')")
                await clip(pg, f'climb5_now_{w}.png', '#climbDetail .bargrid', '#climbDetail .fnkey')
        # Analysis
        await pg.evaluate("""()=>{K={k:9,mode:'min'};P=['i','iv','V','VII','III','VI','ii\\u00b0','bII','i'].map(r=>({...parseRoman(r,K),inv:0,beats:4}));saveP();AN.tab='prog';location.hash='analysis';room('analysis');renderAnalysis()}""")
        await pg.wait_for_timeout(700)
        print(w, 'analysis', json.dumps(await pg.evaluate(LETTER)))
        await clip(pg, f'analysis_{w}.png', '.clrn', '.clrn + .fnkey')
        # Ear Lab chips
        await pg.evaluate("()=>{S.level=6;location.hash='ear';EAR.all=false;EAR.st={};room('ear')}")
        for d, l in (('bass', 3), ('cad', 3)):
            await pg.evaluate("(a)=>{const [d,l]=a;EAR.drill=d;EAR.lvl[d]=l;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();EAR.q=earGen(EAR.drill,earLvl(),R);EAR.q.plays=1;renderEar()}", [d, l]); await pg.wait_for_timeout(300)
            await pg.evaluate("""()=>{const q=EAR.q;if(q.d==='bass')earMark(false,q.a.slice(0,-1).concat([q.opts.find(x=>x!==q.a[q.a.length-1])]));else earMark(false,(q.opts||[...document.querySelectorAll('#earMain [data-earans]')].map(x=>x.dataset.earans)).find(x=>x!==q.a));renderEar()}""")
            await pg.wait_for_timeout(500)
            m = await pg.evaluate("""()=>({chips:[...document.querySelectorAll('.el-chords .el-ch')].map(c=>{const f=c.querySelector('small .fn'),s=c.querySelector('small');return{t:s.textContent,fn:f&&f.textContent,fs:f&&getComputedStyle(f).fontSize,col:f&&getComputedStyle(f).color,face:getComputedStyle(c).color,w:Math.round(c.getBoundingClientRect().width)}}),
               keys:document.querySelectorAll('#earMain .fnkey').length,over:document.documentElement.scrollWidth>innerWidth,
               verdict:[...document.querySelectorAll('.el-result .el-verdict,.el-result h3,.el-result .el-head')].map(e=>[e.textContent.trim().slice(0,30),getComputedStyle(e).color])})""")
            print(w, 'ear', d, json.dumps(m))
            await clip(pg, f'ear_{d}_{w}.png', '.el-result', None, pad=6)
        # FR-19 checkbox
        await pg.evaluate("()=>{EAR.drill='mel';EAR.lvl.mel=2;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();EAR.q=earGen('mel',2,R);EAR.q.plays=1;renderEar()}"); await pg.wait_for_timeout(400)
        print(w, 'earLet', json.dumps(await pg.evaluate("()=>{const l=document.querySelector('#earLet');if(!l)return null;const cs=getComputedStyle(l),lb=l.closest('label').getBoundingClientRect();const r={w:l.getBoundingClientRect().width,app:cs.appearance,acc:cs.accentColor,h:lb.height,bg0:cs.backgroundColor,chk:l.checked};l.click();r.bg1=getComputedStyle(l).backgroundColor;r.chk1=l.checked;l.click();return r}")))
        # hovers: rhythm tiles and everything with a US title
        await pg.evaluate("()=>{EAR.drill='rhy';EAR.lvl.rhy=3;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();EAR.q=earGen('rhy',3,R);EAR.q.plays=1;renderEar()}"); await pg.wait_for_timeout(600)
        if w == 1366:
            print('hovers ear rhy', json.dumps(await pg.evaluate("()=>[...new Set([...document.querySelectorAll('[title*=\"US:\"]')].map(e=>(e.textContent.trim().slice(0,18)||e.className)+' => '+e.title))]"), ensure_ascii=False, indent=0))
            for rm in ('keys', 'climbs', 'analysis', 'forms', 'gym', 'oracle', 'library'):
                try:
                    await pg.evaluate("(r)=>{location.hash=r;room(r)}", rm); await pg.wait_for_timeout(700)
                    print('hovers', rm, json.dumps(await pg.evaluate("()=>[...new Set([...document.querySelectorAll('[title*=\"US:\"]')].map(e=>(e.textContent.trim().slice(0,18)||e.className)+' => '+e.title))].slice(0,40)"), ensure_ascii=False, indent=0))
                except Exception as e: print('room', rm, 'ERR', str(e)[:100])
        # C15 piano labels, C16 song links
        await pg.evaluate("()=>{location.hash='keys';room('keys')}"); await pg.wait_for_timeout(700)
        print(w, 'piano', json.dumps(await pg.evaluate("()=>{const L=[...document.querySelectorAll('.piano .c')].filter(e=>e.offsetParent);const rs=L.map(e=>e.getBoundingClientRect());let ov=0;for(let i=1;i<rs.length;i++){}return{n:L.length,fs:[...new Set(L.map(e=>getComputedStyle(e).fontSize))],txt:L.map(e=>e.textContent).slice(0,6)}}")))
        await clip(pg, f'piano_{w}.png', '.piano', None, pad=24)
        sl = await pg.evaluate("""()=>{const o={};for(const s of ['.song .sb a','.c6h .sb a','.istart .sb a']){const L=[...document.querySelectorAll(s)].filter(e=>e.offsetParent);o[s]={n:L.length,h:[...new Set(L.map(e=>Math.round(e.getBoundingClientRect().height)))],wmin:Math.min(...L.map(e=>Math.round(e.getBoundingClientRect().width)))}}return o}""")
        print(w, 'songlinks keys', json.dumps(sl))
        for rm in ('library', 'climbs', 'forms'):
            await pg.evaluate("(r)=>{location.hash=r;room(r)}", rm); await pg.wait_for_timeout(600)
            sl = await pg.evaluate("""()=>{const o={};for(const s of ['.song .sb a','.c6h .sb a']){const L=[...document.querySelectorAll(s)].filter(e=>e.offsetParent);if(L.length)o[s]={n:L.length,h:[...new Set(L.map(e=>Math.round(e.getBoundingClientRect().height)))],wmin:Math.min(...L.map(e=>Math.round(e.getBoundingClientRect().width)))}}return o}""")
            print(w, 'songlinks', rm, json.dumps(sl))
            if sl and w == 390:
                await clip(pg, f'songlinks_{rm}_{w}.png', '.song' if '.song .sb a' in sl else '.c6h', None)
        print(w, 'page errors', errs)
        await pg.close()
    await b.close()

async def main():
    async with async_playwright() as p: await run(p)
asyncio.run(main())
