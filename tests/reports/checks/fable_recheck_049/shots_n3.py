"""Fable's re-check renders for N1 / N2 (0.49 RC, e90aa5b). Run: python3 shots.py <repo dir> [scene ...]
Writes <scene>_<w>[_names].png (viewport), ..._card.png (whole Ear Lab card) and facts.json (text read from the page)."""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1]).resolve()
OUT = pathlib.Path(__file__).resolve().parent / 'n3'
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright

PRE = "(()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='ear';EAR.all=false;EAR.st={};EAR.rd={};EAR.reached={};room('ear')})()"
STUB = "window.earPlay=()=>{};window.elPlay=()=>{}"
SEED = "(s)=>{let a=s>>>0;Math.random=()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}"
MEL = """(o)=>{EAR.mod='home';EAR.rd={};EAR.reached={};EAR.sysSel=null;const want=o.want?new Function('q','return '+o.want):null;let q,ok=false;
 for(let t=0;t<3000;t++){EAR.drill='mel';EAR.lvl.mel=o.l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();q=EAR.q;if(!want||want(q)){ok=true;break}}
 if(!ok)return{err:'no item for '+o.want};
 const parts=q.l===11?['mel','bass']:['mel'];const log=[];
 for(const part of parts){if(q.l===11&&EAR.part!==part)document.querySelector(`[data-earpart="${part}"]`).click();
  let T=ladTruthEntries(q,part).map((e,j)=>({s:e.s,t:e.t,idx:j+1}));
  const ed=part==='bass'?o.bedit:o.edit;if(ed)T=new Function('T','q','return '+ed)(T,q)||T;
  const frac=part==='bass'?(o.bfrac===undefined?o.frac:o.bfrac):o.frac,n=Math.floor(T.length*frac);
  for(let j=0;j<n;j++){const e=T[j];if(e.s===null){document.querySelector(`[data-rest="${e.t}"]`).click();continue}
   const lb=document.querySelector(`[data-len="${e.t}"]`);if(!lb||lb.getAttribute('aria-disabled')==='true'){log.push('len '+e.t+' not live at '+j);break}
   if(lb.getAttribute('aria-checked')!=='true')lb.click();
   const rb=document.querySelector(`[data-earsol="${e.s}"]`);if(!rb){log.push('no row '+e.s);break}rb.click()}}
 if(o.chk){if(!earFull(q))log.push('not full');else earCheck()}
 return{l:q.l,metre:q.metre,mode:q.mode,key:q.key,anac:q.anac,a:q.a.join(' '),bass:q.bass?q.bass.map(b=>b.midi):null,bassTruth:q.bass?[ladFirst(q,'bass').s,...ladTruthEntries(q,'bass').map(e=>e.s)].join(' '):null,off:typeof earBassOff==='function'?earBassOff(q):null,res:EAR.res&&EAR.res.kind,log}}"""
FACTS = """()=>{const tx=s=>[...document.querySelectorAll(s)].map(e=>e.textContent);const m=document.getElementById('earMel');
 return{melW:EAR.melW,melClient:m?m.clientWidth:null,psBuilt:EAR.psBuilt,sys:EAR.q&&EAR.q.l>=4?earMelSystems(EAR.q,'mel').map(s=>s.map(b=>b.bi)):null,
  map:[...document.querySelectorAll('#earMain .el-sysmap button')].map(b=>({t:b.childNodes[0].textContent,a:b.getAttribute('aria-label'),p:b.getAttribute('aria-pressed'),st:[...b.querySelectorAll('i span')].map(x=>x.className).join(' ')})),
  labels:tx('#earMel svg text:not(.melsol):not(.melname)'),sol:tx('#earMel text.melsol'),names:tx('#earMel text.melname').slice(0,12),
  lnote:tx('#earMain .el-lnote'),rows:[...document.querySelectorAll('#earMain .earlad [data-earsol]')].map(b=>b.dataset.earsol+'>'+b.querySelector('b').textContent+' ['+b.getAttribute('aria-label')+']'),
  teach:tx('#earMain .el-teach'),head:tx('#earMain .el-rhead, #earMain .el-result h3'),lbl:tx('#earMain .melscore .lbl'),svgs:document.querySelectorAll('#earMel svg').length,
  over:document.documentElement.scrollWidth-innerWidth}}"""
