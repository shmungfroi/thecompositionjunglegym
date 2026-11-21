"""Generate EAR1W, the balanced weights of cadences rung 1 (0.49 C31, Justin 21 Nov 2026, L108).
Run: python3 tests/gen_cad1_weights.py <repo dir>      (under a minute; needs playwright and Chrome, like the suites, and numpy + scipy)

The app lists every strict rung 1 realisation once (earR1Pool; those in use with the default options, earR1Use). Before C31 the browser
fitted their weights itself (earR1Fit, iterative proportional fitting): the register, key and spacing were balanced, but the top line was
left as the fit happened to leave it (perfect ended so-so 73% of the time and re-mi 1%), so the soprano gave the answer away. C31 asks for
the soprano line (both notes and the pair) and the tenor-soprano gap of the last chord to be spread as evenly across the answers as the
strict rules allow. That needs a linear programme (tests/cadweights_lp.py), so the weights are fitted here and stored in index.html on the
line `const EAR1W='...';` (3 base-36 characters per entry in use, in earR1Pool order, scaled so the largest in each answer is 46655).

Features and their treatment (exact tells, points above chance; see cadweights_lp.py):
  register, key, spacing: first and last bass, first and last soprano note, key, lowest and highest note together, span, spacing of both
    chords (earClose, C32): each capped at 4 points (the ladder rule is 5).
  forced: the soprano degree of the first chord, of the last chord, and the soprano line (both degrees): the chords themselves differ
    (V, IV or I first; I, V or vi last), so these can never reach chance. Their floor (the least each can be on its own, from the pool)
    is computed and reported; the fit makes their excess over the floor as small as it can.
  the tenor-soprano gap (exact semitones) of the last and the first chord: made as small as possible (the last chord's counts 3 times).
  answers that share a chord: perfect vs plagal (both end on I) from the last soprano degree and the last chord's tenor-soprano gap, made
    as small as possible; perfect vs interrupted (both start on V) from the first soprano degree and gap, capped at 4 points.
Then the weights are moved as little as possible from the old fit (earR1Fit), so the voicings keep their variety. 3% of every model is
the plain draw (EARR1OPT.mix), so all strict voicings stay in use. Run this after any change to the rung 1 pool (CADT[1], the keys, the
ranges, the strict rules, EAR_CLOSE_LT), then run tests/earlab_items_test.py (section K).
"""
import sys, asyncio, pathlib, re, collections
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'harness')); sys.path.insert(0, str(HERE))
import cjg, cadweights_lp as LP
from playwright.async_api import async_playwright
import numpy as np

A = ['perfect', 'plagal', 'imperfect', 'interrupted']
SHARE = {('perfect', 'V I'): 1, ('plagal', 'IV I'): 1, ('imperfect', 'I V'): .5, ('imperfect', 'IV V'): .5, ('interrupted', 'V vi'): 1}


def features(close_lt):
    dg = lambda m, p: (m - p['k']) % 12
    lo = lambda p: min(p['ch'][0][0], p['ch'][1][0]); hi = lambda p: max(p['ch'][0][3], p['ch'][1][3])
    op = lambda c: c[3] - c[1] >= close_lt
    st = lambda c: c[3] - c[1]
    return {
        'first bass': (lambda p: p['ch'][0][0], A), 'last bass': (lambda p: p['ch'][1][0], A),
        'first soprano note': (lambda p: p['ch'][0][3], A), 'last soprano note': (lambda p: p['ch'][1][3], A), 'key': (lambda p: p['k'], A),
        'lowest and highest note': (lambda p: (lo(p), hi(p)), A), 'span': (lambda p: hi(p) - lo(p), A),
        'spacing of both chords': (lambda p: (op(p['ch'][0]), op(p['ch'][1])), A),
        'soprano degree, first chord': (lambda p: dg(p['ch'][0][3], p), A),
        'soprano degree, last chord': (lambda p: dg(p['ch'][1][3], p), A),
        'soprano line (both degrees)': (lambda p: (dg(p['ch'][0][3], p), dg(p['ch'][1][3], p)), A),
        'tenor-soprano gap, last chord': (lambda p: st(p['ch'][1]), A),
        'tenor-soprano gap, first chord': (lambda p: st(p['ch'][0]), A),
        'perfect vs plagal: last soprano degree': (lambda p: dg(p['ch'][1][3], p), ['perfect', 'plagal']),
        'perfect vs plagal: last tenor-soprano gap': (lambda p: st(p['ch'][1]), ['perfect', 'plagal']),
        'perfect vs interrupted: first soprano degree': (lambda p: dg(p['ch'][0][3], p), ['perfect', 'interrupted']),
        'perfect vs interrupted: first tenor-soprano gap': (lambda p: st(p['ch'][0]), ['perfect', 'interrupted']),
        'perfect vs plagal: last chord, exact voicing': (lambda p: tuple(p['ch'][1]), ['perfect', 'plagal']),
        'perfect vs interrupted: first chord, exact voicing': (lambda p: tuple(p['ch'][0]), ['perfect', 'interrupted']),
    }


