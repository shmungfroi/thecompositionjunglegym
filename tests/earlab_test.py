"""Ear Lab test (register 0.46, items E1–E15).
Run: python3 tests/earlab_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

The app generates the questions; this file re-derives what they should be, independently, with music21 and its own
voice-leading rules, and fails on any mismatch. It does not call the app's own checker to decide a pass, except where
the register asks for it ("passes the existing SATB checker"), and then it checks with its own rules as well.

Sections
  A  cadence models: every template x key x level  (E8, E9, E10)
  B  bass and numerals: every progression x key x level; 6,000 generated questions against the allow-list (E8, E9, E11)
  C  tells: no answer predictable above chance from length, tempo or register (E10)
  D  pool sizes at level 1 (E11)
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
                scale_degree=r.scaleDegree, secondary=r.secondaryRomanNumeral is not None, figure=r.figure)


PERFECT = {0: 'P1', 7: 'P5'}


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
        return sd == [5, 1] and root_pos
    if cat == 'plagal':
        return sd == [4, 1] and root_pos
    if cat == 'imperfect':
        return sd[1] == 5 and not f[1]['secondary']
    if cat == 'interrupted':
        return sd == [5, 6]
    return False


POP = [('V', 'IV'), ('V', 'iv'), ('ii', 'I'), ('ii', 'vi'), ('V7', 'IV')]


def pop_moves(toks):
    # a cadential 6/4 (I:2 / i:2) is a dominant-function chord, so ii6-I6/4 is the textbook approach, not ii-I
    base = [t.split(':')[0] if not t.endswith(':2') else 'cad64' for t in toks]
    return [(a, b) for a, b in zip(base, base[1:]) if (a, b) in POP]


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
        bass = await pg.evaluate("""()=>{const out=[];for(const l of [1,2,3])for(const rns of earBassProgs(l))for(const k of BKEYS)for(const reg of [{b:42,s:66},{b:52,s:74},{b:47,s:70}]){const key={k,mode:'maj'},P=earProg(rns,key,reg);
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

        # ---------------- C: tells ----------------
        tells = await pg.evaluate("""()=>{let s=17;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};const o={cad:[],metre:[],qual:[]};
            for(const l of [1,2,3])for(let i=0;i<5000;i++){const c=earGen('cad',l,R);o.cad.push({l,a:c.a,n:c.ch.length,lo:Math.min(...c.ch.flat()),hi:Math.max(...c.ch.flat()),
                s2:c.rns[1],open:c.ch[0].join(','),fin:c.ch[c.ch.length-1][3]});
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
        # E3: the relabelled cadences
        want = {('k331d', 2): 'vii°7/V – V', ('chopin7', 1): 'V7 – I', ('jesu', 4): 'V7/V – V', ('jesu', 1): 'V65/V – V', ('ohaupt', 1): 'V/vi – vi',
                ('chorale', 3): 'V7/IV – IV', ('jesu', 3): 'V/III – III'}
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
        txt = await pg.evaluate("""()=>({tip:earTips('blind'),cadl:CADL,labels:Object.values(AN.meta).flatMap(m=>(m.cads||[]).map(c=>c.t))})""")
        if 'checked independently in music21' in txt['tip'] or 'independent review' not in txt['tip']:
            fail('H', 'the blind-analysis tip still overstates the checking (E7)')
        if txt['cadl'].get('imperfect') != 'Imperfect (half)' or txt['cadl'].get('perfect') != 'Perfect (authentic)':
            fail('H', 'cadence buttons are not NSW-first')
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
                    COUNT['fixture rows (chords) for models since retired'] += 1
                    continue
                if not got['ch']:
                    fail('J', f"fixture {row['t']} key {row['k']}: not generated")
                    continue
                for i, pcs in enumerate(row['pcs']):
                    if not {m % 12 for m in got['ch'][i]} <= set(pcs):
                        fail('J', f"fixture {row['t']} key {row['k']} chord {i+1}: {sorted({m%12 for m in got['ch'][i]})} vs {pcs}")
        else:
            COUNT['fixture rows (none present)'] = 0
        await b.close()

    report = {'counts': dict(COUNT), 'failures': {k: v[:25] for k, v in FAIL.items()}, 'n_failures': sum(len(v) for v in FAIL.values())}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)

asyncio.run(main())
