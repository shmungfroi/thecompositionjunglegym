"""Ear Lab item generation and scoring (register 0.48: R4, EL-6, EL-7, EL-10, EL-11, R16).
Run: python3 tests/earlab_items_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

The app generates the questions; this file checks them with its own rules (music21 for chord spelling, its own interval
and voice-leading arithmetic), and asks the app's SATB checker only where the register says "passes the SATB checker".

Sections
  Q  EL-6  chord quality: root position only at rungs 1-3, >= 1,000 seeded items per rung, spacing, two registers, register tell,
           augmented and diminished 7th answers name no inversion and say the chord is symmetrical
  K  EL-7  cadences rung 1: four basic cadences, two chords after the key chord, open voicing, SATB checker, balance, tells
  S  R4    cadences rung 3: six answers, family feedback, SATB checker, mode tell, the 6/4 bass motion, >= 100 distinct items per answer
  M  EL-10 stats model (unit) and a scoring flow in the page
  U  EL-11 rung wording, Stage switch, show all, Stage tags, rung change mid-question, page errors at Stages 4, 5, 6
"""
import sys, asyncio, json, pathlib, collections

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import roman, key as m21key, harmony

FAIL = collections.defaultdict(list)
COUNT = collections.Counter()
def fail(sec, msg):
    FAIL[sec].append(msg)

RNG = """(seed)=>{let s=seed;return ()=>{s=(s*16807)%2147483647;return s/2147483647}}"""
NM = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def predict_acc(rows, feat, ans):
    """Held-out accuracy of the best guess of `ans` from `feat` alone (fit on one half, scored on the other, both ways),
    and chance (the most common answer)."""
    half = [rows[0::2], rows[1::2]]
    hit = 0
    for tr, te in ((half[0], half[1]), (half[1], half[0])):
        by = collections.defaultdict(collections.Counter)
        tot = collections.Counter(ans(r) for r in tr)
        for r in tr:
            by[feat(r)][ans(r)] += 1
        default = tot.most_common(1)[0][0]
        for r in te:
            c = by.get(feat(r))
            hit += (c.most_common(1)[0][0] if c else default) == ans(r)
    tot = collections.Counter(ans(r) for r in rows)
    return hit / len(rows), tot.most_common(1)[0][1] / len(rows)


MARGIN = 0.05
def tell(sec, rows, name, feat, ans, where):
    acc, ch = predict_acc(rows, feat, ans)
    COUNT['tell checks'] += 1
    if acc > ch + MARGIN:
        fail(sec, f'{where}: {name} predicts the answer {acc:.0%} of the time (chance {ch:.0%})')


# chord-symbol suffixes for music21 (independent spelling of the chord the app should play)
M21Q = {'': '', 'm': 'm', 'dim': 'dim', 'aug': '+', 'maj7': 'maj7', '7': '7', 'm7': 'm7', 'm7b5': 'm7b5', 'dim7': 'dim7'}


