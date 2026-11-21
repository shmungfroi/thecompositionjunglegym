"""Rung 11: how often each bass offset comes up, and the most octave marks drawn on the bass ladder for each. Run: python3 dist.py <repo>"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1]).resolve(); OUT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
PRE = "(()=>{S.level=6;location.hash='ear';EAR.all=false;room('ear')})()"
JS = """(n)=>{const o={};for(let i=0;i<n;i++){EAR.drill='mel';EAR.lvl.mel=11;EAR.q=null;EAR.done=false;EAR.res=null;earNew();const q=EAR.q;document.querySelector('[data-earpart="bass"]').click();
 const off=Math.abs(earBassOff(q)),rows=[...document.querySelectorAll('#earMain .earlad [data-earsol] b')].map(b=>b.textContent),mk=Math.max(...rows.map(t=>(t.match(/,/g)||[]).length)),
  used=Math.max(...[ladFirst(q,'bass').s,...ladTruthEntries(q,'bass').map(e=>e.s)].map(s=>((earBassShow(q,s)||'').match(/,/g)||[]).length)),k=q.mode+' off'+off;
 o[k]=o[k]||{n:0,rowsMax:0,marksOnLadder:{},marksInAnswer:{}};o[k].n++;o[k].rowsMax=Math.max(o[k].rowsMax,rows.length);o[k].marksOnLadder[mk]=(o[k].marksOnLadder[mk]||0)+1;o[k].marksInAnswer[used]=(o[k].marksInAnswer[used]||0)+1;
 document.querySelector('[data-earpart="mel"]').click()}return o}"""
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(viewport={'width': 1366, 'height': 768})
        await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
        await pg.evaluate(PRE); await pg.evaluate("window.earPlay=()=>{};window.elPlay=()=>{}")
        r = await pg.evaluate(JS, 1500); await b.close()
    (OUT / 'r11_offset_distribution.json').write_text(json.dumps(r, indent=1)); print(json.dumps(r, indent=1))
asyncio.run(main())
