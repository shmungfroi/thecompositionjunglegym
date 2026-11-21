"""Ear Lab test (register 0.46, items E1–E15).
Run: python3 tests/earlab_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

The app generates the questions; this file re-derives what they should be, independently, with music21 and its own
voice-leading rules, and fails on any mismatch. It does not call the app's own checker to decide a pass, except where
the register asks for it ("passes the existing SATB checker"), and then it checks with its own rules as well.

Sections
  A  cadence models: every template x key x level  (E8, E9, E10)
  B  bass and numerals: every progression x key x level; 6,000 generated questions against the allow-list (E8, E9, E11);
     BHL 0.48 (IC_EAR_048 S3): no cadence model, bass progression or generated question moves ii(6) to IV or ii°(6) to iv
  C  tells: no answer predictable above chance from length, tempo or register (E10); 0.49 C3: exact-semitone register tells at rungs 2-3
  D  pool sizes at level 1 (E11); 0.49 C4: the rung 1 V–vi pool against an independent exhaustive enumeration
  E  blind analysis windows, labels and buttons (E1–E5)
  F  blind playback note lengths (E6)
  G  ranges (E14)
  H  text (E7, E12)
  I  every drill at every level renders and marks without page errors
  J  fixtures from the independent checker (tests/fixtures/earlab_ic.json), when present
  L  0.49 ladders (LADDER_REGISTER_049): pools, tells (5,000 seeded items a rung), new-thing share, range and do = 60 + pc, RF and the
     anacrusis rule, names (D12), M9 pivot window and both readings (D8), M11 outer voices (2,000 items, independent checker), marking
     (D4, D11, R8, R9), readiness (D10), the duration palette (L103), playback. All labelled self-check: the build's own checks.
"""
import sys, asyncio, json, pathlib, collections, random

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import roman, key as m21key, pitch as m21pitch

FAIL = collections.defaultdict(list)
COUNT = collections.Counter()
def fail(sec, msg):
    FAIL[sec].append(msg)

NM = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
TON = ['C', 'D-', 'D', 'E-', 'E', 'F', 'F#', 'G', 'A-', 'A', 'B-', 'B']


def m21key_of(k, mode):
    t = TON[k % 12]
    if mode == 'min':
        t = {'D-': 'C#', 'A-': 'G#'}.get(t, t)
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
    pcs = {p.pitchClass for p in r.pitches}
    sev = r.seventh.pitchClass if r.seventh is not None else None
    third = r.third.pitchClass if r.third is not None else None
    return dict(pcs=pcs, root=r.root().pitchClass, bass=r.bass().pitchClass, third=third, seventh=sev,
                scale_degree=r.scaleDegree, secondary=r.secondaryRomanNumeral is not None, figure=r.figure)


PERFECT = {0: 'P1', 7: 'P5'}


def vl_check(chs, toks, k, mode, where):
    """Independent strict-SATB rules. chs: list of [B,T,A,S] MIDI numbers."""
    tonic = k % 12
    lt = (tonic + 11) % 12
    info = [rn_info(t, k, mode) for t in toks]
    RANGES = [(40, 60), (48, 67), (55, 74), (60, 79)]
    for i, (c, f) in enumerate(zip(chs, info)):
        pcs = {m % 12 for m in c}
        if not pcs <= f['pcs']:
            fail('A', f'{where}: chord {i+1} {toks[i]} has {sorted(NM[p] for p in pcs - f["pcs"])} not in {f["figure"]}')
        need = {f['root'], f['third']} | ({f['seventh']} if f['seventh'] is not None else set())
        if not need <= pcs:
            fail('A', f'{where}: chord {i+1} {toks[i]} is missing root, 3rd or 7th')
        if c[0] % 12 != f['bass']:
            fail('A', f'{where}: chord {i+1} {toks[i]} bass {NM[c[0]%12]} should be {NM[f["bass"]]}')
        for v, (lo, hi) in enumerate(RANGES):
            if not lo <= c[v] <= hi:
                fail('G', f'{where}: chord {i+1} voice {v} {c[v]} outside {lo}-{hi}')
        if any(c[v] > c[v+1] for v in range(3)):
            fail('A', f'{where}: chord {i+1} voices cross')
        if c[3] - c[2] > 12 or c[2] - c[1] > 12:
            fail('A', f'{where}: chord {i+1} upper voices more than an octave apart')
    for i in range(len(chs) - 1):
        P, N, f0, f1 = chs[i], chs[i+1], info[i], info[i+1]
        for a in range(4):
            for b in range(a + 1, 4):
                i0, i1 = (P[b] - P[a]) % 12, (N[b] - N[a]) % 12
                da, db = N[a] - P[a], N[b] - P[b]
                if i0 in PERFECT and i0 == i1 and (da or db) and da != 0 and db != 0:
                    fail('A', f'{where}: consecutive {PERFECT[i0]} voices {a},{b} chords {i+1}-{i+2}')
        # 7ths fall by step
        if f0['seventh'] is not None:
            for v in range(4):
                if P[v] % 12 == f0['seventh'] and N[v] - P[v] not in (-1, -2):
                    fail('A', f'{where}: 7th of {toks[i]} in voice {v} moves {N[v]-P[v]}')
        # leading note rises in the outer voices at V(7) -> I / i / vi / VI
        dom = f0['scale_degree'] == 5 and not f0['secondary']
        if dom and f1['scale_degree'] in (1, 6) and not f1['secondary']:
            for v in (0, 3):
                if P[v] % 12 == lt and N[v] - P[v] != 1:
                    fail('A', f'{where}: leading note in voice {v} does not rise ({toks[i]}-{toks[i+1]})')
            if f1['scale_degree'] == 6:
                if sum(1 for m in N if m % 12 == f1['third']) != 2:
                    fail('A', f'{where}: {toks[i+1]} after V does not double its 3rd')
        # no augmented 2nds: a 3-semitone move between adjacent letter names (le <-> ti in minor; any spelled aug 2nd)
        for v in range(4):
            if abs(N[v] - P[v]) == 3 and mode == 'min' and {P[v] % 12, N[v] % 12} == {(tonic + 8) % 12, lt}:
                fail('A', f'{where}: augmented 2nd in voice {v}')
    return info


def cad_category_ok(cat, toks, k, mode):
    f = [rn_info(t, k, mode) for t in toks[-2:]]
    sd = [x['scale_degree'] for x in f]
    root_pos = toks[-1].find(':') < 0
    if cat == 'perfect':
        return sd == [5, 1] and root_pos and not (len(toks) >= 3 and toks[-3] in ('I:2', 'i:2'))
    if cat == 'plagal':
        return sd == [4, 1] and root_pos
    if cat == 'imperfect':
        return sd[1] == 5 and not f[1]['secondary'] and not (mode == 'min' and toks[-2] == 'iv:1')
    if cat == 'interrupted':
        return sd == [5, 6]
    # R4 (0.48): rung 3 answers of their own
    if cat == 'phrygian':
        return mode == 'min' and toks[-2] == 'iv:1' and sd[1] == 5 and root_pos
    if cat == 'cad64':
        return len(toks) >= 3 and toks[-3] in ('I:2', 'i:2') and sd == [5, 1] and root_pos
    return False


POP = [('V', 'IV'), ('V', 'iv'), ('ii', 'I'), ('ii', 'vi'), ('V7', 'IV')]


def retro_moves(toks):
    """ii(6) -> IV and ii°(6) -> iv: a retrogression in common-practice harmony (the pre-dominant moves forward, IV to ii, ii to V)."""
    base = [t.split(':')[0] for t in toks]
    return [(a, b) for a, b in zip(base, base[1:]) if (a, b) in (('ii', 'IV'), ('ii°', 'iv'))]


def pop_moves(toks):
    # a cadential 6/4 (I:2 / i:2) is a dominant-function chord, so ii6-I6/4 is the textbook approach, not ii-I
    base = [t.split(':')[0] if not t.endswith(':2') else 'cad64' for t in toks]
    return [(a, b) for a, b in zip(base, base[1:]) if (a, b) in POP]


def vvi_enum(k, open_only=True):
    """0.49 C4: every strict four-part V–vi in major key k (independent of the app). Voices B 40-60, T 48-67, A 55-74, S 60-79 (the app's
    ranges), no crossing, S-A and A-T within an octave, open spacing (S-T more than an octave) unless open_only is False. V complete
    with one leading note; vi complete with its 3rd doubled (two do). Every voice: no leap over an octave, of a 7th or a tritone; the
    leading note rises a semitone to do. No parallel or contrary 5ths / octaves / unisons, no overlap, no hidden 5th or octave in the
    outer voices."""
    so, ti, re_, la, do, mi = [(k + x) % 12 for x in (7, 11, 2, 9, 0, 4)]

    def voicings(bass_pc, pcs, ok):
        out = []
        for b in range(40, 61):
            if b % 12 != bass_pc:
                continue
            for t in range(48, 68):
                for a in range(55, 75):
                    for s in range(60, 80):
                        v = (b, t, a, s)
                        if not (b <= t <= a <= s) or any(x % 12 not in pcs for x in v) or s - a > 12 or a - t > 12 or (open_only and s - t <= 12):
                            continue
                        if ok([x % 12 for x in v]):
                            out.append(v)
        return out
    V = voicings(so, {so, ti, re_}, lambda c: c.count(ti) == 1 and set(c) == {so, ti, re_})
    VI = voicings(la, {la, do, mi}, lambda c: set(c) == {la, do, mi} and c.count(do) == 2)
    res = []
    for P in V:
        for N in VI:
            good = all(abs(N[i] - P[i]) <= 12 and abs(N[i] - P[i]) not in (6, 10, 11) and (P[i] % 12 != ti or N[i] - P[i] == 1) for i in range(4))
            for i in range(4):
                for j in range(i + 1, 4):
                    if (P[j] - P[i]) % 12 == (N[j] - N[i]) % 12 and (N[j] - N[i]) % 12 in (0, 7) and P[i] != N[i] and P[j] != N[j]:
                        good = False
            if any(N[i] > P[i + 1] or N[i + 1] < P[i] for i in range(3)):
                good = False
            mb, ms = N[0] - P[0], N[3] - P[3]
            if mb * ms > 0 and (N[3] - N[0]) % 12 in (0, 7):
                good = False
            if good:
                res.append((P, N))
    return res


def predict_acc(rows, feat, ans):
    """Held-out accuracy of the best guess of `ans` from `feat` alone (fit on one half, scored on the other, both ways),
    and chance (the most common answer). Scoring in-sample would flatter any feature with many values."""
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


