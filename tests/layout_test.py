"""Layout and text test: every room, climb, form, analysis score (all layers on) and Ear Lab drill at 1440, 1024 and 390 px.
Fails on overlapping text (HTML and SVG), text clipped by its box, or text past the right edge of the screen.
Run: python3 tests/layout_test.py <repo dir>"""
import sys,asyncio,json,pathlib
import pathlib as _p
REPO_ARG=sys.argv[1] if len(sys.argv)>1 else '.'
sys.argv=['x',str(_p.Path(REPO_ARG).resolve()),'/tmp','1440']
sys.path.insert(0,str(_p.Path(__file__).resolve().parent/'harness'));import cjg
from playwright.async_api import async_playwright
route=cjg.make_route(sys.argv[1])
DET=open(str(_p.Path(__file__).with_name('layout_detect.js'))).read()
SC=['chorale','ohaupt','jesu','k331a','k331d','k545','maple','entertainer','chopin7','chopin20']
FORMS=['phrase','blues12','jazzblues','minblues','rhythm','rag','rondo','tv','sonata','sonrondo']
INST=['piano','guitar','uke','bass']
def views():
    V=[]
    for i in INST: V.append((f'seed/{i}',f"location.hash='seed';S.inst='{i}';room('seed')"))
    for r in ['keys','voice','oracle','climbs','forms','ear']: V.append((r,f"location.hash='{r}'"))
    V.append(('gym',"location.hash='gym';if(!P.length){for(const r of ['I','vi','ii','V','I','IV','V7','I'])document.querySelector(`[data-add=\"${r}\"]`)?.click()}"))
    for k in range(1,14): V.append((f'climbs/{k}',f"location.hash='climbs/{k}'"))
    for f in FORMS: V.append((f'forms/{f}',f"location.hash='forms/{f}'"))
    for s in SC: V.append((f'analysis/{s}',f"location.hash='analysis';AN.tab='score';AN.score='{s}';AN.layers={{harm:true,cad:true,form:true}};room('analysis')"))
    V.append(('analysis/prog',"location.hash='analysis';AN.tab='prog';room('analysis')"))
    V.append(('analysis/map',"location.hash='analysis';AN.tab='map';room('analysis')"))
    for d in ['metre','rhy','qual','cad','bass','mel','blind']: V.append((f'ear/{d}',f"location.hash='ear';EAR.drill='{d}';room('ear')"))
    return V
async def main():
    widths=[int(w) for w in (sys.argv_w if False else ['1440','1024','390'])]
    res={}
    async with async_playwright() as p:
        b=await cjg.launch(p,args=[])
        for W in widths:
            pg=await b.new_page(viewport={'width':W,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:150]))
            await pg.route('**/*',route);await pg.goto('http://app/index.html');await pg.wait_for_timeout(1500)
            for name,js in views():
                await pg.evaluate(js);await pg.wait_for_timeout(1300 if name.startswith('analysis') else 500)
                await pg.evaluate("scrollTo(0,0)")
                r=await pg.evaluate(DET)
                res[f'{W} {name}']=r
                if r['overlap'] or r['clipped'] or r['offscreen']:
                    pass
            res[f'{W} errors']=errs
            await pg.close()
        await b.close()
    bad={k:v for k,v in res.items() if not k.endswith('errors') and (v['overlap'] or v['clipped'] or v['offscreen'])}
    print(json.dumps({'views':len([k for k in res if not k.endswith('errors')]),'views_with_findings':len(bad),'findings':bad,'page_errors':{k:v for k,v in res.items() if k.endswith('errors') and v}},ensure_ascii=False,indent=1))
asyncio.run(main())
