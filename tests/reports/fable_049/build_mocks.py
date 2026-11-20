"""Fable 0.49: build the ladder mock-ups from the live app (index.html is not edited).
Each scene loads the app, puts the Ear Lab in a real state, injects c5.css + ladder049.css, swaps in the new markup with mock.js,
then writes a PNG render (png/) and a static, script-free HTML copy (mocks/) at 1366x768 and 390x844.
Run from the repo root: python3 tests/reports/fable_049/build_mocks.py [scene ...]"""
import sys, asyncio, json, pathlib, re
HERE = pathlib.Path(__file__).resolve().parent; REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
CSS = (HERE / 'c5.css').read_text() + (HERE / 'ladder049.css').read_text(); JS = (HERE / 'mock.js').read_text()
SIZES = [(1366, 768), (390, 844)]
FONTS = """@font-face{font-family:'Outfit';font-weight:300;src:url(../../../../design/earlab_048/fonts/outfit-latin-300-normal.woff2) format('woff2')}
@font-face{font-family:'Outfit';font-weight:400;src:url(../../../../design/earlab_048/fonts/outfit-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:'Outfit';font-weight:600;src:url(../../../../design/earlab_048/fonts/outfit-latin-600-normal.woff2) format('woff2')}
@font-face{font-family:'Outfit';font-weight:700;src:url(../../../../design/earlab_048/fonts/outfit-latin-700-normal.woff2) format('woff2')}
@font-face{font-family:'Poiret One';font-weight:400;src:url(../../../../design/earlab_048/fonts/poiret-one-latin-400-normal.woff2) format('woff2')}"""

# Placeholder melodies in F major (do = F). The real items come from the ladder register; these only test the layout.
M4 = {'sig': '2/4', 'bars': [[{'d': '8', 's': 'd', 'given': 1}, {'d': '8', 's': 'r'}, {'d': 'q', 's': 'm'}], [{'d': 'q', 's': 's'}, {'d': '8', 's': 'm'}, {'d': '8', 's': 'r'}],
      [{'d': '8', 's': 'd'}, {'d': '8', 's': 'm'}, {'d': '8', 's': 's'}, {'d': '8', 's': 'm'}], [{'d': 'q', 's': 'r'}, {'d': 'q', 's': 'd'}]]}
M8 = {'sig': '3/4', 'bars': [[{'d': 'q', 's': 'd', 'given': 1}, {'d': 'q', 's': 'm'}, {'d': 'q', 's': 's'}], [{'d': 'qd', 's': 'l'}, {'d': '8', 's': 's'}, {'d': 'q', 's': 'm'}],
      [{'d': '8', 's': 'f'}, {'d': '8', 's': 'm'}, {'d': 'q', 's': 'r'}, {'d': 'q', 's': 't,'}], [{'d': 'h', 's': 'd'}, {'d': 'q', 'rest': 1}],
      [{'d': 'q', 's': 'm'}, {'d': 'q', 's': 's'}, {'d': 'q', 's': 'l'}], [{'d': '8', 's': 's'}, {'d': '8', 's': 'f'}, {'d': 'q', 's': 'm'}, {'d': 'q', 's': 'd'}],
      [{'d': 'q', 's': 'r'}, {'d': '8', 's': 't,'}, {'d': '8', 's': 'd'}, {'d': 'q', 's': 'r'}], [{'d': 'h', 's': 'd'}, {'d': 'q', 'rest': 1}]]}
ST = {'n': 23, 'ok': 17, 'streak': 3, 'best': 6, 'shown': 1, 'skipped': 0}
MEL_ASK = "()=>{EAR.drill='mel';EAR.lvl.mel=2;EAR.q=earGen('mel',2,R);EAR.q.plays=1;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar()}"
Q4 = 'The key chord plays first, then two clicks count you in. The first note is given. Write the rhythm, then the solfa.'
Q8 = 'The key chord plays first, then three clicks count you in. The first note is given. Write the rhythm, then the solfa.'
ASK = "(t)=>{const a=document.querySelector('#earCard .el-ask');if(a)a.textContent=t}"

