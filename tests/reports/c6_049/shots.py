"""C6 (0.49): before/after PNGs of the function-colour changes. Run from the repo root:
  python3 tests/reports/c6_049/shots.py after  [REPO]      (REPO defaults to this checkout)
  python3 tests/reports/c6_049/shots.py before REPO_AT_049 (a checkout or `git archive` of the commit before C6)
Writes png/<tag>_<shot>_<width>.png at 1366 and 390 wide."""
import sys, asyncio, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else HERE.parents[2]
TAG = sys.argv[1]
sys.path.insert(0, str(HERE.parents[1] / 'harness'))
import cjg
from playwright.async_api import async_playwright
OUT = HERE / 'png'; OUT.mkdir(exist_ok=True)
SIZES = [(1366, 768), (390, 844)]

async def clip(pg, path, sel, below=None, pad=10):
    r = await pg.evaluate("""([s,b])=>{const e=document.querySelector(s);if(!e)return null;e.scrollIntoView({block:'center'});const a=e.getBoundingClientRect();let bt=a.bottom;
        if(b){const n=document.querySelector(b);if(n)bt=Math.max(bt,n.getBoundingClientRect().bottom)}return{x:a.x+scrollX,y:a.y+scrollY,w:a.width,h:bt-a.y}}""", [sel, below])
    print(path.name, r)
    if not r: print('MISSING', path.name, sel); return
    await pg.screenshot(path=str(path), full_page=True, clip={'x': max(0, r['x'] - pad), 'y': max(0, r['y'] - pad), 'width': r['w'] + 2 * pad, 'height': r['h'] + 2 * pad})

async def run(p):
    b = await cjg.launch(p)
    for w, h in SIZES:
        pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate("window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11);window.earPlay=()=>{}")
        # 1 a climb bar grid: climb 4 (the first grid, with the legend line under it)
        await pg.evaluate("()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='climbs';room('climbs')}")
        await pg.wait_for_timeout(700)
        await pg.evaluate("()=>{CL.open=3;renderClimbs()}"); await pg.wait_for_timeout(500)
        await clip(pg, OUT / f'{TAG}_bargrid_{w}.png', '#climbDetail .bargrid', '#climbDetail .bargrid + .fnkey')
        # 3 the circle of fifths (climb 5 loop wheel)
        await pg.evaluate("()=>{CL.open=4;renderClimbs()}"); await pg.wait_for_timeout(500)
        await clip(pg, OUT / f'{TAG}_wheel_{w}.png', '.wheelbox')
        # 2 the Analysis numeral strip
        await pg.evaluate("""()=>{K={k:9,mode:'min'};P=['i','iv','V','VII','III','VI','ii\\u00b0','i'].map(r=>({...parseRoman(r,K),inv:0,beats:4}));saveP();AN.tab='prog';location.hash='analysis';room('analysis');renderAnalysis()}""")
        await pg.wait_for_timeout(600)
        await clip(pg, OUT / f'{TAG}_numerals_{w}.png', '.clrn', '.clrn + .fnkey')
        # 4 an Ear Lab result with chord chips (bass drill, then a cadence drill)
        await pg.evaluate("()=>{S.level=6;location.hash='ear';EAR.all=false;EAR.st={};room('ear')}")
        for d, l in (('bass', 1), ('cad', 2)):
            await pg.evaluate("(a)=>{const [d,l]=a;EAR.drill=d;EAR.lvl[d]=l;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();EAR.q=earGen(EAR.drill,earLvl(),R);EAR.q.plays=1;renderEar()}", [d, l]); await pg.wait_for_timeout(300)
            await pg.evaluate("""()=>{const q=EAR.q;if(q.d==='bass')earMark(false,q.a.slice(0,-1).concat([q.opts.find(x=>x!==q.a[q.a.length-1])]));else earMark(false,(q.opts||[...document.querySelectorAll('#earMain [data-earans]')].map(x=>x.dataset.earans)).find(x=>x!==q.a));renderEar()}""")
            await pg.wait_for_timeout(500)
            await clip(pg, OUT / f'{TAG}_earlab_{d}_{w}.png', '.el-chords', '.el-chords + .fnkey', pad=14)
        await pg.close()
    await b.close()

async def main():
    async with async_playwright() as p: await run(p)
asyncio.run(main())
