"""Regenerate EAR23W, the balanced weights of the cadence rungs 2 and 3 (0.49 C3; fitted by linear programming since 0.49 C33).
Run: python3 tests/gen_cad23_weights.py <repo dir>      (about 3 minutes; needs playwright and Chrome, like the suites, and numpy + scipy)

The app lists every (mode, answer, model, key, grid point) of rungs 2 and 3 in a fixed order (earR23Index) and realises each with the same
strict code the questions use (earR23Pool). Building the pool takes about a minute in the browser, too long to do when a student opens the
drill, so the weights are stored in index.html on the line `const EAR23W=...;` (3 base-36 characters per entry, scaled so the largest in
its mode and answer is 46655, as earR23Weights decodes them).

0.49 C33 (L108): the weights are fitted here, in each mode, by tests/cadweights_lp.py, so that every one of these features predicts the
answer as little as the pool allows (the same cap for all, the smallest that can be met, at least 3 points): the key, the opening voicing,
the first and last bass and soprano notes, the lowest note, the highest note, the two together, the span, the spacing pattern of every
chord (open or close each, earClose) and the final chord's completeness. Each answer keeps its model share (earR23Share); 10% of every
answer is the plain draw (EAR23OPT.mix), so every realisation stays in use; then the weights are moved as little as possible from the
plain draw. (Before C33 the browser's iterative fit, earR23Fit, did this; it is kept in the app as the fallback for a stale table.)
Run this after any change to CADT[2], CADT[3], the keys, the grid, the strict rules or the voicing code, then run tests/earlab_test.py
(section C checks the tells on generated items and that the table matches the index).
"""
import sys, asyncio, pathlib, re, collections
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'harness')); sys.path.insert(0, str(HERE))
import cjg, cadweights_lp as LP
from playwright.async_api import async_playwright
import numpy as np


def features(close_lt):
    lo = lambda p: min(map(min, p['ch'])); hi = lambda p: max(map(max, p['ch']))
    return {'key': lambda p: p['k'], 'opening voicing': lambda p: tuple(p['ch'][0]), 'first bass': lambda p: p['ch'][0][0],
            'first soprano': lambda p: p['ch'][0][3], 'lowest note': lo, 'highest note': hi, 'lowest and highest note': lambda p: (lo(p), hi(p)),
            'span': lambda p: hi(p) - lo(p), 'last bass': lambda p: p['ch'][-1][0], 'last soprano': lambda p: p['ch'][-1][3],
            'spacing pattern': lambda p: ''.join('c' if c[3] - c[1] < close_lt else 'o' for c in p['ch']),
            'final chord complete': lambda p: len(set(m % 12 for m in p['ch'][-1])) >= 3}


def enc(ix, w):
    mx = collections.defaultdict(float)
    for e, x in zip(ix, w):
        mx[e['md'] + e['a']] = max(mx[e['md'] + e['a']], x)
    out = []
    for e, x in zip(ix, w):
        v = round(x / mx[e['md'] + e['a']] * 46655) if mx[e['md'] + e['a']] > 0 else 0
        out.append(np.base_repr(v, 36).lower().rjust(3, '0'))
    return ''.join(out)


def fit(pool, l, share_of, mix, close_lt):
    w = np.zeros(len(pool)); report = {}
    for md in ('maj', 'min'):
        idx = [i for i, p in enumerate(pool) if p['md'] == md and p['ch']]
        P = [pool[i] for i in idx]
        answers = sorted(set(p['a'] for p in P))
        F = {k: (f, answers, 0) for k, f in features(close_lt).items()}
        share = {(p['a'], p['t']): share_of[f"{md}|{p['a']}|{p['t']}"] for p in P}
        t = LP.minimax(P, answers, F, share, list(F), mix)
        cap = max(3.0, t + .5)
        ww, _ = LP.fit(P, answers, F, share, {k: cap for k in F}, {}, mix, LP.plain(P, share))
        for j, i in enumerate(idx):
            w[i] = ww[j]
        report[md] = (t, cap, LP.tells(P, F, ww))
    return w, report


async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1500)
        d = await pg.evaluate("""()=>{const o={mix:EAR23OPT.mix,close:EAR_CLOSE_LT};for(const l of [2,3]){const pool=earR23Pool(l),sh={};
            for(const md of ['maj','min'])for(const a in CADT[l][md])for(const t of CADT[l][md][a])sh[md+'|'+a+'|'+t]=earR23Share(l,md,a,t);
            o[l]={pool:pool.map(e=>({md:e.md,a:e.a,t:e.t,k:e.k,ch:e.ch})),share:sh}}return o}""")
        await b.close()
    lines = {}
    for l in ('2', '3'):
        pool = d[l]['pool']
        w, rep = fit(pool, int(l), d[l]['share'], d['mix'], d['close'])
        lines[l] = enc(pool, w)
        miss = sum(1 for e in pool if not e['ch'])
        print(f"rung {l}: {len(pool)} entries ({miss} grid points with no strict realisation, weight 0), {len(lines[l])} characters")
        for md, (t, cap, tl) in rep.items():
            print(f"  {md}: smallest common cap {t:.2f} points, cap used {cap:.2f}; exact tells: " + ', '.join(f'{k} {v:+.1f}' for k, v in tl.items()))
    f = REPO / 'index.html'
    src = f.read_text(encoding='utf-8')
    line = "const EAR23W={2:'%s',3:'%s'};" % (lines['2'], lines['3'])
    new, n = re.subn(r"^const EAR23W=\{.*\};$", lambda m: line, src, count=1, flags=re.M)
    if n != 1:
        sys.exit('no EAR23W line found in index.html')
    f.write_text(new, encoding='utf-8')


asyncio.run(main())
