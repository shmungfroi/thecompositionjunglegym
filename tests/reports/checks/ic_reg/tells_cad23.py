"""IC_REG_049 probe C3a: register tells on cadence rungs 2 and 3.
Exact: from the weighted pools (the draw is: mode, then answer uniform within the mode, then entry by weight).
Empirical: from the seeded generated sample, half to learn the table, half to test (held-out Bayes accuracy).
Gain = accuracy predicting the answer from (mode + feature) minus accuracy from mode alone (chance)."""
import json, collections, random
D = json.load(open('/tmp/icreg/cad23.json'))
def feats(ch):
    x = [m for v in ch for m in v]; lo, hi = min(x), max(x); z = len(ch) - 1
    return {'lo': lo, 'hi': hi, 'lo,hi': (lo, hi), 'span': hi - lo, 'firstB': ch[0][0], 'firstS': ch[0][3],
            'lastB': ch[z][0], 'lastS': ch[z][3], 'open voicing': tuple(ch[0]), 'last chord outer': (ch[z][0], ch[z][3]),
            'last chord voicing': tuple(ch[z]), 'penult outer': (ch[z-1][0], ch[z-1][3]), 'outer lo/hi of last 2': (min(ch[z-1][0], ch[z][0]), max(ch[z-1][3], ch[z][3])),
            'mean pitch (rounded)': round(sum(x) / len(x)), 'n chords': len(ch), 'firstB,lastB': (ch[0][0], ch[z][0]), 'firstS,lastS': (ch[0][3], ch[z][3])}
REG = ['lo', 'hi', 'lo,hi', 'span', 'firstB', 'firstS', 'lastB', 'lastS', 'open voicing', 'last chord outer', 'penult outer', 'outer lo/hi of last 2', 'mean pitch (rounded)', 'firstB,lastB', 'firstS,lastS', 'last chord voicing', 'n chords']
res = {}
for l in (2, 3):
    pool = D[f'pool{l}']; nulls = sum(1 for e in pool if not e['ch'])
    # exact distribution per mode
    tot = collections.defaultdict(float)
    for e in pool:
        if e['ch']: tot[(e['md'], e['a'])] += e['w']
    out = {'null realisations with weight>0': nulls}
    for md in ('maj', 'min'):
        ans = sorted({a for (m, a) in tot if m == md}); n = len(ans)
        row = {}
        for f in REG:
            J = collections.defaultdict(lambda: collections.defaultdict(float))
            for e in pool:
                if e['md'] != md or not e['ch']: continue
                J[feats(e['ch'])[f]][e['a']] += e['w'] / tot[(md, e['a'])] / n
            acc = sum(max(d.values()) for d in J.values())
            # worst single value: largest P(a|x)-1/n among values carrying >=1% of the mass
            worst = max(((max(d.values()) / sum(d.values()) - 1 / n, sum(d.values()), x) for x, d in J.items() if sum(d.values()) >= .01), default=(0, 0, None))
            row[f] = {'gain_pts': round(100 * (acc - 1 / n), 2), 'worst_value': str(worst[2]), 'worst_value_excess_pts': round(100 * worst[0], 1), 'worst_value_mass_pct': round(100 * worst[1], 1)}
        out[md] = {'answers': ans, 'chance_pct': round(100 / n, 1), 'exact': row}
    # empirical held-out on the generated sample
    G = D[f'gen{l}']; random.Random(5).shuffle(G); A, B = G[:len(G)//2], G[len(G)//2:]
    emp = {}
    for f in REG:
        T = collections.defaultdict(collections.Counter); Mo = collections.defaultdict(collections.Counter)
        for q in A: T[(q['md'], feats(q['ch'])[f])][q['a']] += 1; Mo[q['md']][q['a']] += 1
        hit = base = 0
        for q in B:
            c = T.get((q['md'], feats(q['ch'])[f])); p = (c or Mo[q['md']]).most_common(1)[0][0]
            hit += p == q['a']; base += Mo[q['md']].most_common(1)[0][0] == q['a']
        emp[f] = round(100 * (hit - base) / len(B), 2)
    out['empirical_heldout_gain_pts'] = emp
    out['sample answer counts'] = {md: dict(collections.Counter(q['a'] for q in G if q['md'] == md)) for md in ('maj', 'min')}
    out['sample keys'] = {md: len({q['k'] for q in G if q['md'] == md}) for md in ('maj', 'min')}
    out['sample distinct voicings'] = len({json.dumps(q['ch']) for q in G})
    res[l] = out
json.dump(res, open('/tmp/icreg/tells.json', 'w'), indent=1)
for l in (2, 3):
    r = res[l]; print(f'=== rung {l}: nulls {r["null realisations with weight>0"]}, keys {r["sample keys"]}, distinct {r["sample distinct voicings"]}')
    print('answers', r['sample answer counts'])
    for md in ('maj', 'min'):
        print(md, 'chance', r[md]['chance_pct'])
        for f, v in r[md]['exact'].items(): print(f'  {f:24s} exact gain {v["gain_pts"]:6.2f}  worst value {v["worst_value"]} +{v["worst_value_excess_pts"]} (mass {v["worst_value_mass_pct"]}%)')
    print('empirical held-out gain', r['empirical_heldout_gain_pts'])
