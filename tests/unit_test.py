"""Targeted unit tests for register items P2-4, P2-6 and R9.
Run: python3 tests/unit_test.py <repo dir>

P2-4  chordInfo().dom is true only for chords that carry the leading note (V, V7, vii°, vii°7 in major and minor),
      and false for the minor v / v7 and the subtonic VII / VII7 of a minor key. After VII or v, VI is no longer
      forced to double its 3rd (that rule is for V-VI, where the leading note must rise).
P2-6  Every scale the Keys room offers on every tonic it offers (major, natural, harmonic and melodic minor) is spelled
      as music21 spells it. A theoretical key is flagged, and the flag offers the usual enharmonic tonic.
R9    chordInfo() on every degree of a major and a minor key (triads and 7th chords, in several keys): the function
      (analyse().f, shown through FNAME) and chordInfo().dom. vii° and vii°7 in a major key are dominant (D); the minor
      v / v7 and VII / VII7 of a minor key are the modal dominant (MD, "soft pull · modal dominant"; 0.48 decision 12,
      formerly W and S), never dominant; dom is true exactly for the D chords (consistent with P2-4).
M-12  (R2) a chord on the 5th with no 3rd (sus4, 5, 7sus4) is D in major and minor, in homes() and analyse(), and the Keys
      text says it has no 3rd (not "the minor v"); v / v7 stay MD; VIIsus4 / VII5 in minor are MD.
X-12  (R2) climb 8 draws a borrowed ♭VII rose when MD_MAJOR is on; the Analysis key text names "borrowed into major".
S-T1  (R2) every Ear Lab rhythm tile hover pairs its values one to one with the US names (syn: three of each).
D12   (0.48 decision 12) homes() (the Keys room) and analyse() agree: minor v / v7 and minor-key VII / VII7 are MD in
      both, V / V7 / vii° / vii°7 stay D; the borrowed v and ♭VII of a major key are MD; MD is coloured madder rose
      #b1729d (--md) in FN, FNHEX and the gym/SATB numeral colours; no function colour is the old blue-grey #7fb3c8;
      the deepened #8b4978 is defined for ivory; MD text reaches at least 4.5:1 on every ground it is drawn on.
C9    (0.49) the Ear Lab function map (earNumFn) agrees with analyse(): minor v / v7 and VII / VII7 are MD, and so are the
      borrowed v / ♭VII of a major key while MD_MAJOR is on (X when it is off); V, V7, vii°, vii°7 stay D; MD draws in var(--md).
      0.49 C24: every numeral outside the key (borrowed iv / ii° / ♭III / ♭VI in major, I / IV / II in minor, major II or III,
      i in major ...) is X, as analyse() 'C', root position and inverted; minor vi is X (spelled check).
      0.49 C35: analyse() checks spelling too, so it agrees on all of them, including the 17 minor numerals spelled outside the key
      (vi, vi°, vi°7, VI°, VI°7, iv°, IV°, ivø7, IVø7, iv°7, IV°7, ii°7, II°7, V+, v+, vii+, ♯VII+), with no exception.
C8    (0.49) the Chord Library's augmented and diminished 7th texts say "symmetrical" only for equal temperament and name the
      wrap-round interval (diminished 4th / augmented 2nd); the dim7 is vii°7 of four minor keys.
ICfix (0.50, IC_050_B0) levels stay 1-7 (lvClamp, lvLoad never re-migrates over a stored number, a data-l click elsewhere does
      nothing); aug 6ths Level 6 step 20; colour chords, Oracle switches, climbs 1, 2, 9, 11 by level; 12 dictation keys from Level 5;
      SATB doubling split and the short "comes at Level n" note; Analysis and form tags; the split Ear Lab rungs (content, places,
      >= 100 distinct items, saved numbers, next by place); help text in places; a level and a rising step on every tagged item.
"""
import re, sys, asyncio, json, pathlib, collections
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import scale, pitch

FAIL = []
TONICS = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B', 'Cb', 'Fb', 'E#', 'B#']


def m21(tonic, sc):
    t = pitch.Pitch(tonic.replace('b', '-') if len(tonic) > 1 else tonic)
    S = {'maj': scale.MajorScale, 'nmin': scale.MinorScale, 'hmin': scale.HarmonicMinorScale, 'mmin': scale.MelodicMinorScale}[sc](t)
    if sc == 'mmin':  # ascending melodic minor = natural minor with raised 6th and 7th
        from music21 import interval
        return [p.replace('-', 'b') for p in [t.transpose(i).name for i in ['P1', 'M2', 'm3', 'P4', 'P5', 'M6', 'M7', 'P8']]]
    ps = S.getPitches(t.name + '4', t.name + '5')
    return [p.name.replace('-', 'b') for p in ps][:8]


