"""Ear Lab item generation and scoring (register 0.48: R4, EL-6, EL-7, EL-10, EL-11, R16).
Run: python3 tests/earlab_items_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

The app generates the questions; this file checks them with its own rules (music21 for chord spelling, its own interval
and voice-leading arithmetic), and asks the app's SATB checker only where the register says "passes the SATB checker".

Sections
  Q  EL-6  chord quality: root position only at rungs 1-3, >= 1,000 seeded items per rung, spacing, two registers, register tell,
           augmented and diminished 7th answers name no inversion and say the chord is symmetrical
  K  EL-7  cadences rung 1: four basic cadences, two chords after the key chord, SATB checker, balance, tells; 0.49 C12 complete
           chords only, C23 open or close spacing for every model with no spacing tell
  K2 EL S2 / S1 (IC_EAR2_048): rung 1 model share inside imperfect (I–V and IV–V about half each), the IV-first ambiguity, the soprano
           tells, and the RUNG1_SOP_BALANCE switch (default off; on: strict, soprano tells lower, register tells still near chance)
  S  R4    cadences rung 3: six answers, family feedback, SATB checker, mode tell, the 6/4 bass motion, >= 100 distinct items per answer
  M  EL-10 stats model (unit) and a scoring flow in the page
  U  EL-11 rung wording, Stage switch, show all, Stage tags, rung change mid-question, page errors at Stages 4, 5, 6
  N  0.48 logic: "Nearly" at cadences rung 3 (Justin 19 Nov 2026, option a): judge, stats model, tally, streak, log, journal, feedback
  I  0.48 logic: the two rung 3 phrases that end interrupted after a cadential 6/4 (kept, answer "Interrupted"): strict SATB, one right
           answer, feedback, the CAD64_INT_NEARLY switch (default true = Nearly, Justin 20 Nov 2026, item B)
  P  reconcile 0.48: every cadence result-panel sentence (card, spec 9.5), for every answer at every rung, is true of its item
  B  IC_EAR_048 S5: blind analysis sentences against each excerpt (no single-voice claims, its own numerals and mode, the key it
           cadences in, the bass on the root of the last chord from meta.json events and music21)
  T2 IC_EAR_048 S6: metre sentences say "you heard ... every bar / each beat" only when every split click sounded
  V  BHL 0.48 (IC_EAR_048 S1, S2): the strict rules (below, ic_errors) for cadences rungs 1 and 2 and for bass and numerals, as well as
           rung 3: generated items, every rung 1 realisation the drill can draw, every rung 2 and rung 3 model x key x register on the question grid
           (earR23Index, 0.49 C3),
           every bass progression x key x register
  T  0.48 logic: Pulse and metre: answer grid per rung (2/4 from rung 1, 12/8 from rung 2), every metre against the fixture rows
           (tests/fixtures/metre_items.json) and music21, balance, and the tempo / playing-time tells
"""
import sys, asyncio, json, pathlib, collections, re

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
                # the result panel names no inversion or root position for the symmetrical chords (the panel does not say "symmetrical":
                # that sentence lived only in the removed, never-called earAnsTxt; IC_EAR_048 C4, open for Justin)
                if any(w in txt for w in ('1st inversion', '2nd inversion', '3rd inversion', 'root position')):
                    fail('Q', f'{where}: result panel "{txt}" names an inversion or root position for a symmetrical chord')
            elif 'root position' not in txt:
                fail('Q', f'{where}: result panel "{txt}" does not say root position')
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


CLOSE_LT = 12


