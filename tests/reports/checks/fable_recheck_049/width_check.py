"""Should 1 re-check: the bar map, the systems and the drawn labels agree after the first render and after a resize. Run: python3 width_check.py <repo>"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1]).resolve(); OUT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
PRE = "(()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='ear';EAR.all=false;EAR.st={};EAR.rd={};EAR.reached={};room('ear')})()"
NEW = """(o)=>{const want=new Function('q','return '+o.want);let q,ok=false;EAR.sysSel=null;
 for(let t=0;t<4000;t++){EAR.drill='mel';EAR.lvl.mel=o.l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();q=EAR.q;if(want(q)){ok=true;break}}
 if(!ok)return null;
 if(o.chk){for(const e of ladTruthEntries(q,'mel')){if(e.s===null){document.querySelector(`[data-rest="${e.t}"]`).click();continue}const lb=document.querySelector(`[data-len="${e.t}"]`);if(lb.getAttribute('aria-checked')!=='true')lb.click();document.querySelector(`[data-earsol="${e.s}"]`).click()}earCheck()}
 return q.metre}"""
STATE = """()=>{const q=EAR.q,m=document.getElementById('earMel'),sys=earMelSystems(q,'mel').map(s=>s.filter(b=>b.bi>0).length),labs=[...document.querySelectorAll('#earMel svg text:not(.melsol):not(.melname)')].map(t=>t.textContent),phone=innerWidth<761;
 return{w:innerWidth,melW:EAR.melW,client:m.clientWidth,built:EAR.psBuilt,per:earMelPerSys(q),sys,map:document.querySelectorAll('#earMain .el-sysmap button').length,labs,done:EAR.done,
  ok:EAR.melW===m.clientWidth&&EAR.psBuilt===earMelPerSys(q)&&(sys.length<2||document.querySelectorAll('#earMain .el-sysmap button').length===sys.length)&&(phone||labs.length===sys.length*(EAR.done?2:1))}}"""
SEMI = "ladEntriesToLine(q,ladTruthEntries(q,'mel'),'mel').some(x=>x.dur===105)"
async def main():
    rows = []; bad = []
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1366, 'height': 768}); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate(PRE); await pg.evaluate("window.earPlay=()=>{};window.elPlay=()=>{}")
        for metre in ('2/4', '3/4', '4/4', '6/8'):
            for chk in (0, 1):
                for seq in ((1366, 1100, 1024, 900, 800, 761, 760, 390, 1366), (390, 800, 1200, 390)):
                    for i, w in enumerate(seq):
                        await pg.set_viewport_size({'width': w, 'height': 800}); await pg.wait_for_timeout(260)
                        if i == 0:
                            m = None
                            for l in (12, 10, 8, 6):
                                m = await pg.evaluate(NEW, dict(l=l, chk=chk, want="q.metre==='%s'&&%s" % (metre, SEMI)))
                                if m: break
                            if not m: rows.append(f'{metre}: no item with semiquavers'); break
                            await pg.wait_for_timeout(120)
                        s = await pg.evaluate(STATE); s['metre'] = metre; s['step'] = f'{seq[0]}>{w}' if i else f'new at {w}'
                        rows.append(json.dumps(s, ensure_ascii=False))
                        if not s['ok']: bad.append(s)
        await b.close()
    (OUT / 'width_check.txt').write_text('\n'.join(rows) + f'\n\nstates {len(rows)}, disagreements {len(bad)}, page errors {errs[:3]}\n')
    print(len(rows), 'states;', len(bad), 'bad;', errs[:3]); [print(json.dumps(x)[:400]) for x in bad[:8]]
    import collections; print(collections.Counter((json.loads(r)['metre'], json.loads(r)['w'], json.loads(r)['client'], json.loads(r)['per']) for r in rows if r.startswith('{')))
asyncio.run(main())
