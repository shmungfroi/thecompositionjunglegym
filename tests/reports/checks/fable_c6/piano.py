"""C15: Keys piano labels at 11 px. python3 tests/reports/checks/fable_c6/piano.py"""
import sys, asyncio, pathlib, json
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in [(1440, 900), (1366, 768), (1024, 768), (390, 844)]:
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
            await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
            await pg.evaluate("()=>{location.hash='keys';room('keys')}"); await pg.wait_for_timeout(800)
            m = await pg.evaluate("""()=>{const L=[...document.querySelectorAll('.piano .c')].filter(e=>e.getClientRects().length);if(!L.length)return null;const P=L[0].closest('.piano');P.scrollIntoView({block:'center'});
              const rs=L.map(e=>{const g=document.createRange();g.selectNodeContents(e);return g.getBoundingClientRect()});let minGap=999;for(let i=1;i<rs.length;i++)minGap=Math.min(minGap,Math.round(rs[i].left-rs[i-1].right));
              const a=P.getBoundingClientRect();return{n:L.length,fs:[...new Set(L.map(e=>getComputedStyle(e).fontSize))],minGap,clip:{x:a.x+scrollX,y:a.y+scrollY,w:a.width,h:a.height},sc:P.scrollWidth>P.clientWidth,par:P.parentElement.className}}""")
            print(w, json.dumps(m))
            if m:
                c = m['clip']; await pg.screenshot(path=str(HERE / f'piano_{w}.png'), full_page=True, clip={'x': max(0, c['x'] - 6), 'y': c['y'] - 6, 'width': min(c['w'] + 12, w), 'height': c['h'] + 36})
            await pg.close()
        await b.close()
asyncio.run(main())
