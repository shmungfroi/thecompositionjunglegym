#!/usr/bin/env python3
"""Melody rung 12 (classical): the curated phrase excerpts from the ten licensed scores (register M12, build 0.49).

Unlike repertoire_scan.py (which proved supply with sliding windows and an automatic key per window), this picks PHRASES:
  - the chorales: one excerpt per phrase, phrase ends at each fermata (the cadence list in scores/meta.json), the upbeat included;
  - Chopin Op. 28/7: each two-bar unit with its upbeat (the piece's own phrase shape);
  - the other pieces: two-bar units aligned with the section starts in scores/meta.json (`sections`), in the section's own key
    (meta.json's key text for the section, else the piece's key), never the scan's automatic key.
Each candidate is kept when it is dictatable: 5–24 notes; no rest longer than a beat inside; no leap over an octave; every note
diatonic in the key (la-based minor may use si and fi), at most two other chromatic notes; ends on a note of the tonic triad; every
duration is a written value the palette offers, and no note crosses a beat except a whole-beat value or a dotted crotchet starting on
a beat. Ornaments and grace notes are left out (they are played); tied notes are merged.
Then the hand-pick rules: no two excerpts overlap; at most 8 from each rag (they are long and alike); a short list of rejects
(PICK_OUT) after listening through the candidates' solfa.
Output: m12_excerpts.json (the data table, also printed as a markdown table) and the JS constant for index.html (LADM12).
Every pick needs the independent theory check before release (register M12).
Run: python3 tests/reports/ladder_049/m12_curate.py [--js]
"""
import collections, json, sys, pathlib
import music21 as m

ROOT = pathlib.Path(__file__).resolve().parents[3]
SRC = ROOT / 'scores' / 'src'
META = json.load(open(ROOT / 'scores' / 'meta.json'))
FILES = {'chorale': 'chor001', 'ohaupt': 'chor080', 'jesu': 'chor138', 'k545': 'sonata15-1', 'k331a': 'sonata11-1a', 'k331d': 'sonata11-1d',
         'maple': 'mapleleaf', 'entertainer': 'entertainer', 'chopin7': '028-1-BH-007', 'chopin20': '028-1-BH-020'}
TON = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
DIA = {0: ('d', 0), 2: ('r', 1), 4: ('m', 2), 5: ('f', 3), 7: ('s', 4), 9: ('l', 5), 11: ('t', 6)}
CHR_UP = {1: ('di', 0), 3: ('ri', 1), 6: ('fi', 3), 8: ('si', 4), 10: ('li', 5)}
CHR_DN = {1: ('ra', 1), 3: ('me', 2), 6: ('se', 4), 8: ('le', 5), 10: ('te', 6)}
TICK = 420
PICK_OUT = {'k545_42-43', 'k545_44-45',      # the recapitulation in F: bars 1-4 transposed (a transposition is not a new item)
            'k545_63-64', 'k545_65-66',      # the recapitulation's S: bars 18-21 transposed, only the last note differs
            'maple_8-8',                     # a broken-octave accompaniment figure, not the tune
            'maple_49-50'}                   # the A strain's return: bars 15-16 again with one added note
MAX_PER = {'maple': 8, 'entertainer': 8}


def parse_key(txt):
    """'A♭ major' / 'E minor' / 'G major (V)' -> (tonic pc, mode)"""
    t = txt.replace('♭', 'b').replace('♯', '#').split()
    pc = (TON[t[0][0]] + (-1 if 'b' in t[0][1:] else 1 if '#' in t[0][1:] else 0)) % 12
    return pc, ('min' if t[1].startswith('minor') else 'maj')


def melody(key):
    sc = m.converter.parse(str(SRC / (FILES[key] + '.krn')))

    def mean(pt):
        ps = [x.midi for n in pt.flatten().notes for x in n.pitches]
        return sum(ps) / max(1, len(ps))
    p = max(sc.parts, key=mean)
    ev, meas_info = [], []
    for mix, meas in enumerate(p.getElementsByClass('Measure')):
        ts = meas.timeSignature or meas.getContextByClass('TimeSignature') or (meas_info and m.meter.TimeSignature(meas_info[-1][4])) or sc.recurse().getElementsByClass('TimeSignature')[0]
        bq = ts.barDuration.quarterLength
        mo = float(meas.getOffsetBySite(p))
        meas_info.append((meas.number, mo, float(bq), float(meas.duration.quarterLength), ts.ratioString))
        by = collections.OrderedDict()
        for n in meas.recurse().notesAndRests:
            if n.duration.isGrace or n.quarterLength == 0:
                continue
            off = float(n.getOffsetInHierarchy(meas))
            if n.isRest:
                by.setdefault(off, [None, float(n.quarterLength), '', False])
                continue
            top = max(x.midi for x in n.pitches)
            tie = n.tie.type if n.tie is not None else ''
            ferm = any('Fermata' in type(e).__name__ for e in n.expressions)
            if off not in by or by[off][0] is None or by[off][0] < top:
                by[off] = [top, float(n.quarterLength), tie, ferm]
        for off, (pp, d, tie, ferm) in sorted(by.items()):
            a = mo + off
            if ev and tie in ('stop', 'continue') and ev[-1][1] == pp and abs(ev[-1][0] + ev[-1][2] - a) < 1e-6:
                ev[-1][2] += d
                ev[-1][4] = ev[-1][4] or ferm
                continue
            # a rest under a sounding note is not a rest of the line
            if pp is None and ev and ev[-1][0] + ev[-1][2] > a + 1e-6:
                continue
            ev.append([a, pp, d, mix, ferm])
    # cut overlaps (top-line notes that sound past the next onset)
    for i in range(len(ev) - 1):
        ev[i][2] = min(ev[i][2], ev[i + 1][0] - ev[i][0])
    return ev, meas_info


