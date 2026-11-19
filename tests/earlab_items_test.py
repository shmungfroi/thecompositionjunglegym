"""Ear Lab item generation and scoring (register 0.48: R4, EL-6, EL-7, EL-10, EL-11, R16).
Run: python3 tests/earlab_items_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

The app generates the questions; this file checks them with its own rules (music21 for chord spelling, its own interval
and voice-leading arithmetic), and asks the app's SATB checker only where the register says "passes the SATB checker".

Sections
  Q  EL-6  chord quality: root position only at rungs 1-3, >= 1,000 seeded items per rung, spacing, two registers, register tell,
           augmented and diminished 7th answers name no inversion and say the chord is symmetrical
  K  EL-7  cadences rung 1: four basic cadences, two chords after the key chord, open voicing, SATB checker, balance, tells
  S  R4    cadences rung 3: six answers, family feedback, SATB checker, mode tell, the 6/4 bass motion, >= 100 distinct items per answer
  M  EL-10 stats model (unit) and a scoring flow in the page
  U  EL-11 rung wording, Stage switch, show all, Stage tags, rung change mid-question, page errors at Stages 4, 5, 6
"""
import sys, asyncio, json, pathlib, collections

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import roman, key as m21key, harmony

FAIL = collections.defaultdict(list)
COUNT = collections.Counter()
def fail(sec, msg):
    FAIL[sec].append(msg)

RNG = """(seed)=>{let s=seed;return ()=>{s=(s*16807)%2147483647;return s/2147483647}}"""
NM = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


def predict_acc(rows, feat, ans):
    """Held-out accuracy of the best guess of `ans` from `feat` alone (fit on one half, scored on the other, both ways),
    and chance (the most common answer)."""
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


MARGIN = 0.05
def tell(sec, rows, name, feat, ans, where):
    acc, ch = predict_acc(rows, feat, ans)
    COUNT['tell checks'] += 1
    if acc > ch + MARGIN:
        fail(sec, f'{where}: {name} predicts the answer {acc:.0%} of the time (chance {ch:.0%})')


# chord-symbol suffixes for music21 (independent spelling of the chord the app should play)
M21Q = {'': '', 'm': 'm', 'dim': 'dim', 'aug': '+', 'maj7': 'maj7', '7': '7', 'm7': 'm7', 'm7b5': 'm7b5', 'dim7': 'dim7'}


