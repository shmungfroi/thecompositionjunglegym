"""IC_SELF_048 probe 1-3: Ear Lab cadence rung 1 (imperfect I–V / IV–V share, incomplete tonic, RUNG1_SOP_BALANCE).
Run: python3 tests/reports/checks/ic_self/p1_rung1.py <repo>
Own checker (no app rules reused): music21 for chord identity, own arithmetic for voice leading."""
import sys, asyncio, json, pathlib, collections
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import chord as m21chord, roman, key as m21key, pitch as m21pitch

N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
RNG = "(seed)=>{let s=seed;return ()=>{s=(s*16807)%2147483647;return s/2147483647}}"
NM = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
RANGES = [(40, 60), (48, 67), (55, 74), (60, 79)]  # B T A S (wide textbook limits: E2-C4, C3-G4, G3-D5, C4-G5)
DEG = {'I': (0, [0, 4, 7]), 'IV': (5, [5, 9, 0]), 'V': (7, [7, 11, 2]), 'vi': (9, [9, 0, 4])}

def check_pair(k, rns, P, N_):
    E = []
    LN = (k + 11) % 12
    for v, rn, nm in ((P, rns[0], 'c1'), (N_, rns[1], 'c2')):
        root, pcs = DEG[rn]; pcs = [(k + x) % 12 for x in pcs]
        vp = [m % 12 for m in v]
        if any(p not in pcs for p in vp): E.append(f'{nm} non-chord tone')
        if v[0] % 12 != pcs[0]: E.append(f'{nm} not root position')
        if vp.count(pcs[1]) == 0: E.append(f'{nm} no 3rd')
        if not all(v[i] <= v[i + 1] for i in range(3)): E.append(f'{nm} crossing')
        if v[3] - v[2] > 12 or v[2] - v[1] > 12: E.append(f'{nm} spacing')
        for i, (lo, hi) in enumerate(RANGES):
            if not lo <= v[i] <= hi: E.append(f'{nm} range v{i} {v[i]}')
        if rn == 'V' and vp.count(LN) > 1: E.append(f'{nm} doubled LN')
        incomplete = len(set(vp)) < 3
        if incomplete and not (nm == 'c2' and rns == ['V', 'I']): E.append(f'{nm} incomplete outside V-I final')
        if incomplete and not (vp.count(pcs[0]) == 3 and vp.count(pcs[1]) == 1): E.append(f'{nm} incomplete not root x3 + 3rd')
        # music21 identity
        # transpose to C so music21's own spelling of the MIDI notes cannot mislead the key
        ch = m21chord.Chord([m21pitch.Pitch(midi=m - k) for m in v])
        rnm = roman.romanNumeralFromChord(ch, m21key.Key('C'))
        if rnm.romanNumeral != rn or rnm.inversion() != 0: E.append(f'{nm} music21 says {rnm.figure}')
    # motion
    for i in range(4):
        mv = abs(N_[i] - P[i])
        if mv > 12 or mv in (6, 10, 11): E.append(f'leap {mv} v{i}')
    for i in range(3):
        if N_[i] > P[i + 1] or N_[i + 1] < P[i]: E.append(f'overlap v{i}/v{i+1}')
    for a in range(4):
        for b in range(a + 1, 4):
            i1, i2 = (P[b] - P[a]) % 12, (N_[b] - N_[a]) % 12
            if i1 == i2 and i1 in (0, 7) and P[a] != N_[a] and P[b] != N_[b]:
                E.append(f'consecutive {"8ve/uni" if i1 == 0 else "5th"} v{a}-v{b}' + (' (contrary)' if (N_[a]-P[a])*(N_[b]-P[b]) < 0 else ''))
    io = (N_[3] - N_[0]) % 12
    if io in (0, 7) and (N_[0] - P[0]) * (N_[3] - P[3]) > 0 and abs(N_[3] - P[3]) > 2:
        E.append('hidden 5th/8ve outer voices (soprano leaps)')
    if rns[0] == 'V':
        for i in range(4):
            if P[i] % 12 == LN:
                if i in (0, 3) and N_[i] - P[i] != 1: E.append(f'LN in outer v{i} does not rise')
                if i in (1, 2) and N_[i] - P[i] != 1 and not (rns[1] == 'I' and N_[i] % 12 == (k + 7) % 12 and P[i] - N_[i] in (3, 4)):
                    E.append(f'inner LN v{i} neither rises nor falls to 5th')
                if rns[1] == 'vi' and N_[i] - P[i] != 1: E.append('LN does not rise in V-vi')
    return E

