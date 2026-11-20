"""IC_REG_049 probe C7: the counterpoint checker's spelled interval names (c2IvA) against music21 for every ordered pair of
pitches C2-B6 with double flat .. double sharp (175 pitches, 30,625 pairs), plus c2Span/c2Bars/c2PerfPair outputs."""
import asyncio, json, sys, pathlib, collections, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import pitch, interval
REPO = pathlib.Path(__file__).resolve().parents[4]
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(); await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html'); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""()=>{const P=[];for(let dn=14;dn<49;dn++)for(const a of [-2,-1,0,1,2])P.push(c2Pitch(dn,a));const o=[];
          for(const x of P)for(const y of P){const iv=c2Iv(x,y);o.push([x.dn,x.acc,y.dn,y.acc,iv.q,iv.gen,c2IvA(iv)])}
          return{o,span:[8,9,10,11,12,13,15,16,17,18,22].map(g=>c2Art(c2Span(g))),bars:[c2Bars(9,9),c2Bars(8,9)],
           pp:[[1,8],[8,1],[1,1],[8,8],[8,15],[5,5],[12,5]].map(([g0,g1])=>c2PerfPair({gen:g0,pc:g0%7===5?'5':'8'},{gen:g1,pc:g1%7===5?'5':'8'}))}}""")
        await b.close(); return r
R = asyncio.run(main())
L = 'CDEFGAB'
def m21(dn, acc):
    return pitch.Pitch(L[dn % 7] + {-2: '--', -1: '-', 0: '', 1: '#', 2: '##'}[acc] + str(dn // 7))
ORD = {'Unison': 1, 'Second': 2, 'Third': 3, 'Fourth': 4, 'Fifth': 5, 'Sixth': 6, 'Seventh': 7, 'Octave': 8, 'Ninth': 9, 'Tenth': 10, 'Eleventh': 11, 'Twelfth': 12, 'Thirteenth': 13, 'Fourteenth': 14, 'Fifteenth': 15}
def ordn(n): return f'{n}' + ('th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))
def expect(x, y):
    a, b = m21(*x), m21(*y)
    lo, hi = (a, b) if (a.ps < b.ps or (a.ps == b.ps and a.diatonicNoteNum <= b.diatonicNoteNum)) else (b, a)
    try: iv = interval.Interval(noteStart=lo, noteEnd=hi)
    except Exception: return None  # music21 has no name beyond quadruply altered
    q = iv.diatonic.specifier.niceName.lower()  # e.g. 'doubly-augmented'
    g = abs(iv.generic.directed); g = g if g >= 1 else 1
    if iv.generic.directed < 0: g = abs(iv.generic.directed)  # letters cross (E# up to Fb): music21 calls it descending
    base = 'unison' if g == 1 else 'octave' if g == 8 else 'double octave' if g == 15 else ordn(g)
    name = (base if q == 'perfect' and g in (1, 8, 15) else q.replace('-', ' ') + ' ' + base)
    return ('an ' if re.match(r'^(augmented|octave|8|11|18)', name) else 'a ') + name
bad = collections.Counter(); ex = {}; NA = []
n = 0
for dn1, a1, dn2, a2, q, gen, name in R['o']:
    e = expect((dn1, a1), (dn2, a2)); n += 1
    if e is None:
        bad[('music21 n/a', re.sub(r'\d+', 'N', name))] += 0; NA.append(name); continue
    if e != name:
        k = (re.sub(r'\d+', 'N', e), re.sub(r'\d+', 'N', name)); bad[k] += 1; ex.setdefault(k, ((dn1, a1, dn2, a2), e, name))
print('beyond music21 (5-fold+):', len(NA), collections.Counter(re.sub(r' \S+$', '', x[2:]) for x in NA).most_common(6)); print('pairs', n, 'mismatches', sum(bad.values()))
for k, c in bad.most_common(20):
    if k in ex: print(c, ex[k])
print('quality strings used:', collections.Counter(re.sub(r' \S+$', '', x[6][2:].strip()) for x in R['o']).most_common(30))
print('span', R['span']); print('bars', R['bars']); print('perfpair', R['pp'])
json.dump({'n': n, 'mismatch': sum(bad.values()), 'examples': {str(k): str(v) for k, v in ex.items()}, 'span': R['span'], 'bars': R['bars'], 'pp': R['pp']}, open('/tmp/icreg/c7.json', 'w'), indent=1)
