"""0.50 UI screenshots and sideways-scroll check (self-check, not a pass/fail suite on looks).
Run: python3 tests/ui_shots_050.py <repo dir>
For 1440, 1366x768, 1280x800, 1024, 820 and 390: the top bar, the level list open (popover over 760 px, More sheet at or under it),
the Chord Library and Forms pages; writes PNGs to tests/reports/ui_050/ and reports sideways scroll (document wider than the window)
and any element in the top bar that overflows it. One browser, one page at a time.
"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

SIZES = [(1440, 900), (1366, 768), (1280, 800), (1024, 768), (820, 1180), (390, 844)]
OUT = REPO / 'tests' / 'reports' / 'ui_050'


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rep = []
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in SIZES:
            ctx = await b.new_context(viewport={'width': w, 'height': h})
            await ctx.route('**/*', cjg.make_route(REPO))
            pg = await ctx.new_page()
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://app/index.html')
            await pg.wait_for_timeout(900)
            row = {'w': w, 'h': h}
            row['top'] = await pg.evaluate("""()=>{const t=document.querySelector('.top'),r=t.getBoundingClientRect(),s=document.querySelector('.search').getBoundingClientRect(),
              over=[...t.children].filter(c=>c.offsetParent&&c.getBoundingClientRect().right>r.right+0.5).map(c=>c.className||c.id);
              return{height:Math.round(r.height),search:Math.round(s.width),overflowing:over,level:document.getElementById('lvBtn').getBoundingClientRect().width|0,
              lvTextShown:getComputedStyle(document.querySelector('.lvbtn-t')).display!=='none',journalText:getComputedStyle(document.querySelector('.jbtn .jt')).display!=='none'}}""")
            await pg.screenshot(path=str(OUT / f'topbar_{w}.png'), clip={'x': 0, 'y': 0, 'width': w, 'height': 120 if w <= 760 else 70})
            # level list open
            await pg.click('#lvBtn')
            await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(OUT / f'levellist_{w}.png'))
            row['list'] = await pg.evaluate("""()=>{const box=document.getElementById('lvPop').offsetParent?document.getElementById('lvPop'):document.getElementById('msLvl'),r=box.getBoundingClientRect();
              return{where:box.id,left:Math.round(r.left),right:Math.round(r.right),top:Math.round(r.top),bottom:Math.round(r.bottom),inWindow:r.left>=0&&r.right<=innerWidth,
              rows:[...box.querySelectorAll('.lvopt')].map(o=>Math.round(o.getBoundingClientRect().height)),
              clipped:[...box.querySelectorAll('.lvd')].filter(d=>d.scrollWidth>d.clientWidth+1).length}}""")
            await pg.keyboard.press('Escape')
            if w <= 760:
                await pg.evaluate("document.getElementById('msheet').hidden=true")
            await pg.wait_for_timeout(150)
            for name, js in (('library', "location.hash='seed'"), ('forms', "location.hash='forms'")):
                await pg.evaluate(js)
                await pg.wait_for_timeout(500)
                await pg.screenshot(path=str(OUT / f'{name}_{w}.png'))
                row[name + '_scroll'] = await pg.evaluate("[document.documentElement.scrollWidth,innerWidth]")
            row['sideways'] = any(row[k][0] > row[k][1] for k in ('library_scroll', 'forms_scroll'))
            row['errors'] = errs
            rep.append(row)
            await ctx.close()
        await b.close()
    print(json.dumps(rep, indent=1))
    bad = [r for r in rep if r['sideways'] or r['errors'] or r['top']['overflowing'] or not r['list']['inWindow']]
    sys.exit(1 if bad else 0)

asyncio.run(main())
