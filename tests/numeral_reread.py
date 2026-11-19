"""R8 (0.48): re-read every Analysis numeral and cadence label from the notes, and generate the numerals.

Run from the repo root:
    python3 tests/numeral_reread.py            check scores/meta.json against the notes (exit 1 on any difference)
    python3 tests/numeral_reread.py --write    write the generated numerals, functions and cadence chords into meta.json
    python3 tests/numeral_reread.py --table    print the full table (score, bar, line, notes, old, new, evidence)

How it reads the notes
  * The three chorales' Humdrum files (scores/src) are read line by line: every data line is a time slice, and the
    note sounding in each voice at that slice is spelled from the **kern token (so C# stays C#, not D-flat).
  * music21 re-reads the same files independently (converter.parse + chordify). Every slice must hold exactly the
    pitches music21 finds at that offset, or the script stops.
  * A label is anchored to a note (note-L<line>F<field>): its chord is the slice at that line, minus the non-chord
    tones listed in DECIDE (each with its reason), with the 4-3 / 2-3 suspensions spelled out there.

How it names a chord (the generator; fixes the old labels' faults)
  * root, third, fifth, seventh, inversion and quality come from music21 (Chord.root(), .inversion(), interval checks);
  * case from the third (major or augmented upper case, minor or diminished lower case);
  * diminished triad °, diminished 7th °7, half-diminished 7th ø7, augmented +;
  * an altered root carries its accidental (♯vi°, ♭VI): in a minor key the leading-note chord (vii°) is not marked,
    the raised 6th is (♯vi°);
  * figures: 6, 64 for triads; 7, 65, 43, 42 for 7th chords (the app stacks the last two digits);
  * applied chords: a chord that is not in the key (natural, harmonic or melodic minor in a minor key) and acts as V or
    vii° of the next chord is named in that chord's key, e.g. V65/V, vii°6/vi. The target's numeral takes the home
    key's case (harmonic minor for V and vii° in a minor key);
  * a passing 7th on a weak quaver is left out of the harmony row (it is a passing note), and shown as (7) in the
    cadence chords: V(7) – I;
  * a 4-3 (or bass 2-3) suspension is written V(4–3), with the chord the suspension resolves into.
Function (for the harmony row's colour, as the app's FN colours): T tonic, PD predominant, D dominant (V, vii°),
C colour (applied, chromatic or altered chords; a major I inside a minor-key phrase), W the minor v (no leading note, weak pull: register item R9),
S the subtonic VII of a minor key. The final major I of a minor-key piece (Picardy third) stays T.
"""
import sys, re, json, pathlib
from fractions import Fraction as Fr
from music21 import converter, chord, pitch, interval

REPO = pathlib.Path(__file__).resolve().parent.parent
META = REPO / 'scores' / 'meta.json'
SRC = {'chorale': ('chor001.krn', 'G', 'major'), 'ohaupt': ('chor080.krn', 'D', 'major'), 'jesu': ('chor138.krn', 'E', 'minor')}
SUP = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')

