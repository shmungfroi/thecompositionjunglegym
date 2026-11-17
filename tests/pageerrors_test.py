"""Page-error test (charter regression suite 1, plus register item P2-5).
Run: python3 tests/pageerrors_test.py <repo dir>

1. Every room, climb, form, Analysis score and Ear Lab drill at Stages 4, 5 and 6, with every Seed Bank instrument.
   In each view, every visible button in the main panel is clicked once (play buttons are stopped straight away);
   if a click navigates away, the view is reopened. Any uncaught page error fails the test.
2. P2-5: the climb 2 cantus-workshop click sequence from the score audit (cells 0,37 then 1,36), then an
   881-click seeded random run over the climb 2 note-entry grids (counterpoint and cantus workshop) across
   modes, species and positions.
"""
import sys, asyncio, json, pathlib, random
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

SC = ['chorale', 'ohaupt', 'jesu', 'k331a', 'k331d', 'k545', 'maple', 'entertainer', 'chopin7', 'chopin20']
FORMS = ['phrase', 'blues12', 'jazzblues', 'minblues', 'rhythm', 'rag', 'rondo', 'tv', 'sonata', 'sonrondo']


def views():
    V = []
    for i in ['piano', 'guitar', 'uke', 'bass']:
        V.append((f'seed/{i}', f"location.hash='seed';S.inst='{i}';room('seed')"))
    for r in ['keys', 'voice', 'oracle', 'climbs', 'forms', 'ear']:
        V.append((r, f"location.hash='{r}'"))
    V.append(('gym', "location.hash='gym';if(!P.length){for(const r of ['I','vi','ii','V','I','IV','V7','I'])document.querySelector(`[data-add=\"${r}\"]`)?.click()}"))
    for k in range(1, 14):
        V.append((f'climbs/{k}', f"location.hash='climbs/{k}'"))
    for f in FORMS:
        V.append((f'forms/{f}', f"location.hash='forms/{f}'"))
    for s in SC:
        V.append((f'analysis/{s}', f"location.hash='analysis';AN.tab='score';AN.score='{s}';room('analysis')"))
    for d in ['metre', 'rhy', 'qual', 'cad', 'bass', 'mel', 'blind']:
        V.append((f'ear/{d}', f"location.hash='ear';EAR.drill='{d}';room('ear')"))
    return V

# buttons that would leave the page, open a file dialog, download, or wipe saved work are skipped
SKIP = "[data-clback],[data-earreset],[data-export],[data-import],[download],[data-del],[data-bin],[data-wipe],#jExport,#jImport,input[type=file]"
LIST = """(skip)=>[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&!b.disabled&&!b.matches(skip)).length"""
CLICK = """([i,skip])=>{const bs=[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&!b.disabled&&!b.matches(skip));const b=bs[i];if(!b)return false;b.click();return true}"""


async def main():
    out = {'views': 0, 'clicks': 0, 'errors': [], 'p2_5': {}}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        pg.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html')
        await pg.wait_for_timeout(1500)
        for stage in (4, 5, 6):
            await pg.evaluate(f"document.querySelector('#lvl button[data-l=\"{stage}\"]').click()")
            await pg.wait_for_timeout(200)
            for name, js in views():
                await pg.evaluate(js)
                await pg.wait_for_timeout(900 if name.startswith('analysis') else 300)
                out['views'] += 1
                n = min(await pg.evaluate(LIST, SKIP), 45)
                for i in range(n):
                    before = len(errs)
                    h0 = await pg.evaluate('location.hash')
                    ok = await pg.evaluate(CLICK, [i, SKIP])
                    if not ok:
                        break
                    out['clicks'] += 1
                    await pg.wait_for_timeout(40)
                    await pg.evaluate('typeof stopAll==="function"&&stopAll()')
                    if len(errs) > before:
                        out['errors'].append({'stage': stage, 'view': name, 'button': i, 'error': errs[-1]})
                    if await pg.evaluate('location.hash') != h0:
                        await pg.evaluate(js)
                        await pg.wait_for_timeout(250)
        # ---- P2-5 ----
        await pg.evaluate("document.querySelector('#lvl button[data-l=\"6\"]').click()")
        await pg.evaluate("location.hash='climbs/2'")
        await pg.wait_for_timeout(700)
        before = len(errs)
        for k in ['0,37', '1,36']:
            await pg.evaluate("(k)=>document.querySelector(`[data-c2k=\"${k}\"]`)?.click()", k)
            await pg.wait_for_timeout(150)
        out['p2_5']['audit_sequence_errors'] = errs[before:]
        rnd = random.Random(881)
        clicks = 0
        before = len(errs)
        modes = await pg.evaluate("[...document.querySelectorAll('[data-c2m]')].map(b=>b.dataset.c2m)")
        while clicks < 881:
            if clicks % 60 == 0:
                for sel in ['[data-c2m]', '[data-c2s]', '[data-c2p]']:
                    opts = await pg.evaluate(f"[...document.querySelectorAll('{sel}')].filter(b=>b.offsetParent&&!b.disabled).length")
                    if opts:
                        await pg.evaluate(f"(i)=>[...document.querySelectorAll('{sel}')].filter(b=>b.offsetParent&&!b.disabled)[i].click()", rnd.randrange(opts))
                        await pg.wait_for_timeout(80)
            cells = await pg.evaluate("[...document.querySelectorAll('.c2ladw button.c2c,[data-c2k]')].filter(b=>b.offsetParent).length")
            if not cells:
                break
            await pg.evaluate("(i)=>[...document.querySelectorAll('.c2ladw button.c2c,[data-c2k]')].filter(b=>b.offsetParent)[i].click()", rnd.randrange(cells))
            clicks += 1
            if clicks % 10 == 0:
                await pg.wait_for_timeout(60)
        await pg.wait_for_timeout(300)
        await pg.evaluate('stopAll()')
        out['p2_5']['random_clicks'] = clicks
        out['p2_5']['random_run_errors'] = errs[before:]
        await b.close()
    out['n_errors'] = len(out['errors']) + len(out['p2_5']['audit_sequence_errors']) + len(out['p2_5']['random_run_errors'])
    ok = out['n_errors'] == 0 and out['p2_5'].get('random_clicks') == 881
    out['errors'] = out['errors'][:25]
    print(json.dumps(out, indent=1, ensure_ascii=False))
    sys.exit(0 if ok else 1)

asyncio.run(main())