SEMI = "ladEntriesToLine(q,ladTruthEntries(q,'mel'),'mel').some(x=>x.dur===105)"
WRONG = "T.map((e,j)=>j===%d&&e.s?{...e,s:[...document.querySelectorAll('[data-earsol]')].map(x=>x.dataset.earsol).find(x=>x!==e.s&&!/[a-z]{2}/.test(x)&&x!==(T[j-1]||{}).s)}:e)"
def o11(off, mode): return "q.mode==='%s'&&earBassOff(q)===%d" % (mode, off)
LATE = "T.map((e,j)=>j===T.length-2&&e.s?{...e,s:[...document.querySelectorAll('[data-earsol]')].map(x=>x.dataset.earsol).find(x=>x!==e.s&&!/[a-z]{2}/.test(x)&&x!==(T[j-1]||{}).s)}:e)"
BRHY = "(()=>{const k=T.findIndex((e,j)=>j>=2&&e.t>=840);if(k<0)return T;const o=T.slice();o.splice(k,1,{...T[k],t:T[k].t/2},{...T[k],t:T[k].t/2});return o})()"
SCENES = {
 'n3_maj_off1_basslate': (dict(l=11, want=o11(1,'maj'), frac=1, bfrac=1, chk=1, bedit=LATE), 19),
 'n3_maj_off2_basslate': (dict(l=11, want=o11(2,'maj'), frac=1, bfrac=1, chk=1, bedit=LATE), 19),
 'n3_min_off1_basslate': (dict(l=11, want=o11(1,'min'), frac=1, bfrac=1, chk=1, bedit=LATE), 23),
 'n3_min_off2_basslate': (dict(l=11, want=o11(2,'min'), frac=1, bfrac=1, chk=1, bedit=LATE), 23),
 'n3_maj_off1_bassfirst': (dict(l=11, want=o11(1,'maj'), frac=1, bfrac=1, chk=1, bedit=WRONG % 1), 19),
 'n3_maj_off1_mellate': (dict(l=11, want=o11(1,'maj'), frac=1, bfrac=1, chk=1, edit=LATE), 19),
 'n3_min_off2_mellate': (dict(l=11, want=o11(2,'min'), frac=1, bfrac=1, chk=1, edit=LATE), 23),
 'n3_min_off1_both': (dict(l=11, want=o11(1,'min'), frac=1, bfrac=1, chk=1, edit=LATE, bedit=WRONG % 1), 23),
 'n3_maj_off1_bassrhythm': (dict(l=11, want=o11(1,'maj'), frac=1, bfrac=1, chk=1, bedit=BRHY), 19),
 'n3_maj_off1_allright': (dict(l=11, want=o11(1,'maj'), frac=1, bfrac=1, chk=1), 19),
 'n1_r12_up34_result': (dict(l=12, want="q.metre==='3/4'&&q.anac&&" + SEMI, frac=1, chk=1, edit=WRONG % 2), 33),
 'n1_r12_noup44_result': (dict(l=12, want="q.metre==='4/4'&&!q.anac&&" + SEMI, frac=1, chk=1, edit=WRONG % 3), 35),
 'n1_r12_nosemi_up_result': (dict(l=12, want="q.anac&&!" + SEMI, frac=1, chk=1, edit=WRONG % 3), 37),
 'n1_r6_up68_result': (dict(l=6, want="q.metre==='6/8'&&q.anac", frac=1, chk=1, edit=WRONG % 3), 5),
}
HIDE = "()=>{window.__h=[];document.querySelectorAll('body *').forEach(e=>{if(getComputedStyle(e).position==='fixed'&&!e.closest('#earMain')){window.__h.push([e,e.style.visibility]);e.style.visibility='hidden'}})}"
SHOW = "()=>{(window.__h||[]).forEach(([e,v])=>e.style.visibility=v)}"
async def main():
    args = sys.argv[2:]; namesets = ['k', 'kk'] if '--kk' in args else ['k']; args = [a for a in args if a != '--kk']
    names = args or list(SCENES)
    ff = OUT / 'facts.json'; F = json.loads(ff.read_text()) if ff.exists() else {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in ((1366, 768), (1024, 768), (390, 844)):
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2 if w < 500 else 1)
            errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.route('**/*', cjg.make_route(REPO))
            await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
            await pg.evaluate(PRE); await pg.evaluate(STUB)
            for nm in names:
                o, seed = SCENES[nm]
                for ns in namesets:
                    tag = f'{nm}_{w}' + ('' if ns == 'k' else '_kk')
                    await pg.evaluate("(n)=>{EAR.names=n;EAR.part='mel';EAR.sugNow=false;EAR.sugSeen={}}", ns)
                    await pg.evaluate(SEED, seed)
                    r = await pg.evaluate(MEL, o); await pg.wait_for_timeout(350)
                    f = await pg.evaluate(FACTS); f['scene'] = r; f['errs'] = errs[:3]; F[tag] = f
                    await pg.evaluate("window.scrollTo(0,0)")
                    if w < 500:
                        sel = '#earResult' if o.get('chk') else '#earMain .el-head'
                        await pg.evaluate("(s)=>{const c=document.querySelector(s)||document.querySelector('#earMain .el-head');scrollTo(0,c.getBoundingClientRect().top+scrollY-100)}", sel)
                        await pg.wait_for_timeout(120); await pg.screenshot(path=str(OUT / f'{tag}.png'))
                        await pg.evaluate("()=>{const c=document.querySelector('#earMain .melscore');if(c)scrollTo(0,c.getBoundingClientRect().top+scrollY-110)}")
                        await pg.wait_for_timeout(120); await pg.screenshot(path=str(OUT / f'{tag}_staves.png'))
                        await pg.evaluate("()=>{const c=document.querySelector('#earMain .earlad');if(c)scrollTo(0,c.getBoundingClientRect().top+scrollY-330)}")
                        await pg.wait_for_timeout(120); await pg.screenshot(path=str(OUT / f'{tag}_ladder.png'))
                        await pg.evaluate("window.scrollTo(0,0)")
                    else:
                        await pg.screenshot(path=str(OUT / f'{tag}.png'))
                    await pg.evaluate(HIDE)
                    el = await pg.query_selector('#earMain .el-card') or await pg.query_selector('#earMain')
                    await el.screenshot(path=str(OUT / f'{tag}_card.png'))
                    await pg.evaluate(SHOW)
                    print(tag, json.dumps({k: f[k] for k in ('melW', 'melClient', 'psBuilt', 'sys', 'map', 'labels', 'lnote', 'teach', 'over')}, ensure_ascii=False)[:900], '|', json.dumps(r, ensure_ascii=False)[:400], errs[:2], flush=True)
            await pg.close()
        await b.close()
    ff.write_text(json.dumps(F, indent=1, ensure_ascii=False))
asyncio.run(main())
