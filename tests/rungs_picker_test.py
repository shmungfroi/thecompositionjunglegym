"""Ear Lab 21-rung picker (0.50 V10): self-checks (the builder's own).
Run: python3 tests/rungs_picker_test.py <repo dir>

  P1  every drill, every learner level 1-7: 7 level groups, 21 slots, written slots match EARSLOT, number = 3*(level-1)+step
  P2  first visit: first written rung at the learner's level, else the nearest written rung below, else the lowest (rule written out here, not read from the app)
  P3  the open tab on entering a drill is the level of the rung in use; a tab click opens a level and does not change the rung
  P4  the suggestion (8 of the last 10) points to the next WRITTEN rung, skipping 'not yet' slots
  P5  changing the learner's level (the real level buttons) moves only the `you` mark, never the rung in use
  P6  labels and wording: drill sub-label, card tag, rung line (with and without the curriculum bracket), aria-labels
  P7  geometry at 1440, 1366x768, 1280x800, 1024, 900, 820, 390, 360: one row over 900 px, no sideways scroll, phone targets >= 44 px high,
      360 px tabs >= 40 px wide; screenshots to tests/reports/rungs_050/
"""
import sys, asyncio, pathlib, re, json
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

SLOT = {'metre': [2, 5, 8], 'rhy': [2, 4, 5, 7, 8, 9, 11, 13, 15, 16], 'qual': [1, 7, 13], 'cad': [4, 5, 13, 7], 'bass': [3, 4, 10],
        'mel': [2, 3, 4, 5, 6, 9, 10, 12, 13, 15, 16, 18, 7], 'blind': [7, 10, 13]}
# 0.50 ICfix: SLOT is in internal order (as EARSLOT): the split-off rungs cad 4 (place 7) and mel 13 (place 7) are appended.
BYPLACE = {d: sorted(range(1, len(a) + 1), key=lambda n: a[n - 1]) for d, a in SLOT.items()}
LVN = ['', 'First steps', 'Foundation', 'Developing', 'Intermediate', 'Senior', 'Advanced', 'Extension']
N = [0]; FAILS = []
def check(c, m):
    N[0] += 1
    if not c: FAILS.append(m)
