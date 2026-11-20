"""Fable verification of the C5 build (0.49). Measures and screenshots the built index.html; nothing is injected.
Run from the repo root: python3 tests/reports/checks/fable_c5/verify.py"""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent; REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
SIZES = [(1440, 900), (1366, 768), (1024, 768), (390, 844)]
BOX = "(s)=>{const e=document.querySelector(s);if(!e||!e.getBoundingClientRect().width)return null;const r=e.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]}"
PROBE = """()=>{const B=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return r.width?[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]:null};
 const P=document.getElementById('kp-intervals');const small=[];P.querySelectorAll('button,a,label.tick,label.note,input,select').forEach(e=>{if(!e.offsetParent)return;if(e.matches('input[type=checkbox]'))return;const r=e.getBoundingClientRect();if(r.height<43.5||r.width<43.5)small.push((e.className||e.parentElement.className)+':'+e.textContent.trim().slice(0,12)+':'+Math.round(r.width)+'x'+Math.round(r.height))});
 const a=P.querySelector('.istart .sb a'),cs=a&&getComputedStyle(a),cb=P.querySelector('.tick input:not(:checked)'),cc=cb&&getComputedStyle(cb),ck=P.querySelector('.tick input:checked'),ckc=ck&&getComputedStyle(ck);
 const tr=P.querySelector('label.tick');
 return {kqhead:B('.kqhead'),tally:B('.kqhead .el-tally'),tabs:B('.kqhead .gtabs'),small:[...new Set(small)],link:cs&&[cs.color,cs.textDecorationLine,cs.borderTopColor,cs.borderRadius,Math.round(a.getBoundingClientRect().height)],
  box:cc&&[cc.appearance,cc.backgroundColor,cc.borderTopColor,cc.borderRadius,Math.round(cb.getBoundingClientRect().width),Math.round(cb.getBoundingClientRect().height)],
  boxOn:ckc&&[ckc.backgroundColor,ckc.borderTopColor,getComputedStyle(ck,'::after').opacity,getComputedStyle(ck,'::after').borderLeftColor],
  tickrow:tr&&Math.round(tr.getBoundingClientRect().height),over:document.documentElement.scrollWidth-innerWidth}}"""
TOP = """()=>{const h=document.querySelector('header.top'),hr=h.getBoundingClientRect();const kids=[...h.children].filter(e=>e.getBoundingClientRect().width).map(e=>{const r=e.getBoundingClientRect();return [(e.className||e.id||e.tagName).toString().split(' ')[0],Math.round(r.x),Math.round(r.width),Math.round(r.height)]});
 let ov=false;const ks=[...h.children].filter(e=>e.getBoundingClientRect().width);for(let i=1;i<ks.length;i++){if(ks[i].getBoundingClientRect().left<ks[i-1].getBoundingClientRect().right-0.5&&Math.abs(ks[i].getBoundingClientRect().top-ks[i-1].getBoundingClientRect().top)<10)ov=true}
 const last=ks[ks.length-1].getBoundingClientRect();const q=document.getElementById('q'),f=document.querySelector('.search').getBoundingClientRect();
 const c=document.createElement('canvas').getContext('2d');const cs=getComputedStyle(q);c.font=cs.fontStyle+' '+cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily;const pw=c.measureText(q.placeholder).width;
 const inner=q.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
 return {kids,overlap:ov,rightSpill:Math.round(last.right-hr.right),form:Math.round(f.width),input:Math.round(q.getBoundingClientRect().width),placeholderPx:Math.round(pw),innerPx:Math.round(inner),placeholderFits:pw<=inner+0.5,docOver:document.documentElement.scrollWidth-innerWidth,crumb:getComputedStyle(document.querySelector('.top .crumb')).display,title:document.querySelector('.top .t').innerText.replace(/\\s+/g,' ')}}"""
M = {}

