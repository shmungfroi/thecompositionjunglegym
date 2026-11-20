"""IC_SELF_048 probe 4-5: function colours of chords on the 5th and the (flat) 7th; MD_MAJOR on, and off via a patched copy.
Run: python3 tests/reports/checks/ic_self/p2_function.py <repo>
Expected values are this checker's own reading of the spec (not taken from the app):
  major key: V, V7, Vsus4, Vsus2, V5, V7sus4 -> D;  v, v7 (borrowed) -> MD if MD_MAJOR else C;  bVII, bVII7, bVIIsus4/sus2/5/7sus4 -> MD if MD_MAJOR else C
  minor key: V, V7, Vsus4, V5, V7sus4 -> D;  v, v7 -> MD;  VII, VII7, VIIsus4, VIIsus2, VII5, VII7sus4 -> MD; vii° (raised) -> D"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright

JS = r"""()=>{const o=[];
 for(let k=0;k<12;k++)for(const mode of ['maj','min']){const key={k,mode},tl=tonicLetter(key);
  const cases=[[4,7,['','7','m','m7','sus4','sus2','5','7sus4']],[6,10,['','7','sus4','sus2','5','7sus4']]];
  if(mode==='min')cases.push([6,11,['dim','dim7']]);
  for(const [deg,semi,qs] of cases)for(const q of qs){const root=spell(tl+deg,60+mod(k+semi,12)).name;let a,h=null;
   try{a=withKey(key,()=>analyse({root,q,inv:0},key));const c=chordOf(root,q,0);h=(homes(c).find(x=>x.k===k&&x.mode===mode)||{}).f||null}catch(e){a={f:'ERR '+e.message,num:''}}
   o.push({k,mode,deg,semi,q,root,f:a.f,num:a.num,homes:h,hex:FNHEX[a.f]||null,name:FNAME[a.f]||null})}}
 return o}"""

def expect(r, mdm):
    q, mode, semi = r['q'], r['mode'], r['semi']
    if semi == 11: return 'D'
    if semi == 7:
        if q in ('m', 'm7'): return 'MD' if (mode == 'min' or mdm) else 'C'
        if mode == 'min' and q == 'sus2': return None  # Vsus2 in minor has the raised 6th: outside the spec
        return 'D'
    if semi == 10:
        return 'MD' if (mode == 'min' or mdm) else 'C'

async def run(pg, patched):
    await pg.goto('http://app/index.html#gym'); await pg.wait_for_timeout(1200)
    mdm = await pg.evaluate('MD_MAJOR')
    rows = await pg.evaluate(JS)
    bad = []
    for r in rows:
        e = expect(r, mdm)
        if e is None: continue
        if r['f'] != e: bad.append(f"{'off' if patched else 'on'} {r['mode']}{r['k']} {r['root']}{r['q']} ({r['num']}): {r['f']}, expected {e}")
        if r['homes'] is not None and r['homes'] != r['f']: bad.append(f"homes/analyse disagree {r['mode']}{r['k']} {r['root']}{r['q']}: homes {r['homes']} analyse {r['f']}")
        if r['f'] == 'MD' and (r['hex'] != '#bd6b97' or 'soft pull' not in (r['name'] or '')): bad.append(f"MD colour/name {r}")
    # Gym cards: colour, label (FNAME) and numeral on the page for a C major and an A minor progression
    ui = await pg.evaluate(r"""async()=>{const out=[];for(const [key,rns] of [[{k:0,mode:'maj'},['I','v','bVII','V','Vsus4','v7','bVII7']],[{k:9,mode:'min'},['i','v','VII','V','VII7','v7']]]){
      K.k=key.k;K.mode=key.mode;P=rns.map(r=>{const p=parseRoman(r,key);return p?{root:p.root,q:p.q,inv:0,beats:4}:null}).filter(Boolean);
      P.push({root:spell(tonicLetter(key)+4,60+mod(key.k+7,12)).name,q:'sus4',inv:0,beats:4},{root:spell(tonicLetter(key)+4,60+mod(key.k+7,12)).name,q:'5',inv:0,beats:4});
      renderGym();await new Promise(r=>setTimeout(r,50));
      document.querySelectorAll('#prog .pc[data-pi]').forEach((d,i)=>out.push({key:key.mode+key.k,num:d.querySelector('.num').textContent,sym:d.querySelector('.cs').textContent,
        fx:d.querySelector('.fx').textContent,col:getComputedStyle(d).getPropertyValue('--c').trim(),f:analyse(P[i],K).f}))}return out}""")
    for u in ui:
        want_col = {'MD': '#bd6b97', 'D': '#c8473b', 'T': '#8fbf6a', 'PD': '#c9a24a'}.get(u['f'])
        fx_want = {'MD': 'soft pull · modal dominant', 'D': 'pull · dominant', 'T': 'home · tonic', 'PD': 'away · predominant', 'C': 'colour'}[u['f']]
        if not u['fx'].startswith(fx_want): bad.append(f"gym card label {u}")
        if want_col and u['col'].lower() not in (want_col, f"var(--{ {'MD':'md','D':'red','T':'green','PD':'gold'}[u['f']] })"): bad.append(f"gym card colour {u}")
    # climb 8: borrowed v / bVII bars in C major
    c8 = await pg.evaluate(r"""()=>{const K0={k:0,mode:'maj'};const L='I v bVII IV I'.split(' ').map(r=>({...parseRoman(r,K0),rn:r,inv:0}));const d=document.createElement('div');
      d.innerHTML=c8Bars(L,K0,'x');return [...d.querySelectorAll('.bar')].map(b=>[b.querySelector('span').textContent,b.getAttribute('style'),b.className])}""")
    for rn, st, cl in c8:
        if rn in ('v', '♭VII'):
            ok = ('var(--md)' in st and 'md' in cl.split()) if mdm else ('var(--md)' not in st and 'md' not in cl.split())
            if not ok: bad.append(f"climb 8 bar {rn}: style {st} class {cl} (MD_MAJOR={mdm})")
    # Keys room text for Gsus4 / G5 (C major, C minor) and Gm (C minor), Bb (C minor)
    keys = await pg.evaluate(r"""()=>{const o=[];location.hash='seed';for(const [root,q,key] of [['G','sus4',{k:0,mode:'maj'}],['G','5',{k:0,mode:'min'}],['G','7sus4',{k:0,mode:'min'}],['G','m',{k:0,mode:'min'}],['Bb','',{k:0,mode:'min'}],['Bb','sus4',{k:0,mode:'min'}]]){
      S.root=root;S.q=q;S.inv=0;S.key=key;try{render()}catch(e){}o.push([root+q,key.mode,(document.getElementById('ctx')||{}).textContent||''])}return o}""")
    return mdm, rows, bad, ui, c8, keys

async def main():
    rep = {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for patched in (False, True):
            pg = await b.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            def mk(route, patched):
                async def rt(r):
                    if patched and r.request.url.split('?')[0].split('#')[0] in ('http://app/index.html', 'http://app/'):
                        src = (REPO / 'index.html').read_text().replace('const MD_MAJOR=true;', 'const MD_MAJOR=false;')
                        return await r.fulfill(body=src, content_type='text/html')
                    return await route(r)
                return rt
            await pg.route('**/*', mk(cjg.make_route(REPO), patched))
            mdm, rows, bad, ui, c8, keys = await run(pg, patched)
            rep['off' if patched else 'on'] = {'MD_MAJOR': mdm, 'cases': len(rows), 'bad': bad, 'pageerrors': errs, 'gym': ui, 'climb8': c8, 'keys': keys,
                                              'sample': [f"{r['mode']}{r['k']} {r['root']}{r['q']} {r['num']} {r['f']}" for r in rows if r['k'] == 0]}
            await pg.close()
        await b.close()
    print(json.dumps(rep, indent=1, ensure_ascii=False))

asyncio.run(main())