lvl = lambda p: -(-p // 3)
def first_visit(d, lv):
    a = sorted(SLOT[d])
    at = [p for p in a if lvl(p) == lv]
    if at: return at[0]
    below = [p for p in a if lvl(p) < lv]
    return below[-1] if below else a[0]

# read the picker out of the DOM: per group, the slots in order (button place, or a run of 'not yet')
READ = """()=>{const out={groups:[],on:null,open:null,you:null,sug:[],tabsug:[],rungline:document.querySelector('#earMain .el-rungline').textContent,
  rungHTML:document.querySelector('#earMain .el-rungline').innerHTML,drillSub:[...document.querySelectorAll('#earMain .el-drill small')].map(e=>e.textContent),tag:document.querySelector('#earMain .el-tag').textContent,
  old:document.querySelectorAll('#earMain .el-rungs,#earMain .el-band,#earMain .el-bandtab,#earMain .el-bandmore,#earMain .el-all,#earMain [data-earall]').length};
 document.querySelectorAll('#earMain .el-lg').forEach((g,i)=>{const cells=[...g.querySelectorAll('.el-lgr > *')].map(c=>c.tagName==='BUTTON'?{b:+c.textContent,n:+c.dataset.earlv,on:c.classList.contains('on'),sug:c.classList.contains('sug'),pressed:c.getAttribute('aria-pressed'),al:c.getAttribute('aria-label')}:{ny:+c.style.getPropertyValue('--n'),al:c.getAttribute('aria-label'),txt:c.textContent});
  const t=g.querySelector('.el-ltab');out.groups.push({i:i+1,cells,you:g.classList.contains('you'),none:g.classList.contains('none'),open:g.classList.contains('open'),tab:{band:+t.dataset.band,exp:t.getAttribute('aria-expanded'),al:t.getAttribute('aria-label'),has:t.classList.contains('has'),sug:t.classList.contains('sug'),you:t.classList.contains('you'),none:t.classList.contains('none')},al:g.getAttribute('aria-label')})});
 return out}"""
SETUP = "([d,lv])=>{localStorage.removeItem('cjg_curric');lvlSet(lv);EAR.drill=d;EAR.lvl={};EAR.band=0;EAR.rd={};EAR.reached={};EAR.q=null;EAR.done=false;EAR.st={};location.hash='ear';room('ear');renderEar()}"

def slots_of(g):
    out = []
    for c in g['cells']:
        if 'b' in c: out.append(('b', c))
        else: out += [('ny', c)] * c['ny']
    return out

async def page(b, w, h, errs=None):
    pg = await b.new_page(viewport={'width': w, 'height': h})
    if errs is not None: pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.route('**/*', cjg.make_route(REPO))
    await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    return pg

async def logic(b):
    errs = []
    pg = await page(b, 1366, 768, errs)
    for d in SLOT:
        for lv in range(1, 8):
            await pg.evaluate(SETUP, [d, lv]); await pg.wait_for_timeout(30)
            o = await pg.evaluate(READ); t = f'{d} @L{lv}'
            # P1
            check(o['old'] == 0, f'{t}: old picker markup present')
            check(len(o['groups']) == 7, f'{t}: {len(o["groups"])} level groups')
            allslots = [s for g in o['groups'] for s in slots_of(g)]
            check(len(allslots) == 21, f'{t}: {len(allslots)} slots')
            places = []
            for g in o['groups']:
                sl = slots_of(g)
                check(len(sl) == 3, f'{t}: level {g["i"]} has {len(sl)} slots')
                check(g['tab']['band'] == g['i'] and g['al'] == f'Level {g["i"]}, {LVN[g["i"]]}', f'{t}: group label {g["al"]}')
                pos = 0
                for c in g['cells']:
                    p = 3 * (g['i'] - 1) + pos + 1
                    if 'ny' not in c:
                        pos += 1
                        places.append(p)
                        check(c['b'] == p, f'{t}: level {g["i"]} step {p - 3*(g["i"]-1)} shows {c["b"]}, expected {p}')
                        check(SLOT[d][c['n'] - 1] == p, f'{t}: button {c["b"]} carries internal rung {c["n"]} = place {SLOT[d][c["n"]-1]}')
                        check(c['al'].startswith(f'Rung {p}, Level {g["i"]}'), f'{t}: aria {c["al"]}')
                    else:
                        pos += c['ny']
                        check(c['al'] in (f'Rung {p}, not yet written', f'Rungs {p} to {p + c["ny"] - 1}, not yet written') and c['txt'] == 'not yet', f'{t}: not-yet cell {c["al"]} / {c["txt"]}')
                check(g['none'] == (not any(k == 'b' for k, _ in sl)), f'{t}: .none on level {g["i"]}')
                check(g['you'] == (g['i'] == lv) and g['tab']['you'] == (g['i'] == lv), f'{t}: .you mark on level {g["i"]}')
                runs = [c for c in g['cells'] if 'ny' in c]
                check(sum(1 for c in g['cells'] if 'ny' in c) <= 2, f'{t}: runs')
                if g['none']: check(len(g['cells']) == 1 and g['cells'][0]['ny'] == 3, f'{t}: empty level is one cell of 3')
            check(places == sorted(SLOT[d]), f'{t}: written places {places} != EARSLOT {sorted(SLOT[d])}')
            # P2 + P3
            want = first_visit(d, lv)
            ons = [c['b'] for g in o['groups'] for k, c in slots_of(g) if k == 'b' and c['on']]
            check(ons == [want], f'{t}: first visit on rung {ons}, expected {want}')
            opens = [g['i'] for g in o['groups'] if g['open']]
            check(opens == [lvl(want)], f'{t}: open tab {opens}, expected {lvl(want)}')
            check([g['i'] for g in o['groups'] if g['tab']['has']] == [lvl(want)], f'{t}: .has on the tab of the rung in use')
            check(o['rungline'].startswith(f'Rung {want} of 21 · Level {lvl(want)}, {LVN[lvl(want)]}'), f'{t}: rung line {o["rungline"][:60]}')
    check(not errs, f'page errors {errs[:3]}')
    # P3: tabs open a level without changing the rung
    for d in ('mel', 'cad'):
        await pg.evaluate(SETUP, [d, 4]); r0 = await pg.evaluate("(d)=>EAR.lvl[d]", d)
        for k in (1, 7, 3):
            await pg.evaluate("(k)=>document.querySelector('#earMain .el-ltab[data-band=\"'+k+'\"]').click()", k)
            o = await pg.evaluate(READ)
            check([g['i'] for g in o['groups'] if g['open']] == [k] and [g['tab']['exp'] for g in o['groups'] if g['i'] == k] == ['true'] and sum(g['tab']['exp'] == 'true' for g in o['groups']) == 1, f'{d}: tab {k} opens exactly its level')
            check(await pg.evaluate("(d)=>EAR.lvl[d]", d) == r0 and sum(1 for g in o['groups'] for c in g['cells'] if c.get('on')) == 1, f'{d}: tab {k} changed the rung in use')
        # clicking a rung closes nothing special: the open tab follows the rung in use again
        await pg.evaluate("()=>document.querySelector('#earMain [data-earlv]:not(.on)').click()")
        o = await pg.evaluate(READ); on = [g['i'] for g in o['groups'] for c in g['cells'] if c.get('on')]
        check([g['i'] for g in o['groups'] if g['open']] == on, f'{d}: after a rung click the open tab is the rung\'s level')
        # entering another drill opens the tab of that drill's rung
        await pg.evaluate("()=>document.querySelector('#earMain .el-ltab[data-band=\"7\"]').click()")
        await pg.evaluate("()=>document.querySelector('#earMain [data-eardr=\"qual\"]').click()")
        o = await pg.evaluate(READ); on = [g['i'] for g in o['groups'] for c in g['cells'] if c.get('on')]
        check([g['i'] for g in o['groups'] if g['open']] == on and len(on) == 1, f'{d} -> qual: open tab follows the rung in use')
    # P4: the suggestion skips 'not yet'
    for d in ('mel', 'rhy'):
        for j in range(len(BYPLACE[d]) - 1):
            n, m = BYPLACE[d][j], BYPLACE[d][j + 1]   # the next written rung by place
            await pg.evaluate(SETUP, [d, 4]); await pg.evaluate("([d,n])=>{EAR.lvl[d]=n;EAR.rd={[d]:{[n]:[1,1,1,1,1,1,1,1,0,1]}};renderEar()}", [d, n])
            o = await pg.evaluate(READ)
            sg = [c['b'] for g in o['groups'] for k, c in slots_of(g) if k == 'b' and c['sug']]
            nxt = SLOT[d][m - 1]
            check(sg == [nxt], f'{d} rung {SLOT[d][n-1]}: suggestion {sg}, expected next written {nxt}')
            check([g['i'] for g in o['groups'] if g['tab']['sug']] == [lvl(nxt)], f'{d} rung {SLOT[d][n-1]}: .sug on tab of level {lvl(nxt)}')
            check(all('suggested next' in c['al'] for g in o['groups'] for k, c in slots_of(g) if k == 'b' and c['sug']), f'{d}: aria suggested next')
            if nxt != SLOT[d][n-1] + 1: INFO.setdefault('gaps_skipped', []).append(f'{d} {SLOT[d][n-1]}->{nxt}')
    await pg.evaluate(SETUP, ['qual', 4]); await pg.evaluate("()=>{EAR.rd={qual:{1:[1,1,1,1,1,1,1,1,1,1]}};renderEar()}")
    o = await pg.evaluate(READ); check(not any(c.get('sug') for g in o['groups'] for c in g['cells']), 'qual: no readiness data, so no suggestion')
    # P5: the learner's level changes through the real level buttons; the rung in use stays
    for d, lv0 in (('mel', 4), ('cad', 6), ('rhy', 1), ('blind', 7)):
        await pg.evaluate(SETUP, [d, lv0]); o0 = await pg.evaluate(READ); r0 = await pg.evaluate("(d)=>[EAR.lvl[d],earLvl()]", d)
        for lv in (1, 2, 5, 7, lv0):
            await pg.evaluate("(l)=>document.querySelector('#lvl button[data-l=\"'+l+'\"]').click()", lv); await pg.wait_for_timeout(60)
            if not await pg.evaluate("()=>!!document.querySelector('#earMain .el-lg')"): await pg.evaluate("()=>{location.hash='ear';room('ear')}")
            o = await pg.evaluate(READ)
            check(await pg.evaluate("(d)=>[EAR.lvl[d],earLvl()]", d) == r0, f'{d}: rung in use moved when the learner level went {lv0} -> {lv}')
            check([g['i'] for g in o['groups'] if g['you']] == [lv] and [g['i'] for g in o['groups'] if g['tab']['you']] == [lv], f'{d}: .you mark at level {lv}')
            check([g['i'] for g in o['groups'] if g['open']] == [g['i'] for g in o0['groups'] if g['open']], f'{d}: open tab moved with the learner level')
            check([c['b'] for g in o['groups'] for k, c in slots_of(g) if k == 'b' and c['on']] == [c['b'] for g in o0['groups'] for k, c in slots_of(g) if k == 'b' and c['on']], f'{d}: rung button in use changed')
    # P6: labels
    await pg.evaluate(SETUP, ['mel', 4]); o = await pg.evaluate(READ)
    o = await pg.evaluate(READ)
    check(o['drillSub'] == ['3 rungs', '10 rungs', '3 rungs', '4 rungs', '3 rungs', '13 rungs', '3 rungs'], f'drill sub-labels {o["drillSub"]}')
    check(o['tag'] == 'Rungs 2 to 18 · 13 written', f'card tag {o["tag"]}')
    check(re.match(r'^Rung 10 of 21 · Level 4, Intermediate \(≈ NSW Stage 5\) · ', o['rungline']) and 'white-space:nowrap">(≈ NSW Stage 5)</span>' in o['rungHTML'], f'rung line {o["rungline"][:90]}')
    for d, tag in (('rhy', 'Rungs 2 to 16 · 10 written'), ('metre', 'Rungs 2 to 8 · 3 written')):
        await pg.evaluate(SETUP, [d, 4]); check((await pg.evaluate(READ))['tag'] == tag, f'{d} tag')
    await pg.evaluate(SETUP, ['mel', 4]); await pg.evaluate("()=>{localStorage.setItem('cjg_curric','');renderEar()}"); o = await pg.evaluate(READ)
    check('(' not in o['rungline'].split('·')[1] and o['rungline'].startswith('Rung 10 of 21 · Level 4, Intermediate · '), f'rung line without curriculum: {o["rungline"][:80]}')
    await pg.evaluate("()=>{localStorage.removeItem('cjg_curric');renderEar()}")
    await pg.evaluate(SETUP, ['mel', 4]); g4 = (await pg.evaluate(READ))['groups'][3]
    check(g4['tab']['al'] == 'Level 4, Intermediate, your level, rungs 10 to 12', f'tab aria {g4["tab"]["al"]}')
    g7 = (await pg.evaluate(READ))['groups'][6]
    check(g7['tab']['al'] == 'Level 7, Extension, not yet written' and g7['cells'][0]['al'] == 'Rungs 19 to 21, not yet written', f'empty level aria {g7["tab"]["al"]} / {g7["cells"][0]["al"]}')
    await pg.close()

OVER = "()=>document.documentElement.scrollWidth-document.documentElement.clientWidth"
GEOM = """()=>{const r=e=>e.getBoundingClientRect(),vis=e=>e.offsetParent!==null&&r(e).width>0;
 const g=[...document.querySelectorAll('#earMain .el-lg')],lgr=g.map(e=>e.querySelector('.el-lgr')).filter(vis),tabs=[...document.querySelectorAll('#earMain .el-ltab')].filter(vis),
  rb=[...document.querySelectorAll('#earMain .el-lgr button')].filter(vis),ny=[...document.querySelectorAll('#earMain .el-ny')].filter(vis),sm=[];
 document.querySelectorAll('#earMain .el-rp7 *, #earMain .el-rungline *').forEach(e=>{if(e.children.length||!vis(e)||!e.textContent.trim())return;const f=parseFloat(getComputedStyle(e).fontSize);if(f<10.99)sm.push(e.textContent.trim()+':'+f)});
 const rp=r(document.querySelector('#earMain .el-rp7')),card=r(document.querySelector('#earCard'));
 return{tops:[...new Set(lgr.map(e=>Math.round(r(e).top)))],nl:lgr.length,tabH:tabs.map(e=>r(e).height),tabW:tabs.map(e=>r(e).width),rbH:rb.map(e=>r(e).height),rbW:rb.map(e=>r(e).width),nyH:ny.map(e=>r(e).height),
  small:sm,rpRight:rp.right,cardRight:card.right,rpLeft:rp.left,cardLeft:card.left,nbtn:rb.length,nny:ny.length}}"""
VIEWS = [(1440, 900), (1366, 768), (1280, 800), (1024, 768), (900, 800), (820, 1180), (390, 844), (360, 740)]
async def geometry(b):
    shots = REPO / 'tests/reports/rungs_050'; shots.mkdir(parents=True, exist_ok=True)
    INFO['geometry'] = {}
    for w, h in VIEWS:
        errs = []
        pg = await page(b, w, h, errs)
        for d, lv in (('mel', 4), ('cad', 6), ('metre', 1)):
            await pg.evaluate(SETUP, [d, lv]); await pg.wait_for_timeout(250)
            await pg.evaluate("()=>{const e=document.querySelector('#earCard');e.scrollIntoView({block:'start'})}"); await pg.wait_for_timeout(100)
            o = await pg.evaluate(GEOM); t = f'{w}x{h} {d}'
            check(await pg.evaluate(OVER) <= 0, f'{t}: sideways scroll {await pg.evaluate(OVER)}')
            check(o['rpLeft'] >= o['cardLeft'] - 0.5 and o['rpRight'] <= o['cardRight'] + 0.5, f'{t}: picker outside its card {o["rpLeft"]}..{o["rpRight"]} vs {o["cardLeft"]}..{o["cardRight"]}')
            check(not o['small'], f'{t}: text under 11 px {o["small"][:3]}')
            if w > 900:
                check(o['nl'] == 7 and len(o['tops']) == 1, f'{t}: seven groups in one row {o["tops"]}')
                check(not o['tabH'], f'{t}: tabs hidden on a laptop')
                if d == 'mel': INFO['geometry'][f'{w}: rung cell width (min..max)'] = f"{min(o['rbW']):.0f}..{max(o['rbW']):.0f}, height {min(o['rbH']):.0f}"
            else:
                check(len(o['tabH']) == 7 and o['nl'] == 1, f'{t}: seven tabs over one open row ({len(o["tabH"])} tabs, {o["nl"]} rows)')
                check(all(x >= 43.5 for x in o['tabH']) and all(x >= 43.5 for x in o['rbH']) and all(x >= 43.5 for x in o['nyH']), f'{t}: phone targets under 44 px high {o["tabH"][:1]} {o["rbH"][:1]}')
                check(min(o['tabW']) >= (39.5 if w <= 360 else 43.5) or w > 500, f'{t}: tab width {min(o["tabW"]):.1f}')
                if d == 'mel': INFO['geometry'][f'{w}: tab width, rung height'] = f"{min(o['tabW']):.0f}, {min(o['rbH']):.0f}"
            if d == 'mel' or (d == 'cad' and w in (1440, 390)):
                await pg.screenshot(path=str(shots / f'picker_{d}_{w}x{h}.png'))
        check(not errs, f'{w}: page errors {errs[:2]}')
        await pg.close()

INFO = {}
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        await logic(b)
        await geometry(b)
        await b.close()
    print(json.dumps({'checks': N[0], 'failures': FAILS, 'n_failures': len(FAILS), 'info': INFO}, indent=1, ensure_ascii=False))
    sys.exit(1 if FAILS else 0)
asyncio.run(main())
