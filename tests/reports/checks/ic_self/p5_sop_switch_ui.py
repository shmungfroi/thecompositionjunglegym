"""IC_SELF_048 probe 3 (UI): with RUNG1_SOP_BALANCE on, the cadence drill at rung 1 runs in the page: new question, answer, feedback,
next, 40 times, with no page error; the item drawn each time is strict-clean by the app's checker and has a realisation.
Also: EARR1OPT.inc=false (after clearing the weight cache) removes every incomplete tonic.
Run: python3 tests/reports/checks/ic_self/p5_sop_switch_ui.py <repo>"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright

async def main():
    out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(viewport={'width': 1440, 'height': 900}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1500)
        out['default'] = await pg.evaluate('RUNG1_SOP_BALANCE')
        await pg.evaluate("()=>{RUNG1_SOP_BALANCE=true;EAR.drill='cad';EAR.lvl.cad=1;EAR.q=null;renderEar()}")
        rows = []
        for i in range(40):
            await pg.evaluate("()=>{window.tone=()=>{};earNew()}")
            await pg.wait_for_timeout(120)
            q = await pg.evaluate("()=>EAR.q&&{a:EAR.q.a,rns:EAR.q.rns,ch:EAR.q.ch,app:EAR.q.ch?withKey(EAR.q.key,()=>checkSATB(EAR.q.ch,cadList(EAR.q.rns.join(' '),EAR.q.key))).filter(e=>e.sev!=='info').map(e=>e.rule):['none'],opts:[...document.querySelectorAll('#earMain [data-earans]')].map(b=>b.dataset.earans)}")
            if not q: rows.append({'err': 'no question'}); continue
            pick = q['opts'][i % len(q['opts'])] if q['opts'] else None
            if pick:
                await pg.click(f'#earMain [data-earans="{pick}"]'); await pg.wait_for_timeout(120)
            fb = await pg.evaluate("()=>{const r=document.querySelector('#earMain .el-res, #earMain .el-result, #earMain [class*=result]');return r?r.textContent.slice(0,160):''}")
            rows.append({'a': q['a'], 'rns': q['rns'], 'app': q['app'], 'opts': q['opts'], 'picked': pick, 'done': await pg.evaluate('EAR.done'), 'fb': fb})
        out['ui'] = rows
        out['inc_off'] = await pg.evaluate("""()=>{RUNG1_SOP_BALANCE=false;EARR1OPT.inc=false;for(const k in EARR1)delete EARR1[k];const W=earR1Weights();let inc=0,n=0;
            for(const a in W)for(const e of W[a]){n++;if(new Set(e.ch[1].map(m=>((m%12)+12)%12)).size<3)inc++}
            const R=(s=>()=>{s=(s*16807)%2147483647;return s/2147483647})(5);let incQ=0;for(let i=0;i<2000;i++){const q=earGen('cad',1,R);if(q.a==='perfect'&&new Set(q.ch[1].map(m=>m%12)).size<3)incQ++}
            EARR1OPT.inc=true;for(const k in EARR1)delete EARR1[k];return {entries:n,incomplete:inc,incomplete_in_2000_items:incQ}}""")
        out['pageerrors'] = errs
        await b.close()
    bad = [r for r in out['ui'] if r.get('err') or r['app'] or not r['done'] or len(r['opts']) != 4]
    out['bad'] = bad
    print(json.dumps(out, indent=1, ensure_ascii=False))

asyncio.run(main())
