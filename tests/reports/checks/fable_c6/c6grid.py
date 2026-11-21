"""Climb 6 bar grid at several widths (the function letter against the falling-fifth mark). python3 tests/reports/checks/fable_c6/c6grid.py [tag]"""
import sys, asyncio, pathlib, json
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness')); sys.path.insert(0, str(HERE))
import cjg
from playwright.async_api import async_playwright
TAG = sys.argv[1] if len(sys.argv) > 1 else 'c6grid'
M = """()=>{const cv=document.createElement('canvas').getContext('2d');cv.font='600 11px Outfit';return [...document.querySelectorAll('#climbDetail .bar[data-fn]')].map(b=>{const t=b.dataset.fn,w=cv.measureText(t).width+t.length,r=b.getBoundingClientRect(),L=r.right-9-w,T=r.bottom-17;let gap=99;
 const tw=document.createTreeWalker(b,NodeFilter.SHOW_TEXT);let n;while((n=tw.nextNode())){if(!n.nodeValue.trim())continue;const g=document.createRange();g.selectNodeContents(n);for(const q of g.getClientRects())if(q.bottom>T+1&&q.top<r.bottom-6)gap=Math.min(gap,Math.round(L-q.right))}
 return[t,Math.round(r.width),Math.round(r.height),gap]})}"""
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in [(1440, 900), (1366, 768), (1024, 768), (800, 900), (390, 844), (360, 780)]:
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
            await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
            await pg.evaluate("()=>{S.level=6;location.hash='climbs';room('climbs')}"); await pg.wait_for_timeout(600)
            for ci in (5, 3, 6, 10):
                await pg.evaluate("(i)=>{CL.open=i;renderClimbs()}", ci); await pg.wait_for_timeout(500)
                m = await pg.evaluate(M); print(w, 'climb', ci + 1, 'min gap', min(x[3] for x in m), json.dumps(m))
                if ci == 5:
                    r = await pg.evaluate("()=>{const e=document.querySelector('#climbDetail .bargrid');e.scrollIntoView({block:'center'});const a=e.getBoundingClientRect(),k=document.querySelector('#climbDetail .fnkey').getBoundingClientRect();return{x:a.x+scrollX,y:a.y+scrollY,w:a.width,h:k.bottom-a.y}}")
                    await pg.screenshot(path=str(HERE / f'{TAG}_{w}.png'), full_page=True, clip={'x': max(0, r['x'] - 10), 'y': r['y'] - 10, 'width': r['w'] + 20, 'height': r['h'] + 20})
            await pg.close()
        await b.close()
asyncio.run(main())
