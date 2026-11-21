"""Ear Lab test (register 0.46, items E1–E15).
Run: python3 tests/earlab_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

The app generates the questions; this file re-derives what they should be, independently, with music21 and its own
voice-leading rules, and fails on any mismatch. It does not call the app's own checker to decide a pass, except where
the register asks for it ("passes the existing SATB checker"), and then it checks with its own rules as well.

Sections
  A  cadence models: every template x key x level  (E8, E9, E10)
  B  bass and numerals: every progression x key x level; 6,000 generated questions against the allow-list (E8, E9, E11);
     BHL 0.48 (IC_EAR_048 S3): no cadence model, bass progression or generated question moves ii(6) to IV or ii°(6) to iv
  C  tells: no answer predictable above chance from length, tempo or register (E10); 0.49 C3: exact-semitone register tells at rungs 2-3;
     0.49 C33: the spacing pattern of every chord and the final chord's completeness at rungs 1-3; C32: the close/open boundary
  D  pool sizes at level 1 (E11); 0.49 C4 / C23: the rung 1 V–vi pool (open or close spacing, >= 100) against an independent
     exhaustive enumeration; C12: no incomplete chord at rung 1
  A  (also) 0.49 C25: no major triad in first inversion doubles its 3rd or drops its 5th (vi / VI excepted), in every cadence and
     bass realisation checked by vl_check; C34: no root-position triad doubles its 3rd with no 5th
  E  blind analysis windows, labels and buttons (E1–E5)
  F  blind playback note lengths (E6)
  G  ranges (E14)
  H  text (E7, E12)
  I  every drill at every level renders and marks without page errors
  J  fixtures from the independent checker (tests/fixtures/earlab_ic.json), when present
"""
import sys, asyncio, json, pathlib, collections, random

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import roman, key as m21key, pitch as m21pitch

FAIL = collections.defaultdict(list)
COUNT = collections.Counter()
def fail(sec, msg):
    FAIL[sec].append(msg)

NM = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']
TON = ['C', 'D-', 'D', 'E-', 'E', 'F', 'F#', 'G', 'A-', 'A', 'B-', 'B']


def m21key_of(k, mode):
    t = TON[k % 12]
    if mode == 'min':
        t = {'D-': 'C#', 'A-': 'G#'}.get(t, t)
        return m21key.Key(t.lower())
    return m21key.Key(t)


def figure(tok):
    """'ii°:1' -> 'iio6', 'I:2' -> 'I64', 'V7' -> 'V7', 'V7/V' -> 'V7/V'"""
    rn, _, inv = tok.partition(':')
    rn = rn.replace('°', 'o')
    if inv in ('1', '2'):
        if '7' in rn:
            rn = rn.replace('7', {'1': '65', '2': '43'}[inv], 1)
        else:
            base, slash, sec = rn.partition('/')
            rn = base + {'1': '6', '2': '64'}[inv] + slash + sec
    return rn


def rn_info(tok, k, mode):
    r = roman.RomanNumeral(figure(tok), m21key_of(k, mode))
    pcs = {p.pitchClass for p in r.pitches}
    sev = r.seventh.pitchClass if r.seventh is not None else None
    third = r.third.pitchClass if r.third is not None else None
    return dict(pcs=pcs, root=r.root().pitchClass, bass=r.bass().pitchClass, third=third, seventh=sev,
                scale_degree=r.scaleDegree, secondary=r.secondaryRomanNumeral is not None, figure=r.figure,
                major_triad=r.isMajorTriad(), inversion=r.inversion(), fifth=r.fifth.pitchClass if r.fifth is not None else None)


PERFECT = {0: 'P1', 7: 'P5'}


def dbl_check(chs, toks, info, where, sec):
    """0.49 C25 (IC_REG_049 S1): a major triad in first inversion (music21's reading) is complete and doubles its root or 5th, never its
    3rd; vi / VI (which double the 3rd after V) are the one exception."""
    for i, (c, f) in enumerate(zip(chs, info)):
        base = toks[i].split(':')[0].split('/')[0]
        if f['major_triad'] and f['inversion'] == 1 and base not in ('vi', 'VI'):
            COUNT[f'C25 doubling check ({sec}): major first-inversion chords checked'] += 1
            if sum(1 for m in c if m % 12 == f['third']) > 1:
                fail(sec, f'{where}: chord {i+1} {toks[i]} doubles its 3rd ({c})')
            if f['fifth'] not in {m % 12 for m in c}:
                fail(sec, f'{where}: chord {i+1} {toks[i]} has no 5th ({c})')
        # 0.49 C34 (IC_C_ENG_049 S4, L108): no triad in root position (IV, vi, III, VI, a final I or i ...) doubles its 3rd and leaves out
        # its 5th; vi / VI after V double the 3rd but keep the 5th
        if f['seventh'] is None and f['inversion'] == 0 and f['third'] is not None and f['fifth'] is not None:
            COUNT[f'C34 doubling check ({sec}): root-position triads checked'] += 1
            if sum(1 for m in c if m % 12 == f['third']) > 1 and f['fifth'] not in {m % 12 for m in c}:
                fail(sec, f'{where}: chord {i+1} {toks[i]} doubles its 3rd and has no 5th ({c})')


