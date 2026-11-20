"""Regenerate EAR23W, the balanced weights of the cadence rungs 2 and 3 (0.49 C3).
Run: python3 tests/gen_cad23_weights.py <repo dir>      (about 2 minutes; needs playwright and Chrome, like the suites)

The app lists every (mode, answer, model, key, grid point) of rungs 2 and 3 in a fixed order (earR23Index), realises each with the same
strict code the questions use (earR23Pool) and fits a weight to each (earR23Fit, deterministic). Building the pool takes about a minute in
the browser, too long to do when a student opens the drill, so the weights are stored in index.html on the line `const EAR23W=...;`.
Run this after any change to CADT[2], CADT[3], the keys, the grid, the strict rules or the voicing code, then run tests/earlab_test.py
(section C checks the tells on generated items and that the table matches the index).
"""
import sys, asyncio, pathlib, re
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1500)
        tab = await pg.evaluate("()=>{const o={};for(const l of [2,3]){const pool=earR23Pool(l);o[l]={s:earR23Enc(l,earR23Fit(l,pool)),n:pool.length,miss:pool.filter(e=>!e.ch).length}}return o}")
        await b.close()
    f = REPO / 'index.html'
    src = f.read_text(encoding='utf-8')
    line = "const EAR23W={2:'%s',3:'%s'};" % (tab['2']['s'], tab['3']['s'])
    new, n = re.subn(r"^const EAR23W=\{.*\};$", lambda m: line, src, count=1, flags=re.M)
    if n != 1:
        sys.exit('no EAR23W line found in index.html')
    f.write_text(new, encoding='utf-8')
    for l in ('2', '3'):
        print(f"rung {l}: {tab[l]['n']} entries ({tab[l]['miss']} grid points with no strict realisation, weight 0), {len(tab[l]['s'])} characters")


asyncio.run(main())
