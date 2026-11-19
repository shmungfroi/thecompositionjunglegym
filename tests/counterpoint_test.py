#!/usr/bin/env python3
"""Counterpoint test: charter suite 6, "Species and fugue: the independent counterpoint checker".

Run:  python3 tests/counterpoint_test.py <repo dir>
      (needs playwright + Chrome and music21; tests/run_all installs the offline harness in tests/harness)
Prints a JSON report (counts, the first 25 failures, the regression cases) and exits 1 on any failure.

The app's climb 2 engine (c2Check, c2CantusCheck, c3Check, c3mCheck; solvers c2Solve, c3Solve, c3mSolve; models
C2MODELS, C3MODELS, C3MMODELS) and climb 13 (c13Line, c13Answer, c13Inv, c13Aug, c13TLine and the playback buttons)
are driven in a headless page. Everything is judged by this file's OWN implementation: music21 for interval names
and qualities, and a Python rule checker written from the rule-book texts (C2RB, C3RB, C3MRB; Fux, Gradus ad
Parnassum), never by the app's checker. Where the app's code departs from its own rule book, this file follows the
rule book. Any disagreement fails. The seven defects this suite found in 0.47 (CP-1..CP-6, C13-1) were fixed in 0.48
(item R12); each is now a fixed regression case in section R, and the sweep holds the app to the rule book with no
known-failure allowances.

Size of the 18 Nov 2026 run (about 100 s): 10,980 two-voice counterpoints, 1,845 three-voice first-species and
3,276 mixed-species counterpoints, 4,006 cantus lines, 283,694 interval names (11,025 pairs + 272,669 verticals),
1,812 climb-13 lines (about 21,700 pitches), 1,208 inversions, 604 augmentations, 20 playback checks; 15 regression
checks (section R, 0.48).

Sections:
  A  c2Iv names and classes for every ordered pair of 105 pitches (C2..B6, flat/natural/sharp) against music21
     (11,025 pairs), and the name of every vertical of every checked counterpoint
  B  rhythm layouts of every species (1, 2, 2 with a whole-note penultimate bar, 3, 4 with broken ligatures, 5 with
     florid rhythm plans) for 4-16-bar cantus; c2Plan obeys the florid limits; c2RhFix keeps valid plans
  C  two voices, every mode x species x position: the embedded models, solver outputs (3 seeds; 3 broken-ligature
     sets in species 4; 3 rhythm plans in species 5), solver outputs for 10 random cantus lines (rising and falling
     cadences, finals D E F G A C), 16 random mutations of each, a random walk and (species 5) a random rhythm plan per
     base; every error AND warning compared by (rule code, severity, notes). Models and solver outputs must be
     error-free. The rule-card examples must show their rule (bad version) and not (good version).
  D  the cantus checker, C1-C15, on about 4,000 lines (random cantus-like and random)
  E  three voices, first species (T1-T9, V1-V2, M1-M7): 18 models, solver outputs, 40 mutations each
  F  three voices, mixed species (MX1-MX3, T and V rules, M1, M4, M7; the app's M2, M3 and T3 warnings are not
     compared): the 108 models, solver outputs, 25 mutations each
  R  regression cases for the seven 0.47 defects fixed in 0.48 (R12): CP-1 third-species cambiata (four notes),
     CP-2 florid tied unison (H4), CP-3 cantus C6 after a 5th, CP-4 three-voice M3 (outline, repeated note resets),
     CP-5 mixed-species V2 into the downbeat (and model lydhigh23), CP-6 mixed-species downbeats (S2c/S3d), C13-1
     the minor 7th at the ends of a line
  N  Justin's answers of 19 Nov 2026 (0.48): (8) the H4 card's tag and text (a tied unison in fifth species is a Should)
     and H4 severity over section C (tied florid unison warns, new-note florid unison is an error); (9) S3d into the
     final bar in both checkers (two-voice: the rule book above now has no final-bar exception; fixed cases built from
     the third-species models, two-voice and mixed; counts in both corpora; models unchanged); (10) interval names
     spelled out with the right article in every message of the four checkers over the whole corpus (C, D, E, F and
     the rule cards, pitch names of the exercise removed, then no abbreviation such as P5, d5, A4, M10), and c2IvA for every pair of
     105 pitches against music21's interval name
  G  climb 13: pitches of subjects (the 4 built-in and 600 random, in all 24 keys and the 6 modes), real answers
     (exactly up a 5th; modal: up a 5th within the mode), tonal answers (so in the head answered by do), inversion
     (around the first note, and 1<->5: same rhythm, every step reversed), augmentation (every value doubled), the
     drawn lines (moved by whole octaves, within a tritone of the subject), and the playback buttons (subject,
     inversion, augmentation, diminution = exactly half the subject's onsets and lengths)

Not covered: climb 13's beat-by-beat pair checker (c13Pair) and what uses it (canon, stretto finder,
countersubject, transformation tables), the fugue planner, ladders, score drawing, and whether a counterpoint exists
where the solver finds none (aeo2above has no model; reported as a count).
"""

# =====================================================================================================
#  the independent checker: two voices, cantus, three voices
# =====================================================================================================
from functools import lru_cache
from music21 import pitch as m21pitch, interval as m21interval
import re

LET = 'CDEFGAB'
NAT = [0, 2, 4, 5, 7, 9, 11]


class P:
    __slots__ = ('dn', 'acc', 'li', 'oct', 'midi')

    def __init__(self, dn, acc=0):
        self.dn, self.acc = dn, acc
        self.li, self.oct = dn % 7, dn // 7
        self.midi = 12 * (self.oct + 1) + NAT[self.li] + acc

    def m21(self):
        return LET[self.li] + {1: '#', -1: '-', 0: ''}[self.acc] + str(self.oct)

    def __repr__(self):
        return self.m21()


def parse(s):
    li = LET.index(s[0])
    acc = 1 if '#' in s else (-1 if 'b' in s[1:] else 0)
    octv = int(re.sub(r'[^0-9]', '', s))
    return P(octv * 7 + li, acc)


@lru_cache(maxsize=None)
def _ivname(a, b):
    """music21 interval between two (dn,acc) pitches, lower first (by sounding pitch, then letter)."""
    pa, pb = P(*a), P(*b)
    lo, hi = (pa, pb) if (pa.midi, pa.dn) <= (pb.midi, pb.dn) else (pb, pa)
    iv = m21interval.Interval(noteStart=m21pitch.Pitch(lo.m21()), noteEnd=m21pitch.Pitch(hi.m21()))
    name = iv.name
    gen = iv.generic.undirected
    q = re.match(r'[A-Za-z]+', name).group(0)
    return name, gen, q, abs(iv.semitones)


class Iv:
    __slots__ = ('name', 'gen', 'q', 'g7', 's', 'cls', 'pc')

    def __init__(self, a, b):
        self.name, self.gen, self.q, self.s = _ivname((a.dn, a.acc), (b.dn, b.acc))
        self.g7 = (self.gen - 1) % 7 + 1
        if self.q == 'P' and self.g7 in (1, 5):
            self.cls = 'P'
        elif self.g7 in (3, 6) and self.q in ('M', 'm'):
            self.cls = 'I'
        else:
            self.cls = 'D'
        self.pc = ('8' if self.g7 == 1 else '5') if self.cls == 'P' else None


def iv(a, b):
    return Iv(a, b)


# ---------------- modes, ficta ----------------
def fin_of(cf):
    return parse(cf[-1])


def rise_of(cf):
    return parse(cf[-2]).dn < parse(cf[-1]).dn


def needs_raise(fin):
    """K2: if the final is approached from below by a whole tone, and the step above the final is not a
    semitone (Phrygian), the note below is raised. Computed from the white-note scale."""
    below = fin.midi - P(fin.dn - 1).midi
    above = P(fin.dn + 1).midi - fin.midi
    return below == 2 and above != 1


def cantus(cf, open_=False):
    ps = [parse(s) for s in cf]
    fin = ps[-1]
    if not open_ and rise_of(cf) and needs_raise(fin):
        ps[-2] = P(ps[-2].dn, 1)
    return ps


# ---------------- rhythm layout: positions in eighths (bar = 8) ----------------
RH = {'rh': ['r4', 'h'], 'rh~': ['r4', 'h~'], 'hh': ['h', 'h'], 'hh~': ['h', 'h~'], 'qqqq': ['q'] * 4, 'hqq': ['h', 'q', 'q'],
      'qqh~': ['q', 'q', 'h~'], 'qeeqq': ['q', 'e', 'e', 'q', 'q'], 'qqqee': ['q', 'q', 'q', 'e', 'e'], 'hqee': ['h', 'q', 'e', 'e'], 'w': ['w']}
DUR = {'h': 4, 'q': 2, 'e': 1, 'w': 8}


def layout(sp, n, br=None):
    """attacks: list of dict(bar,pos,dur,tie,brk). sp 25 = second species with a whole note in the bar before the end."""
    br = br or []
    att = []
    if sp == 1:
        att = [dict(bar=b, pos=0, dur=8, tie=False) for b in range(n)]
    elif sp in (2, 25):
        att.append(dict(bar=0, pos=4, dur=4, tie=False))
        for b in range(1, n - 1):
            if sp == 25 and b == n - 2:
                att.append(dict(bar=b, pos=0, dur=8, tie=False))
            else:
                att += [dict(bar=b, pos=0, dur=4, tie=False), dict(bar=b, pos=4, dur=4, tie=False)]
        att.append(dict(bar=n - 1, pos=0, dur=8, tie=False))
    elif sp == 3:
        att += [dict(bar=0, pos=p, dur=2, tie=False) for p in (2, 4, 6)]
        for b in range(1, n - 1):
            att += [dict(bar=b, pos=p, dur=2, tie=False) for p in (0, 2, 4, 6)]
        att.append(dict(bar=n - 1, pos=0, dur=8, tie=False))
    elif sp == 4:
        for b in range(n - 1):
            if b > 0 and b in br:
                att.append(dict(bar=b, pos=0, dur=4, tie=False, brk=True))
            att.append(dict(bar=b, pos=4, dur=4, tie=(b < n - 2 and (b + 1) not in br)))
        att.append(dict(bar=n - 1, pos=0, dur=8, tie=False))
    elif sp == 5:
        for b in range(n):
            pat = RH[br[b]]
            pos = 0
            for j, t in enumerate(pat):
                if t[0] == 'r':
                    pos += int(t[1:]); continue
                d = DUR[t.rstrip('~')]
                tied_in = att and att[-1]['tie'] and j == 0
                if tied_in:
                    pos += d; continue
                att.append(dict(bar=b, pos=pos, dur=d, tie=t.endswith('~') and j == len(pat) - 1))
                pos += d
    return att


def verticals(att, n):
    """one vertical per attack, plus one at each downbeat where a note is tied over (on=False)."""
    V = []
    for i, a in enumerate(att):
        if a['pos'] > 0 and i > 0 and att[i - 1]['tie'] and att[i - 1]['bar'] == a['bar'] - 1:
            V.append(dict(bar=a['bar'], pos=0, a=i - 1, on=False))
        V.append(dict(bar=a['bar'], pos=a['pos'], a=i, on=True))
    return V


