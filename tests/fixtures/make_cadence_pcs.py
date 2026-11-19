"""Rebuild the cadence_pcs rows of tests/fixtures/earlab_ic.json (register 0.48, R16).
Run: python3 tests/fixtures/make_cadence_pcs.py <repo dir>

The app is asked only which models and keys each cadence rung uses (CADT, earCadKeys). The pitch classes of every chord come from
music21's Roman numerals, not from the app, so earlab_test section J compares the app's chords with an independent spelling.
Rows for models the app no longer uses are dropped; the blind rows are kept as they are.
"""
import sys, json, asyncio, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import roman, key as m21key

TON = ['C', 'D-', 'D', 'E-', 'E', 'F', 'F#', 'G', 'A-', 'A', 'B-', 'B']


def m21key_of(k, mode):
    t = TON[k % 12]
    if mode == 'min':
        t = {'D-': 'C#', 'A-': 'G#'}.get(t, t)
        return m21key.Key(t.lower())
    return m21key.Key(t)


def figure(tok):
    rn, _, inv = tok.partition(':')
    rn = rn.replace('°', 'o')
    if inv in ('1', '2'):
        if '7' in rn:
            rn = rn.replace('7', {'1': '65', '2': '43'}[inv], 1)
        else:
            base, slash, sec = rn.partition('/')
            rn = base + {'1': '6', '2': '64'}[inv] + slash + sec
    return rn


async def models():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page()
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1200)
        out = await pg.evaluate("""()=>{const o=[];for(const l of [1,2,3])for(const md in CADT[l])for(const c in CADT[l][md])for(const t of CADT[l][md][c])
            for(const k of earCadKeys(l,md))o.push({t,k,md});return o}""")
        await b.close()
    return out


def main():
    fx = REPO / 'tests' / 'fixtures' / 'earlab_ic.json'
    F = json.loads(fx.read_text())
    want = {(m['t'], m['k'], m['md']) for m in asyncio.run(models())}
    old = F.get('cadence_pcs', [])
    kept = [r for r in old if (r['t'], r['k'], r['md']) in want]
    have = {(r['t'], r['k'], r['md']) for r in kept}
    added = []
    for t, k, md in sorted(want - have, key=lambda x: (x[2], x[0], x[1])):
        kk = m21key_of(k, md)
        pcs = [sorted({p.pitchClass for p in roman.RomanNumeral(figure(tok), kk).pitches}) for tok in t.split()]
        added.append({'t': t, 'k': k, 'md': md, 'pcs': pcs, 'src': 'music21 Roman numerals (0.48 R16)'})
    F['cadence_pcs'] = kept + added
    fx.write_text(json.dumps(F, ensure_ascii=False, indent=0))
    print(f'cadence_pcs: {len(old)} rows before, {len(old) - len(kept)} dropped (models retired), {len(added)} added, {len(F["cadence_pcs"])} now')


main()
