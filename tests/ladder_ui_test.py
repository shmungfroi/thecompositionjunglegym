"""Ear Lab 0.49 ladder UI: self-checks (the builder's own; Fable verifies against the mock-ups).
Run: python3 tests/ladder_ui_test.py <repo dir>

  U1  the last-10 window (D10): Shown, Skipped and Nearly are not in it; the suggestion rule (8 of the last 10, next rung shown at the Stage, crosses a Stage with "Rung 5 starts Stage 5"),
      and the dot (EAR.reached) is earned once and stays
  U2  earLenLive (the palette's live lengths): every rung and metre, every legal bar of the engine is reachable length by length; the chosen length moves to the longest live shorter one
  E2E answering with the engine's own right answer through the UI marks right at every melody rung 4 to 12 (both settings at rung 9) and every rhythm rung 1 to 10
  V   the new views at 1366 and 390: 11 px floor, 44 px phone targets, no sideways scroll (.el-bandtab, .el-bandmore, .el-len, .el-undo1, .el-mut, half rungs, .el-tile.tup, .grp.set buttons)
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
STUB = "window.earPlayKeep=window.earPlay;window.earPlay=()=>{}"

UNIT = """()=>{const o={};
 // U1 the window
 let rd={};['ok','ok','shown','skipped','nearly','ok','ok','ok','ok','ok','ok','miss','miss'].forEach(k=>ladRdPush(rd,'mel',4,k));
 o.win=rd.mel[4].join('');            // shown, skipped, nearly never enter
 o.rdy=[ladRdState({mel:{4:[1,1,1,1,1,1,1,1,0,0]}},'mel',4,[4,5]).ready,ladRdState({mel:{4:[1,1,1,1,1,1,1,0,0,0]}},'mel',4,[4,5]).ready,ladRdState({mel:{4:[1,1,1,1,1,1,1,1,1,1]}},'mel',4,[4]).ready];
 // the suggestion row: crosses a Stage and says so; not shown when not ready; shown once
 EAR.drill='mel';EAR.lvl.mel=4;EAR.rd={mel:{4:[1,1,1,1,1,1,1,1,0,1]}};EAR.reached={};EAR.sugSeen={};EAR.sugNow=false;EAR.done=true;
 earUiMarked('ok');o.now1=EAR.sugNow;o.html=earSugHTML('mel',4);o.reached=(EAR.reached.mel||[]).slice();
 EAR.sugNow=false;earUiMarked('ok');o.now2=EAR.sugNow;     // not again until the count has dropped and climbed back
 EAR.rd={mel:{4:[1,1,1,1,1,1,0,0,1,1]}};earUiMarked('miss');EAR.sugNow=false;o.html2=earSugHTML('mel',4);o.reachedKept=(EAR.reached.mel||[]).includes(4);
 EAR.rd={mel:{4:[1,1,1,1,1,1,1,1,1,1]},rhy:{}};EAR.drill='mel';EAR.lvl.mel=5;EAR.sugNow=true;EAR.sugSeen={};o.within=earSugHTML('mel',5).includes('starts Stage');   // 5 -> 6 is inside Stage 5
 EAR.rd={};EAR.reached={};EAR.done=false;EAR.sugNow=false;
 return o}"""

LENLIVE = """()=>{const bad=[];let n=0;
 for(let l=4;l<=12;l++)for(let i=0;i<24;i++){const q=ladGenMel(l,Math.random);if(!q.cells&&l<4)continue;
  const T=ladTruthEntries(q,'mel');
  // every note of the right answer is live when it is its turn (the palette never forbids the true answer)
  for(let j=0;j<T.length;j++){const e=T[j],ents=T.slice(0,j);n++;if(!earLenLive(q,ents,'mel',e.t,e.s===null)){bad.push({l,j,t:e.t,rest:e.s===null,metre:q.metre});break}}
  // the chosen length moves to the longest live length shorter than it, else the shortest live one
  const P=ladPalette(q,[],'mel');if(!P.done){const live=earLiveSet(P,false),L=[...live].sort((a,b)=>a-b);n++;
   const big=earLenPick(live,99999),small=earLenPick(live,1);if(big!==L[L.length-1]||small!==L[0])bad.push({l,pick:[big,small,L]})}}
 return{n,bad:bad.slice(0,5),nbad:bad.length}}"""

E2E_MEL = """([l,mod,N])=>{const bad=[];let n=0;EAR.mod=mod;
 for(let i=0;i<N;i++){EAR.drill='mel';EAR.lvl.mel=l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();const q=EAR.q;let stuck=null;
  const parts=q.l===11?['mel','bass']:['mel'];
  for(const part of parts){if(q.l===11&&EAR.part!==part)document.querySelector(`[data-earpart="${part}"]`).click();
   const T=ladTruthEntries(q,part);
   for(let j=0;j<T.length;j++){const e=T[j],idx=j+1;
    if(e.s===null){const b=document.querySelector(`[data-rest="${e.t}"]`);if(!b||b.getAttribute('aria-disabled')==='true'){stuck='rest '+e.t;break}b.click();continue}
    const lb=document.querySelector(`[data-len="${e.t}"]`);if(!lb||lb.getAttribute('aria-disabled')==='true'){stuck='length '+e.t+' not live at note '+j;break}
    if(lb.getAttribute('aria-checked')!=='true')lb.click();
    let nm=e.s;if(part==='mel'&&q.l===9&&mod==='move'&&q.readings&&idx>q.pivot)nm=q.readings.move[idx];
    const rb=document.querySelector(`[data-earsol="${nm}"]`);if(!rb){stuck='no row '+nm;break}rb.click();
    if(part==='mel'&&q.l===9&&mod==='move'&&q.readings&&idx===q.pivot){const m=document.querySelector('[data-earmut]');if(!m||m.disabled){stuck='no mutation button';break}m.click()}}
   if(stuck)break}
  if(stuck){bad.push({stuck,a:q.a.join(' ')});continue}
  if(!earFull(q)){bad.push({stuck:'not full',a:q.a.join(' ')});continue}
  earCheck();n++;if(EAR.res.kind!=='ok')bad.push({kind:EAR.res.kind,a:q.a.join(' ')})}
 return{l,mod,n,nbad:bad.length,bad:bad.slice(0,3)}}"""

E2E_RHY = """([l,N])=>{const bad=[];let n=0;
 for(let i=0;i<N;i++){EAR.drill='rhy';EAR.lvl.rhy=l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();const q=EAR.q;let stuck=null;
  for(const k of q.a){const b=document.querySelector(`.el-tile[data-earcell="${k}"]`);if(!b||b.disabled){stuck=k+(b?' disabled':' missing');break}b.click()}
  if(!stuck&&q.drums){const T=ladDrumOns(q.drums);for(const key of['kick','snare'])for(const t of T[key]){const b=document.querySelector(`[data-eardrum="${key}:${t}"]`);if(!b){stuck='drum '+key+t;break}b.click()}}
  if(stuck){bad.push({stuck,metre:q.metre,a:q.a.join(' ')});continue}
  earCheck();n++;if(EAR.res.kind!=='ok')bad.push({kind:EAR.res.kind,a:q.a.join(' ')})}
 return{l,n,nbad:bad.length,bad:bad.slice(0,3)}}"""

# a melody scene: write the first part of the right answer, optionally spoil one note, optionally check
SCENE = """([l,mod,frac,spoil,chk,wantS])=>{EAR.mod=mod;const want=wantS?new Function('q','return '+wantS):null;let q;
 for(let t=0;t<300;t++){EAR.drill='mel';EAR.lvl.mel=l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();q=EAR.q;if(!want||want(q))break}
 const parts=q.l===11?['mel','bass']:['mel'];
 for(const part of parts){if(q.l===11&&EAR.part!==part)document.querySelector(`[data-earpart="${part}"]`).click();
  const T=ladTruthEntries(q,part),n=Math.floor(T.length*frac);
  for(let j=0;j<n;j++){const e=T[j],idx=j+1;if(e.s===null){document.querySelector(`[data-rest="${e.t}"]`).click();continue}
   const lb=document.querySelector(`[data-len="${e.t}"]`);if(lb.getAttribute('aria-checked')!=='true')lb.click();
   let nm=e.s;if(q.l===9&&mod==='move'&&q.readings&&idx>q.pivot)nm=q.readings.move[idx];
   if(spoil&&j===spoil&&part==='mel')nm=[...document.querySelectorAll('[data-earsol]')].map(x=>x.dataset.earsol).find(x=>x!==nm&&!/[a-z]{2}/.test(x))||nm;
   document.querySelector(`[data-earsol="${nm}"]`).click();
   if(q.l===9&&mod==='move'&&q.readings&&idx===q.pivot&&frac>.45)document.querySelector('[data-earmut]').click()}}
 if(chk)earCheck();return{l:q.l}}"""

SMALL = """()=>{const out=[];[...document.querySelectorAll('#earMain *')].forEach(e=>{if(!e.offsetParent&&!(e instanceof SVGElement))return;
 const t=[...e.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim()).length;if(!t)return;const cs=getComputedStyle(e),fs=parseFloat(cs.fontSize),r=e.getBoundingClientRect();
 if(r.width&&fs<10.95&&cs.visibility!=='hidden'&&cs.display!=='none'&&!(e instanceof SVGElement))out.push((e.className||e.tagName)+':'+e.textContent.trim().slice(0,16)+':'+fs)});
 document.querySelectorAll('#earMain svg text').forEach(t=>{const sv=t.closest('svg');if(!sv.getBoundingClientRect().width)return;const r=t.getBoundingClientRect(),fs=parseFloat(getComputedStyle(t).fontSize);
  const vb=sv.viewBox&&sv.viewBox.baseVal,sc=vb&&vb.width?sv.getBoundingClientRect().width/vb.width:1;if(fs*sc<10.9&&r.width)out.push('svg text '+t.textContent.slice(0,10)+':'+(fs*sc).toFixed(1))});return out}"""
TARGETS = """()=>{const bad=[];document.querySelectorAll('#earMain button').forEach(b=>{if(!b.offsetParent)return;const r=b.getBoundingClientRect();if(r.width<1||b.closest('.el-foot'))return;
 if(r.height<43.5||r.width<43.5)bad.push((b.className||b.tagName)+':'+b.textContent.trim().slice(0,14)+':'+Math.round(r.width)+'x'+Math.round(r.height))});return bad}"""
COUNT = "(s)=>document.querySelectorAll('#earMain '+s).length"
OVER = "document.documentElement.scrollWidth-innerWidth"

async def page(b, w, h):
    pg = await b.new_page(viewport={'width': w, 'height': h})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.route('**/*', cjg.make_route(REPO))
    await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    await pg.evaluate(PRE); await pg.evaluate(STUB)
    return pg, errs

async def run(p):
    b = await cjg.launch(p)
    pg, errs = await page(b, 1366, 900)
    # ---- U1
    o = await pg.evaluate(UNIT)
    check(o['win'] == '1111111100' or o['win'] == '11111111' + '00' or o['win'] == '1111111100', f"U1 window {o['win']}")
    check(o['rdy'] == [True, False, False], f"U1 ready {o['rdy']}")
    check(o['now1'] is True and 'Rung 5 starts Stage 5' in o['html'] and 'Ready for rung 5?' in o['html'], f"U1 suggestion row {o['html'][:200]}")
    check(o['reached'] == [4], f"U1 dot earned {o['reached']}")
    check(o['now2'] is False, 'U1 the row shows once per climb')
    check(o['reachedKept'] is True, 'U1 the dot stays once earned')
    check(o['within'] is False, 'U1 a suggestion inside a Stage has no "starts Stage" wording')
    # ---- U2
    o = await pg.evaluate(LENLIVE)
    check(o['nbad'] == 0, f"U2 earLenLive over {o['n']} checks: {o['bad']}")
    # ---- E2E
    for l in range(4, 13):
        for mod in (('home', 'move') if l == 9 else ('home',)):
            r = await pg.evaluate(E2E_MEL, [l, mod, 12])
            check(r['nbad'] == 0 and r['n'] == 12, f"E2E melody rung {l} ({mod}): {r}")
    for l in range(1, 11):
        r = await pg.evaluate(E2E_RHY, [l, 25])
        check(r['nbad'] == 0 and r['n'] == 25, f"E2E rhythm rung {l}: {r}")
    check(not errs, f'page errors {errs[:3]}')
    await pg.close()
    # ---- V: the new views
    VIEWS = [('mel entry r6', 6, 'home', .6, 0, 0, None), ('mel result r6', 6, 'home', 1, 3, 1, None),
             ('mel r7 gauge result', 7, 'home', 1, 5, 1, 'q.aug2&&q.aug2.length'), ('mel r8 entry', 8, 'home', .5, 0, 0, None),
             ('mel r9 move entry', 9, 'move', .7, 0, 0, "q.readings&&q.kind==='M-V'"), ('mel r9 move result', 9, 'move', 1, 0, 1, "q.readings&&q.kind==='M-V'"),
             ('mel r10', 10, 'home', .5, 0, 0, None), ('mel r11', 11, 'home', .5, 0, 0, None), ('mel r12', 12, 'home', .5, 0, 0, None)]
    for w, h in ((1366, 900), (390, 844)):
        pg, errs = await page(b, w, h)
        for tag, l, mod, frac, spoil, chk, want in VIEWS:
            await pg.evaluate(SCENE, [l, mod, frac, spoil, bool(chk), want]); await pg.wait_for_timeout(150)
            t = f'{w}px {tag}'
            check(not await pg.evaluate(SMALL), f'{t}: text under 11 px {(await pg.evaluate(SMALL))[:3]}')
            check(await pg.evaluate(OVER) <= 0, f'{t}: sideways scroll {await pg.evaluate(OVER)}')
            check(await pg.evaluate(COUNT, '.el-bandtab') >= 1 and await pg.evaluate(COUNT, '.el-rungline') == 1, f'{t}: picker and rung line')
            if not chk: check(await pg.evaluate(COUNT, '.el-len') >= (1 if l == 11 else 3), f'{t}: palette cells')
            if mod == 'move' and not chk: check(await pg.evaluate(COUNT, '.el-mut') == 1, f'{t}: mutation button only under Move do')
            if mod == 'home' and l == 9: check(await pg.evaluate(COUNT, '.el-mut') == 0, f'{t}: no mutation button under Keep home do')
            if w < 500:
                tg = await pg.evaluate(TARGETS); check(not tg, f'{t}: targets under 44 px {tg[:5]}')
        # the picker: phones fold to tabs (.el-bandtab), "n more" chip (.el-bandmore) appears when the Stage hides rungs
        await pg.evaluate("EAR.drill='mel';EAR.lvl.mel=4;EAR.q=null;EAR.done=false;S.level=4;EAR.all=false;renderEar()")
        check(await pg.evaluate(COUNT, '.el-bandmore') >= 1, f'{w}px picker: .el-bandmore when Stage 4 hides rungs')
        # rhythm views
        await pg.evaluate("S.level=6;EAR.all=false")
        for l in (4, 7, 8, 9, 10):
            await pg.evaluate("""(l)=>{EAR.drill='rhy';EAR.lvl.rhy=l;EAR.q=null;EAR.done=false;EAR.res=null;earNew()}""", l); await pg.wait_for_timeout(120)
            t = f'{w}px rhythm r{l}'
            check(not await pg.evaluate(SMALL), f'{t}: text under 11 px {(await pg.evaluate(SMALL))[:3]}')
            check(await pg.evaluate(OVER) <= 0, f'{t}: sideways scroll {await pg.evaluate(OVER)}')
            if l >= 7: check(await pg.evaluate(COUNT, '.grp.set .el-seg button') == 2, f'{t}: names setting from rung 7')
            if l < 7: check(await pg.evaluate(COUNT, '.grp.set') == 0, f'{t}: no names setting below rung 7')
            if w < 500:
                tg = await pg.evaluate(TARGETS); check(not tg, f'{t}: targets under 44 px {tg[:5]}')
            await pg.evaluate("earCheck()") if await pg.evaluate("earFull(EAR.q)") else await pg.evaluate("earMark(false,null);renderEar()")
            await pg.wait_for_timeout(120)
            check(not await pg.evaluate(SMALL), f'{t} result: text under 11 px {(await pg.evaluate(SMALL))[:3]}')
            check(await pg.evaluate(OVER) <= 0, f'{t} result: sideways scroll')
        check(not errs, f'{w}px page errors {errs[:3]}')
        await pg.close()
    await b.close()

async def main():
    async with async_playwright() as p:
        await run(p)
    print(json.dumps({'checks': N[0], 'failures': FAILS[:30], 'n_failures': len(FAILS)}, indent=1, ensure_ascii=False))
    sys.exit(1 if FAILS else 0)
asyncio.run(main())