# ===================================================================================================================
# L: the 0.49 ladders (LADDER_REGISTER_049; Justin's answers L101-L104). A port of the reference model's checks
# (tests/reports/ladder_049/ladder_proto.py): pools (rule P), tells (5-point margin over the given information), the new-thing share
# (rule N, D2), range and do placement (MR1, MR2), the fill rules (RF) and the anacrusis / last-bar rule (D9), the names table (D12),
# the M9 pivot window and both readings (D8), the M11 outer voices (an independent counterpoint checker), marking (D4, D11, R8, R9),
# readiness (D10), the duration palette (L103). Every check here is the build's own: labelled "self-check" in the counts.
# ===================================================================================================================
LTICK = 420
# the cells, re-entered here from the register (ticks; n note, r rest, t tied), not read from the app
LCELLS = {'q': [(420, 'n')], 'e2': [(210, 'n')] * 2, 'h': [(840, 'n')], 'qr': [(420, 'r')], 'w': [(1680, 'n')], 'hd': [(1260, 'n')],
          's4': [(105, 'n')] * 4, 'dq': [(630, 'n'), (210, 'n')], 'es2': [(210, 'n'), (105, 'n'), (105, 'n')], 's2e': [(105, 'n'), (105, 'n'), (210, 'n')],
          'er': [(210, 'r'), (210, 'n')], 're': [(210, 'n'), (210, 'r')], 'cD': [(630, 'n')], 'c3': [(210, 'n')] * 3, 'cqe': [(420, 'n'), (210, 'n')],
          'ceq': [(210, 'n'), (420, 'n')], 'cdse': [(315, 'n'), (105, 'n'), (210, 'n')], 'c6': [(105, 'n')] * 6, 'cDD': [(1260, 'n')],
          'syn': [(210, 'n'), (420, 'n'), (210, 'n')], 'synT': [(210, 'n'), (210, 'n'), (210, 't'), (210, 'n')], 'antA': [(210, 'n'), (210, 'n'), (420, 't')],
          'antB': [(210, 'n'), (210, 'n')], 'tri': [(140, 'n')] * 3, 'dsq': [(315, 'n'), (105, 'n')], 'tres': [(630, 'n'), (630, 'n'), (420, 'n')],
          'charl': [(630, 'n'), (210, 'n'), (840, 'r')], 'q5': [(84, 'n')] * 5, 'q7_34': [(60, 'n')] * 7, 'q7_43': [(60, 'n')] * 7,
          'e': [(210, 'n')], 'qd': [(630, 'n')], 'cq': [(420, 'n')]}
LBAR = {'2/4': 840, '3/4': 1260, '4/4': 1680, '6/8': 1260, '12/8': 2520, '5/4': 2100, '7/8': 1470}
COMPOUND = {'6/8', '12/8'}
APPROVED = {'q': 'ta', 'e2': 'ti-ti', 'h': 'ta-a', 's4': 'tika-tika', 'qr': 'sa', 'dq': 'tam-ti', 'es2': 'ti-tika', 's2e': 'tika-ti', 'syn': 'syn-co-pa',
            'w': 'ta-a-a-a', 'hd': 'ta-a-a', 'er': 'sa ti', 're': 'ti sa', 'cD': 'tam', 'c3': 'ti-ti-ti', 'cqe': 'ta ti', 'ceq': 'ti ta', 'cdse': 'tim-ka-ti',
            'c6': 'tika-tika-tika', 'cDD': 'ta-a-a', 'synT': 'ti ti-i ti', 'tri': 'tri-o-la', 'dsq': 'tim-ka', 'tres': 'tam ti-i ta', 'charl': 'tam ti sa-a',
            'q5': 'ta-da-ki-na-dom', 'q7_34': 'ta-ki-ta ta-ka-di-mi', 'q7_43': 'ta-ka-di-mi ta-ki-ta'}
SEMI = [0, 2, 4, 5, 7, 9, 11]
SYLW = {'d': (0, 0), 'r': (1, 0), 'm': (2, 0), 'f': (3, 0), 's': (4, 0), 'l': (5, 0), 't': (6, 0), 'di': (0, 1), 'ri': (1, 1), 'fi': (3, 1), 'si': (4, 1), 'li': (5, 1),
        'ra': (1, -1), 'me': (2, -1), 'se': (4, -1), 'le': (5, -1), 'te': (6, -1)}


def l_semis(tx):
    b = tx.rstrip(",'")
    o = tx.count("'") - tx.count(',')
    w, a = SYLW[b]
    return SEMI[w] + 12 * o + a


def l_tell_table(rows, feats, targets, margin=0.05):
    """ladder_proto.tell_table: accuracy of the majority answer per (given, feature) value against per given value alone; cells with
    fewer than 30 items on average are skipped (too many values for the sample)"""
    out = []
    for fn, (f, st) in feats.items():
        for tn, t in targets.items():
            rr = [x for x in rows if t(x) is not None]
            if not rr:
                continue
            S = st or (lambda x: 0)
            vals = len(set((S(x), f(x)) for x in rr))
            if len(rr) / max(1, vals) < 30:
                continue

            def acc_of(g):
                by = collections.defaultdict(collections.Counter)
                for x in rr:
                    by[g(x)][t(x)] += 1
                return sum(c.most_common(1)[0][1] for c in by.values()) / len(rr)
            acc, base = acc_of(lambda x: (S(x), f(x))), acc_of(S)
            out.append(dict(feature=fn, target=tn, acc=acc, base=base, fail=acc > base + margin))
    return out


def l_rf_check(it, where, melody=False):
    """RF and D9, re-derived: cells on beats; two-beat cells on strong beats only (synT at beat 2 of 4/4 by its tie); dotted minim from beat 1;
    semibreve only as a whole 4/4 bar; tresillo and Charleston whole 4/4 bars; no all-rest bar; bar lengths add up; the last bar is shortened
    by the anacrusis"""
    m = it['metre']
    bar = LBAR[m]
    bl = it['barLen']
    if it['anac'] and (bl[-1] != bar - it['anac'] or any(x != bar for x in bl[:-1])):
        fail('L', f'{where}: anacrusis {it["anac"]} but bar lengths {bl}')
    if not it['anac'] and any(x != bar for x in bl):
        fail('L', f'{where}: bar lengths {bl} in {m}')
    if sum(sum(d for d, _ in LCELLS[c]) for c in it['anacCells']) != it['anac']:
        fail('L', f'{where}: anacrusis cells {it["anacCells"]} do not make {it["anac"]}')
    strong = {'2/4': [0], '3/4': [0], '4/4': [0, 840], '5/4': [0, 1260], '6/8': [0], '12/8': [0, 1260], '7/8': [0]}[m]
    for b, cells in enumerate(it['cells']):
        p = 0
        notes = 0
        L = bl[b]
        for c in cells:
            w = sum(d for d, _ in LCELLS[c])
            if m == '7/8':
                pass
            elif m in COMPOUND:
                if p % 630 and not (c == 'cq' and p + w == L):
                    fail('L', f'{where}: bar {b+1} compound cell {c} starts off the beat at {p}')
            else:
                if p % 420 and not (c == 'e' and p + w == L):
                    fail('L', f'{where}: bar {b+1} cell {c} starts off the beat at {p}')
                last_fig = melody and b == len(it['cells']) - 1 and c == 'h' and not (m == '4/4' and p < 840 < p + w)   # a melody's ending figure
                if w == 840 and c != 'synT' and p not in strong and m != '5/4' and not last_fig:
                    fail('L', f'{where}: bar {b+1} two-beat cell {c} at {p} (not a strong beat)')
                if m == '5/4' and it.get('grp'):
                    g0 = it['grp'][0] * 420
                    if p < g0 < p + w:
                        fail('L', f'{where}: bar {b+1} cell {c} crosses the 5/4 grouping {it["grp"]}')
                if c == 'synT' and not (m == '4/4' and p == 420):
                    fail('L', f'{where}: tied syncopation away from the bar middle')
                if c == 'hd' and p != 0 and m != '5/4':
                    fail('L', f'{where}: dotted minim at {p}')
                if c in ('w', 'tres', 'charl') and not (m == '4/4' and p == 0 and L == 1680):
                    fail('L', f'{where}: {c} is not a whole 4/4 bar')
            notes += sum(1 for d, k in LCELLS[c] if k == 'n')
            p += w
        if p != L:
            fail('L', f'{where}: bar {b+1} adds up to {p}, not {L}')
        if not notes:
            fail('L', f'{where}: bar {b+1} is all rest')
    if it['cells'][-1] and it['cells'][-1][-1] == 'antB':
        fail('L', f'{where}: a tie over the end of the line')


def l_ctp_check(it, where):
    # IC_LADDER_ENG M-3: the move the melody makes AS the bass changes (the note sounding just before the bass onset to the note at it) is checked
    # for consecutive and direct 5ths / octaves as well as the notes at the bass onsets
    """M11 outer voices, independently (music21 for the chords): each bass note is the root or (ii°: only) the 3rd of the chord it names,
    in the key; the melody note at the bass note's onset belongs to that chord; no parallel or consecutive 5ths / octaves between the
    outer voices; no direct 5th / octave with a leap in the melody; no crossing; the leading note in the bass rises; I (i) first, V–I (i)
    at the end, both in root position"""
    do, mode = it['do'], it['mode']
    tonic = (do + 9) % 12 if mode == 'min' else do
    k = m21key.Key(TON[tonic] if mode != 'min' else {'D-': 'C#', 'A-': 'G#'}.get(TON[tonic], TON[tonic]).lower())
    B = it['bass']
    sop = []
    for b in B:
        n = next((x for x in it['notes'] if x[0] <= b[0] < x[0] + x[1]), None)
        if n is None:
            fail('L', f'{where}: no melody note at the bass onset {b[0]}')
            return
        sop.append(n[2])
    for j, b in enumerate(B):
        fig = b[3].replace('°', 'o')
        inv = fig.endswith('6')
        rn = roman.RomanNumeral(fig, k)
        pcs = {p.pitchClass for p in rn.pitches}
        want = rn.third.pitchClass if inv else rn.root().pitchClass
        if b[2] % 12 != want:
            fail('L', f'{where}: bass {b[2]} is not the {"3rd" if inv else "root"} of {b[3]}')
        if sop[j] % 12 not in pcs:
            fail('L', f'{where}: melody {sop[j]} not in {b[3]} at slot {j+1}')
        if b[2] >= sop[j]:
            fail('L', f'{where}: crossing at slot {j+1}')
    if B[0][3] not in ('I', 'i') or B[-1][3] not in ('I', 'i') or B[-2][3] != 'V':
        fail('L', f'{where}: does not open on I and close V–I: {[x[3] for x in B]}')
    lt = (tonic + 11) % 12
    for j in range(1, len(B)):
        prev = [x for x in it['notes'] if x[0] < B[j][0]]
        if prev:
            s0, s1, b0, b1 = prev[-1][2], sop[j], B[j - 1][2], B[j][2]
            i0, i1 = (s0 - b0) % 12, (s1 - b1) % 12
            COUNT['self-check L8 M11 bass changes checked against the melody note before them (IC M-3)'] += 1
            if i0 in (0, 7) and i0 == i1 and s0 != s1 and b0 != b1:
                fail('L', f'{where}: consecutive {"octaves" if i0 == 0 else "5ths"} as the bass changes into slot {j+1} (melody {s0}->{s1})')
            elif i1 in (0, 7) and (s1 - s0) * (b1 - b0) > 0 and abs(s1 - s0) > 2:
                fail('L', f'{where}: direct {"octave" if i1 == 0 else "5th"} as the bass changes into slot {j+1}')
    for j in range(1, len(B)):
        s0, s1, b0, b1 = sop[j - 1], sop[j], B[j - 1][2], B[j][2]
        i0, i1 = (s0 - b0) % 12, (s1 - b1) % 12
        if i0 in (0, 7) and i0 == i1 and s0 != s1 and b0 != b1:
            fail('L', f'{where}: consecutive {"octaves" if i0 == 0 else "5ths"} slots {j}-{j+1}')
        elif i1 in (0, 7) and (s1 - s0) * (b1 - b0) > 0 and abs(s1 - s0) > 2:
            fail('L', f'{where}: direct {"octave" if i1 == 0 else "5th"} with a melodic leap into slot {j+1}')
        if b0 % 12 == lt and b1 - b0 != 1:
            fail('L', f'{where}: the leading note in the bass does not rise (slot {j})')
    COUNT['self-check L8 M11 outer-voice items checked (independent checker)'] += 1


