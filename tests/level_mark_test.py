"""0.50 Fable fix: self-checks for the design-check fixes (the builder's own).
Run: python3 tests/level_mark_test.py <repo dir>

  M1  the "your level" disc (.lvm.now) survives stopAll(): on #lvBtn, the checked row of the level list (popover and More sheet),
      the "New at Level n" header and the Ear Lab picker caption; after load, after a rail click, after Play in the Ear Lab, after Stop.
      "Playing now" marks (.now without .lvm) are still cleared by stopAll().
  M2  Chord Library side panel at 1100x700, 1280x800, 1366x768, 1440x900, Levels 1, 4, 7: Root, the selected row and Inversion on screen,
      the panel inside the window, the panel itself not scrolled, only the list scrolls, no sideways scroll
  S1  Esc on the Curriculum select closes the level popover (focus back on the button); Tab out of the popover closes it
  S2  after a rung-tab press focus is on that tab        S3  after a chord type is picked in the sheet focus is on the chord-type button
  S4  tablet sheet rows >= 46 px, band headers >= 44 px  S6  no "null" in the melody instruction before the first Play
  A   a run of two unwritten rungs reads "Rungs a and b, not yet written"
  S7  compact climb cards show the title and the family, no "Climb n" (text and aria-label); full cards and the climb page keep the number
  S8  Chord Library above its highest written level: "No new chord types at Level n yet: they arrive in a later update. ..."
"""
import sys, asyncio, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

N = [0]; FAILS = []
def check(c, m):
    N[0] += 1
    if not c: FAILS.append(m)

MARKS = """()=>{const c=s=>{const e=document.querySelector(s);return e?e.classList.contains('now'):null};
 return{btn:c('#lvBtn .lvm'),pop:c('#lvPop .lvopt[aria-checked="true"] .lvm'),sheet:c('#msLvl .lvopt[aria-checked="true"] .lvm'),
  popOther:document.querySelectorAll('#lvPop .lvopt:not([aria-checked="true"]) .lvm.now').length,level:S.level,btnText:document.querySelector('#lvBtn .lvm').textContent.trim()}}"""
PANEL = """()=>{const r=e=>{const b=e.getBoundingClientRect();return[Math.round(b.top),Math.round(b.bottom)]},pk=document.getElementById('picker'),l=document.getElementById('qualList');
 return{win:innerHeight,panel:r(pk),panelScroll:pk.scrollTop,panelOver:pk.scrollHeight-pk.clientHeight,rootLbl:r(pk.querySelector('.plbl')),root:r(document.getElementById('rootPads')),
  sel:r(l.querySelector('.lvrow.on')),list:r(l),listScrolls:l.scrollHeight>l.clientHeight,listOv:getComputedStyle(l).overflowY,inv:r(document.getElementById('invPads')),
  over:document.documentElement.scrollWidth-document.documentElement.clientWidth}}"""

async def page(b, w, h, errs):
    pg = await b.new_page(viewport={'width': w, 'height': h})
    pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.route('**/*', cjg.make_route(REPO))
    await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    return pg

def marks_ok(m, where):
    check(m['btn'] is True, f'M1 {where}: #lvBtn .lvm lost .now')
    check(m['pop'] is True, f'M1 {where}: checked row in the popover lost .now')
    check(m['sheet'] is True, f'M1 {where}: checked row in the More sheet lost .now')
    check(m['popOther'] == 0, f'M1 {where}: {m["popOther"]} other rows carry .now')
    check(m['btnText'] == str(m['level']), f'M1 {where}: button shows {m["btnText"]}, level is {m["level"]}')

