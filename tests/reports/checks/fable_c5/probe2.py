"""Second pass: real answer path on a phone, focus ring in context, zoomed checkbox, between-size top bar."""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent; REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
BOX = "(s)=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]}"
async def main():
    out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 390, 'height': 844}, device_scale_factor=2); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
        await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{S.level=6;location.hash='ear';EAR.all=false;EAR.st={};room('ear');window.earPlay=()=>{}}")
        await pg.evaluate("()=>{EAR.drill='cad';EAR.lvl.cad=1;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];EAR.st={};renderEar()}"); await pg.wait_for_timeout(200)
        out['btns0'] = await pg.evaluate("[...document.querySelectorAll('#earCard button')].map(b=>(b.className+'|'+b.innerText.trim().slice(0,20)+'|'+(b.disabled?'dis':'')))")
        seq = []
        seq.append(await pg.evaluate(BOX, '.el-head'))
        await pg.evaluate("()=>{const b=document.querySelector('#earCard .el-play, #earCard [data-ear=play], #earCard button.play')||[...document.querySelectorAll('#earCard button')].find(x=>/Play/.test(x.innerText));b.click()}"); await pg.wait_for_timeout(500)
        out['btns1'] = await pg.evaluate("[...document.querySelectorAll('#earCard button')].map(b=>(b.className+'|'+b.innerText.trim().slice(0,20)+'|'+(b.disabled?'dis':'')))")
        seq.append(await pg.evaluate(BOX, '.el-head'))
        await pg.evaluate("()=>{const b=[...document.querySelectorAll('#earCard button')].find(x=>/Perfect/.test(x.innerText)&&!x.disabled);b&&b.click()}"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{const b=[...document.querySelectorAll('#earCard button')].find(x=>/^Check/.test(x.innerText.trim())&&!x.disabled);b&&b.click()}"); await pg.wait_for_timeout(500)
        seq.append(await pg.evaluate(BOX, '.el-head'))
        out['tally_after'] = await pg.evaluate("document.querySelector('#earCard .el-tally').innerText.replace(/\\s+/g,' ')")
        out['tally_box'] = await pg.evaluate(BOX, '#earCard .el-tally')
        out['head_seq'] = seq
        await pg.evaluate("scrollTo(0,0)"); await pg.screenshot(path=str(HERE / 'c51_ear_first_real_answer_390.png'))
        # Keys focus ring in context, at 2x
        await pg.evaluate("()=>{location.hash='keys';room('keys');document.querySelector('[data-ktab=intervals]').click()}"); await pg.wait_for_timeout(400)
        await pg.locator('#kp-intervals label.tick input').first.focus(); await pg.keyboard.press('Tab'); await pg.keyboard.press('Shift+Tab'); await pg.wait_for_timeout(200)
        r = await pg.evaluate(BOX, '#kp-intervals label.tick')
        await pg.screenshot(path=str(HERE / 'c52_keys_ticks_focus_context_390_2x.png'), clip={'x': 0, 'y': max(0, r[1] - 60), 'width': 390, 'height': 170})
        out['errs'] = errs
        await pg.close()
        # desktop zoom on the boxes
        pg = await b.new_page(viewport={'width': 1440, 'height': 900}, device_scale_factor=3)
        await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{S.level=6;location.hash='keys';room('keys');document.querySelector('[data-ktab=intervals]').click()}"); await pg.wait_for_timeout(400)
        lab = pg.locator('#kp-intervals label.tick').first; await lab.scroll_into_view_if_needed()
        r = await pg.evaluate(BOX, '#kp-intervals label.tick')
        await pg.screenshot(path=str(HERE / 'c52_keys_ticks_zoom_3x.png'), clip={'x': r[0] - 12, 'y': r[1] - 10, 'width': 280, 'height': 40})
        await pg.close()
        # between sizes
        for w in (901, 800, 761, 950):
            pg = await b.new_page(viewport={'width': w, 'height': 768})
            await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
            await pg.evaluate("()=>{location.hash='analysis';room('analysis')}"); await pg.wait_for_timeout(300)
            await pg.screenshot(path=str(HERE / f'c56_screen_{w}.png'), clip={'x': 0, 'y': 0, 'width': w, 'height': 220})
            out[f'lvl_{w}'] = await pg.evaluate("()=>{const l=document.querySelector('.top .lvl');const r=l.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height),l.innerText.replace(/\\s+/g,' ')]}")
            await pg.add_style_tag(content="@media (min-width:761px) and (max-width:1180px){.top{gap:22px!important;padding:0 22px!important}.top .t{font-size:22px!important;letter-spacing:5px!important}.search{flex:1!important;min-width:0!important}.search input{padding:10px 14px 10px 18px!important}}@media (min-width:761px) and (max-width:900px){.top .tw{display:inline!important}}")
            await pg.wait_for_timeout(200)
            out[f'lvl_{w}_before'] = await pg.evaluate("()=>{const l=document.querySelector('.top .lvl');const r=l.getBoundingClientRect();return [Math.round(r.width),Math.round(r.height)]}")
            await pg.close()
        await b.close()
    print(json.dumps(out, indent=1, ensure_ascii=False))
asyncio.run(main())
