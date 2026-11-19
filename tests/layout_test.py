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
    V.append(('climbs/13/fugue',"location.hash='climbs/13';setTimeout(()=>document.querySelector('[data-c13tab=\"fugue\"]')?.click(),50)"))
    for f in FORMS: V.append((f'forms/{f}',f"location.hash='forms/{f}'"))
    for s in SC: V.append((f'analysis/{s}',f"location.hash='analysis';AN.tab='score';AN.score='{s}';AN.layers={{harm:true,cad:true,form:true}};room('analysis')"))
    V.append(('analysis/prog',"location.hash='analysis';AN.tab='prog';room('analysis')"))
    V.append(('analysis/map',"location.hash='analysis';AN.tab='map';room('analysis')"))
    for d in ['metre','rhy','qual','cad','bass','mel','blind']: V.append((f'ear/{d}',f"location.hash='ear';EAR.drill='{d}';room('ear')"))
    return V

EARQ="""(()=>{const out=[];const W=innerWidth;const tb=document.querySelector('.tabbar,#tabbar,nav.tabs');const tbTop=tb&&getComputedStyle(tb).position==='fixed'?tb.getBoundingClientRect().top:innerHeight;
const dk=document.querySelector('.el-dock');const dkr=dk&&dk.offsetParent!==null?dk.getBoundingClientRect():null;
const m=document.getElementById('earMain');if(!m)return{small:['no earMain'],covered:[]};
const small=[],covered=[];
for(const e of m.querySelectorAll('button,[role=button],[role=radio],[data-earopt],input,select')){const r=e.getBoundingClientRect();if(!r.width||!r.height||e.offsetParent===null)continue;
 if(W<=500&&(r.height<43.5||r.width<43.5)&&!e.closest('.earladder'))small.push((e.className||e.tagName)+' '+(e.textContent||'').trim().slice(0,18)+' '+Math.round(r.width)+'x'+Math.round(r.height));
 if(W<=500&&e.closest('.earladder')&&r.height<43.5&&r.width<43.5)small.push('ladder '+(e.textContent||'').trim().slice(0,10)+' '+Math.round(r.width)+'x'+Math.round(r.height));}
return{small,covered}})()"""
async def ear_states(pg,W):
    """Ear Lab with a question open and answered, per drill: targets >=44px on phones, no sideways scroll, nothing under the tab bar or dock."""
    out={}
    for d in ['metre','rhy','qual','cad','bass','mel','blind']:
        await pg.evaluate(f"location.hash='ear';EAR.drill='{d}';room('ear')");await pg.wait_for_timeout(350)
        await pg.evaluate("(()=>{const b=document.querySelector('[data-earplay=\"all\"]');b&&b.click()})()");await pg.wait_for_timeout(400)
        await pg.evaluate("elStop&&elStop()")
        for stage in ['asked','answered']:
            if stage=='answered':
                await pg.evaluate("document.querySelector('[data-earshow]')?.click()")
                await pg.wait_for_timeout(300)
            await pg.evaluate("scrollTo(0,0)")
            r=await pg.evaluate(DET)
            sw=await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
            q=await pg.evaluate(EARQ)
            off=list(r['offscreen'])
            if sw>1: off.append(f'page scrolls sideways by {sw}px')
            off+=['target under 44px: '+x for x in q['small']]
            # nothing hidden behind the fixed tab bar or dock: the last control must be reachable by scrolling
            await pg.evaluate("scrollTo(0,document.documentElement.scrollHeight)")
            cov=await pg.evaluate("""(()=>{const m=document.getElementById('earMain');if(!m)return[];const f=[...document.querySelectorAll('.tabbar,nav.tabs,.el-dock')].filter(e=>e.offsetParent!==null&&getComputedStyle(e).position==='fixed');const top=Math.min(innerHeight,...f.map(e=>e.getBoundingClientRect().top));const bad=[];for(const e of m.querySelectorAll('button,.el-result,.el-foot')){const r=e.getBoundingClientRect();if(r.height&&r.bottom>top+1&&r.top<innerHeight-1&&e.offsetParent!==null&&f.length)bad.push((e.className||e.tagName)+' under bar')}return bad.slice(0,3)})()""")
            off+=cov
            out[f'ear-card/{d}/{stage}']={'overlap':r['overlap'],'clipped':r['clipped'],'offscreen':off}
    return out
async def main():
    widths=[int(w) for w in (sys.argv_w if False else ['1440','1366','1024','390'])]
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
                sw=await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
                if sw>1: r['offscreen']=list(r['offscreen'])+[f'page scrolls sideways by {sw}px']
                res[f'{W} {name}']=r
                if r['overlap'] or r['clipped'] or r['offscreen']:
                    pass
            for name,r in (await ear_states(pg,W)).items(): res[f'{W} {name}']=r
            res[f'{W} errors']=errs
            await pg.close()
        await b.close()
    bad={k:v for k,v in res.items() if not k.endswith('errors') and (v['overlap'] or v['clipped'] or v['offscreen'])}
    print(json.dumps({'views':len([k for k in res if not k.endswith('errors')]),'views_with_findings':len(bad),'findings':bad,'page_errors':{k:v for k,v in res.items() if k.endswith('errors') and v}},ensure_ascii=False,indent=1))
    sys.exit(1 if bad or any(v for k,v in res.items() if k.endswith('errors')) else 0)
asyncio.run(main())