async def newpage(b, w, h):
    pg = await b.new_page(viewport={'width': w, 'height': h}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    return pg, errs

async def one(b, w, h):
    pg, errs = await newpage(b, w, h); m = M.setdefault(str(w), {})
    # ---- C5-1 / C5-2 Ear Lab
    await pg.evaluate("()=>{S.level=6;location.hash='ear';EAR.all=false;EAR.st={};room('ear');window.earPlay=()=>{};window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11)}")
    for d in ('metre', 'cad', 'mel', 'bass'):
        await pg.evaluate("(d)=>{EAR.drill=d;EAR.lvl[d]=1;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];EAR.st={};renderEar()}", d); await pg.wait_for_timeout(150)
        h0 = await pg.evaluate(BOX, '.el-head'); t0 = await pg.evaluate(BOX, '#earCard .el-tally')
        if d == 'cad': await pg.screenshot(path=str(HERE / f'c51_ear_empty_{w}.png'))
        if d == 'mel':
            await pg.evaluate("()=>{EAR.q=earGen('mel',1,R);EAR.q.plays=1;renderEar()}"); await pg.wait_for_timeout(250)
            el = await pg.query_selector('.melacts'); await el.scroll_into_view_if_needed()
            await el.screenshot(path=str(HERE / f'c52_ear_unticked_{w}.png'))
            m['ear_cb_off'] = await pg.evaluate("()=>{const c=document.querySelector('.melacts label.note input');const s=getComputedStyle(c);const r=c.getBoundingClientRect(),l=c.closest('label').getBoundingClientRect();return {box:[Math.round(r.width),Math.round(r.height)],app:s.appearance,bg:s.backgroundColor,border:s.borderTopColor,row:Math.round(l.height),checked:c.checked}}")
            await pg.click('.melacts label.note input'); await pg.wait_for_timeout(250)
            el = await pg.query_selector('.melacts'); await el.scroll_into_view_if_needed(); await el.screenshot(path=str(HERE / f'c52_ear_ticked_{w}.png'))
            m['ear_cb_on'] = await pg.evaluate("()=>{const c=document.querySelector('.melacts label.note input');if(!c)return null;const s=getComputedStyle(c),a=getComputedStyle(c,'::after');return {bg:s.backgroundColor,border:s.borderTopColor,tick:a.opacity,tickCol:a.borderLeftColor,checked:c.checked}}")
            await pg.screenshot(path=str(HERE / f'c52_ear_ticked_screen_{w}.png'))
            c = await pg.query_selector('.melacts label.note input')
            if c and await c.is_checked(): await c.click()
        await pg.evaluate("(st)=>{EAR.st[EAR.drill]=st;renderEar()}", {'n': 12, 'ok': 10, 'streak': 4, 'best': 6, 'shown': 0, 'skipped': 0}); await pg.wait_for_timeout(150)
        h1 = await pg.evaluate(BOX, '.el-head'); t1 = await pg.evaluate(BOX, '#earCard .el-tally'); m[f'head_{d}'] = {'empty': h0, 'counted': h1, 'tally_empty': t0, 'tally_counted': t1}
        if d == 'cad':
            await pg.evaluate("scrollTo(0,0)"); await pg.screenshot(path=str(HERE / f'c51_ear_counted_{w}.png'))
    m['ear_over'] = await pg.evaluate("document.documentElement.scrollWidth-innerWidth")
    # real answer path at one drill: answer a metre question by clicking, measure head before/after
    await pg.evaluate("()=>{EAR.drill='metre';EAR.lvl.metre=1;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];EAR.st={};renderEar()}"); await pg.wait_for_timeout(150)
    ha = await pg.evaluate(BOX, '.el-head')
    try:
        await pg.evaluate("()=>{const b=[...document.querySelectorAll('#earCard button')].find(x=>/^(Play|Start|Hear)/i.test(x.textContent.trim()));b&&b.click()}"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{const b=document.querySelector('#earCard .chip:not([disabled]), #earCard .opts button, #earCard .el-opts button');b&&b.click()}"); await pg.wait_for_timeout(300)
        await pg.evaluate("()=>{const b=[...document.querySelectorAll('#earCard button')].find(x=>/^Check/i.test(x.textContent.trim()));b&&b.click()}"); await pg.wait_for_timeout(300)
    except Exception as e: m['real_answer_err'] = str(e)[:100]
    m['head_real'] = {'before': ha, 'after': await pg.evaluate(BOX, '.el-head'), 'tally_text': await pg.evaluate("document.querySelector('#earCard .el-tally').innerText.replace(/\\s+/g,' ')")}
    await pg.evaluate("scrollTo(0,0)"); await pg.screenshot(path=str(HERE / f'c51_ear_real_answer_{w}.png'))
    # ---- Keys
    await pg.evaluate("()=>{location.hash='keys';room('keys');document.querySelector('[data-ktab=intervals]').click()}"); await pg.wait_for_timeout(400)
    await pg.screenshot(path=str(HERE / f'keys_full_{w}.png'), full_page=True)
    m['keys_rest'] = await pg.evaluate(PROBE)
    await pg.evaluate("()=>{document.querySelector('[data-kgq=new]').click()}"); await pg.wait_for_timeout(250)
    for sc in ((0, 0), (9, 9), (40, 48)):
        await pg.evaluate("(a)=>{const G=KS.gym;G.st[G.mode]={n:a[1],ok:a[0],streak:Math.min(a[0],7),best:Math.min(a[0],12)};gymTallyRefresh()}", list(sc))
        m[f'keys_{sc[1]}'] = await pg.evaluate(PROBE)
        el = await pg.query_selector('#ivGym'); await el.scroll_into_view_if_needed(); await el.screenshot(path=str(HERE / f'c53_keys_gym_{sc[1]}_{w}.png'))
    for sel, name in (('#ivSongs', 'c54_keys_songs'), ('#kp-intervals .picker', 'c55_keys_picker')):
        el = await pg.query_selector(sel); await el.scroll_into_view_if_needed(); await el.screenshot(path=str(HERE / f'{name}_{w}.png'))
    # tick rows: unticked and ticked in Keys
    lab = await pg.query_selector('#kp-intervals label.tick')
    par = await lab.evaluate_handle('e=>e.parentElement'); await par.as_element().scroll_into_view_if_needed()
    m['keys_ticks_initial'] = await pg.evaluate("[...document.querySelectorAll('#kp-intervals label.tick input')].map(c=>c.checked)")
    await par.as_element().screenshot(path=str(HERE / f'c52_keys_ticks_a_{w}.png'))
    TK = '#kp-intervals label.tick input'
    async def toggle():
        n = await pg.locator(TK).count()
        for i in range(n): await pg.locator(TK).nth(i).click(); await pg.wait_for_timeout(80)
    await toggle()
    par = await (await pg.query_selector('#kp-intervals label.tick')).evaluate_handle('e=>e.parentElement')
    await pg.wait_for_timeout(200); await pg.mouse.move(2, 2)
    await par.as_element().screenshot(path=str(HERE / f'c52_keys_ticks_b_{w}.png'))
    m['keys_ticks_toggled'] = await pg.evaluate("[...document.querySelectorAll('#kp-intervals label.tick input')].map(c=>c.checked)")
    m['keys_after_toggle'] = await pg.evaluate(PROBE)
    await toggle()
    par = await (await pg.query_selector('#kp-intervals label.tick')).evaluate_handle('e=>e.parentElement')
    # focus ring
    await pg.locator(TK).first.focus(); await pg.keyboard.press('Tab'); await pg.keyboard.press('Shift+Tab'); await pg.wait_for_timeout(150)
    m['focus_ring'] = await pg.evaluate("()=>{const s=getComputedStyle(document.activeElement);return [document.activeElement.type,s.outlineStyle,s.outlineWidth,s.outlineColor]}")
    await par.as_element().screenshot(path=str(HERE / f'c52_keys_ticks_focus_{w}.png'))
    # song-starter hover
    a = await pg.query_selector('#kp-intervals .istart .sb a')
    if a:
        await a.scroll_into_view_if_needed(); await a.hover(); await pg.wait_for_timeout(200)
        m['link_hover'] = await pg.evaluate("()=>{const s=getComputedStyle(document.querySelector('#kp-intervals .istart .sb a'));return [s.color,s.borderTopColor]}")
        el = await pg.query_selector('#ivSongs'); await el.screenshot(path=str(HERE / f'c54_keys_songs_hover_{w}.png')); await pg.mouse.move(2, 2)
    # sing mode
    await pg.evaluate("()=>document.querySelector('[data-kgm=sing]').click()"); await pg.wait_for_timeout(200)
    await pg.evaluate("()=>{const b=document.querySelector('[data-kgq=snew]');b&&b.click()}"); await pg.wait_for_timeout(300)
    m['keys_sing'] = await pg.evaluate(PROBE)
    el = await pg.query_selector('#ivGym'); await el.scroll_into_view_if_needed(); await el.screenshot(path=str(HERE / f'c55_keys_sing_{w}.png'))
    await pg.screenshot(path=str(HERE / f'keys_screen_{w}.png'))
    # ---- checkboxes in every other room (regression sweep)
    rooms = await pg.evaluate("()=>[...new Set([...document.querySelectorAll('[data-room]')].map(e=>e.dataset.room))]")
    m['rooms'] = rooms; sweep = {}
    for r in rooms:
        try:
            await pg.evaluate("(r)=>{location.hash=r;room(r)}", r); await pg.wait_for_timeout(350)
        except Exception as e:
            sweep[r] = 'ERR ' + str(e)[:80]; continue
        info = await pg.evaluate("""()=>[...document.querySelectorAll('input[type=checkbox]')].filter(c=>c.offsetParent).map(c=>{const r=c.getBoundingClientRect(),l=c.closest('label'),lr=l&&l.getBoundingClientRect(),s=getComputedStyle(c);
          let clip=false;if(l){const t=[...l.childNodes].filter(n=>n.nodeType===3&&n.textContent.trim())[0];}
          return {lab:(l?l.className+'|'+l.innerText.trim().slice(0,28):'(no label)'),box:[Math.round(r.width),Math.round(r.height)],row:lr&&[Math.round(lr.width),Math.round(lr.height)],disp:l&&getComputedStyle(l).display,checked:c.checked,app:s.appearance,midOff:lr&&Math.round((r.top+r.height/2)-(lr.top+lr.height/2))}})""")
        sweep[r] = {'boxes': info, 'over': await pg.evaluate("document.documentElement.scrollWidth-innerWidth")}
        if info:
            seen = set(); i = 0
            for k, el in enumerate(await pg.query_selector_all('input[type=checkbox]')):
                if not await el.is_visible(): continue
                par = await el.evaluate_handle("e=>{let p=e.closest('label')||e;p=p.parentElement;return p}")
                key = await par.evaluate("e=>e.className+e.innerText.slice(0,30)")
                if key in seen: continue
                seen.add(key)
                try:
                    await par.as_element().scroll_into_view_if_needed(); await par.as_element().screenshot(path=str(HERE / f'sweep_{r}_{i}_{w}.png')); i += 1
                except Exception: pass
                if i >= 4: break
    m['sweep'] = sweep; m['errors'] = errs
    await pg.close()

async def topbar(b):
    T = M.setdefault('top', {})
    for w in (1440, 1366, 1281, 1280, 1181, 1180, 1024, 901, 900, 800, 761, 760, 390):
        pg, errs = await newpage(b, w, 768 if w != 390 else 844)
        for r in ('analysis', 'keys'):
            await pg.evaluate("(r)=>{location.hash=r;room(r)}", r); await pg.wait_for_timeout(350)
            T[f'{w}_{r}'] = await pg.evaluate(TOP)
            if r == 'analysis' or w in (1024, 1280):
                await pg.screenshot(path=str(HERE / f'c56_top_{w}_{r}.png'), clip={'x': 0, 'y': 0, 'width': w, 'height': 110 if w < 761 else 64})
        if w in (1024, 1280):
            await pg.screenshot(path=str(HERE / f'c56_screen_{w}.png'))
            await pg.fill('#q', 'Bm7'); await pg.wait_for_timeout(500)
            await pg.screenshot(path=str(HERE / f'c56_typed_{w}.png'))
            T[f'{w}_typed'] = await pg.evaluate("()=>{const q=document.getElementById('q');return {val:q.value,scrollW:q.scrollWidth,clientW:q.clientWidth}}")
        T[f'{w}_errors'] = errs
        await pg.close()

async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h in SIZES: await one(b, w, h)
        await topbar(b)
        await b.close()
    (HERE / 'metrics.json').write_text(json.dumps(M, indent=1))
asyncio.run(main())