# ----------------------------------------------------------------------------------------------------------------
# Decisions that need the ear and the voice-leading, not just the vertical slice. Key: (score, anchor line, n) where
# n counts labels on the same anchor.
#   drop: pitches at the anchor that are non-chord tones; lines: read these lines instead of the anchor's;
#   sus: (suspended pitch, resolution pitch, figure); target: applied-chord target degree (1-7) when the
#   resolution is not the next label; plain: True to name a chromatic chord as it stands (no applied reading).
# Every entry carries 'why' (the evidence, which goes into the report).
DECIDE = {
    ('chorale', 'L107', 0): {'drop': ['F#4'], 'why': 'alto F♯ is a 9–8 suspension tied over from bar 16, resolving to E on the next quaver'},
    ('chorale', 'L111', 0): {'lines': [111, 112], 'drop': ['A2'], 'why': 'bass A on the beat is a passing note (C–B–A–G); the chord is G–B–D, G arriving in the bass on the next quaver'},
    ('chorale', 'L81', 0): {'sus': ('A4', 'G4', '7–6'), 'why': 'B–D–A–D: the alto A is prepared (sounds in the chord before) and falls to G on the next quaver over the same B: a 7–6 suspension over I6. B–D–A has no F♯, so it is not a iii7 chord'},
    ('chorale', 'L81', 1): {'lines': [82], 'why': 'the resolution of the 7–6 (G–B–D over B): covered by I6(7–6)'},
    ('chorale', 'L84', 0): {'sus': ('G4', 'F#4', '4–3'), 'why': 'D–D–G–C: alto G is held over from the previous beat (prepared) and falls to F♯ on the next quaver: D–F♯–A–C with a 4–3 suspension. No 3rd on the beat, so not a minor iv'},
    ('chorale', 'L98', 0): {'sus': ('A4', 'G4', '9–8'), 'why': 'G–B–A–D: the alto A is held over (dotted) from the V6 on beat 1 and falls to G on the next quaver over the same G bass: I with a 9–8 suspension'},
    ('chorale', 'L117', 0): {'sus': ('G3', 'F#3', '2–3'), 'why': 'G–D–A–D: the bass G is tied from the previous I and falls to F♯ (a bass 2–3 suspension); the upper voices D–A–D are the dominant. No 3rd above G, so not a minor i'},
    ('ohaupt', 'L40', 0): {'sus': ('B3', 'A#3', '4–3'), 'target': 6, 'why': 'F♯–B–F♯–C♯: tenor B is held from the previous chord and falls to A♯ (4–3); the 6th of a 6/4 (D) is absent, so this is V of B minor with a suspended 4th, not vi⁶₄'},
    ('ohaupt', 'L61', 1): {'lines': [62], 'why': 'beat 2: the 6/4 neighbour returns to D–A–F♯–D; label moved to the tenor A (note-L62F2) where this chord starts'},
    ('ohaupt', 'L69', 0): {'target': 2, 'why': 'E–C–F♯–A: F♯–A–C–E over E is the half-diminished ii of E minor in 4/2 (the bass then dips to D♯, vii°7 of E minor, before E minor arrives). C natural, so not iii⁴₂ of D major'},
    ('ohaupt', 'L71', 0): {'drop': ['F#4'], 'why': 'alto F♯ is re-struck over E–G–B and falls to E: an appoggiatura (9–8)'},
    ('ohaupt', 'L97', 0): {'sus': ('D4', 'C#4', '4–3'), 'why': 'A–A–D–E: the alto D falls (through B) to C♯ on beat 4: V with a 4–3 suspension. No F♯, so not a 6/4 of D, and never a minor i'},
    ('jesu', 'L50', 0): {'sus': ('E4', 'D#4', '4–3'), 'why': 'B–E–B–F♯: tenor E falls to D♯ on beat 4 (4–3); no G, so not a minor i⁶₄'},
    ('jesu', 'L73', 0): {'plain': True, 'why': 'E–E–G–C♯: C♯–E–G over E, C♯ the raised 6th of E minor; it leads to F♯–A♯–D, so it is not vii° of the next chord: ♯vi°6 (ii°6 of B minor)'},
    ('jesu', 'L81', 0): {'sus': ('B3', 'A#3', '4–3'), 'target': 5, 'why': 'F♯–B–F♯–C♯: tenor B falls to A♯ on the next beat (4–3); no D, so not v⁶₄: V of V (F♯ major) with a suspended 4th'},
    ('jesu', 'L81', 1): {'lines': [82], 'target': 5, 'why': 'beat 4 of bar 10: F♯–A♯–F♯–C♯ (alto E on the last quaver is a passing 7th), resolving to B major in bar 11: the resolution of the 4–3, so covered by V(4–3)/V'},
}