SCENES = {
 # melody rung 6, step 1: rhythm being written (5 of 8 beats)
 'mel_r6_rhythm': dict(stage=6, pre=MEL_ASK, js="""(a)=>{const [M4,M8,ST,phone]=a;MK.tally(ST);
   MK.head({drill:'mel',cur:6,done:[1,2,3,4,5],stage:6,what:'Stage 5 · four bars of 2/4, crotchets and quavers, do to la',last:[1,1,0,1,1,1,0,1,null,null]});
   MK.desk({M:M4,step:1,rhTxt:'5 of 8 beats',soTxt:'after the rhythm',label:'Write the melody · bar 3 of 4',view:2,mapState:['rh','rh1'],cells:1,off:['h'],aria:'Rhythm so far: bars 1 and 2, and the first beat of bar 3'});
   MK.draw(M4,{rhythm:8,solfa:1,caret:true,bars:phone?[2,3]:null})}""", ask=Q4),
 # melody rung 6, step 2: rhythm complete, solfa 7 of 12
 'mel_r6_solfa': dict(stage=6, pre=MEL_ASK, js="""(a)=>{const [M4,M8,ST,phone]=a;MK.tally(ST);
   MK.head({drill:'mel',cur:6,done:[1,2,3,4,5],stage:6,what:'Stage 5 · four bars of 2/4, crotchets and quavers, do to la',last:[1,1,0,1,1,1,0,1,null,null]});
   MK.desk({M:M4,step:2,rhFull:true,rhTxt:'8 of 8 beats',soTxt:'7 of 12 notes',label:'Write the melody · bar 3 of 4',view:2,mapState:['so','half'],ladder:MK.ladder([-3,5],'m'),aria:'Rhythm written. Solfa so far: do re mi, so mi re, do'});
   MK.draw(M4,{solfa:7,cursor:'solfa',bars:phone?[2,3]:null})}""", ask=Q4),
 # melody rung 11: eight bars of 3/4, solfa step, in the third system
 'mel_r11_8bars': dict(stage=6, pre=MEL_ASK, js="""(a)=>{const [M4,M8,ST,phone]=a;MK.tally({n:9,ok:6,streak:2,best:4,shown:0,skipped:1});
   MK.head({drill:'mel',cur:11,done:[1,2,3,4,5,6,7,8,9],stage:6,what:'Stage 6 · eight bars of 3/4 with dotted rhythms, so, to la',last:[1,0,1,1,0,1,1,1,1,null]});
   MK.desk({M:M8,step:2,rhFull:true,rhTxt:'24 of 24 beats',soTxt:'14 of 26 notes',label:'Write the melody · bar 5 of 8',view:4,mapState:['so','so','half','rh'],ladder:MK.ladder([-3,5],'s'),aria:'Rhythm written. Solfa written to bar 5'});
   MK.draw(M8,{solfa:14,cursor:'solfa',bars:phone?[4,5]:null})}""", ask=Q8),
 # rhythm dictation at Stage 4: three rungs and the chip for the rest
 'rhy_stage4': dict(stage=4, pre="()=>{EAR.drill='rhy';EAR.lvl.rhy=2;EAR.q=earGen('rhy',2,R);EAR.q.plays=1;EAR.done=false;EAR.res=null;EAR.ans=EAR.q.a.slice(0,2);renderEar()}", js="""(a)=>{const [M4,M8,ST,phone]=a;MK.tally({n:6,ok:4,streak:1,best:3,shown:0,skipped:0});
   MK.head({drill:'rhy',cur:2,done:[1],stage:4,what:'Stage 4 · one bar of 4/4, adds semiquavers and the crotchet rest',last:[1,0,1,1,0,1,null,null,null,null]})}"""),
 # the suggestion: rhythm rung 3 answered right, 8 of the last 10, next rung starts Stage 5
 'suggest_rhy': dict(stage=6, pre="()=>{EAR.drill='rhy';EAR.lvl.rhy=3;EAR.q=earGen('rhy',3,R);EAR.q.plays=1;EAR.done=false;EAR.res=null;EAR.ans=EAR.q.a.slice();renderEar();earMark(true,EAR.q.a.slice());renderEar()}", js="""(a)=>{const [M4,M8,ST,phone]=a;MK.tally({n:31,ok:24,streak:5,best:7,shown:1,skipped:0});
   MK.head({drill:'rhy',cur:3,done:[1,2,3],sug:4,stage:6,what:'Stage 4 · two bars of 4/4 with syncopation',last:[1,1,0,1,1,1,0,1,1,1]});
   MK.sug({cur:3,next:4,lead:'8 of your last 10 right.',ask:'Ready for rung 4?',note:'Rung 4 starts Stage 5: two bars of 6/8.'})}"""), # the picker in every state, at four widths
 'picker_states': dict(stage=6, sizes=[(1440, 900), (1366, 768), (1024, 768), (390, 844)], pre=MEL_ASK, js="""(a)=>{MK.sheet([
   {cap:'Melody · Stage 6 · on rung 6',drill:'mel',cur:6,done:[1,2,3,4,5],stage:6},
   {cap:'Melody · Stage 5 · on rung 8, rung 9 suggested',drill:'mel',cur:8,done:[1,2,3,4,5,6,7,8],sug:9,stage:5},
   {cap:'Melody · Stage 4 · on rung 2',drill:'mel',cur:2,done:[1],stage:4},
   {cap:'Melody · Stage 6 · on rung 12, the Stage 4 band opened on a phone',drill:'mel',cur:12,done:[1,2,3,4,5,6,7,8,9,10,11],stage:6,open:4},
   {cap:'Rhythm · Stage 6 · on rung 3, rung 4 suggested',drill:'rhy',cur:3,done:[1,2,3],sug:4,stage:6},
   {cap:'Rhythm · Stage 5 · on rung 10 (chosen through the chip; a rung in use always shows)',drill:'rhy',cur:10,done:[1,2,3,4,5],stage:5},
   {cap:'Rhythm · Stage 4 · on rung 1',drill:'rhy',cur:1,done:[],stage:4}])}"""),
}