def sec_Q(qual):
    for l in (1, 2, 3):
        rows = [q for q in qual if q['l'] == l]
        COUNT[f'EL-6 chord quality rung {l} items'] = len(rows)
        if len(rows) < 1000:
            fail('Q', f'rung {l}: only {len(rows)} items checked')
        regs = collections.Counter()
        for q in rows:
            where = f"rung {l} {q['a'] or 'maj'} on {q['root']} {q['notes']}"
            if q['inv'] != 0:
                fail('Q', f'{where}: inversion {q["inv"]}')
            cs = harmony.ChordSymbol(q['root'].replace('b', '-') + M21Q[q['a']])
            want = [p.pitchClass for p in cs.pitches]  # root position, in stacking order
            n = q['notes']
            if [m % 12 for m in n] != want:
                fail('Q', f'{where}: notes {[NM[m % 12] for m in n]} are not {cs.figure} in root position')
            if any(b - a >= 12 or b <= a for a, b in zip(n, n[1:])) or n[-1] - n[0] >= 12:
                fail('Q', f'{where}: not in close position')
            lo = n[0]
            if not (49 <= lo <= 60 or 61 <= lo <= 72):
                fail('Q', f'{where}: lowest note {lo} outside the two registers')
            regs[0 if lo <= 60 else 1] += 1
            txt = q['txt']
            if q['a'] in ('aug', 'dim7'):
                if 'symmetrical' not in txt or any(w in txt for w in ('1st inversion', '2nd inversion', '3rd inversion', 'root position,')):
                    fail('Q', f'{where}: answer text "{txt}" names an inversion or does not say the chord is symmetrical')
            elif 'root position' not in txt:
                fail('Q', f'{where}: answer text "{txt}" does not say root position')
        if min(regs.values()) < len(rows) * .4:
            fail('Q', f'rung {l}: registers unbalanced {dict(regs)}')
        tell('Q', rows, 'lowest note (6-semitone bands)', lambda r: r['notes'][0] // 6, lambda r: r['a'], f'chord quality rung {l}')
        tell('Q', rows, 'lowest note', lambda r: r['notes'][0], lambda r: r['a'], f'chord quality rung {l}')
        tell('Q', rows, 'highest note (6-semitone bands)', lambda r: r['notes'][-1] // 6, lambda r: r['a'], f'chord quality rung {l}')


TON = ['C', 'D-', 'D', 'E-', 'E', 'F', 'F#', 'G', 'A-', 'A', 'B-', 'B']


def m21key_of(k, mode):
    t = TON[k % 12]
    if mode == 'min':
        t = {'D-': 'C#', 'A-': 'G#', 'G-': 'F#'}.get(t, t)
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
    return dict(pcs={p.pitchClass for p in r.pitches}, root=r.root().pitchClass, bass=r.bass().pitchClass,
                third=r.third.pitchClass if r.third is not None else None,
                seventh=r.seventh.pitchClass if r.seventh is not None else None,
                sd=r.scaleDegree, secondary=r.secondaryRomanNumeral is not None, inv=r.inversion(), figure=r.figure)


def vl_errors(chs, toks, k, mode):
    """Independent strict-SATB rules (the same rules as earlab_test section A). chs: list of [B,T,A,S] MIDI numbers."""
    out = []
    tonic = k % 12
    lt = (tonic + 11) % 12
    info = [rn_info(t, k, mode) for t in toks]
    RANGES = [(40, 60), (48, 67), (55, 74), (60, 79)]
    for i, (c, f) in enumerate(zip(chs, info)):
        pcs = {m % 12 for m in c}
        if not pcs <= f['pcs']:
            out.append(f'chord {i+1} {toks[i]} has notes outside {f["figure"]}')
        need = {f['root'], f['third']} | ({f['seventh']} if f['seventh'] is not None else set())
        if not need <= pcs:
            out.append(f'chord {i+1} {toks[i]} is missing its root, 3rd or 7th')
        if c[0] % 12 != f['bass']:
            out.append(f'chord {i+1} {toks[i]} bass {NM[c[0] % 12]} should be {NM[f["bass"]]}')
        for v, (lo, hi) in enumerate(RANGES):
            if not lo <= c[v] <= hi:
                out.append(f'chord {i+1} voice {v} {c[v]} outside {lo}-{hi}')
        if any(c[v] > c[v + 1] for v in range(3)):
            out.append(f'chord {i+1} voices cross')
        if c[3] - c[2] > 12 or c[2] - c[1] > 12:
            out.append(f'chord {i+1} upper voices more than an octave apart')
        if f['sd'] == 5 and not f['secondary'] and sum(1 for m in c if m % 12 == lt) > 1:
            out.append(f'chord {i+1} doubles the leading note')
    for i in range(len(chs) - 1):
        P, N, f0, f1 = chs[i], chs[i + 1], info[i], info[i + 1]
        for a in range(4):
            for b in range(a + 1, 4):
                i0, i1 = (P[b] - P[a]) % 12, (N[b] - N[a]) % 12
                da, db = N[a] - P[a], N[b] - P[b]
                if i0 in (0, 7) and i0 == i1 and da != 0 and db != 0:
                    out.append(f'consecutive {"5ths" if i0 == 7 else "8ves"} voices {a},{b} chords {i+1}-{i+2}')
        if f0['seventh'] is not None:
            for v in range(4):
                if P[v] % 12 == f0['seventh'] and N[v] - P[v] not in (-1, -2):
                    out.append(f'7th of {toks[i]} in voice {v} moves {N[v]-P[v]}')
        dom = f0['sd'] == 5 and not f0['secondary']
        if dom and f1['sd'] in (1, 6) and not f1['secondary']:
            for v in (0, 3):
                if P[v] % 12 == lt and N[v] - P[v] != 1:
                    out.append(f'leading note in voice {v} does not rise ({toks[i]}-{toks[i+1]})')
            if f1['sd'] == 6 and sum(1 for m in N if m % 12 == f1['third']) != 2:
                out.append(f'{toks[i+1]} after V does not double its 3rd')
        # cadential 6/4: the 6th and 4th above the bass fall by step
        if f0['sd'] == 1 and f0['inv'] == 2 and f1['sd'] == 5:
            for v in (1, 2, 3):
                if P[v] % 12 in (f0['root'], f0['third']) and N[v] - P[v] not in (-1, -2) and not (f1['seventh'] is not None and N[v] % 12 == f1['seventh']):
                    out.append(f'cadential 6/4: voice {v} does not fall by step')
        for v in range(4):
            if abs(N[v] - P[v]) == 3 and mode == 'min' and {P[v] % 12, N[v] % 12} == {(tonic + 8) % 12, lt}:
                out.append(f'augmented 2nd in voice {v}')
            if abs(N[v] - P[v]) > 12:
                out.append(f'voice {v} leaps more than an octave')
    return out


def cad_ok(cat, toks, k, mode):
    """Does the progression end with this cadence? (independent of the app; music21 numerals)"""
    f = [rn_info(t, k, mode) for t in toks]
    sd = [x['sd'] for x in f]
    last_root = f[-1]['inv'] == 0
    if cat == 'perfect':
        return sd[-2:] == [5, 1] and last_root and f[-2]['inv'] == 0 and not (len(f) > 2 and sd[-3] == 1 and f[-3]['inv'] == 2)
    if cat == 'plagal':
        return sd[-2:] == [4, 1] and last_root
    if cat == 'imperfect':
        return sd[-1] == 5 and last_root and not f[-1]['secondary'] and not (mode == 'min' and sd[-2] == 4 and f[-2]['inv'] == 1) \
            and not (sd[-2] == 1 and f[-2]['inv'] == 2)
    if cat == 'interrupted':
        return sd[-2:] == [5, 6] and not f[-1]['secondary']
    if cat == 'phrygian':
        return mode == 'min' and toks[-2] == 'iv:1' and sd[-1] == 5 and last_root
    if cat == 'cad64':
        return len(f) >= 3 and sd[-3:] == [1, 5, 1] and f[-3]['inv'] == 2 and f[-2]['inv'] == 0 and last_root
    return False


def sec_K(items, real):
    COUNT['EL-7 rung 1 items'] = len(items)
    if len(items) < 1000:
        fail('K', f'only {len(items)} rung 1 items checked')
    cats = collections.Counter(q['a'] for q in items)
    if set(cats) != {'perfect', 'plagal', 'imperfect', 'interrupted'}:
        fail('K', f'rung 1 answers are {sorted(cats)}, not the four basic cadences')
    for c, n in cats.items():
        COUNT[f'EL-7 rung 1 answer {c}'] = n
        if abs(n / len(items) - .25) > .03:
            fail('K', f'rung 1 answers unbalanced: {dict(cats)}')
    allowed = {'perfect': [['V', 'I']], 'plagal': [['IV', 'I']], 'imperfect': [['I', 'V'], ['IV', 'V']], 'interrupted': [['V', 'vi']]}
    distinct = collections.defaultdict(set)
    for q in items + real:
        where = f"rung 1 {q['a']} [{' '.join(q['rns'])}] in {NM[q['k']]} {q['md']}"
        if q['md'] != 'maj':
            fail('K', f'{where}: not a major key')
        if q['rns'] not in allowed[q['a']]:
            fail('K', f'{where}: not one of the basic models for {q["a"]}')
        if not q['ch'] or len(q['ch']) != 2:
            fail('K', f'{where}: {len(q["ch"] or [])} chords after the key chord, not 2')
            continue
        if not q.get('cue_ok', True):
            fail('K', f'{where}: the key chord does not play first')
        for c in q['ch']:
            if c[3] - c[1] <= 12:
                fail('K', f'{where}: chord {c} is not in open spacing (soprano {c[3]}, tenor {c[1]})')
        if q['app']:
            fail('K', f'{where}: app SATB checker reports {q["app"]}')
        for e in vl_errors(q['ch'], q['rns'], q['k'], 'maj'):
            fail('K', f'{where}: {e}')
        if not cad_ok(q['a'], q['rns'], q['k'], 'maj'):
            fail('K', f'{where}: does not end with a {q["a"]} cadence')
        distinct[q['a']].add((tuple(q['rns']), q['k'], json.dumps(q['ch'])))
    for c, v in distinct.items():
        COUNT[f'EL-7 rung 1 distinct items {c}'] = len(v)
    W = 'cadences rung 1'
    A = lambda r: r['a']
    tell('K', items, 'lowest note (6-semitone bands)', lambda r: min(map(min, r['ch'])) // 6, A, W)
    tell('K', items, 'highest note (6-semitone bands)', lambda r: max(map(max, r['ch'])) // 6, A, W)
    tell('K', items, 'register drawn (bass, soprano)', lambda r: (r['reg']['b'], r['reg']['s']), A, W)
    tell('K', items, 'top note of the first chord', lambda r: r['ch'][0][3], A, W)
    tell('K', items, 'top note of the last chord', lambda r: r['ch'][-1][3], A, W)
    tell('K', items, 'highest top note', lambda r: max(c[3] for c in r['ch']), A, W)
    tell('K', items, 'bass note of the first chord', lambda r: r['ch'][0][0], A, W)
    tell('K', items, 'bass note of the last chord', lambda r: r['ch'][-1][0], A, W)
    tell('K', items, 'lowest bass note', lambda r: min(c[0] for c in r['ch']), A, W)
    tell('K', items, 'key', lambda r: r['k'], A, W)


async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1500)

        # ---------------- Q: EL-6 chord quality ----------------
        qual = await pg.evaluate("""(mk)=>{const R=eval(mk)(29),o=[];for(const l of [1,2,3])for(let i=0;i<1500;i++){const q=earGen('qual',l,R);
            o.push({l,a:q.a,root:q.root,inv:q.inv,notes:q.notes,txt:earAnsTxt(q)})}return o}""", RNG)
        sec_Q(qual)

        # ---------------- K: EL-7 cadences rung 1 ----------------
        k1 = await pg.evaluate("""(mk)=>{const R=eval(mk)(31),o=[];const chk=q=>q.ch?withKey(q.key,()=>checkSATB(q.ch,cadList(q.rns.join(' '),q.key))).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation'];
            for(let i=0;i<2000;i++){const q=earGen('cad',1,R);o.push({a:q.a,rns:q.rns,k:q.key.k,md:q.key.mode,reg:q.reg,ch:q.ch,app:chk(q)})}return o}""", RNG)
        # every model x key x a spread of registers, through the same path the questions use
        k1r = await pg.evaluate("""()=>{const o=[];for(const c in CADT[1].maj)for(const t of CADT[1].maj[c])for(const k of earCadKeys(1,'maj'))for(let b=41;b<=52;b+=2)for(let s=67;s<=77;s+=2)for(const fb of [42,49,56])for(const ls of [67,72,77]){
            const key={k,mode:'maj'},rns=t.split(' '),P=earCadProg(1,rns,key,{b,s,fb,ls});
            o.push({a:c,rns,k,md:'maj',reg:{b,s,fb,ls},ch:P.ch,app:P.ch?withKey(key,()=>checkSATB(P.ch,P.L)).filter(e=>e.sev==='error').map(e=>e.rule):['no realisation']})}return o}""")
        COUNT['EL-7 rung 1 model x key x register realisations'] = len(k1r)
        # the key chord plays before the two chords (audio is another item's; this only reads the order of the notes)
        cue = await pg.evaluate("""(mk)=>{const R=eval(mk)(37);const T=[];const o=window.c2Tone;window.c2Tone=(m,t)=>T.push([m,t]);EAR.drill='cad';EAR.lvl.cad=1;
            const res=[];for(let i=0;i<40;i++){EAR.q=earGen('cad',1,R);T.length=0;earPlay();stopAll();const times=[...new Set(T.map(x=>x[1].toFixed(3)))];res.push(times.length)}window.c2Tone=o;return res}""", RNG)
        if any(n != 3 for n in cue):
            fail('K', f'rung 1 playback is not key chord + two chords: onsets {collections.Counter(cue)}')
        sec_K(k1, k1r)

        if errs:
            fail('page', f'page errors: {errs[:5]}')
        await b.close()

    report = {'counts': dict(COUNT), 'failures': {k: v[:25] for k, v in FAIL.items()}, 'n_failures': sum(len(v) for v in FAIL.values())}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)

asyncio.run(main())
