"""Score measure suite (0.47 house engraving standard), self-check for every VexFlow score view at 1440, 1024 and 390 px.
Run: python3 tests/score_measure_test.py <repo dir>

For every visible VexFlow score (svg.vfx inside a .sframe) in every view below:
  S  staff-space: the gap between staff lines, measured on screen, is the task value (glance 6 px; exercise 7 px on
     desktop >= 900 px, 6.5 px on phones) within 0.15 px.
  R  whole-bar rests centred in their bar within 2 px (FR-2).
  K  climb 4: each chord card's edges within 4 px of its bar's barlines (K2).
  T  text: every SVG text renders at >= 11 px, except stacked figured-bass figures (class fig) at 9 px.
  O  no sideways overflow on desktop: the score frame never scrolls sideways at 1440 and 1024.
  L  ledger lines: ivory at 70% (never #444), 1.2 px on screen.
  B  bar sums: every non-empty voice fills its bar (reported by the engraving layer as data-incomplete).
  X  no text-on-text overlap inside a score (overlap > 20% of the smaller box).
  E  no page errors while drawing.
"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

def views():
    V = [('seed', "location.hash='seed'"), ('voice', "location.hash='voice'"),
         ('keys/scales', "location.hash='keys'"),
         ('keys/chromatic', "location.hash='keys';KS.tab='scales';KS.tonic='C';KS.sc='chrom';renderKeysRoom()"),
         ('keys/A# chromatic (triple sharp respelled)', "location.hash='keys';KS.tab='scales';KS.tonic='A#';KS.sc='chrom';renderKeysRoom()"),
         ('keys/E# octatonic (triple sharp respelled)', "location.hash='keys';KS.tab='scales';KS.tonic='E#';KS.sc='oct';renderKeysRoom()"),
         ('keys/intervals', "location.hash='keys';KS.tab='intervals';renderKeysRoom()"),
         ('keys/circle', "location.hash='keys';KS.tab='circle';renderKeysRoom()"),
         ('keys/back', "location.hash='keys';KS.tab='scales';KS.tonic='C';KS.sc='maj';renderKeysRoom()")]
    for k in range(1, 14):
        V.append((f'climbs/{k}', f"location.hash='climbs/{k}'"))
    for sp in [1, 2, 3, 4, 5]:
        V.append((f'climbs/2 species {sp}', f"location.hash='climbs/2';C2.sp={sp};renderClimb2()"))
    V.append(('climbs/2 three voices', "location.hash='climbs/2';C2.sp=6;C2.c3.sp=1;renderClimb2()"))
    V.append(('climbs/2 three voices species 2', "location.hash='climbs/2';C2.sp=6;C2.c3.sp=2;renderClimb2()"))
    V.append(('climbs/2 back', "location.hash='climbs/2';C2.sp=1;C2.c3.sp=1;renderClimb2()"))
    V.append(('climbs/12 planing', "location.hash='climbs/12';C12.tab='plane';renderClimb12()"))
    V.append(('climbs/12 static', "location.hash='climbs/12';C12.tab='static';renderClimb12()"))
    V.append(('climbs/13 fugue', "location.hash='climbs/13';C13.tab='fugue';renderClimb13()"))
    for f in ['phrase', 'tv']:
        V.append((f'forms/{f}', f"location.hash='forms/{f}'"))
    V.append(('climbs/2 rule examples', "location.hash='climbs/2';C2.sp=1;renderClimb2();document.querySelectorAll('details.c2rule').forEach(d=>{d.open=true;c2DrawEx(d.dataset.c2card)})"))
    V.append(('ear/rhy question', "location.hash='ear';EAR.drill='rhy';room('ear');earNew()"))
    V.append(('ear/rhy answer', "earMark(false,[]);renderEar()"))
    V.append(('ear/mel answer', "location.hash='ear';EAR.drill='mel';room('ear');earNew();earMark(false,[]);renderEar()"))
    V.append(('ear/rhy stave rung 1', "location.hash='ear';EAR.drill='rhy';EAR.lvl.rhy=1;room('ear');earNew()"))
    V.append(('ear/rhy stave rung 3 answered', "EAR.lvl.rhy=3;earNew();earMark(false,[]);renderEar()"))
    V.append(('ear/rhy stave rung 5 answered', "EAR.lvl.rhy=5;earNew();earMark(false,[]);renderEar()"))
    return V

# EL-5: the one-line rhythm stave is inline SVG inside .el-rhy (not VexFlow): five-line stave on one line, final barline,
# text >= 11 px on screen, nothing wider than its frame, one stave per bar group, no text on text.
RHY = r"""()=>{const out=[];document.querySelectorAll('#earMain .el-rhy').forEach(box=>{if(!box.getClientRects().length)return;const f=[];
 const svg=box.querySelector('svg');if(!svg){f.push('no svg');out.push({id:'el-rhy',f});return}
 const k=svg.getScreenCTM().a;
 svg.querySelectorAll('text').forEach(t=>{if(!t.textContent.trim())return;const px=parseFloat(t.getAttribute('font-size')||getComputedStyle(t).fontSize)*k;if(px<10.95)f.push(`T "${t.textContent.slice(0,10)}" ${px.toFixed(1)} px`)});
 const sr=svg.getBoundingClientRect(),br=box.getBoundingClientRect();if(sr.right>br.right+1||sr.left<br.left-1)f.push(`W svg ${Math.round(sr.width)} px wider than frame ${Math.round(br.width)}`);
 if(box.scrollWidth>box.clientWidth+1)f.push('O scrolls sideways');
 const ys=new Set([...svg.querySelectorAll('line,path')].filter(e=>{const b=e.getBoundingClientRect();return b.height<1.5&&b.width>60}).map(e=>Math.round(e.getBoundingClientRect().top)));
 if(ys.size<1)f.push('S no stave line');
 const T=[...svg.querySelectorAll('text')].filter(t=>t.textContent.trim()).map(t=>({t:t.textContent.slice(0,8),r:t.getBoundingClientRect()}));
 for(let i=0;i<T.length;i++)for(let j=i+1;j<T.length;j++){const a=T[i].r,b=T[j].r,ix=Math.min(a.right,b.right)-Math.max(a.left,b.left),iy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);if(ix>1&&iy>1&&ix*iy>0.2*Math.min(a.width*a.height,b.width*b.height))f.push(`X "${T[i].t}" over "${T[j].t}"`)}
 out.push({id:'el-rhy '+(box.className||''),task:'rhy',n:1,f:[...new Set(f)].slice(0,6),resp:''})});return out}"""
MEASURE = r"""(W)=>{const out=[];const desk=document.documentElement.clientWidth>=900;
 document.querySelectorAll('main .sframe').forEach(fr=>{const svg=fr.querySelector('svg.vfx');if(!svg||!fr.getClientRects().length)return;
  const task=svg.dataset.task,want=task==='glance'?6:desk?7:6.5,id=fr.id||fr.className,f=[];
  const sp=[];svg.querySelectorAll('g.vf-stave').forEach(g=>{const ys=[...g.querySelectorAll(':scope>path')].map(p=>{const r=p.getBoundingClientRect();return r.top+r.height/2}).sort((a,b)=>a-b);for(let i=1;i<ys.length;i++)sp.push(ys[i]-ys[i-1])});
  const bad=sp.filter(d=>Math.abs(d-want)>0.15);if(!sp.length)f.push('S no staff lines');else if(bad.length)f.push(`S staff-space ${bad[0].toFixed(2)} px, want ${want}`);
  const k=svg.getScreenCTM().a,T=[];
  svg.querySelectorAll('text').forEach(t=>{if(!t.textContent.trim())return;const px=parseFloat(t.getAttribute('font-size'))*k,fig=t.classList.contains('fig');
   if(fig?Math.abs(px-9)>0.3:px<10.95)f.push(`T "${t.textContent.slice(0,12)}" ${px.toFixed(1)} px`);const r=t.getBoundingClientRect();if(r.width>0)T.push({t:t.textContent.slice(0,12),r,fig})});
  if(desk&&fr.scrollWidth>fr.clientWidth+1)f.push(`O scrolls sideways by ${fr.scrollWidth-fr.clientWidth} px`);
  svg.querySelectorAll('path.ledger').forEach(p=>{const s=p.getAttribute('stroke'),w=parseFloat(p.getAttribute('stroke-width'))*k;if(s!=='rgba(236,226,200,.7)'||Math.abs(w-1.2)>0.05)f.push(`L ledger ${s} ${w.toFixed(2)} px`)});
  if(svg.querySelector('[stroke="#444"],[fill="#444"]'))f.push('L #444 present');
  if(svg.dataset.incomplete)f.push('B incomplete: '+svg.dataset.incomplete);
  for(let i=0;i<T.length;i++)for(let j=i+1;j<T.length;j++){const a=T[i].r,b=T[j].r;if(T[i].fig||T[j].fig)continue;const ix=Math.min(a.right,b.right)-Math.max(a.left,b.left),iy=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);
   if(ix>1&&iy>1&&ix*iy>0.2*Math.min(a.width*a.height,b.width*b.height))f.push(`X "${T[i].t}" over "${T[j].t}"`)}
  // FR-2: a whole-bar rest is centred in its bar
  svg.querySelectorAll('g.vf-stavenote[data-mid]').forEach(g=>{const m=svg.getScreenCTM(),x=+g.dataset.mid*m.a+m.e,hs=[...g.querySelectorAll('.vf-notehead')].map(h=>h.getBoundingClientRect()).filter(r=>r.width>0),r=hs.length?(()=>{const R=Math.max(...hs.map(h=>h.right)),w=Math.min(...hs.map(h=>h.width));return{left:R-w,right:R}})():g.getBoundingClientRect();if(Math.abs((r.left+r.right)/2-x)>2)f.push(`R rest or chord off centre by ${((r.left+r.right)/2-x).toFixed(1)} px`)});
  out.push({id,task,n:sp.length,f:[...new Set(f)].slice(0,6),resp:fr.dataset.resp||''})});
 // K2: climb 4 cards sit on their bars (card edge within 4 px of the bar's barlines)
 [0,1].forEach(si=>{const cs=document.querySelectorAll(`#c4C${si} .c4card`),rs=document.querySelectorAll(`#c4S${si} rect.bhl`);if(!cs.length)return;const f=[];
  cs.forEach((c,i)=>{const a=c.getBoundingClientRect(),b=rs[i]&&rs[i].getBoundingClientRect();if(!b){f.push('K no bar for card '+(si*4+i+1));return}if(Math.abs(a.left-3-b.left)>4||Math.abs(a.right+3-b.right)>4)f.push(`K card ${si*4+i+1} off its bar: ${(a.left-3-b.left).toFixed(1)}/${(a.right+3-b.right).toFixed(1)} px`)});
  out.push({id:'c4 cards '+si,task:'cards',n:1,f,resp:''})});
 return out}"""

async def main():
    res, total, fails, errs = {}, 0, 0, {}
    async with async_playwright() as p:
        b = await cjg.launch(p, args=[])
        for W in [1440, 1024, 390]:
            pg = await b.new_page(viewport={'width': W, 'height': 900}); E = []
            pg.on('pageerror', lambda e: E.append(str(e)[:200]))
            await pg.route('**/*', cjg.make_route(str(REPO))); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(1500)
            for name, js in views():
                try:
                    await pg.evaluate(js)
                except Exception as e:
                    E.append(f'{name}: {str(e)[:150]}')
                await pg.wait_for_timeout(600)
                r = await pg.evaluate(MEASURE, W)
                if name.startswith('ear/rhy'): r = r + await pg.evaluate(RHY)
                for s in r:
                    total += 1
                    if s['f']:
                        fails += 1; res.setdefault(f'{W} {name}', []).append({'score': s['id'], 'findings': s['f']})
            if E: errs[W] = E
            await pg.close()
        await b.close()
    print(json.dumps({'scores_measured': total, 'scores_with_findings': fails, 'findings': res, 'page_errors': errs}, indent=1, ensure_ascii=False))
    sys.exit(1 if fails or errs or total < 60 else 0)

asyncio.run(main())