# ---------------- the checker ----------------
def check(cf_str, sp, pos, cp_dn, br=None, open_=False):
    """Returns list of (code, sev, tuple(attack indices)). Rules from the app's rule book (C2RB) and Fux."""
    br = br or []
    above = pos == 'above'
    cf = cantus(cf_str, open_)
    n = len(cf)
    fin = fin_of(cf_str)
    rise = rise_of(cf_str)
    att = layout(sp, n, br)
    N = len(att)
    assert len(cp_dn) == N, (len(cp_dn), N)
    raise_ok = needs_raise(fin)
    sub_li = (fin.dn - 1) % 7

    def acc_of(i, d):
        # ficta in the counterpoint: the cadence note, when the counterpoint approaches the final from below
        return 1 if (not open_ and not rise and raise_ok and i == N - 2 and d % 7 == sub_li) else 0

    cp = [P(d, acc_of(i, d)) for i, d in enumerate(cp_dn)]
    out = []

    def add(code, sev, a):
        out.append((code, sev, tuple(a)))

    V = verticals(att, n)
    for v in V:
        v['p'] = cp[v['a']]
        v['c'] = cf[v['bar']]
        v['iv'] = iv(v['p'], v['c'])
    S2 = sp in (2, 25)

    def bad_side(p, c):
        return p.midi < c.midi if above else p.midi > c.midi

    for v in V:
        p, c, I, a = v['p'], v['c'], v['iv'], v['a']
        first = a == 0 and v['on']
        last = a == N - 1 and not open_
        if bad_side(p, c):
            add('H5', 'warn', [a])
        if I.gen > 10:
            add('H6', 'warn', [a])
        if first:
            ok = I.cls == 'P' and (above or I.g7 == 1)
            if not ok:
                add('H2', 'err', [a])
            continue
        if last:
            if not (I.cls == 'P' and I.g7 == 1) or p.li != fin.li:
                add('H3', 'err', [a])
            continue
        diss = I.cls == 'D'
        nxt = cp[a + 1] if a + 1 < N else None
        n2 = cp[a + 2] if a + 2 < N else None
        prv = cp[a - 1] if a >= 1 else None
        if sp == 5:
            t = att[a]
            if not v['on']:
                if diss and nxt is not None:
                    want = p.dn - 1
                    direct = nxt.dn == want
                    deco = (n2 is not None and n2.dn == want and abs(nxt.dn - p.dn) <= 2
                            and iv(nxt, cf[att[a + 1]['bar']]).cls != 'D')
                    if not direct and not deco:
                        add('S4b', 'err', [a, a + 1])
                    else:
                        sus_kind(add, above, I, a)
                elif I.gen == 1:
                    add('H4', 'warn', [a])  # H4: unison on a downbeat (tied); fourth species warns, so does florid (CP-2)
            elif v['pos'] == 0:
                if diss:
                    add('S5a', 'err', [a])
                elif I.gen == 1:
                    add('H4', 'err', [a])
            elif diss and t['dur'] != 1:
                if prv is not None and nxt is not None:
                    d1, d2 = p.dn - prv.dn, nxt.dn - p.dn
                    ok = abs(d1) == 1 and d1 == d2
                    if t['dur'] == 2:
                        ok = ok or (abs(d1) == 1 and d2 == -d1) or cambiata(d1, d2, nxt, n2)
                    if not ok:
                        add('S5b', 'err', [a - 1, a, a + 1])
            if v['on'] and t['dur'] == 1 and prv is not None and nxt is not None:
                if abs(p.dn - prv.dn) != 1 or abs(nxt.dn - p.dn) != 1:
                    add('S5c', 'err', [a - 1, a, a + 1])
            continue
        if sp == 3:
            if v['pos'] == 0:
                if diss:
                    add('S3a', 'err', [a])
                elif I.gen == 1:
                    add('H4', 'err', [a])
            elif diss and prv is not None and nxt is not None:
                d1, d2 = p.dn - prv.dn, nxt.dn - p.dn
                ok = (abs(d1) == 1 and d1 == d2) or (abs(d1) == 1 and d2 == -d1) or cambiata(d1, d2, nxt, n2)
                if not ok:
                    add('S3b', 'err', [a - 1, a, a + 1])
            continue
        strong = sp == 1 or (S2 and v['pos'] == 0) or (sp == 4 and v['on'] and v['pos'] == 0)
        if strong:
            if diss:
                add('H1' if sp == 1 else 'S2a', 'err', [a])
            elif I.gen == 1:
                add('H4', 'warn' if sp == 4 else 'err', [a])
        elif S2 or (sp == 4 and v['on'] and v['bar'] in br):
            if diss and prv is not None and nxt is not None:
                d1, d2 = p.dn - prv.dn, nxt.dn - p.dn
                if not (abs(d1) == 1 and d1 == d2):
                    add('S2b', 'err', [a - 1, a, a + 1])
        elif sp == 4:
            if v['on']:
                if diss:
                    add('S4a', 'err', [a])
                elif I.gen == 1:
                    add('H4', 'warn', [a])
            else:
                if diss:
                    if nxt is not None:
                        if nxt.dn != p.dn - 1:
                            add('S4b', 'err', [a, a + 1])
                        else:
                            sus_kind(add, above, I, a, pair=True)
                elif I.gen == 1:
                    add('H4', 'warn', [a])

    # motion between successive verticals
    pairs = list(zip(V, V[1:]))
    for A, B in pairs:
        dc, dp = B['c'].midi - A['c'].midi, B['p'].midi - A['p'].midi
        if not dc or not dp:
            continue
        same = (dc > 0) == (dp > 0)
        if A['iv'].cls == 'P' and B['iv'].cls == 'P' and A['iv'].pc == B['iv'].pc:
            add('V1' if same else 'V2', 'err', [A['a'], B['a']])
            continue
        if same and B['iv'].cls == 'P' and (B['a'] != N - 1 or open_):
            add('V3', 'err' if sp == 1 else 'warn', [A['a'], B['a']])
        ov = (B['p'].midi < A['c'].midi or B['c'].midi > A['p'].midi) if above else (B['p'].midi > A['c'].midi or B['c'].midi < A['p'].midi)
        if ov:
            add('V4', 'warn', [A['a'], B['a']])

    # S2c: perfect intervals on successive downbeats, weak beat moving a step or a 3rd
    if S2:
        D = [v for v in V if v['pos'] == 0]
        for A, B in zip(D, D[1:]):
            if B['bar'] != A['bar'] + 1:
                continue
            if A['iv'].cls == 'P' and B['iv'].cls == 'P' and A['iv'].pc == B['iv'].pc:
                wi = A['a'] + 1
                if wi < N and att[wi]['bar'] == A['bar']:
                    w = cp[wi]
                    already = any(x[0] in ('V1', 'V2') and x[2][1] == B['a'] for x in out)
                    if abs(w.dn - A['p'].dn) <= 2 and not already:
                        add('S2c', 'err', [A['a'], A['a'] + 1, B['a']])
    # S3d (a Should). The card has no exception for the final bar, so the step into the last downbeat counts too
    # (0.48, Justin 19 Nov: both checkers follow the card; until 0.48 the app's two-voice checker left the final bar out)
    if sp in (3, 5):
        D = [v for v in V if v['pos'] == 0]
        for A, B in zip(D, D[1:]):
            if B['bar'] != A['bar'] + 1:
                continue
            if A['iv'].cls == 'P' and B['iv'].cls == 'P' and A['iv'].pc == B['iv'].pc and A['p'].midi != B['p'].midi:
                add('S3d', 'warn', [A['a'], B['a']])
    # S5e, cadential suspension (fifth species)
    if sp == 5 and not open_:
        same = 1
        first_att = lambda b: [i for i, x in enumerate(att) if x['bar'] == b][:1]
        for b in range(2, n - 1):
            same = same + 1 if br[b] == br[b - 1] else 1
            if same == 3:
                add('S5e', 'warn', first_att(b))
        qq = 0
        for b in range(1, n - 1):
            qq = qq + 1 if br[b] == 'qqqq' else 0
            if qq == 3:
                add('S5e', 'warn', first_att(b))
        if not any(r.endswith('~') for r in br):
            add('S5e', 'warn', [0])
        sv = next((v for v in V if v['bar'] == n - 2 and v['pos'] == 0), None)
        if sv and not rise and not (not sv['on'] and sv['iv'].cls == 'D' and sv['iv'].g7 == (7 if above else 2)):
            add('S4e', 'warn', [sv['a']])
    if sp == 4:
        W = [v for v in V if v['on'] and v['pos'] == 4]
        for A, B in zip(W, W[1:]):
            if B['bar'] != A['bar'] + 1:
                continue
            if A['iv'].cls == 'P' and B['iv'].cls == 'P' and A['iv'].pc == B['iv'].pc and A['p'].midi != B['p'].midi:
                add('S4d', 'err', [A['a'], B['a']])
        for b in br:
            ix = [i for i, x in enumerate(att) if x['bar'] == b and x['pos'] == 0]
            if ix:
                add('S4f', 'warn', ix)
        sv = next((v for v in V if v['bar'] == n - 2 and v['pos'] == 0), None)
        if not open_ and sv:
            want = (4 if above else None) if rise else (7 if above else 2)
            if want and not (sv['iv'].cls == 'D' and sv['iv'].g7 == want):
                add('S4e', 'warn' if rise else 'err', [sv['a']])
        run, lastt = 0, None
        for v in V:
            if v['on']:
                continue
            if v['iv'].cls != 'D':
                run, lastt = 0, None; continue
            nx = cp[v['a'] + 1] if v['a'] + 1 < N else None
            if nx is None or nx.dn != v['p'].dn - 1:
                run, lastt = 0, None; continue
            tag = (v['iv'].g7, iv(nx, cf[v['bar']]).g7)
            run = run + 1 if tag == lastt else 1
            lastt = tag
            if run == 4:
                add('S4g', 'warn', [v['a']])
    if sp == 1:
        run = 1
        for A, B in zip(V, V[1:]):
            dc, dp = B['c'].midi - A['c'].midi, B['p'].midi - A['p'].midi
            if A['iv'].cls == 'I' and A['iv'].g7 == B['iv'].g7 and dc != 0 and (dc > 0) == (dp > 0) and dp != 0:
                run += 1
                if run == 4:
                    add('H7', 'warn', [B['a'] - 3, B['a'] - 2, B['a'] - 1, B['a']])
            else:
                run = 1
    # K1 the modal cadence
    if not open_:
        pen = cp[N - 2]
        v = next(x for x in V if x['on'] and x['a'] == N - 2)
        wantM6 = above != rise
        I = v['iv']
        ok = (I.g7 == 6 and I.q == 'M') if wantM6 else (I.g7 == 3 and I.q == 'm')
        step = (pen.dn - fin.dn) % 7 == (1 if rise else 6)
        if not ok or not step:
            add('K1', 'err', [N - 2])
        elif abs(cp[N - 1].dn - pen.dn) != 1:
            add('K1', 'err', [N - 2, N - 1])
    # melody
    for i in range(1, N):
        a, b = cp[i - 1], cp[i]
        I = iv(a, b)
        up = b.midi > a.midi
        if b.midi == a.midi:
            add('M7', 'err' if sp in (2, 25, 3, 5) else 'warn', [i - 1, i])
            continue
        okmel = I.name in ('m2', 'M2', 'm3', 'M3', 'P4', 'P5', 'P8') or (I.name == 'm6' and up)
        if not okmel:
            add('M1', 'err', [i - 1, i])
            continue
        c = cp[i + 1] if i + 1 < N else None
        if c is not None and I.gen >= 5 and c.midi != b.midi:
            back = (c.midi > b.midi) != up
            if not back:
                add('M2', 'warn', [i - 1, i, i + 1])
            elif I.gen >= 6 and abs(c.dn - b.dn) != 1:
                add('M2', 'warn', [i - 1, i, i + 1])
        if c is not None and c.midi != b.midi:
            I2 = iv(b, c)
            if I.gen >= 3 and I2.gen >= 3 and (c.midi > b.midi) == up:
                o = iv(a, c)
                if (o.cls == 'D' and not (o.g7 == 4 and o.q == 'P')) or o.gen > 8:
                    add('M3', 'warn', [i - 1, i, i + 1])
    ms = [p.midi for p in cp]
    hi, lo = max(ms), min(ms)
    r = iv(cp[ms.index(lo)], cp[ms.index(hi)])
    if r.gen > 10:
        add('M4', 'warn', [ms.index(lo), ms.index(hi)])
    if sp in (1, 4) and ms.count(hi) > 1:
        add('M5', 'warn', [i for i, m in enumerate(ms) if m == hi])
    tp = [0] + [i for i in range(1, N - 1) if (ms[i] - ms[i - 1]) and (ms[i + 1] - ms[i]) and ((ms[i] - ms[i - 1] > 0) != (ms[i + 1] - ms[i] > 0))] + [N - 1]
    for x, y in zip(tp, tp[1:]):
        o = iv(cp[x], cp[y])
        if o.s == 6:
            add('M6', 'warn', [x, y])
    return sorted(out), cp, cf, V


def cambiata(d1, d2, nx, n2):
    """S3c: step down to the dissonance, leap down a 3rd, then step back up (the four-note figure; CP-1)."""
    if not (d1 == -1 and d2 == -2):
        return False
    if n2 is not None and n2.dn - nx.dn != 1:
        return False
    return True


def sus_kind(add, above, I, a, pair=False):
    if above and I.g7 == 2 and I.gen == 2:
        add('S4c', 'err', [a, a + 1])
    elif above and I.g7 == 2:
        add('S4c', 'warn', [a, a + 1] if pair else [a])
    elif not above and I.g7 == 7:
        add('S4c', 'warn', [a, a + 1] if pair else [a])


