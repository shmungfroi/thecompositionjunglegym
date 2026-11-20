"""IC_SELF_048 probe 7: rhythm tile hovers in the live Ear Lab rhythm drill (rung 3, so the syncopation tile `syn` is offered).
Run: python3 tests/reports/checks/ic_self/p4_syn_hover.py <repo>
Own expectations: each Australian value in the title is paired, in order and with repeats, with its US name
(crotchet=quarter note, quaver=eighth note, minim=half note, semiquaver=sixteenth note, rest -> rest, dotted kept, plural kept)."""
import sys, asyncio, json, pathlib, re
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright

US = {'crotchet': 'quarter note', 'quaver': 'eighth note', 'minim': 'half note', 'semiquaver': 'sixteenth note'}
def us_of(part):
    part = part.strip(); m = re.match(r'^(\d+ )?(dotted )?(crotchet|quaver|minim|semiquaver)(s?)( rest)?$', part)
    if not m: return None
    n, dot, v, pl, rest = m.groups(); u = US[v]
    if rest: u = u.replace(' note', ' rest')
    if pl: u += 's'
    return (n or '') + (dot or '') + u

async def main():
    out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(viewport={'width': 1440, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>{EAR.drill='rhy';EAR.lvl.rhy=3;EAR.q=null;EAR.ans=[];renderEar()}")
        await pg.wait_for_timeout(400)
        # start a question the way the app does, so the answer area (tiles) is drawn
        await pg.evaluate("()=>{try{EAR.q=earGen('rhy',3);EAR.done=false;EAR.ans=[];renderEar()}catch(e){}}")
        await pg.wait_for_timeout(1200)
        tiles = await pg.evaluate("()=>[...document.querySelectorAll('#earMain [data-earcell]')].map(b=>[b.dataset.earcell,b.getAttribute('title'),b.getAttribute('aria-label')])")
        out['tiles_live'] = tiles
        # hover the syn tile with the mouse; then force several more sync passes (idempotence)
        if any(t[0] == 'syn' for t in tiles):
            await pg.hover('#earMain [data-earcell="syn"]'); await pg.wait_for_timeout(300)
            out['syn_after_hover'] = await pg.evaluate("()=>document.querySelector('#earMain [data-earcell=\"syn\"]').getAttribute('title')")
            out['syn_after_5_syncs'] = await pg.evaluate("()=>{const b=document.querySelector('#earMain [data-earcell=\"syn\"]');for(let i=0;i<5;i++)termBtnSync(b);return b.getAttribute('title')}")
            # add a syn cell and re-render (tiles rebuilt), check again
            await pg.click('#earMain [data-earcell="syn"]'); await pg.wait_for_timeout(500)
            out['syn_after_click_rerender'] = await pg.evaluate("()=>{const b=document.querySelector('#earMain [data-earcell=\"syn\"]');return b?b.getAttribute('title'):null}")
        out['pageerrors'] = errs
        await b.close()
    bad = []
    for k, t, aria in out['tiles_live']:
        if not t or ' · US: ' not in t: bad.append(f'{k}: no US hover: {t!r}'); continue
        au, us = t.split(' · US: ', 1)
        au_parts, us_parts = au.split(', '), us.split(', ')
        want = [us_of(x) for x in au_parts]
        if None in want: bad.append(f'{k}: Australian part not a value name: {au!r}')
        if us_parts != want: bad.append(f'{k}: {t!r} -> expected US {", ".join(map(str, want))}')
        if aria != au: bad.append(f'{k}: aria-label {aria!r} differs from the Australian title {au!r}')
    for kk in ('syn_after_hover', 'syn_after_5_syncs', 'syn_after_click_rerender'):
        if kk in out and out[kk] != 'quaver, crotchet, quaver · US: eighth note, quarter note, eighth note': bad.append(f'{kk}: {out[kk]!r}')
    out['bad'] = bad
    print(json.dumps(out, indent=1, ensure_ascii=False))

asyncio.run(main())
