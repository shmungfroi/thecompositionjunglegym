"""IC_REG_049 probe C3c: strict common-practice voice leading of every rung 2/3 cadence realisation the app can play
(every weighted pool entry), checked independently: chord content and bass from music21 RomanNumeral (not the app's tables),
then textbook four-part rules written here. Input: /tmp/icreg/cad23.json (dump_cad23.py)."""
import json, collections
from music21 import roman, key as m21key
D = json.load(open('/tmp/icreg/cad23.json'))
NAMES_MAJ = ['C', 'D-', 'D', 'E-', 'E', 'F', 'F#', 'G', 'A-', 'A', 'B-', 'B']
NAMES_MIN = ['c', 'c#', 'd', 'e-', 'e', 'f', 'f#', 'g', 'g#', 'a', 'b-', 'b']
FIG = {0: '', 1: '6', 2: '64'}; FIG7 = {0: '7', 1: '65', 2: '43', 3: '42'}
_rc = {}
def rn_info(tok, k, md):
    ck = (tok, k, md)
    if ck in _rc: return _rc[ck]
    base, _, inv = tok.partition(':'); inv = int(inv or 0)
    if base.endswith('7') or '7/' in base:
        fig = base.replace('7', FIG7[inv], 1)
    elif '/' in base:
        a, b = base.split('/', 1); fig = a + FIG[inv] + '/' + b
    else: fig = base + FIG[inv]
    K = m21key.Key(NAMES_MAJ[k] if md == 'maj' else NAMES_MIN[k])
    r = roman.RomanNumeral(fig, K)
    pcs = [p.pitchClass for p in r.pitches]
    info = {'fig': fig, 'pcs': set(pcs), 'n': len(set(pcs)), 'bass': r.bass().pitchClass, 'root': r.root().pitchClass,
            'third': r.third.pitchClass, 'fifth': r.fifth.pitchClass if r.fifth else None, 'sev': r.seventh.pitchClass if r.seventh else None,
            'inv': inv, 'base': base.split('/')[0], 'sec': '/' in base, 'deg': r.scaleDegree}
    _rc[ck] = info; return info