# Cadence chords are generated from the harmony labels: the arrival chord's label and the label before it (its
# resolved chord, without the suspension figure), with (7) where a passing 7th (a minor 7th above the root, after the
# chord's onset and before the arrival) sounds. Decisions: (score, cadence index) -> lines to read the chord before the
# arrival from (when the label before it is a neighbour chord), a cadence text, and the reason.
CAD_DECIDE = {
    ('ohaupt', 2): {'lines': [59], 'why': 'bar 5 beat 4: E–A–G–C♯ (the tenor A on the second quaver turns vii°6 into V⁴₃), resolving to the tonic bass D with a IV⁶₄ neighbour above, then I: V⁴₃–I, not a plagal cadence'},
    ('ohaupt', 3): {'t': 'Imperfect (half) cadence in E minor (i⁶–V there; the bass rises G–A–B, so not a Phrygian cadence)',
                    'why': 'bar 7 beat 4: G–B–E–G = E minor over G (ii⁶ in D, i⁶ in E minor), bass passing A; bar 8: B–B–D♯–F♯ = B major, V of E minor. Not Phrygian: that needs iv⁶–V with the bass falling a semitone; here the bass rises G–A–B'},
}

# anchors moved so that a label sits on the note where its chord starts
REANCHOR = {('ohaupt', 'L61', 1): 'note-L62F2'}  # the I of beat 2 hangs on the tenor A that starts it


def kpitch(tok):
    m = re.search(r'([a-gA-G])\1*', tok)
    s = m.group(0)
    octv = 3 + len(s) if s[0].islower() else 4 - len(s)
    acc = re.match(r'(#+|-+|n)?', tok[m.end():]).group(0).replace('n', '')
    return s[0].upper() + acc + str(octv)


def kdur(tok):
    m = re.match(r'[\[\(]*(\d+)(\.*)', tok)
    d = Fr(4, int(m.group(1)))
    dd = d
    for _ in m.group(2):
        dd /= 2
        d += dd
    return d


def read_kern(path):
    """line number -> (onset in crotchets, [bass, tenor, alto, soprano] sounding)"""
    t, ends, cur, out = Fr(0), [Fr(0)] * 4, [None] * 4, {}
    for i, ln in enumerate(path.read_text().split('\n'), 1):
        if not ln or ln[0] in '*!=':
            continue
        for j, tk in enumerate(ln.split('\t')):
            if tk == '.':
                continue
            if 'r' in tk and not re.search('[a-gA-G]', tk):
                cur[j] = None
            else:
                cur[j] = kpitch(tk)
            ends[j] = t + kdur(tk)
        out[i] = (t, list(cur))
        t = min(e for e in ends if e > t)
    return out


def m21_check(path, slices):
    """music21's own reading of the file must give the same pitches at every slice."""
    s = converter.parse(str(path)).chordify().flatten()
    got = {}
    for c in s.getElementsByClass('Chord'):
        got[Fr(c.offset).limit_denominator(64)] = sorted({p.nameWithOctave.replace('-', 'b') for p in c.pitches})  # chordify merges unisons
    bad = []
    for ln, (t, cur) in slices.items():
        want = sorted({x for x in cur if x})
        if got.get(t) != want:
            bad.append((ln, float(t), want, got.get(t)))
    return bad


def m21p(n):
    return pitch.Pitch(n.replace('b', '-') if len(n) > 2 and n[1] == 'b' else n)


class Key:
    def __init__(self, tonic, mode):
        self.t, self.mode = m21p(tonic + '4'), mode
        steps = ['M2', 'M3', 'P4', 'P5', 'M6', 'M7'] if mode == 'major' else ['M2', 'm3', 'P4', 'P5', 'm6', 'm7']
        self.scale = [self.t.name] + [self.t.transpose(s).name for s in steps]
        self.extra = [] if mode == 'major' else [self.t.transpose('M6').name, self.t.transpose('M7').name]

    def degree(self, p):
        """0-6 by letter, and the accidental against the (natural) scale degree in semitones"""
        d = ('CDEFGAB'.index(p.step) - 'CDEFGAB'.index(self.t.step)) % 7
        acc = (p.pitchClass - m21p(self.scale[d] + '4').pitchClass + 6) % 12 - 6
        return d, acc

    def diatonic(self, names):
        ok = set(self.scale) | set(self.extra)
        return all(n in ok for n in names)


