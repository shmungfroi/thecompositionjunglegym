"""R17 (0.48): Analysis score ids and cadence anchors. No browser; needs verovio==6.4.1 (as scores/src/engrave.py).
Run: python3 tests/score_ids_test.py <repo dir>

ids     In the three chorale engravings (closed score, satb2gs) every note carries the id of its own voice: on the upper
        staff layer 1 is the soprano (Humdrum field 4) and layer 2 the alto (field 3); on the lower staff layer 1 is the
        tenor (field 2) and layer 2 the bass (field 1). Before R17 six tenor-bass unisons had their ids swapped.
anchor  Every cadence's anchor note starts exactly when the cadence arrives (meta.json "a", to 2 ms), so the cadence tag
        and the blind-analysis excerpt hang on the arrival chord. Before R17 three K. 331 Var. III anchors sat
        208-625 ms late (on a later note of the arrival bar's figuration).
"""
import sys, json, pathlib, re
import xml.etree.ElementTree as ET

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(REPO / 'scores' / 'src'))
import engrave  # noqa: E402

NS = '{http://www.w3.org/2000/svg}'
FIELD = {(0, 0): '4', (0, 1): '3', (1, 0): '2', (1, 1): '1'}
fails, n = [], {'note ids checked': 0, 'cadence anchors checked': 0}
meta = json.loads((REPO / 'scores' / 'meta.json').read_text())

# ---- ids ----
for key in sorted(engrave.CHORALES):
    for suf in ['', '.t', '.p']:
        root = ET.parse(REPO / 'scores' / f'{key}{suf}.svg').getroot()
        for me in root.iter(NS + 'g'):
            if me.get('data-class') != 'measure':
                continue
            staves = [g for g in me if g.get('data-class') == 'staff']
            for si, st in enumerate(staves):
                layers = [g for g in st if g.get('data-class') == 'layer']
                for li, ly in enumerate(layers):
                    for nt in ly.iter(NS + 'g'):
                        if nt.get('data-class') != 'note':
                            continue
                        nid = nt.get('data-id')
                        n['note ids checked'] += 1
                        want = FIELD.get((si, li))
                        got = re.search(r'F(\d)', nid).group(1)
                        if got != want:
                            fails.append(f'ids {key}{suf}: {nid} sits in staff {si + 1} layer {li + 1} (field {want} expected)')

# ---- anchors ----
for key, m in meta.items():
    if not m['cads']:
        continue
    raw = engrave.prep(key, (engrave.HERE / engrave.SRC[key]).read_text())
    nt = engrave.note_table(engrave.toolkit({'xmlIdSeed': 1}, raw))
    onsets = sorted({v[0] for v in nt.values()})
    for c in m['cads']:
        n['cadence anchors checked'] += 1
        if c['id'] not in nt:
            fails.append(f"anchor {key}: {c['id']} is not a sounding note")
            continue
        on = nt[c['id']][0]
        if abs(on - c['a']) > 2:
            fails.append(f"anchor {key} {c.get('bar', '')} {c['ch']}: anchor {c['id']} starts at {on} ms, the cadence arrives at {c['a']} ms ({on - c['a']:+d} ms)")
        if not any(abs(o - c['a']) <= 2 for o in onsets):
            fails.append(f"anchor {key} {c['ch']}: no note starts at the arrival time {c['a']} ms")

print(json.dumps({'counts': n, 'failures': len(fails)}, indent=1))
for f in fails:
    print('FAIL', f)
sys.exit(1 if fails else 0)