def ms_of(key, meas_info, q_abs):
    """ms in the app's event timeline for an absolute quarter offset, through the measure list in meta.json (same order and count
    as the Humdrum measures: checked)"""
    T = [t0 for b, mid, t0 in META[key]['measures']]
    if len(T) != len(meas_info):
        # repeats written out differently: map by bar number (unique in these scores apart from upbeat bars)
        lab = {}
        for b, mid, t0 in META[key]['measures']:
            lab.setdefault(b, t0)
        T = [lab.get(str(num) if num else '') for num, mo, bq, dq, ts in meas_info]
        for i in range(2, len(T)):   # a trailing bar the app does not list: extend at the same speed
            if T[i] is None and T[i - 1] is not None and T[i - 2] is not None:
                T[i] = T[i - 1] + (T[i - 1] - T[i - 2]) / meas_info[i - 2][3] * meas_info[i - 1][3]
        if any(t is None for t in T):
            return None
    for i, (num, mo, bq, dq, ts) in enumerate(meas_info):
        if mo - 1e-6 <= q_abs < mo + dq - 1e-6 or i == len(meas_info) - 1:
            per_q = (T[i + 1] - T[i]) / dq if i + 1 < len(T) else (T[i] - T[i - 1]) / meas_info[i - 1][3]
            return round(T[i] + (q_abs - mo) * per_q), per_q
    return None


def solfa(midi, do, minor, prev=None, nxt=None):
    rel = (midi - do) % 12
    o = (midi - (60 + do % 12)) // 12 if False else None
    if rel in DIA:
        s, w = DIA[rel]
    elif minor and rel in (8, 6) and True:
        s, w = ('si', 4) if rel == 8 else ('fi', 3)
    else:
        # chromatic: raised when rising to the next note, lowered when falling
        up = nxt is not None and nxt > midi
        s, w = (CHR_UP if up else CHR_DN)[rel]
    # octave marks against do = 60 + pc (rule MR1); w is the letter step above do
    semis = {'d': 0, 'r': 2, 'm': 4, 'f': 5, 's': 7, 'l': 9, 't': 11, 'di': 1, 'ri': 3, 'fi': 6, 'si': 8, 'li': 10,
             'ra': 1, 'me': 3, 'se': 6, 'le': 8, 'te': 10}[s]
    base = 60 + do % 12
    octv = (midi - base - semis) // 12
    return s + ("'" * octv if octv > 0 else ',' * (-octv)), s


LEGAL = {0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0}


def legal(on_in_bar, d, beat, compound):
    if d not in LEGAL:
        return False
    pos = on_in_bar % beat
    if abs(d / beat - round(d / beat)) < 1e-6:
        return pos < 1e-6
    if d == 1.5 and not compound:
        return pos < 1e-6
    return pos + d <= beat + 1e-6


def windows(key, ev, meas_info):
    M = META[key]
    out = []
    idx = {}
    for i, x in enumerate(meas_info):
        idx.setdefault(x[0], i)
    num_off = {num: (meas_info[i][1], meas_info[i][2], meas_info[i][3], meas_info[i][4]) for num, i in idx.items()}
    if key in ('chorale', 'ohaupt', 'jesu'):
        start = 0
        for i, e in enumerate(ev):
            if e[4]:
                out.append(('phrase', ev[start:i + 1], None, True))
                # the next phrase starts after the fermata note (its upbeat is the rest of the bar)
                start = i + 1
        return out
    if key == 'chopin7':
        for b in range(1, 16, 2):
            if b not in num_off or b + 1 not in num_off:
                continue
            mo, bq, dq, ts = num_off[b]
            a0 = mo - 1.0
            a1 = num_off[b + 1][0] + 2.0
            out.append(('%d-%d' % (b, b + 1), [e for e in ev if a0 - 1e-6 <= e[0] < a1 - 1e-6], None, True))
        return out
    secs = M.get('sections') or []
    cadbars = {c.get('bar') for c in M.get('cads', []) if c.get('bar')}
    for name, b0, b1, col, txt in secs:
        for w in (2, 4):
            for b in range(b0, b1, w if w == 2 else 4):
                if b + w - 1 > b1 or b not in num_off or b + w - 1 not in num_off:
                    continue
                mo = num_off[b][0]
                e1 = b + w - 1
                a1 = num_off[e1][0] + num_off[e1][2]
                out.append(('%d-%d' % (b, e1), [e for e in ev if mo - 1e-6 <= e[0] < a1 - 1e-6], txt, e1 == b1 or e1 in cadbars))
    return out