async def run():
    async with async_playwright() as p:
        b = await cjg.launch(p); errs = []
        # ---- M1 ----
        pg = await page(b, 1366, 768, errs)
        marks_ok(await pg.evaluate(MARKS), 'fresh load')
        for lv in (2, 6):
            await pg.evaluate("(l)=>document.querySelector('#lvPop .lvopt[data-l=\"'+l+'\"]').click()", lv); await pg.wait_for_timeout(80)
            marks_ok(await pg.evaluate(MARKS), f'level {lv} picked')
            for rm in ('keys', 'climbs', 'forms', 'ear', 'seed'):
                await pg.evaluate("(r)=>document.querySelector('.rail button[data-room=\"'+r+'\"]').click()", rm); await pg.wait_for_timeout(120)
                marks_ok(await pg.evaluate(MARKS), f'level {lv}, rail click {rm}')
                if rm in ('seed', 'keys'):
                    hd = await pg.evaluate("(r)=>{const e=document.querySelector('#room-'+r+' h3.lvbh .lvm');return e?e.classList.contains('now'):null}", rm)
                    check(hd is not False, f'M1 level {lv}: "New at Level" header mark in {rm} lost .now')
        await pg.reload(); await pg.wait_for_timeout(900)
        marks_ok(await pg.evaluate(MARKS), 'reload with a stored level')
        # Play in the Ear Lab, at the learner's own level so the caption disc is shown
        await pg.evaluate("()=>{lvlSet(4);EAR.drill='mel';EAR.lvl={};EAR.band=0;EAR.q=null;EAR.done=false;location.hash='ear';room('ear');renderEar()}"); await pg.wait_for_timeout(200)
        cap = "()=>{const e=document.querySelector('#earMain .el-lg.you .el-lgcap .lvm');return e?e.classList.contains('now'):null}"
        check(await pg.evaluate(cap) is True, 'M1 Ear Lab: caption disc before Play')
        await pg.click('#earMain [data-earplay="all"]'); await pg.wait_for_timeout(700)
        check(await pg.evaluate("()=>!!EAR.q") is True, 'M1 Ear Lab: Play made no question')
        check(await pg.evaluate(cap) is True, 'M1 Ear Lab: caption disc after Play'); marks_ok(await pg.evaluate(MARKS), 'after Play')
        await pg.evaluate("()=>stopAll()"); await pg.wait_for_timeout(100)
        check(await pg.evaluate(cap) is True, 'M1 Ear Lab: caption disc after Stop'); marks_ok(await pg.evaluate(MARKS), 'after Stop')
        # "playing now" marks are still cleared
        left = await pg.evaluate("()=>{const d=document.createElement('div');d.className='bar now';document.body.appendChild(d);stopAll();const n=document.querySelectorAll('.now:not(.lvm)').length;d.remove();return n}")
        check(left == 0, f'M1: stopAll left {left} playing marks')
        # ---- S6 ----
        await pg.evaluate("()=>{EAR.q=null;EAR.done=false;renderEar()}")
        for lv in (1, 4, 7):
            await pg.evaluate("(l)=>{lvlSet(l);EAR.lvl={};EAR.q=null;renderEar()}", lv)
            for d in ('mel', 'rhy'):
                await pg.evaluate("(d)=>{EAR.drill=d;EAR.q=null;renderEar()}", d)
                t = await pg.evaluate("()=>document.getElementById('earMain').innerText")
                check('null' not in t and 'undefined' not in t and 'NaN' not in t, f'S6 {d} L{lv}: null/undefined/NaN in the card text')
                if d == 'mel' and 'count you in' in t: check('then clicks count you in' in t or 'counts you in' in t, f'S6 mel L{lv}: instruction wording')
        # ---- A: two unwritten rungs ----
        seen = set()
        for d in ('metre', 'rhy', 'qual', 'cad', 'bass', 'mel', 'blind'):
            await pg.evaluate("(d)=>{EAR.drill=d;EAR.q=null;renderEar()}", d)
            for al, n in await pg.evaluate("()=>[...document.querySelectorAll('#earMain .el-ny')].map(e=>[e.getAttribute('aria-label'),+e.style.getPropertyValue('--n')])"):
                seen.add(n); a = al.split(',')[0]
                check((n == 1 and a.startswith('Rung ') and ' ' not in a[5:]) or (n == 2 and ' and ' in a and ' to ' not in a) or (n == 3 and ' to ' in a), f'A {d}: "{al}" for a run of {n}')
                if n == 2: x, y = a[6:].split(' and '); check(int(y) == int(x) + 1, f'A {d}: "{al}"')
        check(seen == {1, 2, 3}, f'A: run lengths seen {seen}')
        # ---- S1 ----
        await pg.evaluate("()=>{location.hash='seed';room('seed')}"); await pg.wait_for_timeout(100)
        await pg.click('#lvBtn'); check(await pg.evaluate("()=>!lvPop.hidden&&document.activeElement.classList.contains('lvopt')"), 'S1: popover opens with focus on a row')
        await pg.keyboard.press('Escape'); check(await pg.evaluate("()=>lvPop.hidden&&document.activeElement.id==='lvBtn'"), 'S1: Esc on a row closes, focus on the button')
        await pg.click('#lvBtn'); await pg.focus('#lvCur'); await pg.keyboard.press('Escape')
        check(await pg.evaluate("()=>lvPop.hidden&&document.activeElement.id==='lvBtn'&&lvBtn.getAttribute('aria-expanded')==='false'"), 'S1: Esc on the Curriculum select closes, focus on the button')
        await pg.click('#lvBtn'); await pg.focus('#lvCur'); await pg.keyboard.press('Tab'); await pg.wait_for_timeout(50)
        check(await pg.evaluate("()=>lvPop.hidden&&!document.activeElement.closest('.lvc')"), 'S1: Tab out of the popover closes it')
        await pg.click('#lvBtn'); await pg.keyboard.press('Tab'); await pg.wait_for_timeout(50)
        check(await pg.evaluate("()=>!lvPop.hidden&&document.activeElement.id==='lvCur'"), 'S1: Tab from a row to the select keeps the popover open')
        await pg.select_option('#lvCur', index=0); check(await pg.evaluate("()=>!lvPop.hidden"), 'S1: changing the curriculum keeps the popover open')
        await pg.keyboard.press('Escape'); await pg.evaluate("()=>{localStorage.removeItem('cjg_curric')}")
        await pg.close()
        # ---- M2 ----
        for w, h in ((1100, 700), (1280, 800), (1366, 768), (1440, 900)):
            pg = await page(b, w, h, errs); await pg.evaluate("localStorage.clear()"); await pg.reload(); await pg.wait_for_timeout(900)
            for lv in (None, 1, 4, 7):
                if lv: await pg.evaluate("(l)=>{lvlSet(l);render()}", lv); await pg.wait_for_timeout(150)
                types = await pg.evaluate("()=>[...document.querySelectorAll('#qualList [data-pq]')].map(e=>e.dataset.pq)")
                for q in ([None] if lv is None else [types[0], types[len(types) // 2], types[-1]]):
                    if q is not None: await pg.evaluate("(q)=>document.querySelector('#qualList [data-pq=\"'+q+'\"]').click()", q); await pg.wait_for_timeout(120)
                    g = await pg.evaluate(PANEL); t = f'M2 {w}x{h} L{lv or "fresh"} {q!r}'
                    check(g['panel'][1] <= g['win'] and g['panel'][0] >= 0, f'{t}: panel {g["panel"]} outside the {g["win"]} px window')
                    check(g['panelScroll'] == 0 and g['panelOver'] <= 1, f'{t}: the panel itself scrolls ({g["panelScroll"]}, {g["panelOver"]})')
                    check(g['rootLbl'][0] >= g['panel'][0] and g['root'][1] <= g['list'][0], f'{t}: Root {g["rootLbl"]} {g["root"]} not pinned above the list {g["list"]}')
                    check(g['sel'][0] >= g['list'][0] - 1 and g['sel'][1] <= g['list'][1] + 1, f'{t}: selected row {g["sel"]} outside the list {g["list"]}')
                    check(g['inv'][0] >= g['list'][1] and g['inv'][1] <= g['panel'][1], f'{t}: Inversion {g["inv"]} not pinned below the list {g["list"]} in {g["panel"]}')
                    check(g['listOv'] == 'auto' and g['list'][1] - g['list'][0] >= 120, f'{t}: list area {g["list"]}')
                    check(g['over'] <= 0, f'{t}: sideways scroll {g["over"]}')
            await pg.evaluate("window.scrollTo(0,500)"); await pg.wait_for_timeout(120); g = await pg.evaluate(PANEL)
            check(g['panel'][0] >= 0 and g['panel'][1] <= g['win'] and g['inv'][1] <= g['win'], f'M2 {w}x{h} scrolled: panel {g["panel"]}')
            await pg.close()
        # ---- S2 (rung tabs, 900 px and under) ----
        for w, h in ((820, 1180), (390, 844)):
            pg = await page(b, w, h, errs)
            await pg.evaluate("()=>{lvlSet(4);EAR.drill='mel';EAR.lvl={};EAR.band=0;EAR.q=null;location.hash='ear';room('ear');renderEar()}"); await pg.wait_for_timeout(200)
            for k in (2, 6, 4):
                r0 = await pg.evaluate("()=>EAR.lvl.mel")
                await pg.click(f'#earMain .el-ltab[data-band="{k}"]'); await pg.wait_for_timeout(60)
                check(await pg.evaluate("(k)=>{const a=document.activeElement;return a.classList.contains('el-ltab')&&+a.dataset.band===k&&a.getAttribute('aria-expanded')==='true'}", k), f'S2 {w}: focus after tab {k}')
                check(await pg.evaluate("()=>EAR.lvl.mel") == r0, f'S2 {w}: tab {k} changed the rung')
            await pg.focus('#earMain .el-ltab[data-band="4"]'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(60)
            check(await pg.evaluate("()=>document.activeElement.classList.contains('el-ltab')&&document.activeElement.dataset.band==='4'"), f'S2 {w}: focus after Enter on a tab')
            await pg.close()
        # ---- S3, S4 (chord-type sheet under 1100 px) ----
        for w, h in ((1024, 768), (820, 1180), (390, 844)):
            pg = await page(b, w, h, errs); await pg.evaluate("()=>{lvlSet(4);render()}"); await pg.wait_for_timeout(120)
            await pg.click('#qualBtn'); await pg.wait_for_timeout(120)
            hs = await pg.evaluate("()=>({row:[...document.querySelectorAll('#qsheet .lvrow')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height),bh:[...document.querySelectorAll('#qsheet .lvbh')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height)})")
            check(len(hs['row']) > 3 and min(hs['row']) >= 45.5, f'S4 {w}: sheet rows {min(hs["row"] or [0])} px')
            check(len(hs['bh']) > 0 and min(hs['bh']) >= 43.5, f'S4 {w}: sheet band headers {min(hs["bh"] or [0])} px')
            q = await pg.evaluate("()=>{const e=[...document.querySelectorAll('#qsheet [data-pq]')].filter(e=>e.offsetParent&&!e.classList.contains('on'))[0];e.click();return e.dataset.pq}"); await pg.wait_for_timeout(120)
            check(await pg.evaluate("(q)=>qsheet.hidden&&S.q===q&&document.activeElement.id==='qualBtn'&&document.activeElement.isConnected", q), f'S3 {w}: after picking {q!r} focus is not on the chord-type button')
            await pg.click('#qualBtn'); await pg.keyboard.press('Escape'); check(await pg.evaluate("()=>qsheet.hidden&&document.activeElement.id==='qualBtn'"), f'S3 {w}: Esc returns focus')
            check(await pg.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth") <= 0, f'S3 {w}: sideways scroll')
            await pg.close()
        # ---- S7 (compact climb cards), S8 (empty "New" band above what is built) ----
        pg = await page(b, 1366, 768, errs)
        for lv in (1, 3, 5, 7):
            await pg.evaluate("(l)=>{lvlSet(l);location.hash='climbs';room('climbs')}", lv); await pg.wait_for_timeout(150)
            c = await pg.evaluate("()=>({cmp:[...document.querySelectorAll('#climbList .climb.cmp')].map(e=>[e.querySelector('.tx b').textContent,e.querySelector('.tx small').textContent,e.getAttribute('aria-label')||'']),full:[...document.querySelectorAll('#climbList .lvband.new .climb')].map(e=>!!e.querySelector('.n')&&/^\\d+$/.test(e.querySelector('.n').textContent.trim()))})")
            check(len(c['cmp']) > 0, f'S7 L{lv}: no compact cards')
            for t, sm, al in c['cmp']:
                check('Climb' not in sm and not any(ch.isdigit() for ch in sm) and sm.strip() != '', f'S7 L{lv}: compact small line "{sm}"')
                check(not al.startswith('Climb ') and al.startswith(t), f'S7 L{lv}: compact aria-label "{al}"')
            check(all(c['full']), f'S7 L{lv}: a full card lost its number')
        await pg.evaluate("()=>document.querySelector('#climbList [data-clopen]').click()"); await pg.wait_for_timeout(200)
        check(__import__('re').search(r'climb \d+', (await pg.evaluate("()=>document.getElementById('climbDetail').innerText.slice(0,400)")).lower()) is not None, 'S7: the climb page keeps "Climb n"')
        await pg.evaluate("()=>{location.hash='seed';room('seed')}")
        top = await pg.evaluate("()=>Math.max(...qualItems().map(x=>x.l||1))")
        for lv in range(1, 8):
            await pg.evaluate("(l)=>{lvlSet(l);render()}", lv); await pg.wait_for_timeout(60)
            o = await pg.evaluate("()=>{const n=document.querySelector('#qualList .lvband.new');const p=n.querySelector('.lvnone');return{none:p?p.textContent:null,rows:n.querySelectorAll('.lvrow').length,met:document.querySelectorAll('#qualList .lvband.met .lvrow').length}}")
            if lv > top:
                check(o['none'] == f'No new chord types at Level {lv} yet: they arrive in a later update. Everything you have met is below.' and o['rows'] == 0 and o['met'] > 0, f'S8 L{lv}: "{o["none"]}"')
            elif o['rows']: check(o['none'] is None, f'S8 L{lv}: empty line beside {o["rows"]} rows')
            else: check(o['none'] == f'No new chord types at Level {lv}. Everything you have met is below.', f'S8 L{lv}: "{o["none"]}"')
        check(top < 7, f'S8: the library now reaches Level {top}; the later-update line is no longer exercised')
        # a list that has not opted in keeps the plain line
        await pg.evaluate("()=>{lvlSet(7);location.hash='keys';room('keys')}"); await pg.wait_for_timeout(150)
        for t in await pg.evaluate("()=>[...document.querySelectorAll('#room-keys .lvnone')].map(e=>e.textContent)"): check('later update' not in t, f'S8 keys: "{t}"')
        await pg.close()
        check(not errs, f'page errors {errs[:3]}')
        await b.close()

asyncio.run(run())
print(f'level_mark_test: {N[0]} checks, {len(FAILS)} failed')
for f in FAILS[:40]: print('  FAIL', f)
sys.exit(1 if FAILS else 0)
