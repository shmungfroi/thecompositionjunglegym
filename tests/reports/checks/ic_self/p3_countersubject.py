"""IC_SELF_048 probe 6: climb 13 countersubject labels and the IC1 note, against this checker's own interval arithmetic (music21).
Run: python3 tests/reports/checks/ic_self/p3_countersubject.py <repo> [n per context]
Fuzz: random subjects and countersubjects (degrees, holds, rests) in C major, A minor, G minor, F# minor and D Dorian, plus fixed cases.
For every pair issue (I1/IC1/I2/I3/I4) of c13CSCheck (answer issues and CS1 excluded):
  - the register word (above / below / on the same note as) agrees with the sounding pitches of that position;
  - an interval named in the message is the music21 interval between the two sounding pitches;
  - IC1 <=> inverted position, strong beat, both notes struck, a perfect 4th / 11th by music21 that was a perfect 5th / 12th as written;
  - the "was a 5th before the voices swapped" note appears exactly on IC1 issues, never on I2."""
import sys, asyncio, json, pathlib, collections, re, random
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
N = int(sys.argv[2]) if len(sys.argv) > 2 else 1500
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import interval as m21i, pitch as m21p

QN = {'P': 'perfect', 'M': 'major', 'm': 'minor', 'A': 'augmented', 'd': 'diminished', 'AA': 'doubly altered', 'dd': 'doubly altered'}
def ordn(n): return f"{n}{'th' if 11 <= n % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')}"
def phrase(name):
    q, g = re.match(r'([A-Za-z]+)(\d+)', name).groups(); g = int(g)
    base = 'unison' if g == 1 else 'octave' if g == 8 else 'double octave' if g == 15 else ordn(g)
    return base if (q == 'P' and g in (1, 8, 15)) else QN[q] + ' ' + base
def m21pitch(t):  # app name like 'F#', octave
    return m21p.Pitch(t['name'].replace('b', '-') + str(t['oct']))
def iv(a, b):
    pa, pb = m21pitch(a), m21pitch(b)
    lo, hi = (pa, pb) if (pa.ps < pb.ps or (pa.ps == pb.ps and pa.diatonicNoteNum <= pb.diatonicNoteNum)) else (pb, pa)
    return m21i.Interval(lo, hi).name

JS = r"""([cases])=>{const out=[];const CT={cmaj:{modal:false,key:{k:0,mode:'maj'}},amin:{modal:false,key:{k:9,mode:'min'}},gmin:{modal:false,key:{k:7,mode:'min'}},fsmin:{modal:false,key:{k:6,mode:'min'}}};
 const M=c2Mode('dor');CT.dor={modal:true,M,fin:c2Fin(M)};
 const P=p=>p?{name:p.name,oct:p.oct,midi:p.midi,on:p.on!==false}:null;
 for(const [ctxn,sub,cs] of cases){const ctx=CT[ctxn];let iss;try{iss=c13CSCheck(sub,cs,ctx)}catch(e){out.push({ctxn,sub,cs,err:String(e)});continue}
  out.push({ctxn,sub,cs,S:c13Line(sub,ctx).map(P),C2:c13Line(cs,ctx).map(P),C:c13Line(cs,ctx,-7).map(P),iss:iss.map(x=>({code:x.code,sev:x.sev,cells:x.cells,msg:x.msg,pos:x.pos,iv:x.iv?x.iv.name:null}))})}
 return out}"""

def fixed():
    # (ctx, subject, countersubject, label); 8 cells, beats 1 and 3 (cells 0, 2, 4, 6) strong
    F = []
    F.append(('cmaj', [0, 1, 2, 3, 4, 3, 2, 0], [4, 3, 6, 5, 6, 5, 4, 2], 'P5 above on strong beats (C4-G4 at cell 0)'))
    F.append(('cmaj', [0, 1, 2, 3, 4, 3, 2, 0], [3, 'h', 5, 'h', 7, 'h', 4, 'h'], 'P4 / A4 written'))
    F.append(('cmaj', [3, 'h', 3, 'h', 6, 'h', 6, 'h'], [6, 'h', 7, 'h', 9, 'h', 10, 'h'], 'A4 F-B / d5 B-F'))
    F.append(('cmaj', [0, 'h', 0, 'h', 0, 'h', 0, 'h'], [10, 'h', 11, 'h', 9, 'h', 7, 'h'], 'P11 / P12 above'))
    F.append(('cmaj', [4, 'h', 4, 'h', 4, 'h', 4, 'h'], [0, 'h', -3, 'h', 1, 'h', 0, 'h'], 'CS written below'))
    F.append(('cmaj', [0, 1, 2, 3, 4, 5, 4, 3], [2, 4, 4, 1, 6, 0, 6, 5], 'weak-beat dissonances'))
    F.append(('amin', [5, 'h', 6, 'h', 7, 'h', 0, 'h'], [6, 'h', 5, 'h', 6, 'h', 7, 'h'], 'minor: le / si'))
    F.append(('amin', [6, 7, 5, 'h', 6, 0, 0, 'h'], [6, 7, 13, 'h', 13, 7, 7, 'h'], 'minor: A1 / A8 / d7 / A2'))
    F.append(('amin', [-1, 0, 5, 'h', -1, 0, 6, 0], [5, 'h', -1, 0, 6, 'h', 12, 'h'], 'minor: A2 / d7'))
    return F