def vl_check(chs, toks, k, mode, where):
    """Independent strict-SATB rules. chs: list of [B,T,A,S] MIDI numbers."""
    tonic = k % 12
    lt = (tonic + 11) % 12
    info = [rn_info(t, k, mode) for t in toks]
    RANGES = [(40, 60), (48, 67), (55, 74), (60, 79)]
    for i, (c, f) in enumerate(zip(chs, info)):
        pcs = {m % 12 for m in c}
        if not pcs <= f['pcs']:
            fail('A', f'{where}: chord {i+1} {toks[i]} has {sorted(NM[p] for p in pcs - f["pcs"])} not in {f["figure"]}')
        need = {f['root'], f['third']} | ({f['seventh']} if f['seventh'] is not None else set())
        if not need <= pcs:
            fail('A', f'{where}: chord {i+1} {toks[i]} is missing root, 3rd or 7th')
        if c[0] % 12 != f['bass']:
            fail('A', f'{where}: chord {i+1} {toks[i]} bass {NM[c[0]%12]} should be {NM[f["bass"]]}')
        for v, (lo, hi) in enumerate(RANGES):
            if not lo <= c[v] <= hi:
                fail('G', f'{where}: chord {i+1} voice {v} {c[v]} outside {lo}-{hi}')
        if any(c[v] > c[v+1] for v in range(3)):
            fail('A', f'{where}: chord {i+1} voices cross')
        if c[3] - c[2] > 12 or c[2] - c[1] > 12:
            fail('A', f'{where}: chord {i+1} upper voices more than an octave apart')
    dbl_check(chs, toks, info, where, 'A')
    for i in range(len(chs) - 1):
        P, N, f0, f1 = chs[i], chs[i+1], info[i], info[i+1]
        for a in range(4):
            for b in range(a + 1, 4):
                i0, i1 = (P[b] - P[a]) % 12, (N[b] - N[a]) % 12
                da, db = N[a] - P[a], N[b] - P[b]
                if i0 in PERFECT and i0 == i1 and (da or db) and da != 0 and db != 0:
                    fail('A', f'{where}: consecutive {PERFECT[i0]} voices {a},{b} chords {i+1}-{i+2}')
        # 7ths fall by step
        if f0['seventh'] is not None:
            for v in range(4):
                if P[v] % 12 == f0['seventh'] and N[v] - P[v] not in (-1, -2):
                    fail('A', f'{where}: 7th of {toks[i]} in voice {v} moves {N[v]-P[v]}')
        # leading note rises in the outer voices at V(7) -> I / i / vi / VI
        dom = f0['scale_degree'] == 5 and not f0['secondary']
        if dom and f1['scale_degree'] in (1, 6) and not f1['secondary']:
            for v in (0, 3):
                if P[v] % 12 == lt and N[v] - P[v] != 1:
                    fail('A', f'{where}: leading note in voice {v} does not rise ({toks[i]}-{toks[i+1]})')
            if f1['scale_degree'] == 6:
                if sum(1 for m in N if m % 12 == f1['third']) != 2:
                    fail('A', f'{where}: {toks[i+1]} after V does not double its 3rd')
        # no augmented 2nds: a 3-semitone move between adjacent letter names (le <-> ti in minor; any spelled aug 2nd)
        for v in range(4):
            if abs(N[v] - P[v]) == 3 and mode == 'min' and {P[v] % 12, N[v] % 12} == {(tonic + 8) % 12, lt}:
                fail('A', f'{where}: augmented 2nd in voice {v}')
    return info


def cad_category_ok(cat, toks, k, mode):
    f = [rn_info(t, k, mode) for t in toks[-2:]]
    sd = [x['scale_degree'] for x in f]
    root_pos = toks[-1].find(':') < 0
    if cat == 'perfect':
        return sd == [5, 1] and root_pos and not (len(toks) >= 3 and toks[-3] in ('I:2', 'i:2'))
    if cat == 'plagal':
        return sd == [4, 1] and root_pos
    if cat == 'imperfect':
        return sd[1] == 5 and not f[1]['secondary'] and not (mode == 'min' and toks[-2] == 'iv:1')
    if cat == 'interrupted':
        return sd == [5, 6]
    # R4 (0.48): rung 3 answers of their own
    if cat == 'phrygian':
        return mode == 'min' and toks[-2] == 'iv:1' and sd[1] == 5 and root_pos
    if cat == 'cad64':
        return len(toks) >= 3 and toks[-3] in ('I:2', 'i:2') and sd == [5, 1] and root_pos
    return False


POP = [('V', 'IV'), ('V', 'iv'), ('ii', 'I'), ('ii', 'vi'), ('V7', 'IV')]


def retro_moves(toks):
    """ii(6) -> IV and ii°(6) -> iv: a retrogression in common-practice harmony (the pre-dominant moves forward, IV to ii, ii to V)."""
    base = [t.split(':')[0] for t in toks]
    return [(a, b) for a, b in zip(base, base[1:]) if (a, b) in (('ii', 'IV'), ('ii°', 'iv'))]


def pop_moves(toks):
    # a cadential 6/4 (I:2 / i:2) is a dominant-function chord, so ii6-I6/4 is the textbook approach, not ii-I
    base = [t.split(':')[0] if not t.endswith(':2') else 'cad64' for t in toks]
    return [(a, b) for a, b in zip(base, base[1:]) if (a, b) in POP]


def vvi_enum(k, open_only=True):
    """0.49 C4: every strict four-part V–vi in major key k (independent of the app). Voices B 40-60, T 48-67, A 55-74, S 60-79 (the app's
    ranges), no crossing, S-A and A-T within an octave, open spacing (S-T more than an octave) unless open_only is False. V complete
    with one leading note; vi complete with its 3rd doubled (two do). Every voice: no leap over an octave, of a 7th or a tritone; the
    leading note rises a semitone to do. No parallel or contrary 5ths / octaves / unisons, no overlap, no hidden 5th or octave in the
    outer voices."""
    so, ti, re_, la, do, mi = [(k + x) % 12 for x in (7, 11, 2, 9, 0, 4)]

    def voicings(bass_pc, pcs, ok):
        out = []
        for b in range(40, 61):
            if b % 12 != bass_pc:
                continue
            for t in range(48, 68):
                for a in range(55, 75):
                    for s in range(60, 80):
                        v = (b, t, a, s)
                        if not (b <= t <= a <= s) or any(x % 12 not in pcs for x in v) or s - a > 12 or a - t > 12 or (open_only and s - t <= 12):
                            continue
                        if ok([x % 12 for x in v]):
                            out.append(v)
        return out
    V = voicings(so, {so, ti, re_}, lambda c: c.count(ti) == 1 and set(c) == {so, ti, re_})
    VI = voicings(la, {la, do, mi}, lambda c: set(c) == {la, do, mi} and c.count(do) == 2)
    res = []
    for P in V:
        for N in VI:
            good = all(abs(N[i] - P[i]) <= 12 and abs(N[i] - P[i]) not in (6, 10, 11) and (P[i] % 12 != ti or N[i] - P[i] == 1) for i in range(4))
            for i in range(4):
                for j in range(i + 1, 4):
                    if (P[j] - P[i]) % 12 == (N[j] - N[i]) % 12 and (N[j] - N[i]) % 12 in (0, 7) and P[i] != N[i] and P[j] != N[j]:
                        good = False
            if any(N[i] > P[i + 1] or N[i + 1] < P[i] for i in range(3)):
                good = False
            mb, ms = N[0] - P[0], N[3] - P[3]
            if mb * ms > 0 and (N[3] - N[0]) % 12 in (0, 7):
                good = False
            if good:
                res.append((P, N))
    return res


