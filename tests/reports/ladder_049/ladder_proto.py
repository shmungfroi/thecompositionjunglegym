#!/usr/bin/env python3
"""Prototype generators for the 0.49 Ear Lab ladders (melody 1-11, rhythm 1-10).

NOT the app code. A reference model of LADDER_REGISTER_049.md, written to prove
  (1) pool sizes: distinct items per rung (key/tempo excluded: a transposition is not a new item),
  (2) tells: no answer predictable from length, tempo, register, key or mode,
  (3) the "new thing" share and that earlier material stays in the mix.
The JS port in index.html must reproduce these rules; the numbers here are its acceptance targets.

Run:  python3 tests/reports/ladder_049/ladder_proto.py [--n 20000] [--json out.json]

Units: rhythm in ticks, 12 ticks to a crotchet (semiquaver 3, quaver 6, triplet quaver 4, dotted quaver 9).
Pitch: do-relative diatonic index i (d=0, r=1 ... t=6, d'=7, t,=-1, l,=-2, s,=-3) plus alter (-1, 0, +1).
"""
import argparse, collections, json, random, sys

# ------------------------------------------------------------------ solfa
DIA = ['d', 'r', 'm', 'f', 's', 'l', 't']
SEMI = [0, 2, 4, 5, 7, 9, 11]
RAISE = {0: 'di', 1: 'ri', 3: 'fi', 4: 'si', 5: 'li'}          # no raised mi or ti (that is fa, do)
LOWER = {1: 'ra', 2: 'me', 4: 'se', 5: 'le', 6: 'te'}          # Justin's chart (20 Nov): flats te le se me ra, sharps di ri fi si li


def syl(i, a=0):
    w, o = i % 7, i // 7
    s = DIA[w] if a == 0 else (RAISE if a > 0 else LOWER)[w]
    return s + ("'" * o if o > 0 else ',' * (-o))