# ---------------- cantus checker (C1-C15) ----------------
def cantus_check(fin, cfs):
    """Rules C1-C15 from the rule book. C6: 'after a 5th, 6th or octave, turn back by step' (CP-3)."""
    out = []
    add = lambda code, sev, a: out.append((code, sev, tuple(a)))
    P_ = [parse(s) for s in cfs]
    n = len(P_)
    F = parse(fin + '4')
    if not n:
        return out
    if n < 8 or n > 14:
        add('C1', 'warn', [])
    if P_[0].li != F.li:
        add('C2', 'err', [0])
    if n > 1 and P_[-1].li != F.li:
        add('C2', 'err', [n - 1])
    if n > 1 and abs(P_[-1].dn - P_[-2].dn) != 1:
        add('C3', 'err', [n - 2, n - 1])
    leaps = 0
    mv = []
    for i in range(1, n):
        a, b = P_[i - 1], P_[i]
        I = iv(a, b)
        up = b.midi > a.midi
        mv.append(b.dn - a.dn)
        if b.midi == a.midi:
            add('C9', 'err', [i - 1, i]); continue
        if I.gen >= 3:
            leaps += 1
        okmel = I.name in ('m2', 'M2', 'm3', 'M3', 'P4', 'P5', 'P8') or (I.name == 'm6' and up)
        if not okmel:
            add('C5', 'err', [i - 1, i]); continue
        c = P_[i + 1] if i + 1 < n else None
        if c is not None and I.gen >= 5 and c.midi != b.midi:
            same_dir = (c.midi > b.midi) == up
            not_step = abs(c.dn - b.dn) != 1
            if same_dir or not_step:
                add('C6', 'warn', [i - 1, i, i + 1])
        if c is not None and c.midi != b.midi:
            I2 = iv(b, c)
            up2 = c.midi > b.midi
            if I.gen >= 3 and I2.gen >= 3 and up2 == up:
                o = iv(a, c)
                if (o.cls == 'D' and not (o.g7 == 4 and o.q == 'P')) or o.gen > 8:
                    add('C14', 'warn', [i - 1, i, i + 1])
                d = P_[i + 2] if i + 2 < n else None
                if d is not None and iv(c, d).gen >= 3 and (d.midi > c.midi) == up:
                    add('C14', 'warn', [i - 1, i, i + 1, i + 2])
    if n > 3 and leaps > (n - 1) * 0.4:
        add('C4', 'warn', [])
    rn = 1
    for i in range(1, len(mv)):
        if mv[i] and mv[i - 1] and (mv[i] > 0) == (mv[i - 1] > 0):
            rn += 1
            if rn == 5:
                add('C12', 'warn', [i - 3, i + 1])
        else:
            rn = 1
    for k in (2, 3):
        for i in range(0, len(mv) - 2 * k + 1):
            if mv[i:i + k] == mv[i + k:i + 2 * k] and len(set(mv[i:i + k])) > 1:
                add('C13', 'warn', [i, i + 2 * k]); break
    if n > 2:
        ms = [p.midi for p in P_]
        hi, lo = max(ms), min(ms)
        ix = [i for i, m in enumerate(ms) if m == hi]
        if len(ix) > 1:
            add('C7', 'warn', ix)
        elif n >= 6 and (ix[0] < 2 or ix[0] > n - 3):
            add('C15', 'warn', ix)
        if iv(P_[ms.index(lo)], P_[ms.index(hi)]).gen > 10:
            add('C8', 'warn', [])
        tp = [0] + [i for i in range(1, n - 1) if (ms[i] - ms[i - 1]) and (ms[i + 1] - ms[i]) and ((ms[i] - ms[i - 1] > 0) != (ms[i + 1] - ms[i] > 0))] + [n - 1]
        for x, y in zip(tp, tp[1:]):
            if iv(P_[x], P_[y]).s == 6:
                add('C10', 'warn', [x, y])
    return sorted(out)


# ---------------- three voices, first species (T1-T9, V1, V2, M rules) ----------------
CI = {'low': 2, 'mid': 1, 'high': 0}


def c3_check(cf_str, arr, cps):
    """cps: {voice: [dn,...]} for the two counterpoint voices. Voices: 0 top, 1 middle, 2 bottom.
    Returns list of (code, sev, bars tuple, voices tuple)."""
    n = len(cf_str)
    ci = CI[arr]
    cf = cantus(cf_str)
    fin = fin_of(cf_str)
    raise_ok = needs_raise(fin)
    V = [None] * 3
    for v in range(3):
        if v == ci:
            V[v] = cf; continue
        dn = cps[v]
        L = []
        for i, d in enumerate(dn):
            acc = 1 if (raise_ok and i == n - 2 and dn[i + 1] == d + 1 and (d + 1 - fin.dn) % 7 == 0) else 0
            L.append(P(d, acc))
        V[v] = L
    out = []
    add = lambda code, sev, bars, voices: out.append((code, sev, tuple(bars), tuple(voices)))
    pairs = [(0, 1), (0, 2), (1, 2)]

    def bass_of(ch):
        bi = 0
        for k in range(1, 3):
            if ch[k].midi < ch[bi].midi:
                bi = k
        return bi
    for i in range(n):
        ch = [V[v][i] for v in range(3)]
        bi = bass_of(ch)
        for v in range(3):
            if v != bi and iv(ch[bi], ch[v]).cls == 'D':
                add('T1', 'err', [i], [v])
        for a, b in pairs:
            if a == bi or b == bi:
                continue
            I = iv(ch[a], ch[b])
            if I.g7 in (2, 7):
                add('T1', 'err', [i], [a, b])
            elif I.g7 in (4, 5) and I.q != 'P':
                add('T1', 'warn', [i], [a, b])
        if 0 < i < n - 1 and not any(iv(ch[bi], ch[v]).g7 in (3, 6) for v in range(3) if v != bi):
            add('T2', 'warn', [i], [0, 1, 2])
        for a, b in pairs:
            if ch[a].midi == ch[b].midi and 0 < i < n - 1:
                add('T6', 'warn', [i], [a, b])
        for a, b in pairs:
            if ch[a].midi < ch[b].midi:
                add('T4', 'warn', [i], [a, b])
        if ch[0].midi - ch[1].midi > 12:
            add('T5', 'warn', [i], [0, 1])
        if ch[1].midi - ch[2].midi > 19:
            add('T5', 'warn', [i], [1, 2])
    f0 = [V[v][0] for v in range(3)]
    b0 = bass_of(f0)
    for v in range(3):
        if v != b0:
            I = iv(f0[b0], f0[v])
            if not (I.cls == 'P' or I.g7 == 3):
                add('T7', 'err', [0], [v])
    if (f0[b0].dn - fin.dn) % 7 not in (0, 4):
        add('T7', 'warn', [0], [2])
    L = [V[v][n - 1] for v in range(3)]
    bl = bass_of(L)
    if (L[bl].dn - fin.dn) % 7 != 0:
        add('T8', 'err', [n - 1], [bl])
    for v in range(3):
        if v == bl:
            continue
        I = iv(L[bl], L[v])
        if not (I.cls == 'P' or (I.g7 == 3 and I.q == 'M')):
            add('T8', 'err', [n - 1], [v])
    down = up = -1
    for v in range(3):
        a, b = V[v][n - 2], V[v][n - 1]
        if (b.dn - fin.dn) % 7 != 0:
            continue
        if a.dn == b.dn + 1: down = v
        if a.dn == b.dn - 1: up = v
    if down < 0 or up < 0:
        add('T9', 'err', [n - 2, n - 1], [0, 1, 2])
    for i in range(1, n):
        for a, b in pairs:
            p0, q0, p1, q1 = V[a][i - 1], V[b][i - 1], V[a][i], V[b][i]
            i0, i1 = iv(p0, q0), iv(p1, q1)
            ma, mb = p1.midi - p0.midi, q1.midi - q0.midi
            if i0.cls == 'P' and i1.cls == 'P' and i0.pc == i1.pc and (ma or mb):
                if ma and mb:
                    add('V1' if (ma > 0) == (mb > 0) else 'V2', 'err', [i - 1, i], [a, b])
            elif (a, b) == (0, 2) and i1.cls == 'P' and ma and mb and (ma > 0) == (mb > 0) and abs(ma) > 2 and i < n - 1:
                add('T3', 'warn', [i - 1, i], [a, b])
    for v in range(3):
        if v == ci:
            continue
        Ls = V[v]
        prev_leap = None  # (gen, up) of the previous move if it was a leap
        for i in range(1, n):
            a, b = Ls[i - 1], Ls[i]
            I = iv(a, b)
            up = b.midi > a.midi
            if a.midi == b.midi:
                add('M7', 'warn', [i - 1, i], [v])
                prev_leap = None  # a repeated note ends the pair of leaps (CP-4)
                continue
            if not (I.name in ('m2', 'M2', 'm3', 'M3', 'P4', 'P5', 'P8') or (I.name == 'm6' and up)):
                add('M1', 'err', [i - 1, i], [v])
            if I.gen >= 5 and i + 1 < n:
                nx = Ls[i + 1].midi - b.midi
                if not nx or (nx > 0) == (b.midi - a.midi > 0):
                    add('M2', 'warn', [i, i + 1], [v])
            # rule book M3: two leaps the same way must outline a 5th, 6th or octave (not a 7th, a tritone or more than an octave)
            if prev_leap and I.gen >= 3 and prev_leap[1] == up:
                o = iv(Ls[i - 2], b)
                if (o.cls == 'D' and not (o.g7 == 4 and o.q == 'P')) or o.gen > 8:
                    add('M3', 'warn', [i - 2, i], [v])
            prev_leap = (I.gen, up) if I.gen >= 3 else None
        ds = [p.dn for p in Ls]
        if max(ds) - min(ds) > 9:
            add('M4', 'warn', [0, n - 1], [v])
    return sorted(out), V


