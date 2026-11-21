"""Every climb 4 example and climb 5 family: least gap between the function letter and the bar's text. python3 tests/reports/checks/fable_c6/sweep.py"""
import sys, asyncio, pathlib, json, re
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
M = re.search(r'M = """(.*?)"""', (HERE / 'c6grid.py').read_text(), re.S).group(1)
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in [(1366, 768), (1024, 768), (390, 844), (360, 780)]:
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
            await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
            await pg.evaluate("()=>{S.level=6;location.hash='climbs';room('climbs')}"); await pg.wait_for_timeout(600)
            await pg.evaluate("()=>{CL.open=3;renderClimbs()}"); await pg.wait_for_timeout(400)
            for ex in await pg.evaluate("()=>C4EX.map(x=>x.k)"):
                await pg.evaluate("(k)=>{C4.ex=k;renderClimb4()}", ex); await pg.wait_for_timeout(150)
                m = await pg.evaluate(M); g = min(x[3] for x in m)
                print(w, 'climb 4', ex, len(m), 'bars, width', m[0][1], 'min gap', g, '' if g >= 4 else '<<<', [x for x in m if x[3] < 4])
                if ex in ('blues', 'mblues') or len(m) == 12:
                    if w in (390, 1366):
                        r = await pg.evaluate("()=>{const e=document.querySelector('#climbDetail .bargrid');e.scrollIntoView({block:'center'});const a=e.getBoundingClientRect(),k=document.querySelector('#climbDetail .fnkey').getBoundingClientRect();return{x:a.x+scrollX,y:a.y+scrollY,w:a.width,h:k.bottom-a.y}}")
                        await pg.screenshot(path=str(HERE / f'climb4_{ex}_{w}.png'), full_page=True, clip={'x': max(0, r['x'] - 10), 'y': r['y'] - 10, 'width': r['w'] + 20, 'height': r['h'] + 20})
            await pg.evaluate("()=>{CL.open=4;renderClimbs()}"); await pg.wait_for_timeout(400)
            for fam in await pg.evaluate("()=>C5FAM.map(x=>x.k)"):
                for v in ('', 'pedal'):
                    await pg.evaluate("([k,v])=>{C5.fam=k;Object.keys(C5.v).forEach(x=>C5.v[x]=x===v);renderClimb5()}", [fam, v]); await pg.wait_for_timeout(150)
                    m = await pg.evaluate(M); g = min(x[3] for x in m)
                    print(w, 'climb 5', fam, v, len(m), 'bars, width', m[0][1], 'min gap', g, '' if g >= 4 else '<<<', [x for x in m if x[3] < 4])
            await pg.close()
        await b.close()
asyncio.run(main())
