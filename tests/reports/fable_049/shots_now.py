"""Fable 0.49: capture the current (0.48) state that C5 and the ladder design start from.
Run: python3 tests/reports/fable_049/shots_now.py   (from the repo root). Writes now/*.png and now/metrics.json."""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
OUT = HERE / 'now'; OUT.mkdir(exist_ok=True)
SIZES = [(1440, 900), (1366, 768), (1024, 768), (390, 844)]
PRE = "(l)=>{S.level=l;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===l));location.hash='ear';EAR.all=false;EAR.st={};room('ear')}"
VIEW = "(a)=>{const [d,l]=a;EAR.drill=d;EAR.lvl[d]=l;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();}"
BOX = "(s)=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return {x:Math.round(r.x),y:Math.round(r.y),w:Math.round(r.width),h:Math.round(r.height)}}"
M = {}

async def run(p):
    b = await cjg.launch(p)
    for w, h in SIZES:
        pg = await b.new_page(viewport={'width': w, 'height': h})
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate(PRE, 6)
        await pg.evaluate("window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11);window.earPlay=()=>{}")
        m = M[str(w)] = {}
        m['top_search'] = await pg.evaluate(BOX, '#searchForm'); m['top_q'] = await pg.evaluate(BOX, '#q')
        m['top_children'] = await pg.evaluate("[...document.querySelector('header.top').children].map(e=>{const r=e.getBoundingClientRect();return [e.className||e.id||e.tagName,Math.round(r.x),Math.round(r.width),getComputedStyle(e).display]})")
        await pg.screenshot(path=str(OUT / f'top_{w}.png'), clip={'x': 0, 'y': 0, 'width': w, 'height': 70})
        for d, l in ((('mel', 1), ('mel', 3), ('rhy', 3), ('cad', 1)) if w in (1366, 390) else (('mel', 3),)):
            await pg.evaluate(VIEW, [d, l]); await pg.wait_for_timeout(150)
            m[f'{d}{l}_head_idle'] = await pg.evaluate(BOX, '.el-head'); m[f'{d}{l}_tally_idle'] = await pg.evaluate(BOX, '.el-tally')
            m[f'{d}{l}_rungs'] = await pg.evaluate(BOX, '.el-rungs')
            await pg.screenshot(path=str(OUT / f'{d}{l}_idle_{w}.png'), full_page=(w == 390))
            await pg.evaluate("()=>{EAR.q=earGen(EAR.drill,earLvl(),R);EAR.q.plays=1;renderEar()}"); await pg.wait_for_timeout(250)
            if d in ('mel', 'rhy'):
                await pg.evaluate("()=>{const q=EAR.q;EAR.ans=q.a.slice(0,Math.max(2,q.a.length-2));renderEar()}"); await pg.wait_for_timeout(250)
            await pg.screenshot(path=str(OUT / f'{d}{l}_asked_{w}.png'), full_page=(w == 390))
            if d == 'mel':
                m[f'mel{l}_desk'] = await pg.evaluate(BOX, '.meldesk'); m[f'mel{l}_lad'] = await pg.evaluate(BOX, '.meldesk .earlad')
                m[f'mel{l}_step'] = await pg.evaluate(BOX, '.meldesk .earstep'); m[f'mel{l}_score'] = await pg.evaluate(BOX, '.melscore')
                m[f'mel{l}_nsteps'] = await pg.evaluate("document.querySelectorAll('.meldesk .earstep').length")
                m[f'mel{l}_chk'] = await pg.evaluate(BOX, '#earLet')
            if d == 'rhy':
                m['rhy_tile'] = await pg.evaluate(BOX, '#earMain .el-tile, #earMain [data-earrhy]')
            await pg.evaluate("""()=>{const q=EAR.q;if(q.d==='rhy'||q.d==='bass'||q.d==='mel')earMark(false,q.d==='rhy'?q.a.slice(0,-1).concat(['q']):q.a.slice(1).map(x=>x));else earMark(false,(q.opts||[...document.querySelectorAll('#earMain [data-earans]')].map(x=>x.dataset.earans)).find(x=>x!==q.a));renderEar()}""")
            await pg.wait_for_timeout(250)
            m[f'{d}{l}_head_answered'] = await pg.evaluate(BOX, '.el-head'); m[f'{d}{l}_tally_answered'] = await pg.evaluate(BOX, '.el-tally')
            await pg.screenshot(path=str(OUT / f'{d}{l}_answered_{w}.png'), full_page=(w == 390))
            await pg.evaluate("EAR.st={}")
        # Stage 4 rung row
        await pg.evaluate(PRE, 4); await pg.evaluate(VIEW, ['mel', 1]); await pg.wait_for_timeout(150)
        m['s4_rungrow'] = await pg.evaluate(BOX, '.el-rungrow')
        await pg.screenshot(path=str(OUT / f'mel_stage4_{w}.png'))
        # Keys room
        await pg.evaluate("()=>{S.level=6;location.hash='keys';room('keys');document.querySelector('[data-ktab=intervals]').click()}"); await pg.wait_for_timeout(500)
        for mode in ('name', 'sing'):
            await pg.evaluate("(md)=>{const b=document.querySelector(`[data-kgm=${md}]`);if(b)b.click()}", mode); await pg.wait_for_timeout(200)
            for sc in ((0, 0), (9, 9), (40, 48)):
                await pg.evaluate("(a)=>{const G=KS.gym;G.st[G.mode]={n:a[1],ok:a[0],streak:Math.min(a[0],7),best:Math.min(a[0],12)};gymTallyRefresh()}", list(sc))
                m[f'keys_{mode}_{sc[1]}_head'] = await pg.evaluate(BOX, '.kqhead'); m[f'keys_{mode}_{sc[1]}_tally'] = await pg.evaluate(BOX, '.kqhead .el-tally'); m[f'keys_{mode}_{sc[1]}_tabs'] = await pg.evaluate(BOX, '.kqhead .gtabs')
            el = await pg.query_selector('#ivGym')
            if el:
                await el.scroll_into_view_if_needed(); await el.screenshot(path=str(OUT / f'keys_gym_{mode}_{w}.png'))
        m['keys_buttons'] = await pg.evaluate("[...document.querySelectorAll('#room-keys button')].filter(b=>b.offsetParent).map(b=>{const r=b.getBoundingClientRect();return [b.className,b.textContent.trim().slice(0,22),Math.round(r.width),Math.round(r.height)]}).filter(x=>x[3]<44)")
        m['keys_links'] = await pg.evaluate("[...document.querySelectorAll('#room-keys a')].filter(b=>b.offsetParent).map(a=>{const cs=getComputedStyle(a),r=a.getBoundingClientRect();return [a.textContent.trim().slice(0,30),cs.color,cs.textDecorationLine,Math.round(r.height),a.parentElement.className,a.className]}).slice(0,8)")
        m['keys_checks'] = await pg.evaluate("[...document.querySelectorAll('#room-keys input[type=checkbox]')].filter(b=>b.offsetParent).map(a=>{const cs=getComputedStyle(a),r=a.getBoundingClientRect(),l=a.closest('label').getBoundingClientRect();return [a.closest('label').className,Math.round(r.width),cs.accentColor,Math.round(l.height)]})")
        h3 = await pg.evaluate_handle("[...document.querySelectorAll('#room-keys h3')].find(h=>h.textContent==='Song starters').parentElement")
        try:
            await h3.as_element().scroll_into_view_if_needed(); await h3.as_element().screenshot(path=str(OUT / f'keys_songs_{w}.png'))
        except Exception as e: m['songs_err'] = str(e)[:100]
        await pg.close()
    await b.close()
    (OUT / 'metrics.json').write_text(json.dumps(M, indent=1))

async def main():
    async with async_playwright() as p: await run(p)
asyncio.run(main())