def sec_K(items, real, tl=None):
    # 0.49 C31: the tells are measured on a larger sample (tl, 10,000 items) when given, so sampling noise stays well inside the margin
    T = tl or items
    COUNT['EL-7 rung 1 items for the tell checks'] = len(T)
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
        # 0.49 C23 (Justin 21 Nov 2026, L101): open or close spacing, for every model (EARR1OPT.open off); the upper voices stay within an
        # octave of each other. 0.49 C12 (L101): complete chords in every cadence (EARR1OPT.inc off)
        for c in q['ch']:
            if c[3] - c[2] > 12 or c[2] - c[1] > 12:
                fail('K', f'{where}: chord {c} has upper voices more than an octave apart')
        fin = set(m % 12 for m in q['ch'][-1]); fst = set(m % 12 for m in q['ch'][0])
        if len(fin) < 3 or len(fst) < 3:
            fail('K', f'{where}: incomplete chord {q["ch"]} (rung 1 uses the complete chord, C12)')
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
    tell('K', T, 'lowest note (6-semitone bands)', lambda r: min(map(min, r['ch'])) // 6, A, W)
    tell('K', T, 'highest note (6-semitone bands)', lambda r: max(map(max, r['ch'])) // 6, A, W)
    tell('K', T, 'register drawn (bass, soprano)', lambda r: (r['reg']['b'], r['reg']['s']), A, W)
    tell('K', T, 'top note of the first chord', lambda r: r['ch'][0][3], A, W)
    tell('K', T, 'top note of the last chord', lambda r: r['ch'][-1][3], A, W)
    tell('K', T, 'highest top note', lambda r: max(c[3] for c in r['ch']), A, W)
    tell('K', T, 'bass note of the first chord', lambda r: r['ch'][0][0], A, W)
    tell('K', T, 'bass note of the last chord', lambda r: r['ch'][-1][0], A, W)
    tell('K', T, 'lowest bass note', lambda r: min(c[0] for c in r['ch']), A, W)
    tell('K', T, 'key', lambda r: r['k'], A, W)
    # BHL 0.48 (Justin 20 Nov 2026, item H): the lowest and highest notes together, at every resolution the independent check used, and the span
    lo = lambda r: min(map(min, r['ch'])); hi = lambda r: max(map(max, r['ch']))
    for w in (1, 2, 3, 4, 6):
        tell('K', T, f'lowest and highest note together ({w}-semitone bands)' if w > 1 else 'lowest and highest note together (exact)',
             (lambda w: lambda r: (lo(r) // w, hi(r) // w))(w), A, W)
    tell('K', T, 'span from lowest to highest note (exact)', lambda r: hi(r) - lo(r), A, W)
    # 0.49 C23: open or close spacing must not give the answer away (each chord, and both together)
    # 0.49 C32 (L108): open = the soprano an octave or more above the tenor (close = less than an octave; EAR_CLOSE_LT in the app)
    op = lambda c: c[3] - c[1] >= CLOSE_LT
    tell('K', T, 'spacing of the first chord (open or close)', lambda r: op(r['ch'][0]), A, W)
    tell('K', T, 'spacing of the last chord (open or close)', lambda r: op(r['ch'][-1]), A, W)
    tell('K', T, 'spacing of both chords (open or close each)', lambda r: (op(r['ch'][0]), op(r['ch'][-1])), A, W)
    # 0.49 C12: the final chord's completeness (with the incomplete tonic on it was +16 points); all complete now, so it cannot tell
    tell('K', T, 'final chord complete', lambda r: len(set(m % 12 for m in r['ch'][-1])) == 3, A, W)
    ncl = sum(1 for r in items if not op(r['ch'][0]) or not op(r['ch'][-1]))
    COUNT['C23 rung 1 items with a close-spaced chord'] = f'{ncl} of {len(items)}'
    for c in ('perfect', 'plagal', 'imperfect', 'interrupted'):
        rr = [r for r in items if r['a'] == c]
        COUNT[f'C23 rung 1 {c}: share with a close-spaced chord'] = f'{sum(1 for r in rr if not op(r["ch"][0]) or not op(r["ch"][-1])) / max(1, len(rr)):.1%}'
    # 0.49 C31 (Justin 21 Nov 2026, L108): the top line and the tenor-soprano gap. The chords themselves differ (the last chord is I, V or vi;
    # the first V, IV or I), so the soprano degrees can never reach chance: on its own (from the pool, exact), the last soprano degree can
    # come down to +25 points, the first to +25, the line (both) to +38; with the register held, the line cannot go below about +55 and
    # the last chord's gap below about +17 (tests/reports/C_ENG_049_report.md, C31). Each is checked against the level the balanced
    # weights (EAR1W) reach, measured exactly (tests/gen_cad1_weights.py) plus 3 points for sampling. Answers that share a chord must not
    # be told apart by its voicing (5-point margin, chance 50%): perfect / plagal by the final I, perfect / interrupted by the first V.
    dg = lambda r, i: (r['ch'][i][3] - r['k']) % 12
    for nm, f, ceil in (('soprano line (degrees of both top notes)', lambda r: (dg(r, 0), dg(r, -1)), .568),
                        ('final soprano note (degree)', lambda r: dg(r, -1), .253),
                        ('first soprano note (degree)', lambda r: dg(r, 0), .278),
                        ('soprano motion (semitones)', lambda r: r['ch'][-1][3] - r['ch'][0][3], .30),
                        ('tenor-soprano gap of the last chord (exact)', lambda r: r['ch'][-1][3] - r['ch'][-1][1], .206),
                        ('tenor-soprano gap of the first chord (exact)', lambda r: r['ch'][0][3] - r['ch'][0][1], .073)):
        a, c = predict_acc(T, f, A)
        COUNT['tell checks'] += 1
        COUNT[f'C31 rung 1 {nm}: points above chance (ceiling)'] = f'{100*(a-c):+.1f} ({100*ceil:+.1f} + 3)'
        if a > c + ceil + .03:
            fail('K', f'C31: {nm} predicts the answer {a:.0%} of the time (chance {c:.0%}; the balanced weights reach {c+ceil:.0%})')
    for (x, y, i, nm) in (('perfect', 'plagal', -1, 'last'), ('perfect', 'interrupted', 0, 'first')):
        rr = [r for r in T if r['a'] in (x, y)]
        for fn, f in (('soprano degree', lambda r, i=i: dg(r, i)), ('tenor-soprano gap', lambda r, i=i: r['ch'][i][3] - r['ch'][i][1])):
            tell('K', rr, f'{x} vs {y}: {fn} of the {nm} chord', f, A, W)
        # the exact voicing of the shared chord (register included) cannot be held to 5 points with everything else: the weights reach
        # +7.0 (perfect / plagal) and +6.1 (perfect / interrupted) exactly (before C31: +38.7 and +19.2); checked against that + 3
        a, c = predict_acc(rr, lambda r, i=i: tuple(r['ch'][i]), A)
        ceil = {'last': .070, 'first': .061}[nm]
        COUNT['tell checks'] += 1
        COUNT[f'C31 rung 1 {x} vs {y}: exact voicing of the {nm} chord, points above chance (ceiling)'] = f'{100*(a-c):+.1f} ({100*ceil:+.1f} + 3)'
        if a > c + ceil + .03:
            fail('K', f'C31: {x} vs {y}: the exact voicing of the {nm} chord predicts the answer {a:.0%} of the time (chance {c:.0%})')


SIX = ['perfect', 'plagal', 'imperfect', 'interrupted', 'phrygian', 'cad64']


def r1_sop(r):
    return ((r['ch'][0][3] - r['k']) % 12, (r['ch'][1][3] - r['k']) % 12)


def sec_K2(off, on, flag_default):
    """EL S2 and S1 (IC_EAR2_048). off / on: rung 1 items with RUNG1_SOP_BALANCE off (default) / on."""
    if flag_default is not False:
        fail('K2', f'RUNG1_SOP_BALANCE defaults to {flag_default}, not false (Justin has not ruled)')
    A = lambda r: r['a']
    acc_sop = {}
    for name, items in (('off', off), ('on', on)):
        imp = [q for q in items if q['a'] == 'imperfect']
        share = sum(q['rns'][0] == 'IV' for q in imp) / len(imp)
        COUNT[f'K2 IV–V share of imperfect (switch {name})'] = f'{share:.1%}'
        if not .42 <= share <= .58:
            fail('K2', f'switch {name}: IV–V is {share:.0%} of imperfect items (want about half)')
        ivf = [q for q in items if q['rns'][0] == 'IV']
        pl = sum(q['a'] == 'plagal' for q in ivf) / len(ivf)
        COUNT[f'K2 first chord IV -> plagal (switch {name})'] = f'{pl:.1%}'
        # plagal (all IV–I) against imperfect IV–V (half of imperfect): 2/3 is the floor the four basic models allow
        if pl > .72:
            fail('K2', f'switch {name}: a first chord of IV means plagal {pl:.0%} of the time')
        a, c = predict_acc(items, lambda r: r['rns'][0], A)
        COUNT[f'K2 first chord alone: accuracy vs chance (switch {name})'] = f'{a:.1%} vs {c:.1%}'
        if a > .66:
            fail('K2', f'switch {name}: the first chord alone gives the answer {a:.0%} of the time')
        for fn, f in (('soprano solfa path', r1_sop), ('soprano degree, first chord', lambda r: r1_sop(r)[0]), ('soprano degree, last chord', lambda r: r1_sop(r)[1])):
            a, c = predict_acc(items, f, A)
            COUNT[f'K2 {fn}: accuracy vs chance (switch {name})'] = f'{a:.1%} vs {c:.1%}'
            acc_sop[(name, fn)] = a
        # the register tells stay near chance either way
        lo = lambda r: min(map(min, r['ch'])); hi = lambda r: max(map(max, r['ch']))
        for w in (1, 2, 3, 4, 6):
            tell('K2', items, f'switch {name}: lowest and highest note ({w}-semitone bands)', (lambda w: lambda r: (lo(r) // w, hi(r) // w))(w), A, 'cadences rung 1')
        tell('K2', items, f'switch {name}: span', lambda r: hi(r) - lo(r), A, 'cadences rung 1')
        for fn, f in (('first bass', lambda r: r['ch'][0][0]), ('last bass', lambda r: r['ch'][1][0]), ('first soprano', lambda r: r['ch'][0][3]),
                      ('last soprano', lambda r: r['ch'][1][3]), ('key', lambda r: r['k'])):
            tell('K2', items, f'switch {name}: {fn}', f, A, 'cadences rung 1')
        # strict rules, every item
        errs = collections.Counter(e.split(': ', 1)[-1] for q in items for e in ic_errors(dict(q, md='maj')))
        COUNT[f'K2 strict rules, items checked (switch {name})'] = len(items)
        if errs:
            fail('K2', f'switch {name}: strict errors {dict(errs.most_common(5))}')
        # 0.49 C23: open and close spacing both allowed (spacing tells are checked in section K); C12: complete chords only
        for q in items:
            if q['ch'] and any(len(set(m % 12 for m in c)) < 3 for c in q['ch']):
                fail('K2', f'switch {name}: incomplete chord {q["ch"]}')
                break
    # 0.49 C31 (L108): with the switch off (the default), the weights come from EAR1W, which balances the top line further than the 0.48
    # switch did, so the default now tells less than the switch on (before C31 it was the other way round)
    for fn in ('soprano solfa path', 'soprano degree, first chord', 'soprano degree, last chord'):
        if acc_sop[('off', fn)] > acc_sop[('on', fn)] + .005:
            fail('K2', f'{fn}: switch off (EAR1W) {acc_sop[("off", fn)]:.1%} is not below switch on {acc_sop[("on", fn)]:.1%}')
    # 0.49 C12 (L101, complete chords only) takes away the incomplete tonic's so–mi and re–do top lines, so a complete V–I can only have
    # so–so, ti–do or re–mi on top: with the switch off the path now reads about 92% (82% with the incomplete tonic; 83% with the switch on).
    # The ceiling moves from 86% to 94%; the switch (Justin has not ruled) is what lowers it. tests/reports/C_ENG_049_report.md
    # 0.49 C31: with EAR1W the path reads about 81% (chance 25%; 92% before C31); the ceiling comes down from 94% to 84%
    if acc_sop[('off', 'soprano solfa path')] > .84:
        fail('K2', f'soprano solfa path predicts {acc_sop[("off", "soprano solfa path")]:.0%} with the switch off (about 81% measured since 0.49 C31)')



def sec_V(d):
    """BHL 0.48: strict rules (ic_errors) beyond rung 3: cadences rungs 1-2 and bass and numerals. d: lists of {k, md, rns, ch, where}."""
    for name, rows in d.items():
        errs = collections.Counter(); ex = []; none = 0
        for q in rows:
            if not q['ch']:
                none += 1
                continue
            e = ic_errors(q)
            for x in e:
                errs[x.split(': ', 1)[-1] if ': ' in x else x] += 1
            if e and len(ex) < 3:
                ex.append(f"{q['md']} {NM[q['k']]} {' '.join(q['rns'])} {q['ch']}: {e[:2]}")
        COUNT[f'V strict rules: {name} checked'] = len(rows)
        if none:
            fail('V', f'{name}: {none} with no realisation')
        if errs:
            fail('V', f'{name}: strict errors {dict(errs.most_common(6))}; e.g. {ex}')


def bass_degrees(q):
    return tuple((c[0] - q['k']) % 12 for c in q['ch'])


# ---- strict SATB rules for cadences rung 3, after the independent theory check (0.48, checks/ic/vl.py); errors only ----
VL_Q = {'maj': [0, 4, 7], 'min': [0, 3, 7], 'dim': [0, 3, 6], 'dom7': [0, 4, 7, 10]}
VL_RN = {'maj': {'I': (0, 'maj'), 'ii': (2, 'min'), 'iii': (4, 'min'), 'IV': (5, 'maj'), 'V': (7, 'maj'), 'V7': (7, 'dom7'), 'vi': (9, 'min'), 'V7/V': (2, 'dom7'),
                 'V7/vi': (4, 'dom7')},
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
        if c['rn'].startswith('V7/') and pcs.count((c['root'] + 4) % 12) > 1: E.append(f'ch{i} {c["rn"]} doubled its leading note')
        if c['inv'] == 2 and pcs.count(c['bass']) < 2: E.append(f'ch{i} 6/4 without doubled bass')
        if c['sev'] is not None and pcs.count(c['sev']) > 1: E.append(f'ch{i} doubled 7th')
        # 0.49 C25 (IC_REG_049 S1): a major triad in first inversion is complete and doubles its root or 5th, never its 3rd (vi / VI excepted)
        if c['inv'] == 1 and c['sev'] is None and (c['third'] - c['root']) % 12 == 4 and (c['fifth'] - c['root']) % 12 == 7 and c['rn'] not in ('vi', 'VI'):
            if pcs.count(c['third']) > 1: E.append(f'ch{i} {c["rn"]}6 doubles its 3rd')
            if c['fifth'] not in pcs: E.append(f'ch{i} {c["rn"]}6 has no 5th')
        # 0.49 C34 (IC_C_ENG_049 S4, L108): no root-position triad (IV, vi, III, VI, a final I or i ...) doubles its 3rd and leaves out its 5th
        if c['inv'] == 0 and c['sev'] is None and pcs.count(c['third']) > 1 and c['fifth'] not in pcs:
            E.append(f'ch{i} {c["rn"]} doubles its 3rd with no 5th')
    for i in range(1, len(V)):
        P, N, cp, cn = V[i - 1], V[i], C[i - 1], C[i]
        for j in range(4):
            mv = abs(N[j] - P[j])
            if mv > 12 or mv in (10, 11): E.append(f'{i}: voice {j} leaps {mv}')
            # BHL 0.48 (IC_EAR_048 S1): no tritone leap (augmented 4th or diminished 5th) in any voice
            if mv == 6: E.append(f'{i}: voice {j} leaps a tritone')
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
        # the leading note of a secondary dominant (fi in V7/V, si in V7/vi) rises a semitone (IC_EAR_048 S2)
        if cp['rn'].startswith('V7/'):
            for j in range(4):
                if P[j] % 12 == (cp['root'] + 4) % 12 and N[j] - P[j] != 1: E.append(f'{i}: {cp["rn"]} leading note does not rise')
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
        # the result panel, answered with the family (Nearly off); earAnsTxt, which held the old family text, was never called (IC_EAR_048 C4)
        if a == 'phrygian' and not ('a Phrygian cadence is a kind of imperfect cadence' in txt and 'iv⁶ to V' in txt):
            fail('S', f'Phrygian feedback does not name its family: {txt}')
        if a == 'cad64' and not ('decorates a perfect cadence' in txt and '⁶₄' in txt):
            fail('S', f'cadential 6/4 feedback does not name its family: {txt}')
    # 0.48 logic + card: a family answer is Nearly (EAR_NEARLY on: gold panel, "Nearly", the spec 9.5 sentence, the button marked is-near);
    # with the switch off it is a wrong answer whose text names the family without calling the answer right (reconcile 0.48)
    for a, r in ui['near'].items():
        # 0.48 terms merge: the cadence bracket is the term pass's full "(US: half cadence)", never a hand-written "(US: half)"
        say = {'phrygian': r'and that is right: this is an imperfect cadence( \(US: half cadence\))?\. It is the special kind\.', 'cad64': r'and that is right\. Listen just before V'}[a]
        if not r or 'near' not in r['cls'].split() or r['verdict'] != 'Nearly' or not re.search(say, r['teach']) or r['opt'] is None \
                or re.search(r'\(US: (half|authentic|deceptive)\)', r['teach']):
            fail('S', f'{a} answered with its family (Nearly on): {r}')
    for a, r in ui['nearOff'].items():
        if not r or 'bad' not in r['cls'].split() or r['verdict'] != 'Not this time' or 'that is the right family' not in r['teach'] \
                or 'and that is right' in r['teach'] or 'The answer here is the more exact name' not in r['teach']:
            fail('S', f'{a} answered with its family (Nearly off): {r}')
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
    for (a, md), r in ui['fbm'].items():
        txt = r['teach']
        if a == 'phrygian' and ('fa to mi' not in txt or 'le to so' in txt or 'le–so' in txt):
            fail('S', f'Phrygian feedback solfa ({md}): {txt}')
        # the cadential 6/4 chip in the cadence bracket reads "cadential 6/4" (IC_EAR_048 S4); its bass solfa is in its title
        if a == 'cad64':
            c64 = [c for c in r['chips'] if '⁶₄' in c['t']]
            if len(c64) != 1 or c64[0]['s'] != 'cadential 6/4' or f"(bass {'mi' if md == 'min' else 'so'})" not in c64[0]['t']:
                fail('S', f'cadential 6/4 chip solfa ({md}): {r["chips"]}')
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
            const T=earTeachQual(q,{kind:'shown',given:null});o.push({l,a:q.a,root:q.root,inv:q.inv,notes:q.notes,txt:T.head+' ('+T.small+') '+T.teach})}return o}""", RNG)
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
        globals()['CLOSE_LT'] = await pg.evaluate('EAR_CLOSE_LT')
        k1t = await pg.evaluate("(mk)=>{const R=eval(mk)(41),o=[];for(let i=0;i<10000;i++){const q=earGen('cad',1,R);o.push({a:q.a,k:q.key.k,reg:q.reg,ch:q.ch})}return o}", RNG)
        sec_K(k1, k1r, k1t)

        # ---------------- K2: EL S2 / S1 (IC_EAR2_048) ----------------
        k2 = await pg.evaluate("""(mk)=>{const o={def:RUNG1_SOP_BALANCE};const run=(flag,seed)=>{RUNG1_SOP_BALANCE=flag;const R=eval(mk)(seed),a=[];
              for(let i=0;i<6000;i++){const q=earGen('cad',1,R);a.push({a:q.a,rns:q.rns,k:q.key.k,ch:q.ch})}return a};
            try{o.off=run(false,73);o.on=run(true,79)}finally{RUNG1_SOP_BALANCE=false}return o}""", RNG)
        sec_K2(k2['off'], k2['on'], k2['def'])

        # ---------------- S: R4 cadences rung 3 ----------------
        k3 = await pg.evaluate("""(mk)=>{const R=eval(mk)(43),o=[];for(let i=0;i<12000;i++){const q=earGen('cad',3,R);o.push({a:q.a,md:q.key.mode,k:q.key.k,rns:q.rns,ch:q.ch,opts:q.opts})}return o}""", RNG)
        k3r = await pg.evaluate("""()=>{const o=[];for(const md of ['maj','min'])for(const c in CADT[3][md])for(const t of CADT[3][md][c])for(const k of earCadKeys(3,md))
            for(const reg of [{b:41,s:64},{b:53,s:76},{b:41,s:76},{b:53,s:64},{b:47,s:70}]){const key={k,mode:md},rns=t.split(' '),P=earCadProg(3,rns,key,reg);
            o.push({a:c,md,k,rns,reg,ch:P.ch,app:P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation']})}return o}""")
        ui = await pg.evaluate("""async(mk)=>{const R=eval(mk)(47);EAR.drill='cad';EAR.lvl.cad=3;const fb={},near={},nearOff={};let labels=null;const RP=()=>{const e=document.querySelector('#earMain .el-result');return e?{cls:e.className,verdict:(e.querySelector('.el-verdict')||{}).textContent||'',teach:(e.querySelector('.el-teach')||{}).textContent||'',chips:[...e.querySelectorAll('.el-ch')].map(c=>({t:c.title,s:(c.querySelector('small')||{}).textContent||''})),opt:(document.querySelector('#earMain .el-opt.is-near')||{}).dataset}:null};
            const strip=h=>{const d=document.createElement('div');d.innerHTML=h;return d};
            const fbm={};for(const [a,md] of [['phrygian','min'],['cad64','maj'],['cad64','min']]){let q;do{q=earGen('cad',3,R)}while(q.a!==a||q.key.mode!==md);
              const T=earTeachCad(q,{kind:'shown',given:null}),P=strip(T.pic||'');fbm[a+'|'+md]={teach:T.teach,chips:[...P.querySelectorAll('.el-cad .el-ch')].map(c=>({t:c.title,s:(c.querySelector('small')||{}).textContent||''}))}}
            for(const a of ['phrygian','cad64']){let q;do{q=earGen('cad',3,R)}while(q.a!==a);const n0=EAR_NEARLY;EAR_NEARLY=false;fb[a]=earTeachCad(q,{kind:'miss',given:CADPARENT[a]}).teach;EAR_NEARLY=n0;
              EAR.q=q;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();labels=[...document.querySelectorAll('#earMain [data-earans]')].map(b=>b.textContent);
              document.querySelector(`#earMain [data-earans="${CADPARENT[a]}"]`).click();near[a]=RP();
              EAR_NEARLY=false;EAR.q=q;EAR.done=false;EAR.res=null;renderEar();document.querySelector(`#earMain [data-earans="${CADPARENT[a]}"]`).click();
              nearOff[a]=RP();EAR_NEARLY=true}
            return{labels,fb,near,nearOff,fbm}}""", RNG)
        ui['fbm'] = {tuple(k.split('|')): v for k, v in ui['fbm'].items()}
        sec_S(k3, k3r, ui)

        # ---------------- V: strict rules for cadences rungs 1-2 and bass and numerals (BHL 0.48) ----------------
        vd = await pg.evaluate("""(mk)=>{const R=eval(mk)(67),o={'cadences rung 1 items':[],'cadences rung 2 items':[],'bass and numerals items':[],
              'cadences rung 1, every realisation the drill can draw':[],'cadences rung 2, every model x key x register':[],'bass and numerals, every progression x key x register':[]};
            const row=(q)=>({k:q.key.k,md:q.key.mode,rns:q.rns||q.a,ch:q.ch});
            for(let i=0;i<3000;i++)o['cadences rung 1 items'].push(row(earGen('cad',1,R)));
            for(let i=0;i<4000;i++)o['cadences rung 2 items'].push(row(earGen('cad',2,R)));
            for(const l of [1,2,3])for(let i=0;i<1500;i++)o['bass and numerals items'].push(row(earGen('bass',l,R)));
            for(const e of earR1Pool())o['cadences rung 1, every realisation the drill can draw'].push({k:e.k,md:'maj',rns:e.t.split(' '),ch:e.ch});
            // 0.49 C3: the question grid is earR23Index (every mode, answer, model, key and grid point the balanced draw can pick), rungs 2 and 3
            o['cadences rung 3, every model x key x register']=[];
            for(const l of [2,3])for(const e of earR23Index(l)){const P=earCadM(l,e.t.split(' '),{k:e.k,mode:e.md},{b:e.b,s:e.s});o[`cadences rung ${l}, every model x key x register`].push({k:e.k,md:e.md,rns:e.t.split(' '),ch:P.ch})}
            for(const l of [1,2,3])for(const rns of earBassProgs(l))for(const k of BKEYS)for(const reg of [{b:42,s:66},{b:52,s:74},{b:47,s:70}]){
              const P=earBassProg(rns,{k,mode:'maj'},reg);o['bass and numerals, every progression x key x register'].push({k,md:'maj',rns,ch:P.ch})}
            return o}""", RNG)
        # rung 2 grid points with no strict realisation are skipped by the questions (earCadReg); every model x key must have at least one
        r2 = vd['cadences rung 2, every model x key x register']
        have = collections.defaultdict(int)
        for q in r2:
            have[(q['md'], q['k'], ' '.join(q['rns']))] += bool(q['ch'])
        COUNT['V rung 2 model x key with a strict realisation on every grid register (4 x 5)'] = f"{sum(1 for v in have.values() if v == 20)} of {len(have)}"
        if any(v == 0 for v in have.values()):
            fail('V', f"rung 2 model x key with no strict realisation: {[k for k, v in have.items() if v == 0][:5]}")
        vd['cadences rung 2, every model x key x register'] = [q for q in r2 if q['ch']]
        r3 = vd['cadences rung 3, every model x key x register']
        have3 = collections.defaultdict(int)
        for q in r3:
            have3[(q['md'], q['k'], ' '.join(q['rns']))] += bool(q['ch'])
        COUNT['V rung 3 model x key with a strict realisation on every grid register (5 x 5)'] = f"{sum(1 for v in have3.values() if v == 25)} of {len(have3)}"
        if any(v == 0 for v in have3.values()):
            fail('V', f"rung 3 model x key with no strict realisation: {[k for k, v in have3.items() if v == 0][:5]}")
        vd['cadences rung 3, every model x key x register'] = [q for q in r3 if q['ch']]
        sec_V(vd)

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
            const Y=(n,ok,streak,best,shown,skipped,nearly=0)=>({n,ok,streak,best,shown,skipped,nearly});
            const cases=[[[],Y(0,0,0,0,0,0)],[['ok'],Y(1,1,1,1,0,0)],
             [['ok','ok','shown'],Y(2,2,2,2,1,0)],[['ok','skipped','ok'],Y(2,2,2,2,0,1)],
             [['ok','ok','miss','ok'],Y(4,3,1,2,0,0)],[['shown','shown','skipped'],Y(0,0,0,0,2,1)],
             [['miss','shown','ok','skipped','ok','ok'],Y(4,3,3,3,1,1)],
             // 0.48 logic, Nearly: streak kept, not scored (n and ok unchanged), counted in nearly
             [['ok','ok','nearly'],Y(2,2,2,2,0,0,1)],[['ok','nearly','ok'],Y(2,2,2,2,0,0,1)],[['ok','miss','nearly','nearly'],Y(2,1,0,1,0,0,2)],
             [['nearly'],Y(0,0,0,0,0,0,1)],[['ok','nearly','miss'],Y(2,1,0,1,0,0,1)]];
            for(const [ks,want] of cases)o.push({ks,got:run(ks),want});
            // old saved records (no shown/skipped/nearly) are read with zeros, and the input is never changed
            const old={n:3,ok:2,streak:1,best:2},nx=earStatNext(old,'skipped');o.push({ks:['legacy+skipped'],got:nx,want:Y(3,2,1,2,0,1)});
            o.push({ks:['legacy+nearly'],got:earStatNext(old,'nearly'),want:Y(3,2,1,2,0,0,1)});
            o.push({ks:['input unchanged'],got:old,want:{n:3,ok:2,streak:1,best:2}});return o}""")
        for c in unit:
            COUNT['EL-10 stats model unit cases'] += 1
            if c['got'] != c['want']:
                fail('M', f"earStatNext {c['ks']}: {c['got']} != {c['want']}")
        dialogs = []
        pg.on('dialog', lambda d: (dialogs.append(d.message), asyncio.ensure_future(d.dismiss())))
        flow = await pg.evaluate("""async()=>{const o={};const st=()=>({...earSt()}),strip=()=>(document.querySelector('#earMain .el-foot')||{}).textContent||'';
            // 0.48 card: with no question open the Play toggle makes the first one, so [data-earnew] falls back to it
            const click=sel=>{const b=document.querySelector('#earMain '+sel)||(sel==='[data-earnew]'&&document.querySelector('#earMain #earStage [data-earplay="all"]'));if(!b)throw new Error('no '+sel);b.click()};
            window.earPlay=()=>{};EAR.drill='cad';EAR.lvl.cad=2;EAR.st.cad={...EARST0};EAR.q=null;EAR.done=false;renderEar();
            click('[data-earnew]');o.start=st();
            click('[data-earans="'+EAR.q.a+'"]');o.right1=st();click('[data-earnew]');
            click('[data-earans="'+EAR.q.a+'"]');o.right2=st();click('[data-earnew]');
            click('[data-earshow]');o.shown=st();o.shownStrip=strip();o.shownRes=document.querySelector('#earMain .el-result').textContent;click('[data-earnew]');
            EAR.q.plays=1; /* a question counts as skipped only once it has been played (spec 4) */ click('[data-earnew]');o.skipped=st();o.skipStrip=strip();o.toast=document.getElementById('toast').textContent;
            const wrong=EAR.q.opts.find(x=>x!==EAR.q.a);click('[data-earans="'+wrong+'"]');o.miss=st();
            // melody: undo and redo end once the answer is marked (buttons gone, Ctrl+Z does nothing)
            EAR.drill='mel';EAR.lvl.mel=1;EAR.q=null;renderEar();click('[data-earnew]');const q=EAR.q;
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

        # ---------------- N: "Nearly" at cadences rung 3 (Justin 19 Nov 2026, option a) ----------------
        nf = await pg.evaluate("""(mk)=>{const R=eval(mk)(59),o={flags:{nearly:EAR_NEARLY,int:CAD64_INT_NEARLY,hold:CAD3_HOLD,zero:{...EARST0}}};
            const st=()=>({...earSt()}),line=()=>(document.querySelector('#earMain .el-foot')||{}).textContent||'',res=()=>{const e=document.querySelector('#earMain .el-result');return e?(e.querySelector('.el-verdict').textContent+' | '+e.querySelector('.el-teach').textContent):''},
              cls=()=>(document.querySelector('#earMain .el-result')||{}).className||'',lastLog=()=>(LOG[LOG.length-1]||{}).s||'',tally=()=>(document.querySelector('#earMain .el-tally')||{}).getAttribute?document.querySelector('#earMain .el-tally').getAttribute('aria-label'):'';
            window.earPlay=()=>{};S.level=6;EAR.drill='cad';EAR.lvl.cad=3;EAR.st.cad={...EARST0};
            const ask=(l,pred)=>{let q;do{q=earGen('cad',l,R)}while(!pred(q));EAR.lvl.cad=l;EAR.q=q;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();return q};
            const click=v=>document.querySelector(`#earMain [data-earans="${v}"]`).click();
            const step=(name,l,pred,given)=>{const q=ask(l,pred);const g=typeof given==='function'?given(q):given;click(g);o[name]={st:st(),res:res(),cls:cls(),line:line(),tally:tally(),log:lastLog(),judge:earJudge(q,g)}};
            step('right1',3,q=>q.a==='perfect','perfect');step('right2',3,q=>q.a==='plagal','plagal');
            step('nearPhr',3,q=>q.a==='phrygian','imperfect');step('near64',3,q=>q.a==='cad64','perfect');
            step('right3',3,q=>q.a==='imperfect','imperfect');
            // the reverse is wrong: Phrygian for a plain imperfect cadence, Cadential 6/4 for a plain perfect one
            o.rev1=earJudge((()=>{let q;do{q=earGen('cad',3,R)}while(q.a!=='imperfect');return q})(),'phrygian');
            o.rev2=earJudge((()=>{let q;do{q=earGen('cad',3,R)}while(q.a!=='perfect');return q})(),'cad64');
            // Nearly is rung 3 only (rung 2 has no Phrygian or 6/4 answer) and cadences only
            o.r2=earJudge((()=>{let q;do{q=earGen('cad',2,R)}while(q.a!=='imperfect');return q})(),'perfect');
            step('miss',3,q=>q.a==='plagal','perfect');step('nearAfterMiss',3,q=>q.a==='phrygian','imperfect');
            document.querySelector('#earMain [data-earjournal]').click();o.journal=lastLog();
            // reset clears nearly; undo restores it
            const before=st();document.querySelector('#earMain [data-earreset]').click();document.querySelector('#earMain [data-earresetyes]').click();o.zero=st();
            document.querySelector('#earMain [data-earresetundo]').click();o.restored=JSON.stringify(st())===JSON.stringify(before);
            return o}""", RNG)
        COUNT['N flags (EAR_NEARLY on, CAD64_INT_NEARLY on, held models in)'] = 3
        if nf['flags']['nearly'] is not True or nf['flags']['int'] is not True or nf['flags']['hold'] is not False:
            fail('N', f"flags: {nf['flags']}")
        if nf['flags']['zero'] != {'n': 0, 'ok': 0, 'streak': 0, 'best': 0, 'shown': 0, 'skipped': 0, 'nearly': 0}:
            fail('N', f"EARST0 is {nf['flags']['zero']}")
        F7 = ('n', 'ok', 'streak', 'best', 'shown', 'skipped', 'nearly')
        expN = {'right1': (1, 1, 1, 1, 0, 0, 0), 'right2': (2, 2, 2, 2, 0, 0, 0), 'nearPhr': (2, 2, 2, 2, 0, 0, 1), 'near64': (2, 2, 2, 2, 0, 0, 2),
                'right3': (3, 3, 3, 3, 0, 0, 2), 'miss': (4, 3, 0, 3, 0, 0, 2), 'nearAfterMiss': (4, 3, 0, 3, 0, 0, 3)}
        for k, v in expN.items():
            got = tuple(nf[k]['st'][x] for x in F7)
            COUNT['N flow checks'] += 1
            if got != v:
                fail('N', f'after {k}: {dict(zip(F7, got))}, expected {dict(zip(F7, v))}')
        for k in ('nearPhr', 'near64', 'nearAfterMiss'):
            r = nf[k]
            COUNT['N Nearly result checks'] += 1
            if r['judge'] != 'nearly' or not r['res'].startswith('Nearly | ') or 'near' not in r['cls'].split() or not r['log'].endswith('nearly'):
                fail('N', f"{k}: judge {r['judge']}, result '{r['res'][:60]}', class '{r['cls']}', log '{r['log']}'")
            # card foot: "n answered · m nearly · s shown · k skipped" ("answered" excludes nearly); tally "Score ok of n"
            st = r['st']
            if f"{st['n']} answered · {st['nearly']} nearly · {st['shown']} shown · {st['skipped']} skipped" not in r['line'] \
                    or f"Score {st['ok']} of {st['n']}, streak {st['streak']}" not in r['tally']:
                fail('N', f"{k}: foot '{r['line']}', tally '{r['tally']}'")
        if nf['nearPhr']['res'].count('fa to mi') != 1 or re.findall(r'\b(le|so)\b', nf['nearPhr']['res']):
            fail('N', f"Phrygian Nearly text solfa: {nf['nearPhr']['res']}")
        for k in ('rev1', 'rev2', 'r2'):
            COUNT['N reverse / rung 2 checks'] += 1
            if nf[k] != 'wrong':
                fail('N', f'{k}: judged {nf[k]}, expected wrong')
        nt = await pg.evaluate("""()=>({maj:earCadNear('cad64',false,true),min:earCadNear('cad64',true,true),majOff:earCadNear('cad64',false,false),minOff:earCadNear('cad64',true,false),
            one:typeof EARNEAR==='undefined'&&typeof earNearTxt==='undefined'&&typeof EAR64INT==='undefined'})""")
        for k, (V, six) in {'maj': ('V to I close', '(I⁶₄)'), 'min': ('V to i close', '(i⁶₄)'), 'majOff': ('V to I close', '(I⁶₄)'), 'minOff': ('V to i close', '(i⁶₄)')}.items():
            if V not in nt[k] or six not in nt[k]:
                fail('N', f'cadential 6/4 Nearly text is not mode-aware ({k}): {nt[k]}')
        if not nt['one']:
            fail('N', 'a second Nearly text source (EARNEAR / earNearTxt / EAR64INT) still exists')
        COUNT['N flow checks'] += 1
        if not nf['journal'].endswith(', 3 nearly'):
            fail('N', f"journal line: {nf['journal']}")
        if nf['zero'].get('nearly') != 0 or not nf['restored']:
            fail('N', f"reset: {nf['zero']}, undo restored {nf['restored']}")
        COUNT['N flow checks'] += 2

        # ---------------- I: interrupted after a cadential 6/4 (kept; answer "Interrupted") ----------------
        ii = await pg.evaluate("""(mk)=>{const R=eval(mk)(61),o={held:CAD3_HELD.slice(),inPool:CAD3_HELD.filter(x=>Object.values(CADT[3]).some(m=>(m.interrupted||[]).includes(x))),items:[],fb:{},judge:{},near:{}};
            for(let i=0;i<12000;i++){const q=earGen('cad',3,R);o.items.push({a:q.a,md:q.key.mode,k:q.key.k,rns:q.rns,ch:q.ch,i64:earCad64Int(q)})}
            window.earPlay=()=>{};S.level=6;EAR.drill='cad';EAR.lvl.cad=3;
            for(const md of ['maj','min']){let q;do{q=earGen('cad',3,R)}while(!earCad64Int(q)||q.key.mode!==md);o.fb[md]=earTeachCad(q,{kind:'shown',given:null}).teach;
              o.judge[md]={interrupted:earJudge(q,'interrupted'),cad64:earJudge(q,'cad64'),perfect:earJudge(q,'perfect'),imperfect:earJudge(q,'imperfect')};
              for(const flag of [false,true]){CAD64_INT_NEARLY=flag;EAR.st.cad={...EARST0,n:5,ok:4,streak:3,best:3};EAR.q=q;EAR.done=false;EAR.res=null;renderEar();
                document.querySelector('#earMain [data-earans="cad64"]').click();const e=document.querySelector('#earMain .el-result');o.near[md+'|'+flag]={res:e.querySelector('.el-verdict').textContent+' | '+e.querySelector('.el-teach').textContent,
                  chips:[...e.querySelectorAll('.el-ch')].map(c=>({t:c.title,s:(c.querySelector('small')||{}).textContent||''})),st:{...earSt()},judge:earJudge(q,'cad64')};
                if(!flag){EAR.q=q;EAR.done=false;EAR.res=null;renderEar();document.querySelector('#earMain [data-earans="interrupted"]').click();o.panelRight=o.panelRight||{};
                  o.panelRight[md]=document.querySelector('#earMain .el-result .el-teach').textContent}}
              CAD64_INT_NEARLY=true}
            // a plain interrupted cadence (no 6/4) gets no 6/4 sentence; a cadential 6/4 item answered Interrupted is plain wrong
            let q;do{q=earGen('cad',3,R)}while(q.a!=='interrupted'||earCad64Int(q));o.plain=earTeachCad(q,{kind:'shown',given:null}).teach;
            do{q=earGen('cad',3,R)}while(q.a!=='cad64');o.c64int=earJudge(q,'interrupted');
            return o}""", RNG)
        if sorted(ii['inPool']) != sorted(ii['held']):
            fail('I', f"interrupted-after-6/4 models in the rung 3 pool: {ii['inPool']} of {ii['held']}")
        i64 = [q for q in ii['items'] if q['i64']]
        COUNT['I interrupted-after-6/4 items (of 12,000)'] = len(i64)
        for q in i64:
            if q['a'] != 'interrupted' or 'I:2' not in q['rns'] and 'i:2' not in q['rns']:
                fail('I', f"item flagged as interrupted after a 6/4 is {q['a']} {q['rns']}")
                break
            if not cad_ok('interrupted', q['rns'], q['k'], q['md']) or cad_ok('cad64', q['rns'], q['k'], q['md']):
                fail('I', f"{q['rns']}: interrupted {cad_ok('interrupted', q['rns'], q['k'], q['md'])}, cadential 6/4 {cad_ok('cad64', q['rns'], q['k'], q['md'])}")
                break
            e = ic_errors(q) + vl_errors(q['ch'], q['rns'], q['k'], q['md'])
            if e:
                fail('I', f"{q['md']} {NM[q['k']]} {q['rns']}: strict SATB {e[:3]}")
                break
        # the 6/4 is the tonic in second inversion over so, preceded by IV (iv), followed by V on the same bass (or its octave), then vi (VI) a step up
        for q in i64:
            j = q['rns'].index('I:2' if q['md'] == 'maj' else 'i:2')
            b64, bV, bvi = q['ch'][j][0], q['ch'][j + 1][0], q['ch'][j + 2][0]
            if (b64 - q['k']) % 12 != 7 or (b64 - bV) % 12 != 0 or (bvi - bV) not in (1, 2, -10, -11) or (bvi - q['k']) % 12 != (9 if q['md'] == 'maj' else 8):
                fail('I', f"{q['md']} {NM[q['k']]} {q['rns']}: bass {b64}-{bV}-{bvi} is not so-so-(la or le)")
                break
            COUNT['I bass-line checks'] += 1
        dist = collections.defaultdict(set)
        for q in i64:
            dist[q['md']].add((q['k'], json.dumps(q['ch'])))
        for md in ('maj', 'min'):
            COUNT[f'I distinct interrupted-after-6/4 items, {md}'] = len(dist[md])
            if len(dist[md]) < 40:
                fail('I', f'{md}: only {len(dist[md])} distinct interrupted-after-6/4 items')
        intr = [q for q in ii['items'] if q['a'] == 'interrupted']
        COUNT['I share of interrupted items that pass through a 6/4'] = f'{len(i64)}/{len(intr)}'
        # the 6/4 alone does not give the answer: among items with a cadential 6/4 in them, both answers occur (reported)
        with64 = collections.Counter(q['a'] for q in ii['items'] if any(t.endswith(':2') for t in q['rns']))
        COUNT['I answers of items containing a 6/4'] = json.dumps(dict(with64))
        if set(with64) != {'cad64', 'interrupted'}:
            fail('I', f'items containing a 6/4 are {dict(with64)}')
        for md, txt in ii['fb'].items():
            vi = 'vi' if md == 'maj' else 'VI'
            COUNT['I feedback checks'] += 1
            if not txt.startswith(f'An interrupted cadence: V sets up the close, then the bass steps up to {vi}') or 'comes on the way, but the cadence itself is interrupted' not in txt or f'(V–{vi})' not in txt:
                fail('I', f'{md} feedback: {txt}')
        # the card's result panel, answered Interrupted: the spec sentence plus the 6/4 sentence (one source, CAD64INT)
        for md, txt in ii['panelRight'].items():
            vi, I = ('vi', 'I') if md == 'maj' else ('VI', 'i')
            COUNT['I feedback checks'] += 1
            if not txt.startswith(f'An interrupted cadence: V sets up the close, then the bass steps up to {vi}') or f'A cadential 6/4 ({I}⁶₄, the home chord over the dominant bass) comes on the way, but the cadence itself is interrupted (V–{vi}).' not in txt:
                fail('I', f'{md} panel, answered Interrupted: {txt}')
        if 'cadential 6/4' in ii['plain'].lower():
            fail('I', f"a plain interrupted cadence mentions the 6/4: {ii['plain']}")
        for md, j in ii['judge'].items():
            # BHL 0.48 (Justin 20 Nov 2026, item B): with the switch at its default (on), "Cadential 6/4" here is Nearly
            if j != {'interrupted': 'correct', 'cad64': 'nearly', 'perfect': 'wrong', 'imperfect': 'wrong'}:
                fail('I', f'{md} judging: {j}')
        F7 = ('n', 'ok', 'streak', 'best', 'shown', 'skipped', 'nearly')
        for k, r in ii['near'].items():
            md, flag = k.split('|')
            got = tuple(r['st'][x] for x in F7)
            COUNT['I CAD64_INT_NEARLY checks'] += 1
            if flag == 'false':
                if r['judge'] != 'wrong' or not r['res'].startswith('Not this time | ') or got != (6, 4, 0, 3, 0, 0, 0) or 'and that is right' in r['res']:
                    fail('I', f'"Cadential 6/4" on an interrupted-after-6/4 item ({md}, switch off): {r["judge"]}, {dict(zip(F7, got))}, "{r["res"][:50]}"')
            else:
                if r['judge'] != 'nearly' or not r['res'].startswith('Nearly | ') or got != (5, 4, 3, 3, 0, 0, 1):
                    fail('I', f'"Cadential 6/4" on an interrupted-after-6/4 item ({md}, switch on): {r["judge"]}, {dict(zip(F7, got))}, "{r["res"][:50]}"')
            vi, I = ('vi', 'I') if md == 'maj' else ('VI', 'i')
            lead = 'You heard the cadential 6/4, and it is there' if flag == 'false' else 'You heard the cadential 6/4, and that is right'
            if lead not in r['res'] or f'so the cadence itself is interrupted (V–{vi})' not in r['res'] or f'{I}⁶₄ over the dominant bass' not in r['res'] or 'held dominant bass' in r['res']:
                fail('I', f'"Cadential 6/4" on an interrupted-after-6/4 item ({k}): feedback "{r["res"]}"')
            # the chord strip: the 6/4 before the cadence is named "cadential 6/4", not "tonic", and its title gives both readings
            c64 = [c for c in r['chips'] if c['s'] == 'cadential 6/4']
            if len(c64) != 1 or 'tonic chord' not in c64[0]['t'] or 'part of the dominant' not in c64[0]['t'] or any(c['s'] == 'tonic' and '⁶₄' in c['t'] for c in r['chips']):
                fail('I', f'chord strip ({k}): {r["chips"]}')
        if ii['c64int'] != 'wrong':
            fail('I', f"Interrupted for a cadential 6/4 item is judged {ii['c64int']}")

        # ---------------- T: Pulse and metre ----------------
        MF = json.loads((pathlib.Path(__file__).resolve().parent / 'fixtures' / 'metre_items.json').read_text())
        mt = await pg.evaluate("""(mk)=>{const R=eval(mk)(67),o={opts:{1:earMetreOpts(1),2:earMetreOpts(2),3:earMetreOpts(3)},label:METL,stage:EARSTAGE.metre,tag:earStageTag('metre'),
              edr:EDR.find(x=>x[0]==='metre')[2],items:[]};
            for(const l of [1,2,3])for(let i=0;i<6000;i++){const q=earGen('metre',l,R),barLen=q.len/4,nb=Math.max(4,Math.round((q.dur||10)/barLen),Math.ceil(10/barLen-1e-9));
              const bars=[0,1,2,3].map(b=>q.ev.filter(e=>e.t>=b*barLen-1e-6&&e.t<(b+1)*barLen-1e-6).map(e=>({t:+(e.t-b*barLen).toFixed(5),a:e.a})));
              o.items.push({l,a:q.a,bpm:q.bpm,len:q.len,dur:q.dur,nb,play:nb*barLen,n:q.ev.length,bars,lvl:q.lvl})}
            // the scheduler's own bar count (the same rule, from the app): a few items through earSchedMetre with a silent click
            const oc=window.earClick,ot=window.c2Tone;window.earClick=()=>{};window.c2Tone=()=>{};o.sched=[];
            try{for(let i=0;i<300;i++){const q=earGen('metre',1+i%3,R),S=earSchedMetre(q,ELPRE),d=S.events[S.events.length-1].t-S.lead;o.sched.push({span:d,barLen:q.len/4,dur:q.dur})}}finally{window.earClick=oc;window.c2Tone=ot}
            return o}""", RNG)
        from music21 import meter
        rows = {r['sig']: r for r in MF['metres']}
        for l in (1, 2, 3):
            want = [r['sig'] for r in MF['metres'] if r['rung'] <= l]
            COUNT['T answer grid per rung'] += 1
            if mt['opts'][str(l)] != want:
                fail('T', f"rung {l}: earMetreOpts {mt['opts'][str(l)]}, fixture {want}")
        if mt['stage'] != MF['stage'] or mt['tag'] != 'Stage 4–5' or mt['edr'] != '4–5':
            fail('T', f"metre Stages: EARSTAGE {mt['stage']}, tag {mt['tag']}, EDR {mt['edr']}")
        for sig, r in rows.items():
            COUNT['T fixture rows'] += 1
            if mt['label'].get(sig) != r['label']:
                fail('T', f"{sig}: label {mt['label'].get(sig)}, fixture {r['label']}")
            ts = meter.TimeSignature(sig)
            if r['kind'] != 'irregular':
                # music21: beat count and the split of one beat (simple 2, compound 3)
                if ts.beatCount != r['beats'] or ts.beatDivisionCount != r['split'] or ts.classification.split()[0].lower() != r['kind'] \
                        or ts.classification.split()[1].lower() != r['label'].split()[1].lower():
                    fail('T', f"{sig}: music21 {ts.beatCount} beats, split {ts.beatDivisionCount}, '{ts.classification}' vs fixture {r}")
            else:
                # unequal beats: the grouping adds up to the bar, and the accented clicks fall at the start of each group
                if sum(r['group']) != ts.numerator:
                    fail('T', f"{sig}: grouping {r['group']} does not add up to {ts.numerator}")
                starts = [sum(r['group'][:i]) for i in range(len(r['group']))]
                at = [i for i, a in enumerate(r['accents']) if a >= 1] if r['unit'] == 'crotchet' else [starts[i] for i, a in enumerate(r['accents']) if a >= 1]
                if at != starts:
                    fail('T', f"{sig}: accents {r['accents']} are not at the group starts {starts}")
        by = collections.defaultdict(list)
        for q in mt['items']:
            by[q['l']].append(q)
        for l, qs in by.items():
            cnt = collections.Counter(q['a'] for q in qs)
            COUNT[f'T rung {l} answers'] = json.dumps(dict(sorted(cnt.items())))
            if set(cnt) != set(mt['opts'][str(l)]):
                fail('T', f'rung {l}: answers drawn {sorted(cnt)}')
            if max(cnt.values()) / len(qs) > 1 / len(cnt) + 0.03:
                fail('T', f'rung {l}: unbalanced {dict(cnt)}')
        # every item: its bars match the fixture (beats, accents, split) - read from the events, not from METRES
        bad = 0
        for q in mt['items']:
            r = rows[q['a']]
            bd = 60 / q['bpm']
            for bar in q['bars']:
                beats = [e for e in bar if e['a'] >= 0]
                acc = [e['a'] for e in beats]
                if acc != r['accents']:
                    bad += 1; fail('T', f"{q['a']} rung {q['l']}: accents {acc}, fixture {r['accents']}") if bad < 4 else None
                    break
                if r.get('unit') == 'quaver':
                    q8 = bd / 2
                    starts = [round(e['t'] / q8) for e in bar]
                    grp = [b - a for a, b in zip(starts, starts[1:] + [sum(r['group'])])]
                    if starts != list(range(sum(r['group']))) or [round(e['t'] / q8) for e in beats] != [sum(r['group'][:i]) for i in range(len(r['group']))]:
                        bad += 1; fail('T', f"{q['a']}: quaver grouping {starts}") if bad < 4 else None
                        break
                else:
                    pos = [round(e['t'] / bd * r['split'], 4) for e in bar]
                    if any(abs(p - round(p)) > 1e-3 for p in pos) or [round(e['t'] / bd, 4) for e in beats] != list(range(r['beats'])):
                        bad += 1; fail('T', f"{q['a']}: onsets {pos} are not on the beat or its {r['split']}-way split") if bad < 4 else None
                        break
            if abs(q['len'] - 4 * r['bar_beats'] * bd) > 1e-6:
                bad += 1; fail('T', f"{q['a']}: four bars last {q['len']:.3f} s, expected {4 * r['bar_beats'] * bd:.3f}") if bad < 4 else None
            if q['lvl'] != q['l'] or not 60 <= q['bpm'] <= 120 or not 11 <= q['dur'] <= 17:
                bad += 1; fail('T', f"{q['a']}: rung {q['lvl']}, bpm {q['bpm']}, drawn length {q['dur']}") if bad < 4 else None
            if q['nb'] < 4 or q['play'] < 10 - 1e-6:
                bad += 1; fail('T', f"{q['a']} at {q['bpm']}: {q['nb']} bars, {q['play']:.2f} s") if bad < 4 else None
        COUNT['T metre items checked (bars against the fixture)'] = len(mt['items'])
        for x in mt['sched']:
            bars = x['span'] / x['barLen']
            if abs(bars - round(bars)) > 1e-6 or round(bars) < 4 or x['span'] < 10 - 1e-6:
                fail('T', f"earSchedMetre plays {bars:.2f} bars, {x['span']:.2f} s")
                break
            if abs(round(bars) - max(4, round(x['dur'] / x['barLen'] + 1e-9), -(-10 // x['barLen']))) > 1:
                fail('T', f"earSchedMetre plays {round(bars)} bars for a drawn length of {x['dur']:.2f} s")
                break
        COUNT['T scheduler checks'] = len(mt['sched'])
        # tells: no metre from tempo or from how long it plays (the playing time is on screen); the simple/compound split too
        A = lambda r: r['a']
        SC = lambda r: rows[r['a']]['kind']
        for l, qs in by.items():
            W = f'metre rung {l}'
            for name, f in (('tempo (bpm)', lambda r: r['bpm']), ('tempo (10-bpm bands)', lambda r: r['bpm'] // 10),
                            ('playing time (whole seconds)', lambda r: int(r['play'] + .6)), ('playing time (0.5 s)', lambda r: round(r['play'] * 2))):
                tell('T', qs, name, f, A, W)
                if l > 1:
                    tell('T', qs, name + ', simple or compound', f, SC, W)
            # reported, not failed: tempo and playing time together. Whole bars at a known tempo make the total number of beats a multiple
            # of the beats in a bar, so the pair carries the metre itself (counting every beat of 14 s and dividing is hearing the metre).
            acc, ch = predict_acc(qs, lambda r: (r['bpm'] // 10, int(r['play'] + .6)), A)
            COUNT[f'info: {W}, tempo and playing time together (10 bpm, whole seconds): accuracy vs chance'] = f'{acc:.0%} vs {ch:.0%}'
            # reported, not failed: the speed of the fastest clicks and the number of clicks. Compound beats split in three, so at the
            # same beat tempo the clicks come 1.5 times as fast; making that speed even would make the beat tempo a tell instead.
            for name, f in (('fastest click (25 ms bands)', lambda r: round(min(b2['t'] - b1['t'] for bar in r['bars'] for b1, b2 in zip(bar, bar[1:])) / .025)),
                            ('number of clicks (5s)', lambda r: (r['n'] * r['nb'] // 4) // 5)):
                acc, ch = predict_acc(qs, f, A)
                acc2, ch2 = predict_acc(qs, f, SC) if l > 1 else (0, 0)
                COUNT[f'info: {W}, {name}: metre / simple-compound accuracy vs chance'] = f'{acc:.0%} vs {ch:.0%}' + (f' / {acc2:.0%} vs {ch2:.0%}' if l > 1 else '')

        # ---------------- P: every cadence result-panel sentence is true of its item (reconcile 0.48) ----------------
        pt = await pg.evaluate("""(mk)=>{const R=eval(mk)(71),o=[];const N0=EAR_NEARLY,C0=CAD64_INT_NEARLY;
            try{for(const l of [1,2,3])for(let i=0;i<(l===3?4000:2000);i++){const q=earGen('cad',l,R),T={};
              for(const g of [null,...q.opts])for(const nf of (l===3?[true,false]:[true]))for(const cf of (l===3&&earCad64Int(q)&&g==='cad64'?[false,true]:[false])){
                EAR_NEARLY=nf;CAD64_INT_NEARLY=cf;const j=g===null?'shown':earJudge(q,g),kind=g===null?'shown':j==='correct'?'ok':j==='nearly'?'nearly':'miss';
                T[`${g}|${nf}|${cf}`]={kind,t:earTeachCad(q,{kind,given:g}).teach}}
              const P=document.createElement('div');P.innerHTML=earChordRowHTML(q);
              const chips=[...P.querySelectorAll('.el-ch')].map(c=>({t:c.title,s:(c.querySelector('small')||{}).textContent||'',cad:!!c.closest('.el-cad')}));
              o.push({l,a:q.a,md:q.key.mode,k:q.key.k,rns:q.rns,ch:q.ch,i64:earCad64Int(q),T,chips})}}finally{EAR_NEARLY=N0;CAD64_INT_NEARLY=C0}return o}""", RNG)
        bad = collections.Counter(); ex = {}
        def flag(rule, q, key, t):
            bad[rule] += 1
            ex.setdefault(rule, f"rung {q['l']} {q['md']} {q['a']} [{' '.join(q['rns'])}] given {key}: {t}")
        for q in pt:
            k, ch, rns, md = q['k'], q['ch'], q['rns'], q['md']
            dg = lambda m: (m - k) % 12
            P, Nn = ch[-2], ch[-1]
            mv = Nn[0] - P[0]
            do_held = any(dg(P[v]) == 0 and Nn[v] == P[v] for v in range(4))
            so_held = any(b[0] == a[0] and dg(a[0]) == 7 for a, b in zip(ch, ch[1:]))
            has64 = any(t.endswith(':2') for t in rns)
            for key, r in q['T'].items():
                t, kind = r['t'], r['kind']
                g = key.split('|')[0]
                COUNT['P panel sentences checked'] += 1
                if 'held dominant bass' in t: flag('says "no held dominant bass"', q, key, t)
                if 'bass falls to the home note' in t and mv >= 0: flag('says the bass falls home, it rises', q, key, t)
                if 'bass rises to the home note' in t and mv <= 0: flag('says the bass rises home, it falls', q, key, t)
                if 'is held through both chords' in t and not do_held: flag('says the home note is held, it is not', q, key, t)
                if re.search(r'steps up to (vi|VI)', t) and q['a'] == 'interrupted' and mv not in (1, 2): flag('says the bass steps up to vi', q, key, t)
                if re.search(r'no [Ii]⁶₄', t) and has64 and 'does stay on' not in t: flag('says there is no 6/4, there is one', q, key, t)
                if 'You heard IV near the end, and that is right' in t or 'You heard iv near the end, and that is right' in t:
                    if not re.match(r'^(IV|iv)(:|$)', rns[-2]) and q['a'] == 'imperfect': flag('says IV is near the end, it is not', q, key, t)
                if 'does not fall a semitone into V' in t and mv == -1: flag('says no semitone into V, there is one', q, key, t)
                # IC_EAR_048 C1: "stays on so" (mi in minor) only on the same pitch; an octave move is said ("dropping an octave into V")
                if 'stays on it' in t: flag('"stays on it" (the 0.48 wording that ignored an octave drop)', q, key, t)
                if re.search(r'stays on (so|mi)\b', t) and q['a'] == 'cad64':
                    j = max(i for i, x in enumerate(rns) if x.endswith(':2'))
                    mv64 = ch[j + 1][0] - ch[j][0]
                    said = 'dropping an octave into V' in t and -12 or 'rising an octave into V' in t and 12 or 0
                    if mv64 != said: flag(f'says the 6/4 bass moves {said} into V, it moves {mv64}', q, key, t)
                    COUNT['P 6/4-into-V bass sentences checked (of them, an octave move)'] += 1
                    if mv64: COUNT['P 6/4-into-V bass sentences: octave move said'] += 1
                if 'does stay on' in t and not so_held: flag('says the bass stays on so (V–V7), it does not', q, key, t)
                if ('comes on the way' in t or 'You heard the cadential 6/4' in t) != q['i64']: flag('6/4-on-the-way sentence on the wrong items', q, key, t)
                if md == 'min':
                    if re.search(r'\b(vi|IV|I)\b|I⁶₄|\b(bass|on) so\b|\ble\b', t): flag('major numeral or do-based solfa in a minor key', q, key, t)
                else:
                    if re.search(r'\b(VI|iv|i)\b|i⁶₄', t) and 'iv⁶' not in t: flag('minor numeral in a major key', q, key, t)
                    if 'fa to mi' in t and 'Phrygian' not in t: flag('fa to mi outside a Phrygian sentence', q, key, t)
                # a wrong mark never calls the answer given right; Nearly and right marks never say "not"
                if kind == 'miss' and g in ('imperfect', 'perfect', 'cad64') and re.search(r'and that is right: this is|that is right\. Listen just before V|cadential 6/4, and that is right', t):
                    flag('marked wrong but the text calls the answer right', q, key, t)
                if kind == 'nearly' and 'and that is right' not in t: flag('Nearly without "that is right"', q, key, t)
        # IC_EAR_048 S4: wherever a 6/4 is followed by V (a cadential 6/4), its chip reads "cadential 6/4", inside the cadence bracket too,
        # and its title gives both readings (tonic in second inversion, Ic, as Analysis labels it; part of the dominant) and the bass solfa
        for q in pt:
            for i, rn in enumerate(q['rns']):
                if not (rn.endswith(':2') and i + 1 < len(q['rns']) and q['rns'][i + 1].startswith('V')):
                    continue
                c = q['chips'][i]
                COUNT['P cadential 6/4 chips checked'] += 1
                if c['s'] != 'cadential 6/4' or 'second inversion' not in c['t'] or 'c),' not in c['t'] or 'part of the dominant' not in c['t'] \
                        or f"(bass {'mi' if q['md'] == 'min' else 'so'})" not in c['t']:
                    bad[f"cadential 6/4 chip {'in' if c['cad'] else 'before'} the cadence bracket reads \"{c['s']}\""] += 1
                    ex.setdefault(f"cadential 6/4 chip {'in' if c['cad'] else 'before'} the cadence bracket reads \"{c['s']}\"", f"rung {q['l']} {q['md']} {q['a']} [{' '.join(q['rns'])}]: {c}")
        COUNT['P panel items'] = len(pt)
        for rule, n in bad.items():
            fail('P', f'{rule}: {n} sentences, e.g. {ex[rule]}')

        # ---------------- B: blind analysis sentences are true of each excerpt (IC_EAR_048 S5) ----------------
        bl = await pg.evaluate("""async()=>{await earLoadBlind();const o=[];const N0=EAR_NEARLY;
            for(const x of EAR.blind){const q={d:'blind',...x,a:x.cat,l:3,lvl:3},T={};
              for(const g of [null,...earBlindCats(3)]){const j=g===null?'shown':earJudge(q,g),kind=g===null?'shown':j==='correct'?'ok':j==='nearly'?'nearly':'miss';
                const d=document.createElement('div');d.innerHTML=earTeachCad(q,{kind,given:g}).teach;T[String(g)]={kind,t:d.textContent}}
              o.push({score:x.score,bar:x.bar,key:x.key,chords:x.chords,label:x.label,cat:x.cat,s:x.s,e:x.e,T})}return o}""")
        meta = json.loads((REPO / 'scores' / 'meta.json').read_text())
        fig = lambda t: re.sub(r'(64|65|43|42|6)(?=$|[/\s)])', lambda m: {'64': '⁶₄', '65': '⁶₅', '43': '⁴₃', '42': '⁴₂', '6': '⁶'}[m.group(1)], t)
        COUNT['B blind excerpts'] = len(bl)
        for x in bl:
            where = f"{x['score']} bar {x['bar']} ({x['chords']})"
            toks = [fig(t) for t in re.split(r'\s*–\s*', x['chords'])]
            fin, pen = toks[-1], toks[-2]
            minor = 'minor' in x['key']
            lk = re.search(r'cadence in ([A-G][♭♯]? (?:major|minor))', x['label'])
            for g, r in x['T'].items():
                t = r['t']
                COUNT['B blind sentences checked'] += 1
                # no claim about a single voice: the excerpts have no voicing, and the leading note falls in two of them
                if 'leading note' in t:
                    fail('B', f'{where} given {g}: names the leading note: {t}')
                # the numerals said are the excerpt's own (a minor V–i says "to i", never "V to I")
                if (re.search(r'\bV to I\b', t) and fin != 'I') or (minor and fin == 'i' and re.search(r'\bI\b', t)):
                    fail('B', f'{where} given {g}: major numerals for a V–i excerpt: {t}')
                if x['cat'] == 'perfect' and ' – '.join(toks) not in t and f'to {fin},' not in t:
                    fail('B', f'{where} given {g}: does not name the last chord {fin}: {t}')
                if x['cat'] == 'imperfect' and f'stops on {fin}' not in t:
                    fail('B', f'{where} given {g}: does not say it stops on {fin}: {t}')
                if bool(lk) != ('tonicisation' in t or 'the dominant of' in t or 'the tonic of' in t) or (lk and lk.group(1) not in t):
                    fail('B', f'{where} given {g}: the key it cadences in ({lk and lk.group(1)}) is not said, or said wrongly: {t}')
                if 'Picardy' in t and not (minor and fin == 'I'):
                    fail('B', f'{where} given {g}: Picardy third on a {fin} ending in {x["key"]}: {t}')
            # "the bass lands on the root" of the last chord: the lowest note sounding at the arrival (meta.json events), against music21
            if x['cat'] == 'perfect' and any('bass lands on' in r['t'] for r in x['T'].values()):
                M = meta[x['score']]
                cad = next(c for c in M['cads'] if c['ch'] == x['chords'] and c.get('e') == x['e'])
                at = [e for e in M['events'] if e[0] <= cad['a'] + 5 < e[0] + e[2]]
                tonic, mode = x['key'].split()
                K = m21key.Key(tonic.replace('♭', '-').replace('♯', '#'), mode)
                root = roman.RomanNumeral(re.sub(r'\(.*?\)|[⁶₄₅⁴₂]', '', fin), K).root().pitchClass
                COUNT['B blind bass-on-root checks'] += 1
                if not at or min(e[1] for e in at) % 12 != root:
                    fail('B', f'{where}: says the bass lands on the root of {fin}, the lowest note at the arrival is {at and NM[min(e[1] for e in at) % 12]}')

        # ---------------- T2: metre sentences claim only what every item plays (IC_EAR_048 S6) ----------------
        # each split click sounds three times in four, so "you heard ... in every bar / each beat" is true only if every split sounded
        ms = await pg.evaluate("""(mk)=>{const R=eval(mk)(73),o=[];for(const l of [1,2,3])for(let i=0;i<600;i++){const q=earGen('metre',l,R),M=METRES[q.a];
              const full=q.a==='7/8'||q.ev.filter(e=>e.a===-1).length===4*M.b*(M.sub-1),T={};
              for(const g of [null,...earMetreOpts(l)]){const j=g===null?'shown':earJudge(q,g),kind=g===null?'shown':j==='correct'?'ok':'miss';T[String(g)]=earTeachMetre(q,{kind,given:g}).teach}
              o.push({l,a:q.a,full,T})}return o}""", RNG)
        t2 = collections.Counter(); t2x = {}
        for q in ms:
            for g, t in q['T'].items():
                COUNT['T2 metre sentences checked'] += 1
                m = re.search(r'You heard[^.]*?\b(every|each) (bar|beat|one)\b', t)
                if m and not q['full']:
                    t2[m.group(0)] += 1; t2x.setdefault(m.group(0), f"{q['a']} given {g}: {t}")
                if re.search(r'inside one beat: it splits', t) and not q['full']:
                    t2['inside one beat: it splits'] += 1; t2x.setdefault('inside one beat: it splits', f"{q['a']} given {g}: {t}")
        for rule, n in t2.items():
            fail('T2', f'"{rule}" where some split clicks did not sound: {n} sentences, e.g. {t2x[rule]}')

        # sections N and I leave the cadence drill on rung 3; put it back where section M left it (rung 2, no open question), because section U
        # expects the saved rung to be inside the Stage
        await pg.evaluate("()=>{EAR.lvl.cad=2;EAR.q=null;EAR.done=false;EAR.res=null;EAR.st.cad={...EARST0};CAD64_INT_NEARLY=true;EAR_NEARLY=true;renderEar()}")
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
                    for(const n of rungs){document.querySelector(`#earMain [data-earlv="${n}"]`).click();if(d==='blind')await earLoadBlind();(document.querySelector('#earMain [data-earnew]')||document.querySelector('#earMain #earStage [data-earplay="all"]')).click();
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
            (document.querySelector('#earMain [data-earnew]')||document.querySelector('#earMain #earStage [data-earplay="all"]')).click();const q1=EAR.q;EAR.q.plays=1;document.querySelector('#earMain [data-earlv="3"]').click();
            const o={st:{...earSt()},q:EAR.q,toast:document.getElementById('toast').textContent,lvl:earLvl(),line:document.querySelector('#earMain .el-foot').textContent};
            (document.querySelector('#earMain [data-earnew]')||document.querySelector('#earMain #earStage [data-earplay="all"]')).click();document.querySelector('#earMain [data-earans="'+EAR.q.a+'"]').click();document.querySelector('#earMain [data-earlv="2"]').click();
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