# ---------------- three voices, mixed species (MX1-MX3, T rules, V1, V2) ----------------
def c3m_check(cf_str, arr, spv, sp, cps):
    """One voice (spv) in species sp (2, 3 or 4) and one in whole notes. Errors only, plus the T2/T4/T6/T5 warnings.
    From the rule book (the app follows it since 0.48, R12):
      - V2: consecutive perfect intervals by contrary motion are checked from the last note of a bar into the
        next downbeat too, not only similar motion (CP-5);
      - between the species voice and another voice, perfect intervals on successive DOWNBEATS follow the
        two-voice rules the MX rule book points to (S2c in second species, S3d (a Should) in third), not V1/V2 (CP-6)."""
    n = len(cf_str)
    ci = CI[arr]
    wv = [v for v in range(3) if v != ci and v != spv][0]
    cf = cantus(cf_str)
    fin = fin_of(cf_str)
    raise_ok = needs_raise(fin)
    att = layout(sp, n, [])
    N = len(att)
    Wd, Sd = cps[wv], cps[spv]
    W = [P(d, 1 if (raise_ok and i == n - 2 and Wd[i + 1] == d + 1 and (d + 1 - fin.dn) % 7 == 0) else 0) for i, d in enumerate(Wd)]
    SP = [P(d, 1 if (raise_ok and att[i]['bar'] == n - 2 and i + 1 < N and Sd[i + 1] == d + 1 and (d + 1 - fin.dn) % 7 == 0 and i == N - 2) else 0)
          for i, d in enumerate(Sd)]
    out = []
    add = lambda code, sev, bars, voices: out.append((code, sev, tuple(bars), tuple(voices)))
    VT = verticals(att, n)

    def at(v, b, vt):
        return cf[b] if v == ci else W[b] if v == wv else (SP[vt['a']] if vt is not None else None)

    def chord(vt):
        return [at(v, vt['bar'], vt) for v in range(3)]

    def bass_i(ch):
        bi = 0
        for k in (1, 2):
            if ch[k].midi < ch[bi].midi:
                bi = k
        return bi

    def isdis(a, b):
        return iv(a, b).cls == 'D'

    def diss_against(ch, v):
        bi = bass_i(ch)
        p = ch[v]
        if v == bi or p.midi == ch[bi].midi:
            return any(isdis(p, ch[o]) for o in range(3) if o != v)
        if isdis(ch[bi], p):
            return True
        return any(iv(ch[o], p).g7 in (2, 7) for o in range(3) if o != v and o != bi)

    for k, vt in enumerate(VT):
        ch = chord(vt)
        b = vt['bar']
        bi = bass_i(ch)
        down = vt['pos'] == 0
        if down or (b == 0 and k == 0):
            for v in (ci, wv):
                if v != bi and isdis(ch[bi], ch[v]) and spv != bi:
                    add('T1', 'err', [b], [v])
            if ci != bi and wv != bi and iv(ch[ci], ch[wv]).g7 in (2, 7):
                add('T1', 'err', [b], [ci, wv])
        if diss_against(ch, spv):
            a = vt['a']
            p = SP[a]
            pr = SP[a - 1] if a >= 1 else None
            nx = SP[a + 1] if a + 1 < N else None
            n2 = SP[a + 2] if a + 2 < N else None
            if down and not vt['on']:
                if not (nx is not None and nx.dn == p.dn - 1):
                    add('MX3', 'err', [b], [spv])
                else:
                    ch2 = [nx if v == spv else at(v, b, None) for v in range(3)]
                    if diss_against(ch2, spv):
                        add('MX3', 'err', [b], [spv])
                    bs = bass_i(ch)
                    if bs != spv and iv(ch[bs], p).g7 == 2:
                        add('MX3', 'warn', [b], [spv])
            elif down:
                add('MX1', 'err', [b], [spv])
            else:
                if sp == 4:
                    add('MX2', 'err', [b], [spv])
                elif pr is not None and nx is not None:
                    d1, d2 = p.dn - pr.dn, nx.dn - p.dn
                    ok = abs(d1) == 1 and d1 == d2
                    if sp == 3:
                        ok = ok or (abs(d1) == 1 and d2 == -d1) or cambiata(d1, d2, nx, n2)
                    if not ok:
                        add('MX2', 'err', [b], [spv])
        if down and 0 < b < n - 1:
            if not any(iv(ch[bi], ch[v]).g7 in (3, 6) for v in range(3) if v != bi):
                add('T2', 'warn', [b], [0, 1, 2])
            for x, y in ((0, 1), (1, 2)):
                if ch[x].midi < ch[y].midi:
                    add('T4', 'warn', [b], [x, y])
            for x, y in ((0, 1), (0, 2), (1, 2)):
                if ch[x].midi == ch[y].midi:
                    add('T6', 'warn', [b], [x, y])
            if ch[0].midi - ch[1].midi > 12:
                add('T5', 'warn', [b], [0, 1])
    # parallels between successive downbeats
    downs = [vt for k, vt in enumerate(VT) if vt['pos'] == 0 or k == 0]
    for A, B in zip(downs, downs[1:]):
        CA, CB = chord(A), chord(B)
        for x, y in ((0, 1), (0, 2), (1, 2)):
            i0, i1 = iv(CA[x], CA[y]), iv(CB[x], CB[y])
            mx, my = CB[x].midi - CA[x].midi, CB[y].midi - CA[y].midi
            if i0.cls == 'P' and i1.cls == 'P' and i0.pc == i1.pc and mx and my:
                code = 'V1' if (mx > 0) == (my > 0) else 'V2'
                if spv in (x, y) and sp in (2, 3) and A['bar'] + 1 == B['bar'] and A['pos'] == 0:
                    # two-voice rules: S2c (second species) / S3d (third species, a Should)
                    if sp == 3:
                        add('S3d', 'warn', [A['bar'], B['bar']], [x, y]); continue
                    wi = A['a'] + 1
                    if abs(SP[wi].dn - SP[A['a']].dn) > 2:
                        continue
                    add('S2c', 'err', [A['bar'], B['bar']], [x, y]); continue
                add(code, 'err', [A['bar'], B['bar']], [x, y])
    # the species voice's last note of a bar into the next downbeat
    for b in range(n - 1):
        last = max(i for i, x in enumerate(att) if x['bar'] == b)
        nxt = next(vt for vt in VT if vt['bar'] == b + 1 and vt['pos'] == 0)
        if nxt['a'] == last:
            continue
        p0, p1 = SP[last], SP[nxt['a']]
        for o in (ci, wv):
            q0, q1 = at(o, b, None), at(o, b + 1, None)
            i0, i1 = iv(p0, q0), iv(p1, q1)
            m1, m2 = p1.midi - p0.midi, q1.midi - q0.midi
            if i0.cls == 'P' and i1.cls == 'P' and i0.pc == i1.pc and m1 and m2:
                if (m1 > 0) == (m2 > 0):
                    add('V1', 'err', [b, b + 1], [spv, o])
                else:
                    add('V2', 'err', [b, b + 1], [spv, o])
    # start, end, cadence
    ch = [SP[0] if v == spv else at(v, 0, None) for v in range(3)]
    bi = bass_i(ch)
    for v in range(3):
        if v != bi:
            I = iv(ch[bi], ch[v])
            if not (I.cls == 'P' or I.g7 == 3):
                add('T7', 'err', [0], [v])
    last = [SP[-1] if v == spv else at(v, n - 1, None) for v in range(3)]
    bi = bass_i(last)
    if (last[bi].dn - fin.dn) % 7:
        add('T8', 'err', [n - 1], [bi])
    for v in range(3):
        if v != bi:
            I = iv(last[bi], last[v])
            if not (I.cls == 'P' or (I.g7 == 3 and I.q == 'M')):
                add('T8', 'err', [n - 1], [v])
    pen = [SP[-2] if v == spv else at(v, n - 2, None) for v in range(3)]
    dn_ = up_ = -1
    for v in range(3):
        a, b = pen[v], last[v]
        if (b.dn - fin.dn) % 7:
            continue
        if a.dn == b.dn + 1: dn_ = v
        if a.dn == b.dn - 1: up_ = v
    if dn_ < 0 or up_ < 0:
        add('T9', 'err', [n - 2, n - 1], [0, 1, 2])
    # melody
    for Lst, v, isSp in ((W, wv, False), (SP, spv, True)):
        for i in range(1, len(Lst)):
            a, b = Lst[i - 1], Lst[i]
            if a.midi == b.midi:
                if isSp and sp != 4:
                    add('M7', 'err', [], [v])
                elif not isSp:
                    add('M7', 'warn', [i - 1, i], [v])
                continue
            I = iv(a, b)
            if not (I.name in ('m2', 'M2', 'm3', 'M3', 'P4', 'P5', 'P8') or (I.name == 'm6' and b.midi > a.midi)):
                add('M1', 'err', [] if isSp else [i - 1, i], [v])
        ds = [p.dn for p in Lst]
        if max(ds) - min(ds) > 9:
            add('M4', 'warn', [], [v])
    return sorted(out)


# =====================================================================================================
#  climb 13 oracle
# =====================================================================================================
from music21 import key as m21key, pitch as m21pitch