R = {'B': (40, 62), 'T': (48, 67), 'A': (55, 74), 'S': (60, 79)}
def check(t, k, md, ch):
    rns = t.split(' '); I = [rn_info(x, k, md) for x in rns]; F = []; LN = (k + 11) % 12; tonic = k
    for i, (v, c) in enumerate(zip(ch, I)):
        pc = [m % 12 for m in v]
        for j, nm in enumerate('BTAS'):
            if not R[nm][0] <= v[j] <= R[nm][1]: F.append(f'c{i} range {nm} {v[j]}')
        if not (v[0] <= v[1] <= v[2] <= v[3]): F.append(f'c{i} crossing')
        if v[3] - v[2] > 12 or v[2] - v[1] > 12: F.append(f'c{i} spacing')
        if pc[0] != c['bass']: F.append(f'c{i} wrong bass for {c["fig"]}')
        if any(p not in c['pcs'] for p in pc): F.append(f'c{i} non-chord note in {c["fig"]}')
        miss = c['pcs'] - set(pc)
        if miss - ({c['fifth']} if c['fifth'] is not None and c['inv'] == 0 else set()): F.append(f'c{i} incomplete {c["fig"]} missing {miss}')
        if miss: F.append(f'INFO c{i} 5th omitted {c["fig"]}')
        if c['base'] in ('V', 'V7') and pc.count(LN) > 1: F.append(f'c{i} doubled leading note')
        if c['sec'] and pc.count(c['third']) > 1: F.append(f'c{i} doubled secondary leading note')
        if c['sev'] is not None and pc.count(c['sev']) > 1: F.append(f'c{i} doubled 7th')
        if c['inv'] == 2 and pc.count(c['bass']) < 2: F.append(f'c{i} 6/4 without doubled bass')
        if c['inv'] == 1 and c['base'].startswith('ii') and md == 'min' and pc.count(c['third']) < 2 and pc.count(c['root']) > 1: F.append(f'INFO c{i} ii°6 doubles root (3rd preferred)')
    for i in range(len(ch) - 1):
        P, N, a, b = ch[i], ch[i + 1], I[i], I[i + 1]
        for j in range(4):
            d = N[j] - P[j]; ad = abs(d)
            if ad > 12: F.append(f'm{i} leap>8ve v{j}')
            if ad in (10, 11): F.append(f'm{i} leap 7th v{j}')
            if ad == 6: F.append(f'm{i} tritone leap v{j}')
            if md == 'min' and ad == 3 and {P[j] % 12, N[j] % 12} == {(k + 8) % 12, LN}: F.append(f'm{i} aug 2nd v{j}')
        for j in range(3):
            if N[j] > P[j + 1] or N[j + 1] < P[j]: F.append(f'm{i} overlap v{j}/{j+1}')
        for x in range(4):
            for y in range(x + 1, 4):
                i0, i1 = (P[y] - P[x]) % 12, (N[y] - N[x]) % 12
                if i0 == i1 and i0 in (0, 7) and P[x] != N[x] and P[y] != N[y]: F.append(f'm{i} consecutive {"8ve/unison" if i0 == 0 else "5th"} v{x}/{y}')
        io = (N[3] - N[0]) % 12; dS, dB = N[3] - P[3], N[0] - P[0]
        if io in (0, 7) and dS * dB > 0 and abs(dS) > 2 and (P[3] - P[0]) % 12 != io: F.append(f'm{i} hidden {io} outer, soprano leap')
        if (P[3] - P[0]) % 12 == 6 and io == 7 and dS and dB: F.append(f'INFO m{i} unequal 5ths outer d5-P5')
        # leading note of V/V7
        if a['base'] in ('V', 'V7') and not a['sec'] and b['base'] in ('I', 'i', 'vi', 'VI') and a['base'] != b['base']:
            for j in range(4):
                if P[j] % 12 == LN and N[j] - P[j] != 1:
                    if j in (0, 3) or b['base'] in ('vi', 'VI'): F.append(f'm{i} LN not resolved v{j} into {b["fig"]}')
                    elif not (b['inv'] == 0 and N[j] % 12 == b['fifth'] and P[j] - N[j] in (3, 4)): F.append(f'm{i} inner LN goes astray v{j}')
                    else: F.append(f'INFO m{i} inner LN falls to 5th')
        # V -> vi/VI: 3rd of vi/VI doubled
        if a['base'] in ('V', 'V7') and b['base'] in ('vi', 'VI') and [m % 12 for m in N].count(b['third']) != 2: F.append(f'INFO m{i} {b["fig"]} after V without doubled 3rd')
        # chordal 7th falls by step (unless the chord repeats)
        if a['sev'] is not None and rns[i] != rns[i + 1]:
            for j in range(4):
                if P[j] % 12 == a['sev'] and P[j] - N[j] not in (1, 2): F.append(f'm{i} 7th not resolved down v{j}')
        # secondary LN rises
        if a['sec']:
            for j in range(4):
                if P[j] % 12 == a['third'] and N[j] - P[j] != 1: F.append(f'm{i} secondary LN not rising v{j}')
        # cadential 6/4 -> V: 6th and 4th above bass fall by step
        if a['inv'] == 2 and a['base'] in ('I', 'i') and b['base'] in ('V', 'V7'):
            for j in (1, 2, 3):
                if P[j] % 12 in (a['third'], a['root']) and P[j] - N[j] not in (1, 2) and not (b['sev'] is not None and N[j] % 12 == b['sev'] and P[j] % 12 == a['root'] and N[j] == P[j]):
                    F.append(f'm{i} cad 6/4 upper voice does not fall by step v{j}')
                # (do held to become the 7th of V7 is the standard I64-V7 exception)
        # V -> V7 same bass: fine. 6/4 bass approach/leave: the cadential 6/4 bass must stay for V
        if a['inv'] == 2 and N[0] != P[0] and b['base'] in ('V', 'V7'): F.append(f'm{i} cad 6/4 bass moves')
    return F
rep = {}
for l in (2, 3):
    pool = D[f'pool{l}']; seen = {}; C = collections.Counter(); ex = {}; inf = collections.Counter(); W = collections.defaultdict(float)
    for e in pool:
        key = (e['t'], e['k'], e['md'], json.dumps(e['ch']))
        if key in seen: continue
        f = check(e['t'], e['k'], e['md'], e['ch']); seen[key] = f
        for x in f:
            tag = ' '.join(x.split()[1:3]) if not x.startswith('INFO') else ' '.join(x.split()[2:5])
            if x.startswith('INFO'): inf[tag] += 1
            else: C[tag] += 1; ex.setdefault(tag, (e['t'], e['k'], e['md'], e['ch'], x))
    # also every generated item
    gbad = sum(1 for q in D[f'gen{l}'] if any(not x.startswith('INFO') for x in check(q['t'], q['k'], q['md'], q['ch'])))
    rep[l] = {'distinct realisations': len(seen), 'faulty': sum(1 for f in seen.values() if any(not x.startswith('INFO') for x in f)),
              'faults': dict(C), 'examples': {k: str(v) for k, v in ex.items()}, 'info': dict(inf), 'generated items checked': len(D[f'gen{l}']), 'generated faulty': gbad}
    print(l, json.dumps(rep[l], indent=1))
json.dump(rep, open('/tmp/icreg/vl.json', 'w'), indent=1)