CAPPED = ['first bass', 'last bass', 'first soprano note', 'last soprano note', 'key', 'lowest and highest note', 'span', 'spacing of both chords']
PAIRCAP = ['perfect vs interrupted: first soprano degree', 'perfect vs interrupted: first tenor-soprano gap',
           'perfect vs plagal: last soprano degree', 'perfect vs plagal: last tenor-soprano gap']
OBJ = {'soprano degree, first chord': 1, 'soprano degree, last chord': 1, 'soprano line (both degrees)': 1, 'tenor-soprano gap, last chord': 3,
       'tenor-soprano gap, first chord': 1,
       'perfect vs plagal: last chord, exact voicing': 2, 'perfect vs interrupted: first chord, exact voicing': 8}
CAP, PCAP = 4.0, 4.0


def floors(P, F, mix):
    out = {}
    for k in OBJ:
        Fk = {k: (F[k][0], F[k][1], 0)}
        out[k] = round(LP.minimax(P, F[k][1], Fk, SHARE, [k], mix), 1)
    return out


def run(P, close_lt, mix, anchor):
    F0 = features(close_lt)
    fl = floors(P, {k: (f, R, 0) for k, (f, R) in F0.items()}, mix)
    F = {k: (f, R, fl.get(k, 0)) for k, (f, R) in F0.items()}
    w, s = LP.fit(P, A, F, SHARE, {**{k: CAP for k in CAPPED}, **{k: PCAP for k in PAIRCAP}}, OBJ, mix, anchor)
    for a in A:
        ii = [i for i, p in enumerate(P) if p['a'] == a]
        w[ii] /= w[ii].sum()
    return w, fl, LP.tells(P, {k: (f, R, 0) for k, (f, R) in F0.items()}, w), LP.tells(P, {k: (f, R, 0) for k, (f, R) in F0.items()}, anchor)


def enc(P, w):
    mx = collections.defaultdict(float)
    for p, x in zip(P, w):
        mx[p['a']] = max(mx[p['a']], x)
    return ''.join(np.base_repr(round(x / mx[p['a']] * 46655), 36).lower().rjust(3, '0') for p, x in zip(P, w))


async def dump(repo):
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        await pg.route('**/*', cjg.make_route(repo))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1500)
        d = await pg.evaluate("""()=>{const F=earR1Fit(),W=new Map();for(const a in F)for(const e of F[a])W.set(e.t+'|'+e.k+'|'+JSON.stringify(e.ch),e.w);
            return{close:EAR_CLOSE_LT,mix:EARR1OPT.mix,pool:earR1Pool().filter(p=>earR1Use(p)).map(p=>({a:p.a,t:p.t,k:p.k,ch:p.ch,q:W.get(p.t+'|'+p.k+'|'+JSON.stringify(p.ch))||0}))}}""")
        await b.close()
    return d


def main():
    d = asyncio.run(dump(REPO))
    P = d['pool']
    anchor = np.array([p['q'] for p in P], float)
    for (a, t), s in SHARE.items():   # the anchor in the fit's units: each model's share
        ii = [i for i, p in enumerate(P) if p['t'] == t]
        anchor[ii] *= s / anchor[ii].sum()
    w, fl, after, before = run(P, d['close'], d['mix'], anchor)
    print(f'rung 1: {len(P)} entries in use, EAR_CLOSE_LT {d["close"]}, mix {d["mix"]}')
    print('floors (least possible on its own): ' + ', '.join(f'{k} {v:+.1f}' for k, v in fl.items()))
    for k in after:
        print(f'  {k:48s} before (earR1Fit) {before[k]:+6.1f}   after {after[k]:+6.1f}')
    for t in ('V I', 'IV I', 'I V', 'IV V', 'V vi'):
        v = np.array([w[i] for i, p in enumerate(P) if p['t'] == t]); v = v / v.sum()
        print(f'  {t}: {len(v)} voicings, all with weight > 0: {bool((v > 0).all())}, effective number {1 / (v * v).sum():.0f}')
    f = REPO / 'index.html'
    src = f.read_text(encoding='utf-8')
    line = "const EAR1W='%s';" % enc(P, w)
    new, n = re.subn(r"^const EAR1W='.*';$", lambda m: line, src, count=1, flags=re.M)
    if n != 1:
        sys.exit('no EAR1W line found in index.html')
    f.write_text(new, encoding='utf-8')


if __name__ == '__main__':
    main()