KEYN = {'maj': ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'],
        'min': ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']}


def tonal_pitch(k, mode, d, prev, nxt):
    """music21 pitch for scale degree d (0 = tonic, may be negative or > 6) in key k/mode. Minor: natural minor,
    with the 7th raised when the line moves to or from the tonic (the leading note)."""
    tn = KEYN[mode][k].replace('b', '-')
    K = m21key.Key(tn if mode == 'maj' else tn.lower())
    base_midi = (48 if k > 4 else 60) + k
    deg = d % 7
    p = K.pitchFromDegree(deg + 1)
    p = m21pitch.Pitch(p.name)
    # a missing neighbour (first or last note of a line) is not the tonic (C13-1)
    if mode == 'min' and deg == 6 and ((prev is not None and prev % 7 == 0) or (nxt is not None and nxt % 7 == 0)):
        p = p.transpose('A1')
    midi = base_midi + (p.pitchClass - base_midi % 12) % 12 + 12 * (d // 7)
    # find octave giving the right MIDI number for this spelling
    for o in range(0, 9):
        q = m21pitch.Pitch(p.name + str(o))
        if q.midi == midi:
            return q
    raise ValueError((k, mode, d, p.name, midi))


def c13_line(cells, ctx):
    """[(m21 Pitch or None, on)] per cell, like the app's c13Line, computed independently."""
    ds = [c if isinstance(c, int) else None for c in cells]
    out, last = [], None
    for i, c in enumerate(cells):
        if c == 'h':
            out.append((last[0], False) if last else None); continue
        if c is None:
            last = None; out.append(None); continue
        prev = next((x for x in reversed(ds[:i]) if x is not None), None)
        nxt = next((x for x in ds[i + 1:] if x is not None), None)
        if ctx['modal']:
            p = P(ctx['fin_dn'] + c)
            q = m21pitch.Pitch(p.m21())
        else:
            q = tonal_pitch(ctx['k'], ctx['mode'], c, prev, nxt)
        last = (q, True)
        out.append(last)
    return out


def head_len(cells):
    """the opening notes on do or so (the tonic-dominant head that a tonal answer adjusts)"""
    h = 0
    for c in cells:
        if not isinstance(c, int):
            continue
        if c % 7 in (0, 4):
            h += 1
        else:
            break
    return h


def c13_answer(cells, ctx, typ):
    """real: every note up a perfect 5th (modal: up a 5th within the mode, no new accidentals).
    tonal: in the head, so (the co-final) is answered by do (the final): up a 4th instead."""
    L = c13_line(cells, ctx)
    hn = head_len(cells) if typ == 'tonal' else 0
    out, k = [], -1
    for x, c in zip(L, cells):
        if x is None:
            out.append(None); continue
        p, on = x
        if on:
            k += 1
        mut = False
        if typ == 'tonal' and k < hn:
            # find the degree of the k-th attacked note
            nums = [c2 for c2 in cells if isinstance(c2, int)]
            mut = nums[k] % 7 == 4
        if ctx['modal']:
            dn = (p.octave * 7 + 'CDEFGAB'.index(p.step)) + (3 if mut else 4)
            q = m21pitch.Pitch(P(dn).m21())
        else:
            q = p.transpose('P4' if mut else 'P5')
        out.append((q, on, mut))
    return out


# =====================================================================================================
#  the run
# =====================================================================================================
import sys, asyncio, json, collections, random, time, pathlib

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

COUNT = collections.Counter()
FAIL = []
REG = []


def fail(sec, msg):
    FAIL.append(f'{sec}: {msg}')


def judge(sec, app, mine, desc):
    """app and mine: lists of issues. Pass if the app reports exactly what the rule book gives."""
    A, T = collections.Counter(app), collections.Counter(mine)
    if A == T:
        return 'pass'
    fail(sec, f'{desc}: app only {sorted((A - T).elements())[:4]}, rule book only {sorted((T - A).elements())[:4]}')
    return 'fail'


def rand_plan(n, rng):
    """a fifth-species rhythm plan within the app's stated limits: bar 1 starts after a half rest, a bar after a tie
    starts with a half note, the bar before the end does not tie over, the last bar is a whole note."""
    R = [rng.choice(['rh', 'rh~'])]
    for b in range(1, n - 1):
        o = ['hh', 'hh~', 'hqq', 'qqh~', 'qqqq', 'qeeqq', 'qqqee', 'hqee']
        if R[-1].endswith('~'):
            o = [p for p in o if p[0] == 'h']
        if b == n - 2:
            o = [p for p in o if not p.endswith('~')]
        R.append(rng.choice(o))
    return R + ['w']


def rand_cantus(rng):
    f = rng.choice('DEFGAC')
    F = {'D': 4, 'E': 4, 'F': 4, 'G': 3, 'A': 3, 'C': 4}[f] * 7 + LET.index(f)
    n = rng.randint(8, 14)
    d = [F]
    for _ in range(n - 3):
        nx = max(F - 4, min(F + 8, d[-1] + rng.choice([1, 1, 1, -1, -1, -1, 2, -2, 3, -3, 4])))
        d.append(nx + 1 if nx == d[-1] else nx)
    pen = F + 1 if rng.random() < .6 else F - 1   # falling (re-do) or rising (ti-do) into the final
    if d[-1] == pen:
        d[-1] = pen + (2 if pen > F else -2)
    d += [pen, F]
    return [LET[x % 7] + str(x // 7) for x in d]


def rand_subject(rng):
    n = rng.choice([8, 12, 16])
    cells = [rng.choice([0, 0, 4, 2, 7, -3])]
    while len(cells) < n:
        if rng.random() < .25 and cells[-1] != 'h':
            cells.append('h'); continue
        p = next(c for c in reversed(cells) if isinstance(c, int))
        cells.append(max(-3, min(9, p + rng.choice([-1, 1, -1, 1, -2, 2, 3, -3, 4, -4]))))
    return cells


def pk(p):
    return (p.step, int(p.alter), p.octave, p.midi)


def apk(x):
    return (LET[x['li']], x['acc'], x['oct'], x['midi'])


JS_RUN2 = r"""(cases)=>cases.map(c=>{const M=c.k==='own'?{k:'own',cf:c.cf}:c2Mode(c.k);const r=c2Check(M,c.sp,c.pos,c.cp,c.br);
  return{app:r.iss.map(x=>[x.code,x.sev,x.att]),names:r.V.map(v=>v.iv?v.iv.name:null)}})"""

JS_BASE2 = r"""(cfg)=>{const R=c2Rng(cfg.seed),out=[],SPS=[1,2,25,3,4,5];const own=cfg.own.map(cf=>({k:'own',cf}));
 for(const M of C2M.concat(own))for(const sp of SPS)for(const pos of ['above','below']){
   const n=M.cf.length,rows=c2Rows(M,pos);
   const brs=sp===4?[[],[1+Math.floor(R()*(n-3))],[1+Math.floor(R()*(n-3))]]:sp===5?[1,2,3].map(()=>c2Plan(n,1+Math.floor(R()*500))):[[]];
   const seeds=M.k==='own'?1:cfg.seeds;
   for(const br of brs)for(let s=0;s<seeds;s++){const cp=c2Solve(M,sp,pos,1+s*7919+Math.floor(R()*1000),null,sp===2||sp===25?2500:8000,br);if(cp)out.push({src:'solver',k:M.k,cf:M.cf,sp,pos,cp,br,rows})}
   if(M.k!=='own'){const m=c2Model(M,sp,pos);if(m)out.push({src:'model',k:M.k,cf:M.cf,sp,pos,cp:m.cp,br:m.br||[],rows});else out.push({src:'nomodel',k:M.k,sp,pos})}
 }
 return out}"""


async def main():
    t_start = time.time()
    rng = random.Random(20261118)
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#climbs/2')
        await pg.wait_for_timeout(1500)

        # ---------------- A: interval names, every pair of pitches C2..B6 with flats, naturals and sharps ----------------
        pitches = [(dn, acc) for dn in range(14, 49) for acc in (-1, 0, 1)]
        app_iv = await pg.evaluate("(P)=>{const out=[];for(const a of P)for(const b of P){const r=c2Iv(c2Pitch(a[0],a[1]),c2Pitch(b[0],b[1]));out.push(r.name+'|'+r.cls)}return out}", pitches)
        k = 0
        for a in pitches:
            for bb in pitches:
                name, gen, q, s = _ivname(a, bb)
                got_name, got_cls = app_iv[k].split('|'); k += 1
                COUNT['interval names (all pitch pairs)'] += 1
                if q in ('P', 'M', 'm', 'A', 'd'):
                    exp_cls = Iv(P(*a), P(*bb)).cls
                    if got_name != name or got_cls != exp_cls:
                        fail('A', f'c2Iv{P(*a), P(*bb)}: app {got_name}/{got_cls}, music21 {name}/{exp_cls}')
                elif not got_name.startswith('x') or got_cls != 'D':
                    fail('A', f'c2Iv{P(*a), P(*bb)}: music21 {name} (doubly altered), app {got_name}/{got_cls}')

        # ---------------- B: rhythm layouts ----------------
        lay_jobs = []
        for n in range(4, 17):
            for sp in (1, 2, 25, 3):
                lay_jobs.append((sp, n, []))
            for _ in range(4):
                lay_jobs.append((4, n, sorted(rng.sample(range(1, n - 1), rng.randint(0, min(3, n - 2))))))
            for _ in range(6):
                lay_jobs.append((5, n, rand_plan(n, rng)))
        app_lay = await pg.evaluate("(J)=>J.map(([sp,n,br])=>({att:c2Layout(sp,n,br).att.map(a=>[a.bar,a.beat,a.dur,!!a.tie]),fix:sp===5?c2RhFix(br,n):null}))", lay_jobs)
        DURN = {'w': 8, 'h': 4, 'q': 2, '8': 1}
        for (sp, n, br), r in zip(lay_jobs, app_lay):
            COUNT['rhythm layouts'] += 1
            unit = {1: 8, 2: 4, 25: 4, 3: 2, 4: 4, 5: 1}[sp]
            got = [(bar, beat * unit, DURN[d], t) for bar, beat, d, t in r['att']]
            exp = [(a['bar'], a['pos'], a['dur'], bool(a['tie'])) for a in layout(sp, n, br)]
            if got != exp:
                fail('B', f'layout sp{sp} n{n} br{br}: app {got[:6]}..., mine {exp[:6]}...')
            if sp == 5 and r['fix'] != br:
                fail('B', f'c2RhFix changed a valid plan {br} -> {r["fix"]}')
        plans = await pg.evaluate("()=>{const o=[];for(let n=5;n<=16;n++)for(let s=1;s<=20;s++)o.push(c2Plan(n,s));return o}")
        for pl in plans:
            COUNT['c2Plan rhythm plans'] += 1
            n = len(pl)
            ok = pl[0] in ('rh', 'rh~') and pl[-1] == 'w' and not pl[-2].endswith('~') and all(
                not pl[i - 1].endswith('~') or pl[i][0] == 'h' for i in range(1, n))
            if not ok:
                fail('B', f'c2Plan gave an impossible plan {pl}')

        # ---------------- C: two voices, every species ----------------
        own = [rand_cantus(rng) for _ in range(10)]
        base = await pg.evaluate(JS_BASE2, {'seed': 3, 'seeds': 3, 'own': own})
        cases = []
        for c in base:
            if c['src'] == 'nomodel':
                COUNT['missing models (null)'] += 1
                if f"{c['k']}{c['sp']}{c['pos']}" != 'aeo2above':
                    fail('C', f"no model for {c['k']} species {c['sp']} {c['pos']}")
                continue
            cases.append(c)
        COUNT['two-voice models'] = sum(c['src'] == 'model' for c in cases)
        COUNT['two-voice solver outputs'] = sum(c['src'] == 'solver' for c in cases)
        for c in list(cases):
            rw = c['rows']
            for _ in range(16):
                cp = list(c['cp'])
                for _ in range(rng.randint(1, 3)):
                    i = rng.randrange(len(cp))
                    cp[i] = cp[i] + rng.choice([-2, -1, 1, 2]) if rng.random() < .7 else rng.choice(rw)
                cases.append(dict(c, src='mutation', cp=[min(max(x, rw[-1]), rw[0]) for x in cp]))
            cp = [rng.choice(rw)]
            for _ in range(len(c['cp']) - 1):
                cp.append(min(max(cp[-1] + rng.choice([-1, 1, -1, 1, -2, 2, -3, 3, 4, -4, 0]), rw[-1]), rw[0]))
            cases.append(dict(c, src='random walk', cp=cp))
            if c['sp'] == 5:
                n = len(c['cf']); pl = rand_plan(n, rng)
                cases.append(dict(c, src='random plan', br=pl, cp=[rng.choice(rw) for _ in layout(5, n, pl)]))
        res = []
        for i in range(0, len(cases), 500):
            res += await pg.evaluate(JS_RUN2, [{k: c[k] for k in ('k', 'cf', 'sp', 'pos', 'cp', 'br')} for c in cases[i:i + 500]])
        for c, r in zip(cases, res):
            COUNT['two-voice counterpoints checked'] += 1
            COUNT[f"  from {c['src']}"] += 1
            mine, cp, cf, V = check(c['cf'], c['sp'], c['pos'], c['cp'], c['br'])
            names = [v['iv'].name for v in V]
            COUNT['interval names (checker verticals)'] += len(names)
            if names != r['names']:
                fail('C', f"interval names {c['k']} sp{c['sp']} {c['pos']} {c['cp']}: app {r['names']} music21 {names}")
            app = [(a, s, tuple(t)) for a, s, t in r['app']]
            desc = f"{c['src']} {c['k']}{'' if c['k'] != 'own' else ' ' + ' '.join(c['cf'])} sp{c['sp']} {c['pos']} cp={c['cp']} br={c['br']}"
            judge('C', app, mine, desc)
            if c['src'] in ('model', 'solver'):
                e = [x for x in app + mine if x[1] == 'err']
                if e:
                    fail('C', f'{c["src"]} has errors: {desc}: {e}')
        # rule-card examples: the bad version shows its rule, the good one does not
        exs = await pg.evaluate("()=>Object.entries(C2EXAMPLES).map(([k,e])=>({k,msg:e.msg,code:C2CODE[e.rule],sp:e.sp,pos:e.pos,good:e.good,bad:e.bad,open:!!e.open,br:e.br||[],appg:c2Check({k:'ex',cf:e.good.cf,open:e.open},e.sp,e.pos,e.good.cp.map(s=>c2Parse(s.replace('#','')).dn),e.br||[]).iss.map(x=>x.code),appb:c2Check({k:'ex',cf:e.bad.cf,open:e.open},e.sp,e.pos,e.bad.cp.map(s=>c2Parse(s.replace('#','')).dn),e.br||[]).iss.map(x=>x.code)}))")
        for e in exs:
            code = e['code']  # the rule the card illustrates (an 'Allowed' card, e.g. S3c, illustrates the rule it is the exception to)
            if code != e['k'].split('_')[0]:
                COUNT['rule-card examples shown through another rule'] += 1
            COUNT['rule-card examples'] += 1
            g = [x[0] for x in check(e['good']['cf'], e['sp'], e['pos'], [parse(s.replace('#', '')).dn for s in e['good']['cp']], e['br'], open_=e['open'])[0]]
            bd = [x[0] for x in check(e['bad']['cf'], e['sp'], e['pos'], [parse(s.replace('#', '')).dn for s in e['bad']['cp']], e['br'], open_=e['open'])[0]]
            if code in g or code not in bd:
                fail('C', f'rule card {e["k"]}: good example gives {g}, bad gives {bd}')
            # 0.47 FR-3: a "follows the rule" example breaks no Must rule at all. An open fragment may begin on an
            # imperfect consonance (H2 is about the first note of a whole piece), but never on a dissonance.
            ge = [x for x in check(e['good']['cf'], e['sp'], e['pos'], [parse(s.replace('#', '')).dn for s in e['good']['cp']], e['br'], open_=e['open'])[0] if x[1] == 'err']
            first = iv(parse(e['good']['cf'][0]), parse(e['good']['cp'][0].replace('#', '')))
            # every card is an excerpt: the H2 "begin on a perfect consonance" rule is waived when it starts on a consonance
            other = [x[0] for x in ge if not (x[0] == 'H2' and code != 'H2' and first.cls != 'D')]
            COUNT['rule-card good examples with no error (FR-3)'] += 1
            if other:
                fail('C', f'rule card {e["k"]}: the "follows the rule" example breaks {other} (first interval {first.name})')
            # "Breaks it" shows exactly one fault: the card's rule. Its only error (after the same fragment H2 waiver) is
            # the card's rule; for a Should rule (a warning) it has no error at all. Documented companion: H5's crossing
            # makes the V4 overlap warning too (warnings other than the card's are not counted as errors).
            ball = check(e['bad']['cf'], e['sp'], e['pos'], [parse(s.replace('#', '')).dn for s in e['bad']['cp']], e['br'], open_=e['open'])[0]
            bfirst = iv(parse(e['bad']['cf'][0]), parse(e['bad']['cp'][0].replace('#', '')))
            be = [x[0] for x in ball if x[1] == 'err' and not (x[0] == 'H2' and code != 'H2' and bfirst.cls != 'D')]
            must = any(x[0] == code and x[1] == 'err' for x in ball)
            COUNT['rule-card bad examples with exactly their own fault'] += 1
            if (must and be != [code]) or (not must and (be or code not in [x[0] for x in ball])):
                fail('C', f'rule card {e["k"]}: the "breaks it" example gives errors {be} (card rule {code})')
            if bfirst.cls == 'D' and code != 'H2' and not str(e.get('msg', '')).startswith('Bar 1'):
                fail('C', f'rule card {e["k"]}: the "breaks it" example also opens on a dissonance ({bfirst.name})')
            if sorted(g) != sorted(e['appg']) or sorted(bd) != sorted(e['appb']):
                fail('C', f'rule card {e["k"]}: app {e["appg"]}/{e["appb"]} vs mine {g}/{bd}')

        # ---------------- D: the cantus checker ----------------
        cants = []
        for _ in range(4000):
            if rng.random() < .55:
                cants.append(rand_cantus(rng))
            else:
                f = rng.choice('DEFGAC'); F = {'D': 4, 'E': 4, 'F': 4, 'G': 3, 'A': 3, 'C': 4}[f] * 7 + LET.index(f)
                cants.append([LET[d % 7] + str(d // 7) for d in (rng.randint(F - 4, F + 8) for _ in range(rng.randint(2, 16)))])
        cants = [(c[-1][0] if rng.random() < .85 else rng.choice('DEFGAC'), c) for c in cants]
        builtin = await pg.evaluate("C2M.map(M=>[M.fin,M.cf])")
        cants += [tuple(x) for x in builtin]
        app = await pg.evaluate("(L)=>L.map(([f,c])=>c2CantusCheck(f,c).iss.map(x=>[x.code,x.sev,x.att]))", cants)
        for (f, c), a in zip(cants, app):
            COUNT['cantus lines checked'] += 1
            judge('D', [(x, s, tuple(t)) for x, s, t in a], cantus_check(f, c), f'cantus on {f}: {" ".join(c)}')
        for f, c in builtin:
            if any(x[1] == 'err' for x in cantus_check(f, c)):
                fail('D', f'built-in cantus {c} breaks a Must rule: {cantus_check(f, c)}')

        # ---------------- E: three voices, first species ----------------
        t1 = time.time()
        base3 = await pg.evaluate("""(own)=>{const out=[];for(const M of C2M.concat(own.map(cf=>({k:'own',cf}))))for(const arr of ['low','mid','high']){
            const m=M.k!=='own'?C3MODELS[M.k+arr]:null;if(M.k!=='own'){if(m)out.push({src:'model',k:M.k,cf:M.cf,arr,cps:m});else out.push({src:'nomodel',k:M.k,arr})}
            const s=c3Solve(M,arr,M.k==='own'?5:17,M.k==='own'?3000:6000);if(s)out.push({src:'solver',k:M.k,cf:M.cf,arr,cps:s})}return out}""", own[:3])
        COUNT['three-voice solve time (s)'] = round(time.time() - t1)
        cases3 = []
        for c in base3:
            if c['src'] == 'nomodel':
                fail('E', f"no three-voice model for {c['k']} {c['arr']}"); continue
            cases3.append(c)
            for _ in range(40):
                cps = {k: list(v) for k, v in c['cps'].items()}
                for _ in range(rng.randint(1, 3)):
                    v = rng.choice(list(cps)); i = rng.randrange(len(cps[v]))
                    cps[v][i] += rng.choice([-3, -2, -1, 1, 2, 3, 4, -4, 7, -7])
                cases3.append(dict(c, src='mutation', cps=cps))
        app = await pg.evaluate("(L)=>L.map(c=>{const M=c.k==='own'?{k:'own',cf:c.cf}:c2Mode(c.k);return c3Check(M,c.arr,c.cps).iss.map(x=>[x.code,x.sev,x.bars,x.voices])})", cases3)
        for c, a in zip(cases3, app):
            COUNT['three-voice (first species) checked'] += 1
            COUNT[f"  3v from {c['src']}"] += 1
            cps = {int(k): v for k, v in c['cps'].items()}
            A = [(x, s, tuple(bb), tuple(v)) for x, s, bb, v in a]
            desc = f"3v {c['src']} {c['k']} {c['arr']} {c['cps']}"
            mine3 = c3_check(c['cf'], c['arr'], cps)[0]
            judge('E', A, mine3, desc)
            if c['src'] != 'mutation' and any(x[1] == 'err' for x in mine3 + A):
                fail('E', f'{desc} has errors')

        # ---------------- F: three voices, mixed species ----------------
        t1 = time.time()
        basem = await pg.evaluate("""()=>{const out=[];for(const key in C3MMODELS){const k=key.slice(0,3),arr=key.slice(3,-2),spv=+key[key.length-2],sp=+key[key.length-1];
            out.push({src:'model',k,cf:c2Mode(k).cf,arr,spv,sp,cps:C3MMODELS[key]})}
          for(const M of C2M)for(const sp of [2,3,4]){const arr=['low','mid','high'][C2M.indexOf(M)%3],spv=[0,1,2].find(v=>v!==C3ARR[arr].cf);const s=c3mSolve(M,arr,spv,sp,9,2500);if(s)out.push({src:'solver',k:M.k,cf:M.cf,arr,spv,sp,cps:s})}
          return out}""")
        COUNT['mixed-species solve time (s)'] = round(time.time() - t1)
        COUNT['mixed-species models'] = sum(c['src'] == 'model' for c in basem)
        if COUNT['mixed-species models'] != 6 * 3 * 2 * 3:
            fail('F', f"expected 108 mixed-species models (6 modes x 3 arrangements x 2 species voices x 3 species), found {COUNT['mixed-species models']}")
        casesm = []
        for c in basem:
            casesm.append(c)
            for _ in range(25):
                cps = {k: list(v) for k, v in c['cps'].items()}
                for _ in range(rng.randint(1, 2)):
                    v = rng.choice(list(cps)); i = rng.randrange(len(cps[v]))
                    cps[v][i] += rng.choice([-3, -2, -1, 1, 2, 3, 4, -4])
                casesm.append(dict(c, src='mutation', cps=cps))
        # the app's warnings M2, M3 and T3 are not part of this comparison (see the docstring)
        app = await pg.evaluate("(L)=>L.map(c=>c3mCheck(c2Mode(c.k),c.arr,c.spv,c.sp,c.cps).iss.filter(x=>!['M2','M3','T3'].includes(x.code)).map(x=>[x.code,x.sev,x.bars,x.voices]))", casesm)
        appm = app
        for c, a in zip(casesm, app):
            COUNT['three-voice (mixed species) checked'] += 1
            cps = {int(k): v for k, v in c['cps'].items()}
            A = [(x, s, tuple(bb), tuple(v)) for x, s, bb, v in a]
            desc = f"mixed {c['src']} {c['k']}{c['arr']}{c['spv']}{c['sp']} {c['cps']}"
            minem = c3m_check(c['cf'], c['arr'], c['spv'], c['sp'], cps)
            judge('F', A, minem, desc)
            if c['src'] != 'mutation':
                e = [x for x in minem + A if x[1] == 'err']
                if e:
                    fail('F', f'{desc} has errors {e}')

        # ---------------- R: regression cases for the seven defects fixed in 0.48 (R12) ----------------
        # Each case must agree with the rule book (the checker above) AND show the specific behaviour the fix is about.
        def reg(rid, what, ok, detail=''):
            REG.append({'id': rid, 'what': what, 'pass': bool(ok)})
            COUNT['regression cases'] += 1
            if not ok:
                fail('R', f'{rid} {what}: {detail}')

        C2CF = await pg.evaluate("()=>Object.fromEntries(C2M.map(M=>[M.k,M.cf]))")
        two = [
            # CP-1: Dorian, third species above. Attacks 28-31 are D4 C4 A3 B3: step down to the dissonant C, leap down a
            # 3rd, step back up (the four-note cambiata, S3c); the line then falls to A3. 0.47 gave S3b at 29-31.
            ('CP-1', 'four-note cambiata accepted in third species', 'dor', 3, 'above', [],
             [40, 38, 37, 36, 35, 33, 34, 35, 36, 37, 39, 40, 39, 38, 37, 36, 37, 38, 39, 40, 39, 38, 36, 35, 34, 33, 32, 29, 31, 32, 31, 29, 30, 29, 33, 32, 33, 34, 35, 36],
             lambda A: ('S3b', 'err', (29, 30, 31)) not in A),
            # CP-2: Aeolian, florid above (a solver output). The tie into a downbeat makes a unison there (attack 11):
            # H4 warns, as it does for the same tie in fourth species. 0.47 reported nothing.
            ('CP-2', 'tied unison on a florid downbeat warned (H4)', 'aeo', 5, 'above', ['rh~', 'hh~', 'hqee', 'hqq', 'qqh~', 'hh~', 'hqq', 'qqqee', 'qqh~', 'hqee', 'w'],
             [30, 32, 33, 32, 31, 30, 29, 30, 31, 30, 31, 30, 31, 30, 31, 32, 33, 32, 31, 30, 32, 33, 32, 33, 32, 33],
             lambda A: ('H4', 'warn', (11,)) in A),
        ]
        got = await pg.evaluate("(L)=>L.map(c=>c2Check(c2Mode(c[0]),c[1],c[2],c[4],c[3]).iss.map(x=>[x.code,x.sev,x.att]))", [[k, sp, pos, br, cp] for _, _, k, sp, pos, br, cp, _ in two])
        for (rid, what, k, sp, pos, br, cp, cond), g in zip(two, got):
            A = [(a, sv, tuple(t)) for a, sv, t in g]
            mine = check(C2CF[k], sp, pos, cp, br)[0]
            reg(rid, what, cond(A) and judge('R', A, mine, f'{rid} {k} sp{sp} {pos}') == 'pass', f'app {A}')
        # CP-3: cantus on F, ... C4 G4 D4 ...: a 5th up, then a leap back down (a 4th). C6: turn back by step.
        cf3 = ['C4', 'B4', 'A4', 'F4', 'A3', 'C4', 'E4', 'D5', 'C4', 'G4', 'D4', 'F4']
        A = [(a, sv, tuple(t)) for a, sv, t in await pg.evaluate("(c)=>c2CantusCheck('F',c).iss.map(x=>[x.code,x.sev,x.att])", cf3)]
        reg('CP-3', 'cantus C6 warns a leap back after a 5th', ('C6', 'warn', (8, 9, 10)) in A and judge('R', A, cantus_check('F', cf3), 'CP-3') == 'pass', f'app {A}')
        # CP-4: three voices, Dorian, cantus low. (a) the middle voice D4 F4 C5 (bars 9-11: a 3rd then a 5th up, an
        # octave in all: fine, 0.47 warned); (b) B3 D4 F4 (two 3rds up outlining a diminished 5th: warned, 0.47 missed
        # it); (c) A3 D4 D4 A4 (a 4th, a repeated note, a 5th: the repeat ends the pair, 0.47 warned)
        base4 = {'0': [38, 36, 39, 40, 39, 40, 38, 37, 38, 42, 40], '1': [38, 36, 37, 38, 37, 36, 35, 34, 33, 35, 40]}
        c4 = [('octave outline not warned', base4, lambda A: not any(x[0] == 'M3' for x in A)),
              ('tritone outline warned', dict(base4, **{'1': [38, 36, 37, 27, 29, 31, 35, 34, 33, 35, 36]}), lambda A: ('M3', 'warn', (3, 5), (1,)) in A),
              ('a repeated note ends the pair of leaps', dict(base4, **{'1': [38, 36, 37, 26, 29, 29, 33, 34, 33, 35, 36]}), lambda A: not any(x[0] == 'M3' and x[3] == (1,) for x in A))]
        got = await pg.evaluate("(L)=>L.map(c=>c3Check(c2Mode('dor'),'low',c).iss.map(x=>[x.code,x.sev,x.bars,x.voices]))", [x[1] for x in c4])
        for (what, cps, cond), g in zip(c4, got):
            A = [(a, sv, tuple(b_), tuple(v)) for a, sv, b_, v in g]
            mine = c3_check(C2CF['dor'], 'low', {int(k_): v for k_, v in cps.items()})[0]
            reg('CP-4', f'three-voice M3: {what}', cond(A) and judge('R', A, mine, f'CP-4 {what}') == 'pass', f'app {[x for x in A if x[0] == "M3"]}')
        # CP-5 and CP-6: mixed species
        mx = [
            ('CP-5', 'V2 by contrary motion into the downbeat (Phrygian, cantus low, top voice in second species)', 'phr', 'low', 0, 2,
             {'0': [41, 39, 41, 40, 41, 42, 41, 40, 38, 37, 36, 37, 38, 39, 38, 37, 38, 39, 37, 40, 36, 37], '1': [39, 37, 38, 39, 38, 39, 40, 38, 40, 37, 33, 34]},
             lambda A: ('V2', 'err', (9, 10), (0, 1)) in A),
            ('CP-5', 'the 0.47 model lydhigh23 shows its V2 (unison to octave, bars 1-2)', 'lyd', 'high', 2, 3,
             {'1': [24, 28, 30, 29, 30, 28, 29, 30, 28, 29, 28], '2': [22, 23, 24, 21, 20, 19, 20, 21, 20, 21, 23, 25, 24, 23, 22, 21, 22, 21, 20, 21, 22, 23, 22, 20, 21, 20, 22, 19, 20, 21, 22, 21, 22, 23, 22, 20, 21, 22, 23, 24]},
             lambda A: ('V2', 'err', (0, 1), (2, 1)) in A),
            ('CP-6', 'second species: octaves on successive downbeats with a small weak-beat move are S2c, not V1/V2', 'phr', 'low', 0, 2,
             {'0': [41, 39, 41, 40, 41, 42, 41, 40, 38, 37, 36, 37, 38, 39, 38, 37, 38, 43, 37, 40, 36, 37], '1': [39, 37, 38, 39, 38, 39, 40, 39, 40, 39, 36, 34]},
             lambda A: ('S2c', 'err', (8, 9), (0, 2)) in A and not any(x[0] in ('V1', 'V2') and x[2:] == ((8, 9), (0, 2)) for x in A)),
            ('CP-6', 'third species: perfect intervals on successive downbeats are S3d (a Should), not V1', 'phr', 'low', 0, 3,
             {'0': [41, 42, 41, 39, 40, 39, 38, 36, 37, 38, 37, 35, 36, 37, 38, 37, 38, 37, 40, 41, 42, 43, 42, 40, 41, 40, 39, 41, 42, 41, 40, 38, 39, 38, 37, 39, 40, 39, 38, 36, 37, 38, 36, 37], '1': [39, 37, 38, 39, 40, 37, 36, 36, 35, 34, 33, 34]},
             lambda A: ('S3d', 'warn', (5, 6), (0, 1)) in A and not any(x[0] in ('V1', 'V2') and x[2:] == ((5, 6), (0, 1)) for x in A)),
        ]
        got = await pg.evaluate("(L)=>L.map(c=>c3mCheck(c2Mode(c[0]),c[1],c[2],c[3],c[4]).iss.filter(x=>!['M2','M3','T3'].includes(x.code)).map(x=>[x.code,x.sev,x.bars,x.voices]))", [[k, arr, spv, sp, cps] for _, _, k, arr, spv, sp, cps, _ in mx])
        for (rid, what, k, arr, spv, sp, cps, cond), g in zip(mx, got):
            A = [(a, sv, tuple(b_), tuple(v)) for a, sv, b_, v in g]
            mine = c3m_check(C2CF[k], arr, spv, sp, {int(k_): v for k_, v in cps.items()})
            reg(rid, what, cond(A) and judge('R', A, mine, f'{rid} {what}') == 'pass', f'app {A}')
        nm = await pg.evaluate("()=>{const m=C3MMODELS.lydhigh23;return{m,iss:c3mCheck(c2Mode('lyd'),'high',2,3,m).iss.map(x=>[x.code,x.sev,x.bars,x.voices])}}")
        e = [x for x in nm['iss'] if x[1] == 'err'] + [x for x in c3m_check(C2CF['lyd'], 'high', 2, 3, {int(k_): v for k_, v in nm['m'].items()}) if x[1] == 'err']
        reg('CP-5', 'the replacement model lydhigh23 has no errors and the bass begins on the final', not e and nm['m']['2'][0] % 7 == 3, f'errors {e}, first bass note dn {nm["m"]["2"][0]}')
        # C13-1: minor 7th at the ends of a line (no neighbour there is not the tonic); the leading note is still raised
        c13 = [('A minor C B G: the last note G stays natural', [2, 1, -1], 9, 2, (4, 0)),
               ('A minor G E A: the first note G stays natural', [-1, -3, 0], 9, 0, (4, 0)),
               ('C sharp minor, the B at the end of the line stays natural', [7, 'h', 4, 1, 'h', 2, 6, 'h'], 1, 6, (6, 0)),
               ('A minor A G A: the leading note is raised (G sharp)', [0, -1, 0], 9, 1, (4, 1))]
        got = await pg.evaluate("(L)=>L.map(([c,k,i])=>{const p=c13Line(c,{modal:false,key:{k,mode:'min'}})[i];return[p.li,p.acc]})", [[c, k, i] for _, c, k, i, _ in c13])
        for (what, cells, k, i, want), g in zip(c13, got):
            exp = c13_line(cells, {'modal': False, 'k': k, 'mode': 'min'})[i][0]
            reg('C13-1', what, tuple(g) == want and (LET.index(exp.step), int(exp.alter)) == want, f'app (li, acc) {g}, music21 {exp}')

        # ---------------- N: Justin's answers of 19 Nov 2026 (0.48, items 8, 9 and 10) ----------------
        # 8. H4: a tied unison in fifth species stays a warning; the card's tag and wording say so.
        h4 = await pg.evaluate("()=>{const r=C2RB.find(x=>x[0]==='H4');return{tag:r[2],text:r[5],sp:r[3]}}")
        reg('N-8', 'H4 card tag: Must for new notes (species 1-3, 5), Should for species 4 and tied notes in 5',
            h4['tag'] == 'Must 1–3, 5 (new notes) · Should 4, 5 (tied notes)', f"tag {h4['tag']!r}")
        reg('N-8', 'H4 card text: in fifth species a tied note may make a unison on the downbeat, used sparingly',
            'fifth species a tied note may make a unison on the downbeat' in h4['text'] and 'sparingly' in h4['text']
            and 'new note on a downbeat in second, third or fifth species' in h4['text'], h4['text'])
        h4n = collections.Counter()
        for c, r in zip(cases, res):
            if c['sp'] not in (4, 5):
                continue
            hs = [(sv, tuple(t)) for code_, sv, t in r['app'] if code_ == 'H4']
            if not hs:
                continue
            V5 = check(c['cf'], c['sp'], c['pos'], c['cp'], c['br'])[3]
            for sv, t in hs:
                tied = any(v['a'] == t[0] and not v['on'] and v['pos'] == 0 and v['iv'].gen == 1 for v in V5)
                kind = f"sp{c['sp']} {'tied' if tied else 'new'} {sv}"
                h4n[kind] += 1
                COUNT[f'H4 messages, {kind}'] += 1
                if (c['sp'] == 4 and sv != 'warn') or (c['sp'] == 5 and sv != ('warn' if tied else 'err')):
                    fail('N', f"H4 {kind}: {c['k']} sp{c['sp']} {c['pos']} cp={c['cp']} br={c['br']}")
        reg('N-8', 'H4 severity over section C: every tied unison on a florid downbeat warns, every new-note one is an error',
            h4n['sp5 tied warn'] > 0 and h4n['sp5 new err'] > 0 and not h4n['sp5 tied err'] and not h4n['sp5 new warn'], dict(h4n))
        # 9. S3d into the final bar: both checkers follow the card (no final-bar exception); the two-voice one warns.
        s3n = {'two': 0, 'mixed': 0}
        for c, r in zip(cases, res):
            N_ = len(c['cp'])
            for code_, sv, t in r['app']:
                if code_ == 'S3d' and t[-1] == N_ - 1:
                    s3n['two'] += 1
                    if c['src'] == 'model':
                        COUNT['two-voice models with S3d into the final bar (models were not changed)'] += 1
                    if sv != 'warn':
                        fail('N', f"S3d into the final bar is not a warning: {c['k']} sp{c['sp']} {c['pos']} cp={c['cp']}")
        COUNT['S3d into the final bar, two voices (section C)'] = s3n['two']
        got = await pg.evaluate("""()=>{const out=[];for(const M of C2M)for(const pos of ['above','below']){const m=c2Model(M,3,pos);if(!m)continue;const L=c2Layout(3,M.cf.length,[]),N=L.att.length,
            i=L.att.findIndex(a=>a.bar===M.cf.length-2&&a.beat===0),before=c2Check(M,3,pos,m.cp,[]).iss.filter(x=>x.code==='S3d'&&x.att[1]===N-1).length;
            for(const d of c2Rows(M,pos)){const cp=m.cp.slice();cp[i]=d;const iss=c2Check(M,3,pos,cp,[]).iss;
              if(iss.some(x=>x.code==='S3d'&&x.att[0]===i&&x.att[1]===N-1)&&!iss.some(x=>x.sev==='err')){out.push({k:M.k,pos,cp,i,N,before,iss:iss.map(x=>[x.code,x.sev,x.att])});break}}}return out}""")
        for g in got:
            COUNT['S3d final-bar regression cases (two voices, third species)'] += 1
            A = [(a, sv, tuple(t)) for a, sv, t in g['iss']]
            mine = check(C2CF[g['k']], 3, g['pos'], g['cp'], [])[0]
            if g['before']:
                fail('N', f"model {g['k']}3{g['pos']} already has S3d into the final bar (models were not to change)")
            reg('N-9', f"two voices: S3d warns into the final bar ({g['k']} {g['pos']}, attacks {g['i']} and {g['N'] - 1})",
                ('S3d', 'warn', (g['i'], g['N'] - 1)) in A and judge('N', A, mine, f"N-9 {g['k']}3{g['pos']}") == 'pass', f'app {A}')
        reg('N-9', 'two voices: final-bar S3d cases built from at least 4 of the 12 third-species models (ion, lyd above and below)', len(got) >= 4, f'{len(got)} found')
        got = await pg.evaluate("""()=>{const out=[];for(const key in C3MMODELS){if(key[key.length-1]!=='3')continue;const k=key.slice(0,3),arr=key.slice(3,-2),spv=+key[key.length-2],M=c2Mode(k),n=M.cf.length,m=C3MMODELS[key];
            const L=c2Layout(3,n,[]),i=L.att.findIndex(a=>a.bar===n-2&&a.beat===0);
            for(const d of c3Rows(M,arr,spv)){const cps={...m,[spv]:m[spv].slice()};cps[spv][i]=d;const iss=c3mCheck(M,arr,spv,3,cps).iss;
              if(iss.some(x=>x.code==='S3d'&&x.bars[0]===n-2&&x.bars[1]===n-1)&&!iss.some(x=>x.sev==='err')){out.push({key,k,arr,spv,cps,n,iss:iss.filter(x=>!['M2','M3','T3'].includes(x.code)).map(x=>[x.code,x.sev,x.bars,x.voices])});break}}}return out}""")
        for g in got[:12]:
            A = [(a, sv, tuple(b_), tuple(v)) for a, sv, b_, v in g['iss']]
            mine = c3m_check(C2CF[g['k']], g['arr'], g['spv'], 3, {int(k_): v for k_, v in g['cps'].items()})
            reg('N-9', f"mixed species: S3d warns into the final bar ({g['key']})",
                any(x[0] == 'S3d' and x[1] == 'warn' and x[2] == (g['n'] - 2, g['n'] - 1) for x in A) and judge('N', A, mine, f"N-9 {g['key']}") == 'pass', f'app {A}')
        COUNT['S3d final-bar cases found (mixed third species models)'] = len(got)
        reg('N-9', 'mixed species: final-bar S3d cases built from at least 2 third-species models', len(got) >= 2, f'{len(got)} found')
        # and in the section F corpus (models, solver outputs, mutations): S3d into the final bar, all agreeing with the rule book above
        s3m = 0
        for c, a in zip(casesm, appm):
            n_ = len(c['cf'])
            for code_, sv, bb, vv in a:
                if code_ == 'S3d' and bb[-1] == n_ - 1:
                    s3m += 1
                    if sv != 'warn':
                        fail('N', f"mixed S3d into the final bar is not a warning: {c['k']}{c['arr']}{c['spv']}{c['sp']}")
        COUNT['S3d into the final bar, mixed species (section F)'] = s3m
        reg('N-9', 'S3d into the final bar is reported (as a warning) in both corpora', s3n['two'] > 0 and s3m > 0, f"two voices {s3n['two']}, mixed {s3m}")
        # 10. interval names spelled out in every message of the four checkers, over the whole corpus above
        await pg.evaluate("""()=>{window.__cpStrip=(m,ps)=>{let s=m;[...new Set(ps.filter(Boolean).flatMap(p=>[p.txt,c2Pitch(p.dn-1).txt,c2Pitch(p.dn+1).txt]))].sort((a,b)=>b.length-a.length).forEach(t=>{s=s.split(t).join('♪')});return s}}""")
        msgs = []
        for i in range(0, len(cases), 500):
            msgs += await pg.evaluate("(L)=>L.flatMap(c=>{const M=c.k==='own'?{k:'own',cf:c.cf}:c2Mode(c.k);const r=c2Check(M,c.sp,c.pos,c.cp,c.br);return r.iss.map(x=>['two-voice',x.msg,__cpStrip(x.msg,r.cp.concat(r.cf))])})",
                                      [{k: c[k] for k in ('k', 'cf', 'sp', 'pos', 'cp', 'br')} for c in cases[i:i + 500]])
        msgs += await pg.evaluate("(L)=>L.flatMap(([f,c])=>{const r=c2CantusCheck(f,c);return r.iss.map(x=>['cantus',x.msg,__cpStrip(x.msg,r.P)])})", cants)
        msgs += await pg.evaluate("(L)=>L.flatMap(c=>{const M=c.k==='own'?{k:'own',cf:c.cf}:c2Mode(c.k);const r=c3Check(M,c.arr,c.cps);return r.iss.map(x=>['three-voice',x.msg,__cpStrip(x.msg,r.V.flat())])})", cases3)
        msgs += await pg.evaluate("(L)=>L.flatMap(c=>{const r=c3mCheck(c2Mode(c.k),c.arr,c.spv,c.sp,c.cps);return r.iss.map(x=>['mixed',x.msg,__cpStrip(x.msg,r.cf.concat(r.W,r.SP))])})", casesm)
        msgs += await pg.evaluate("""()=>Object.values(C2EXAMPLES).flatMap(e=>{const ps=['good','bad'].flatMap(s=>e[s].cf.concat(e[s].cp)).map(c2Parse);
            const run=s=>c2Check({k:'ex',cf:e[s].cf,open:e.open},e.sp,e.pos,e[s].cp.map(x=>c2Parse(x.replace('#','')).dn),e.br||[]).iss.map(x=>['rule card',x.msg,__cpStrip(x.msg,ps)]);
            return[['rule card (shown)',anA(e.msg),__cpStrip(anA(e.msg),ps)]].concat(run('good'),run('bad'))})""")
        ABBR = re.compile(r'\b[dAPMm]\d+\b')                                  # P5, M6, m3, d5, A4, P12 ... (pitch names removed first)
        ABBR_RAW = re.compile(r'\b(?:a|an|dissonant)\s+[dAPMm]\d+\b')          # an abbreviation after an article (pitch names never are)
        WRONG_A = re.compile(r'\ba\s+(?:augmented|octave|11th|18th)\b')
        WRONG_AN = re.compile(r'\ban\s+(?:perfect|major|minor|diminished|doubly|unison|double|[2-79]|1[02-7])')
        bad_m = collections.Counter()
        for src, raw, stripped in msgs:
            COUNT['checker messages read for interval names'] += 1
            COUNT[f'  messages from {src}'] += 1
            for what, rx, txt in (('abbreviated interval', ABBR, stripped), ('abbreviated interval after an article', ABBR_RAW, raw),
                                  ("'a' before a vowel sound", WRONG_A, raw), ("'an' before a consonant sound", WRONG_AN, raw)):
                if rx.search(txt):
                    bad_m[what] += 1
                    if bad_m[what] <= 3:
                        fail('N', f'{what} in a {src} message: {raw}')
        COUNT['distinct checker messages'] = len({m[1] for m in msgs})
        reg('N-10', f'interval names spelled out, articles right, in all {len(msgs)} checker messages of the corpus', not bad_m and len(msgs) > 50000, dict(bad_m))
        # the spelled-out name of every ordered pair of section A's 105 pitches, against music21's own interval name
        app_nm = await pg.evaluate("(P)=>{const out=[];for(const a of P)for(const b of P)out.push(typeof c2IvA==='function'?c2IvA(c2Iv(c2Pitch(a[0],a[1]),c2Pitch(b[0],b[1]))):'(no c2IvA)');return out}", pitches)
        ORD = lambda n: f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
        k = 0; bad_n = 0
        for a in pitches:
            for bb in pitches:
                pa, pb = P(*a), P(*bb)
                lo, hi = (pa, pb) if (pa.midi, pa.dn) <= (pb.midi, pb.dn) else (pb, pa)
                m = m21interval.Interval(noteStart=m21pitch.Pitch(lo.m21()), noteEnd=m21pitch.Pitch(hi.m21()))
                g = m.generic.undirected
                ql = m.niceName.rsplit(' ', 1)[0].lower()
                ql = 'doubly altered' if ql.startswith(('doubly', 'triply')) else ql
                base = {1: 'unison', 8: 'octave', 15: 'double octave'}.get(g, ORD(g))
                want = base if (ql == 'perfect' and g in (1, 8, 15)) else f'{ql} {base}'
                want = ('an ' if re.match(r'(augmented|octave)', want) else 'a ') + want
                COUNT['spelled-out interval names (all pitch pairs) vs music21'] += 1
                if app_nm[k] != want:
                    bad_n += 1
                    if bad_n <= 3:
                        fail('N', f'c2IvA{pa, pb}: app {app_nm[k]!r}, music21 {want!r} ({m.niceName})')
                k += 1
        reg('N-10', 'the spelled-out name and article of every pair of 105 pitches match music21', not bad_n, f'{bad_n} differ')

        # ---------------- G: climb 13 - subjects, answers, inversion, augmentation, diminution ----------------
        subs = await pg.evaluate("()=>{const o=[];for(const sys in C13SUB)for(const k in C13SUB[sys]){const s=C13SUB[sys][k];o.push({sys,id:k,cells:s.cells,key:s.key||null,mk:s.mk||null})}return o}")
        jobs = []
        for s in subs:
            jobs.append((s['cells'], {'modal': False, 'k': s['key']['k'], 'mode': s['key']['mode']} if s['sys'] == 'tonal' else {'modal': True, 'mk': s['mk']}))
        for _ in range(600):
            ctx = ({'modal': False, 'k': rng.randrange(12), 'mode': rng.choice(['maj', 'min'])} if rng.random() < .7
                   else {'modal': True, 'mk': rng.choice(['dor', 'aeo', 'ion', 'mix', 'phr', 'lyd'])})
            jobs.append((rand_subject(rng), ctx))
        res = await pg.evaluate("""(jobs)=>jobs.map(([cells,c])=>{const ctx=c.modal?{modal:true,M:c2Mode(c.mk),fin:c2Fin(c2Mode(c.mk))}:{modal:false,key:{k:c.k,mode:c.mode}};
          const P=L=>L.map(p=>p?{li:p.li,acc:p.acc,oct:p.oct,midi:p.midi,on:p.on,mut:!!p.mut}:null);
          const o={fin:ctx.modal?ctx.fin.dn:null,line:P(c13Line(cells,ctx)),real:P(c13Answer(cells,ctx,'real')),tonal:P(c13Answer(cells,ctx,'tonal')),inv1:c13Inv(cells,'first'),inv15:c13Inv(cells,'15'),aug:c13Aug(cells)};
          C13.tr.axis='first';o.tinv1=P(c13TLine('inv',cells,ctx));C13.tr.axis='15';o.tinv15=P(c13TLine('inv',cells,ctx));o.taug=P(c13TLine('aug',cells,ctx));
          o.linv1=P(c13Line(o.inv1,ctx));o.linv15=P(c13Line(o.inv15,ctx));o.laug=P(c13Line(o.aug,ctx));return o})""", [[c, x] for c, x in jobs])

        def cmp_line(mine, got, with_mut=False):
            if len(mine) != len(got):
                return f'length {len(got)} vs {len(mine)}'
            for i, (m, a) in enumerate(zip(mine, got)):
                if (m is None) != (a is None):
                    return f'cell {i}: app {a} mine {m}'
                if m and (pk(m[0]) != apk(a) or m[1] != a['on'] or (with_mut and m[2] != a['mut'])):
                    return f'cell {i}: app {apk(a)} on={a["on"]} mut={a["mut"]}, expected {pk(m[0])} on={m[1]}' + (f' mut={m[2]}' if with_mut else '')
            return None

        for (cells, ctx), r in zip(jobs, res):
            if ctx['modal']:
                ctx = dict(ctx, fin_dn=r['fin'])
            where = f"{'modal ' + ctx['mk'] if ctx['modal'] else KEYN[ctx['mode']][ctx['k']] + ' ' + ctx['mode']} {cells}"
            # pitches of the subject, then the real and tonal answers
            for nm, fn, mut in (('subject', lambda: c13_line(cells, ctx), False),
                                ('real answer', lambda: c13_answer(cells, ctx, 'real'), True),
                                ('tonal answer', lambda: c13_answer(cells, ctx, 'tonal'), True)):
                COUNT['climb 13 lines (subject/answers)'] += 1
                COUNT['climb 13 pitches'] += sum(1 for x in cells if x is not None)
                got = r[{'subject': 'line', 'real answer': 'real', 'tonal answer': 'tonal'}[nm]]
                e = cmp_line(fn(), got, mut)
                if e:
                    fail('G', f'{nm} {where}: {e}')
            # inversion: the same rhythm, every diatonic step reversed; around the first note, or 1 <-> 5
            nums = [c for c in cells if isinstance(c, int)]
            for ax, inv in (('first', r['inv1']), ('15', r['inv15'])):
                COUNT['climb 13 inversions'] += 1
                inums = [c for c in inv if isinstance(c, int)]
                if [isinstance(c, int) for c in inv] != [isinstance(c, int) for c in cells] or [c for c in inv if not isinstance(c, int)] != [c for c in cells if not isinstance(c, int)]:
                    fail('G', f'inversion ({ax}) changed the rhythm: {where} -> {inv}')
                if [y - x for x, y in zip(inums, inums[1:])] != [x - y for x, y in zip(nums, nums[1:])]:
                    fail('G', f'inversion ({ax}) does not reverse every step: {where} -> {inv}')
                if ax == 'first' and inums[0] != nums[0]:
                    fail('G', f'inversion around the first note moved the first note: {where} -> {inv}')
                if ax == '15' and any((x % 7 == 0) != (y % 7 == 4) or (x % 7 == 4) != (y % 7 == 0) for x, y in zip(nums, inums)):
                    fail('G', f'1<->5 inversion does not swap do and so: {where} -> {inv}')
            # augmentation: every value doubled, same notes
            COUNT['climb 13 augmentations'] += 1
            def durs(cs):
                out = []
                for c in cs:
                    if isinstance(c, int):
                        out.append([c, 1])
                    elif c == 'h' and out:
                        out[-1][1] += 1
                return out
            da, ds = durs(r['aug']), durs(cells)
            if [x[0] for x in da] != [x[0] for x in ds] or [x[1] for x in da] != [2 * x[1] for x in ds] or len(r['aug']) != 2 * len(cells):
                fail('G', f'augmentation is not the subject at double length: {where} -> {r["aug"]}')
            # the drawn/played lines: the transformed cells, moved by whole octaves to sit within a tritone of the subject
            s0 = next(x for x in r['line'] if x)
            for nm, tl, base in (('inversion', r['tinv1'], r['linv1']), ('1-5 inversion', r['tinv15'], r['linv15']), ('augmentation', r['taug'], r['laug'])):
                f0 = next((x for x in tl if x), None)
                sh = {(t['midi'] - u['midi']) for t, u in zip(tl, base) if t and u}
                if len(sh) != 1 or next(iter(sh)) % 12 or any((t is None) != (u is None) or (t and (t['li'], t['acc'], t['on']) != (u['li'], u['acc'], u['on'])) for t, u in zip(tl, base)):
                    fail('G', f'{nm} line is not the transformed cells moved by octaves: {where}')
                elif abs(f0['midi'] - s0['midi']) > 6:
                    fail('G', f'{nm} starts {f0["midi"] - s0["midi"]} semitones from the subject: {where}')

        # playback of the four buttons: subject, inversion, augmentation, diminution
        await pg.goto('http://app/index.html#climbs/13')
        await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{window.__T=[];c2Tone=(m,t,d)=>{__T.push([m,t,d])};S.level=6;C13.tab='fugue'}")
        play_jobs = [('tonal', k, None) for k in ('A', 'B')] + [('modal', k, None) for k in ('A', 'B')] + \
                    [('own', None, (rand_subject(rng), rng.randrange(12), rng.choice(['maj', 'min']))) for _ in range(6)]
        for sysk, sub, own_s in play_jobs:
            for axis in ('first', '15'):
                out = await pg.evaluate("""async([sys,sub,own,axis])=>{if(own){C13.sys='tonal';C13.ownOn=true;C13.own=own[0];C13.key={k:own[1],mode:own[2]}}else{C13.sys=sys;C13.ownOn=false;C13.sub=sub}
                  C13.tr.axis=axis;renderClimb13();const r={};for(const k of ['sub','inv','aug','dim']){__T.length=0;const el=document.querySelector(`[data-c13play="${k}"]`);if(!el)return{missing:k};el.click();await new Promise(z=>setTimeout(z,300));if(!__T.length){el.click();await new Promise(z=>setTimeout(z,300))}r[k]=__T.slice()}
                  const ctx=c13Ctx(),cells=c13Sub();r.cells=cells;r.invcells=c13Inv(cells,axis);r.exp_inv=c13TLine('inv',cells,ctx).filter(p=>p&&p.on).map(p=>p.midi);return r}""",
                                      [sysk, sub, own_s, axis])
                COUNT['climb 13 playback checks'] += 1
                if 'missing' in out:
                    fail('G', f'no button data-c13play="{out["missing"]}" in the fugue tab'); break
                S_, D_, A_, I_ = out['sub'], out['dim'], out['aug'], out['inv']
                if not S_:
                    fail('G', f'subject plays nothing ({sysk} {sub} {own_s})'); continue
                rel = lambda T: [(m, round(t - T[0][1], 6), round(d, 6)) for m, t, d in T]
                rs, rd, ra = rel(S_), rel(D_), rel(A_)
                if len(rd) != len(rs) or any(m != m2 or abs(t / 2 - t2) > 1e-4 or abs(d / 2 - d2) > 1e-4 for (m, t, d), (m2, t2, d2) in zip(rs, rd)):
                    fail('G', f'diminution is not the subject at half length ({sysk} {sub} {own_s}): {rs[:4]} vs {rd[:4]}')
                if len(ra) != len(rs) or any(m != m2 or abs(2 * t - t2) > 1e-4 or abs(2 * d - d2) > 1e-4 for (m, t, d), (m2, t2, d2) in zip(rs, ra)):
                    fail('G', f'augmentation playback is not the subject at double length ({sysk} {sub} {own_s})')
                # the inversion played = the inverted cells, independently pitched, moved by octaves near the subject
                if sysk == 'modal':
                    ctx = {'modal': True, 'fin_dn': await pg.evaluate("c13Ctx().fin.dn")}
                else:
                    kk = await pg.evaluate("c13Ctx().key")
                    ctx = {'modal': False, 'k': kk['k'], 'mode': kk['mode']}
                L = [x for x in c13_line(out['invcells'], ctx) if x and x[1]]
                s0m = next(x for x in c13_line(out['cells'], ctx) if x)[0].midi
                o = 0
                while L[0][0].midi + o - s0m > 6: o -= 12
                while s0m - (L[0][0].midi + o) > 6: o += 12
                if [m for m, t, d in I_] != [x[0].midi + o for x in L]:
                    fail('G', f'inversion playback ({axis}) {sysk} {sub} {own_s}: {[m for m, t, d in I_]} vs {[x[0].midi + o for x in L]}')
        await pg.evaluate("()=>{C13.ownOn=false;C13.sys='tonal';C13.sub='A'}")
        await b.close()

    COUNT['page errors'] = len(errs)
    for e in errs[:5]:
        fail('page', e)
    report = {
        'suite': 'counterpoint_test (charter suite 6: species and fugue, independent counterpoint checker)',
        'counts': dict(COUNT),
        'runtime_s': round(time.time() - t_start, 1),
        'n_failures': len(FAIL),
        'failures': FAIL[:25],
        'regression_cases': REG,
    }
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    asyncio.run(main())