def sec_key(key, txt):
    home = parse_key(META[key]['key'])
    if not txt:
        return home
    for t in (txt or '').replace('(', ' ').replace(')', ' ').replace(':', ' ').replace(';', ' ').split(','):
        w = t.split()
        for j in range(len(w) - 1):
            if w[j + 1] in ('major', 'minor', 'minor.') and w[j][0] in TON and len(w[j]) <= 2:
                try:
                    return parse_key(w[j] + ' ' + w[j + 1])
                except Exception:
                    pass
    if 'modulates' in txt or 'sequence' in txt:
        return None
    return home


def build():
    cands = []
    for key in FILES:
        ev, meas_info = melody(key)
        for w in windows(key, ev, meas_info):
            lab, notes, txt, phrase_end = w
            k = sec_key(key, txt)
            if k is None or not notes:
                continue
            tonic, mode = k
            minor = mode == 'min'
            do = (tonic + 3) % 12 if minor else tonic
            # trim leading and trailing rests
            while notes and notes[0][1] is None:
                notes = notes[1:]
            while notes and notes[-1][1] is None:
                notes = notes[:-1]
            pitches = [e for e in notes if e[1] is not None]
            if not (5 <= len(pitches) <= 24):
                continue
            first_bar = notes[0][3]
            num_off = {i: (x[1], x[2], x[3], x[4]) for i, x in enumerate(meas_info)}
            mo, bq, dq, ts = num_off[first_bar]
            compound = ts in ('6/8', '9/8', '12/8')
            beat = 1.5 if compound else 1.0
            reasons = []
            if any(e[1] is None and e[2] > beat for e in notes):
                reasons.append('long rest')
            if any(abs(a[1] - b[1]) > 12 for a, b in zip(pitches, pitches[1:])):
                reasons.append('leap over an octave')
            for e in notes:
                bo = e[0] - num_off[e[3]][0]
                if not legal(round(bo, 4), round(e[2], 4), beat, compound):
                    reasons.append('duration %s at %s' % (e[2], bo))
                    break
            sols = []
            chrom = 0
            for i, e in enumerate(pitches):
                nx = pitches[i + 1][1] if i + 1 < len(pitches) else None
                s, base = solfa(e[1], do, minor, None, nx)
                if base not in ('d', 'r', 'm', 'f', 's', 'l', 't') and not (minor and base in ('si', 'fi')):
                    chrom += 1
                sols.append(s)
            if chrom > 2:
                reasons.append('%d chromatic notes' % chrom)
            last = (pitches[-1][1] - do) % 12
            tri = {9, 0, 4} if minor else {0, 4, 7}
            if last not in tri and not phrase_end:
                reasons.append('does not end on the tonic triad (and is not a phrase end)')
            if sum(1 for a, b in zip(pitches, pitches[1:]) if abs(a[1] - b[1]) == 12) > 1:
                reasons.append('octave jumps in the top line (doubling, not a melody)')
            # the anacrusis: notes before the first full bar's downbeat
            full_bar = first_bar if abs(notes[0][0] - mo) < 1e-6 and dq >= bq - 1e-6 else first_bar + 1
            fb_off = num_off[full_bar][0] if full_bar in num_off else mo
            anac_q = max(0.0, fb_off - notes[0][0])
            start_q = notes[0][0]
            # level: the lowest rung whose material covers it (indicative; rung 12 is its own rung)
            durs = {round(e[2], 4) for e in notes}
            bases = {s.rstrip(",'") for s in sols}
            if chrom:
                lvl = 10
            elif bases & {'si', 'fi'} and minor:
                lvl = 7
            elif bases & {'te', 'fi'}:
                lvl = 8
            elif ts in ('3/4', '6/8') or anac_q or not durs <= {0.5, 1.0, 2.0} or minor:
                lvl = 6 if not minor else 6
            else:
                lvl = 4
            rhy_extra = bool(durs - {0.5, 1.0, 2.0, 1.5, 3.0, 4.0})   # dotted quavers or semiquavers: beyond the generated rungs' rhythm
            msr = ms_of(key, meas_info, start_q)
            end_q = notes[-1][0] + notes[-1][2]
            mse = ms_of(key, meas_info, end_q - 1e-6)
            if not msr or not mse:
                reasons.append('no ms map')
            nm = lambda i: meas_info[i][0] or 'upbeat'
            bars_lab = '%s-%s' % (nm(notes[0][3]), nm(notes[-1][3]))
            cid = '%s_%s' % (key, bars_lab)
            # bar lengths (ticks) from the first full bar to the end; the last bar may be short
            bl = []
            b = full_bar
            while b in num_off and num_off[b][0] < end_q - 1e-6:
                mo2, bq2, dq2, ts2 = num_off[b]
                bl.append(int(round(min(bq2, end_q - mo2) * TICK)))
                b += 1
            cands.append(dict(id=cid, score=key, bars=bars_lab, unit=lab, key=('%s %s' % (META[key]['key'].split()[0], META[key]['key'].split()[1]) if (tonic, mode) == parse_key(META[key]['key']) else
                                                                          '%s %s' % (['C', 'D♭', 'D', 'E♭', 'E', 'F', 'F♯', 'G', 'A♭', 'A', 'B♭', 'B'][tonic], 'minor' if minor else 'major')),
                              tonic=tonic, mode=mode, do=do, metre=ts, anac=int(round(anac_q * TICK)), level=lvl, rhy_extra=rhy_extra, reasons=reasons,
                              solfa=' '.join(sols), n=len(pitches),
                              notes=[[int(round((e[0] - start_q) * TICK)), int(round(e[2] * TICK)), e[1],
                                      (sols[pitches.index(e)] if e[1] is not None else None)] for e in notes],
                              barLen=bl, ms=[msr[0], mse[0] + 1] if msr and mse else None, msPerQ=msr[1] if msr else None,
                              credit=META[key]['src'].split('.')[0] + '. ' + META[key]['t']))
    return cands