def fuzz(n, seed=11):
    R = random.Random(seed); out = []
    for ctxn in ('cmaj', 'amin', 'gmin', 'fsmin', 'dor'):
        for _ in range(n):
            L = R.choice([8, 12, 16])
            sub = []; cs = []
            for i in range(L):
                sub.append(R.choice([R.randint(-3, 8)] * 6 + ['h'] + ([None] if R.random() < .05 else [])) if i else R.choice([0, 4]))
                cs.append(R.choice([R.randint(-3, 13)] * 6 + ['h', None]) if i else R.randint(-3, 13))
            out.append((ctxn, sub, cs, 'fuzz'))
    return out

async def main():
    cases = fixed() + fuzz(N)
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#climbs/13'); await pg.wait_for_timeout(1500)
        res = []
        for i in range(0, len(cases), 500):
            res += await pg.evaluate(JS, [[c[:3] for c in cases[i:i + 500]]])
        await b.close()
    bad = collections.Counter(); ex = collections.defaultdict(list); seen = collections.Counter(); ic1 = 0; ic1_exp = 0
    fixed_out = []
    for c, r in zip(cases, res):
        if 'err' in r: bad['exception'] += 1; ex['exception'].append(r); continue
        for x in r['iss']:
            if x['code'] == 'CS1' or x['msg'].startswith('CS with the'): continue
            i = x['cells'][0]; inv = x['pos'] == 'inverted'
            lo_line, hi_line = (r['S'], r['C']) if inv else (r['C2'], r['S'])
            a, s = (r['C'][i], r['S'][i]) if inv else (r['C2'][i], r['S'][i])
            # register word
            want = 'above' if a['midi'] > s['midi'] else 'below' if a['midi'] < s['midi'] else 'on the same note as'
            pref = (f'CS an octave lower, {want} the subject: ' if inv else f'CS {want} the subject: ')
            if not x['msg'].startswith(pref):
                bad['register word'] += 1; ex['register word'].append((x['msg'][:90], want, x['pos']))
            if x['code'] in ('I1', 'IC1', 'I2'):
                nm = iv(a, s); seen[(r['ctxn'][-3:], nm)] += 1
                ph = phrase(nm); art = 'an' if re.match(r'(augmented|octave|8th|11th|18th)', ph) else 'a'
                if not re.search(r'\b' + art + ' ' + re.escape(ph) + r'\b', x['msg']):
                    bad['interval name'] += 1; ex['interval name'].append((x['msg'], nm))
                # where the message prints the two pitches, they are the sounding pitches
                m = re.search(r': (\S+) against (\S+) is', x['msg'])
                if m:
                    t = lambda q: q['name'].replace('#', '♯').replace('b', '♭') + str(q['oct'])
                    p1, p2 = (s, a) if inv else (a, s)
                    if (m.group(1), m.group(2)) != (t(p1).replace('B♭', 'B♭'), t(p2)):
                        # letter 'b' in note name B must not be turned into a flat
                        tt = lambda q: q['name'][0] + q['name'][1:].replace('#', '♯').replace('b', '♭') + str(q['oct'])
                        if (m.group(1), m.group(2)) != (tt(p1), tt(p2)):
                            bad['pitch names'] += 1; ex['pitch names'].append((x['msg'][:120], tt(p1), tt(p2)))
            # IC1 rule
            strong = i % 2 == 0
            exp = False
            if inv and strong and a['on'] and s['on'] and x['code'] in ('I1', 'IC1'):
                nm = iv(a, s); w = iv(r['C2'][i], r['S'][i]) if r['C2'][i] else None
                exp = nm in ('P4', 'P11') and w in ('P5', 'P12')
            ic1_exp += exp; ic1 += x['code'] == 'IC1'
            if (x['code'] == 'IC1') != exp:
                bad['IC1 rule'] += 1; ex['IC1 rule'].append((x['code'], x['msg'][:140]))
            note = 'was a 5th before the voices swapped' in x['msg']
            if note != (x['code'] == 'IC1'):
                bad['note placement'] += 1; ex['note placement'].append((x['code'], x['msg'][:160]))
        if c[3] != 'fuzz':
            fixed_out.append({'case': c[3], 'ctx': c[0], 'issues': [f"{x['code']} [{x['pos']}] {x['msg']}" for x in r['iss'] if x['code'] != 'CS1']})
    rep = {'cases': len(cases), 'pageerrors': errs, 'bad': dict(bad), 'examples': {k: v[:4] for k, v in ex.items()},
           'IC1 issued': ic1, 'IC1 expected': ic1_exp,
           'intervals seen (mode, m21)': {f'{k[0]} {k[1]}': v for k, v in sorted(seen.items())}, 'fixed': fixed_out}
    print(json.dumps(rep, indent=1, ensure_ascii=False))

asyncio.run(main())