async def ladder_section(pg):
    MK = "(seed)=>{let s=seed;return()=>{s=(s*16807)%2147483647;return s/2147483647}}"
    # ---------------- L0: stages, settings, names ----------------
    st = await pg.evaluate("""()=>({mel:EARSTAGE.mel,rhy:EARSTAGE.rhy,rs:[4,5,6].map(g=>{S.level=g;EAR.all=false;return{mel:earRungsShown('mel'),rhy:earRungsShown('rhy')}}),
        edr:EDR.find(x=>x[0]==='rhy')[2],tag:earStageTag('rhy'),names:EAR.names,mod:EAR.mod,saved:(()=>{EAR.names='kk';EAR.mod='move';earSave();const o=LS.get('cjg_ear');EAR.names='k';EAR.mod='home';earSave();return[o.names,o.mod,typeof o.rd]})(),
        N:LADNAMES,NK:LADNAMES_KK,R:RHYNAMES,tiles:Object.fromEntries([1,2,3,4,5,6,7,8,9,10].map(l=>[l,ladRhyTiles(l)])),ec:[1,2,3].map(l=>earCells(l).join(' '))})""")
    COUNT['self-check L0 Stage table and settings'] = 1
    if st['mel'] != [4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6] or st['rhy'] != [4, 4, 4, 5, 5, 5, 5, 6, 6, 6]:
        fail('L', f"EARSTAGE mel {st['mel']} rhy {st['rhy']}")
    want_rs = [dict(mel=[1, 2, 3, 4], rhy=[1, 2, 3]), dict(mel=list(range(1, 9)), rhy=list(range(1, 8))), dict(mel=list(range(1, 13)), rhy=list(range(1, 11)))]
    if st['rs'] != want_rs:
        fail('L', f"rungs shown by Stage {st['rs']}")
    if st['edr'] != '4–6' or st['tag'] != 'Stage 4–6':
        fail('L', f"rhythm dictation Stage tag {st['edr']} / {st['tag']}")
    if st['names'] != 'k' or st['mod'] != 'home' or st['saved'] != ['kk', 'move', 'object']:
        fail('L', f"settings: names {st['names']}, mod {st['mod']}, saved {st['saved']}")
    # names (D12; approved 20 Nov and 21:24): every tile at every rung has a name in both tables; the approved names unchanged
    for k, v in APPROVED.items():
        COUNT['self-check L6 names checked'] += 1
        if st['N'].get(k) != v:
            fail('L', f"name of {k}: {st['N'].get(k)!r}, approved {v!r}")
    for l, tiles in st['tiles'].items():
        for k in tiles:
            COUNT['self-check L6 tile x rung names'] += 1
            if not st['N'].get(k) or not st['NK'].get(k):
                fail('L', f'rung {l} tile {k}: no time name in one of the two settings')
    if st['N']['tri'] != 'tri-o-la' or st['NK']['tri'] != 'ta-ki-ta' or any(st['N'][k] != st['NK'][k] for k in st['N'] if k not in ('tri', 'trq')):
        fail('L', 'names setting: only the triplet (and its tied form) changes between Kodály and Kodály with konnakol tuplets (D12)')
    # the swung pair written as a triplet crotchet-quaver: tri-o-la with the first two notes tied, held on the vowel (coordinator, from L97)
    if st['N']['trq'] != 'tri-i-la' or st['NK']['trq'] != 'ta-a-ta':
        fail('L', f"trq names {st['N']['trq']} / {st['NK']['trq']} (tri-i-la / ta-a-ta)")
    if st['R'] != st['N']:
        fail('L', 'RHYNAMES is not the ladder names table')

    # ---------------- L1-L4, L11: melody items (5,000 seeded per rung) ----------------
    N = 5000
    mel = {}
    for l in range(1, 12):   # one rung per call (the page keeps one rung's items at a time)
        mel[l] = await pg.evaluate("""(a)=>{const[MK,N,l]=a,R=eval(MK)(491+l),rows=[];for(let i=0;i<N;i++){const q=ladGenMel(l,R);
        rows.push({l,id:q.id,key:q.key.do,octv:q.doMidi-60-q.key.do,n:q.n,tempo:q.tempo||0,metre:q.metre||'',anac:q.anac||0,sol:q.a,new:q.new,
          var:String((q.info&&(q.info.kind||q.info.var||q.info.tune))||''),rb1:q.cells?q.cells[0].join(' '):null,lo:Math.min(...q.midi),hi:Math.max(...q.midi),
          cue:i<500?ladCueNotes(q):null,home:(q.info&&q.info.home)||0,mode:q.mode,barLen:i<1000?q.barLen||null:null,cells:i<1000?q.cells:null,anacCells:q.anacCells||[],
          bass:q.bass?q.bass.map(b=>[b.on,b.dur,b.midi,b.chord]):null,notes:l===11&&i<2000?q.notes.map(x=>[x.on,x.dur,x.midi]):null,do:q.key.do,
          aug2:q.aug2||null,ns:l===7?q.notes.map(x=>x.sol):null})}return rows}""", [MK, N, l])
    for l, rows in mel.items():
        ids = {x['id'] for x in rows}
        COUNT[f'self-check L1 M{l} distinct items in {N}'] = len(ids)
        if len(ids) < 100:
            fail('L', f'M{l}: {len(ids)} distinct items in {N} draws (rule P: at least 100)')
        if l >= 2:
            sh = sum(1 for x in rows if x['new']) / len(rows)
            COUNT[f'self-check L3 M{l} new-thing share'] = round(sh, 3)
            if not 0.60 <= sh <= 0.73:
                fail('L', f'M{l}: new-thing share {sh:.2f} (rule N: 0.60-0.73)')
        lo, hi = min(x['lo'] for x in rows), max(x['hi'] for x in rows)
        COUNT[f'self-check L4 M{l} MIDI range'] = f'{lo}-{hi}'
        if lo < 55 or hi > 83:
            fail('L', f'M{l}: MIDI {lo}-{hi} outside G3-B5 (MR2)')
        if any(x['octv'] != 0 for x in rows):
            fail('L', f'M{l}: do is not 60 + pc for every item (MR1)')
        for x in rows[:500]:
            T = 60 + x['do'] + SEMI[x['home'] % 7] + 12 * (x['home'] // 7)
            if x['cue'][1] != T or x['cue'][0] != T - 12:
                fail('L', f"M{l}: key cue {x['cue']} is not the mode's tonic triad at do = 60 + pc (D7)")
                break
        if l >= 4:
            for x in rows[:1000]:
                l_rf_check(dict(metre=x['metre'], barLen=x['barLen'], anac=x['anac'], anacCells=x['anacCells'], cells=x['cells']), f'M{l} {x["id"][:40]}', melody=True)
                COUNT['self-check L5 melody rhythms checked against RF and D9'] += 1
            tp = [x['tempo'] for x in rows]
            if min(tp) < 72 or max(tp) > 96:
                fail('L', f'M{l}: tempo {min(tp)}-{max(tp)} (72-96)')
    # D5: fa-si at most once, as a step, flagged
    for x in mel[7]:
        if x['aug2'] is not None:
            COUNT['self-check L2 M7 items checked for fa-si (D5)'] += 1
            steps = [i for i in range(len(x['ns']) - 1) if x['ns'][i].rstrip(",'") == 'f' and x['ns'][i + 1].rstrip(",'") == 'si' and l_semis(x['ns'][i + 1]) - l_semis(x['ns'][i]) == 3]
            if len(steps) > 1 or sorted(steps) != sorted(x['aug2']):
                fail('L', f"M7 fa-si: steps at {steps}, flagged {x['aug2']}")
                break
    # tells (the prototype's tables)
    for l, rows in mel.items():
        feats = {'key signature': (lambda x: x['key'], None),
                 'octave of the melody against the key cue': (lambda x: x['octv'], lambda x: x['key']),
                 'number of notes (shown at rungs 1-3 only)': (lambda x: x['n'] if x['l'] <= 3 else 0, None),
                 'tempo (8-bpm bands)': (lambda x: x['tempo'] // 8, None),
                 'anacrusis (shown in the bar outline)': (lambda x: x['anac'], None)}
        targets = {'note 2 solfa': lambda x: x['sol'][1], 'note 3 solfa': lambda x: x['sol'][2] if x['n'] > 2 else None,
                   'note 4 solfa': lambda x: x['sol'][3] if x['n'] > 3 else None, 'penultimate solfa': lambda x: x['sol'][-2],
                   'contains the new thing': lambda x: x['new'] if l >= 2 else None, 'variant': lambda x: x['var'] or None,
                   'rhythm of bar 1': lambda x: x['rb1']}
        tl = l_tell_table(rows, feats, {k: v for k, v in targets.items() if k != 'rhythm of bar 1'})
        if l >= 4:
            tl += l_tell_table(rows, {k + ', given the metre': (f, lambda x: x['metre']) for k, (f, s) in feats.items()}, {'rhythm of bar 1': targets['rhythm of bar 1']})
            tl += l_tell_table(rows, {'metre (shown)': (lambda x: x['metre'], None)}, {k: v for k, v in targets.items() if k != 'rhythm of bar 1'})
        if l == 11:
            tl += l_tell_table(rows, {'length': (lambda x: x['n'], None), 'key': (lambda x: x['key'], None)},
                               {'bass first note': lambda x: x['bass'][0][3], 'bass last note': lambda x: x['bass'][-1][3]})
        COUNT[f'self-check L2 M{l} tells checked (5,000 items)'] = len(tl)
        for t in tl:
            if t['fail']:
                fail('L', f"M{l} tell: {t['feature']} predicts {t['target']} {t['acc']:.0%} (given-information baseline {t['base']:.0%})")
    # L8: M11 outer voices
    for x in mel[11][:2000]:
        l_ctp_check(dict(do=x['do'], mode='min' if x['mode'] == 'min' else 'maj', bass=x['bass'], notes=x['notes']), f"M11 {x['id'][:30]}")

    # ---------------- rhythm items ----------------
    rhy = {}
    for l in range(1, 11):
        rhy[l] = await pg.evaluate("""(a)=>{const[MK,N,l]=a,R=eval(MK)(503+l),rows=[];for(let i=0;i<N;i++){const q=ladGenRhy(l,R);
        rows.push({l,id:q.id,metre:q.metre,tempo:q.tempo,pitch:q.pitch,anac:q.anac,anacCells:q.anacCells,cells:q.cells,barLen:q.barLen,new:q.new,hn:ladRhyHiddenNew(l,q),
          tup:!!q.tup,kick:q.drums?q.drums.kick:null,swing:q.swing,backbeat:q.backbeat,grp:q.grp})}return rows}""", [MK, N, l])
    for l, rows in rhy.items():
        ids = [x['id'] for x in rows]
        COUNT[f'self-check L1 R{l} distinct items in {N}'] = len(set(ids))
        if l == 1:
            if len(set(ids)) != 99:
                fail('L', f'R1: {len(set(ids))} distinct bars (D1: exactly 99)')
        elif len(set(ids)) < 100:
            fail('L', f'R{l}: {len(set(ids))} distinct items (rule P)')
        if 2 <= l <= 9:
            sh = sum(1 for x in rows if x['new']) / len(rows)
            COUNT[f'self-check L3 R{l} new-thing share'] = round(sh, 3)
            if not 0.60 <= sh <= 0.73:
                fail('L', f'R{l}: new-thing share {sh:.2f}')
        for x in rows[:1500]:
            l_rf_check(x, f'R{l} {x["id"][:40]}')
            COUNT['self-check L5 rhythm items checked against RF and D9'] += 1
        if l == 9:
            for x in rows:
                if x['tup']:
                    COUNT['self-check L13 R9 tuplet items checked'] += 1
                    per = [sum(1 for c in b if c in ('q5', 'q7_34', 'q7_43')) for b in x['cells']]
                    if x['metre'] not in ('4/4', '5/4') or max(per) > 1:
                        fail('L', f"R9 tuplets: metre {x['metre']}, per bar {per}")

        def secs(x):
            return round((x['anac'] + sum(x['barLen'])) / LTICK * 60 / x['tempo'])
        # given information: the metre and the bar outline, which shows the anacrusis and the last bar shortened by it (D9). With an upbeat
        # of a quaver the short last bar must end on a quaver, so the anacrusis is part of the baseline, not a feature (the reference model
        # did not shorten the last bar)
        given = lambda x: (x['metre'], x['anac'])
        feats = {'tempo (8-bpm bands)': (lambda x: x['tempo'] // 8, given), 'playing time (whole seconds)': (secs, given),
                 'tone pitch (MIDI)': (lambda x: x['pitch'], given), 'anacrusis (shown), metre given': (lambda x: x['anac'], lambda x: x['metre'])}
        allc = lambda x: [c for b in x['cells'] for c in b]
        targets = {'first cell': lambda x: x['cells'][0][0], 'second cell': lambda x: x['cells'][0][1] if len(x['cells'][0]) > 1 else None,
                   'last cell': lambda x: x['cells'][-1][-1], 'contains a new cell (hidden)': lambda x: x['hn']}
        if l == 9:
            targets['contains a tuplet'] = lambda x: x['tup']
        if l == 10:
            targets['kick density'] = lambda x: sum(bin(m).count('1') for m in x['kick'])
        tl = l_tell_table(rows, {k: v for k, v in feats.items() if not k.startswith('anacrusis')}, targets)
        tl += l_tell_table(rows, {k: v for k, v in feats.items() if k.startswith('anacrusis')}, {k: v for k, v in targets.items() if k != 'last cell'})
        COUNT[f'self-check L2 R{l} tells checked (5,000 items)'] = len(tl)
        for t in tl:
            if t['fail']:
                fail('L', f"R{l} tell: {t['feature']} predicts {t['target']} {t['acc']:.0%} (baseline {t['base']:.0%})")
    # D1: no repeat of a rung 1 bar within the last 30 (the app's own draw, earGen)
    seq = await pg.evaluate("()=>{const o=[];for(let i=0;i<3000;i++)o.push(earGen('rhy',1).id);return o}")
    rep = [i for i in range(len(seq)) if seq[i] in seq[max(0, i - 30):i]]
    COUNT['self-check L1 R1 consecutive draws checked for repeats within 30'] = len(seq)
    if rep:
        fail('L', f'R1: {len(rep)} repeats within 30 items (D1), first at {rep[0]}')

    # ---------------- L7: M9 pivot window and both readings ----------------
    m9 = await pg.evaluate("""(MK)=>{const R=eval(MK)(497),o=[];while(o.length<2000){const q=ladGenMel(9,R);if(!q.kind)continue;
        o.push({kind:q.kind,do:q.key.do,pivot:q.pivot,win:q.pivotWindow,home:q.readings.home,move:q.readings.move,a:q.a,midi:q.midi,pn:q.pivotNames,nk:q.newKey})}return o}""", MK)
    for q in m9:
        COUNT['self-check L7 M9 items checked'] += 1
        w = f"M9 {q['kind']} {' '.join(q['a'][:6])}"
        sh = 7 if q['kind'] in ('M-V', 'm-v') else 0
        if q['home'] != q['a']:
            fail('L', f'{w}: the Keep home do reading is not the item\'s solfa')
        dm = 60 + q['do']
        for j, (h, mv, mi) in enumerate(zip(q['home'], q['move'], q['midi'])):
            if dm + l_semis(h) != mi:
                fail('L', f'{w}: home reading {h} is not MIDI {mi}')
                break
            nd = dm + (sh if j >= q['pivot'] else 0)
            if (nd + l_semis(mv) - mi) % 12:
                fail('L', f'{w}: move reading {mv} at {j} is not MIDI {mi} with do {nd}')
                break
            if j < q['pivot'] and mv != h:
                fail('L', f'{w}: the readings differ before the pivot')
                break
        if q['pn'][0] != q['home'][q['pivot']] or q['pn'][1] != q['move'][q['pivot']]:
            fail('L', f"{w}: pivot names {q['pn']}")
        if q['kind'] in ('M-V', 'm-v') and q['home'][q['pivot']].rstrip(",'") == 'f':
            fail('L', f'{w}: the pivot is fa going to V')
        # the window, re-derived: run of notes common to both keys before the first note only in the new key
        # minor keys carry fi and si; for minor -> relative major the old key is the harmonic minor, so the major's so is the new note (IC M-7)
        MAJ, MIN, HMIN = {0, 2, 4, 5, 7, 9, 11}, {9, 11, 0, 2, 4, 5, 7, 6, 8}, {9, 11, 0, 2, 4, 5, 8}
        old = HMIN if q['kind'] == 'm-III' else MAJ if q['kind'][0] == 'M' else MIN
        new = {'M-V': {(x + 7) % 12 for x in MAJ}, 'M-vi': MIN, 'm-III': MAJ, 'm-v': {(x + 7) % 12 for x in MIN}}[q['kind']]
        if q['kind'] == 'm-III':
            COUNT['self-check L7 m-III windows narrower than the item (IC M-7)'] += q['win'] != [0, len(q['home']) - 1]
        pcs = [l_semis(h) % 12 for h in q['home']]
        first = next((j for j in range(q['pivot'] + 1, len(pcs)) if pcs[j] in new and pcs[j] not in old), None)
        end = (first - 1) if first is not None else len(pcs) - 1
        stt = min(end, q['pivot'])
        while stt > 0 and pcs[stt - 1] in old and pcs[stt - 1] in new:
            stt -= 1
        if [min(stt, q['pivot']), max(end, q['pivot'])] != q['win']:
            fail('L', f"{w}: pivot window {q['win']}, re-derived {[stt, end]}")

    # ---------------- L9, L10: marking, palette, readiness ----------------
    mk = await pg.evaluate("""(MK)=>{const R=eval(MK)(499),o={right:{},wrong:{},pal:{},beams:0,err:[]};
        for(let l=1;l<=12;l++){let r=0,w=0,p=0;for(let i=0;i<150;i++){const q=ladGenMel(l,R),parts=l===11?['mel','bass']:['mel'],A={};
          for(const part of parts){const E=ladTruthEntries(q,part);A[part]=E;let ok=true;for(let j=0;j<E.length;j++){if(!ladPalette(q,E.slice(0,j),part).lengths.some(x=>x.t===E[j].t&&x.rest===!E[j].s)){ok=false;break}}
            if(ok&&ladPalette(q,E,part).done)p++}
          const ans=l===11?A:A.mel;if(ladMelMark(q,ans,{mod:'home'}).ok)r++;
          // one wrong pitch: a note a step away
          const B=JSON.parse(JSON.stringify(ans)),L=l===11?B.mel:B,k=L.findIndex(e=>e.s);if(k>=0){const pp=ladParse(L[k].s);L[k].s=ladSyl(pp.i+1,0)}
          const mm=ladMelMark(q,B,{mod:'home'});if(!mm.ok&&!mm.nearly&&mm.detail.some(d=>!d.pitch))w++}
         o.right[l]=r;o.wrong[l]=w;o.pal[l]=p}
        // M10: the other chromatic spelling = Nearly (D4)
        let nl=0,nt=0;for(let i=0;i<400&&nt<50;i++){const q=ladGenMel(10,R);if(!q.chrom||!q.chrom.length)continue;const E=ladTruthEntries(q),j=q.chrom[0]-1,pp=ladParse(E[j].s);
          const s2=pp.a>0?ladSyl(pp.i+1,-1):ladSyl(pp.i-1,1),F=E.map(x=>({...x}));F[j].s=s2;nt++;const m=ladMelMark(q,F);if(m.nearly&&!m.ok)nl++}
        o.m10=[nl,nt];
        // M9 (D8, L102, L107; IC M-6, M-7): dominant kinds: the pivot only under Move do, and an answer in the new key's syllables after the
        // pivot is right; relative kinds: right with no mutation, and a needless mutation with every note right is right (with the sentence)
        let pv=[0,0,0,0,0,0,0];for(let i=0;i<600&&pv[0]+pv[3]<500;i++){const q=ladGenMel(9,R);if(!q.kind)continue;const E=ladTruthEntries(q),dom=q.kind==='M-V'||q.kind==='m-v';
          const M=E.map((e,j)=>({...e,s:j+1>q.pivot?q.readings.move[j+1]:e.s}));
          if(dom){pv[0]++;if(ladMelMark(q,E,{mod:'home'}).ok&&ladMelMark(q,E,{mod:'move',pivot:q.pivot}).ok)pv[1]++;
            if(!ladMelMark(q,E,{mod:'move',pivot:null}).ok&&!ladMelMark(q,E,{mod:'move',pivot:q.pivotWindow[1]+1}).ok)pv[2]++;
            if(ladMelMark(q,M,{mod:'move',pivot:q.pivot}).ok)pv[6]++}
          else{pv[3]++;if(ladMelMark(q,E,{mod:'move',pivot:null}).ok)pv[4]++;const m=ladMelMark(q,E,{mod:'move',pivot:0});if(m.ok&&/no mutation/.test(m.note))pv[5]++}}
        o.m9=pv;
        // rhythm: the answer itself is right; the register's Nearly cases
        o.rr={};for(let l=1;l<=10;l++){let r=0;for(let i=0;i<300;i++){const q=ladGenRhy(l,R);if(ladRhyMark(q,q.a).ok)r++}o.rr[l]=r}
        const base={d:'rhy',l:6,metre:'4/4',anac:0,anacCells:[],cells:[['q','synT','q']],barLen:[1680],swing:false};base.a=base.cells.flat();
        o.d11=ladRhyMark(base,['q','syn','q']).kind;o.d11b=ladRhyMark(base,['q','synT','q']).kind;
        const t7={d:'rhy',l:9,metre:'4/4',anac:0,anacCells:[],cells:[['q7_43','q','h']],barLen:[1680]};t7.a=t7.cells.flat();o.sep=ladRhyMark(t7,['q7_34','q','h']).kind;
        const sw={d:'rhy',l:8,metre:'4/4',anac:0,anacCells:[],cells:[['e2','q','h']],barLen:[1680],swing:true};sw.a=sw.cells.flat();o.swing=ladRhyMark(sw,['trq','q','h']).kind;
        o.wrongR=ladRhyMark(sw,['q','q','h']).kind;
        // R10 marking by parts
        const g=ladGenRhy(10,R),D=ladDrumOns(g.drums);o.r10=[ladRhyMark(g,{riff:g.a,drums:D}).ok,ladRhyMark(g,{riff:g.a,drums:{kick:D.kick.slice(1),snare:D.snare}}).ok];
        // D10 readiness: answered only; 8 of the last 10
        let rd={};['ok','ok','shown','skipped','nearly','ok','ok','ok','ok','ok','ok','miss','miss'].forEach(k=>ladRdPush(rd,'mel',4,k));
        o.rd=[rd.mel[4].join(''),ladRdState(rd,'mel',4,[4,5]).ready,ladRdState({mel:{4:[1,1,1,1,1,1,1,1,0,0]}},'mel',4,[4,5]).ready,ladRdState({mel:{4:[1,1,1,1,1,1,1,0,0,0]}},'mel',4,[4,5]).ready,
          ladRdState({mel:{4:[1,1,1,1,1,1,1,1,1,1]}},'mel',4,[4]).ready];
        // beaming: quaver pairs beamed, crotchets not
        const q4=ladGenMel(4,R),E4=ladTruthEntries(q4),bm=ladBeams(q4,E4);let full=[{t:q4.notes[0].dur,s:'x'},...E4];o.beams=bm.every(g=>g.every(j=>full[j].t<420)&&g.length>=2);
        return o}""", MK)
    for l in range(1, 13):
        COUNT['self-check L9 melody answers marked'] += 150
        if mk['right'][str(l)] != 150:
            fail('L', f"M{l}: the right answer is marked right {mk['right'][str(l)]} of 150")
        if mk['wrong'][str(l)] != 150:
            fail('L', f"M{l}: one wrong pitch is marked wrong (with the note flagged) {mk['wrong'][str(l)]} of 150")
        if mk['pal'][str(l)] != (300 if l == 11 else 150):
            fail('L', f"M{l}: the answer can be entered through the palette {mk['pal'][str(l)]} times")
    COUNT['self-check L9 M10 enharmonic spellings marked Nearly'] = f"{mk['m10'][0]} of {mk['m10'][1]}"
    if mk['m10'][1] < 20 or mk['m10'][0] != mk['m10'][1]:
        fail('L', f"M10: the other chromatic spelling is Nearly {mk['m10']}")
    v = mk['m9']
    COUNT['self-check L9 M9 marking: dominant items, relative items'] = f'{v[0]}, {v[3]}'
    if v[1] != v[0] or v[2] != v[0] or v[6] != v[0]:
        fail('L', f"M9 dominant kinds: right in both settings {v[1]}, pivot required under Move do {v[2]}, new-key syllables right {v[6]} of {v[0]}")
    if v[4] != v[3] or v[5] != v[3] or v[3] < 50:
        fail('L', f"M9 relative kinds under Move do: right with no mutation {v[4]}, right with a needless one (and the sentence) {v[5]} of {v[3]}")
    for l in range(1, 11):
        if mk['rr'][str(l)] != 300:
            fail('L', f"R{l}: the answer itself is marked right {mk['rr'][str(l)]} of 300")
    if (mk['d11'], mk['d11b'], mk['sep'], mk['swing'], mk['wrongR']) != ('nearly', 'right', 'nearly', 'nearly', 'wrong'):
        fail('L', f"rhythm Nearly cases (D11 syn, septuplet grouping, swing triplet, plain wrong): {mk['d11']}, {mk['d11b']}, {mk['sep']}, {mk['swing']}, {mk['wrongR']}")
    if mk['r10'] != [True, False]:
        fail('L', f"R10 marking by parts: {mk['r10']}")
    if mk['rd'] != ['1111111100', True, True, False, False]:
        fail('L', f"readiness (D10): {mk['rd']}")
    if not mk['beams']:
        fail('L', 'beaming groups a note of a crotchet or longer')
    COUNT['self-check L9 marking, readiness and beaming cases'] = 12

    # ---------------- L15: regressions for IC_LADDER_ENG_049 (Musts and Shoulds) ----------------
    ic = await pg.evaluate("""(MK)=>{const R=eval(MK)(509),o={};
        // M-1 melodic minor: si only to la by step, fi only to si
        let b1=0,n1=0;for(let i=0;i<3000;i++){const q=ladGenMel(7,R);if(q.info.var!=='melo')continue;q.notes.forEach((x,j)=>{const y=q.notes[j+1];
          if(x.s==='si'){n1++;if(!y||y.i!==x.i+1||y.a!==0)b1++}if(x.s==='fi'){n1++;if(!y||y.s!=='si'||y.i!==x.i+1)b1++}})}o.m1=[b1,n1];
        // M-2 M8 kinds a quarter each; S1 M9 kinds, keys and range; S2 M10 range; S3 M11 content share
        const cnt=(l,N,f)=>{const c={};for(let i=0;i<N;i++){const q=ladGenMel(l,R);const k=f(q);if(k!=null)c[k]=(c[k]||0)+1}return c};
        o.m8=cnt(8,3000,q=>q.new?q.info.var:null);
        let r9=0;o.m9k=cnt(9,2000,q=>{if(q.notes.some(x=>x.i<-3||x.i>7))r9++;return q.kind||null});o.m9r=r9;o.m9key=cnt(9,2000,q=>q.key.do);
        let r10=0;cnt(10,2000,q=>{if(q.notes.some(x=>x.i<-3||x.i>7))r10++;return null});o.m10r=r10;
        let c11=0,n11=0;cnt(11,600,q=>{n11++;if(q.bass.some(b=>/6$/.test(b.chord)||['ii','vi','ii°','VI'].includes(b.chord.replace(/6$/,''))))c11++;return null});o.m11=[c11,n11];
        // M-4 antA generated at beat 2 of 4/4
        let a4=0,a4bad=0;for(let i=0;i<3000;i++){const q=ladGenRhy(6,R);q.cells.forEach(b=>{let p=0;b.forEach(k=>{if(k==='antA'){a4++;if(q.metre!=='4/4'||p!==420)a4bad++}p+=ladW(k)})})}o.m4=[a4,a4bad];
        // M-5 tie-in names
        o.m5=['q','e2','h','hd','w','s4','s2e','es2','dq'].map(k=>ladRhyNames({anacCells:[],cells:[['h','q','antB'],[k]]},'k')[2][0].name);
        // M-8 5/4 and 7/8: ti-ti as two single quavers is not right; M-9 no false Nearly
        let m8=0,m8n=0;for(let i=0;i<3000&&m8n<300;i++){const q=ladGenRhy(9,R);if(!['5/4','7/8'].includes(q.metre)||!q.a.includes('e2'))continue;m8n++;const a=q.a.flatMap(k=>k==='e2'?['e','e']:[k]);if(ladRhyMark(q,a).ok)m8++}o.m8b=[m8,m8n];
        const t9={d:'rhy',l:6,metre:'4/4',anac:0,anacCells:[],cells:[['syn','q','q'],['q','synT','q']],barLen:[1680,1680]};t9.a=t9.cells.flat();
        o.m9b=[ladRhyMark(t9,['syn','q','q','q','syn','q']).kind,ladRhyMark(t9,['syn','e2','q','q','syn','q']).kind,ladRhyMark(t9,['syn','q','q','e2','syn','q']).kind];
        // M-10 palette: random walks never dead-end; illegal offers absent
        const pal={walks:0,dead:0,hd44:0,qd45:0,h68:0,bass:0};
        for(const l of [4,5,6,7,8,9,10,11])for(let i=0;i<150;i++){const q=ladGenMel(l,R);for(const part of (l===11?['mel','bass']:['mel'])){const E=[];
          for(let st=0;st<200;st++){const P=ladPalette(q,E,part);if(P.done)break;if(!P.lengths.length){pal.dead++;break}
            if(part==='bass'&&P.lengths.some(x=>x.t===630||x.rest))pal.bass++;
            if(part==='mel'){if(q.metre==='4/4'&&P.bar>0&&P.bar<q.cells.length&&P.lengths.some(x=>x.t===1260))pal.hd44++;
              if(l<=5&&P.lengths.some(x=>x.t===630))pal.qd45++;if(q.metre==='6/8'&&P.bar===q.cells.length&&P.lengths.some(x=>x.t===840))pal.h68++}
            const c=P.lengths[Math.floor(R()*P.lengths.length)];E.push({s:c.rest?null:'d',t:c.t})}pal.walks++}}
        o.pal=pal;
        // M-11, M-12 the excerpt table
        o.m12={ids:LADM12.map(x=>x.id),credits:LADM12.map(x=>x.credit),c20:(LADM12.find(x=>x.id==='chopin20_5-8')||{notes:[]}).notes.slice(0,5).map(n=>n[3]),
          c34:(LADM12.find(x=>x.id==='chopin20_3-4')||{notes:[]}).notes.map(n=>n[3]),outline:LADM12.filter(x=>{const B={'2/4':840,'3/4':1260,'4/4':1680,'6/8':1260}[x.metre];
            return x.barLen.slice(0,-1).some(b=>b!==B)||x.barLen[x.barLen.length-1]!==B-(x.anac||0)}).map(x=>x.id)};
        // S4 hidden new share at R7, R8 (S4)
        o.r78=[7,8].map(l=>{let h=0;for(let i=0;i<2000;i++)if(ladRhyHiddenNew(l,ladGenRhy(l,R)))h++;return h/2000});
        return o}""", MK)
    COUNT['self-check L15 IC regressions run'] = 1
    if ic['m1'][0] or ic['m1'][1] < 100:
        fail('L', f"M7 melodic minor: {ic['m1'][0]} raised notes not rising by step to the next ({ic['m1'][1]} checked; IC M-1)")
    tot8 = sum(ic['m8'].values())
    if set(ic['m8']) != {'dor', 'mix', 'te', 'fi'} or any(not 0.2 <= v / tot8 <= 0.3 for v in ic['m8'].values()):
        fail('L', f"M8 kinds not a quarter each: {ic['m8']} (IC M-2)")
    tot9 = sum(ic['m9k'].values())
    if any(not 0.2 <= v / tot9 <= 0.3 for v in ic['m9k'].values()) or ic['m9r']:
        fail('L', f"M9 kinds {ic['m9k']}, {ic['m9r']} items outside s,..d' (IC S1)")
    if max(ic['m9key'].values()) > 1.35 * min(ic['m9key'].values()):
        fail('L', f"M9 keys uneven: {ic['m9key']} (IC S1)")
    if ic['m10r']:
        fail('L', f"M10: {ic['m10r']} items outside s,..d' (IC S2)")
    if ic['m11'][0] / ic['m11'][1] < 0.6:
        fail('L', f"M11 new thing by content {ic['m11']} (IC S3: at least 0.60)")
    if ic['m4'][0] < 50 or ic['m4'][1]:
        fail('L', f"R6 anticipation of beat 3: {ic['m4'][0]} generated, {ic['m4'][1]} misplaced (IC M-4)")
    want5 = ['-i', '-i-ti', '-i-i', '-i-i-i', '-i-i-i-i', '-i-ka-ti-ka', '-i-ka-ti', '-i-ti-ka', '-i-ti']
    if ic['m5'] != want5:
        fail('L', f"tie-in names {ic['m5']}, want {want5} (IC M-5: held on the vowel, the other notes their own syllables)")
    if ic['m8b'][0] or ic['m8b'][1] < 50:
        fail('L', f"5/4 and 7/8: ti-ti as two single quavers marked right {ic['m8b'][0]} of {ic['m8b'][1]} (IC M-8)")
    if ic['m9b'] != ['nearly', 'wrong', 'wrong']:
        fail('L', f"Nearly only as the sole difference: {ic['m9b']} (IC M-9)")
    P = ic['pal']
    if P['dead'] or P['hd44'] or P['qd45'] or P['h68'] or P['bass'] or P['walks'] < 1300:
        fail('L', f'palette (IC M-10): {P}')
    COUNT['self-check L15 palette random walks to a full line'] = P['walks']
    m12 = ic['m12']
    if 'k545_50-53' in m12['ids'] or not 40 <= len(m12['ids']) <= 60:
        fail('L', f"M12 picks: {len(m12['ids'])}, k545_50-53 present {'k545_50-53' in m12['ids']}")
    bad_cr = [c for c in m12['credits'] if not any(n in c for n in ('Johann Sebastian Bach', 'Wolfgang Amadeus Mozart', 'Scott Joplin', 'Fryderyk Chopin')) or 'CC BY' not in c or 'Score data:' not in c]
    if bad_cr:
        fail('L', f'M12 credits not in full: {bad_cr[:2]} (IC M-12)')
    if 'ri' in [x.rstrip(",'") for x in m12['c20']] or 'di' not in [x.rstrip(",'") for x in m12['c34'] if x]:
        fail('L', f"M12 chopin20: 5-8 starts {m12['c20']}, 3-4 {m12['c34']} (IC M-11, S6)")
    if m12['outline']:
        fail('L', f"M12 bar outlines not D9: {m12['outline']} (IC S8)")
    if any(x < 0.6 for x in ic['r78']):
        fail('L', f"R7/R8 hidden new share {ic['r78']} (IC S4)")
    # S5 swing: every off-beat quaver point plays at two thirds of the beat
    sw = await pg.evaluate("""async(MK)=>{const R=eval(MK)(521);let n=0,bad=0;EAR.rhy.bpm=null;for(let i=0;i<400&&n<40;i++){const q=ladGenRhy(8,R);if(!q.swing)continue;n++;
        const r=await elRender(q,'all'),tk=60/q.tempo/420;r.info.events.forEach(e=>{const at=Math.round((e.t-r.info.start)/tk+(q.anac||0)),rel=((e.on-(q.anac||0))%420+420)%420;
          if(at!==e.on+(rel===210?70:0))bad++})}return[n,bad]}""", MK)
    COUNT['self-check L15 swing items rendered'] = sw[0]
    if sw[1] or sw[0] < 20:
        fail('L', f'swing: {sw[1]} notes not at their swung place in {sw[0]} items (IC S5)')

    # ---------------- L14: playback renders for every rung (count-in, tuplet accents, swing, backbeat, two parts) ----------------
    pb = await pg.evaluate("""async(MK)=>{const R=eval(MK)(503),o={};for(let l=1;l<=10;l++){const q=ladGenRhy(l,R);EAR.rhy.bpm=null;const r=await elRender(q,'all');
        const want=ladRhyEvents(q.a).ev.filter(e=>!e.rest).length;o['r'+l]=[r.info.events.length,want,+r.info.dur.toFixed(2)]}
        const t9=ladGenRhy(9,R,{wantNew:true});o.acc=ladRhyEvents(['q7_34']).ev.map(e=>e.acc?1:0).join('');
        for(let l=1;l<=12;l++){const q=ladGenMel(l,R);const r=await elRender(q,'all');o['m'+l]=+r.info.dur.toFixed(2)}return o}""", MK)
    COUNT['self-check L14 rungs rendered offline'] = 22
    for l in range(1, 11):
        got, want, d = pb[f'r{l}']
        if got != want or d <= 0:
            fail('L', f'R{l} playback: {got} notes scheduled, {want} written ({d} s)')
    if pb['acc'] != '1001000':
        fail('L', f"septuplet 3+4 accents {pb['acc']} (R9: +3 dB on the first of each group)")
    for l in range(1, 13):
        if not pb[f'm{l}'] > 0:
            fail('L', f'M{l} playback did not render')


async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.add_init_script("""(()=>{window.__N=[];for(const P of [AudioScheduledSourceNode.prototype,AudioBufferSourceNode.prototype]){const st=P.start,sp=P.stop;
          P.start=function(t=0,...a){this.__r={s:t||0,e:Infinity,k:this instanceof AudioBufferSourceNode?'smp':'osc'};__N.push(this.__r);return st.call(this,t,...a)};
          P.stop=function(t=0){if(this.__r)this.__r.e=Math.min(this.__r.e,t);return sp.call(this,t)}}})()""")
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1500)

        # ---------------- A: every cadence model x key x level ----------------
        cad = await pg.evaluate("""()=>{const out=[];for(const l of [1,2,3])for(const md of ['maj','min']){const ts=CADT[l][md];if(!ts)continue;
          for(const c in ts)for(const t of ts[c])for(const k of earCadKeys(l,md))for(const reg of [{b:42,s:66},{b:52,s:74},{b:42,s:74},{b:52,s:66},undefined]){const key={k,mode:md},rns=t.split(' '),P=earCadProg(l,rns,key,reg);
            const app=P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation'];
            out.push({l,md,cat:c,t,k,ch:P.ch,app,sub:cadSub(rns)})}}return out}""")
        seen = set()
        for q in cad:
            where = f"cad L{q['l']} {q['md']} {q['cat']} [{q['t']}] key {NM[q['k']]}"
            COUNT['cad realisations'] += 1
            if (q['t'], q['k'], q['md']) not in seen:
                seen.add((q['t'], q['k'], q['md']))
                COUNT['cad distinct template x key'] += 1
            if q['app']:
                fail('A', f'{where}: app SATB checker reports {q["app"]}')
                continue
            toks = q['t'].split()
            vl_check(q['ch'], toks, q['k'], q['md'], where)
            if not cad_category_ok(q['cat'], toks, q['k'], q['md']):
                fail('A', f'{where}: does not end with a {q["cat"]} cadence')
            if pop_moves(toks):
                fail('A', f'{where}: popular-style succession {pop_moves(toks)} in a common-practice model')
            if q['sub'] == 'Phrygian cadence (iv⁶–V)' and not (q['md'] == 'min' and toks[-2] == 'iv:1' and toks[-1] == 'V'):
                fail('A', f'{where}: labelled Phrygian but is not iv6-V in minor')
        # E10: same lengths in every category; at least 3 models per category per mode at L1
        lens = await pg.evaluate("""()=>{const o={};for(const l of [1,2,3])for(const md in CADT[l])for(const c in CADT[l][md])o[`${l}|${md}|${c}`]=CADT[l][md][c].map(x=>x.split(' ').length);return o}""")
        for l in (1, 2, 3):
            for md in ('maj', 'min'):
                sets = {c: set(v) for kk, v in lens.items() for c in [kk.split('|')[2]] if kk.startswith(f'{l}|{md}|')}
                if sets and len({frozenset(s) for s in sets.values()}) != 1:
                    fail('C', f'L{l} {md}: model lengths differ by category {sets}')
        # EL-7 (0.48): rung 1 is exactly the four basic cadences, two chords each (checked in full in earlab_items_test section K)
        want1 = {'1|maj|perfect': 1, '1|maj|plagal': 1, '1|maj|imperfect': 2, '1|maj|interrupted': 1}
        got1 = {kk: len(v) for kk, v in lens.items() if kk.startswith('1|')}
        if got1 != want1 or any(n != 2 for kk, v in lens.items() if kk.startswith('1|') for n in v):
            fail('C', f'rung 1 models are not the four basic two-chord cadences: {got1}')
        if await pg.evaluate("JSON.stringify(CADT[2])===JSON.stringify(CADT[3])"):
            fail('C', 'levels 2 and 3 have the same cadence models')
        l3 = await pg.evaluate("Object.values(CADT[3]).flatMap(o=>Object.values(o).flat()).join('|')")
        if ':2 V' not in l3 or 'iv:1 V' not in l3:
            fail('C', 'level 3 is missing the cadential 6/4 or the Phrygian cadence')

        # ---------------- B: bass and numerals ----------------
        bass = await pg.evaluate("""()=>{const out=[];for(const l of [1,2,3])for(const rns of earBassProgs(l))for(const k of BKEYS)for(const reg of [{b:42,s:66},{b:52,s:74},{b:47,s:70}]){const key={k,mode:'maj'},P=earBassProg(rns,key,reg);
            out.push({l,rns,k,ch:P.ch,app:P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation']})}return out}""")
        for q in bass:
            where = f"bass L{q['l']} [{' '.join(q['rns'])}] key {NM[q['k']]}"
            COUNT['bass realisations'] += 1
            if q['app']:
                fail('B', f'{where}: app SATB checker reports {q["app"]}')
                continue
            info = vl_check(q['ch'], q['rns'], q['k'], 'maj', where)
            for i, f in enumerate(info):
                if q['ch'][i][0] % 12 != f['root']:
                    fail('B', f'{where}: chord {i+1} is not in root position')
        gen = await pg.evaluate("""()=>{let s=11;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o=[];
            for(const l of [1,2,3])for(let i=0;i<2000;i++){const q=earGen('bass',l,R);o.push({l,a:q.a,opts:q.opts,bass:q.bass,ch:q.ch})}return o}""")
        allow = await pg.evaluate("EBALLOW")
        for q in gen:
            COUNT['bass questions (allow-list)'] += 1
            if q['a'][0] != 'I' or any(x not in q['opts'] for x in q['a']):
                fail('B', f"L{q['l']} {q['a']}: outside the level's chords")
            for a, b2 in zip(q['a'], q['a'][1:]):
                if b2 not in allow[a]:
                    fail('B', f"L{q['l']} {q['a']}: {a}-{b2} is not on the common-practice allow-list")
            if pop_moves(q['a']):
                fail('B', f"L{q['l']} {q['a']}: popular-style succession")
            if q['bass'] != [c[0] for c in q['ch']]:
                fail('B', 'bass-only notes are not the bass of the chords')
        gen = await pg.evaluate("""()=>{let s=13;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o=[];
            for(const l of [1,2,3])for(let i=0;i<2000;i++){const q=earGen('cad',l,R);o.push({l,a:q.a,rns:q.rns})}return o}""")
        for q in gen:
            COUNT['cadence questions (allow-list)'] += 1
            if pop_moves(q['rns']):
                fail('B', f"cad L{q['l']} {q['rns']}: popular-style succession")
            if retro_moves(q['rns']):
                fail('B', f"cad L{q['l']} {q['rns']}: retrogression {retro_moves(q['rns'])}")
        # BHL 0.48 (IC_EAR_048 S3): every model and every bass progression, as well as the generated questions above
        allp = await pg.evaluate("[...[1,2,3].flatMap(l=>Object.values(CADT[l]).flatMap(o=>Object.values(o).flat())),...[1,2,3].flatMap(l=>earBassProgs(l).map(p=>p.join(' ')))]")
        COUNT['models and bass progressions checked for ii(6)-IV'] = len(allp)
        for t in allp:
            if retro_moves(t.split()):
                fail('B', f'[{t}]: retrogression {retro_moves(t.split())}')
        for q in [x for x in await pg.evaluate("""()=>{let s=29;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o=[];for(const l of [1,2,3])for(let i=0;i<2000;i++)o.push(earGen('bass',l,R).a);return o}""")]:
            COUNT['bass questions checked for ii(6)-IV'] += 1
            if retro_moves(q):
                fail('B', f'bass {q}: retrogression {retro_moves(q)}')

        # ---------------- C: tells ----------------
        tells = await pg.evaluate("""()=>{let s=17;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o={cad:[],metre:[],qual:[]};
            for(const l of [1,2,3])for(let i=0;i<5000;i++){const c=earGen('cad',l,R);o.cad.push({l,a:c.a,sub:c.sub||'',md:c.key.mode,n:c.ch.length,lo:Math.min(...c.ch.flat()),hi:Math.max(...c.ch.flat()),
                s2:c.rns[1],open:c.ch[0].join(','),fin:c.ch[c.ch.length-1][3],fb:c.ch[0][0],lb:c.ch[c.ch.length-1][0],fs:c.ch[0][3]});
              const m=earGen('metre',l,R);o.metre.push({l,a:m.a,bpm:m.bpm,comp:/8$/.test(m.a)&&m.a!=='7/8'});
              const q=earGen('qual',l,R);o.qual.push({l,a:q.a,lo:q.notes[0],hi:q.notes[q.notes.length-1]})}return o}""")
        MARGIN = 0.05
        def tell(sec, rows, name, feat, ans, levels=(1, 2, 3)):
            for l in levels:
                rr = [r for r in rows if r['l'] == l]
                acc, ch = predict_acc(rr, feat, ans)
                COUNT['tell checks'] += 1
                if acc > ch + MARGIN:
                    fail('C', f'{sec} L{l}: {name} predicts the answer {acc:.0%} of the time (chance {ch:.0%})')
        tell('cadences', tells['cad'], 'number of chords', lambda r: r['n'], lambda r: r['a'])
        tell('cadences', tells['cad'], 'lowest note (6-semitone bands)', lambda r: r['lo'] // 6, lambda r: r['a'])
        tell('cadences', tells['cad'], 'highest note (6-semitone bands)', lambda r: r['hi'] // 6, lambda r: r['a'])
        # at rung 1 the two chords are the cadence itself, so the second and opening chords are the answer, not a tell;
        # rung 1's register, top-note, bass-note and key tells are in earlab_items_test section K
        tell('cadences', tells['cad'], 'second chord', lambda r: r['s2'], lambda r: r['a'], (2, 3))
        tell('cadences', tells['cad'], 'opening voicing', lambda r: r['open'], lambda r: r['a'], (2, 3))
        # register 0.48 (design spec section 11): mode and phrase length, alone and together, must not give the answer away
        tell('cadences', tells['cad'], 'mode', lambda r: r['md'], lambda r: r['a'])
        tell('cadences', tells['cad'], 'mode and number of chords', lambda r: (r['md'], r['n']), lambda r: r['a'])
        tell('cadences', tells['cad'], 'lowest and highest note (6-semitone bands)', lambda r: (r['lo'] // 6, r['hi'] // 6), lambda r: r['a'])
        # 0.49 C3 (IC_EAR2_048 C2): exact-semitone register tells at rungs 2 and 3, alone and with the mode. Before 0.49 the exact lowest and
        # highest note pair predicted the answer 11 (rung 2) and 14 (rung 3) points above chance, and the last bass note 11 (rung 2, 7 keys).
        # Rung 1's are in earlab_items_test section K. The bass and soprano degrees (lowest note as do or so ...) are the cadence, not a tell.
        EX = (('lowest note (exact)', lambda r: r['lo']), ('highest note (exact)', lambda r: r['hi']), ('lowest and highest note (exact pair)', lambda r: (r['lo'], r['hi'])),
              ('span (exact)', lambda r: r['hi'] - r['lo']), ('first bass note (exact)', lambda r: r['fb']), ('last bass note (exact)', lambda r: r['lb']),
              ('first soprano note (exact)', lambda r: r['fs']), ('last soprano note (exact)', lambda r: r['fin']))
        for name, f in EX:
            tell('cadences', tells['cad'], name, f, lambda r: r['a'], (2, 3))
            tell('cadences', tells['cad'], 'mode and ' + name, lambda r, f=f: (r['md'], f(r)), lambda r: r['a'], (2, 3))
        for l in (2, 3):
            rr = [r for r in tells['cad'] if r['l'] == l]
            for name, f in EX[:4]:
                acc, ch = predict_acc(rr, f, lambda r: r['a'])
                COUNT[f'info: rung {l} {name}: accuracy vs chance'] = f'{acc:.1%} vs {ch:.1%}'
        # the balanced table is in place and current (its length matches the index; a stale or missing table falls back to the old draw)
        t23 = await pg.evaluate("({w2:!!earR23Weights(2),w3:!!earR23Weights(3),draw:/earR23Draw\\(l,mode,a,r\\)/.test(earGenCad.toString()),keys2:earCadKeys(2,'maj').length+earCadKeys(2,'min').length,"
                                "nz2:(earR23Weights(2)||[]).filter(x=>x>0).length,nz3:(earR23Weights(3)||[]).filter(x=>x>0).length})")
        COUNT['C3 balanced table (rungs 2, 3): entries with weight > 0'] = f"{t23['nz2']}, {t23['nz3']}"
        if not (t23['w2'] and t23['w3'] and t23['draw'] and t23['keys2'] == 24):
            fail('C', f'C3: EAR23W missing or stale, or rung 2 not on all 24 keys (run tests/gen_cad23_weights.py): {t23}')
        # if rung 3 is marked with the refined answers (Phrygian, cadential 6/4), mode and length are reported against those as well
        for l in (3,):
            rr = [r for r in tells['cad'] if r['l'] == l]
            ref = lambda r: r['a'] + ('|' + r['sub'] if r['sub'] else '')
            for name, feat in (('mode', lambda r: r['md']), ('number of chords', lambda r: r['n']), ('mode and number of chords', lambda r: (r['md'], r['n']))):
                acc, ch = predict_acc(rr, feat, ref)
                COUNT[f'info: rung 3 refined answers, {name}: accuracy vs chance'] = f'{acc:.0%} vs {ch:.0%}'
                if rr and any(r['a'] in ('phrygian', 'cad64') for r in rr) and acc > ch + MARGIN:
                    fail('C', f'cadences L3 (refined answers): {name} predicts the answer {acc:.0%} of the time (chance {ch:.0%})')
        # the two rung 3 models that end interrupted after a cadential 6/4: kept as interrupted models (Justin, 19 Nov 2026; full checks in
        # earlab_items_test section I)
        held = await pg.evaluate("CAD3_HELD.filter(x=>Object.values(CADT[3]).some(o=>(o.interrupted||[]).includes(x)))")
        if len(held) != 2:
            fail('C', f'interrupted-after-6/4 models in the rung 3 interrupted pool: {held}')
        # merge 0.48: one register path for cadence items (earCadReg); 0.48 logic: "Nearly" on, held models in; BHL 0.48: CAD64_INT_NEARLY on
        # (Justin 20 Nov 2026, item B)
        mg = await pg.evaluate("({reg:/earCadReg\\(rns,key,r/.test(earGenCad.toString()),nearly:EAR_NEARLY,hold:CAD3_HOLD,int:CAD64_INT_NEARLY})")
        COUNT['merge checks (earCadReg path, Nearly on, CAD64_INT_NEARLY on, held models in)'] = 4
        if not mg['reg'] or mg['nearly'] is not True or mg['hold'] is not False or mg['int'] is not True:
            fail('C', f'merge: earGenCad register path / Nearly / hold switch / CAD64_INT_NEARLY: {mg}')
        tell('metre', tells['metre'], 'tempo (10-bpm bands)', lambda r: r['bpm'] // 10, lambda r: r['comp'])
        tell('metre', tells['metre'], 'tempo (10-bpm bands)', lambda r: r['bpm'] // 10, lambda r: r['a'])
        tell('chord quality', tells['qual'], 'lowest note (6-semitone bands)', lambda r: r['lo'] // 6, lambda r: r['a'])
        for l in (1, 2, 3):
            bp = [r['bpm'] for r in tells['metre'] if r['l'] == l]
            if min(bp) < 60 or max(bp) > 120 or max(bp) - min(bp) < 50:
                fail('C', f'metre L{l}: tempo range {min(bp)}-{max(bp)} is not 60-120')
        # the second chord must not give the category away (the old level-1 plagal tell)
        for l in (2, 3):
            rr = [r for r in tells['cad'] if r['l'] == l]
            by = collections.defaultdict(set)
            for r in rr:
                by[r['s2']].add(r['a'])
            only = {k: v for k, v in by.items() if len(v) == 1}
            if only:
                fail('C', f'cadences L{l}: second chord {list(only)} occurs in only one category')

        # ---------------- D: pool sizes at level 1 ----------------
        pools = await pg.evaluate("""()=>{let s=19;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};
            const d=(dr,f)=>{const S=new Set();for(let i=0;i<30000;i++){const q=earGen(dr,1,R);if(q)S.add(f(q))}return S.size};
            return{'melodic dictation (solfa sequences)':d('mel',q=>q.a.join(' ')),'chord quality (distinct voicings)':d('qual',q=>q.notes.join(',')),'bass (progression x key)':d('bass',q=>q.a.join(' ')+'|'+q.key.k)}}""")
        for k, v in pools.items():
            COUNT[f'L1 pool: {k}'] = v
            # EL-6 (0.48): chord quality is root position only, close spacing, two registers, so rung 1 (major, minor) has
            # 2 x 12 roots x 2 registers = 48 voicings; the floor there is all 48, not 100
            floor = 48 if k.startswith('chord quality') else 100
            if v < floor:
                fail('D', f'level 1 {k}: {v} distinct items (floor {floor})')
        # 0.49 C4: rung 1 interrupted cadence (V–vi). Its pool is every strict, open, complete realisation in the twelve keys; this
        # independent enumeration (strict common-practice rules, below) finds the same set, so the 28 voicings are the honest maximum while
        # rung 1 keeps open spacing and complete chords (EL-7 / BHL H). With close spacing allowed it would be 108 (register 0.49 C12, Drafted).
        r1 = await pg.evaluate("()=>({vvi:earR1Pool().filter(p=>p.t==='V vi').map(p=>p.k+':'+p.ch.map(v=>v.join(',')).join('|')),by:earR1Pool().reduce((o,p)=>(o[p.t]=(o[p.t]||0)+1,o),{}),"
                               "w:Object.fromEntries(Object.entries(earR1Weights()).map(([a,L])=>[a,L.filter(e=>e.w>=1e-4).length]))})")
        mine = {f"{k}:{','.join(map(str, P))}|{','.join(map(str, N))}" for k in range(12) for P, N in vvi_enum(k)}
        mine_close = sum(len(vvi_enum(k, open_only=False)) for k in range(12))
        COUNT['C4 rung 1 V–vi: app pool / independent enumeration (open) / with close spacing'] = f"{len(r1['vvi'])} / {len(mine)} / {mine_close}"
        COUNT['C4 rung 1 pool per model'] = json.dumps(r1['by'])
        COUNT['C4 rung 1 pool entries with weight >= 1e-4 per answer'] = json.dumps(r1['w'])
        if set(r1['vvi']) != mine:
            fail('D', f"C4 rung 1 V–vi pool differs from the independent enumeration: app only {sorted(set(r1['vvi']) - mine)[:3]}, enumeration only {sorted(mine - set(r1['vvi']))[:3]}")
        if r1['w'].get('interrupted', 0) < len(mine):
            fail('D', f"C4 rung 1 interrupted: only {r1['w'].get('interrupted')} of {len(mine)} voicings carry weight")

        # ---------------- E: blind analysis ----------------
        blind = await pg.evaluate("""async()=>{await earLoadBlind();return{items:EAR.blind.map(x=>({...x})),cats:[1,2,3].map(l=>earBlindCats(l)),meta:AN.meta}}""")
        meta = blind['meta']
        items = blind['items']
        expected = sum(1 for k in ['chorale', 'ohaupt', 'jesu', 'k331a', 'k331d', 'chopin7', 'chopin20'] for c in meta[k]['cads'] if c.get('blind') is not False)
        if len(items) != expected or expected != 30:
            fail('E', f'blind pool has {len(items)} items, expected 30 (31 cadences minus O Haupt bar 6)')
        if any(x['score'] == 'ohaupt' and x['bar'] == '6' for x in items):
            fail('E', 'O Haupt bar 6 (V4/3-I with a plagal neighbour) is still in the marked pool')
        for x in items:
            COUNT['blind items checked'] += 1
            m = meta[x['score']]
            tn, md = m['key'].replace('♭', '-').replace('♯', '#').split()
            kk = m21key.Key(tn if md == 'major' else tn.lower())
            last = x['chords'].split('–')[-1].strip().split()[0].replace('64', '')
            r = roman.RomanNumeral(last, kk)
            pcs = {q.pitchClass for q in r.pitches}
            # notes as the app plays them: onset in [s-5, e-5), each cut at e
            ev = [(ms, pp, min(d, x['e'] - ms)) for ms, pp, d in m['events'] if x['s'] - 5 <= ms < x['e'] - 5]
            tend = max(ms + d for ms, pp, d in ev)
            last_snd = {pp % 12 for ms, pp, d in ev if ms < tend - 1 and ms + d >= tend - 30}
            where = f"{x['score']} bar {x['bar']} ({x['chords']})"
            if not last_snd or not last_snd <= pcs or r.root().pitchClass not in last_snd:
                fail('E', f'{where}: last sounding notes {sorted(NM[q] for q in last_snd)} are not the final chord {r.figure} {sorted(NM[q] for q in pcs)}')
            # E2: nothing from the next bar's downbeat or the next phrase
            nxt = [ms for ms, pp, d in m['events'] if ms >= x['e'] - 5 and ms < x['e'] + 5]
            later = [ms for ms, pp, d in ev if ms > x['a'] + 5 and any((pp2 % 12) not in pcs for ms2, pp2, d2 in ev if abs(ms2 - ms) <= 5)]
            if later:
                fail('E', f'{where}: notes outside the cadence chord start after the arrival at {later[:3]}')
            # bar number shown = the bar the cadence arrives in
            arr_bar = [b2 for b2, mid, t0 in m['measures'] if t0 <= x['a'] + 5][-1]
            if arr_bar != x['bar']:
                fail('E', f'{where}: bar shown {x["bar"]}, arrival is in bar {arr_bar}')
        for l, cats in zip((1, 2, 3), blind['cats']):
            for c in cats:
                if not any(x['cat'] == c and x['lvl'] <= l for x in items):
                    fail('E', f'level {l}: button {c} is offered but no item has that answer')
            for c in {x['cat'] for x in items if x['lvl'] <= l}:
                if c not in cats:
                    fail('E', f'level {l}: answer {c} occurs but has no button')
        # E3: the relabelled cadences. 0.48 R8 re-read the chorale cadences from the notes (tests/numeral_reread.py, which
        # generates them): (7) = a passing minor 7th above the root after the chord's onset. Jesu bar 11: alto F♯–E–D♯
        # over F♯ (passing 7th); O Haupt bar 4: alto F♯–E–D over F♯ (passing 7th); Jesu bar 8: no C sounds (the soprano G
        # over D is a 4th anticipating III), so VII – III, as the numeral row names that chord.
        want = {('k331d', 2): 'vii°7/V – V', ('chopin7', 1): 'V7 – I', ('jesu', 4): 'V(7)/V – V', ('jesu', 1): 'V65/V – V', ('ohaupt', 1): 'V(7)/vi – vi',
                ('chorale', 3): 'V7/IV – IV', ('jesu', 3): 'VII – III'}
        for (k, i), ch in want.items():
            if meta[k]['cads'][i]['ch'] != ch:
                fail('E', f'{k} cadence {i+1}: chords "{meta[k]["cads"][i]["ch"]}", expected "{ch}"')
        if 'Picardy' not in meta['jesu']['cads'][5]['t']:
            fail('E', 'Jesu final cadence does not mention the Picardy third')
        if meta['chopin7']['cads'][1].get('bar') not in (None, 15):
            fail('E', 'Chopin 7 final cadence still shows bar %s' % meta['chopin7']['cads'][1].get('bar'))
        if 'cadential 6/4' in meta['chopin7']['cads'][1]['t'] or 'cadential 6/4 to close' in json.dumps(meta['chopin7']['sections'], ensure_ascii=False):
            fail('E', 'Chopin 7 still calls its final cadence a cadential 6/4')
        if 'Befiehl du deine Wege' not in meta['ohaupt']['t']:
            fail('E', 'BWV 244/44 title is not "Befiehl du deine Wege"')

        # ---------------- F: blind playback note lengths ----------------
        await pg.evaluate("ac();loadSamples('piano')")
        await pg.wait_for_timeout(3000)
        ok_smp = await pg.evaluate("!!(SBUF.piano&&Object.keys(SBUF.piano).length)")
        if not ok_smp:
            fail('F', 'piano samples did not load, so note lengths were not tested')
        else:
            for x in items:
                res = await pg.evaluate("""(x)=>{stopAll();__N.length=0;EAR.q={d:'blind',...x,a:x.cat};earPlay();
                    const nodes=__N.map(n=>({s:n.s,e:n.e,k:n.k}));stopAll();return{nodes}}""", x)
                m = meta[x['score']]
                ev = [(ms, min(d, x['e'] - ms) / 1000) for ms, pp, d in m['events'] if x['s'] - 5 <= ms < x['e'] - 5]
                nodes = [n for n in res['nodes'] if n['e'] != float('inf')]
                # the tonic cue sounds first (1.8 s of synth); score notes start after it. A synth fallback note is two oscillators.
                t_first = min(n['s'] for n in nodes)
                score = [n for n in nodes if n['s'] >= t_first + 1.7]
                t0n = min(n['s'] for n in score)
                ms0 = min(max(ms, x['s']) for ms, d in ev)
                onsets = sorted({max(ms, x['s']) - ms0 for ms, d in ev})
                def near(rel):
                    o = min(onsets, key=lambda o: abs(o - rel))
                    return o if abs(o - rel) <= 3 else None
                played = collections.defaultdict(list)
                for n in score:
                    o = near((n['s'] - t0n) * 1000)
                    if o is None:
                        fail('F', f"{x['score']} bar {x['bar']}: a note starts at {(n['s']-t0n):.3f} s where the score has none")
                        continue
                    played[o].append(n['e'] - n['s'])
                written = collections.defaultdict(list)
                for ms, d in ev:
                    written[max(ms, x['s']) - ms0].append(d)
                if set(played) != set(written):
                    fail('F', f"{x['score']} bar {x['bar']}: {len(set(written)-set(played))} written onsets were not played")
                for o, ls in played.items():
                    for h in ls:
                        COUNT['blind note nodes timed'] += 1
                        if h > max(written[o]) + 0.15 + 1e-6:
                            fail('F', f"{x['score']} bar {x['bar']}: a note sounds {h:.2f} s, the longest written note there is {max(written[o]):.2f} s")
        await pg.evaluate("stopAll()")

        # ---------------- G: ranges ----------------
        rng = await pg.evaluate("""()=>{let s=23;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};let mel=99,ql=99,qh=0,bl=99;
            for(const l of [1,2,3])for(let i=0;i<2000;i++){const m=earGen('mel',l,R);mel=Math.min(mel,...m.midi);const q=earGen('qual',l,R);ql=Math.min(ql,q.notes[0]);qh=Math.max(qh,...q.notes);
              const c=earGen('cad',l,R);bl=Math.min(bl,...c.ch.map(x=>x[0]));const b=earGen('bass',l,R);bl=Math.min(bl,...b.ch.map(x=>x[0]))}
            const dos=[0,2,5,7,10,3,9].map(k=>earDo({k,mode:'maj'}).m);return{mel,ql,qh,bl,dos}}""")
        if rng['mel'] < 55:
            fail('G', f"melody reaches MIDI {rng['mel']} (floor G3 = 55)")
        if any(d < 60 for d in rng['dos']):
            fail('G', f"do sits below middle C in a major key: {rng['dos']}")
        if rng['ql'] < 49:
            fail('G', f"chord quality reaches MIDI {rng['ql']} (floor C#3 = 49)")
        if rng['bl'] < 40:
            fail('G', f"bass reaches MIDI {rng['bl']} (floor E2 = 40)")

        # ---------------- H: text ----------------
        txt = await pg.evaluate("""()=>({tip:ELTIPS.blind.map(x=>x.join(' ')).join(' ')+' '+ELTIPNOTE.blind,cadl:CADL,labels:Object.values(AN.meta).flatMap(m=>(m.cads||[]).map(c=>c.t))})""")
        if 'checked independently in music21' in txt['tip'] or 'independent review' not in txt['tip']:
            fail('H', 'the blind-analysis tip still overstates the checking (E7)')
        # 0.48 R6: the answer buttons show the Australian term only; the US term is on hover (title) and in the feedback
        if txt['cadl'] != {'perfect': 'Perfect cadence', 'plagal': 'Plagal cadence', 'imperfect': 'Imperfect cadence', 'interrupted': 'Interrupted cadence'}:
            fail('H', f"cadence buttons are not the Australian term only: {txt['cadl']}")
        for t in txt['labels']:
            if t.lower().startswith('half cadence') or 'authentic' in t.lower() and '(authentic)' not in t.lower():
                fail('H', f'cadence label not NSW-first: "{t}"')

        # ---------------- I: every drill renders and marks ----------------
        for d in ['metre', 'rhy', 'qual', 'cad', 'bass', 'mel', 'blind']:
            for l in (1, 2, 3):
                await pg.evaluate(f"""(async()=>{{EAR.drill='{d}';EAR.lvl['{d}']={l};EAR.q=null;renderEar();if('{d}'==='blind')await earLoadBlind();earNew();
                    stopAll();earMark(false,null);renderEar();stopAll()}})()""")
                await pg.wait_for_timeout(120)
                COUNT['drill x level rendered'] += 1
        if errs:
            fail('I', f'page errors: {errs[:5]}')

        # ---------------- J: independent checker fixtures ----------------
        fx = pathlib.Path(__file__).resolve().parent / 'fixtures' / 'earlab_ic.json'
        if fx.exists():
            F = json.loads(fx.read_text())
            for row in F.get('blind', []):
                x = next((i for i in items if i['score'] == row['score'] and i['bar'] == row['bar']), None)
                COUNT['fixture rows (blind)'] += 1
                if x is None:
                    fail('J', f"fixture {row['score']} bar {row['bar']}: not in the app's pool")
                    continue
                if x['cat'] != row['cat']:
                    fail('J', f"fixture {row['score']} bar {row['bar']}: app says {x['cat']}, checker says {row['cat']}")
                if 'final_pcs' in row:
                    m = meta[x['score']]
                    ev = [(ms, pp, min(d, x['e'] - ms)) for ms, pp, d in m['events'] if x['s'] - 5 <= ms < x['e'] - 5]
                    tend = max(ms + d for ms, pp, d in ev)
                    last_snd = {pp % 12 for ms, pp, d in ev if ms < tend - 1 and ms + d >= tend - 30}
                    if not last_snd <= set(row['final_pcs']):
                        fail('J', f"fixture {row['score']} bar {row['bar']}: final notes {sorted(last_snd)} vs checker {row['final_pcs']}")
            for row in F.get('cadence_pcs', []):
                COUNT['fixture rows (chords)'] += 1
                got = next((q for q in cad if q['t'] == row['t'] and q['k'] == row['k'] and q['md'] == row['md']), None)
                if got is None:
                    # R16 (0.48): rows for retired models were removed (tests/fixtures/make_cadence_pcs.py), so an unmatched row is a failure
                    fail('J', f"fixture {row['t']} key {row['k']} {row['md']}: the app no longer has this model")
                    continue
                if not got['ch']:
                    fail('J', f"fixture {row['t']} key {row['k']}: not generated")
                    continue
                for i, pcs in enumerate(row['pcs']):
                    if not {m % 12 for m in got['ch'][i]} <= set(pcs):
                        fail('J', f"fixture {row['t']} key {row['k']} chord {i+1}: {sorted({m%12 for m in got['ch'][i]})} vs {pcs}")
            # every model x key the app uses has a fixture row
            rows = {(r['t'], r['k'], r['md']) for r in F.get('cadence_pcs', [])}
            miss = sorted({(q['t'], q['k'], q['md']) for q in cad} - rows)
            COUNT['fixture coverage (model x key)'] = f"{len(rows & {(q['t'], q['k'], q['md']) for q in cad})} of {len({(q['t'], q['k'], q['md']) for q in cad})}"
            if miss:
                fail('J', f'{len(miss)} model x key combinations have no fixture row, e.g. {miss[:3]}')
        else:
            fail('J', 'tests/fixtures/earlab_ic.json is missing')
        n0 = len(errs)
        await ladder_section(pg)
        if len(errs) > n0:
            fail('L', f'page errors in the ladder checks: {errs[n0:][:3]}')
        await b.close()

    report = {'counts': dict(COUNT), 'failures': {k: v[:25] for k, v in FAIL.items()}, 'n_failures': sum(len(v) for v in FAIL.values())}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)

asyncio.run(main())
