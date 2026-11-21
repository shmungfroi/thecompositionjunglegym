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

ISSQ="""(()=>{const out=[];
 const rr=n=>{const r=document.createRange();r.selectNodeContents(n);return[...r.getClientRects()].filter(q=>q.width>1&&q.height>1)};
 document.querySelectorAll('main .iss').forEach(row=>{if(!row.getClientRects().length)return;const lab=(row.textContent||'').trim().slice(0,30),boxes=[];
  const w=document.createTreeWalker(row,NodeFilter.SHOW_TEXT);let n;while(n=w.nextNode()){if(!n.textContent.trim())continue;for(const q of rr(n))boxes.push({t:n.textContent.trim().slice(0,18),q,el:n.parentElement})}
  // no text overlaps another text box in the same row
  for(let i=0;i<boxes.length;i++)for(let j=i+1;j<boxes.length;j++){const a=boxes[i].q,b=boxes[j].q,ix=Math.min(a.right,b.right)-Math.max(a.left,b.left),iy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);if(ix>1&&iy>2)out.push('iss text overlap in "'+lab+'": "'+boxes[i].t+'" x "'+boxes[j].t+'"')}
  // no span in the row narrower than its own text (a squeezed chip or gloss)
  row.querySelectorAll('span').forEach(sp=>{const t=sp.textContent.trim();if(!t)return;const bw=sp.getBoundingClientRect().width,tw=Math.max(0,...rr(sp).map(q=>q.width));if(bw+1<tw)out.push('iss span narrower than its text in "'+lab+'": "'+t.slice(0,18)+'" box '+Math.round(bw)+' text '+Math.round(tw))});
 });
 // score numeral labels lie inside their frame (the SVG, which the frame clips)
 document.querySelectorAll('main .sframe svg').forEach(svg=>{const R=svg.getBoundingClientRect();if(!R.width)return;svg.querySelectorAll('text.rnl').forEach(t=>{const r=t.getBoundingClientRect();if(!r.width)return;if(r.bottom>R.bottom+0.5||r.top<R.top-0.5||r.left<R.left-0.5||r.right>R.right+0.5)out.push('score numeral outside its frame: "'+t.textContent+'" bottom '+Math.round(r.bottom)+' > '+Math.round(R.bottom))})});
 return out.slice(0,12)})()"""
