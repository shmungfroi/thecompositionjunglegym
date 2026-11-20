#!/usr/bin/env python3
"""Melody rung 12 (classical side): how many dictation excerpts the ten licensed scores the app already plays can give.

For each score the melody line is taken from the Humdrum source in scores/src/ (the chorales: the soprano spine; the piano
pieces: the top note of the upper staff at each onset, ties merged). Candidate excerpts are windows of 2 and 4 whole bars
starting at every bar. A window is KEPT when:
  K1  it has 5..24 notes (dictatable), no rest longer than a beat inside it;
  K2  its top line is a real line: no leap over an octave (skyline jumps between voices are rejected);
  K3  every note is diatonic in the local key (key of the window by music21's Krumhansl analysis), or carries one of the
      chromatic syllables rungs 7-10 teach (si in minor, fi, te, and passing/neighbour chromatics); the count of chromatic
      notes sets the window's level;
  K4  it ends on a note of the local tonic triad (a phrase end), or at a cadence bar listed in scores/meta.json.
Each kept window gets a level: the lowest melody rung whose material covers it (3 diatonic crotchet-quaver, 6 leaps and
3/4-6/8, 7 minor si, 8 te/fi, 10 other chromatics). The output is a count per score and per level, and a list of the
first kept windows for the curated set. The curated pool (the build) picks from these by hand; this only proves supply.
Run: python3 tests/reports/ladder_049/repertoire_scan.py [--list]
"""
import collections, json, sys
import music21 as m

SRC = 'scores/src/'
FILES = {'chorale': ('chor001', 'sop'), 'ohaupt': ('chor080', 'sop'), 'jesu': ('chor138', 'sop'),
         'k545': ('sonata15-1', 'top'), 'k331a': ('sonata11-1a', 'top'), 'k331d': ('sonata11-1d', 'top'),
         'maple': ('mapleleaf', 'top'), 'entertainer': ('entertainer', 'top'),
         'chopin7': ('028-1-BH-007', 'top'), 'chopin20': ('028-1-BH-020', 'top')}
DIA = {0: 'd', 2: 'r', 4: 'm', 5: 'f', 7: 's', 9: 'l', 11: 't'}
CHR = {1: 'di/ra', 3: 'ri/me', 6: 'fi/se', 8: 'si/le', 10: 'li/te'}


def line(score, how):
    # the melody part is the one with the highest mean pitch (spine order differs between the encodings: in music21 the
    # chorales' last part is the bass, so position cannot be trusted)
    def mean(pt):
        ps = [x.midi for n in pt.flatten().notes for x in n.pitches]
        return sum(ps) / max(1, len(ps))
    p = max(score.parts, key=mean)
    bars = []
    for meas in p.getElementsByClass('Measure'):
        ev = collections.OrderedDict()
        for n in meas.recurse().notesAndRests:
            off = float(n.getOffsetInHierarchy(meas))
            if n.isRest:
                ev.setdefault(off, ('r', float(n.quarterLength)))
                continue
            top = max(x.midi for x in n.pitches)
            if n.tie is not None and n.tie.type in ('stop', 'continue'):
                continue
            if off not in ev or ev[off][0] == 'r' or ev[off][0] < top:
                ev[off] = (top, float(n.quarterLength))
        bars.append((meas.number, sorted(ev.items())))
    return bars


def solfa(pc_rel, minor):
    rel = pc_rel % 12
    if minor and rel == 8:
        return 'si', True        # la-based minor: raised so
    if rel in DIA:
        return DIA[rel], False
    return CHR[rel], True


def scan(listing=False):
    meta = json.load(open('scores/meta.json'))
    out, kept_all = {}, []
    for key, (f, how) in FILES.items():
        sc = m.converter.parse(SRC + f + '.krn')
        bars = line(sc, how)
        cad_bars = set()
        for c in meta[key].get('cads', []):
            for mi, (lab, mid, ms) in enumerate(meta[key]['measures']):
                pass
        cnt = collections.Counter()
        for w in (2, 4):
            for i in range(len(bars) - w + 1):
                win = bars[i:i + w]
                notes = [(p, d) for _, ev in win for _, (p, d) in ev]
                pitches = [p for p, d in notes if p != 'r']
                if not (5 <= len(pitches) <= 24):
                    continue
                if any(p == 'r' and d > 1 for p, d in notes[1:-1]):
                    continue
                if any(abs(a - b) > 12 for a, b in zip(pitches, pitches[1:])):
                    continue
                st = m.stream.Stream()
                for p in pitches:
                    st.append(m.note.Note(p))
                try:
                    k = st.analyze('key')
                except Exception:
                    continue
                minor = k.mode == 'minor'
                do = (k.tonic.pitchClass + (3 if minor else 0)) % 12
                syl = [solfa(p - do, minor) for p in pitches]
                chrom = [s for s, c in syl if c and s != 'si']
                tonic = {0, 4, 7} if not minor else {9, 0, 4}
                if (pitches[-1] - do) % 12 not in tonic:
                    continue
                lvl = 6 if not chrom and not minor else 7 if not chrom else 8 if set(chrom) <= {'fi/se', 'li/te'} else 10
                if lvl == 6 and all(abs(a - b) <= 4 for a, b in zip(pitches, pitches[1:])):
                    lvl = 3
                cnt[(w, lvl)] += 1
                kept_all.append(dict(score=key, bars='%s-%s' % (win[0][0], win[-1][0]), w=w, key=str(k), level=lvl,
                                     solfa=' '.join(s for s, _ in syl)))
        out[key] = {'%d bars, rung %d' % kw: v for kw, v in sorted(cnt.items())}
    return out, kept_all


if __name__ == '__main__':
    out, kept = scan()
    tot = collections.Counter()
    for k, v in out.items():
        print(k, v)
        for kk, n in v.items():
            tot[kk] += n
    print('TOTAL kept windows', sum(tot.values()), dict(sorted(tot.items())))
    print('scores with at least one kept window:', sum(1 for v in out.values() if v))
    json.dump({'per_score': out, 'kept': kept}, open('tests/reports/ladder_049/repertoire_scan.json', 'w'), indent=1)
    if '--list' in sys.argv:
        for x in kept[:60]:
            print(x)