async def main():
    n = 0
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#keys')
        await pg.wait_for_timeout(1500)
        # ---- P2-4 ----
        dom = await pg.evaluate("""()=>{const o={};for(const [md,k] of [['maj',0],['min',9],['min',4]])for(const rn of ['V','V7','vii°','vii°7','v','v7','VII','VII7','i','iv','VI','III','I','IV','vi','ii'])
            {let p;try{p=parseRoman(rn,{k,mode:md})}catch(e){continue}if(!p)continue;o[`${md}${k} ${rn}`]=chordInfo({...p,inv:0},{k,mode:md}).dom}return o}""")
        for k, v in dom.items():
            n += 1
            md, rn = k.split(' ')
            # vii°7 in a major key (the fully diminished 7th borrowed from minor) carries the leading note: dominant since R9 (0.48)
            want = rn in ('V', 'V7', 'vii°', 'vii°7')
            if v != want:
                FAIL.append(f'P2-4 {k}: dom={v}, expected {want}')
        dbl = await pg.evaluate("""()=>{const o=[];for(const k of [9,4,2,7,0])for(const s of ['i VII VI','i v VI']){const key={k,mode:'min'},r=realise(s,key);if(!r.sat){o.push([s,k,'none']);continue}
            const I=withKey(key,()=>chordInfo(r.L[2],key)),t3=I.third.midi%12,c=r.sat[2].filter(m=>m%12===t3).length;o.push([s,k,c])}return o}""")
        for s, k, c in dbl:
            n += 1
            if c == 'none':
                FAIL.append(f'P2-4 {s} in key {k}: no realisation')
        # ---- R9 ----
        WANT = {'maj': {'I': 'T', 'ii': 'PD', 'iii': 'T', 'IV': 'PD', 'V': 'D', 'vi': 'T', 'vii°': 'D',
                        'Imaj7': 'T', 'ii7': 'PD', 'iii7': 'T', 'IVmaj7': 'PD', 'V7': 'D', 'vi7': 'T', 'viiø7': 'D', 'vii°7': 'D'},
                'min': {'i': 'T', 'ii°': 'PD', 'III': 'T', 'iv': 'PD', 'V': 'D', 'v': 'MD', 'VI': 'T', 'VII': 'MD', 'vii°': 'D',
                        'i7': 'T', 'iiø7': 'PD', 'IIImaj7': 'T', 'iv7': 'PD', 'V7': 'D', 'v7': 'MD', 'VImaj7': 'T', 'VII7': 'MD', 'vii°7': 'D'}}
        fx = await pg.evaluate("""(W)=>{const o=[];for(const [md,ks] of [['maj',[0,7,2,5,10]],['min',[9,4,2,0,6]]])for(const k of ks)for(const rn of Object.keys(W[md])){
            const key={k,mode:md},p=parseRoman(rn,key);if(!p){o.push({md,k,rn,err:'parse'});continue}
            for(const inv of [0,1,2]){const I=withKey(key,()=>chordInfo({...p,inv},key));o.push({md,k,rn,inv,f:I.a.f,name:FNAME[I.a.f],dom:I.dom,num:I.a.num})}}return o}""", WANT)
        for r in fx:
            n += 1
            if r.get('err'):
                FAIL.append(f"R9 {r['md']}{r['k']} {r['rn']}: could not parse")
                continue
            want = WANT[r['md']][r['rn']]
            if r['f'] != want:
                FAIL.append(f"R9 {r['md']}{r['k']} {r['rn']} inv {r['inv']}: function {r['f']} ({r['name']}), expected {want}")
            if r['dom'] != (want == 'D'):
                FAIL.append(f"R9 {r['md']}{r['k']} {r['rn']} inv {r['inv']}: dom={r['dom']}, expected {want == 'D'}")
            if want == 'MD' and r['name'] != 'soft pull · modal dominant':
                FAIL.append(f"R9 {r['md']}{r['k']} {r['rn']}: reads '{r['name']}'")
            if want != 'D' and (r['name'] or '').endswith('· dominant'):
                FAIL.append(f"R9 {r['md']}{r['k']} {r['rn']}: reads '{r['name']}' but has no leading note")
        # ---- D12 (0.48 decision 12): modal dominant ----
        d12 = await pg.evaluate("""()=>{const o=[];
            for(const k of [9,4,2,0,6,11,1])for(const [rn,want] of [['v','MD'],['v7','MD'],['VII','MD'],['VII7','MD'],['V','D'],['V7','D'],['vii°','D'],['vii°7','D'],['i','T'],['iv','PD']]){
              const key={k,mode:'min'},p=parseRoman(rn,key);if(!p){o.push({k,rn,err:'parse'});continue}
              const c=chordOf(p.root,p.q,0),h=homes(c).find(x=>x.k===k&&x.mode==='min'),a=withKey(key,()=>analyse(p,key)),I=withKey(key,()=>chordInfo({...p,inv:0},key));
              o.push({k,rn,want,homes:h?h.f:null,an:a.f,dom:I.dom,col:FN[a.f],kcol:h?FN[h.f]:null})}
            for(const k of [0,7,2,5,10])for(const [rn,want] of [['bVII','MD'],['bVII7','MD'],['v','MD'],['V','D'],['iv','C'],['bVI','C']]){
              const key={k,mode:'maj'},p=parseRoman(rn,key);if(!p){o.push({k,rn,err:'parse maj'});continue}
              const a=withKey(key,()=>analyse(p,key));o.push({k,rn,want,maj:true,an:a.f,homes:a.f,dom:withKey(key,()=>chordInfo({...p,inv:0},key)).dom,col:FN[a.f]})}
            return o}""")
        for r in d12:
            n += 1
            if r.get('err'):
                FAIL.append(f"D12 {r}"); continue
            tag = f"D12 {'maj' if r.get('maj') else 'min'}{r['k']} {r['rn']}"
            if r['an'] != r['want'] or r['homes'] != r['want']:
                FAIL.append(f"{tag}: analyse {r['an']}, homes {r['homes']}, expected {r['want']}")
            if r['want'] == 'MD' and (r['col'] != 'var(--md)' or (not r.get('maj') and r['kcol'] != 'var(--md)') or r['dom']):
                FAIL.append(f"{tag}: colour {r['col']} / {r.get('kcol')}, dom {r['dom']}")
        # ---- C9 (0.49): the Ear Lab function map agrees with Analysis on the modal dominant ----
        c9 = await pg.evaluate("""()=>{const o=[];
            const L={min:[['v','MD'],['v7','MD'],['VII','MD'],['VII7','MD'],['V','D'],['V7','D'],['vii°','D'],['vii°7','D'],['i','T'],['III','T'],['VI','T'],['iv','PD'],['ii°','PD']],
                     maj:[['v','MD'],['v7','MD'],['♭VII','MD'],['♭VII7','MD'],['V','D'],['V7','D'],['vii°','D'],['I','T'],['vi','T'],['ii','PD'],['IV','PD']]};
            // 0.49 C24: every numeral outside the key is X (Analysis 'C'), by case, accidental, quality and mode; diatonic 7ths keep their function
            L.maj.push(['i','X'],['II','X'],['ii°','X'],['iiø7','X'],['III','X'],['III+','X'],['iv','X'],['VI','X'],['VII','X'],['vii','X'],['♭II','X'],['♭III','X'],['♭VI','X'],
                       ['I7','X'],['IV7','X'],['iii','T'],['ii7','PD'],['viiø7','D'],['vii°7','D']);
            L.min.push(['I','X'],['I7','X'],['II','X'],['ii','X'],['ii7','X'],['iii','X'],['IV','X'],['IV7','X'],['vi','X'],['vii','X'],['viiø7','X'],['♭II','X'],
                       ['III+','T'],['iiø7','PD'],['i7','T'],['iv7','PD']);
            // 0.49 C35 (IC_C_ENG_049, L108): the 17 minor-key numerals that sound inside the key but are spelled outside it (C♭, D♯, F𝄪 in
            // C minor): analyse() now checks the spelling as the Ear Lab map does, so both say X (vi is above)
            const C35=['vi°','vi°7','VI°','VI°7','iv°','IV°','ivø7','IVø7','iv°7','IV°7','ii°7','II°7','V+','v+','vii+','♯VII+'];
            C35.forEach(x=>L.min.push([x,'X']));
            for(const md of ['min','maj'])for(const k of md==='min'?[9,4,2,0]:[0,7,2,5])for(const [rn,want] of L[md]){const key={k,mode:md},p=parseRoman(rn.replace('♭','b'),key);
              const an=p?withKey(key,()=>analyse(p,key)).f:null,e=earNumFn(rn,md),e2=earNumFn(rn+':1',md);
              o.push({md,k,rn,want:want==='MD'&&md==='maj'&&!MD_MAJOR?'X':want,an:an==='C'?'X':an,e,e2,col:ELFN[e]&&ELFN[e][1]})}
            return o}""")
        for r in c9:
            n += 1
            tag = f"C9 {r['md']}{r['k']} {r['rn']}"
            if r['e'] != r['want'] or r['e2'] != r['want']:
                FAIL.append(f"{tag}: Ear Lab map {r['e']} / inverted {r['e2']}, expected {r['want']}")
            # 0.49 C35: no exception any more (minor vi and the 16 others above: analyse() reads the spelling, as the Ear Lab map does)
            if r['an'] != r['e']:
                FAIL.append(f"{tag}: Ear Lab {r['e']} but Analysis {r['an']}")
            if r['e'] == 'MD' and r['col'] != 'var(--md)':
                FAIL.append(f"{tag}: MD colour {r['col']}")
        # ---- C8 (0.49): the Chord Library 'symmetrical' sentences name the enharmonic wrap-round interval and stay in equal temperament ----
        c8 = await pg.evaluate("()=>({lib:Object.fromEntries(Q.filter(x=>x.k==='aug'||x.k==='dim7').map(x=>[x.k,x.t])),sym:QSYM})")
        for k, need in (('aug', ('equal temperament', 'diminished 4th', 'major 3rd', 'three equal parts')),
                        ('dim7', ('equal temperament', 'augmented 2nd', 'minor 3rd', 'four equal parts', 'four different minor keys'))):
            n += 1
            t = c8['lib'].get(k, '')
            miss = [w for w in need if w not in t]
            if miss or 'leading-note 7th of four different keys' in t:
                FAIL.append(f'C8 Chord Library {k}: missing {miss}: {t!r}')
            n += 1
            if 'each note is a' in c8['sym'].get(k, '') or ('diminished 4th' if k == 'aug' else 'augmented 2nd') not in c8['sym'].get(k, ''):
                FAIL.append(f"C8 QSYM {k}: {c8['sym'].get(k)!r}")
        css = await pg.evaluate("""()=>{const cs=getComputedStyle(document.documentElement);return{md:cs.getPropertyValue('--md').trim(),mdi:cs.getPropertyValue('--md-ivory').trim(),
            hex:FNHEX.MD,cols:COLS['var(--md)'],fname:FNAME.MD,suit:SUIT.MD,legend:[...document.querySelectorAll('.flegend span')].map(s=>s.textContent+'|'+s.getAttribute('style')).join(' ')}}""")
        n += 1
        if css['md'] != '#b1729d' or css['mdi'] != '#8b4978' or css['hex'] != '#b1729d' or css['cols'] != '#b1729d':
            FAIL.append(f'D12 colour values: {css}')
        n += 1
        if css['fname'] != 'soft pull · modal dominant' or css['suit'] != 'Soft pull' or 'MD modal dominant: soft pull' not in css['legend'] or 'var(--md)' not in css['legend']:
            FAIL.append(f'D12 names and Keys legend: {css}')
        src = (REPO / 'index.html').read_text(encoding='utf-8')
        n += 1
        fnline = next(l for l in src.splitlines() if l.startswith('const FN={'))
        if '#7fb3c8' in fnline or "MD:'var(--md)'" not in fnline:
            FAIL.append(f'D12 FN still uses the blue-grey or lacks MD: {fnline}')
        # the SATB score numerals (Voicing lab) and the gym frame numerals draw MD in #b1729d: E minor, i v6 iv6 V and i VII III
        sv = await pg.evaluate("""async()=>{location.hash='voice';await new Promise(r=>setTimeout(r,500));const o={};
            for(const [nm,prog] of [['v','i v:1 iv:1 V i'],['VII','i VII III iv V i']]){K={k:4,mode:'min'};P=prog.split(' ').map(t=>{const[r,inv]=t.split(':');const p=parseRoman(r,K);return{...p,inv:+(inv||0),beats:4}});
              VL.vc='gym';renderCoach();await new Promise(r=>setTimeout(r,600));
              const tx=[...document.querySelectorAll('#satbStaff svg text')].map(t=>[t.textContent,(t.getAttribute('fill')||t.style.fill||'').toLowerCase()]);o[nm]=tx}return o}""")
        for nm, tx in sv.items():
            n += 1
            hit = [c for t, c in tx if t.startswith(nm) and not t.startswith('vii')]
            if not hit or any(c not in ('#b1729d', 'rgb(177, 114, 157)') for c in hit):
                FAIL.append(f'D12 SATB score numeral {nm}: colours {hit} (texts {[t for t, c in tx][:12]})')
        # contrast: every element drawn in the MD colour, against the ground behind it (alpha-composited), at least 4.5:1
        cr = await pg.evaluate("""async()=>{const lum=c=>{const f=x=>{x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4)};return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])};
            const rgb=s=>{const m=s.match(/[\\d.]+/g);return m?m.map(Number):null};
            const ground=el=>{let stack=[];for(let e=el;e;e=e.parentElement){const b=rgb(getComputedStyle(e).backgroundColor);if(b&&(b.length<4||b[3]>0)){stack.push(b);if(b.length<4||b[3]>=1)break}}
              let c=[11,9,6];for(const b of stack.reverse()){const a=b.length<4?1:b[3];c=c.map((x,i)=>x*(1-a)+b[i]*a)}return c};
            const out=[];const scan=room=>{document.querySelectorAll('body *').forEach(e=>{if(!e.getClientRects().length)return;const cs=getComputedStyle(e);const col=e instanceof SVGElement?(cs.fill||''):cs.color;
              if(!/177, 114, 157|139, 73, 120/.test(col))return;if(!e.textContent.trim())return;const fg=rgb(col),bg=ground(e instanceof SVGElement?e.closest('svg'):e),L1=lum(fg),L2=lum(bg);
              out.push({room,txt:e.textContent.trim().slice(0,30),fg:col,bg:bg.map(Math.round).join(','),cr:Math.round((Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05)*100)/100})})};
            location.hash='voice';await new Promise(r=>setTimeout(r,400));scan('voice');
            location.hash='gym';await new Promise(r=>setTimeout(r,400));scan('gym');
            location.hash='seed';await new Promise(r=>setTimeout(r,300));S.root='E';S.q='m';try{render()}catch(e){}await new Promise(r=>setTimeout(r,300));
            const kc=[...document.querySelectorAll('#keys .kchip')].find(b=>/A minor/.test(b.textContent));if(kc)kc.click();await new Promise(r=>setTimeout(r,300));scan('keys');
            location.hash='analysis';await new Promise(r=>setTimeout(r,300));try{AN.tab='prog';renderAnalysis()}catch(e){}await new Promise(r=>setTimeout(r,300));scan('analysis');
            AN.tab='score';AN.score='jesu';AN.layers.harm=true;renderAnalysis();await new Promise(r=>setTimeout(r,2500));scan('analysis score');return out}""")
        rooms = collections.Counter(x['room'] for x in cr)
        for x in cr:
            n += 1
            if x['cr'] < 4.5:
                FAIL.append(f"D12 contrast {x['cr']}:1 for {x['txt']!r} ({x['fg']} on {x['bg']}) in {x['room']}")
        n += 1
        if len(cr) < 5:
            FAIL.append(f'D12 contrast scan found only {len(cr)} MD elements: {rooms}')
        print('D12 contrast scan:', dict(rooms), 'lowest', min((x['cr'] for x in cr), default=None), file=sys.stderr)
        # ---- R2 (0.48 re-check) M-12: chords on the 5th with no 3rd stay D in both modes; v / v7 are MD; the Keys text says what is open ----
        m12 = await pg.evaluate("""()=>{const o=[];location.hash='seed';
            for(const k of [0,9,4,7,2,5,10,3])for(const mode of ['maj','min'])for(const [q,want] of [['sus4','D'],['5','D'],['7sus4','D'],['','?'],['m','MD'],['m7','MD']]){
              const r=LET[0];const key={k,mode},root=spell(mod(tonicLetter(key)+4,7),60+mod(k+7,12)).name,ch={root,q,inv:0};
              let c;try{c=chordOf(root,q,0)}catch(e){continue}const h=homes(c).find(x=>x.k===k&&x.mode===mode),a=withKey(key,()=>analyse(ch,key));
              S.root=root;S.q=q;S.inv=0;S.key={k,mode};try{render()}catch(e){}const ctx=(document.getElementById('ctx')||{}).textContent||'';
              o.push({k,mode,q,want:want==='?'?(mode==='min'?'D':'D'):want,homes:h?h.f:null,an:a.f,ctx})}return o}""")
        for r in m12:
            if r['mode'] == 'maj' and r['q'] in ('m', 'm7'):
                continue  # minor v in a major key is not diatonic (homes has no entry); analyse() covers it in D12
            n += 1
            tag = f"M-12 {r['mode']}{r['k']} V{r['q']}"
            if r['homes'] != r['want'] or r['an'] != r['want']:
                FAIL.append(f"{tag}: homes {r['homes']}, analyse {r['an']}, expected {r['want']}")
            if r['q'] in ('sus4', '5', '7sus4') and ('the minor v,' in r['ctx'] or 'modal dominant' in r['ctx'] or 'no 3rd' not in r['ctx']):
                FAIL.append(f"{tag}: Keys text {r['ctx'][:160]!r}")
            if r['q'] in ('m', 'm7') and 'the minor v' not in r['ctx']:
                FAIL.append(f"{tag}: Keys text {r['ctx'][:160]!r}")
        m12b = await pg.evaluate("""()=>{const o=[];for(const k of [9,4,0])for(const q of ['sus4','5']){const key={k,mode:'min'},root=spell(mod(tonicLetter(key)+6,7),60+mod(k+10,12)).name;
            o.push([k,q,withKey(key,()=>analyse({root,q,inv:0},key)).f])}return o}""")
        for k, q, f in m12b:
            n += 1
            if f != 'MD':
                FAIL.append(f'M-12 min{k} VII{q}: {f}, expected MD (subtonic, no leading note)')
        # ---- R2 X-12: borrowed v / ♭VII in major follow MD_MAJOR in climb 8 and in the Analysis key text ----
        x12 = await pg.evaluate("""async()=>{location.hash='climbs/8';await new Promise(r=>setTimeout(r,500));const o={md_major:MD_MAJOR};S.level=6;K={k:0,mode:'maj'};
            const L='I bVII IV I'.split(' ').map(r=>({...parseRoman(r,K),rn:r,inv:0}));const h=c8Bars(L,K,'x');const d=document.createElement('div');d.innerHTML=h;
            o.bars=[...d.querySelectorAll('.bar')].map(b=>[b.querySelector('span').textContent,b.getAttribute('style'),b.className]);
            o.src=document.documentElement.innerHTML.length;return o}""")
        n += 1
        bvii = [b for b in x12['bars'] if '♭VII' in b[0]]
        if not bvii or 'var(--md)' not in bvii[0][1] or ' md' not in bvii[0][2]:
            FAIL.append(f"X-12 climb 8 ♭VII bar: {x12['bars']}")
        n += 1
        if "${MD_MAJOR?', and borrowed into major (v, ♭VII)':''}" not in src or 'const MD_MAJOR=true;' not in src or src.count('MD_MAJOR') < 4:
            FAIL.append('X-12: Analysis key text or the MD_MAJOR switch missing')
        # ---- R2 S-T1: every rhythm tile hover pairs its values one to one with the US names ----
        tiles = await pg.evaluate("""()=>{const d=document.createElement('div');document.body.appendChild(d);d.innerHTML=Object.keys(ELTITLE).map(k=>earRhyTile(k)).join('');
            d.querySelectorAll('[data-tt]').forEach(termBtnSync);const o=[...d.querySelectorAll('[data-tt]')].map(b=>[b.dataset.earcell,b.title]);d.remove();return o}""")
        for k, t in tiles:
            n += 1
            mm = re.match(r'^(.*) \(US: (.*)\)$', t)   # 0.49 C14: the bracket form
            if not mm:
                FAIL.append(f'S-T1 tile {k}: hover {t!r}'); continue
            gb, us = mm.group(1).split(', '), mm.group(2).split(', ')
            if len(gb) != len(us):
                FAIL.append(f'S-T1 tile {k}: {len(gb)} values but {len(us)} US names: {t!r}')
            # 0.49 C13: the count is named on both sides, value for value ("2 quavers (US: 2 eighth notes)")
            elif [re.match(r'^(\d+) ', g).group(1) if re.match(r'^\d+ ', g) else '1' for g in gb] != [re.match(r'^(\d+) ', u).group(1) if re.match(r'^\d+ ', u) else '1' for u in us]:
                FAIL.append(f'C13 tile {k}: counts differ between the two sides: {t!r}')
        n += 1
        syn = dict(tiles).get('syn')
        if syn != 'quaver, crotchet, quaver (US: eighth note, quarter note, eighth note)':
            FAIL.append(f'S-T1 syn tile: {syn!r}')
        # ---- P2-6 ----
        rows = await pg.evaluate("""async(T)=>{location.hash='keys';await new Promise(r=>setTimeout(r,400));const o=[];
            for(const sc of ['maj','nmin','hmin','mmin'])for(const t of T){KS.tonic=t;KS.sc=sc;KS.desc=false;renderScales();
              o.push({sc,t,names:scaleTones(t,sc,false).map(x=>x.name),sig:document.getElementById('ksSig').textContent,alt:[...document.querySelectorAll('#ksSig [data-kst]')].map(b=>b.dataset.kst)})}return o}""", TONICS)
        for r in rows:
            n += 1
            want = m21(r['t'], r['sc'])
            if r['names'] != want:
                FAIL.append(f"P2-6 {r['t']} {r['sc']}: app {r['names']} vs music21 {want}")
            # theoretical: the key signature would need more than 7 sharps or flats
            flats = sum(x.count('b') for x in want[:7] if len(x) > 1)
            sharps = sum(x.count('#') for x in want[:7])
            if r['sc'] in ('hmin', 'mmin'):  # the key signature is the natural minor's
                nat = m21(r['t'], 'nmin')
                flats = sum(x.count('b') for x in nat[:7] if len(x) > 1)
                sharps = sum(x.count('#') for x in nat[:7])
            theo = flats > 7 or sharps > 7
            flagged = 'theoretical' in r['sig'].lower()
            if theo != flagged:
                FAIL.append(f"P2-6 {r['t']} {r['sc']}: theoretical={theo}, flagged={flagged}")
            if theo and not r['alt'] and 'enharmonic' not in r['sig']:
                FAIL.append(f"P2-6 {r['t']} {r['sc']}: theoretical key without an enharmonic alternative")
        gb = next(r for r in rows if r['t'] == 'Gb' and r['sc'] == 'mmin')
        if 'F#' not in gb['alt']:
            FAIL.append(f"P2-6 G♭ melodic minor does not offer F♯ melodic minor (offers {gb['alt']})")
        # ---- SRCFIX: a rendered song card links the bare URL and shows the note as text ----
        card = await pg.evaluate("""()=>{S.q='m';renderSongs();const a=[...document.querySelectorAll('#songs .tn a')];
            const wwy=(()=>{S.q='7sus4';renderSongs();return [...document.querySelectorAll('#songs .song')].find(d=>/Weather With You/.test(d.textContent))})();
            return {n:a.length,bad:a.filter(x=>/\\s/.test(x.getAttribute('href'))||!/^https?:\\/\\/\\S+$/.test(x.getAttribute('href'))).length,
              wwy:wwy?wwy.querySelector('.tn').textContent:'',notes:document.querySelectorAll('#songs .srcnote').length}}""")
        n += 1
        if card['bad'] or not card['n']:
            FAIL.append(f"SRCFIX: song card hrefs not bare URLs: {card}")
        n += 1
        if 'a single community transcription' not in card['wwy']:
            FAIL.append('SRCFIX: Weather With You card does not show its source note')
        ks = await pg.evaluate("""()=>{renderKsSongs({k:Object.keys(SCSONGS)[0]});const a=[...document.querySelectorAll('#ksSongs .tn a')];return {n:a.length,bad:a.filter(x=>/\\s/.test(x.getAttribute('href'))).length,notes:document.querySelectorAll('#ksSongs .srcnote').length}}""")
        n += 1
        if ks['bad'] or not ks['notes']:
            FAIL.append(f'SRCFIX: scale song card: {ks}')
        # ---------------- 0.50 ICfix (IC_050_B0): self-checks for each fix ----------------
        ic = await pg.evaluate("""async()=>{const o={},keep=S.level,ls=k=>localStorage.getItem(k);
          // V1-1, V1-6, V1-9: levels never leave 1-7
          o.clamp=[9,0,-3,3.5,'6','x','',null,undefined,NaN,7,1].map(v=>lvClamp(v));
          lvlSet(4);lvlSet(9);o.set9=[S.level,ls('cjg_level')];lvlSet('the cadence');o.setNaN=[S.level,ls('cjg_level')];lvlSet(2.6);o.set26=S.level;
          const d=document.createElement('div');d.className='el-cad';d.dataset.l='the cadence';document.body.appendChild(d);lvlSet(3);d.click();o.dlclick=[S.level,ls('cjg_level')];d.remove();
          const load=(lv,st)=>{localStorage.removeItem('cjg_level');localStorage.removeItem('cjg_stage');if(lv!==null)localStorage.setItem('cjg_level',lv);if(st!==null)localStorage.setItem('cjg_stage',st);S.level=5;lvLoad();return[S.level,ls('cjg_level')]};
          o.load={chosen6_stage4:load('6','4'),stored9_stage4:load('9','4'),nan_stage5:load('NaN','5'),none_stage6:load(null,'6'),half:load('3.5',null),empty_stage4:load('','4'),none_none:load(null,null),zero:load('0','5')};
          // V1-1 / V2-2: augmented sixths
          o.aug6=Q.filter(q=>/\\+6$/.test(q.k)).map(q=>[q.k,q.l,q.stp]);o.qOut=Q.filter(q=>!(q.l>=1&&q.l<=7)).map(q=>q.k);o.libHasAug6=qualItems().some(q=>/\\+6$/.test(q.k));
          // V1-4: colour chords, Oracle sevenths and colour switch
          o.col={};for(const lv of [1,2,3,4,5,6,7])o.col[lv]={maj:colourRomans({k:0,mode:'maj'},false,lv),min:colourRomans({k:9,mode:'min'},false,lv)};
          K={k:0,mode:'maj'};O.sev=true;o.deck7={};for(const lv of [2,3,4,5]){S.level=lv;o.deck7[lv]=deck().some(c=>/7/.test(c.q))}
          location.hash='oracle';room('oracle');await new Promise(r=>setTimeout(r,300));o.ocol={};for(const lv of [2,3,5]){S.level=lv;renderOracle();o.ocol[lv]=[getComputedStyle($('oCol').parentElement).display!=='none',getComputedStyle($('oSev').parentElement).display!=='none']}
          // V1-3: climb 1
          o.c1={};location.hash='climbs/1';room('climbs');await new Promise(r=>setTimeout(r,300));
          for(const lv of [1,2,3,4,5]){S.level=lv;C1.pick=false;renderClimb1();o.c1[lv]={mode:C1.mode,quiz:C1M.filter(m=>m.l<=Math.max(S.level,1)).map(m=>m.k).sort().join(' ')}}
          o.c1tags=Object.fromEntries(C1M.map(m=>[m.k,[m.l,m.stp]]));
          // V1-2: climb 2
          o.c2={};for(const lv of [1,2,3,4,5,6,7]){S.level=lv;C2.pos='below';const L=Math.max(S.level,3);o.c2[lv]={tier:c2Tier(L),posBelow:L>=4,modes:C2M.filter(m=>m.l<=L).map(m=>m.k).join(' '),sp:C2SP.filter(s=>s.l<=L).map(s=>s.k).join(' ')}}
          o.c2tags=Object.fromEntries(C2M.map(m=>[m.k,m.l]));o.c2sp=C2SP.map(s=>s.l);
          // V1-5: climb 11
          const key=C11.key,mel=c11Mel(key);o.c11={};for(const lv of [1,2,4,5,6]){S.level=lv;o.c11[lv]=mel.map((_,i)=>c11Opts(i,key,mel).length)}
          S.level=1;const a1=JSON.stringify(mel.map((_,i)=>c11Opts(i,key,mel)));S.level=2;o.c11same=a1===JSON.stringify(mel.map((_,i)=>c11Opts(i,key,mel)));
          // climb 9 opens on shells below Level 5
          o.c9={};for(const lv of [4,5,6]){S.level=lv;C9.vtPick=false;renderClimb9();o.c9[lv]=C9.vt}
          // V8-1: 12 keys from Level 5
          o.keys=[1,2,3,4,5,6,7].map(l=>LADKEYS[l].length);
          // V11-1, V11-2: SATB doubling split; findings above the level count, short note only
          K={k:0,mode:'maj'};const V=parseRoman('V',K),I=parseRoman('I',K),vo=[[43,59,62,71],[48,55,64,72]];
          o.satb={};for(const lv of [3,5]){S.level=lv;const iss=checkSATB(vo,[{...V,inv:0},{...I,inv:0}]).filter(e=>e.rule==='dbllt');o.satb[lv]=iss.map(e=>({sev:e.sev,lvl:e.lvl,later:e.later,short:/comes at Level 5/.test(e.text),full:/It has to rise/.test(e.text)}))}
          o.satblv=['double','dblinv','dbl7','dbllt','dblchrom'].map(k=>SATBLV[k]);
          // V2-1 Analysis, forms
          o.anlv=ANLV;o.anchrom=ANCHROM;o.anlay=ANLAY;S.level=2;o.anmark2=[anLyMark('form'),anLyMark('cad'),anLyMark('harm')].map(x=>x?x.replace(/<[^>]+>/g,'').trim():'');S.level=3;o.anmark3=anLyMark('harm');
          o.forms=Object.fromEntries(FORMS.map(f=>[f.k,[f.l,f.stp]]));
          // V9-1, V9-2: split rungs
          o.slot={mel:EARSLOT.mel,cad:EARSLOT.cad};o.rn=[rn('mel',5),rn('mel',13),rn('cad',2),rn('cad',4),rn('mel',6)];o.stage=[EARSTAGE.mel[4],EARSTAGE.mel[12],EARSTAGE.cad[1],EARSTAGE.cad[3]];
          let s=11;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};o.split={};
          for(const [dd,l,N] of [['mel',5,400],['mel',13,400],['cad',2,300],['cad',4,300]]){const c={},ids=new Set();let lr=new Set();for(let i=0;i<N;i++){const q=earGen(dd,l,R);const k=dd==='mel'?q.info.var:q.key.mode;c[k]=(c[k]||0)+1;ids.add(dd==='mel'?q.id:JSON.stringify([q.rns,q.key,q.ch]));lr.add(q.l+'/'+q.rung)}o.split[dd+l]={c,distinct:ids.size,lr:[...lr]}}
          // saved progress: an old internal number keeps its rung and place
          EAR.drill='mel';EAR.q=null;EAR.lvl.mel=5;o.saved=[earLvl(),rn('mel',earLvl())];EAR.lvl.mel=12;o.saved.push(earLvl(),rn('mel',12));
          o.next=[earNextRung('mel',5),earNextRung('mel',13),earNextRung('cad',2),earNextRung('cad',4)];
          // #14: Ear Lab help text in places and levels
          o.help=[EARHOW.rhy,EARHOW.cad,EARHOW.mel,ELTIPNOTE.rhy,ELTIPNOTE.cad,ELTIPS.qual[2][0]].join(' | ');
          // V2-4 (#13): a level and a step on every item, steps rising with levels
          const sets={Q,SCALES,IVS,CADS,C1M,C2M,C2SP,C4EX,C5FAM,C6EX,C6Q,C7EX,C8EX,C8Q,C9EX,C10EX,C11V,C11TOOLS,C11VOCSET,C12MODES,C12SHAPES,FORMS,VTYPES:Object.values(VTYPES),ANALYSIS:Object.values(ANLV).map(([l,stp])=>({l,stp}))};
          o.steps={};for(const[n,A]of Object.entries(sets)){const bad=A.filter(x=>!(x.l>=1&&x.l<=7&&Number.isInteger(x.stp)));const srt=A.filter(x=>Number.isInteger(x.stp)).slice().sort((a,b)=>a.stp-b.stp);
            o.steps[n]={n:A.length,missing:bad.length,rising:srt.every((x,i)=>!i||srt[i-1].l<=x.l),sk:A.some(x=>Object.prototype.hasOwnProperty.call(x,'s'))&&n!=='IVS'}}
          o.ivs=IVS.map(x=>x.s).join(',');
          localStorage.removeItem('cjg_stage');lvlSet(keep);return o}""")
        def ck(c, m):
            nonlocal n
            n += 1
            if not c:
                FAIL.append('ICfix ' + m)
        ck(ic['clamp'] == [7, 1, 1, 4, 6, None, None, None, None, None, 7, 1], f"lvClamp {ic['clamp']}")
        ck(ic['set9'] == [7, '7'] and ic['setNaN'] == [7, '7'] and ic['set26'] == 3, f"lvlSet out of range / NaN / 2.6: {ic['set9']} {ic['setNaN']} {ic['set26']}")
        ck(ic['dlclick'] == [3, '3'], f"V1-6 a click on an element with data-l=\"the cadence\" changed the level: {ic['dlclick']}")
        L = ic['load']
        ck(L['chosen6_stage4'] == [6, '6'], f"load: chosen Level 6 with old stage 4 still stored -> {L['chosen6_stage4']}")
        ck(L['stored9_stage4'] == [7, '7'], f"load: stored 9 must clamp to 7, not re-migrate: {L['stored9_stage4']}")
        ck(L['nan_stage5'] == [4, '4'] and L['none_stage6'] == [5, '5'] and L['empty_stage4'] == [2, '2'], f"load: migration only when cjg_level is absent or not a number: {L}")
        ck(L['half'] == [4, '4'] and L['zero'] == [1, '1'] and L['none_none'] == [5, None], f"load: 3.5 / 0 / nothing: {L}")
        ck(ic['aug6'] == [['It+6', 6, 20], ['Fr+6', 6, 20], ['Ger+6', 6, 20]] and not ic['qOut'] and not ic['libHasAug6'], f"aug 6ths {ic['aug6']}, outside 1-7 {ic['qOut']}, in the library list {ic['libHasAug6']}")
        C = ic['col']
        ck(C['1']['maj'] == [] and C['2']['maj'] == [] and C['3']['maj'] == ['iv', 'bVII'] and C['3']['min'] == ['IV'], f"colour chords L1-3 {C['1']} {C['2']} {C['3']}")
        ck({'bVI', 'bIII', 'V7/V', 'V7/vi'} <= set(C['4']['maj']) and 'V7/ii' not in C['4']['maj'] and 'I' in C['4']['min'], f"colour chords L4 {C['4']}")
        ck({'V7/ii', 'V7/iii', 'V7/IV', 'vii°7'} <= set(C['5']['maj']) and 'bII' not in C['5']['maj'] and 'bII' in C['6']['maj'] and 'bII' in C['6']['min'], f"colour chords L5/L6 {C['5']} {C['6']}")
        # migrated learners keep what they had: old Stage 5 (now 4) had iv bIII bVI bVII; old Stage 6 (now 5) had every secondary dominant
        ck({'iv', 'bIII', 'bVI', 'bVII'} <= set(C['4']['maj']) and {'IV', 'I'} <= set(C['4']['min']), 'migrated Stage 5 (Level 4) lost a borrowed chord')
        ck({'V7/ii', 'V7/iii', 'V7/IV', 'V7/V', 'V7/vi'} <= set(C['5']['maj']) and {'V7/iv', 'V7/V'} <= set(C['5']['min']), 'migrated Stage 6 (Level 5) lost a secondary dominant')
        ck(ic['deck7'] == {'2': False, '3': True, '4': True, '5': True}, f"Oracle sevenths by level {ic['deck7']}")
        ck(ic['ocol'] == {'2': [False, False], '3': [True, True], '5': [True, True]}, f"Oracle colour / sevenths switches shown {ic['ocol']}")
        ck([ic['c1'][str(l)]['mode'] for l in (1, 2, 3, 4, 5)] == ['ion', 'ion', 'dor', 'dor', 'dor'], f"climb 1 opening mode {ic['c1']}")
        ck([ic['c1'][str(l)]['quiz'] for l in (1, 2, 3, 4, 5)] == ['aeo ion', 'aeo ion', 'aeo dor ion mix', 'aeo dor ion lyd mix phr', 'aeo dor ion loc lyd mix phr'], f"climb 1 quiz modes {ic['c1']}")
        ck(ic['c1tags'] == {'ion': [1, 1], 'aeo': [1, 2], 'dor': [3, 3], 'mix': [3, 4], 'lyd': [4, 5], 'phr': [4, 6], 'loc': [5, 7]}, f"climb 1 tags {ic['c1tags']}")
        c2 = ic['c2']
        ck([c2[str(l)]['tier'][:7] for l in range(1, 8)] == ['Level 3'] * 3 + ['Level 4', 'Level 5', 'Level 6', 'Level 6'], f"climb 2 tier line {[c2[str(l)]['tier'] for l in range(1, 8)]}")
        ck([c2[str(l)]['sp'] for l in (3, 4, 5, 6)] == ['1', '1 2 3', '1 2 3 4 5', '1 2 3 4 5 6'] and [c2[str(l)]['posBelow'] for l in (1, 3, 4)] == [False, False, True], f"climb 2 species / below by level {c2}")
        ck(ic['c2tags'] == {'dor': 3, 'aeo': 3, 'ion': 3, 'mix': 3, 'phr': 4, 'lyd': 4} and ic['c2sp'] == [3, 4, 4, 5, 5, 6], f"climb 2 tags {ic['c2tags']} {ic['c2sp']}")
        ck(all(x > 0 for x in ic['c11']['1']) and ic['c11same'], f"climb 11 at Level 1 offers the Level 2 set {ic['c11']}")
        ck(all(a <= b for a, b in zip(ic['c11']['2'], ic['c11']['5'])) and sum(ic['c11']['5']) > sum(ic['c11']['2']) and sum(ic['c11']['6']) >= sum(ic['c11']['5']), f"climb 11 grows with the level {ic['c11']}")
        ck(ic['c9'] == {'4': 'shell', '5': 'rootless', '6': 'rootless'}, f"climb 9 opening voicing {ic['c9']}")
        ck(ic['keys'] == [3, 5, 7, 9, 12, 12, 12], f"dictation keys per level {ic['keys']}")
        ck(ic['satb']['3'] and all(e['sev'] == 'error' and e['lvl'] == 5 and e['later'] and e['short'] and not e['full'] for e in ic['satb']['3']), f"SATB doubled leading note at Level 3 {ic['satb']['3']}")
        ck(ic['satb']['5'] and all(e['sev'] == 'error' and not e['later'] and e['full'] and not e['short'] for e in ic['satb']['5']), f"SATB doubled leading note at Level 5 {ic['satb']['5']}")
        ck(ic['satblv'] == [3, 4, 5, 5, 6], f"SATB doubling levels {ic['satblv']}")
        ck(ic['anlv'] == {'chopin7': [3, 1], 'k331a': [3, 2], 'k331d': [3, 3], 'chorale': [4, 4], 'jesu': [5, 5], 'ohaupt': [5, 6], 'k545': [5, 7], 'entertainer': [5, 8], 'maple': [5, 9], 'chopin20': [5, 10]}
           and ic['anchrom'] == {'chopin20': 6}, f"Analysis tags {ic['anlv']} {ic['anchrom']}")
        ck(ic['anmark2'] == ['', '', '3'] and ic['anmark3'] == '', f"Analysis layer marks {ic['anmark2']} {ic['anmark3']!r}")
        ck(ic['forms'] == {'phrase': [1, 1], 'blues12': [2, 2], 'rondo': [3, 3], 'tv': [3, 4], 'jazzblues': [4, 5], 'minblues': [4, 6], 'rag': [5, 7], 'sonata': [5, 8], 'rhythm': [6, 9], 'sonrondo': [6, 10], 'fugue': [6, 11]}, f"forms {ic['forms']}")
        ck(ic['slot']['mel'][:12] == [2, 3, 4, 5, 6, 9, 10, 12, 13, 15, 16, 18] and ic['slot']['mel'][12] == 7 and ic['slot']['cad'] == [4, 5, 13, 7], f"EARSLOT {ic['slot']}")
        ck(ic['rn'] == [6, 7, 5, 7, 9] and ic['stage'] == [2, 3, 2, 3], f"split rung places / levels {ic['rn']} {ic['stage']}")
        sp = ic['split']
        ck(set(sp['mel5']['c']) == {'lapent', 'major'} and set(sp['mel13']['c']) == {'natmin', 'major'}, f"melody split contents {sp['mel5']['c']} {sp['mel13']['c']}")
        ck(set(sp['cad2']['c']) == {'maj'} and set(sp['cad4']['c']) == {'min'}, f"cadence split contents {sp['cad2']['c']} {sp['cad4']['c']}")
        ck(all(sp[k]['distinct'] >= 100 for k in sp), f"split rungs: distinct items {[(k, sp[k]['distinct']) for k in sp]}")
        ck(sp['mel13']['lr'] == ['5/13'] and sp['cad4']['lr'] == ['2/4'] and sp['mel5']['lr'] == ['5/5'], f"split rung items carry content rung / rung {[(k, sp[k]['lr']) for k in sp]}")
        ck(ic['saved'] == [5, 6, 12, 18], f"saved internal numbers keep their rung and place {ic['saved']}")
        ck(ic['next'] == [13, 6, 4, 3], f"next written rung by place {ic['next']}")
        h = ic['help']
        ck('Stage' not in h and 'rung 1,' not in h and 'clapped at rung 2' in h and 'Rung 13 (Level 5)' in h and 'from rung 6' in h and 'the 7th (rung 13)' in h, f"Ear Lab help text: {h[:400]}")
        for k, v in ic['steps'].items():
            ck(v['missing'] == 0 and v['rising'] and not v['sk'], f"steps {k}: {v}")
        ck(ic['ivs'] == '1,2,3,4,5,6,6,7,8,9,10,11,12,3,8,9,10', f"interval semitones {ic['ivs']}")
        if errs:
            FAIL.append(f'page errors: {errs[:3]}')
        await b.close()
    print(json.dumps({'checks': n, 'failures': FAIL[:25], 'n_failures': len(FAIL)}, indent=1, ensure_ascii=False))
    sys.exit(1 if FAIL else 0)

asyncio.run(main())