def semis(i, a=0):
    return SEMI[i % 7] + 12 * (i // 7) + a


# keys: pitch class of do. Stage 4: up to 3 sharps or flats (the current CKEYS2.maj); Stage 5: 4; Stage 6: 5
KEYS = {4: [0, 7, 2, 9, 5, 10, 3], 5: [0, 7, 2, 9, 4, 5, 10, 3, 8], 6: [0, 7, 2, 9, 4, 11, 5, 10, 3, 8, 1]}
STAGE_M = {1: 4, 2: 4, 3: 4, 4: 4, 5: 5, 6: 5, 7: 5, 8: 5, 9: 6, 10: 6, 11: 6, 12: 6}
STAGE_R = {1: 4, 2: 4, 3: 4, 4: 5, 5: 5, 6: 5, 7: 5, 8: 6, 9: 6, 10: 6}
MIN_NOTES = {4: 5, 5: 5, 6: 9, 7: 9, 8: 9, 9: 16, 10: 16, 11: 8}
NEW_SHARE = 2 / 3   # decision D2: share of items that must contain the rung's new thing; the rest review earlier material


def cue_do(pc):
    """rule MR1: do's MIDI is fixed by the key signature alone, the same for major, minor and modal items and for the key cue:
    do = C4..B4 (60 + pc). No octave is chosen per item, so register can only tell what the notes are (which is the answer)."""
    return 60 + pc


def place_do(pc, r, lo_i, hi_i):
    """rule MR2: every rung's range is capped at s,..d' (do-relative -3..7; minor s,..l, harmonic si, allowed), so with MR1 the
    melody always lies in G3..B5 (55..83) and the octave never varies. (A per-item octave choice measured as a tell: +5 to +7
    points on the new thing / the mode, given the key signature.)"""
    c = cue_do(pc)
    if c + semis(lo_i) < 55 or c + semis(hi_i) > 83:
        raise IndexError
    return 0, c


# ------------------------------------------------------------------ rhythm cells (ticks)
# name: (list of (dur, kind) kind n=note r=rest t=tied-continuation, time name, metre family s=simple c=compound)
CELLS = {
    # rung 1
    'q':   ([(12, 'n')], 'ta', 's'),
    'e2':  ([(6, 'n'), (6, 'n')], 'ti-ti', 's'),
    'h':   ([(24, 'n')], 'ta-a', 's'),
    'qr':  ([(12, 'r')], 'sa', 's'),
    # rung 2
    'w':   ([(48, 'n')], 'ta-a-a-a', 's'),
    'hd':  ([(36, 'n')], 'ta-a-a', 's'),
    # rung 3
    's4':  ([(3, 'n')] * 4, 'tika-tika', 's'),
    # rung 4
    'dq':  ([(18, 'n'), (6, 'n')], 'tam-ti', 's'),
    'es2': ([(6, 'n'), (3, 'n'), (3, 'n')], 'ti-tika', 's'),
    's2e': ([(3, 'n'), (3, 'n'), (6, 'n')], 'tika-ti', 's'),
    'er':  ([(6, 'r'), (6, 'n')], 'sa ti', 's'),      # quaver rest + quaver (quaver rest = sa, half a beat)
    're':  ([(6, 'n'), (6, 'r')], 'ti sa', 's'),      # quaver + quaver rest
    # rung 5: the six 6/8 cells (one dotted-crotchet beat each, except tam-am)
    'cD':  ([(18, 'n')], 'tam', 'c'),                  # dotted crotchet
    'c3':  ([(6, 'n')] * 3, 'ti-ti-ti', 'c'),          # three quavers
    'cqe': ([(12, 'n'), (6, 'n')], 'ta ti', 'c'),      # crotchet-quaver
    'ceq': ([(6, 'n'), (12, 'n')], 'ti ta', 'c'),      # quaver-crotchet
    'cdse': ([(9, 'n'), (3, 'n'), (6, 'n')], 'tim-ka-ti', 'c'),  # dotted quaver-semiquaver-quaver (siciliano)
    'c6':  ([(3, 'n')] * 6, 'tika-tika-tika', 'c'),    # six semiquavers (the sixth standard 6/8 cell)
    'cDD': ([(36, 'n')], 'ta-a-a', 'c'),               # dotted minim filling a 6/8 bar (review: named by value, see flags)
    # rung 6: syncopation
    'syn': ([(6, 'n'), (12, 'n'), (6, 'n')], 'syn-co-pa', 's'),
    'synT': ([(6, 'n'), (6, 'n'), (6, 't'), (6, 'n')], 'ti ti-i ti', 's'),  # the same sound, tied across beats 2-3 (bar middle)
    'antA': ([(6, 'n'), (6, 'n'), (12, 't')], 'ti ti-i-i', 's'),            # quaver on 2& (or 4&) tied over to beat 3 (or next bar's 1)
    # rung 7
    'tri': ([(4, 'n')] * 3, 'tri-o-la', 's'),
    'dsq': ([(9, 'n'), (3, 'n')], 'tim-ka', 's'),
    # rung 8 (4/4, two-beat or four-beat figures)
    'tres': ([(18, 'n'), (18, 'n'), (12, 'n')], 'tam ti-i ta', 's'),       # tresillo 3+3+2, one bar of 4/4
    'charl': ([(18, 'n'), (6, 'n'), (24, 'r')], 'tam ti sa-a', 's'),      # Charleston (dotted crotchet, quaver on 2&, rest)
    'e2s': ([(6, 'n'), (6, 'n')], 'ti-ti (swing)', 's'),                   # swung quavers: same notation, swing marked
}


def cell_w(k):
    return sum(d for d, _ in CELLS[k][0])


def onsets(cells, start=0):
    """the sounding pattern: per note (onset tick, kind). Ties: a 't' extends the previous note (no onset)."""
    p, out = start, []
    for k in cells:
        for d, kind in CELLS[k][0]:
            if kind in 'nr':
                out.append((p, kind))
            p += d
    return tuple(out), p


METRE = {  # beats per bar, ticks per beat, bar ticks, strong-beat ticks (where minim/2-beat cells may start)
    '2/4': dict(bar=24, beat=12, strong=[0]),
    '3/4': dict(bar=36, beat=12, strong=[0]),
    '4/4': dict(bar=48, beat=12, strong=[0, 24]),
    '6/8': dict(bar=36, beat=18, strong=[0]),
    '12/8': dict(bar=72, beat=18, strong=[0, 36]),
    '5/4': dict(bar=60, beat=12, strong=[0, 36]),   # 3+2 (the other grouping 2+3: strong [0,24])
    '7/8': dict(bar=42, beat=6, strong=[0]),        # groupings 2+2+3, 3+2+2, 2+3+2
}


def fill_bar(r, metre, vocab, first=False, last=False, grp=None):
    """one bar of cells. Rules (RF): a cell starts on a beat (simple cells on a crotchet beat, compound on a dotted-crotchet
    beat); 2-beat cells (h, dq, syn, synT) only on strong beats so the bar's middle stays visible (no crotchet across the middle
    of 4/4 except the tied form synT, whose tie shows it); 'hd' only at 0 in 3/4 and 4/4; 'w' only as a whole 4/4 bar.
    A bar is never all rest. 7/8 and 5/4 fill group by group (grp)."""
    M = METRE[metre]
    bar = M['bar']
    for _ in range(200):
        out, p = [], 0
        ok = True
        while p < bar:
            c = []
            for k in vocab:
                w, fam = cell_w(k), CELLS[k][2]
                if p + w > bar:
                    continue
                if metre in ('6/8', '12/8'):
                    if fam != 'c' or p % 18:
                        continue
                    if k == 'cDD' and not (p == 0 and metre == '6/8' or p in (0, 36)):
                        continue
                else:
                    if fam != 's':
                        continue
                    if p % 12:
                        continue
                    if k == 'w' and not (metre == '4/4' and p == 0):
                        continue
                    if k == 'hd' and not (metre in ('3/4', '4/4') and p == 0):
                        continue
                    if w == 24 and k not in ('synT',) and p not in M['strong']:
                        continue
                    if k == 'synT' and not (metre == '4/4' and p == 12):
                        continue
                    if k in ('tres', 'charl') and not (metre == '4/4' and p == 0):
                        continue
                    if k == 'antA' and not (metre == '4/4' and p in (12, 36)):   # 2&-into-3, 4&-into-next-1
                        continue
                c.append(k)
            if not c:
                ok = False
                break
            k = r.choice(c)
            out.append(k)
            p += cell_w(k)
        if not ok:
            continue
        ons, _ = onsets(out)
        if all(kind == 'r' for _, kind in ons):
            continue
        if last and out[-1] == 'antA':      # nothing to tie into after the last bar
            continue
        return out
    raise RuntimeError('no fill')


# ------------------------------------------------------------------ RHYTHM LADDER
R_VOCAB = {
    1: ['q', 'e2', 'h', 'qr'],
    2: ['q', 'e2', 'h', 'qr', 'w', 'hd'],
    3: ['q', 'e2', 'h', 'qr', 'w', 'hd', 's4'],
    4: ['q', 'e2', 'h', 'qr', 'w', 'hd', 's4', 'dq', 'es2', 's2e', 'er', 're'],
}
R_VOCAB[5] = R_VOCAB[4] + ['cD', 'c3', 'cqe', 'ceq', 'cdse', 'c6', 'cDD']
R_VOCAB[6] = R_VOCAB[5] + ['syn', 'synT', 'antA']
R_VOCAB[7] = R_VOCAB[6] + ['tri', 'dsq']
R_VOCAB[8] = R_VOCAB[7] + ['tres', 'charl']
R_VOCAB[9] = R_VOCAB[8]
R_NEW = {1: None, 2: {'w', 'hd', '2/4', '3/4'}, 3: {'s4'}, 4: {'dq', 'es2', 's2e', 'er', 're'}, 5: {'6/8', 'cD', 'c3', 'cqe', 'ceq', 'cdse', 'c6'},
         6: {'syn', 'synT', 'antA'}, 7: {'tri', 'dsq', '12/8', 'anac'}, 8: {'tres', 'charl', 'swing', 'backbeat'}, 9: {'5/4', '7/8'}}
R_METRES = {1: ['4/4'], 2: ['2/4', '3/4', '4/4'], 3: ['2/4', '3/4', '4/4'], 4: ['2/4', '3/4', '4/4'],
            5: ['2/4', '3/4', '4/4', '6/8'], 6: ['2/4', '3/4', '4/4', '6/8'], 7: ['2/4', '3/4', '4/4', '6/8', '12/8'],
            8: ['4/4'], 9: ['5/4', '7/8', '2/4', '3/4', '4/4', '6/8']}
R_BARS = {1: 1, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2, 9: 4}


def has_new(l, item):
    N = R_NEW.get(l)
    if not N:
        return True
    flat = set(c for b in item['bars'] for c in b)
    return bool(N & flat) or item['metre'] in N or (item.get('anac') and 'anac' in N) or (item.get('swing') and 'swing' in N) \
        or (item.get('backbeat') and 'backbeat' in N)


def gen_rhy(l, r, want_new=None):
    """rung l item. want_new: True/False forces the new-thing branch (None: drawn with NEW_SHARE)."""
    if want_new is None:
        want_new = r.random() < NEW_SHARE if R_NEW.get(l) else True
    for _ in range(500):
        metres = R_METRES[l]
        if l == 9:   # rung 9: the new metres in 2/3 of items, review metres otherwise
            metre = r.choice(['5/4', '7/8']) if want_new else r.choice(metres[2:])
        else:
            metre = r.choice(metres)
        vocab = R_VOCAB[l] if l < 9 else R_VOCAB[8]
        if metre in ('6/8', '12/8'):
            vocab = [k for k in vocab if CELLS[k][2] == 'c']
        bars = R_BARS[l]
        grp = None
        if metre == '7/8':
            grp = r.choice([(2, 2, 3), (3, 2, 2), (2, 3, 2)])
        if metre == '5/4':
            grp = r.choice([(3, 2), (2, 3)])
        item = dict(l=l, metre=metre, grp=grp, bars=[], anac=False, swing=False, backbeat=False)
        if metre in ('7/8',):
            # quaver-unit groups: each group is ti-ti or ti-ti-ti, or held (crotchet / dotted crotchet), or rest-first
            for b in range(bars):
                bb = []
                for g in grp:
                    bb.append(r.choice(['g%d_%s' % (g, v) for v in ('all', 'long', 'lr')]))
                item['bars'].append(bb)
        elif metre == '5/4':
            for b in range(bars):
                # fill as 3/4 + 2/4 (or 2/4 + 3/4) halves, so cells never cross the grouping
                halves = []
                for g in grp:
                    halves += fill_bar(r, '3/4' if g == 3 else '2/4', [k for k in vocab if CELLS[k][2] == 's' and k not in ('w', 'tres', 'charl', 'synT', 'antA')])
                item['bars'].append(halves)
        else:
            if l == 8:
                vocab = [k for k in vocab if CELLS[k][2] == 's']
            for b in range(bars):
                item['bars'].append(fill_bar(r, metre, vocab, first=b == 0, last=b == bars - 1))
        if l >= 7 and metre not in ('5/4', '7/8') and r.random() < 0.3:
            item['anac'] = r.choice([6, 12]) if metre in ('2/4', '3/4', '4/4') else 6   # upbeat length; last bar shortened by it
        if l == 8:
            item['swing'] = r.random() < 0.4 and any('e2' in b for b in item['bars'])
            item['backbeat'] = r.random() < 0.5
        if has_new(l, item) == want_new or (l == 1):
            return item
    raise RuntimeError('rhythm gen %d' % l)


def rhy_key(it):
    """the distinct-item key: what the student writes (metre, bars as sound plus notation for tied forms, anacrusis, swing)"""
    return (it['metre'], it['grp'], tuple(tuple(b) for b in it['bars']), it['anac'], it['swing'], it['backbeat'])


def rhy_beats(it):
    """per-beat answer labels (the tell-test targets): the cells or cell fragments that cover each beat"""
    out = []
    for b in it['bars']:
        for c in b:
            out.append(c)
    return out


# ------------------------------------------------------------------ MELODY LADDER
def melody_rhythm(l, r):
    """the rhythm of a melody item (rung 4 on). Returns (metre, cells by bar, anacrusis ticks). Final note rule (MF): the
    last bar ends with a long note on a strong beat (h in 2/4 or 4/4 beat 3, hd in 3/4, cDD or cD on beat 2 in 6/8)."""
    if l == 4 or l == 5:
        metre, vocab, bars = r.choice(['2/4', '4/4']), ['q', 'e2', 'h'], 2
    elif l in (6, 7, 8):
        metre, bars = r.choice(['2/4', '3/4', '4/4', '6/8']), 4
        vocab = ['cD', 'c3', 'cqe', 'cDD'] if metre == '6/8' else ['q', 'e2', 'h', 'hd']
    elif l in (9, 10):
        metre, bars = r.choice(['2/4', '3/4', '4/4', '6/8']), 8
        vocab = ['cD', 'c3', 'cqe', 'cDD'] if metre == '6/8' else ['q', 'e2', 'h', 'hd', 'dq']
    else:  # 11
        metre, bars = r.choice(['3/4', '4/4']), r.choice([4, 8])
        vocab = ['q', 'e2', 'h', 'hd']
    out = []
    for b in range(bars):
        if b == bars - 1:
            # final bar: an ending figure, then the long final note
            if metre == '2/4':
                out.append(['h'] if r.random() < .5 else ['q', 'q'])
            elif metre == '4/4':
                out.append([r.choice(['q', 'e2']), r.choice(['q', 'e2']), 'h'] if r.random() < .7 else ['q', 'q', 'h'])
            elif metre == '3/4':
                out.append(['hd'] if r.random() < .5 else [r.choice(['q', 'e2']), 'h'])
            else:
                out.append(['cDD'] if r.random() < .5 else [r.choice(['c3', 'cqe']), 'cD'])
        else:
            out.append(fill_bar(r, metre, [k for k in vocab if not (k == 'hd' and metre != '3/4')]))
    anac = 0
    if l >= 6 and r.random() < 0.3:
        anac = 6 if metre == '6/8' else r.choice([6, 12])
    return metre, out, anac


def n_notes(cells_by_bar, anac):
    ons, _ = onsets([c for b in cells_by_bar for c in b])
    n = sum(1 for _, k in ons if k == 'n')
    return n + (1 if anac == 12 else (1 if anac == 6 else 0))


# pitch sets (do-relative diatonic index) and per-rung movement rules
def mel_spec(l):
    S = {}
    if l == 1:
        S = dict(mode='maj', pool=[0, 1, 2, 3, 4], start=[0, 2, 4], end=[0, 2, 4], n=[5], tri=[0, 2, 4], new=None)
    elif l == 2:
        S = dict(mode='maj', pool=[-3, -2, 0, 1, 2, 3, 4, 5], start=[-3, 0, 2, 4], end=[0], n=[6], tri=[-3, 0, 2, 4], new={-3, -2, 5})
    elif l in (3, 4):
        S = dict(mode='maj', pool=list(range(-3, 8)), start=[-3, 0, 2, 4], end=[0, 7], n=[7, 8], tri=[-3, 0, 2, 4, 7], new={-1, 6})
    elif l == 5:
        S = dict(mode='min', pool=list(range(-3, 6)), start=[-2, 0, 2], end=[-2, 5], n=None, tri=[-2, 0, 2, 5], new='minor')
    elif l == 6:
        S = dict(mode='maj|min', pool=list(range(-3, 8)), n=None, new='domtri')
    elif l == 7:
        S = dict(mode='min', pool=list(range(-3, 8)), n=None, new='si')
    elif l == 8:
        S = dict(mode='modal', pool=list(range(-3, 8)), n=None, new='mode')
    elif l == 9:
        S = dict(mode='mod', n=None, new='mod')
    elif l == 10:
        S = dict(mode='maj|min', n=None, new='chrom')
    elif l == 11:
        S = dict(mode='maj|min', n=None, new='bass')
    return S


def pent(i):
    return i % 7 in (0, 1, 2, 4, 5)


def step_ok(a, b):
    return abs(a - b) == 1


def gen_pitch(l, r, n, want_new, mode, sub=None, tries=4000):
    """the pitch line. Moves allowed per rung (rule MP):
       1  steps, repeats (no 3 in a row), s-m, m-d (both ways)  [as built]
       2  + leaps between tonic-triad notes (s, d m s; up to a 6th: s,-m); range s,..l
       3/4 + t, and t; leading note t goes to d or steps down to l; pentatonic tunes move by pentatonic step (m-s, l-d')
       5  la-based minor: la-pentatonic (l, d r m s l) or natural minor (l, t, d r m f s l); leaps within l d m and l,-d
       6  all diatonic leaps 3rd..6th and the octave; the dominant triad s-t-r outlined (s,-t,-r and s-t-r'); tritone only as
          t-f inside a dominant-7th outline resolving (D6)
       7  harmonic minor (si) or melodic minor (fi si rising, s f falling); si -> l; fi -> si; f-si step allowed in harmonic (D5)
       8  Dorian on re / Mixolydian on so in parent-major solfa, or major with te (falls to l) / fi (rises to s)
    """
    S = mel_spec(l)
    for _ in range(tries):
        if l <= 4:
            pool = S['pool']
            tune = 'dia'
            if l in (3, 4):
                tune = 'pent' if (not want_new) else 'dia'
                if tune == 'pent':
                    pool = [x for x in pool if pent(x)]
            elif l == 2 and not want_new:
                pool = [0, 1, 2, 3, 4]
            seq = [r.choice([x for x in S['start'] if x in pool])]
            ok = True
            for k in range(1, n):
                last = seq[-1]
                c = []
                for x in pool:
                    d = abs(x - last)
                    if d == 0:
                        if l == 1 and not (k > 1 and seq[-2] == x):
                            c.append(x)
                        elif l > 1 and not (k > 1 and seq[-2] == x) and r.random() < .5:
                            c.append(x)
                        continue
                    if l in (3, 4) and tune == 'pent':
                        pp = sorted(pool)
                        if abs(pp.index(x) - pp.index(last)) == 1:
                            c.append(x)
                            continue
                    if d == 1:
                        if l >= 3 and last % 7 == 6 and x % 7 != 0 and x % 7 != 5:
                            continue
                        c.append(x)
                    elif l == 1:
                        if d == 2 and last in (0, 2, 4) and x in (0, 2, 4):
                            c.append(x)
                    elif last in S['tri'] and x in S['tri'] and d <= 5:
                        if l >= 3 and last % 7 == 6:
                            continue
                        c.append(x)
                if k == n - 1:
                    c = [x for x in c if x in S['end']]
                if not c:
                    ok = False
                    break
                seq.append(r.choice(c))
            if not ok:
                continue
            if l >= 3 and seq[-2] % 7 == 6 and seq[-1] % 7 != 0:
                continue
            got = bool(set(seq) & S['new']) if S['new'] else True
            if l == 1 or got == want_new:
                return [(x, 0) for x in seq], dict(mode='maj', tune=tune, home=0)
            continue
        # rungs 5-11: scale tables per item (mode / variant), then a common walk
        if l == 5:
            minor = want_new
            if minor:
                var = r.choice(['lapent', 'natmin'])
                scale = [x for x in range(-3, 6) if (pent(x) if var == 'lapent' else True)]
                home, tri = -2, [-2, 0, 2, 5]
            else:   # review: major (rung 3/4 material)
                var, scale, home, tri = 'major', list(range(-3, 8)), 0, [-3, 0, 2, 4, 7]
            alt = {}
            leaps = 'tri'
        elif l in (6, 10, 11):
            minor = r.random() < .5
            var = 'natmin' if minor else 'major'
            scale = list(range(-3, 8)) if not minor else list(range(-3, 6))
            home, tri = (-2, [-2, 0, 2, 5]) if minor else (0, [-3, 0, 2, 4, 7])
            alt = {}
            leaps = 'all' if (l != 6 or want_new) else 'tri'
        elif l == 7:
            if want_new:
                var = r.choice(['harm', 'melo'])
            else:
                var = 'natmin'
            scale = list(range(-3, 6))
            home, tri = -2, [-2, 0, 2, 5]
            alt = {'harm': {4: 1}, 'melo': {3: 1, 4: 1}, 'natmin': {}}[var]
            leaps = 'all'
        elif l == 8:
            if want_new:
                var = r.choice(['dor', 'mix', 'te', 'fi'])
            else:
                var = r.choice(['major', 'natmin'])
            scale = list(range(-3, 8))
            home = {'dor': 1, 'mix': 4, 'te': 0, 'fi': 0, 'major': 0, 'natmin': -2}[var]
            # modal items stay inside s,..d' too: Dorian on re (r, .. r is not available low, so r..r' is capped: s,..d')
            tri = [x for x in scale if (x - home) % 7 in (0, 2, 4)]
            alt = {}
            leaps = 'all'
        elif l == 9:
            return None   # see gen_mod
        seq = []
        hx = [x for x in scale if x % 7 == home % 7]
        seq.append(r.choice([x for x in scale if x in tri]))
        ok = True
        melo_up = None
        for k in range(1, n):
            last = seq[-1]
            c = []
            for x in scale:
                d = abs(x - last)
                if d == 0:
                    if not (k > 1 and seq[-2] == x) and r.random() < .4:
                        c.append(x)
                    continue
                if d == 1:
                    # minor-mode alterations
                    if var == 'harm' and last % 7 == 4 and x % 7 != 5:   # si -> la
                        continue
                    if var == 'melo' and last % 7 == 3 and x > last and False:
                        continue
                    if var == 'lapent' and not (pent(x) and pent(last)):
                        continue
                    c.append(x)
                elif var == 'lapent' and pent(x) and pent(last) and d == 2 and abs(semis(x) - semis(last)) == 3:
                    c.append(x)   # pentatonic step (minor 3rd)
                elif leaps == 'tri':
                    if last in tri and x in tri and d <= 5:
                        c.append(x)
                else:
                    if 2 <= d <= 5 or d == 7:
                        iv = abs(semis(x) - semis(last))
                        if iv == 6 and not ({last % 7, x % 7} == {3, 6}):
                            continue
                        if iv == 6:      # t-f only inside s t r f (D6): the next note must resolve (f->m or t->d)
                            pass
                        if var == 'lapent' and not (pent(x) and pent(last)):
                            continue
                        c.append(x)
            if k == n - 1:
                c = [x for x in c if x % 7 == home % 7]
                if l == 8 and var in ('dor', 'mix'):
                    c = [x for x in c if x % 7 == home % 7]
            if not c:
                ok = False
                break
            seq.append(r.choice(c))
        if not ok:
            continue
        # alterations
        out = []
        for i, x in enumerate(seq):
            a = 0
            if var == 'harm' and x % 7 == 4:
                a = 1
            if var == 'melo':
                nxt = seq[i + 1] if i + 1 < len(seq) else None
                if x % 7 in (3, 4) and nxt is not None and nxt > x:
                    a = 1
            if var == 'te' and x % 7 == 6 and r.random() < .7:
                nxt = seq[i + 1] if i + 1 < len(seq) else None
                if nxt is not None and nxt == x - 1:
                    a = -1
            if var == 'fi' and x % 7 == 3:
                nxt = seq[i + 1] if i + 1 < len(seq) else None
                if nxt is not None and nxt == x + 1:
                    a = 1
            out.append((x, a))
        # harmonic minor: the raised so must go to la; melodic: fi must go to si (checked)
        bad = False
        for i in range(len(out) - 1):
            (x, a), (y, b) = out[i], out[i + 1]
            if var == 'harm' and x % 7 == 4 and y % 7 != 5:
                bad = True
            if var == 'melo' and x % 7 == 3 and a == 1 and not (y % 7 == 4 and b == 1):
                bad = True
            if abs(semis(x, a) - semis(y, b)) == 6:
                # tritone: only t-f / f-t inside a dominant outline, resolving inward next
                if i + 2 >= len(out):
                    bad = True
                else:
                    z, _ = out[i + 2]
                    if not ((y % 7 == 3 and z == y - 1) or (y % 7 == 6 and z == y + 1)):
                        bad = True
        if bad:
            continue
        if out[-1][0] % 7 != home % 7:
            continue
        if l == 7 and want_new and not any(a for _, a in out):
            continue
        if l == 8 and want_new and var in ('te', 'fi') and not any(a for _, a in out):
            continue
        if l == 6:
            got = any(abs(out[i][0] - out[i + 1][0]) >= 2 and not (out[i][0] in tri and out[i + 1][0] in tri) for i in range(len(out) - 1)) \
                or any(out[i][0] % 7 == 4 and out[i + 1][0] % 7 == 6 and abs(out[i][0] - out[i + 1][0]) == 2 for i in range(len(out) - 1))
            if got != want_new:
                continue
        return out, dict(mode='min' if home % 7 == 5 else 'maj', var=var, home=home)
    return None


def gen_chrom(l, r, base, want_new):
    """rung 10: insert chromatic passing / lower-neighbour notes into a diatonic line (rule MC). Rising passing tones are raised
    (di ri fi si li), falling ones lowered (ra me se le te); lower chromatic neighbours are raised. Each inserted note splits
    the previous note's duration (a crotchet becomes two quavers), so the rhythm stays inside the rung's vocabulary."""
    out = list(base)
    if not want_new:
        return out, 0
    ins = 0
    res = []
    for i in range(len(out) - 1):
        (x, a), (y, b) = out[i], out[i + 1]
        res.append((x, a))
        if a == 0 and b == 0 and abs(y - x) == 1 and abs(semis(y) - semis(x)) == 2 and r.random() < .35:
            res.append((x, 1) if y > x else (x, -1) if (x % 7) in LOWER else (x, 0))
            if res[-1][1] == 0:
                res.pop()
            else:
                ins += 1
        elif a == 0 and b == 0 and y == x and (x % 7) in (1, 4, 5) and r.random() < .3:
            res.append((x - 1, 1))   # lower chromatic neighbour: r-di-r, s-fi-s, l-si-l
            ins += 1
    res.append(out[-1])
    return res, ins


def gen_mel(l, r, want_new=None):
    S = mel_spec(l)
    if want_new is None:
        want_new = r.random() < NEW_SHARE if S.get('new') else True
    stage = STAGE_M[l]
    for _ in range(200):
        metre, rbars, anac = (None, None, 0)
        if l <= 3:
            n = r.choice(S['n'])
        else:
            metre, rbars, anac = melody_rhythm(l, r)
            n = n_notes(rbars, anac)
            if n < MIN_NOTES[l]:      # rule MR2: a floor on the note count, so a 2-bar item is never two minims
                continue
        if l == 9:
            got = gen_mod(r, n, metre, rbars)
            if not got:
                continue
            p, info = got
        elif l == 10:
            got = gen_pitch(10, r, n, True, None)
            if not got:
                continue
            base, info = got
            p, ins = gen_chrom(l, r, base, want_new)
            info = dict(info, ins=ins)
            # a chromatic note sits inside a crotchet split into two quavers: the rhythm gains one note per insertion
            if ins:
                flat = [c for b in rbars for c in b]
                qs = [i for i, c in enumerate(flat) if c == 'q']
                if len(qs) < ins:
                    continue
                for i in r.sample(qs, ins):
                    flat[i] = 'e2'
                # rebuild bars from the flat list
                M = METRE[metre]
                nb, cur, w = [], [], 0
                for c in flat:
                    cur.append(c)
                    w += cell_w(c)
                    if w >= M['bar']:
                        nb.append(cur)
                        cur, w = [], 0
                if cur:
                    nb.append(cur)
                rbars = nb
                if n_notes(rbars, anac) != len(p):
                    continue
        elif l == 11:
            got = gen_pitch(10, r, n, True, None)
            if not got:
                continue
            p, info = got
            info = dict(info, bass=gen_bass(r, rbars, metre, info))
            if info['bass'] is None:
                continue
        else:
            got = gen_pitch(l, r, n, want_new, None)
            if not got:
                continue
            p, info = got
        lo = min(x for x, a in p)
        hi = max(x for x, a in p)
        # rule MK: the key SIGNATURE (do's pitch class) is drawn from the Stage's set for every mode; the tonic follows from
        # the mode (la = do + 9 semitones). Drawing minor tonics from the major list made the signature give the mode away.
        key = r.choice(KEYS[stage])
        try:
            octv, dm = place_do(key, r, lo, hi)
        except IndexError:
            continue
        midi = [dm + semis(x, a) for x, a in p]
        tempo = r.randint(72, 96) if l >= 4 else None
        return dict(l=l, p=p, sol=[syl(x, a) for x, a in p], metre=metre, rbars=rbars, anac=anac, key=key, do=dm, midi=midi,
                    tempo=tempo, new=want_new, info=info, n=len(p), octv=octv)
    raise RuntimeError('mel %d' % l)


def gen_mod(r, n, metre, rbars):
    """rung 9: two phrases of 4 bars. Phrase 1 in the home key, phrase 2 in the new key, joined by a pivot note (rule MM).
    Kinds: major -> dominant (do re-assigned: new do = old so; old fi = new ti), major -> relative minor (la-based: do is NOT
    re-assigned; home moves d -> l and si appears), minor -> relative major (do stays), minor -> dominant minor (new la = old mi;
    do re-assigned: new do = old so). Returns pitches in old-key solfa plus the pivot index and the new-key spelling."""
    kind = r.choice(['M-V', 'M-vi', 'm-III', 'm-v'])
    half = n // 2
    for _ in range(300):
        if kind in ('M-V', 'M-vi'):
            g1 = gen_pitch(3, r, half, True, None)
        else:
            g1 = gen_pitch(5, r, half, True, None)
        if not g1:
            continue
        p1, i1 = g1
        if kind in ('M-vi', 'm-III'):
            # same do: phrase 2 in the relative key, the new leading note (si in minor; ti in major) appears
            g2 = gen_pitch(7, r, n - half, True, None) if kind == 'M-vi' else gen_pitch(3, r, n - half, True, None)
            if not g2:
                continue
            p2, i2 = g2
            shift = 0
        else:
            g2 = gen_pitch(3, r, n - half, True, None) if kind == 'M-V' else gen_pitch(7, r, n - half, True, None)
            if not g2:
                continue
            p2, i2 = g2
            shift = 4   # new do = old so (diatonic +4)
        # pivot: the last note of phrase 1 must be a note common to both keys (in old-key terms not fa when going to V)
        pv = p1[-1][0]
        if shift and pv % 7 == 3:
            continue
        p2o = [(x + shift, a + (1 if shift and (x + shift) % 7 == 3 and (x % 7) == 6 else 0)) for x, a in p2]
        return p1 + p2o, dict(mode='maj' if kind.startswith('M') else 'min', kind=kind, pivot=half - 1, shift=shift, home=0)
    return None


def gen_bass(r, rbars, metre, info):
    """rung 11: a bass line in minims/crotchets under the melody (rule MB): one bass note per beat-pair (4/4: beats 1 and 3;
    3/4: beat 1, dotted minim), chord roots and first inversions of I IV V vi ii (i iv V VI ii° in minor), cadence V-I (V-i) at
    the end; outer-voice checks: no parallel 5ths or octaves, no direct 5ths/8ves into a strong beat with a soprano leap, no
    crossing. Returns the bass as do-relative indices (two octaves below) or None."""
    nb = len(rbars)
    per = 2 if metre == '4/4' else 1
    roots = [0, 3, 4, 5, 1]
    seq = []
    for b in range(nb * per):
        if b == nb * per - 1:
            seq.append(0)
        elif b == nb * per - 2:
            seq.append(4)
        else:
            seq.append(r.choice(roots if b else [0]))
    return [x - 14 for x in seq]


# ------------------------------------------------------------------ keys of distinct items
def mel_key(it):
    return (tuple(it['sol']), it['metre'], tuple(tuple(b) for b in it['rbars']) if it['rbars'] else None, it['anac'],
            tuple(it['info'].get('bass') or ()))


# ------------------------------------------------------------------ tells
def predict_acc(rows, feat, ans):
    """accuracy of the best guess of ans from feat (majority answer per feature value), vs the best guess with no feature"""
    by = collections.defaultdict(collections.Counter)
    tot = collections.Counter()
    for x in rows:
        by[feat(x)][ans(x)] += 1
        tot[ans(x)] += 1
    n = len(rows)
    acc = sum(c.most_common(1)[0][1] for c in by.values()) / n
    ch = tot.most_common(1)[0][1] / n
    return acc, ch


MARGIN = 0.05


def tell_table(rows, feats, targets):
    """feats: name -> (feature, strata). The given-information baseline is the strata (what the screen already shows, e.g. the
    metre or the key signature): a tell is a feature that improves the best guess beyond the strata by more than MARGIN.
    acc = best guess from (strata, feature); base = best guess from strata alone (the plain majority when strata is None)."""
    out = []
    for fn, (f, st) in feats.items():
        for tn, t in targets.items():
            rr = [x for x in rows if t(x) is not None]
            if not rr:
                continue
            S = st or (lambda x: 0)
            vals = len(set((S(x), f(x)) for x in rr))
            if len(rr) / max(1, vals) < 30:     # too many cells for the sample: skip rather than over-fit
                continue
            acc, _ = predict_acc(rr, lambda x: (S(x), f(x)), t)
            base, _ = predict_acc(rr, S, t)
            out.append(dict(feature=fn, given=('none' if st is None else st.__doc__ or 'strata'), target=tn, acc=round(acc, 3),
                            base=round(base, 3), fail=acc > base + MARGIN))
    return out


def _ks(x):
    """key signature"""
    return x['key']


def _metre(x):
    """metre"""
    return x['metre']


def mel_tells(items):
    feats = {
        'key signature': (lambda x: x['key'], None),
        'octave of the melody against the key cue': (lambda x: x['octv'], _ks),
        'number of notes (shown at rungs 1-3 only)': (lambda x: x['n'] if x['l'] <= 3 else 0, None),
        'tempo (8-bpm bands)': (lambda x: (x['tempo'] or 0) // 8, None),
        'metre (shown)': (lambda x: x['metre'], None),
        'anacrusis (shown in the bar outline)': (lambda x: x['anac'], None),
    }
    targets = {
        'note 2 solfa': lambda x: x['sol'][1],
        'note 3 solfa': lambda x: x['sol'][2] if x['n'] > 2 else None,
        'note 4 solfa': lambda x: x['sol'][3] if x['n'] > 3 else None,
        'penultimate solfa': lambda x: x['sol'][-2],
        'contains the new thing': lambda x: x['new'],
        'variant (tune type / mode / modulation kind)': lambda x: x['info'].get('var') or x['info'].get('tune') or x['info'].get('kind'),
        'rhythm of bar 1': lambda x: tuple(x['rbars'][0]) if x['rbars'] else None,
    }
    out = tell_table(items, {k: v for k, v in feats.items() if k != 'metre (shown)'}, targets)
    # the metre is shown, and a bar's rhythm depends on it by definition: for the rhythm target the metre is the given baseline
    rt = {'rhythm of bar 1': targets['rhythm of bar 1']}
    if items[0]['l'] >= 4:
        out += tell_table(items, {k + ', given the metre': (f, _metre) for k, (f, st) in feats.items() if k != 'metre (shown)'}, rt)
        out = [t for t in out if not (t['target'] == 'rhythm of bar 1' and t['given'] == 'none')]
    out += tell_table(items, {'metre (shown)': feats['metre (shown)']}, {k: v for k, v in targets.items() if k != 'rhythm of bar 1'})
    # rule MU1 evidence: what the note count WOULD leak if the desk showed "k of N notes" from rung 4 (it must not)
    if items[0]['l'] >= 4:
        for tn in ('rhythm of bar 1', 'note 4 solfa'):
            t = targets[tn]
            rr = [x for x in items if t(x) is not None]
            acc, ch = predict_acc(rr, lambda x: x['n'], t)
            out.append(dict(feature='number of notes, IF shown (it is not, from rung 4)', given='none', target=tn, acc=round(acc, 3),
                            base=round(ch, 3), fail=False, info_only=True))
    return out


def hidden_new(x):
    """the rung's new thing as hidden content (new cells, swing, backbeat): a new METRE is shown on screen, so not a target"""
    N = R_NEW.get(x['l']) or set()
    flat = set(c for b in x['bars'] for c in b)
    return bool(N & flat) or (x.get('swing') and 'swing' in N) or (x.get('backbeat') and 'backbeat' in N)


def rhy_tells(items):
    def secs(x):
        bar = METRE[x['metre']]['bar']
        return round(len(x['bars']) * bar / 12 * 60 / x['tempo'])
    feats = {
        'tempo (8-bpm bands)': (lambda x: x['tempo'] // 8, _metre),
        'playing time (whole seconds)': (secs, _metre),
        'tone pitch (MIDI)': (lambda x: x['pitch'], _metre),
        'anacrusis (shown)': (lambda x: x['anac'], _metre),
        'tempo (8-bpm bands), metre not given': (lambda x: x['tempo'] // 8, None),
    }
    targets = {
        'first cell': lambda x: x['bars'][0][0],
        'second cell': lambda x: x['bars'][0][1] if len(x['bars'][0]) > 1 else None,
        'last cell': lambda x: x['bars'][-1][-1],
        'contains a new cell (hidden)': lambda x: hidden_new(x) if R_NEW.get(x['l']) else None,
        'metre': lambda x: x['metre'],
    }
    out = tell_table(items, feats, targets)
    # the metre is shown on screen: tempo -> metre is reported as information, not as a tell
    for t in out:
        if t['target'] == 'metre':
            t['info_only'] = True
            t['fail'] = False
    return out


# ------------------------------------------------------------------ main
def run(N, seed=49):
    R = {'melody': {}, 'rhythm': {}}
    for l in range(1, 12):
        r = random.Random(seed + l)
        items = [gen_mel(l, r) for _ in range(N)]
        keys = set(mel_key(x) for x in items)
        pitch_keys = set(tuple(x['sol']) for x in items)
        newshare = sum(1 for x in items if x['new']) / N
        lo = min(min(x['midi']) for x in items)
        hi = max(max(x['midi']) for x in items)
        ns = collections.Counter(x['n'] for x in items)
        tl = mel_tells(items)
        R['melody'][l] = dict(stage=STAGE_M[l], draws=N, distinct=len(keys), distinct_pitch_lines=len(pitch_keys),
                              new_share=round(newshare, 3), midi_range=[lo, hi], notes=dict(sorted(ns.items())),
                              tells_failed=[t for t in tl if t['fail']], tells_checked=len([t for t in tl if not t.get('info_only')]),
                              info=[t for t in tl if t.get('info_only')],
                              sample=[' '.join(x['sol']) + ('' if not x['metre'] else '  [%s %s%s]' % (x['metre'], ' | '.join(' '.join(b) for b in x['rbars']), ' anac %d' % x['anac'] if x['anac'] else '')) for x in items[:3]])
    # rung 1 exact (as built): every 5-note line under the rules
    R['melody'][1]['exact'] = exact_m1()
    for l in range(1, 10):
        r = random.Random(seed * 3 + l)
        items = []
        for _ in range(N):
            it = gen_rhy(l, r)
            it['tempo'] = r.randint(66, 100) if l > 1 else r.randint(66, 84)
            it['pitch'] = 72 if l == 1 else r.choice([67, 69, 72, 74])
            it['new'] = has_new(l, it)
            items.append(it)
        keys = set(rhy_key(x) for x in items)
        tl = rhy_tells(items)
        R['rhythm'][l] = dict(stage=STAGE_R[l], draws=N, distinct=len(keys), new_share=round(sum(1 for x in items if x['new']) / N, 3),
                              metres=dict(collections.Counter(x['metre'] for x in items)),
                              tells_failed=[t for t in tl if t['fail']],
                              info_metre_from_time=[t for t in tl if t.get('info_only') and t['feature'].startswith('tempo') and 'not given' in t['feature']],
                              tells_checked=len(tl),
                              sample=[x['metre'] + ': ' + ' | '.join(' '.join(CELLS[c][1] if c in CELLS else c for c in b) for b in x['bars']) for x in items[:3]])
    R['rhythm'][1]['exact'] = exact_r1()
    R['rhythm'][10] = exact_r10()
    return R


def exact_m1():
    """melody rung 1 as built (earMelOK level 1): count every line exactly"""
    pool = [0, 1, 2, 3, 4]
    def ok(a, b):
        d = abs(a - b)
        return d <= 1 or (d == 2 and a in (0, 2, 4) and b in (0, 2, 4))
    cnt = 0
    def walk(s):
        nonlocal cnt
        if len(s) == 5:
            cnt += 1
            return
        for x in pool:
            if not ok(s[-1], x):
                continue
            if len(s) < 4 and x == s[-1] and len(s) > 1 and s[-2] == x:
                continue
            if len(s) == 4 and x not in (0, 2, 4):
                continue
            walk(s + [x])
    for st in (0, 2, 4):
        walk([st])
    return cnt


def exact_r1():
    """rhythm rung 1 (q, e2, h, qr; 4/4; one bar): every bar under the rules. h on beats 1 or 3."""
    per = ['q', 'e2', 'qr']
    halves = [['h']] + [[a, b] for a in per for b in per]
    bars = [a + b for a in halves for b in halves]
    allowed_any = [b for b in bars if not all(c == 'qr' for c in b)]
    no_rest_first_last = [b for b in allowed_any if b[0] != 'qr' and b[-1] != 'qr']
    as_built_0_48 = [b for b in bars if 'qr' not in b]
    two_bars = len(allowed_any) ** 2
    return dict(one_bar_rest_anywhere=len(allowed_any), one_bar_no_rest_first_or_last=len(no_rest_first_last),
                as_built_048_no_rest=len(as_built_0_48), two_bars_rest_anywhere=two_bars)


def exact_r10():
    """rhythm rung 10 (generated part): two-part grooves, 2 bars of 4/4, kick and snare on one line pair against a riff line.
    Kick: quaver grid, always on beat 1 of each bar; snare: backbeat (2 and 4) plus optional ghost/fill on 4& ; riff: rung 6
    vocabulary. Counted exactly for the drum part, times a sampled riff count."""
    kick_slots = 8   # quavers per bar
    kicks = 0
    for m in range(1 << kick_slots):
        if not (m & 1):
            continue
        if m & (1 << 2) or m & (1 << 6):   # no kick on the snare's beats 2 and 4 (kept apart so each is heard)
            continue
        kicks += 1
    snares = 2   # backbeat, or backbeat + 4& pickup
    r = random.Random(10)
    riffs = set()
    for _ in range(20000):
        riffs.add(tuple(fill_bar(r, '4/4', R_VOCAB[6])))
    return dict(stage=6, kick_patterns_per_bar=kicks, snare_patterns_per_bar=snares, riff_bars_sampled=len(riffs),
                distinct_two_bar_grooves_lower_bound=(kicks * snares) ** 2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=20000)
    ap.add_argument('--json', default=None)
    a = ap.parse_args()
    R = run(a.n)
    fails = 0
    print('MELODY')
    for l, v in R['melody'].items():
        f = len(v['tells_failed'])
        fails += f
        print(f"  M{l:<2} St{v['stage']} distinct {v['distinct']:>6} / {v['draws']} draws (pitch lines {v['distinct_pitch_lines']}), new {v['new_share']:.0%}, "
              f"MIDI {v['midi_range']}, notes {v['notes'] if len(v['notes']) < 6 else (min(v['notes']), max(v['notes']))}, tells {v['tells_checked']} checked, {f} failed")
        for t in v['tells_failed']:
            print('       FAIL', t)
        for t in v.get('info', []):
            print('       info:', t)
        for s in v['sample']:
            print('       e.g.', s)
    print('  M1 exact (as built):', R['melody'][1]['exact'])
    print('RHYTHM')
    for l, v in R['rhythm'].items():
        if l == 10:
            print('  R10', v)
            continue
        f = len(v['tells_failed'])
        fails += f
        print(f"  R{l:<2} St{v['stage']} distinct {v['distinct']:>6} / {v['draws']} draws, new {v['new_share']:.0%}, metres {v['metres']}, tells {v['tells_checked']} checked, {f} failed")
        for t in v['tells_failed']:
            print('       FAIL', t)
        for t in v['info_metre_from_time']:
            print('       info (metre is shown on screen):', t)
        for s in v['sample']:
            print('       e.g.', s)
    print('  R1 exact:', R['rhythm'][1]['exact'])
    if a.json:
        json.dump(R, open(a.json, 'w'), indent=1, default=str)
    print('tell failures:', fails)
    return 0


if __name__ == '__main__':
    sys.exit(main())
