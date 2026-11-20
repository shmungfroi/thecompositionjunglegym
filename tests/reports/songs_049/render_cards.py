"""Render the Dance Monkey and We Don't Talk About Bruno cards at 1366 and 390 wide, and check the 11 px floor and sideways scroll."""
import sys, asyncio, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
CARDS = [('dance-monkey', '', 'Dance Monkey'), ('bruno', 'm', "We Don't Talk About Bruno")]
async def main():
    out = HERE / 'png'; out.mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w in (1366, 390):
            pg = await b.new_page(viewport={'width': w, 'height': 900})
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.route('**/*', cjg.make_route(str(REPO)))
            await pg.goto('http://app/index.html#seed'); await pg.wait_for_timeout(1500)
            for name, q, song in CARDS:
                r = await pg.evaluate("""([q,song])=>{S.q=q;renderSongs();const c=[...document.querySelectorAll('#songs .song')].find(e=>e.querySelector('.t').textContent===song);
                  c.scrollIntoView({block:'center'});const chip=c.querySelector('.gt .nb');const fs=[...c.querySelectorAll('.gt,.gt *')].map(e=>parseFloat(getComputedStyle(e).fontSize));
                  return {label:chip&&chip.textContent,labelFont:chip&&getComputedStyle(chip).fontSize,warnStyled:!!c.querySelector('.gt .lw'),minFont:Math.min(...fs),docW:document.documentElement.scrollWidth,winW:innerWidth,cardW:c.scrollWidth,cardCW:c.clientWidth}}""", [q, song])
                el = pg.locator('#songs .song', has=pg.locator('.t', has_text=song)).first
                await el.screenshot(path=str(out / f'{name}_{w}.png'))
                print(w, song, r)
            print(w, 'page errors', errs)
            await pg.close()
        await b.close()
asyncio.run(main())