def anatomy(names):
    """music21 names the chord: root, bass, inversion and the intervals above the root"""
    c = chord.Chord([m21p(n) for n in names])
    root = c.root()
    pcs = {(p.pitchClass - root.pitchClass) % 12 for p in c.pitches}
    third = 4 if 4 in pcs else 3 if 3 in pcs else None
    fifth = 7 if 7 in pcs else 6 if 6 in pcs else 8 if 8 in pcs else None
    seventh = 10 if 10 in pcs else 11 if 11 in pcs else 9 if (9 in pcs and third == 3 and fifth == 6) else None
    b = (c.bass().pitchClass - root.pitchClass) % 12
    inv = 0 if b == 0 else 1 if b in (3, 4) else 2 if b in (6, 7, 8) else 3
    return c, root, third, fifth, seventh, inv


def name_in(names, key):
    """(numeral without the applied part, degree, accidental, quality) of a chord in a key"""
    c, root, third, fifth, seventh, inv = anatomy(names)
    if third is None:
        raise ValueError(f'no third in {names}: needs a decision (suspension or open 5th)')
    d, acc = key.degree(root)
    if key.mode == 'minor' and d == 6 and acc == 1:   # leading-note chord: not marked
        acc = 0
    upper = third == 4
    rn = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][d]
    rn = rn if upper else rn.lower()
    rn = ('♯' * acc if acc > 0 else '♭' * -acc) + rn
    q = 'aug' if (third == 4 and fifth == 8) else 'dim7' if (third == 3 and fifth == 6 and seventh == 9) else \
        'hdim' if (third == 3 and fifth == 6 and seventh == 10) else 'dim' if (third == 3 and fifth == 6) else \
        ('maj' if upper else 'min')
    rn += {'aug': '+', 'dim': '°', 'dim7': '°', 'hdim': 'ø'}.get(q, '')
    if seventh is not None:
        fig = ['7', '65', '43', '42'][inv]
    else:
        fig = ['', '6', '64'][min(inv, 2)]
    return rn, fig, d, acc, q, seventh is not None


def target_name(d, key):
    up = (d in (0, 3, 4) if key.mode == 'major' else d in (2, 4, 5, 6))
    return ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][d] if up else ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'][d]


def function(d, acc, q, key, applied, diatonic=True):
    if applied or acc or not diatonic:
        return 'C'
    if key.mode == 'major':
        return ['T', 'PD', 'T', 'PD', 'D', 'T', 'D'][d]
    if d == 0:
        return 'T'
    if d == 4:
        return 'D' if q == 'maj' else 'W'
    if d == 6:
        return 'D' if q in ('dim', 'dim7', 'hdim') else 'S' if q == 'maj' else 'C'
    if q == 'aug':
        return 'C'
    return ['T', 'PD', 'T', 'PD', 'D', 'T', 'D'][d]


def up(a, b):
    """(letter steps, semitones) from pitch a up to pitch b"""
    return (('CDEFGAB'.index(b.step) - 'CDEFGAB'.index(a.step)) % 7, (b.pitchClass - a.pitchClass) % 12)


def resolve(names, sus):
    return [sus[1] if n == sus[0] else n for n in names] if sus else list(names)