async def main():
    out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1500)
        info = await pg.evaluate("()=>({sop:RUNG1_SOP_BALANCE,opt:EARR1OPT})")
        out['switches'] = info
        res = {}
        for state in (False, True):
            r = await pg.evaluate("""([mk,st,n])=>{RUNG1_SOP_BALANCE=st;const R=eval(mk)(st?71:53),o=[];
              const chk=q=>withKey(q.key,()=>checkSATB(q.ch,cadList(q.rns.join(' '),q.key))).filter(e=>e.sev!=='info').map(e=>e.rule);
              for(let i=0;i<n;i++){const q=earGen('cad',1,R);o.push({a:q.a,rns:q.rns,k:q.key.k,ch:q.ch,app:q.ch?chk(q):['none']})}
              const W=earR1Weights(),share={};for(const a in W){share[a]={};for(const e of W[a])share[a][e.t]=(share[a][e.t]||0)+e.w}
              const pool=earR1Pool().map(p=>({t:p.t,k:p.k,ch:p.ch,inc:!!p.inc}));RUNG1_SOP_BALANCE=false;return {o,share,pool}}""", [RNG, state, N])
            res[state] = r
        out['pageerrors'] = errs
        await b.close()

    rep = {'switch_defaults': info, 'pageerrors': errs}
    pool = res[False]['pool']
    rep['pool_total'] = len(pool); rep['pool_inc'] = sum(p['inc'] for p in pool)
    rep['pool_by_model'] = collections.Counter(p['t'] for p in pool)
    rep['pool_inc_models'] = collections.Counter(p['t'] for p in pool if p['inc'])
    perr = collections.Counter()
    for p in pool:
        for e in check_pair(p['k'], p['t'].split(), *p['ch']): perr[(p['inc'], e)] += 1
    rep['pool_errors'] = {f'{k[0]}|{k[1]}': v for k, v in perr.items()}
    for state in (False, True):
        o = res[state]['o']; tag = 'sop_on' if state else 'sop_off'
        S = {}
        S['answers'] = collections.Counter(x['a'] for x in o)
        imp = [x for x in o if x['a'] == 'imperfect']
        S['imperfect_forms'] = collections.Counter(' '.join(x['rns']) for x in imp)
        S['weights_share'] = res[state]['share']
        first = collections.defaultdict(collections.Counter)
        for x in o: first[x['rns'][0]][x['a']] += 1
        S['first_chord_to_answer'] = {k: dict(v) for k, v in first.items()}
        last = collections.defaultdict(collections.Counter)
        for x in o: last[x['rns'][1]][x['a']] += 1
        S['last_chord_to_answer'] = {k: dict(v) for k, v in last.items()}
        perf = [x for x in o if x['a'] == 'perfect']
        inc = [x for x in perf if len({m % 12 for m in x['ch'][1]}) < 3]
        S['perfect_items'] = len(perf); S['perfect_incomplete_items'] = len(inc)
        S['distinct_perfect_voicings'] = len({json.dumps(x['ch']) + str(x['k']) for x in perf})
        S['distinct_incomplete_voicings'] = len({json.dumps(x['ch']) + str(x['k']) for x in inc})
        E = collections.Counter(); app = collections.Counter(); bad_ex = []
        for x in o:
            if not x['ch']: E['no realisation'] += 1; continue
            ee = check_pair(x['k'], x['rns'], *x['ch'])
            for e in ee: E[e] += 1
            if ee and len(bad_ex) < 5: bad_ex.append({'x': x, 'e': ee})
            for e in x['app']: app[e] += 1
        S['own_checker_errors'] = dict(E); S['own_checker_examples'] = bad_ex; S['app_checker_nonInfo'] = dict(app)
        # predictiveness of answer from register / surface features (held-out, chance = most common)
        def pred(feat):
            half = [o[0::2], o[1::2]]; hit = 0
            for tr, te in ((half[0], half[1]), (half[1], half[0])):
                by = collections.defaultdict(collections.Counter); tot = collections.Counter(x['a'] for x in tr)
                for x in tr: by[feat(x)][x['a']] += 1
                d = tot.most_common(1)[0][0]
                for x in te:
                    c = by.get(feat(x)); hit += (c.most_common(1)[0][0] if c else d) == x['a']
            return round(hit / len(o), 3)
        lo = lambda x: min(x['ch'][0][0], x['ch'][1][0]); hi = lambda x: max(x['ch'][0][3], x['ch'][1][3])
        S['predict'] = {
            'chance': round(max(S['answers'].values()) / len(o), 3),
            'lo+hi': pred(lambda x: (lo(x), hi(x))), 'span': pred(lambda x: hi(x) - lo(x)), 'key': pred(lambda x: x['k']),
            'first bass': pred(lambda x: x['ch'][0][0]), 'last soprano': pred(lambda x: x['ch'][1][3]),
            'soprano path (solfa)': pred(lambda x: ((x['ch'][0][3] - x['k']) % 12, (x['ch'][1][3] - x['k']) % 12)),
            'incomplete final chord': pred(lambda x: len({m % 12 for m in x['ch'][1]}) < 3),
        }
        # within imperfect, does register tell I-V from IV-V?
        def pred_form(feat):
            half = [imp[0::2], imp[1::2]]; hit = 0
            f = lambda x: x['rns'][0]
            for tr, te in ((half[0], half[1]), (half[1], half[0])):
                by = collections.defaultdict(collections.Counter); tot = collections.Counter(f(x) for x in tr)
                for x in tr: by[feat(x)][f(x)] += 1
                d = tot.most_common(1)[0][0]
                for x in te:
                    c = by.get(feat(x)); hit += (c.most_common(1)[0][0] if c else d) == f(x)
            return round(hit / len(imp), 3)
        S['imperfect_form_predict'] = {'lo+hi': pred_form(lambda x: (lo(x), hi(x))), 'span': pred_form(lambda x: hi(x) - lo(x)),
                                       'last soprano': pred_form(lambda x: x['ch'][1][3])}
        rep[tag] = S
    print(json.dumps(rep, indent=1, default=str))

asyncio.run(main())