def pick(cands):
    kept, per = [], collections.Counter()
    used = collections.defaultdict(list)
    seen = set()
    # longer phrases first (a whole 4-bar phrase beats its two halves), then score order
    order = sorted(cands, key=lambda c: (list(FILES).index(c['score']), -len(c['barLen']), c['notes'][0][0]))
    for c in order:
        if c['reasons'] or c['id'] in PICK_OUT or c['n'] > 24:
            continue
        sig = (c['solfa'], tuple((x[0], x[1]) for x in c['notes']), c['metre'])
        if sig in seen:      # a repeat or a transposition (the recapitulation, a repeated strain) is not a new excerpt
            continue
        if per[c['score']] >= MAX_PER.get(c['score'], 99):
            continue
        a, b = c['notes'][0][0], c['notes'][-1][0]
        if any(not (c['ms'][1] <= x[0] + 2 or c['ms'][0] >= x[1] - 2) for x in used[c['score']]):
            continue
        used[c['score']].append(c['ms'])
        per[c['score']] += 1
        seen.add(sig)
        kept.append(c)
    kept.sort(key=lambda c: (list(FILES).index(c['score']), c['ms'][0]))
    return kept


if __name__ == '__main__':
    cands = build()
    kept = pick(cands)
    out = pathlib.Path(__file__).resolve().parent / 'm12_excerpts.json'
    json.dump({'candidates': len(cands), 'kept': kept, 'rejected': [dict(id=c['id'], reasons=c['reasons']) for c in cands if c['reasons']]},
              open(out, 'w'), indent=1, ensure_ascii=False)
    print('candidates', len(cands), 'kept', len(kept), dict(collections.Counter(c['score'] for c in kept)),
          'levels', dict(sorted(collections.Counter(c['level'] for c in kept).items())))
    print('| # | id | score | bars | key | metre | rung level (pitch) | semiquavers / dotted quavers | notes | solfa (do = tonic of the key; la-based minor) |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for i, c in enumerate(kept, 1):
        print('| %d | %s | %s | %s | %s | %s | %d | %s | %d | %s |' % (i, c['id'], c['score'], c['bars'], c['key'], c['metre'], c['level'], 'yes' if c['rhy_extra'] else '', c['n'], c['solfa']))
    if '--js' in sys.argv:
        rows = [dict(id=c['id'], score=c['score'], bars=c['bars'], tonic=c['tonic'], mode=c['mode'], do=c['do'], metre=c['metre'], anac=c['anac'],
                     level=c['level'], rhyExtra=c['rhy_extra'], tempo=round(60000 / c['msPerQ'], 3) if c['msPerQ'] else 80, barLen=c['barLen'], ms=c['ms'], notes=c['notes'],
                     credit=c['credit']) for c in kept]
        print('JS:const LADM12=' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';')