def generate(names, key, reach=None, target=None, plain=False, sus=None, last=False):
    """numeral text, function and facts for a chord. names: the chord tones after the decisions; reach: (tones of the
    next chord with another root, whether that chord is itself applied) or None."""
    names = resolve(names, sus)
    rn, fig, d, acc, q, sev = name_in(names, key)
    c, root, third, fifth, seventh, inv = anatomy(names)
    if target is None and not plain and reach is not None:
        nr = anatomy(reach[0])[1]
        # an applied chord leans on a leading note that is not in the key's natural scale (or is not in the key at all)
        lt_out = (q == 'maj' and root.transpose('M3').name not in key.scale) or \
                 (q in ('dim', 'dim7', 'hdim') and root.name not in key.scale) or \
                 not key.diatonic([m21p(n).name for n in names])
        if lt_out and q == 'maj' and seventh in (None, 10) and up(nr, root) == (4, 7):      # V(7) of the next chord
            target = key.degree(nr)[0]
        elif lt_out and q in ('dim', 'dim7', 'hdim') and up(root, nr) == (1, 1):            # vii° of the next chord
            target = key.degree(nr)[0]
        if target == 0:
            target = None
    applied = None
    if target is not None:
        # the target is written as the chord actually reached (A major: /IV; B minor: /v), unless that chord is itself
        # an applied chord (then the home key's case: V65/ii before V/V, not V65/V/V)
        if reach is not None and not reach[1] and key.degree(anatomy(reach[0])[1])[0] == target:
            ra = anatomy(reach[0])
            upper = ra[2] == 4
            troot = ra[1]
            rd, racc = key.degree(troot)
            tn = ('♯' * racc if racc > 0 and not (key.mode == 'minor' and target == 6) else '♭' * -racc if racc < 0 else '') + \
                (['I', 'II', 'III', 'IV', 'V', 'VI', 'VII'][target] if upper else ['i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii'][target])
        else:
            tn = target_name(target, key)
            troot = m21p(key.scale[target] + '4')
            if key.mode == 'minor' and target == 4:
                troot = m21p(key.t.transpose('P5').name + '4')
            upper = tn[0].isupper()
        tkey = Key(troot.name, 'major' if upper else 'minor')
        rn, fig = name_in(names, tkey)[:2]
        applied = tn
    tail = ('/' + applied) if applied else ''
    txt = rn + fig + (f'({sus[2]})' if sus else '') + tail
    f = 'T' if (last and key.mode == 'minor' and d == 0 and q == 'maj' and not applied) else function(d, acc, q, key, applied, key.diatonic([m21p(n).name for n in names]))
    return txt, f, {'rn': rn, 'fig': fig, 'tail': tail, 'root': root, 'sev': seventh is not None, 'applied': bool(applied)}


def passing_seventh(info, sl, lines):
    """a minor 7th above the root sounding after the chord's onset, before the next chord (a passing 7th)"""
    pc = (info['root'].pitchClass + 10) % 12
    return any(m21p(n).pitchClass == pc for ln in lines[1:] for n in sl[ln][1] if n)


