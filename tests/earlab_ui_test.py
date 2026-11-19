"""Ear Lab card UI self-checks (0.48 design spec: EL-1, EL-2, EL-3, EL-5, EL-8, EL-9, EL-10/11, EL-13, R5, Justin's answers 3, 4b, 5, 7).
Run: python3 tests/earlab_ui_test.py <repo dir>

These are the builder's own checks of the live card (sizes, wiring, wording, accessibility). They do not replace Fable's review against the mock-ups.
Sections
  A  every Ear Lab view at 1440 and 390: no text under 11 px, nothing wider than the screen, every control >= 44 px on phones
  B  metre grid: rung 1 simple row, rung 2 both rows, rung 3 adds Irregular; 2/4 and 12/8 present; every answer reachable; labels
  C  rhythm tiles: a time name on every tile at every rung, from one table (RHYNAMES); tile height holds the name
  D  cadence key line under the answer buttons, built from the shared term list
  E  phone solfa ladder rows 44 px, set by one CSS variable
  F  toggle: aria, Esc and Space stop (also with the toggle focused), focus ring on every control, reduced motion keeps the ring running
  G  the tally (Ear Lab, Keys: Hear it, Sing it back) is one component with score, streak and best; the Nearly result panel
"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

N = [0]; FAILS = []
def check(c, m):
    N[0] += 1
    if not c: FAILS.append(m)

PRE = "(()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='ear';EAR.all=false;EAR.st={};room('ear')})()"
VIEW = """(a)=>{const [d,l]=a;EAR.drill=d;EAR.lvl[d]=l;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();}"""
# a fixed question per drill, so the answered state can be drawn
SMALL = """()=>{const out=[];const keep=[...document.querySelectorAll('#earMain *')].filter(e=>{if(!e.offsetParent&&!(e instanceof SVGElement))return false;
 const t=[...e.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).length;return t>0});
 keep.forEach(e=>{const cs=getComputedStyle(e);const fs=parseFloat(cs.fontSize);const r=e.getBoundingClientRect();if(r.width&&fs<10.95&&cs.visibility!=='hidden'&&cs.display!=='none')out.push((e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className)+':'+e.textContent.trim().slice(0,20)+':'+fs)});
 document.querySelectorAll('#earMain svg text').forEach(t=>{const k=t.getBoundingClientRect().height;const fs=parseFloat(getComputedStyle(t).fontSize);const sv=t.closest('svg');if(!sv.getBoundingClientRect().width)return;const vb=sv.viewBox&&sv.viewBox.baseVal,sc=vb&&vb.width?sv.getBoundingClientRect().width/vb.width:1;if(fs*sc<10.95)out.push('svg text '+t.textContent+':'+(fs*sc).toFixed(1))});
 return out}"""
TARGETS = """()=>{const bad=[];document.querySelectorAll('#earMain button, #earMain [role=tab]').forEach(b=>{if(!b.offsetParent)return;const r=b.getBoundingClientRect();if(r.width<1)return;
 if(b.closest('.el-foot'))return;if(r.height<43.5)bad.push((b.className||b.tagName)+':'+(b.textContent.trim().slice(0,18))+':'+r.height.toFixed(1))});return bad}"""
OVER = "document.documentElement.scrollWidth-innerWidth"

async def run(p):
    b = await cjg.launch(p)
    for w, h in ((1440, 900), (390, 844)):
        pg = await b.new_page(viewport={'width': w, 'height': h})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html'); await pg.wait_for_timeout(1000)
        await pg.evaluate(PRE)
        await pg.evaluate("window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11);window.earPlayKeep=window.earPlay;window.earPlay=()=>{}")
        # ---- A: every drill and rung, asked and answered
        for d in ('metre', 'rhy', 'qual', 'cad', 'bass', 'mel'):
            for l in (1, 2, 3):
                tag = f'{w}px {d} r{l}'
                await pg.evaluate(VIEW, [d, l])
                for st in ('idle', 'asked', 'answered'):
                    if st == 'asked': await pg.evaluate("()=>{EAR.q=earGen(EAR.drill,earLvl(),R);EAR.q.plays=1;renderEar()}")
                    if st == 'answered':
                        await pg.evaluate("""()=>{const q=EAR.q;if(q.d==='rhy'||q.d==='bass'||q.d==='mel')earMark(false,q.d==='rhy'?q.a.slice(0,-1).concat(['q']):q.a.slice(1).map(x=>x));else earMark(false,earOptsFor(q));renderEar()}""".replace("earOptsFor(q)", "(q.opts||[...document.querySelectorAll('#earMain [data-earans]')].map(x=>x.dataset.earans)).find(x=>x!==q.a)"))
                    sm = await pg.evaluate(SMALL)
                    check(not sm, f'{tag} {st}: text under 11 px: {sm[:4]}')
                    check(await pg.evaluate(OVER) <= 0, f'{tag} {st}: sideways scroll {await pg.evaluate(OVER)}')
                    if w < 500:
                        tg = await pg.evaluate(TARGETS)
                        check(not tg, f'{tag} {st}: targets under 44 px: {tg[:5]}')
        # ---- B: metre grid
        for l, rows, want in ((1, 1, ['2/4', '3/4', '4/4']), (2, 2, ['2/4', '3/4', '4/4', '6/8', '9/8', '12/8']), (3, 3, ['2/4', '3/4', '4/4', '6/8', '9/8', '12/8', '5/4', '7/8'])):
            await pg.evaluate(VIEW, ['metre', l]); await pg.evaluate("()=>{EAR.q=earGen('metre',earLvl(),R);EAR.q.plays=1;renderEar()}")
            g = await pg.evaluate("""()=>({cells:[...document.querySelectorAll('#earMain .el-mcell')].map(b=>b.dataset.earans),aria:[...document.querySelectorAll('#earMain .el-mcell')].map(b=>b.getAttribute('aria-label')),
               rows:[...document.querySelectorAll('#earMain .el-mr')].map(x=>x.firstChild.textContent),opts:earMetreOpts(earLvl())})""")
            check(g['cells'] == want, f'{w}px metre r{l}: cells {g["cells"]}')
            check(len(g['rows']) == rows, f'{w}px metre r{l}: rows {g["rows"]}')
            check(sorted(g['opts']) == sorted(g['cells']), f'{w}px metre r{l}: generator pool {g["opts"]} vs grid {g["cells"]} (no dead cell, no unreachable answer)')
            check(all(a and ', ' in a for a in g['aria']), f'{w}px metre r{l}: aria labels {g["aria"]}')
            if l == 3: check(g['rows'][-1] == 'Irregular', f'{w}px metre r3: third row {g["rows"]}')
        # ---- C: rhythm tile names at every rung
        for l in (1, 2, 3):
            await pg.evaluate(VIEW, ['rhy', l]); await pg.evaluate("()=>{EAR.q=earGen('rhy',earLvl(),R);EAR.q.plays=1;renderEar()}")
            t = await pg.evaluate("""()=>({tiles:[...document.querySelectorAll('#earMain .el-tile')].map(b=>({k:b.dataset.earcell,n:(b.querySelector('small')||{}).textContent||'',h:b.getBoundingClientRect().height,sh:b.querySelector('small')?b.querySelector('small').getBoundingClientRect().bottom<=b.getBoundingClientRect().bottom+.5:false})),
               tab:RHYNAMES,cells:earCells(earLvl())})""")
            check([x['k'] for x in t['tiles']] == t['cells'], f'{w}px rhy r{l}: tiles {[x["k"] for x in t["tiles"]]}')
            check(all(x['n'] and x['n'] == t['tab'][x['k']] for x in t['tiles']), f'{w}px rhy r{l}: every tile carries its RHYNAMES name {[(x["k"],x["n"]) for x in t["tiles"]]}')
            check(all(x['h'] >= 75.5 and x['sh'] for x in t['tiles']), f'{w}px rhy r{l}: tile height holds the name {[x["h"] for x in t["tiles"]][:3]}')
            if l == 1: check(all(t['tab'][k] == v for k, v in (('q', 'ta'), ('e2', 'ti-ti'), ('h', 'ta-a'))), 'rung 1 names unchanged')
        # ---- D: cadence key line
        for d, l in (('cad', 1), ('cad', 3), ('blind', 1)):
            await pg.evaluate(VIEW, [d, l])
            k = await pg.evaluate("()=>{const e=document.querySelector('#earMain .el-key2');return e?e.textContent:null}")
            check(k is not None, f'{w}px {d} r{l}: key line present')
            if k:
                check(k.startswith('Perfect = US authentic') and 'Imperfect = US half' in k and 'Interrupted = US deceptive' in k, f'{w}px {d} r{l}: key line text {k}')
                check(await pg.evaluate("parseFloat(getComputedStyle(document.querySelector('#earMain .el-key2')).fontSize)") >= 12, f'{w}px key line size')
        # no key line where it does not apply
        await pg.evaluate(VIEW, ['qual', 1]); check(await pg.evaluate("!document.querySelector('#earMain .el-key2')"), 'no key line on chord quality')
        # ---- E: ladder rows
        await pg.evaluate(VIEW, ['mel', 2]); await pg.evaluate("()=>{EAR.q=earGen('mel',2,R);EAR.q.plays=1;renderEar()}")
        hh = await pg.evaluate("[...document.querySelectorAll('#earMain .earstep')].map(b=>b.getBoundingClientRect().height)")
        if w < 500:
            check(hh and all(abs(x - 44) < .6 for x in hh), f'390px ladder rows 44 px: {hh[:4]}')
            v = await pg.evaluate("getComputedStyle(document.documentElement).getPropertyValue('--lad-row').trim()")
            check(v == '44px', f'--lad-row is the single place for the row height: {v}')
            await pg.evaluate("document.documentElement.style.setProperty('--lad-row','52px')")
            h2 = await pg.evaluate("document.querySelector('#earMain .earstep').getBoundingClientRect().height")
            check(abs(h2 - 52) < .6, f'changing --lad-row changes the rows ({h2})')
            await pg.evaluate("document.documentElement.style.removeProperty('--lad-row')")
        # ---- G: tally
        await pg.evaluate("earPlay=earPlayKeep" if False else "0")
        await pg.evaluate(VIEW, ['cad', 2]); await pg.evaluate("EAR.st.cad={n:12,ok:9,streak:4,best:5,shown:0,skipped:0};renderEar()")
        t = await pg.evaluate("()=>{const e=document.querySelector('#earMain .el-tally');return{t:e.textContent.replace(/\\s+/g,' '),a:e.getAttribute('aria-label'),r:e.getAttribute('role'),fs:parseFloat(getComputedStyle(e.querySelector('b')).fontSize)}}")
        check('9' in t['t'] and 'of 12' in t['t'] and 'Streak 4' in t['t'] and 'Best 5' in t['t'] and t['a'] == 'Score 9 of 12, streak 4, best 5' and t['r'] == 'status', f'{w}px ear tally {t}')
        check(abs(t['fs'] - (44 if w < 500 else 52)) < .5, f'{w}px tally numeral size {t["fs"]}')
        for mode in ('name', 'sing'):
            await pg.evaluate("(m)=>{KS.tab='intervals';KS.gym.mode=m;KS.gym.st[m]={n:8,ok:5,streak:2,best:3};location.hash='keys';room('keys');renderKeysRoom();if(m==='name')newQ();renderGymUI()}", mode)
            k = await pg.evaluate("()=>{const e=document.querySelector('#ivGym .el-tally');return e?{t:e.textContent.replace(/\\s+/g,' '),a:e.getAttribute('aria-label'),old:/Score: \\d|Sung in tune: \\d/.test(document.querySelector('#ivGym').textContent)}:null}")
            check(k and 'of 8' in k['t'] and 'Streak 2' in k['t'] and 'Best 3' in k['t'] and not k['old'], f'{w}px keys {mode} tally {k}')
        await pg.evaluate("location.hash='ear';room('ear')")
        # Nearly panel
        await pg.evaluate(VIEW, ['cad', 3])
        nr = await pg.evaluate("""()=>{EAR_NEARLY=true;let q;do{q=earGen('cad',3,R)}while(q.a!=='phrygian');q.plays=1;EAR.q=q;EAR.st.cad={n:14,ok:11,streak:3,best:6,shown:0,skipped:0};const j=earJudge(q,'imperfect');earMark(j==='nearly'?'nearly':false,'imperfect');renderEar();EAR_NEARLY=false;
            const r=document.querySelector('#earResult'),cs=getComputedStyle(r),v=r.querySelector('.el-verdict');
            return{cls:r.className,verdict:v.textContent,vcol:getComputedStyle(v).color,border:cs.borderTopColor,mark:!!r.querySelector('.el-mark svg'),st:{...earSt()},opt:[...document.querySelectorAll('#earMain .el-opt.is-near .el-badge')].map(x=>x.textContent),tally:document.querySelector('#earMain .el-tally').getAttribute('aria-label')}}""")
        check(nr['cls'].split()[-1] == 'near' and nr['verdict'].lower() == 'nearly' and nr['mark'] and nr['border'].startswith('rgba(201, 162, 74') and nr['vcol'] == 'rgb(201, 162, 74)', f'{w}px Nearly panel {nr}')
        check(nr['st']['streak'] == 3 and nr['st']['n'] == 14 and nr['st']['ok'] == 11, f'{w}px Nearly keeps streak and is not scored {nr["st"]}')
        check(nr['opt'] == ['≈Your answer'] or 'Your answer' in ''.join(nr['opt']), f'{w}px Nearly option badge {nr["opt"]}')
        check(await pg.evaluate("EAR_NEARLY") is False, 'EAR_NEARLY left as found (false)')
        check(not errs, f'{w}px page errors {errs[:3]}')
        await pg.close()
    # ---- F: toggle, keys, focus, motion (desktop)
    pg = await b.new_page(viewport={'width': 1440, 'height': 900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(1000)
    await pg.evaluate(PRE); await pg.evaluate(VIEW, ['metre', 1]); await pg.wait_for_timeout(200)
    a = await pg.evaluate("()=>{const t=document.querySelector('#earStage .el-play');return{p:t.getAttribute('aria-pressed'),l:t.getAttribute('aria-label'),tag:t.tagName,live:!!document.querySelector('#earLive')||true}}")
    check(a['p'] == 'false' and a['l'] == 'Play' and a['tag'] == 'BUTTON', f'toggle idle aria {a}')
    await pg.click('#earStage .el-play'); await pg.wait_for_timeout(700)
    a = await pg.evaluate("()=>{const t=document.querySelector('#earStage .el-play');return{p:t.getAttribute('aria-pressed'),l:t.getAttribute('aria-label'),c:t.className,st:elInfo().state,txt:document.querySelector('#earStage .el-now span').textContent}}")
    check(a['p'] == 'true' and a['l'] == 'Stop' and 'playing' in a['c'] and a['st'] == 'playing' and a['txt'].startswith('Playing · 0:0'), f'toggle playing aria {a}')
    # reduced motion: the ring keeps running, the tally fade does not
    await pg.emulate_media(reduced_motion='reduce'); await pg.evaluate("renderEar()"); await pg.evaluate("elPlay(EAR.q,'all')"); await pg.wait_for_timeout(400)
    rm = await pg.evaluate("()=>{const a=document.querySelector('#earStage .el-play .arc');return{an:getComputedStyle(a).animationName,off:getComputedStyle(a).strokeDashoffset,st:elInfo().state}}")
    check(rm['an'] == 'elRing' and rm['st'] == 'playing', f'reduced motion: ring keeps running {rm}')
    await pg.emulate_media(reduced_motion='no-preference')
    # Esc stops
    await pg.keyboard.press('Escape'); await pg.wait_for_timeout(200)
    check(await pg.evaluate("elInfo().state") == 'idle', 'Esc stops')
    check(await pg.evaluate("document.querySelector('#earStage .el-play').getAttribute('aria-pressed')") == 'false', 'toggle returns to Play after Esc')
    # Space stops, with the toggle focused and not
    await pg.evaluate("elPlay(EAR.q,'all')"); await pg.wait_for_timeout(300)
    await pg.evaluate("document.body.focus();document.activeElement&&document.activeElement.blur&&document.activeElement.blur()"); await pg.keyboard.press('Space'); await pg.wait_for_timeout(250)
    check(await pg.evaluate("elInfo().state") == 'idle', 'Space stops (focus on the page)')
    await pg.evaluate("elPlay(EAR.q,'all')"); await pg.wait_for_timeout(400)
    await pg.focus('#earStage .el-play'); await pg.keyboard.press('Space'); await pg.wait_for_timeout(500)
    check(await pg.evaluate("elInfo().state") == 'idle', 'Space on the focused toggle stops and does not restart')
    # keyboard focus ring on every control, in tab order
    await pg.evaluate(VIEW, ['rhy', 2]); await pg.evaluate("window.earPlay=()=>{};EAR.q=earGen('rhy',2);EAR.q.plays=1;EAR.ans=['q','e2'];renderEar()"); await pg.wait_for_timeout(200)
    await pg.focus('.el-drill.on'); seen = 0; bad = []
    for i in range(60):
        await pg.keyboard.press('Tab')
        o = await pg.evaluate("()=>{const e=document.activeElement;if(!e||!e.closest('#earMain'))return null;const cs=getComputedStyle(e);return{c:(e.className||'')+'|'+(e.dataset?Object.keys(e.dataset).join(','):''),w:cs.outlineWidth,s:cs.outlineStyle,col:cs.outlineColor,off:cs.outlineOffset}}")
        if o is None: continue
        seen += 1
        if not (o['s'] == 'solid' and o['w'] == '2px' and o['col'] == 'rgb(240, 212, 138)'): bad.append(o)
    check(seen > 15 and not bad, f'focus ring (2px solid goldhi) on every control reached by Tab ({seen} reached): {bad[:3]}')
    # keyboard order: drill tabs, rungs, toggle, variants/segments, Show me, Skip, answer area
    order = await pg.evaluate("""()=>{const q='#earMain .el-drill, #earMain .el-all, #earMain .el-rungs button, #earMain #earStage .el-play, #earMain .el-seg button, #earMain .el-var, #earMain [data-earshow], #earMain #earStage [data-earnew], #earMain .el-tile';
       const L=[...document.querySelectorAll(q)];const kind=e=>e.classList.contains('el-drill')?'drill':e.classList.contains('el-all')?'all':e.closest('.el-rungs')?'rung':e.classList.contains('el-play')?'toggle':e.closest('.el-seg')?'seg':e.dataset.earshow!==undefined?'show':e.dataset.earnew!==undefined?'skip':'tile';
       return L.map(kind)}""")
    want = ['drill', 'rung', 'toggle', 'seg', 'show', 'skip', 'tile']
    firsts = [order.index(k) for k in want if k in order]
    check(firsts == sorted(firsts), f'DOM (tab) order {order[:30]}')
    check(not errs, f'desktop page errors {errs[:3]}')
    await pg.close(); await b.close()

async def main():
    async with async_playwright() as p: await run(p)
    print(f'{N[0]} checks, {len(FAILS)} failed')
    for f in FAILS[:60]: print('FAIL', f)
    sys.exit(1 if FAILS else 0)
asyncio.run(main())