async def shoot(b, name, sc, w, h):
    pg = await b.new_page(viewport={'width': w, 'height': h}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    await pg.add_style_tag(content=CSS); await pg.add_script_tag(content=JS)
    await pg.evaluate("(l)=>{S.level=l;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===l));location.hash='ear';EAR.all=false;EAR.st={};room('ear');window.earPlay=()=>{};window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11)}", sc['stage'])
    await pg.evaluate(sc['pre']); await pg.wait_for_timeout(900)
    if sc.get('ask'): await pg.evaluate(ASK, sc['ask'])
    await pg.evaluate(sc['js'], [M4, M8, ST, w < 761]); await pg.wait_for_timeout(250)
    # measurements the spec quotes
    m = await pg.evaluate("""()=>{const B=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return r.width?[Math.round(r.width),Math.round(r.height)]:null};
      const small=[];document.querySelectorAll('#earCard button').forEach(e=>{if(!e.offsetParent||e.closest('.el-foot'))return;const r=e.getBoundingClientRect();if(r.height<43.5||r.width<43.5)small.push((e.className||e.parentElement.className)+':'+e.textContent.trim().slice(0,10)+':'+Math.round(r.width)+'x'+Math.round(r.height))});
      const tiny=[];document.querySelectorAll('#earCard *').forEach(e=>{if(!e.offsetParent&&!(e instanceof SVGElement))return;if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;let fs=parseFloat(getComputedStyle(e).fontSize);const sv=e.closest('svg');if(sv&&e.dataset&&e.dataset.px)fs=+e.dataset.px;else if(sv){const vb=sv.viewBox&&sv.viewBox.baseVal;if(vb&&vb.width)fs*=sv.getBoundingClientRect().width/vb.width;const k=+sv.dataset.k;if(k&&!vb.width)fs*=k}if(fs<10.95)tiny.push((e.className.baseVal!==undefined?e.className.baseVal:e.className)+':'+e.textContent.trim().slice(0,12)+':'+fs.toFixed(1))});
      return {head:B('#earCard .el-head'),rp:B('.el-rp'),band:B('.el-band.open, .el-band'),rungbtn:B('.el-band.open button, .el-band button'),tab:B('.el-bandtab:not(.open)'),more:B('.el-bandmore'),rungline:B('.el-rungline'),steps:B('.el-steps'),score:B('.melscore'),svg:B('#earMel svg'),lad:B('.melentry .earlad'),step:B('.melentry .earstep'),tile:B('.melentry .el-tile'),sug:B('.el-sug'),desk:B('.meldesk'),
       over:document.documentElement.scrollWidth-innerWidth,small:[...new Set(small)],tiny:[...new Set(tiny)]}}""")
    m['errors'] = errs
    card = await pg.query_selector('#earCard'); await card.evaluate("e=>window.scrollTo(0,e.getBoundingClientRect().top+scrollY-(innerWidth<761?104:70))"); await pg.wait_for_timeout(150)
    await pg.screenshot(path=str(HERE / 'png' / f'{name}_{w}.png'))
    if w < 761 and m.get('steps'):
        await pg.evaluate("()=>{const e=document.querySelector('.melentry');window.scrollTo(0,e.getBoundingClientRect().bottom+scrollY-innerHeight+68+10)}"); await pg.wait_for_timeout(200)
        m['sticky'] = await pg.evaluate("()=>{const s=document.querySelector('.melscore').getBoundingClientRect(),l=[...document.querySelectorAll('.melentry .earstep,.melentry .el-tile')].filter(e=>{const r=e.getBoundingClientRect();return r.top>=s.bottom&&r.bottom<=innerHeight-68});return {score_top:Math.round(s.top),score_bottom:Math.round(s.bottom),rows_fully_visible:l.length,room:innerHeight-68-Math.round(s.bottom)}}")
        await pg.screenshot(path=str(HERE / 'png' / f'{name}_{w}_entry.png'))
    await pg.add_style_tag(content='.tabbar,header.top,.el-dock{display:none!important}.meldesk.r4 .melscore{position:static!important}')   # whole-card render: fixed bars out of the way
    await card.screenshot(path=str(HERE / 'png' / f'{name}_{w}_card.png'))
    # static copy: no scripts, hidden rooms dropped, fonts and assets by relative path
    await pg.evaluate("document.querySelectorAll('style').forEach(s=>{if(s.textContent.startsWith('.tabbar,header.top,.el-dock'))s.remove()})")
    html = await pg.evaluate("""()=>{const d=document.cloneNode(true);d.querySelectorAll('script,link[rel=preconnect],link[rel=stylesheet],section.room[hidden],.msheet,dialog').forEach(e=>e.remove());return '<!doctype html>\\n'+d.documentElement.outerHTML}""")
    html = html.replace('<head>', '<head><!-- Static mock-up, Fable 0.49 (%s at %d px). Built by tests/reports/fable_049/build_mocks.py; not production code. --><style>%s</style>' % (name, w, FONTS), 1)
    html = html.replace('url(fonts/', 'url(../../../../fonts/').replace('url("fonts/', 'url("../../../../fonts/')
    (HERE / 'mocks' / f'{name}_{w}.html').write_text(html, encoding='utf8')
    await pg.close(); return m

async def main():
    want = sys.argv[1:] or list(SCENES); out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for name in want:
            for w, h in SCENES[name].get('sizes', SIZES):
                out[f'{name}_{w}'] = await shoot(b, name, SCENES[name], w, h)
        await b.close()
    mp = HERE / 'png' / 'metrics.json'; old = json.loads(mp.read_text()) if mp.exists() else {}; old.update(out); mp.write_text(json.dumps(old, indent=1))
    for k, v in out.items(): print(k, json.dumps({a: b for a, b in v.items() if b not in (None, [], 0)}))
asyncio.run(main())