VOICE="""(()=>{S.level=6;K.mode='maj';K.k=10;P=[];addRomans('Imaj7 viiø7 vi7 vi7 iii7 ii7 viiø7 vi7');location.hash='voice';room('voice')})()"""
EARQ="""(()=>{const out=[];const W=innerWidth;const tb=document.querySelector('.tabbar,#tabbar,nav.tabs');const tbTop=tb&&getComputedStyle(tb).position==='fixed'?tb.getBoundingClientRect().top:innerHeight;
const dk=document.querySelector('.el-dock');const dkr=dk&&dk.offsetParent!==null?dk.getBoundingClientRect():null;
const m=document.getElementById('earMain');if(!m)return{small:['no earMain'],covered:[]};
const small=[],covered=[];
for(const e of m.querySelectorAll('button,[role=button],[role=radio],[data-earopt],input,select')){const r=(e.tagName==='INPUT'&&e.closest('label')?e.closest('label'):e).getBoundingClientRect();if(!r.width||!r.height||e.offsetParent===null)continue;
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
            # the dock is a fixed overlay that by design (V-1) covers the panel while its Next button is not fully visible: measure the card without it
            await pg.evaluate("document.querySelectorAll('.el-dock').forEach(e=>e.style.visibility='hidden')")
            r=await pg.evaluate(DET)
            sw=await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
            q=await pg.evaluate(EARQ)
            await pg.evaluate("document.querySelectorAll('.el-dock').forEach(e=>e.style.visibility='')")
            off=list(r['offscreen'])
            if sw>1: off.append(f'page scrolls sideways by {sw}px')
            off+=['target under 44px: '+x for x in q['small']]
            # nothing hidden behind the fixed tab bar or dock: the last control must be reachable by scrolling
            await pg.evaluate("scrollTo(0,document.documentElement.scrollHeight)")
            cov=await pg.evaluate("""(()=>{const m=document.getElementById('earMain');if(!m)return[];const f=[...document.querySelectorAll('.tabbar,nav.tabs,.el-dock')].filter(e=>e.offsetParent!==null&&getComputedStyle(e).position==='fixed');const top=Math.min(innerHeight,...f.map(e=>e.getBoundingClientRect().top));const bad=[];for(const e of m.querySelectorAll('button,.el-result,.el-foot')){const r=e.getBoundingClientRect();if(r.height&&r.bottom>top+1&&r.top<innerHeight-1&&e.offsetParent!==null&&f.length)bad.push((e.className||e.tagName)+' under bar')}return bad.slice(0,3)})()""")
            off+=cov
            out[f'ear-card/{d}/{stage}']={'overlap':r['overlap'],'clipped':r['clipped'],'offscreen':off}
    return out
LADSCENE="""([d,l,mod,frac,spoil,chk,wantS])=>{EAR.mod=mod;S.level=6;const want=wantS?new Function('q','return '+wantS):null;let q;
 for(let t=0;t<300;t++){EAR.drill=d;EAR.lvl[d]=l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();q=EAR.q;if(!want||want(q))break}
 try{elStop()}catch(e){}
 if(d==='rhy'){const n=Math.floor(q.a.length*frac);for(let j=0;j<n;j++){const b=document.querySelector(`.el-tile[data-earcell="${q.a[j]}"]`);if(b&&!b.disabled)b.click()}
  if(spoil){while(!earFull(q)){const t=[...document.querySelectorAll('.el-tile:not([disabled])')].pop();if(!t)break;t.click()}}
  if(chk)earCheck();return}
 const T=ladTruthEntries(q,'mel'),n=Math.floor(T.length*frac);
 for(let j=0;j<n;j++){const e=T[j],idx=j+1;if(e.s===null){document.querySelector(`[data-rest="${e.t}"]`).click();continue}
  const lb=document.querySelector(`[data-len="${e.t}"]`);if(lb.getAttribute('aria-checked')!=='true')lb.click();
  let nm=e.s;if(q.l===9&&mod==='move'&&q.readings&&idx>q.pivot)nm=q.readings.move[idx];
  if(spoil&&j===spoil)nm=[...document.querySelectorAll('[data-earsol]')].map(x=>x.dataset.earsol).find(x=>x!==nm&&!/[a-z]{2}/.test(x))||nm;
  document.querySelector(`[data-earsol="${nm}"]`).click();if(q.l===9&&mod==='move'&&q.readings&&idx===q.pivot&&frac>.45)document.querySelector('[data-earmut]').click()}
 if(chk)earCheck()}"""
LADVIEWS=[('long header',['mel',6,'home',0,0,0,None]),('palette desk',['mel',6,'home',.6,0,0,None]),('result state',['mel',6,'home',1,3,1,None]),
 ('rung 7',['mel',7,'home',1,5,1,'q.aug2&&q.aug2.length']),('rung 9 Move do',['mel',9,'move',.7,0,0,"q.readings&&q.kind==='M-V'"]),
 ('rung 12 semiquavers 4/4',['mel',12,'home',.4,0,0,"q.metre==='4/4'&&ladEntriesToLine(q,ladTruthEntries(q,'mel'),'mel').some(x=>x.dur===105)"]),
 ('rung 12 semiquavers 3/4',['mel',12,'home',.4,0,0,"q.metre==='3/4'&&ladEntriesToLine(q,ladTruthEntries(q,'mel'),'mel').some(x=>x.dur===105)"]),
 ('rung 12 semiquavers result',['mel',12,'home',1,0,1,"q.metre==='4/4'&&ladEntriesToLine(q,ladTruthEntries(q,'mel'),'mel').some(x=>x.dur===105)"]),
 ('rhythm rung 10',['rhy',10,'home',.5,0,0,None]),('rhythm rung 9 7/8 result',['rhy',9,'home',1,0,1,"q.metre==='7/8'"]),
 ('rhythm rung 9',['rhy',9,'home',.5,0,0,None]),('rhythm rung 9 result',['rhy',9,'home',1,1,1,None])]
async def ladder_views(pg):
    out={}
    for name,a in LADVIEWS:
        await pg.evaluate(LADSCENE,a);await pg.wait_for_timeout(250);await pg.evaluate("scrollTo(0,0)")
        await pg.evaluate("document.querySelectorAll('.el-dock').forEach(e=>e.style.visibility='hidden')")
        r=await pg.evaluate(DET);sw=await pg.evaluate('document.documentElement.scrollWidth-innerWidth');q=await pg.evaluate(EARQ)
        off=list(r['offscreen'])
        if sw>1: off.append(f'page scrolls sideways by {sw}px')
        off+=['target under 44px: '+x for x in q['small']]
        out[f'ear-ladder/{name}']={'overlap':r['overlap'],'clipped':r['clipped'],'offscreen':off}
        await pg.evaluate("document.querySelectorAll('.el-dock').forEach(e=>e.style.visibility='')")
    return out
NAMESWEEP="""([nm,per])=>{EAR.names=nm;S.level=6;const out=[];let items=0,names=0;
 for(const l of [7,8,9,10])for(let i=0;i<per;i++){EAR.drill='rhy';EAR.lvl.rhy=l;EAR.q=null;EAR.done=false;EAR.res=null;earNew();const q=EAR.q;try{elStop()}catch(e){}
  for(const k of q.a){const b=document.querySelector(`.el-tile[data-earcell="${k}"]`);if(b&&!b.disabled)b.click()}
  if(earFull(q))earCheck();items++;
  document.querySelectorAll('#earMain svg.el-rsvg').forEach((sv,si)=>{const T=[...sv.querySelectorAll('text.melname')].map(t=>({t:t.textContent,r:t.getBoundingClientRect()}));const R=sv.getBoundingClientRect();names+=T.length;
   for(let a=0;a<T.length;a++){const A=T[a].r;if(A.left<R.left-.5||A.right>R.right+.5)out.push({a:T[a].t,b:'(outside its bar)',rung:l,cells:q.a.join(' ')});
    for(let c=a+1;c<T.length;c++){const B=T[c].r,ix=Math.min(A.right,B.right)-Math.max(A.left,B.left),iy=Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top);if(ix>0&&iy>0)out.push({a:T[a].t,b:T[c].t,rung:l,cells:q.a.join(' ')})}}})}
 return{out,items,names}}"""
async def names_sweep(pg,W):
    out={}
    for nm in ('k','kk'):
        r=await pg.evaluate(NAMESWEEP,[nm,40 if W<500 else 15])
        out[f'ear-ladder/rhythm names rungs 7-10 ({nm}, {r["items"]} items, {r["names"]} names)']={'overlap':r['out'][:5],'clipped':[],'offscreen':[]}
        if not r['names']: out[f'ear-ladder/rhythm names rungs 7-10 ({nm}) self-check']={'overlap':[],'clipped':['no names were drawn, the sweep is empty'],'offscreen':[]}
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
                r['clipped']=list(r['clipped'])+await pg.evaluate(ISSQ)
                sw=await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
                if sw>1: r['offscreen']=list(r['offscreen'])+[f'page scrolls sideways by {sw}px']
                res[f'{W} {name}']=r
                if r['overlap'] or r['clipped'] or r['offscreen']:
                    pass
            # regression ISSFIX-049: Voices with a progression that breaks rules (checker rows) in B flat, Stage 6
            await pg.evaluate(VOICE);await pg.wait_for_timeout(1500);await pg.evaluate("scrollTo(0,0)")
            r=await pg.evaluate(DET);r['clipped']=list(r['clipped'])+await pg.evaluate(ISSQ)
            if not await pg.evaluate("document.querySelectorAll('#satbCheck .iss').length"): r['clipped'].append('self-check: no checker rows rendered, the regression view is empty')
            res[f'{W} voice/iss-rows']=r
            for name,r in (await ear_states(pg,W)).items(): res[f'{W} {name}']=r
            for name,r in (await ladder_views(pg)).items(): res[f'{W} {name}']=r
            for name,r in (await names_sweep(pg,W)).items(): res[f'{W} {name}']=r
            res[f'{W} errors']=errs
            await pg.close()
        await b.close()
    bad={k:v for k,v in res.items() if not k.endswith('errors') and (v['overlap'] or v['clipped'] or v['offscreen'])}
    print(json.dumps({'views':len([k for k in res if not k.endswith('errors')]),'views_with_findings':len(bad),'findings':bad,'page_errors':{k:v for k,v in res.items() if k.endswith('errors') and v}},ensure_ascii=False,indent=1))
    sys.exit(1 if bad or any(v for k,v in res.items() if k.endswith('errors')) else 0)
asyncio.run(main())
