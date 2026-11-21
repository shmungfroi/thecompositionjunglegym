"""Climb 6 at 1024 and nearby: where the bar grid sits in its card. python3 tests/reports/checks/fable_c6/c6box.py TAG [REPO]"""
import sys, asyncio, pathlib, json
HERE = pathlib.Path(__file__).resolve().parent
REPO = pathlib.Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else HERE.parents[3]
sys.path.insert(0, str(HERE.parents[3] / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in [(1440, 900), (1366, 768), (1180, 800), (1024, 768), (900, 800), (800, 900), (390, 844)]:
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
            await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
            await pg.evaluate("()=>{S.level=6;location.hash='climbs';room('climbs')}"); await pg.wait_for_timeout(600)
            await pg.evaluate("()=>{CL.open=5;renderClimbs()}"); await pg.wait_for_timeout(500)
            m = await pg.evaluate("""()=>{const g=[...document.querySelectorAll('#climbDetail .bargrid')].find(x=>x.querySelector('.bar em.p5,.bar em.d5'))||document.querySelector('#climbDetail .bargrid'),r=g.getBoundingClientRect(),B=[...g.children].map(x=>x.getBoundingClientRect()),card=g.closest('.card,.panel,section,#climbDetail').getBoundingClientRect(),box=g.closest('.wheelbox');
              g.scrollIntoView({block:'center'});return{grid:[Math.round(r.left),Math.round(r.right)],bars:[Math.round(Math.min(...B.map(b=>b.left))),Math.round(Math.max(...B.map(b=>b.right)))],bw:B.slice(0,4).map(b=>Math.round(b.width)),card:[Math.round(card.left),Math.round(card.right)],inBox:!!box,boxCols:box&&getComputedStyle(box).gridTemplateColumns,docOver:document.documentElement.scrollWidth-innerWidth}}""")
            print(w, json.dumps(m))
            if w in (1024, 390): await pg.screenshot(path=str(HERE / f'{sys.argv[1]}_{w}.png'))
            await pg.close()
        await b.close()
asyncio.run(main())
