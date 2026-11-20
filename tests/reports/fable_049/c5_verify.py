"""Fable 0.49, C5: measure each carried Should before and after c5.css (injected; index.html is not edited).
Run from the repo root: python3 tests/reports/fable_049/c5_verify.py   Writes c5/*.png and c5/metrics.json."""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent; REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
OUT = HERE / 'c5'; OUT.mkdir(exist_ok=True); CSS = (HERE / 'c5.css').read_text()
SIZES = [(1440, 900), (1366, 768), (1024, 768), (390, 844)]
BOX = "(s)=>{const e=document.querySelector(s);if(!e||!e.getBoundingClientRect().width)return null;const r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]}"
PROBE = """()=>{const B=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return r.width?[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]:null};
 const P=document.getElementById('kp-intervals');const small=[];P.querySelectorAll('button,a,label.tick').forEach(e=>{if(!e.offsetParent)return;const r=e.getBoundingClientRect();if(r.height<43.5)small.push((e.className||e.parentElement.className)+':'+e.textContent.trim().slice(0,12)+':'+Math.round(r.height))});
 const a=P.querySelector('.istart .sb a'),cs=a&&getComputedStyle(a),cb=P.querySelector('.tick input:not(:checked)'),cc=cb&&getComputedStyle(cb);
 const tiny=[];P.querySelectorAll('*').forEach(e=>{if(!e.offsetParent)return;if([...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&parseFloat(getComputedStyle(e).fontSize)<10.95)tiny.push(e.className+':'+e.textContent.trim().slice(0,10))});
 return {kqhead:B('.kqhead'),tally:B('.kqhead .el-tally'),tabs:B('.kqhead .gtabs'),small:[...new Set(small)],link:cs&&[cs.color,cs.textDecorationLine,Math.round(a.getBoundingClientRect().height)],
  box:cc&&[cc.appearance,cc.backgroundColor,cc.borderTopColor,Math.round(cb.getBoundingClientRect().width)],tiny:[...new Set(tiny)].slice(0,6),over:document.documentElement.scrollWidth-innerWidth}}"""
M = {}

async def one(b, w, h, after):
    tag = 'after' if after else 'before'
    pg = await b.new_page(viewport={'width': w, 'height': h}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:120]))
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    if after: await pg.add_style_tag(content=CSS)
    m = M.setdefault(str(w), {}).setdefault(tag, {})
    # C5-6 top bar, in three rooms (the crumb changes length)
    m['top'] = await pg.evaluate("[...document.querySelector('header.top').children].filter(e=>e.getBoundingClientRect().width).map(e=>[(e.className||e.id).split(' ')[0],Math.round(e.getBoundingClientRect().width)])")
    m['q_width'] = await pg.evaluate("Math.round(document.getElementById('q').getBoundingClientRect().width)")
    await pg.screenshot(path=str(OUT / f'top_{w}_{tag}.png'), clip={'x': 0, 'y': 0, 'width': w, 'height': 100 if w < 761 else 60})
    # C5-1 header growth, C5-2 checkbox (Ear Lab)
    await pg.evaluate("()=>{S.level=6;location.hash='ear';EAR.all=false;EAR.st={};room('ear');window.earPlay=()=>{};window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11)}")
    for d in ('metre', 'cad', 'mel', 'bass'):
        await pg.evaluate("(d)=>{EAR.drill=d;EAR.lvl[d]=1;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];EAR.st={};renderEar()}", d); await pg.wait_for_timeout(120)
        h0 = await pg.evaluate(BOX, '.el-head')
        if d == 'mel':
            await pg.evaluate("()=>{EAR.q=earGen('mel',1,R);EAR.q.plays=1;renderEar()}"); await pg.wait_for_timeout(200)
            el = await pg.query_selector('.melacts'); await el.scroll_into_view_if_needed(); await el.screenshot(path=str(OUT / f'checkbox_ear_{w}_{tag}.png'))
            m['ear_checkbox_row'] = await pg.evaluate(BOX, '.melacts label.note')
        await pg.evaluate("(st)=>{EAR.st[EAR.drill]=st;renderEar()}", {'n': 12, 'ok': 10, 'streak': 4, 'best': 6, 'shown': 0, 'skipped': 0}); await pg.wait_for_timeout(120)
        h1 = await pg.evaluate(BOX, '.el-head'); m[f'head_{d}'] = {'empty': h0, 'counted': h1}
        if d == 'cad':
            el = await pg.query_selector('.el-head'); await el.screenshot(path=str(OUT / f'head_counted_{w}_{tag}.png'))
            await pg.evaluate("()=>{EAR.st={};renderEar()}"); el = await pg.query_selector('.el-head'); await el.screenshot(path=str(OUT / f'head_empty_{w}_{tag}.png'))
    # C5-3/4/5 Keys
    await pg.evaluate("()=>{location.hash='keys';room('keys');document.querySelector('[data-ktab=intervals]').click()}"); await pg.wait_for_timeout(400)
    await pg.evaluate("()=>{document.querySelector('[data-kgq=new]').click()}"); await pg.wait_for_timeout(200)
    for sc in ((0, 0), (9, 9), (40, 48)):
        await pg.evaluate("(a)=>{const G=KS.gym;G.st[G.mode]={n:a[1],ok:a[0],streak:Math.min(a[0],7),best:Math.min(a[0],12)};gymTallyRefresh()}", list(sc))
        m[f'keys_{sc[1]}'] = await pg.evaluate(PROBE)
    for sel, name in (('#ivGym', 'keys_gym'), ('#ivSongs', 'keys_songs'), ('#kp-intervals .picker', 'keys_picker')):
        el = await pg.query_selector(sel); await el.scroll_into_view_if_needed(); await el.screenshot(path=str(OUT / f'{name}_{w}_{tag}.png'))
    await pg.evaluate("()=>document.querySelector('[data-kgm=sing]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("()=>{const b=document.querySelector('[data-kgq=snew]');b&&b.click()}"); await pg.wait_for_timeout(300)
    m['keys_sing'] = await pg.evaluate(PROBE)
    el = await pg.query_selector('#ivGym'); await el.screenshot(path=str(OUT / f'keys_sing_{w}_{tag}.png'))
    # checkboxes elsewhere (Gym room)
    await pg.evaluate("()=>{location.hash='gym';room('gym')}"); await pg.wait_for_timeout(300)
    el = await pg.query_selector('label.ck')
    if el and await el.is_visible():
        par = await el.evaluate_handle('e=>e.parentElement'); await par.as_element().scroll_into_view_if_needed(); await par.as_element().screenshot(path=str(OUT / f'checkbox_gym_{w}_{tag}.png'))
    m['errors'] = errs
    await pg.close()

async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in SIZES:
            for after in (False, True): await one(b, w, h, after)
        await b.close()
    (OUT / 'metrics.json').write_text(json.dumps(M, indent=1))
    for w in M:
        print(w)
        for k in M[w]['before']: print('  ', k, '\n      before', json.dumps(M[w]['before'][k]), '\n      after ', json.dumps(M[w]['after'][k]))
asyncio.run(main())