def predict_acc(rows, feat, ans):
    """Held-out accuracy of the best guess of `ans` from `feat` alone (fit on one half, scored on the other, both ways),
    and chance (the most common answer). Scoring in-sample would flatter any feature with many values."""
    half = [rows[0::2], rows[1::2]]
    hit = 0
    for tr, te in ((half[0], half[1]), (half[1], half[0])):
        by = collections.defaultdict(collections.Counter)
        tot = collections.Counter(ans(r) for r in tr)
        for r in tr:
            by[feat(r)][ans(r)] += 1
        default = tot.most_common(1)[0][0]
        for r in te:
            c = by.get(feat(r))
            hit += (c.most_common(1)[0][0] if c else default) == ans(r)
    tot = collections.Counter(ans(r) for r in rows)
    return hit / len(rows), tot.most_common(1)[0][1] / len(rows)


async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.add_init_script("""(()=>{window.__N=[];for(const P of [AudioScheduledSourceNode.prototype,AudioBufferSourceNode.prototype]){const st=P.start,sp=P.stop;
          P.start=function(t=0,...a){this.__r={s:t||0,e:Infinity,k:this instanceof AudioBufferSourceNode?'smp':'osc'};__N.push(this.__r);return st.call(this,t,...a)};
          P.stop=function(t=0){if(this.__r)this.__r.e=Math.min(this.__r.e,t);return sp.call(this,t)}}})()""")
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1500)

        # ---------------- A: every cadence model x key x level ----------------
        cad = await pg.evaluate("""()=>{const out=[];for(const l of [1,2,3])for(const md of ['maj','min']){const ts=CADT[l][md];if(!ts)continue;
          for(const c in ts)for(const t of ts[c])for(const k of earCadKeys(l,md))for(const reg of [{b:42,s:66},{b:52,s:74},{b:42,s:74},{b:52,s:66},undefined]){const key={k,mode:md},rns=t.split(' '),P=earCadProg(l,rns,key,reg);
            const app=P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation'];
            out.push({l,md,cat:c,t,k,ch:P.ch,app,sub:cadSub(rns)})}}return out}""")
        seen = set()
        for q in cad:
            where = f"cad L{q['l']} {q['md']} {q['cat']} [{q['t']}] key {NM[q['k']]}"
            COUNT['cad realisations'] += 1
            if (q['t'], q['k'], q['md']) not in seen:
                seen.add((q['t'], q['k'], q['md']))
                COUNT['cad distinct template x key'] += 1
            if q['app']:
                fail('A', f'{where}: app SATB checker reports {q["app"]}')
                continue
            toks = q['t'].split()
            vl_check(q['ch'], toks, q['k'], q['md'], where)
            if not cad_category_ok(q['cat'], toks, q['k'], q['md']):
                fail('A', f'{where}: does not end with a {q["cat"]} cadence')
            if pop_moves(toks):
                fail('A', f'{where}: popular-style succession {pop_moves(toks)} in a common-practice model')
            if q['sub'] == 'Phrygian cadence (iv⁶–V)' and not (q['md'] == 'min' and toks[-2] == 'iv:1' and toks[-1] == 'V'):
                fail('A', f'{where}: labelled Phrygian but is not iv6-V in minor')
        # E10: same lengths in every category; at least 3 models per category per mode at L1
        lens = await pg.evaluate("""()=>{const o={};for(const l of [1,2,3])for(const md in CADT[l])for(const c in CADT[l][md])o[`${l}|${md}|${c}`]=CADT[l][md][c].map(x=>x.split(' ').length);return o}""")
        for l in (1, 2, 3):
            for md in ('maj', 'min'):
                sets = {c: set(v) for kk, v in lens.items() for c in [kk.split('|')[2]] if kk.startswith(f'{l}|{md}|')}
                if sets and len({frozenset(s) for s in sets.values()}) != 1:
                    fail('C', f'L{l} {md}: model lengths differ by category {sets}')
        # EL-7 (0.48): rung 1 is exactly the four basic cadences, two chords each (checked in full in earlab_items_test section K)
        want1 = {'1|maj|perfect': 1, '1|maj|plagal': 1, '1|maj|imperfect': 2, '1|maj|interrupted': 1}
        got1 = {kk: len(v) for kk, v in lens.items() if kk.startswith('1|')}
        if got1 != want1 or any(n != 2 for kk, v in lens.items() if kk.startswith('1|') for n in v):
            fail('C', f'rung 1 models are not the four basic two-chord cadences: {got1}')
        if await pg.evaluate("JSON.stringify(CADT[2])===JSON.stringify(CADT[3])"):
            fail('C', 'levels 2 and 3 have the same cadence models')
        l3 = await pg.evaluate("Object.values(CADT[3]).flatMap(o=>Object.values(o).flat()).join('|')")
        if ':2 V' not in l3 or 'iv:1 V' not in l3:
            fail('C', 'level 3 is missing the cadential 6/4 or the Phrygian cadence')

        # ---------------- B: bass and numerals ----------------
        bass = await pg.evaluate("""()=>{const out=[];for(const l of [1,2,3])for(const rns of earBassProgs(l))for(const k of BKEYS)for(const reg of [{b:42,s:66},{b:52,s:74},{b:47,s:70}]){const key={k,mode:'maj'},P=earBassProg(rns,key,reg);
            out.push({l,rns,k,ch:P.ch,app:P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation']})}return out}""")
        for q in bass:
            where = f"bass L{q['l']} [{' '.join(q['rns'])}] key {NM[q['k']]}"
            COUNT['bass realisations'] += 1
            if q['app']:
                fail('B', f'{where}: app SATB checker reports {q["app"]}')
                continue
            info = vl_check(q['ch'], q['rns'], q['k'], 'maj', where)
            for i, f in enumerate(info):
                if q['ch'][i][0] % 12 != f['root']:
                    fail('B', f'{where}: chord {i+1} is not in root position')
        gen = await pg.evaluate("""()=>{let s=11;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o=[];
            for(const l of [1,2,3])for(let i=0;i<2000;i++){const q=earGen('bass',l,R);o.push({l,a:q.a,opts:q.opts,bass:q.bass,ch:q.ch})}return o}""")
        allow = await pg.evaluate("EBALLOW")
        for q in gen:
            COUNT['bass questions (allow-list)'] += 1
            if q['a'][0] != 'I' or any(x not in q['opts'] for x in q['a']):
                fail('B', f"L{q['l']} {q['a']}: outside the level's chords")
            for a, b2 in zip(q['a'], q['a'][1:]):
                if b2 not in allow[a]:
                    fail('B', f"L{q['l']} {q['a']}: {a}-{b2} is not on the common-practice allow-list")
            if pop_moves(q['a']):
                fail('B', f"L{q['l']} {q['a']}: popular-style succession")
            if q['bass'] != [c[0] for c in q['ch']]:
                fail('B', 'bass-only notes are not the bass of the chords')
        gen = await pg.evaluate("""()=>{let s=13;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o=[];
            for(const l of [1,2,3])for(let i=0;i<2000;i++){const q=earGen('cad',l,R);o.push({l,a:q.a,rns:q.rns})}return o}""")
        for q in gen:
            COUNT['cadence questions (allow-list)'] += 1
            if pop_moves(q['rns']):
                fail('B', f"cad L{q['l']} {q['rns']}: popular-style succession")
            if retro_moves(q['rns']):
                fail('B', f"cad L{q['l']} {q['rns']}: retrogression {retro_moves(q['rns'])}")
        # BHL 0.48 (IC_EAR_048 S3): every model and every bass progression, as well as the generated questions above
        allp = await pg.evaluate("[...[1,2,3].flatMap(l=>Object.values(CADT[l]).flatMap(o=>Object.values(o).flat())),...[1,2,3].flatMap(l=>earBassProgs(l).map(p=>p.join(' ')))]")
        COUNT['models and bass progressions checked for ii(6)-IV'] = len(allp)
        for t in allp:
            if retro_moves(t.split()):
                fail('B', f'[{t}]: retrogression {retro_moves(t.split())}')
        for q in [x for x in await pg.evaluate("""()=>{let s=29;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o=[];for(const l of [1,2,3])for(let i=0;i<2000;i++)o.push(earGen('bass',l,R).a);return o}""")]:
            COUNT['bass questions checked for ii(6)-IV'] += 1
            if retro_moves(q):
                fail('B', f'bass {q}: retrogression {retro_moves(q)}')

        # ---------------- C: tells ----------------
        tells = await pg.evaluate("""()=>{let s=17;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o={cad:[],metre:[],qual:[]};
            for(const l of [1,2,3])for(let i=0;i<5000;i++){const c=earGen('cad',l,R);o.cad.push({l,a:c.a,sub:c.sub||'',md:c.key.mode,n:c.ch.length,lo:Math.min(...c.ch.flat()),hi:Math.max(...c.ch.flat()),
                s2:c.rns[1],open:c.ch[0].join(','),fin:c.ch[c.ch.length-1][3],fb:c.ch[0][0],lb:c.ch[c.ch.length-1][0],fs:c.ch[0][3],
                sp:c.ch.map(v=>earClose(v)?'c':'o').join(''),comp:c.ch.every(v=>new Set(v.map(m=>mod(m,12))).size>=3),fcomp:new Set(c.ch[c.ch.length-1].map(m=>mod(m,12))).size>=3,rns:c.rns,k:c.key.k,ch:c.ch});
              const m=earGen('metre',l,R);o.metre.push({l,a:m.a,bpm:m.bpm,comp:/8$/.test(m.a)&&m.a!=='7/8'});
              const q=earGen('qual',l,R);o.qual.push({l,a:q.a,lo:q.notes[0],hi:q.notes[q.notes.length-1]})}return o}""")
        MARGIN = 0.05
        def tell(sec, rows, name, feat, ans, levels=(1, 2, 3)):
            for l in levels:
                rr = [r for r in rows if r['l'] == l]
                acc, ch = predict_acc(rr, feat, ans)
                COUNT['tell checks'] += 1
                if acc > ch + MARGIN:
                    fail('C', f'{sec} L{l}: {name} predicts the answer {acc:.0%} of the time (chance {ch:.0%})')
        tell('cadences', tells['cad'], 'number of chords', lambda r: r['n'], lambda r: r['a'])
        tell('cadences', tells['cad'], 'lowest note (6-semitone bands)', lambda r: r['lo'] // 6, lambda r: r['a'])
        tell('cadences', tells['cad'], 'highest note (6-semitone bands)', lambda r: r['hi'] // 6, lambda r: r['a'])
        # at rung 1 the two chords are the cadence itself, so the second and opening chords are the answer, not a tell;
        # rung 1's register, top-note, bass-note and key tells are in earlab_items_test section K
        tell('cadences', tells['cad'], 'second chord', lambda r: r['s2'], lambda r: r['a'], (2, 3))
        tell('cadences', tells['cad'], 'opening voicing', lambda r: r['open'], lambda r: r['a'], (2, 3))
        # register 0.48 (design spec section 11): mode and phrase length, alone and together, must not give the answer away
        tell('cadences', tells['cad'], 'mode', lambda r: r['md'], lambda r: r['a'])
        tell('cadences', tells['cad'], 'mode and number of chords', lambda r: (r['md'], r['n']), lambda r: r['a'])
        tell('cadences', tells['cad'], 'lowest and highest note (6-semitone bands)', lambda r: (r['lo'] // 6, r['hi'] // 6), lambda r: r['a'])
        # 0.49 C23 / C12 (rung 1): open or close spacing of the first chord, the last chord and both, and the final chord's completeness
        tell('cadences', tells['cad'], 'spacing of the first chord (open or close)', lambda r: r['sp'][0], lambda r: r['a'], (1,))
        tell('cadences', tells['cad'], 'spacing of the last chord (open or close)', lambda r: r['sp'][-1], lambda r: r['a'], (1,))
        # 0.49 C33 (L108): rungs 2 and 3 too (the spacing pattern of every chord was +7.9 / +15.0, the final chord's completeness +9.3 at rung 3)
        tell('cadences', tells['cad'], 'spacing of every chord (open or close)', lambda r: r['sp'], lambda r: r['a'], (1, 2, 3))
        tell('cadences', tells['cad'], 'mode and spacing of every chord', lambda r: (r['md'], r['sp']), lambda r: r['a'], (2, 3))
        tell('cadences', tells['cad'], 'every chord complete', lambda r: r['comp'], lambda r: r['a'], (1,))
        tell('cadences', tells['cad'], 'final chord complete', lambda r: r['fcomp'], lambda r: r['a'], (1, 2, 3))
        tell('cadences', tells['cad'], 'mode and final chord complete', lambda r: (r['md'], r['fcomp']), lambda r: r['a'], (2, 3))
        # 0.49 C32 (L108): close spacing is the soprano LESS than an octave above the tenor (Kostka & Payne); exactly an octave is open.
        # One named constant in the app (EAR_CLOSE_LT); the checks above read the spacing through it
        c32 = await pg.evaluate("({lt:EAR_CLOSE_LT,oct:earClose([48,60,64,72]),c11:earClose([48,60,64,71]),o13:earClose([48,60,67,73])})")
        COUNT['C32 close/open boundary checks'] = 4
        if c32 != {'lt': 12, 'oct': False, 'c11': True, 'o13': False}:
            fail('C', f'C32: close spacing should be soprano less than an octave above the tenor (an exact octave is open): {c32}')
        for l in (1, 2, 3):
            rr = [r for r in tells['cad'] if r['l'] == l]
            acc, ch = predict_acc(rr, lambda r: r['sp'], lambda r: r['a'])
            COUNT[f'info: rung {l} spacing of every chord (open/close): accuracy vs chance'] = f'{acc:.1%} vs {ch:.1%}'
        if any(not r['comp'] for r in tells['cad'] if r['l'] == 1):
            fail('C', 'C12: a rung 1 item has an incomplete chord')
        # 0.49 C25: the doubling check on every generated cadence question (15,000, rungs 1-3)
        _ri = {}
        for r in tells['cad']:
            info = [_ri.setdefault((t, r['k'], r['md']), rn_info(t, r['k'], r['md'])) for t in r['rns']]
            dbl_check(r['ch'], r['rns'], info, f"cad L{r['l']} {r['md']} [{' '.join(r['rns'])}] key {NM[r['k']]}", 'C')
        # 0.49 C3 (IC_EAR2_048 C2): exact-semitone register tells at rungs 2 and 3, alone and with the mode. Before 0.49 the exact lowest and
        # highest note pair predicted the answer 11 (rung 2) and 14 (rung 3) points above chance, and the last bass note 11 (rung 2, 7 keys).
        # Rung 1's are in earlab_items_test section K. The bass and soprano degrees (lowest note as do or so ...) are the cadence, not a tell.
        EX = (('lowest note (exact)', lambda r: r['lo']), ('highest note (exact)', lambda r: r['hi']), ('lowest and highest note (exact pair)', lambda r: (r['lo'], r['hi'])),
              ('span (exact)', lambda r: r['hi'] - r['lo']), ('first bass note (exact)', lambda r: r['fb']), ('last bass note (exact)', lambda r: r['lb']),
              ('first soprano note (exact)', lambda r: r['fs']), ('last soprano note (exact)', lambda r: r['fin']))
        for name, f in EX:
            tell('cadences', tells['cad'], name, f, lambda r: r['a'], (2, 3))
            tell('cadences', tells['cad'], 'mode and ' + name, lambda r, f=f: (r['md'], f(r)), lambda r: r['a'], (2, 3))
        for l in (2, 3):
            rr = [r for r in tells['cad'] if r['l'] == l]
            for name, f in EX[:4]:
                acc, ch = predict_acc(rr, f, lambda r: r['a'])
                COUNT[f'info: rung {l} {name}: accuracy vs chance'] = f'{acc:.1%} vs {ch:.1%}'
        # the balanced table is in place and current (its length matches the index; a stale or missing table falls back to the old draw)
        t23 = await pg.evaluate("({w2:!!earR23Weights(2),w3:!!earR23Weights(3),draw:/earR23Draw\\(l,mode,a,r\\)/.test(earGenCad.toString()),keys2:earCadKeys(2,'maj').length+earCadKeys(2,'min').length,"
                                "nz2:(earR23Weights(2)||[]).filter(x=>x>0).length,nz3:(earR23Weights(3)||[]).filter(x=>x>0).length})")
        COUNT['C3 balanced table (rungs 2, 3): entries with weight > 0'] = f"{t23['nz2']}, {t23['nz3']}"
        if not (t23['w2'] and t23['w3'] and t23['draw'] and t23['keys2'] == 24):
            fail('C', f'C3: EAR23W missing or stale, or rung 2 not on all 24 keys (run tests/gen_cad23_weights.py): {t23}')
        # if rung 3 is marked with the refined answers (Phrygian, cadential 6/4), mode and length are reported against those as well
        for l in (3,):
            rr = [r for r in tells['cad'] if r['l'] == l]
            ref = lambda r: r['a'] + ('|' + r['sub'] if r['sub'] else '')
            for name, feat in (('mode', lambda r: r['md']), ('number of chords', lambda r: r['n']), ('mode and number of chords', lambda r: (r['md'], r['n']))):
                acc, ch = predict_acc(rr, feat, ref)
                COUNT[f'info: rung 3 refined answers, {name}: accuracy vs chance'] = f'{acc:.0%} vs {ch:.0%}'
                if rr and any(r['a'] in ('phrygian', 'cad64') for r in rr) and acc > ch + MARGIN:
                    fail('C', f'cadences L3 (refined answers): {name} predicts the answer {acc:.0%} of the time (chance {ch:.0%})')
        # the two rung 3 models that end interrupted after a cadential 6/4: kept as interrupted models (Justin, 19 Nov 2026; full checks in
        # earlab_items_test section I)
        held = await pg.evaluate("CAD3_HELD.filter(x=>Object.values(CADT[3]).some(o=>(o.interrupted||[]).includes(x)))")
        if len(held) != 2:
            fail('C', f'interrupted-after-6/4 models in the rung 3 interrupted pool: {held}')
        # merge 0.48: one register path for cadence items (earCadReg); 0.48 logic: "Nearly" on, held models in; BHL 0.48: CAD64_INT_NEARLY on
        # (Justin 20 Nov 2026, item B)
        mg = await pg.evaluate("({reg:/earCadReg\\(rns,key,r/.test(earGenCad.toString()),nearly:EAR_NEARLY,hold:CAD3_HOLD,int:CAD64_INT_NEARLY})")
        COUNT['merge checks (earCadReg path, Nearly on, CAD64_INT_NEARLY on, held models in)'] = 4
        if not mg['reg'] or mg['nearly'] is not True or mg['hold'] is not False or mg['int'] is not True:
            fail('C', f'merge: earGenCad register path / Nearly / hold switch / CAD64_INT_NEARLY: {mg}')
        tell('metre', tells['metre'], 'tempo (10-bpm bands)', lambda r: r['bpm'] // 10, lambda r: r['comp'])
        tell('metre', tells['metre'], 'tempo (10-bpm bands)', lambda r: r['bpm'] // 10, lambda r: r['a'])
        tell('chord quality', tells['qual'], 'lowest note (6-semitone bands)', lambda r: r['lo'] // 6, lambda r: r['a'])
        for l in (1, 2, 3):
            bp = [r['bpm'] for r in tells['metre'] if r['l'] == l]
            if min(bp) < 60 or max(bp) > 120 or max(bp) - min(bp) < 50:
                fail('C', f'metre L{l}: tempo range {min(bp)}-{max(bp)} is not 60-120')
        # the second chord must not give the category away (the old level-1 plagal tell)
        for l in (2, 3):
            rr = [r for r in tells['cad'] if r['l'] == l]
            by = collections.defaultdict(set)
            for r in rr:
                by[r['s2']].add(r['a'])
            only = {k: v for k, v in by.items() if len(v) == 1}
            if only:
                fail('C', f'cadences L{l}: second chord {list(only)} occurs in only one category')

        # ---------------- D: pool sizes at level 1 ----------------
        pools = await pg.evaluate("""()=>{let s=19;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};
            const d=(dr,f)=>{const S=new Set();for(let i=0;i<30000;i++){const q=earGen(dr,1,R);if(q)S.add(f(q))}return S.size};
            return{'melodic dictation (solfa sequences)':d('mel',q=>q.a.join(' ')),'chord quality (distinct voicings)':d('qual',q=>q.notes.join(',')),'bass (progression x key)':d('bass',q=>q.a.join(' ')+'|'+q.key.k)}}""")
        for k, v in pools.items():
            COUNT[f'L1 pool: {k}'] = v
            # EL-6 (0.48): chord quality is root position only, close spacing, two registers, so rung 1 (major, minor) has
            # 2 x 12 roots x 2 registers = 48 voicings; the floor there is all 48, not 100
            floor = 48 if k.startswith('chord quality') else 100
            if v < floor:
                fail('D', f'level 1 {k}: {v} distinct items (floor {floor})')
        # 0.49 C4 / C23: rung 1 interrupted cadence (V–vi). Its pool is every strict, complete realisation in the twelve keys, open or close
        # spacing (Justin 21 Nov 2026, L101: close spacing allowed for all five models together); this independent enumeration (strict
        # common-practice rules, below) must find the same set, and every voicing must carry weight. Open spacing only it was 28.
        r1 = await pg.evaluate("()=>({vvi:earR1Pool().filter(p=>earR1Use(p)&&p.t==='V vi').map(p=>p.k+':'+p.ch.map(v=>v.join(',')).join('|')),by:earR1Pool().filter(p=>earR1Use(p)).reduce((o,p)=>(o[p.t]=(o[p.t]||0)+1,o),{}),"
                               "w:Object.fromEntries(Object.entries(earR1Weights()).map(([a,L])=>[a,L.filter(e=>e.w>=1e-4).length])),"
                               "opt:{inc:EARR1OPT.inc,open:EARR1OPT.open},inc:Object.values(earR1Weights()).flat().filter(e=>e.inc).length,"
                               "cl:Object.values(earR1Weights()).flat().filter(e=>e.cl&&e.w>=1e-4).reduce((o,e)=>(o[e.t]=(o[e.t]||0)+1,o),{})})")
        mine = {f"{k}:{','.join(map(str, P))}|{','.join(map(str, N))}" for k in range(12) for P, N in vvi_enum(k, open_only=False)}
        mine_open = sum(len(vvi_enum(k)) for k in range(12))
        COUNT['C23 rung 1 V–vi: app pool / independent enumeration (open or close) / open only'] = f"{len(r1['vvi'])} / {len(mine)} / {mine_open}"
        COUNT['C23 rung 1 pool per model'] = json.dumps(r1['by'])
        COUNT['C23 rung 1 pool entries with weight >= 1e-4 per answer'] = json.dumps(r1['w'])
        COUNT['C23 rung 1 entries in use with a close-spaced chord, per model'] = json.dumps(r1['cl'])
        if set(r1['vvi']) != mine:
            fail('D', f"C23 rung 1 V–vi pool differs from the independent enumeration: app only {sorted(set(r1['vvi']) - mine)[:3]}, enumeration only {sorted(mine - set(r1['vvi']))[:3]}")
        if len(mine) < 100:
            fail('D', f'C23 rung 1 interrupted: {len(mine)} voicings, floor 100')
        if r1['w'].get('interrupted', 0) < len(mine):
            fail('D', f"C23 rung 1 interrupted: only {r1['w'].get('interrupted')} of {len(mine)} voicings carry weight")
        # close spacing for all five models together (never one alone, which would make spacing a tell; the tells are in earlab_items_test K)
        if r1['opt'] != {'inc': False, 'open': False} or any(r1['cl'].get(t, 0) == 0 for t in ('V I', 'IV I', 'I V', 'IV V', 'V vi')):
            fail('D', f"C12 / C23 rung 1 options {r1['opt']}: close-spaced entries in use per model {r1['cl']}")
        # 0.49 C12 (L101, "always use the complete chord"): no rung 1 entry in use is incomplete
        if r1['inc']:
            fail('D', f"C12 rung 1: {r1['inc']} incomplete entries in use")

        # ---------------- E: blind analysis ----------------
        blind = await pg.evaluate("""async()=>{await earLoadBlind();return{items:EAR.blind.map(x=>({...x})),cats:[1,2,3].map(l=>earBlindCats(l)),meta:AN.meta}}""")
        meta = blind['meta']
        items = blind['items']
        expected = sum(1 for k in ['chorale', 'ohaupt', 'jesu', 'k331a', 'k331d', 'chopin7', 'chopin20'] for c in meta[k]['cads'] if c.get('blind') is not False)
        if len(items) != expected or expected != 30:
            fail('E', f'blind pool has {len(items)} items, expected 30 (31 cadences minus O Haupt bar 6)')
        if any(x['score'] == 'ohaupt' and x['bar'] == '6' for x in items):
            fail('E', 'O Haupt bar 6 (V4/3-I with a plagal neighbour) is still in the marked pool')
        for x in items:
            COUNT['blind items checked'] += 1
            m = meta[x['score']]
            tn, md = m['key'].replace('♭', '-').replace('♯', '#').split()
            kk = m21key.Key(tn if md == 'major' else tn.lower())
            last = x['chords'].split('–')[-1].strip().split()[0].replace('64', '')
            r = roman.RomanNumeral(last, kk)
            pcs = {q.pitchClass for q in r.pitches}
            # notes as the app plays them: onset in [s-5, e-5), each cut at e
            ev = [(ms, pp, min(d, x['e'] - ms)) for ms, pp, d in m['events'] if x['s'] - 5 <= ms < x['e'] - 5]
            tend = max(ms + d for ms, pp, d in ev)
            last_snd = {pp % 12 for ms, pp, d in ev if ms < tend - 1 and ms + d >= tend - 30}
            where = f"{x['score']} bar {x['bar']} ({x['chords']})"
            if not last_snd or not last_snd <= pcs or r.root().pitchClass not in last_snd:
                fail('E', f'{where}: last sounding notes {sorted(NM[q] for q in last_snd)} are not the final chord {r.figure} {sorted(NM[q] for q in pcs)}')
            # E2: nothing from the next bar's downbeat or the next phrase
            nxt = [ms for ms, pp, d in m['events'] if ms >= x['e'] - 5 and ms < x['e'] + 5]
            later = [ms for ms, pp, d in ev if ms > x['a'] + 5 and any((pp2 % 12) not in pcs for ms2, pp2, d2 in ev if abs(ms2 - ms) <= 5)]
            if later:
                fail('E', f'{where}: notes outside the cadence chord start after the arrival at {later[:3]}')
            # bar number shown = the bar the cadence arrives in
            arr_bar = [b2 for b2, mid, t0 in m['measures'] if t0 <= x['a'] + 5][-1]
            if arr_bar != x['bar']:
                fail('E', f'{where}: bar shown {x["bar"]}, arrival is in bar {arr_bar}')
        for l, cats in zip((1, 2, 3), blind['cats']):
            for c in cats:
                if not any(x['cat'] == c and x['lvl'] <= l for x in items):
                    fail('E', f'level {l}: button {c} is offered but no item has that answer')
            for c in {x['cat'] for x in items if x['lvl'] <= l}:
                if c not in cats:
                    fail('E', f'level {l}: answer {c} occurs but has no button')
        # E3: the relabelled cadences. 0.48 R8 re-read the chorale cadences from the notes (tests/numeral_reread.py, which
        # generates them): (7) = a passing minor 7th above the root after the chord's onset. Jesu bar 11: alto F♯–E–D♯
        # over F♯ (passing 7th); O Haupt bar 4: alto F♯–E–D over F♯ (passing 7th); Jesu bar 8: no C sounds (the soprano G
        # over D is a 4th anticipating III), so VII – III, as the numeral row names that chord.
        want = {('k331d', 2): 'vii°7/V – V', ('chopin7', 1): 'V7 – I', ('jesu', 4): 'V(7)/V – V', ('jesu', 1): 'V65/V – V', ('ohaupt', 1): 'V(7)/vi – vi',
                ('chorale', 3): 'V7/IV – IV', ('jesu', 3): 'VII – III'}
        for (k, i), ch in want.items():
            if meta[k]['cads'][i]['ch'] != ch:
                fail('E', f'{k} cadence {i+1}: chords "{meta[k]["cads"][i]["ch"]}", expected "{ch}"')
        if 'Picardy' not in meta['jesu']['cads'][5]['t']:
            fail('E', 'Jesu final cadence does not mention the Picardy third')
        if meta['chopin7']['cads'][1].get('bar') not in (None, 15):
            fail('E', 'Chopin 7 final cadence still shows bar %s' % meta['chopin7']['cads'][1].get('bar'))
        if 'cadential 6/4' in meta['chopin7']['cads'][1]['t'] or 'cadential 6/4 to close' in json.dumps(meta['chopin7']['sections'], ensure_ascii=False):
            fail('E', 'Chopin 7 still calls its final cadence a cadential 6/4')
        if 'Befiehl du deine Wege' not in meta['ohaupt']['t']:
            fail('E', 'BWV 244/44 title is not "Befiehl du deine Wege"')

        # ---------------- F: blind playback note lengths ----------------
        await pg.evaluate("ac();loadSamples('piano')")
        await pg.wait_for_timeout(3000)
        ok_smp = await pg.evaluate("!!(SBUF.piano&&Object.keys(SBUF.piano).length)")
        if not ok_smp:
            fail('F', 'piano samples did not load, so note lengths were not tested')
        else:
            for x in items:
                res = await pg.evaluate("""(x)=>{stopAll();__N.length=0;EAR.q={d:'blind',...x,a:x.cat};earPlay();
                    const nodes=__N.map(n=>({s:n.s,e:n.e,k:n.k}));stopAll();return{nodes}}""", x)
                m = meta[x['score']]
                ev = [(ms, min(d, x['e'] - ms) / 1000) for ms, pp, d in m['events'] if x['s'] - 5 <= ms < x['e'] - 5]
                nodes = [n for n in res['nodes'] if n['e'] != float('inf')]
                # the tonic cue sounds first (1.8 s of synth); score notes start after it. A synth fallback note is two oscillators.
                t_first = min(n['s'] for n in nodes)
                score = [n for n in nodes if n['s'] >= t_first + 1.7]
                t0n = min(n['s'] for n in score)
                ms0 = min(max(ms, x['s']) for ms, d in ev)
                onsets = sorted({max(ms, x['s']) - ms0 for ms, d in ev})
                def near(rel):
                    o = min(onsets, key=lambda o: abs(o - rel))
                    return o if abs(o - rel) <= 3 else None
                played = collections.defaultdict(list)
                for n in score:
                    o = near((n['s'] - t0n) * 1000)
                    if o is None:
                        fail('F', f"{x['score']} bar {x['bar']}: a note starts at {(n['s']-t0n):.3f} s where the score has none")
                        continue
                    played[o].append(n['e'] - n['s'])
                written = collections.defaultdict(list)
                for ms, d in ev:
                    written[max(ms, x['s']) - ms0].append(d)
                if set(played) != set(written):
                    fail('F', f"{x['score']} bar {x['bar']}: {len(set(written)-set(played))} written onsets were not played")
                for o, ls in played.items():
                    for h in ls:
                        COUNT['blind note nodes timed'] += 1
                        if h > max(written[o]) + 0.15 + 1e-6:
                            fail('F', f"{x['score']} bar {x['bar']}: a note sounds {h:.2f} s, the longest written note there is {max(written[o]):.2f} s")
        await pg.evaluate("stopAll()")

        # ---------------- G: ranges ----------------
        rng = await pg.evaluate("""()=>{let s=23;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};let mel=99,ql=99,qh=0,bl=99;
            for(const l of [1,2,3])for(let i=0;i<2000;i++){const m=earGen('mel',l,R);mel=Math.min(mel,...m.midi);const q=earGen('qual',l,R);ql=Math.min(ql,q.notes[0]);qh=Math.max(qh,...q.notes);
              const c=earGen('cad',l,R);bl=Math.min(bl,...c.ch.map(x=>x[0]));const b=earGen('bass',l,R);bl=Math.min(bl,...b.ch.map(x=>x[0]))}
            const dos=[0,2,5,7,10,3,9].map(k=>earDo({k,mode:'maj'}).m);return{mel,ql,qh,bl,dos}}""")
        if rng['mel'] < 55:
            fail('G', f"melody reaches MIDI {rng['mel']} (floor G3 = 55)")
        if any(d < 60 for d in rng['dos']):
            fail('G', f"do sits below middle C in a major key: {rng['dos']}")
        if rng['ql'] < 49:
            fail('G', f"chord quality reaches MIDI {rng['ql']} (floor C#3 = 49)")
        if rng['bl'] < 40:
            fail('G', f"bass reaches MIDI {rng['bl']} (floor E2 = 40)")

        # ---------------- H: text ----------------
        txt = await pg.evaluate("""()=>({tip:ELTIPS.blind.map(x=>x.join(' ')).join(' ')+' '+ELTIPNOTE.blind,cadl:CADL,labels:Object.values(AN.meta).flatMap(m=>(m.cads||[]).map(c=>c.t))})""")
        if 'checked independently in music21' in txt['tip'] or 'independent review' not in txt['tip']:
            fail('H', 'the blind-analysis tip still overstates the checking (E7)')
        # 0.48 R6: the answer buttons show the Australian term only; the US term is on hover (title) and in the feedback
        if txt['cadl'] != {'perfect': 'Perfect cadence', 'plagal': 'Plagal cadence', 'imperfect': 'Imperfect cadence', 'interrupted': 'Interrupted cadence'}:
            fail('H', f"cadence buttons are not the Australian term only: {txt['cadl']}")
        for t in txt['labels']:
            if t.lower().startswith('half cadence') or 'authentic' in t.lower() and '(authentic)' not in t.lower():
                fail('H', f'cadence label not NSW-first: "{t}"')

        # ---------------- I: every drill renders and marks ----------------
        for d in ['metre', 'rhy', 'qual', 'cad', 'bass', 'mel', 'blind']:
            for l in (1, 2, 3):
                await pg.evaluate(f"""(async()=>{{EAR.drill='{d}';EAR.lvl['{d}']={l};EAR.q=null;renderEar();if('{d}'==='blind')await earLoadBlind();earNew();
                    stopAll();earMark(false,null);renderEar();stopAll()}})()""")
                await pg.wait_for_timeout(120)
                COUNT['drill x level rendered'] += 1
        if errs:
            fail('I', f'page errors: {errs[:5]}')

        # ---------------- J: independent checker fixtures ----------------
        fx = pathlib.Path(__file__).resolve().parent / 'fixtures' / 'earlab_ic.json'
        if fx.exists():
            F = json.loads(fx.read_text())
            for row in F.get('blind', []):
                x = next((i for i in items if i['score'] == row['score'] and i['bar'] == row['bar']), None)
                COUNT['fixture rows (blind)'] += 1
                if x is None:
                    fail('J', f"fixture {row['score']} bar {row['bar']}: not in the app's pool")
                    continue
                if x['cat'] != row['cat']:
                    fail('J', f"fixture {row['score']} bar {row['bar']}: app says {x['cat']}, checker says {row['cat']}")
                if 'final_pcs' in row:
                    m = meta[x['score']]
                    ev = [(ms, pp, min(d, x['e'] - ms)) for ms, pp, d in m['events'] if x['s'] - 5 <= ms < x['e'] - 5]
                    tend = max(ms + d for ms, pp, d in ev)
                    last_snd = {pp % 12 for ms, pp, d in ev if ms < tend - 1 and ms + d >= tend - 30}
                    if not last_snd <= set(row['final_pcs']):
                        fail('J', f"fixture {row['score']} bar {row['bar']}: final notes {sorted(last_snd)} vs checker {row['final_pcs']}")
            for row in F.get('cadence_pcs', []):
                COUNT['fixture rows (chords)'] += 1
                got = next((q for q in cad if q['t'] == row['t'] and q['k'] == row['k'] and q['md'] == row['md']), None)
                if got is None:
                    # R16 (0.48): rows for retired models were removed (tests/fixtures/make_cadence_pcs.py), so an unmatched row is a failure
                    fail('J', f"fixture {row['t']} key {row['k']} {row['md']}: the app no longer has this model")
                    continue
                if not got['ch']:
                    fail('J', f"fixture {row['t']} key {row['k']}: not generated")
                    continue
                for i, pcs in enumerate(row['pcs']):
                    if not {m % 12 for m in got['ch'][i]} <= set(pcs):
                        fail('J', f"fixture {row['t']} key {row['k']} chord {i+1}: {sorted({m%12 for m in got['ch'][i]})} vs {pcs}")
            # every model x key the app uses has a fixture row
            rows = {(r['t'], r['k'], r['md']) for r in F.get('cadence_pcs', [])}
            miss = sorted({(q['t'], q['k'], q['md']) for q in cad} - rows)
            COUNT['fixture coverage (model x key)'] = f"{len(rows & {(q['t'], q['k'], q['md']) for q in cad})} of {len({(q['t'], q['k'], q['md']) for q in cad})}"
            if miss:
                fail('J', f'{len(miss)} model x key combinations have no fixture row, e.g. {miss[:3]}')
        else:
            fail('J', 'tests/fixtures/earlab_ic.json is missing')
        await b.close()

    report = {'counts': dict(COUNT), 'failures': {k: v[:25] for k, v in FAIL.items()}, 'n_failures': sum(len(v) for v in FAIL.values())}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)

asyncio.run(main())