def sec_Q(qual):
    for l in (1, 2, 3):
        rows = [q for q in qual if q['l'] == l]
        COUNT[f'EL-6 chord quality rung {l} items'] = len(rows)
        if len(rows) < 1000:
            fail('Q', f'rung {l}: only {len(rows)} items checked')
        regs = collections.Counter()
        for q in rows:
            where = f"rung {l} {q['a'] or 'maj'} on {q['root']} {q['notes']}"
            if q['inv'] != 0:
                fail('Q', f'{where}: inversion {q["inv"]}')
            cs = harmony.ChordSymbol(q['root'].replace('b', '-') + M21Q[q['a']])
            want = [p.pitchClass for p in cs.pitches]  # root position, in stacking order
            n = q['notes']
            if [m % 12 for m in n] != want:
                fail('Q', f'{where}: notes {[NM[m % 12] for m in n]} are not {cs.figure} in root position')
            if any(b - a >= 12 or b <= a for a, b in zip(n, n[1:])) or n[-1] - n[0] >= 12:
                fail('Q', f'{where}: not in close position')
            lo = n[0]
            if not (49 <= lo <= 60 or 61 <= lo <= 72):
                fail('Q', f'{where}: lowest note {lo} outside the two registers')
            regs[0 if lo <= 60 else 1] += 1
            txt = q['txt']
            if q['a'] in ('aug', 'dim7'):
                if 'symmetrical' not in txt or any(w in txt for w in ('1st inversion', '2nd inversion', '3rd inversion', 'root position,')):
                    fail('Q', f'{where}: answer text "{txt}" names an inversion or does not say the chord is symmetrical')
            elif 'root position' not in txt:
                fail('Q', f'{where}: answer text "{txt}" does not say root position')
        if min(regs.values()) < len(rows) * .4:
            fail('Q', f'rung {l}: registers unbalanced {dict(regs)}')
        tell('Q', rows, 'lowest note (6-semitone bands)', lambda r: r['notes'][0] // 6, lambda r: r['a'], f'chord quality rung {l}')
        tell('Q', rows, 'lowest note', lambda r: r['notes'][0], lambda r: r['a'], f'chord quality rung {l}')
        tell('Q', rows, 'highest note (6-semitone bands)', lambda r: r['notes'][-1] // 6, lambda r: r['a'], f'chord quality rung {l}')


TON = ['C', 'D-', 'D', 'E-', 'E', 'F', 'F#', 'G', 'A-', 'A', 'B-', 'B']


def m21key_of(k, mode):
    t = TON[k % 12]
    if mode == 'min':
        t = {'D-': 'C#', 'A-': 'G#', 'G-': 'F#'}.get(t, t)
        return m21key.Key(t.lower())
    return m21key.Key(t)


def figure(tok):
    """'ii°:1' -> 'iio6', 'I:2' -> 'I64', 'V7' -> 'V7', 'V7/V' -> 'V7/V'"""
    rn, _, inv = tok.partition(':')
    rn = rn.replace('°', 'o')
    if inv in ('1', '2'):
        if '7' in rn:
            rn = rn.replace('7', {'1': '65', '2': '43'}[inv], 1)
        else:
            base, slash, sec = rn.partition('/')
            rn = base + {'1': '6', '2': '64'}[inv] + slash + sec
    return rn


def rn_info(tok, k, mode):
    r = roman.RomanNumeral(figure(tok), m21key_of(k, mode))
    return dict(pcs={p.pitchClass for p in r.pitches}, root=r.root().pitchClass, bass=r.bass().pitchClass,
                third=r.third.pitchClass if r.third is not None else None,
                seventh=r.seventh.pitchClass if r.seventh is not None else None,
                sd=r.scaleDegree, secondary=r.secondaryRomanNumeral is not None, inv=r.inversion(), figure=r.figure)


def vl_errors(chs, toks, k, mode):
    """Independent strict-SATB rules (the same rules as earlab_test section A). chs: list of [B,T,A,S] MIDI numbers."""
    out = []
    tonic = k % 12
    lt = (tonic + 11) % 12
    info = [rn_info(t, k, mode) for t in toks]
    RANGES = [(40, 60), (48, 67), (55, 74), (60, 79)]
    for i, (c, f) in enumerate(zip(chs, info)):
        pcs = {m % 12 for m in c}
        if not pcs <= f['pcs']:
            out.append(f'chord {i+1} {toks[i]} has notes outside {f["figure"]}')
        need = {f['root'], f['third']} | ({f['seventh']} if f['seventh'] is not None else set())
        if not need <= pcs:
            out.append(f'chord {i+1} {toks[i]} is missing its root, 3rd or 7th')
        if c[0] % 12 != f['bass']:
            out.append(f'chord {i+1} {toks[i]} bass {NM[c[0] % 12]} should be {NM[f["bass"]]}')
        for v, (lo, hi) in enumerate(RANGES):
            if not lo <= c[v] <= hi:
                out.append(f'chord {i+1} voice {v} {c[v]} outside {lo}-{hi}')
        if any(c[v] > c[v + 1] for v in range(3)):
            out.append(f'chord {i+1} voices cross')
        if c[3] - c[2] > 12 or c[2] - c[1] > 12:
            out.append(f'chord {i+1} upper voices more than an octave apart')
        if f['sd'] == 5 and not f['secondary'] and sum(1 for m in c if m % 12 == lt) > 1:
            out.append(f'chord {i+1} doubles the leading note')
    for i in range(len(chs) - 1):
        P, N, f0, f1 = chs[i], chs[i + 1], info[i], info[i + 1]
        for a in range(4):
            for b in range(a + 1, 4):
                i0, i1 = (P[b] - P[a]) % 12, (N[b] - N[a]) % 12
                da, db = N[a] - P[a], N[b] - P[b]
                if i0 in (0, 7) and i0 == i1 and da != 0 and db != 0:
                    out.append(f'consecutive {"5ths" if i0 == 7 else "8ves"} voices {a},{b} chords {i+1}-{i+2}')
        if f0['seventh'] is not None:
            for v in range(4):
                if P[v] % 12 == f0['seventh'] and N[v] - P[v] not in (-1, -2):
                    out.append(f'7th of {toks[i]} in voice {v} moves {N[v]-P[v]}')
        dom = f0['sd'] == 5 and not f0['secondary']
        if dom and f1['sd'] in (1, 6) and not f1['secondary']:
            for v in (0, 3):
                if P[v] % 12 == lt and N[v] - P[v] != 1:
                    out.append(f'leading note in voice {v} does not rise ({toks[i]}-{toks[i+1]})')
            if f1['sd'] == 6 and sum(1 for m in N if m % 12 == f1['third']) != 2:
                out.append(f'{toks[i+1]} after V does not double its 3rd')
        # cadential 6/4: the 6th and 4th above the bass fall by step
        if f0['sd'] == 1 and f0['inv'] == 2 and f1['sd'] == 5:
            for v in (1, 2, 3):
                if P[v] % 12 in (f0['root'], f0['third']) and N[v] - P[v] not in (-1, -2) and not (f1['seventh'] is not None and N[v] % 12 == f1['seventh']):
                    out.append(f'cadential 6/4: voice {v} does not fall by step')
        for v in range(4):
            if abs(N[v] - P[v]) == 3 and mode == 'min' and {P[v] % 12, N[v] % 12} == {(tonic + 8) % 12, lt}:
                out.append(f'augmented 2nd in voice {v}')
            if abs(N[v] - P[v]) > 12:
                out.append(f'voice {v} leaps more than an octave')
    return out


def cad_ok(cat, toks, k, mode):
    """Does the progression end with this cadence? (independent of the app; music21 numerals)"""
    f = [rn_info(t, k, mode) for t in toks]
    sd = [x['sd'] for x in f]
    last_root = f[-1]['inv'] == 0
    if cat == 'perfect':
        return sd[-2:] == [5, 1] and last_root and f[-2]['inv'] == 0 and not (len(f) > 2 and sd[-3] == 1 and f[-3]['inv'] == 2)
    if cat == 'plagal':
        return sd[-2:] == [4, 1] and last_root
    if cat == 'imperfect':
        return sd[-1] == 5 and last_root and not f[-1]['secondary'] and not (mode == 'min' and sd[-2] == 4 and f[-2]['inv'] == 1) \
            and not (sd[-2] == 1 and f[-2]['inv'] == 2)
    if cat == 'interrupted':
        return sd[-2:] == [5, 6] and not f[-1]['secondary']
    if cat == 'phrygian':
        return mode == 'min' and toks[-2] == 'iv:1' and sd[-1] == 5 and last_root
    if cat == 'cad64':
        return len(f) >= 3 and sd[-3:] == [1, 5, 1] and f[-3]['inv'] == 2 and f[-2]['inv'] == 0 and last_root
    return False


def sec_K(items, real):
    COUNT['EL-7 rung 1 items'] = len(items)
    if len(items) < 1000:
        fail('K', f'only {len(items)} rung 1 items checked')
    cats = collections.Counter(q['a'] for q in items)
    if set(cats) != {'perfect', 'plagal', 'imperfect', 'interrupted'}:
        fail('K', f'rung 1 answers are {sorted(cats)}, not the four basic cadences')
    for c, n in cats.items():
        COUNT[f'EL-7 rung 1 answer {c}'] = n
        if abs(n / len(items) - .25) > .03:
            fail('K', f'rung 1 answers unbalanced: {dict(cats)}')
    allowed = {'perfect': [['V', 'I']], 'plagal': [['IV', 'I']], 'imperfect': [['I', 'V'], ['IV', 'V']], 'interrupted': [['V', 'vi']]}
    distinct = collections.defaultdict(set)
    for q in items + real:
        where = f"rung 1 {q['a']} [{' '.join(q['rns'])}] in {NM[q['k']]} {q['md']}"
        if q['md'] != 'maj':
            fail('K', f'{where}: not a major key')
        if q['rns'] not in allowed[q['a']]:
            fail('K', f'{where}: not one of the basic models for {q["a"]}')
        if not q['ch'] or len(q['ch']) != 2:
            fail('K', f'{where}: {len(q["ch"] or [])} chords after the key chord, not 2')
            continue
        if not q.get('cue_ok', True):
            fail('K', f'{where}: the key chord does not play first')
        for c in q['ch']:
            if c[3] - c[1] <= 12:
                fail('K', f'{where}: chord {c} is not in open spacing (soprano {c[3]}, tenor {c[1]})')
        if q['app']:
            fail('K', f'{where}: app SATB checker reports {q["app"]}')
        for e in vl_errors(q['ch'], q['rns'], q['k'], 'maj'):
            fail('K', f'{where}: {e}')
        if not cad_ok(q['a'], q['rns'], q['k'], 'maj'):
            fail('K', f'{where}: does not end with a {q["a"]} cadence')
        distinct[q['a']].add((tuple(q['rns']), q['k'], json.dumps(q['ch'])))
    for c, v in distinct.items():
        COUNT[f'EL-7 rung 1 distinct items {c}'] = len(v)
    W = 'cadences rung 1'
    A = lambda r: r['a']
    tell('K', items, 'lowest note (6-semitone bands)', lambda r: min(map(min, r['ch'])) // 6, A, W)
    tell('K', items, 'highest note (6-semitone bands)', lambda r: max(map(max, r['ch'])) // 6, A, W)
    tell('K', items, 'register drawn (bass, soprano)', lambda r: (r['reg']['b'], r['reg']['s']), A, W)
    tell('K', items, 'top note of the first chord', lambda r: r['ch'][0][3], A, W)
    tell('K', items, 'top note of the last chord', lambda r: r['ch'][-1][3], A, W)
    tell('K', items, 'highest top note', lambda r: max(c[3] for c in r['ch']), A, W)
    tell('K', items, 'bass note of the first chord', lambda r: r['ch'][0][0], A, W)
    tell('K', items, 'bass note of the last chord', lambda r: r['ch'][-1][0], A, W)
    tell('K', items, 'lowest bass note', lambda r: min(c[0] for c in r['ch']), A, W)
    tell('K', items, 'key', lambda r: r['k'], A, W)


SIX = ['perfect', 'plagal', 'imperfect', 'interrupted', 'phrygian', 'cad64']


def bass_degrees(q):
    return tuple((c[0] - q['k']) % 12 for c in q['ch'])


# ---- strict SATB rules for cadences rung 3, after the independent theory check (0.48, checks/ic/vl.py); errors only ----
VL_Q = {'maj': [0, 4, 7], 'min': [0, 3, 7], 'dim': [0, 3, 6], 'dom7': [0, 4, 7, 10]}
VL_RN = {'maj': {'I': (0, 'maj'), 'ii': (2, 'min'), 'iii': (4, 'min'), 'IV': (5, 'maj'), 'V': (7, 'maj'), 'V7': (7, 'dom7'), 'vi': (9, 'min'), 'V7/V': (2, 'dom7')},
         'min': {'i': (0, 'min'), 'ii°': (2, 'dim'), 'III': (3, 'maj'), 'iv': (5, 'min'), 'V': (7, 'maj'), 'V7': (7, 'dom7'), 'VI': (8, 'maj')}}
VL_RANGE = {0: (40, 62), 1: (48, 67), 2: (55, 74), 3: (60, 79)}


def vl_chord(rn, k, md):
    inv = 0
    if ':' in rn:
        rn, inv = rn.split(':'); inv = int(inv)
    r, q = VL_RN[md][rn]; root = (k + r) % 12
    t = [(root + i) % 12 for i in VL_Q[q]]
    return dict(rn=rn, inv=inv, root=root, q=q, tones=t, bass=t[inv], third=t[1], fifth=t[2], sev=t[3] if len(t) > 3 else None)


def ic_errors(q):
    """Strict errors in one cadence item (q: k, md, rns, ch). Mirrors the independent checker's error rules."""
    E = []; k, md = q['k'], q['md']; LN = (k + 11) % 12
    C = [vl_chord(x, k, md) for x in q['rns']]; V = q['ch']
    for i, (c, v) in enumerate(zip(C, V)):
        pcs = [m % 12 for m in v]
        if not set(pcs) <= set(c['tones']): E.append(f'ch{i} {c["rn"]}: foreign note')
        if v[0] % 12 != c['bass']: E.append(f'ch{i} {c["rn"]}: wrong bass')
        for nm in ('third', 'root'):
            if c[nm] not in pcs: E.append(f'ch{i} {c["rn"]}: no {nm}')
        if c['sev'] is not None and c['sev'] not in pcs: E.append(f'ch{i} {c["rn"]}: no 7th')
        for j in range(4):
            lo, hi = VL_RANGE[j]
            if not lo <= v[j] <= hi: E.append(f'ch{i} voice {j} out of range')
        for j in range(3):
            if v[j] > v[j + 1]: E.append(f'ch{i} crossing')
        if v[3] - v[2] > 12 or v[2] - v[1] > 12: E.append(f'ch{i} upper-voice gap')
        if c['rn'] in ('V', 'V7') and pcs.count(LN) > 1: E.append(f'ch{i} doubled leading note')
        if c['rn'] == 'V7/V' and pcs.count((c['root'] + 4) % 12) > 1: E.append(f'ch{i} V7/V doubled its leading note')
        if c['inv'] == 2 and pcs.count(c['bass']) < 2: E.append(f'ch{i} 6/4 without doubled bass')
        if c['sev'] is not None and pcs.count(c['sev']) > 1: E.append(f'ch{i} doubled 7th')
    for i in range(1, len(V)):
        P, N, cp, cn = V[i - 1], V[i], C[i - 1], C[i]
        for j in range(4):
            mv = abs(N[j] - P[j])
            if mv > 12 or mv in (10, 11): E.append(f'{i}: voice {j} leaps {mv}')
            if md == 'min' and mv == 3 and {P[j] % 12, N[j] % 12} == {(k + 8) % 12, (k + 11) % 12}: E.append(f'{i}: augmented 2nd')
        for j in range(3):
            if N[j] > P[j + 1] or N[j + 1] < P[j]: E.append(f'{i}: overlap')
        for a in range(4):
            for b in range(a + 1, 4):
                if P[a] == N[a] and P[b] == N[b]: continue
                i1, i2 = (P[b] - P[a]) % 12, (N[b] - N[a]) % 12
                if i1 == i2 and i1 in (0, 7) and P[a] != N[a] and P[b] != N[b]: E.append(f'{i}: consecutive 5ths/8ves')
        io = (N[3] - N[0]) % 12
        if io in (0, 7) and (N[0] - P[0]) * (N[3] - P[3]) > 0 and abs(N[3] - P[3]) > 2: E.append(f'{i}: hidden 5th/8ve')
        if cp['rn'] in ('V', 'V7') and cn['rn'] in ('I', 'i', 'vi', 'VI'):
            for j in range(4):
                if P[j] % 12 == LN and N[j] - P[j] != 1:
                    if j in (0, 3) or cn['rn'] in ('vi', 'VI') or not (cn['inv'] == 0 and N[j] % 12 == cn['fifth'] and P[j] - N[j] in (3, 4)):
                        E.append(f'{i}: leading note does not rise')
        if cp['sev'] is not None and cn['rn'] != cp['rn']:
            for j in range(4):
                if P[j] % 12 == cp['sev'] and P[j] - N[j] not in (1, 2): E.append(f'{i}: 7th does not fall by step')
        if cp['rn'] == 'V7/V':
            for j in range(4):
                if P[j] % 12 == (cp['root'] + 4) % 12 and N[j] - P[j] != 1: E.append(f'{i}: fi does not rise')
    return E


def sec_S(items, real, ui):
    COUNT['R4 rung 3 items'] = len(items)
    # every model x key x register: app checker, independent rules, cadence type
    for q in real:
        where = f"rung 3 {q['md']} {q['a']} [{' '.join(q['rns'])}] key {NM[q['k']]} reg {q['reg']}"
        COUNT['R4 rung 3 model x key x register realisations'] += 1
        if not q['ch']:
            fail('S', f'{where}: no realisation')
            continue
        if q['app']:
            fail('S', f'{where}: app SATB checker reports {q["app"]}')
        for e in vl_errors(q['ch'], q['rns'], q['k'], q['md']):
            fail('S', f'{where}: {e}')
        if not cad_ok(q['a'], q['rns'], q['k'], q['md']):
            fail('S', f'{where}: does not end with a {q["a"]} cadence')
        # one right answer: no other category's ending fits too
        others = [c for c in SIX if c != q['a'] and cad_ok(c, q['rns'], q['k'], q['md'])]
        if others:
            fail('S', f'{where}: also fits {others}')
    for q in items:
        if q['opts'] != SIX:
            fail('S', f"rung 3 question offers {q['opts']}, not the six answers")
            break
    # balance and the mode tell
    by_mode = collections.defaultdict(collections.Counter)
    for q in items:
        by_mode[q['md']][q['a']] += 1
    for md, c in by_mode.items():
        COUNT[f'R4 rung 3 {md} answers'] = json.dumps(dict(sorted(c.items())))
    if set(by_mode['min']) != set(SIX):
        fail('S', f"minor items draw {sorted(by_mode['min'])}, not all six")
    if set(by_mode['maj']) != set(SIX) - {'phrygian'}:
        fail('S', f"major items draw {sorted(by_mode['maj'])}")
    tot = collections.Counter(q['a'] for q in items)
    chance = tot.most_common(1)[0][1] / len(items)
    for md, c in by_mode.items():
        n = sum(c.values())
        for a, k in c.items():
            if k / n > chance + MARGIN:
                fail('S', f'mode tell: in {md} the answer {a} comes {k/n:.0%} of the time (chance {chance:.0%})')
    W = 'cadences rung 3'
    A = lambda r: r['a']
    tell('S', items, 'mode', lambda r: r['md'], A, W)
    tell('S', items, 'key and mode', lambda r: (r['k'], r['md']), A, W)
    tell('S', items, 'number of chords', lambda r: len(r['rns']), A, W)
    tell('S', items, 'second chord', lambda r: r['rns'][1], A, W)
    tell('S', items, 'opening voicing', lambda r: tuple(r['ch'][0]), A, W)
    tell('S', items, 'lowest note (6-semitone bands)', lambda r: min(map(min, r['ch'])) // 6, A, W)
    tell('S', items, 'highest note (6-semitone bands)', lambda r: max(map(max, r['ch'])) // 6, A, W)
    # the cadential 6/4's bass motion (so held while the chord changes, then do) is not unique to its button
    so = lambda q: (q['k'] + 7) % 12
    def holds_so(q):
        return any(a[0] == b[0] and a[0] % 12 == so(q) for a, b in zip(q['ch'], q['ch'][1:]))
    hold = collections.Counter(q['a'] for q in items if holds_so(q))
    COUNT['R4 items with the bass held on so, by answer'] = json.dumps(dict(sorted(hold.items())))
    if len([a for a in hold if a != 'cad64']) < 2:
        fail('S', f'the bass held on so occurs only in {sorted(hold)}')
    if hold['cad64'] / max(1, sum(hold.values())) > .55:
        fail('S', f"the bass held on so is a cadential 6/4 {hold['cad64']/sum(hold.values()):.0%} of the time")
    perf_lines = {(q['md'], bass_degrees(q)[-3:]) for q in items if q['a'] == 'perfect'}
    lone = {bass_degrees(q)[-3:] for q in items if q['a'] == 'cad64' and (q['md'], bass_degrees(q)[-3:]) not in perf_lines}
    if lone:
        fail('S', f'cadential 6/4 bass endings never heard in a perfect cadence: {sorted(lone)[:5]}')
    pc = [q for q in items if q['a'] in ('cad64', 'perfect')]
    tell('S', pc, 'bass line in scale degrees (6/4 vs perfect)', lambda r: (r['md'], tuple(m % 12 for m in bass_degrees(r))), A, W)
    # >= 100 distinct items per button
    dist = collections.defaultdict(set)
    for q in items:
        dist[q['a']].add((q['md'], q['k'], tuple(q['rns']), json.dumps(q['ch'])))
    for a in SIX:
        COUNT[f'R4 rung 3 distinct items {a}'] = len(dist[a])
        if len(dist[a]) < 100:
            fail('S', f'{a}: only {len(dist[a])} distinct items')
    # the buttons and the feedback, as rendered
    if ui['labels'] != ['Perfect', 'Plagal', 'Imperfect', 'Interrupted', 'Phrygian', 'Cadential 64']:
        fail('S', f"rung 3 buttons: {ui['labels']}")
    for a, txt in ui['fb'].items():
        if a == 'phrygian' and not ('imperfect (half) cadence in a minor key' in txt and 'iv⁶–V' in txt):
            fail('S', f'Phrygian feedback does not name its family: {txt}')
        if a == 'cad64' and not ('decorated approach to V in a perfect or imperfect cadence' in txt and 'perfect (authentic)' in txt):
            fail('S', f'cadential 6/4 feedback does not name its family: {txt}')
    for a, txt in ui['near'].items():
        fam = {'phrygian': 'It is the special kind', 'cad64': 'That delay is the cadential 6/4'}[a]   # EL-8: the feedback names the family and says what is exact about the answer
        if fam not in txt or not txt.startswith('Not this time'):
            fail('S', f'{a} answered with its family: strip "{txt}"')
    # strict rules (independent theory check 0.48): every rung 3 item and every model x key x register realisation
    errs = collections.Counter()
    for q in items + [dict(r, md=r['md']) for r in real if r['ch']]:
        for e in ic_errors(q):
            errs[e.split(': ', 1)[-1] if ': ' in e else e] += 1
    COUNT['R4 rung 3 strict SATB (independent rules) items checked'] = len(items) + len([r for r in real if r['ch']])
    if errs:
        fail('S', f'rung 3 strict SATB errors: {dict(errs.most_common(8))}')
    d3 = sum(1 for q in items if q['rns'][-1] == 'I' and sum(1 for m in q['ch'][-1] if m % 12 == (q['k'] + 4) % 12) > 1)
    COUNT['R4 rung 3 final major I with a doubled 3rd'] = d3
    if d3:
        fail('S', f'{d3} rung 3 items end on a major tonic with a doubled 3rd')
    # solfa in the feedback is la-based minor (movable do): Phrygian bass fa–mi; the 6/4 over mi in minor, so in major
    for (a, md), txt in ui['fbm'].items():
        if a == 'phrygian' and ('fa–mi' not in txt or 'le–so' in txt):
            fail('S', f'Phrygian feedback solfa ({md}): {txt}')
        if a == 'cad64' and f"over the bass {'mi' if md == 'min' else 'so'}," not in txt:
            fail('S', f'cadential 6/4 feedback solfa ({md}): {txt}')
    COUNT['R4 feedback solfa checks'] = len(ui['fbm'])


async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1500)

        # ---------------- Q: EL-6 chord quality ----------------
        qual = await pg.evaluate("""(mk)=>{const R=eval(mk)(29),o=[];for(const l of [1,2,3])for(let i=0;i<1500;i++){const q=earGen('qual',l,R);
            o.push({l,a:q.a,root:q.root,inv:q.inv,notes:q.notes,txt:earAnsTxt(q)})}return o}""", RNG)
        sec_Q(qual)

        # ---------------- K: EL-7 cadences rung 1 ----------------
        k1 = await pg.evaluate("""(mk)=>{const R=eval(mk)(31),o=[];const chk=q=>q.ch?withKey(q.key,()=>checkSATB(q.ch,cadList(q.rns.join(' '),q.key))).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation'];
            for(let i=0;i<2000;i++){const q=earGen('cad',1,R);o.push({a:q.a,rns:q.rns,k:q.key.k,md:q.key.mode,reg:q.reg,ch:q.ch,app:chk(q)})}return o}""", RNG)
        # every model x key x a spread of registers, through the same path the questions use
        k1r = await pg.evaluate("""()=>{const o=[];for(const c in CADT[1].maj)for(const t of CADT[1].maj[c])for(const k of earCadKeys(1,'maj'))for(let b=41;b<=52;b+=2)for(let s=67;s<=77;s+=2)for(const fb of [42,49,56])for(const ls of [67,72,77]){
            const key={k,mode:'maj'},rns=t.split(' '),P=earCadProg(1,rns,key,{b,s,fb,ls});
            o.push({a:c,rns,k,md:'maj',reg:{b,s,fb,ls},ch:P.ch,app:P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation']})}return o}""")
        COUNT['EL-7 rung 1 model x key x register realisations'] = len(k1r)
        # the key chord plays before the two chords. Playback goes through the Ear Lab transport (elPlay, merge 0.48), which sounds
        # chords on the sampled piano via tone(); this reads the order of the notes it schedules
        cue = await pg.evaluate("""async(mk)=>{const R=eval(mk)(37);await elPreload('cad');const T=[];const o=window.tone;window.tone=(m,t)=>{T.push([m,t])};EAR.drill='cad';EAR.lvl.cad=1;
            const res=[];try{for(let i=0;i<40;i++){EAR.q=earGen('cad',1,R);T.length=0;const inf=elPlay(EAR.q,'all');stopAll();const times=[...new Set(T.map(x=>x[1].toFixed(3)))];res.push(inf&&inf.state==='playing'?times.length:-1)}}finally{window.tone=o}return res}""", RNG)
        if any(n != 3 for n in cue):
            fail('K', f'rung 1 playback is not key chord + two chords: onsets {collections.Counter(cue)}')
        sec_K(k1, k1r)

        # ---------------- S: R4 cadences rung 3 ----------------
        k3 = await pg.evaluate("""(mk)=>{const R=eval(mk)(43),o=[];for(let i=0;i<12000;i++){const q=earGen('cad',3,R);o.push({a:q.a,md:q.key.mode,k:q.key.k,rns:q.rns,ch:q.ch,opts:q.opts})}return o}""", RNG)
        k3r = await pg.evaluate("""()=>{const o=[];for(const md of ['maj','min'])for(const c in CADT[3][md])for(const t of CADT[3][md][c])for(const k of earCadKeys(3,md))
            for(const reg of [{b:41,s:64},{b:53,s:76},{b:41,s:76},{b:53,s:64},{b:47,s:70}]){const key={k,mode:md},rns=t.split(' '),P=earCadProg(3,rns,key,reg);
            o.push({a:c,md,k,rns,reg,ch:P.ch,app:P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation']})}return o}""")
        ui = await pg.evaluate("""async(mk)=>{const R=eval(mk)(47);EAR.drill='cad';EAR.lvl.cad=3;const fb={},near={};let labels=null;
            const fbm={};for(const [a,md] of [['phrygian','min'],['cad64','maj'],['cad64','min']]){let q;do{q=earGen('cad',3,R)}while(q.a!==a||q.key.mode!==md);fbm[a+'|'+md]=earAnsTxt(q)}
            for(const a of ['phrygian','cad64']){let q;do{q=earGen('cad',3,R)}while(q.a!==a);fb[a]=earAnsTxt(q);
              EAR.q=q;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();labels=[...document.querySelectorAll('#earMain [data-earans]')].map(b=>b.textContent);
              document.querySelector(`#earMain [data-earans="${CADPARENT[a]}"]`).click();near[a]=(document.querySelector('#earMain .el-result')||{}).textContent||''}
            return{labels,fb,near,fbm}}""", RNG)
        ui['fbm'] = {tuple(k.split('|')): v for k, v in ui['fbm'].items()}
        sec_S(k3, k3r, ui)

        # "Without the key chord" (independent theory check 0.48): at rung 1, I–V in one key and IV–I a 5th higher can be the same two
        # chords, so the replay is hidden there. At rungs 2–3 every phrase opens on the tonic; check that no voicing, or transposition of
        # one, is heard under two answers, so the replay stays.
        nk = await pg.evaluate("""(mk)=>{const R=eval(mk)(53),o={},ch=[];stopAll();EAR.drill='cad';
            for(const l of [1,2,3]){EAR.lvl.cad=l;EAR.q=earGen('cad',l,R);EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();o[l]=!!document.querySelector('#earMain [data-earplay="nokey"]')}
            for(const l of [1,2,3])for(let i=0;i<(l===1?3000:6000);i++){const q=earGen('cad',l,R);ch.push({l,a:q.a,ch:q.ch})}EAR.q=null;renderEar();return{o,ch}}""", RNG)
        if nk['o'] != {'1': False, '2': True, '3': True}:
            fail('S', f'"Without the key chord" offered at rungs {nk["o"]} (want rung 1 hidden, rungs 2-3 shown)')
        for l in (1, 2, 3):
            ex, tr = collections.defaultdict(set), collections.defaultdict(set)
            for q in (x for x in nk['ch'] if x['l'] == l):
                b0 = q['ch'][0][0]
                ex[json.dumps(q['ch'])].add(q['a']); tr[json.dumps([[m - b0 for m in c] for c in q['ch']])].add(q['a'])
            amb_ex = sum(1 for v in ex.values() if len(v) > 1); amb_tr = sum(1 for v in tr.values() if len(v) > 1)
            COUNT[f'cadences rung {l}: voicings heard under two answers (exact / transposed)'] = f'{amb_ex} / {amb_tr}'
            if l > 1 and (amb_ex or amb_tr):
                fail('S', f'cadences rung {l}: {amb_ex} voicings ({amb_tr} transposed) are heard under two answers without the key chord')

        # ---------------- M: EL-10 stats model and scoring flow ----------------
        unit = await pg.evaluate("""()=>{const Z=EARST0,o=[];const run=ks=>ks.reduce((s,k)=>earStatNext(s,k),Z);
            const cases=[[[],{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}],[['ok'],{n:1,ok:1,streak:1,best:1,shown:0,skipped:0}],
             [['ok','ok','shown'],{n:2,ok:2,streak:2,best:2,shown:1,skipped:0}],[['ok','skipped','ok'],{n:2,ok:2,streak:2,best:2,shown:0,skipped:1}],
             [['ok','ok','miss','ok'],{n:4,ok:3,streak:1,best:2,shown:0,skipped:0}],[['shown','shown','skipped'],{n:0,ok:0,streak:0,best:0,shown:2,skipped:1}],
             [['miss','shown','ok','skipped','ok','ok'],{n:4,ok:3,streak:3,best:3,shown:1,skipped:1}]];
            for(const [ks,want] of cases)o.push({ks,got:run(ks),want});
            // old saved records (no shown/skipped) are read with zeros, and the input is never changed
            const old={n:3,ok:2,streak:1,best:2},nx=earStatNext(old,'skipped');o.push({ks:['legacy+skipped'],got:nx,want:{n:3,ok:2,streak:1,best:2,shown:0,skipped:1}});
            o.push({ks:['input unchanged'],got:old,want:{n:3,ok:2,streak:1,best:2}});return o}""")
        for c in unit:
            COUNT['EL-10 stats model unit cases'] += 1
            if c['got'] != c['want']:
                fail('M', f"earStatNext {c['ks']}: {c['got']} != {c['want']}")
        dialogs = []
        pg.on('dialog', lambda d: (dialogs.append(d.message), asyncio.ensure_future(d.dismiss())))
        flow = await pg.evaluate("""async()=>{const o={};const st=()=>({...earSt()}),strip=()=>(document.querySelector('#earMain .el-foot')||{}).textContent||'';
            const click=sel=>{const b=document.querySelector('#earMain '+sel);if(!b)throw new Error('no '+sel);b.click()};
            window.earPlay=()=>{if(EAR.q)EAR.q.plays=(EAR.q.plays||0)+1};EAR.drill='cad';EAR.lvl.cad=2;EAR.st.cad={...EARST0};EAR.q=null;EAR.done=false;renderEar();
            click('[data-earplay="all"]');o.start=st();
            click('[data-earans="'+EAR.q.a+'"]');o.right1=st();click('[data-earnew]');
            click('[data-earans="'+EAR.q.a+'"]');o.right2=st();click('[data-earnew]');
            click('[data-earshow]');o.shown=st();o.shownStrip=strip();o.shownRes=document.querySelector('#earMain .el-result').textContent;click('[data-earnew]');
            click('[data-earnew]');o.skipped=st();o.skipStrip=strip();o.toast=document.getElementById('toast').textContent;
            const wrong=EAR.q.opts.find(x=>x!==EAR.q.a);click('[data-earans="'+wrong+'"]');o.miss=st();
            // melody: undo and redo end once the answer is marked (buttons gone, Ctrl+Z does nothing)
            EAR.drill='mel';EAR.lvl.mel=1;EAR.q=null;renderEar();click('[data-earplay="all"]');const q=EAR.q;
            for(const x of q.a.slice(1))click('.earstep[data-earsol="'+x+'"]');o.undoBefore=!!document.querySelector('#earMain [data-hist="ear:u"]:not([disabled])');
            click('[data-earchk]');const ans=JSON.stringify(EAR.ans);
            o.undoAfter=document.querySelectorAll('#earMain [data-hist]').length;o.histActive=histActive();o.histLen=HIST.ear.u.length+HIST.ear.r.length;
            document.dispatchEvent(new KeyboardEvent('keydown',{key:'z',ctrlKey:true,bubbles:true}));document.dispatchEvent(new KeyboardEvent('keydown',{key:'y',ctrlKey:true,bubbles:true}));
            o.ansKept=JSON.stringify(EAR.ans)===ans&&EAR.done;
            // reset: inline confirm, keep, reset, undo
            EAR.drill='cad';EAR.q=null;EAR.done=false;renderEar();const before=st();
            click('[data-earreset]');o.ask=!!document.querySelector('#earMain [data-earresetyes]')&&!!document.querySelector('#earMain [data-earresetno]');o.askText=strip();
            click('[data-earresetno]');o.kept=JSON.stringify(st())===JSON.stringify(before)&&!!document.querySelector('#earMain [data-earreset]');
            click('[data-earreset]');click('[data-earresetyes]');o.zero=st();o.undoBtn=!!document.querySelector('#earMain [data-earresetundo]');
            click('[data-earresetundo]');o.restored=JSON.stringify(st())===JSON.stringify(before);o.saved=JSON.stringify(LS.get('cjg_ear').st.cad)===JSON.stringify(before);
            return o}""")
        exp = {'start': (0, 0, 0, 0, 0, 0), 'right1': (1, 1, 1, 1, 0, 0), 'right2': (2, 2, 2, 2, 0, 0), 'shown': (2, 2, 2, 2, 1, 0),
               'skipped': (2, 2, 2, 2, 1, 1), 'miss': (3, 2, 0, 2, 1, 1)}
        for k, v in exp.items():
            got = tuple(flow[k][x] for x in ('n', 'ok', 'streak', 'best', 'shown', 'skipped'))
            COUNT['EL-10 flow checks'] += 1
            if got != v:
                fail('M', f'flow after {k}: (n, ok, streak, best, shown, skipped) = {got}, expected {v}')
        if '1 shown' not in flow['shownStrip'] or not flow['shownRes'].startswith('Shown'):
            fail('M', f"Show me: stats line '{flow['shownStrip']}', result '{flow['shownRes'][:40]}'")
        if '1 skipped' not in flow['skipStrip'] or 'skipped' not in flow['toast'].lower():
            fail('M', f"Next before answering: stats line '{flow['skipStrip']}', toast '{flow['toast']}'")
        if not flow['undoBefore'] or flow['undoAfter'] or flow['histActive'] is not None or flow['histLen'] or not flow['ansKept']:
            fail('M', f"undo/redo after marking: before {flow['undoBefore']}, buttons after {flow['undoAfter']}, histActive {flow['histActive']}, stack {flow['histLen']}, answer kept {flow['ansKept']}")
        if not (flow['ask'] and 'Reset the Cadences score?' in flow['askText'] and flow['kept']):
            fail('M', f"reset does not ask inline first: {flow['askText']}")
        if tuple(flow['zero'][x] for x in ('n', 'ok', 'streak', 'best', 'shown', 'skipped')) != (0,) * 6 or not flow['undoBtn']:
            fail('M', f"reset: {flow['zero']}, undo offered {flow['undoBtn']}")
        if not (flow['restored'] and flow['saved']):
            fail('M', 'reset undo does not restore (and save) the score')
        COUNT['EL-10 flow checks'] += 6
        if dialogs:
            fail('M', f'browser dialogs opened: {dialogs}')

        # ---------------- U: EL-11 rungs, Stage switch, show all, rung change, page errors at Stages 4, 5, 6 ----------------
        # merge 0.48: one Stage table, EARSTAGE (Fable's design spec, section 3): a drill or rung shows when its Stage <= the selected Stage
        WANT = {4: {'metre': [1, 2], 'rhy': [1, 2], 'qual': [1], 'mel': [1]},
                5: {'metre': [1, 2, 3], 'rhy': [1, 2, 3], 'qual': [1, 2], 'cad': [1, 2], 'bass': [1, 2], 'mel': [1, 2], 'blind': [1, 2]},
                6: {d: [1, 2, 3] for d in ('metre', 'rhy', 'qual', 'cad', 'bass', 'mel', 'blind')}}
        await pg.evaluate("()=>{EAR.all=false;EAR.q=null;EAR.done=false}")
        for g in (4, 5, 6):
            await pg.click(f'#lvl button[data-l="{g}"]')
            await pg.evaluate("()=>{location.hash='ear';room('ear')}")
            await pg.wait_for_timeout(200)
            n0 = len(errs)
            seen = {}
            for d in WANT[g]:
                r = await pg.evaluate("""async(d)=>{EAR.q=null;EAR.done=false;const t=document.querySelector(`#earMain [data-eardr="${d}"]`);if(!t)return null;t.click();
                    const rungs=[...document.querySelectorAll('#earMain [data-earlv]')].map(b=>+b.dataset.earlv),out={rungs,txt:document.querySelector('#earMain').textContent,
                      tabs:[...document.querySelectorAll('#earMain [data-eardr]')].map(b=>b.dataset.eardr),tagtxt:[...document.querySelectorAll('#earMain .el-drill small')].map(x=>x.textContent)};
                    for(const n of rungs){document.querySelector(`#earMain [data-earlv="${n}"]`).click();if(d==='blind')await earLoadBlind();document.querySelector('#earMain [data-earplay="all"]').click();
                      await new Promise(r=>setTimeout(r,60));const a=document.querySelector('#earMain [data-earans]');if(a)a.click();else{const s=document.querySelector('#earMain [data-earshow]');if(s)s.click()}stopAll()}
                    return out}""", d)
                COUNT['EL-11 drill x Stage rendered'] += 1
                if r is None:
                    fail('U', f'Stage {g}: drill {d} is not offered')
                    continue
                seen[d] = r
                if r['rungs'] != WANT[g][d]:
                    fail('U', f'Stage {g} {d}: rungs offered {r["rungs"]}, expected {WANT[g][d]}')
                if sorted(r['tabs']) != sorted(WANT[g]):
                    fail('U', f'Stage {g}: drills offered {r["tabs"]}, expected {sorted(WANT[g])}')
                if 'Level ' in r['txt'] or any(not t.startswith('Stage ') for t in r['tagtxt']) or ' S4' in r['txt'] or ' S5' in r['txt']:
                    fail('U', f'Stage {g} {d}: level wording or a short Stage tag in the UI ({r["tagtxt"]})')
            # show all: every drill and every rung (at Stage 6 nothing is hidden, so the chip is not offered)
            if g == 6:
                n6 = await pg.evaluate("()=>document.querySelectorAll('#earMain [data-earall]').length")
                if n6:
                    fail('U', 'Stage 6: a Show all chip is offered with nothing hidden')
                COUNT['EL-11 Stages checked'] += 1
                if len(errs) > n0:
                    fail('U', f'Stage {g}: page errors {errs[n0:][:3]}')
                continue
            al = await pg.evaluate("""()=>{document.querySelector('#earMain [data-earall]').click();const tabs=[...document.querySelectorAll('#earMain [data-eardr]')].map(b=>b.dataset.eardr);
                const t=document.querySelector('#earMain [data-eardr="qual"]');t.click();const r=[...document.querySelectorAll('#earMain [data-earlv]')].map(b=>+b.dataset.earlv);
                document.querySelector('#earMain [data-earall]').click();return{tabs,r,off:[...document.querySelectorAll('#earMain [data-eardr]')].length}}""")
            if len(al['tabs']) != 7 or al['r'] != [1, 2, 3] or al['off'] != len(WANT[g]):
                fail('U', f'Stage {g}: show all gives {al}')
            if len(errs) > n0:
                fail('U', f'Stage {g}: page errors {errs[n0:][:3]}')
            COUNT['EL-11 Stages checked'] += 1
        # the hand-sign rows are never called rungs in the UI
        txt = await pg.evaluate("""()=>{EAR.drill='mel';EAR.lvl.mel=1;EAR.q=earGen('mel',1);EAR.done=false;EAR.ans=[];renderEar();const el=document.querySelector('#earMain');
            return el.textContent+' '+[...el.querySelectorAll('[aria-label],[title]')].map(e=>(e.getAttribute('aria-label')||'')+' '+(e.getAttribute('title')||'')).join(' ')}""")
        ladder = await pg.evaluate("()=>[...document.querySelectorAll('#earMain .earlad, #earMain .earstep')].map(e=>(e.getAttribute('aria-label')||'')+e.textContent).join(' ')")
        if 'rung' in ladder.lower():
            fail('U', 'the hand-sign ladder is called a rung in the UI')
        # rung change mid-question: recorded as skipped, and said
        rc = await pg.evaluate("""()=>{S.level=6;EAR.all=false;EAR.drill='cad';EAR.lvl.cad=2;EAR.st.cad={...EARST0};EAR.q=null;EAR.done=false;renderEar();
            document.querySelector('#earMain [data-earplay="all"]').click();const q1=EAR.q;document.querySelector('#earMain [data-earlv="3"]').click();
            const o={st:{...earSt()},q:EAR.q,toast:document.getElementById('toast').textContent,lvl:earLvl(),line:document.querySelector('#earMain .el-foot').textContent};
            document.querySelector('#earMain [data-earplay="all"]').click();document.querySelector('#earMain [data-earans="'+EAR.q.a+'"]').click();document.querySelector('#earMain [data-earlv="2"]').click();
            o.after={...earSt()};return o}""")
        if rc['st']['skipped'] != 1 or rc['st']['n'] != 0 or rc['q'] is not None or rc['lvl'] != 3:
            fail('U', f"rung change mid-question: {rc['st']}, question {rc['q']}, rung {rc['lvl']}")
        if 'skipped' not in rc['toast'] or '1 skipped' not in rc['line']:
            fail('U', f"rung change mid-question is not said: toast '{rc['toast']}', stats '{rc['line']}'")
        if rc['after']['skipped'] != 1 or rc['after']['n'] != 1:
            fail('U', f"rung change after answering counted as a skip: {rc['after']}")
        COUNT['EL-11 rung-change checks'] = 3

        if errs:
            fail('page', f'page errors: {errs[:5]}')
        await b.close()

    report = {'counts': dict(COUNT), 'failures': {k: v[:25] for k, v in FAIL.items()}, 'n_failures': sum(len(v) for v in FAIL.values())}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)

asyncio.run(main())