def main():
    meta = json.loads(META.read_text())
    write, table = '--write' in sys.argv, '--table' in sys.argv
    rows, diffs, crows = [], [], []
    for key_, (fn, ton, mode) in SRC.items():
        path = REPO / 'scores' / 'src' / fn
        sl = read_kern(path)
        bad = m21_check(path, sl)
        if bad:
            raise SystemExit(f'{key_}: the Humdrum reading and music21 differ at {bad[:3]}')
        K = Key(ton, mode)
        m = meta[key_]
        bars = [(x[0], int(x[1].split('L')[1])) for x in m['measures']]
        datalines = sorted(sl)
        labs = m['labels']
        chords, seen = [], {}
        for i, l in enumerate(labs):
            line = int(l['id'].split('L')[1].split('F')[0])
            ref = (key_, f'L{line}', seen.get(line, 0))
            seen[line] = ref[2] + 1
            dc = dict(DECIDE.get(ref, {}), ref=ref)
            lines = dc.get('lines', [line])
            names = [x for ln in lines for x in sl[ln][1] if x]
            names = [n for n in names if n not in dc.get('drop', [])]
            chords.append({'line': lines[0], 'lines': lines, 'names': names, 'dc': dc, 'res': resolve(names, dc.get('sus'))})
        for c in chords:
            c['rootname'] = anatomy(c['res'])[1].name

        def reach_of(i, applied):
            nx = next((j for j in range(i + 1, len(chords)) if chords[j]['rootname'] != chords[i]['rootname']), None)
            return None if nx is None else (chords[nx]['res'], applied[nx])
        # pass 1 (is each chord applied?), pass 2 (applied targets written as the chord reached)
        applied = [False] * len(chords)
        for _ in range(2):
            out = []
            for i, c in enumerate(chords):
                dc = c['dc']
                out.append(generate(c['names'], K, reach_of(i, applied), dc['target'] - 1 if 'target' in dc else None,
                                    dc.get('plain', False), dc.get('sus'), i == len(chords) - 1))
            applied = [o[2]['applied'] for o in out]
        keep = []
        for i, l in enumerate(labs):
            c, (new, f, info) = chords[i], out[i]
            line = int(l['id'].split('L')[1].split('F')[0])
            bar = next((b for b, ln in reversed(bars) if ln < c['line']), '') or 'upbeat'
            nid = REANCHOR.get(c['dc']['ref'], l['id'])
            prev = keep[-1] if keep else None
            # a suspension label names the chord it resolves into: the resolution is not labelled again;
            # nor is a label repeated on the same note
            sus_prev = prev is not None and chords[prev]['dc'].get('sus')
            covered = (sus_prev and out[prev][0].replace(f"({sus_prev[2]})", '') == new) or \
                      (prev is not None and out[prev][0] == new and labs[prev]['id'] == l['id'])
            rows.append({'score': key_, 'bar': bar, 'line': c['line'], 'id': nid,
                         'notes': ' '.join(sorted(set(x for ln in c['lines'] for x in sl[ln][1] if x), key=lambda n: m21p(n).ps)),
                         'old': l['t'], 'new': f'(removed: {new}, covered by the label before it)' if covered else new, 'f': f, 'why': c['dc'].get('why', '')})
            if covered:
                diffs.append(f"{key_} bar {bar} line {line}: '{l['t']}' repeats the label before it")
                continue
            keep.append(i)
            if l['t'] != new or l.get('f') != f or l['id'] != nid:
                diffs.append(f"{key_} bar {bar} line {line}: meta '{l['t']}'/{l.get('f')} at {l['id']}, notes give '{new}'/{f} at {nid}")
            if write:
                l['t'], l['f'], l['id'] = new, f, nid
        # cadence chords
        for ci, cd in enumerate(m['cads']):
            dec = CAD_DECIDE.get((key_, ci), {})
            aline = int(cd['id'].split('L')[1].split('F')[0])
            ai = next(i for i in keep if chords[i]['line'] == aline)
            if 'lines' in dec:
                names = [x for ln in dec['lines'] for x in sl[ln][1] if x]
                ptxt, _, pinfo = generate(names, K)
                pfrom = dec['lines'][0]
            else:
                pi = keep[keep.index(ai) - 1]
                pinfo = out[pi][2]
                ptxt = pinfo['rn'] + pinfo['fig'] + pinfo['tail']
                pfrom = chords[pi]['line']
            span = [ln for ln in datalines if pfrom <= ln < aline]
            p7 = not pinfo['sev'] and passing_seventh(pinfo, sl, span)
            if p7:
                ptxt = pinfo['rn'] + pinfo['fig'] + '(7)' + pinfo['tail']
            ainfo = out[ai][2]
            ch = f"{ptxt} – {ainfo['rn'] + ainfo['fig'] + ainfo['tail']}"
            why = dec.get('why', '') or (f'passing 7th ({(pinfo["root"].transpose("m7")).name.replace("#", "♯").replace("-", "♭")}) after the onset of the chord before the arrival' if p7 else 'no 7th sounds in the chord before the arrival' if not pinfo['sev'] else 'the 7th sounds with the chord')
            bar = next((b for b, ln in reversed(bars) if ln < aline), '')
            crows.append({'score': key_, 'bar': bar, 'old': cd['ch'], 'new': ch, 'why': why})
            if cd['ch'] != ch or (dec.get('t') and cd['t'] != dec['t']):
                diffs.append(f"{key_} cadence bar {bar}: meta '{cd['ch']}', notes give '{ch}'")
            if write:
                cd['ch'] = ch
                if dec.get('t'):
                    cd['t'] = dec['t']
        if write:
            m['labels'] = [labs[i] for i in keep]
    if table:
        for r in rows:
            print(f"{r['score']}\t{r['bar']}\t{r['line']}\t{r['notes']}\t{r['old']}\t{r['new']}\t{r['f']}\t{r['why']}")
        for r in crows:
            print(f"CAD\t{r['score']}\t{r['bar']}\t{r['old']}\t{r['new']}\t{r['why']}")
    if write:
        META.write_text(json.dumps(meta, ensure_ascii=False, separators=(', ', ': ')))
        print('meta.json written')
        return 0
    for d in diffs:
        print('DIFF', d)
    print(json.dumps({'labels checked': len(rows), 'cadences checked': len(crows), 'differences': len(diffs)}))
    return 1 if diffs else 0


if __name__ == '__main__':
    sys.exit(main())
