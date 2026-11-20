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
D12   (0.48 decision 12) homes() (the Keys room) and analyse() agree: minor v / v7 and minor-key VII / VII7 are MD in
      both, V / V7 / vii° / vii°7 stay D; the borrowed v and ♭VII of a major key are MD; MD is coloured madder rose
      #bd6b97 (--md) in FN, FNHEX and the gym/SATB numeral colours; no function colour is the old blue-grey #7fb3c8;
      the deepened #9e4776 is defined for ivory; MD text reaches at least 4.5:1 on every ground it is drawn on.
"""
import sys, asyncio, json, pathlib, collections
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
        css = await pg.evaluate("""()=>{const cs=getComputedStyle(document.documentElement);return{md:cs.getPropertyValue('--md').trim(),mdi:cs.getPropertyValue('--md-ivory').trim(),
            hex:FNHEX.MD,cols:COLS['var(--md)'],fname:FNAME.MD,suit:SUIT.MD,legend:[...document.querySelectorAll('.flegend span')].map(s=>s.textContent+'|'+s.getAttribute('style')).join(' ')}}""")
        n += 1
        if css['md'] != '#bd6b97' or css['mdi'] != '#9e4776' or css['hex'] != '#bd6b97' or css['cols'] != '#bd6b97':
            FAIL.append(f'D12 colour values: {css}')
        n += 1
        if css['fname'] != 'soft pull · modal dominant' or css['suit'] != 'Soft pull' or 'MD modal dominant: soft pull' not in css['legend'] or 'var(--md)' not in css['legend']:
            FAIL.append(f'D12 names and Keys legend: {css}')
        src = (REPO / 'index.html').read_text(encoding='utf-8')
        n += 1
        fnline = next(l for l in src.splitlines() if l.startswith('const FN={'))
        if '#7fb3c8' in fnline or "MD:'var(--md)'" not in fnline:
            FAIL.append(f'D12 FN still uses the blue-grey or lacks MD: {fnline}')
        # the SATB score numerals (Voicing lab) and the gym frame numerals draw MD in #bd6b97: E minor, i v6 iv6 V and i VII III
        sv = await pg.evaluate("""async()=>{location.hash='voice';await new Promise(r=>setTimeout(r,500));const o={};
            for(const [nm,prog] of [['v','i v:1 iv:1 V i'],['VII','i VII III iv V i']]){K={k:4,mode:'min'};P=prog.split(' ').map(t=>{const[r,inv]=t.split(':');const p=parseRoman(r,K);return{...p,inv:+(inv||0),beats:4}});
              VL.vc='gym';renderCoach();await new Promise(r=>setTimeout(r,600));
              const tx=[...document.querySelectorAll('#satbStaff svg text')].map(t=>[t.textContent,(t.getAttribute('fill')||t.style.fill||'').toLowerCase()]);o[nm]=tx}return o}""")
        for nm, tx in sv.items():
            n += 1
            hit = [c for t, c in tx if t.startswith(nm) and not t.startswith('vii')]
            if not hit or any(c not in ('#bd6b97', 'rgb(189, 107, 151)') for c in hit):
                FAIL.append(f'D12 SATB score numeral {nm}: colours {hit} (texts {[t for t, c in tx][:12]})')
        # contrast: every element drawn in the MD colour, against the ground behind it (alpha-composited), at least 4.5:1
        cr = await pg.evaluate("""async()=>{const lum=c=>{const f=x=>{x/=255;return x<=.03928?x/12.92:Math.pow((x+.055)/1.055,2.4)};return .2126*f(c[0])+.7152*f(c[1])+.0722*f(c[2])};
            const rgb=s=>{const m=s.match(/[\\d.]+/g);return m?m.map(Number):null};
            const ground=el=>{let stack=[];for(let e=el;e;e=e.parentElement){const b=rgb(getComputedStyle(e).backgroundColor);if(b&&(b.length<4||b[3]>0)){stack.push(b);if(b.length<4||b[3]>=1)break}}
              let c=[11,9,6];for(const b of stack.reverse()){const a=b.length<4?1:b[3];c=c.map((x,i)=>x*(1-a)+b[i]*a)}return c};
            const out=[];const scan=room=>{document.querySelectorAll('body *').forEach(e=>{if(!e.getClientRects().length)return;const cs=getComputedStyle(e);const col=e instanceof SVGElement?(cs.fill||''):cs.color;
              if(!/189, 107, 151|158, 71, 118/.test(col))return;if(!e.textContent.trim())return;const fg=rgb(col),bg=ground(e instanceof SVGElement?e.closest('svg'):e),L1=lum(fg),L2=lum(bg);
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
        if errs:
            FAIL.append(f'page errors: {errs[:3]}')
        await b.close()
    print(json.dumps({'checks': n, 'failures': FAIL[:25], 'n_failures': len(FAIL)}, indent=1, ensure_ascii=False))
    sys.exit(1 if FAIL else 0)

asyncio.run(main())
