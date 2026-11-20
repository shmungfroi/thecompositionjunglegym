"""Fable 0.49, entry A/B preview (decision D6 here, D3 in the ladder register).
Builds option (a) rhythm first then solfa, and option (b) a length palette plus the ladder, from the live app
with the same placeholder melody at the same moment (7 of 12 notes), at 1366x768 and 390x844.
Writes static HTML, PNG renders, the parts the comparison sheet uses, parts/metrics.json and sheet_ab.png.
Run from the repo root: python3 tests/reports/fable_049/entry_ab/build_entry_ab.py"""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent; F49 = HERE.parent; REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
CSS = (F49 / 'c5.css').read_text() + (F49 / 'ladder049.css').read_text() + (HERE / 'entry_b.css').read_text()
JS = (F49 / 'mock.js').read_text() + (HERE / 'entry_ab.js').read_text()
FONTS = "".join("@font-face{font-family:'%s';font-weight:%s;src:url(../../../../design/earlab_048/fonts/%s) format('woff2')}\n" % t for t in [
    ('Outfit', 300, 'outfit-latin-300-normal.woff2'), ('Outfit', 400, 'outfit-latin-400-normal.woff2'), ('Outfit', 600, 'outfit-latin-600-normal.woff2'),
    ('Outfit', 700, 'outfit-latin-700-normal.woff2'), ('Poiret One', 400, 'poiret-one-latin-400-normal.woff2')])
# Placeholder melody, F major, rung 6: four bars of 2/4, 12 notes. The same as mocks/mel_r6_*.
M4 = {'sig': '2/4', 'bars': [[{'d': '8', 's': 'd', 'given': 1}, {'d': '8', 's': 'r'}, {'d': 'q', 's': 'm'}], [{'d': 'q', 's': 's'}, {'d': '8', 's': 'm'}, {'d': '8', 's': 'r'}],
      [{'d': '8', 's': 'd'}, {'d': '8', 's': 'm'}, {'d': '8', 's': 's'}, {'d': '8', 's': 'm'}], [{'d': 'q', 's': 'r'}, {'d': 'q', 's': 'd'}]]}
ST = {'n': 23, 'ok': 17, 'streak': 3, 'best': 6, 'shown': 1, 'skipped': 0}
PRE = "()=>{EAR.drill='mel';EAR.lvl.mel=2;EAR.q=earGen('mel',2,R);EAR.q.plays=1;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar()}"
HEAD = "MK.tally(ST);MK.head({drill:'mel',cur:6,done:[1,2,3,4,5],stage:6,what:'Stage 5 · four bars of 2/4, crotchets and quavers, do to la',last:[1,1,0,1,1,1,0,1,null,null]});"
QA = 'The key chord plays first, then two clicks count you in. The first note is given. Write the rhythm, then the solfa.'
QB = 'The key chord plays first, then two clicks count you in. The first note is given. Choose a length, then tap the note.'
SCENES = {
 'a': dict(ask=QA, js="(a)=>{const [M4,ST,phone]=a;" + HEAD + """
   MK.desk({M:M4,step:2,rhFull:true,rhTxt:'8 of 8 beats',soTxt:'7 of 12 notes',label:'Write the melody · bar 3 of 4',view:2,mapState:['so','rh'],ladder:MK.ladder([-3,5],'d'),aria:'Rhythm written. Solfa so far: do re mi, so mi re, do'});
   MK.draw(M4,{solfa:7,cursor:'solfa',bars:phone?[2,3]:null})}"""),
 'b': dict(ask=QB, js="(a)=>{const [M4,ST,phone]=a;" + HEAD + """
   MK.deskB({M:M4,lens:[['q','ta','crotchet'],['e1','ti','quaver'],['h','ta-a','minim']],len:'e1',off:['h'],label:'Write the melody · bar 3 of 4',view:2,mapState:['so',''],ladder:MK.ladder([-3,5],'d'),aria:'Written so far: do re mi, so mi re, do'});
   MK.draw(M4,{rhythm:7,solfa:7,caret:true,bars:phone?[2,3]:null});MK.palStick()}"""),
 # option (a), step 1, for the inset on the sheet only (the full mock is mocks/mel_r6_rhythm_*)
 'a_step1': dict(ask=QA, js="(a)=>{const [M4,ST,phone]=a;" + HEAD + """
   MK.desk({M:M4,step:1,rhTxt:'5 of 8 beats',soTxt:'after the rhythm',label:'Write the melody · bar 3 of 4',view:2,mapState:['rh','rh1'],cells:1,off:['h'],aria:'Rhythm so far'});
   MK.draw(M4,{rhythm:8,solfa:1,caret:true,bars:phone?[2,3]:null})}"""),
}
MEASURE = """()=>{const B=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return r.width?[Math.round(r.width),Math.round(r.height)]:null};
  const all=s=>[...new Set([...document.querySelectorAll(s)].map(e=>{const r=e.getBoundingClientRect();return Math.round(r.width)+'x'+Math.round(r.height)}))];
  const small=[];document.querySelectorAll('#earCard button').forEach(e=>{if(!e.offsetParent||e.closest('.el-foot'))return;const r=e.getBoundingClientRect();if(r.height<43.5||r.width<43.5)small.push((e.className||e.parentElement.className)+':'+e.textContent.trim().slice(0,10)+':'+Math.round(r.width)+'x'+Math.round(r.height))});
  const tiny=[];document.querySelectorAll('#earCard *').forEach(e=>{if(!e.offsetParent||e.closest('svg'))return;if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<10.95)tiny.push(e.className+':'+fs)});
  return {card:B('#earCard'),head:B('#earCard .el-head'),desk:B('.meldesk'),steps:B('.el-steps'),step_btn:all('.el-steps button'),pal:B('.el-pal'),len_btn:all('.el-len'),entry:B('.melentry'),lad:B('.melentry .earlad'),lad_row:all('.melentry .earstep'),tile:all('.melentry .el-tile'),
   score:B('.melscore'),svg:B('#earMel svg'),sysmap_btn:all('.el-sysmap button').filter(x=>x!=='0x0'),over:document.documentElement.scrollWidth-innerWidth,small:[...new Set(small)],tiny:[...new Set(tiny)]}}"""

async def shoot(b, name, sc, w, h):
    pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    await pg.add_style_tag(content=CSS); await pg.add_script_tag(content=JS)
    await pg.evaluate("()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='ear';EAR.all=false;EAR.st={};room('ear');window.earPlay=()=>{};window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11)}")
    await pg.evaluate(PRE); await pg.wait_for_timeout(900)
    await pg.evaluate("(t)=>{const a=document.querySelector('#earCard .el-ask');if(a)a.textContent=t}", sc['ask'])
    await pg.evaluate(sc['js'], [M4, ST, w < 761]); await pg.wait_for_timeout(300)
    m = await pg.evaluate(MEASURE); m['errors'] = errs
    P = HERE / 'parts'; phone = w < 761; card = await pg.query_selector('#earCard')
    if phone:
        # the phone screen while entering: scrolled so the foot of the entry sits just above the tab bar
        await pg.evaluate("()=>{const e=document.querySelector('.melentry');window.scrollTo(0,e.getBoundingClientRect().bottom+scrollY-innerHeight+68)}"); await pg.wait_for_timeout(250)
        m['sticky'] = await pg.evaluate("()=>{const s=document.querySelector('.melscore').getBoundingClientRect(),q=document.querySelector('.el-palwrap,.el-steps').getBoundingClientRect(),l=[...document.querySelectorAll('.melentry .earstep,.melentry .el-tile')].filter(e=>{const r=e.getBoundingClientRect();return r.top>=Math.max(s.bottom,document.querySelector('.el-palwrap')?q.bottom:0)-0.5&&r.bottom<=innerHeight-68});return {score_top:Math.round(s.top),score_bottom:Math.round(s.bottom),switch_or_palette_top:Math.round(q.top),switch_or_palette_bottom:Math.round(q.bottom),dock_top:(d=>d&&d.offsetParent!==null?Math.round(d.getBoundingClientRect().top):null)(document.querySelector('.el-dock')),switch_or_palette_fully_below_score:q.top>=s.bottom-0.5,rows_fully_visible:l.length,room_under_score:innerHeight-68-Math.round(s.bottom)}}")
        if name == 'a_step1':
            await pg.evaluate("()=>{const e=document.querySelector('.el-steps');window.scrollTo(0,e.getBoundingClientRect().top+scrollY-340)}"); await pg.wait_for_timeout(200)
            r = await pg.evaluate("()=>{const a=document.querySelector('.el-steps').getBoundingClientRect(),z=document.querySelector('.melentry').getBoundingClientRect();return {x:a.left-8,y:a.top-8,width:a.width+16,height:z.bottom-a.top+16}}")
            await pg.screenshot(path=str(P / 'a_step1_390.png'), clip=r)
        else:
            await pg.screenshot(path=str(HERE / f'{name}_390.png'))
    if name == 'b':
        r = await pg.evaluate("()=>{const a=document.querySelector('.el-pal').getBoundingClientRect();return {x:a.left-6,y:a.top-6,width:a.width+12,height:a.height+12}}")
        await pg.screenshot(path=str(P / f'b_palette_{w}.png'), clip=r)
    await pg.add_style_tag(content='.tabbar,header.top,.el-dock{display:none!important}.meldesk.r4 .melscore{position:static!important}')
    if name != 'a_step1':
        await card.screenshot(path=str(HERE / (f'{name}_390_card.png' if phone else f'{name}_1366.png')))
        if not phone:
            await (await pg.query_selector('.meldesk')).screenshot(path=str(P / f'{name}_1366_desk.png'))
        await pg.evaluate("document.querySelectorAll('style').forEach(s=>{if(s.textContent.startsWith('.tabbar,header.top,.el-dock'))s.remove()})")
        html = await pg.evaluate("""()=>{const d=document.cloneNode(true);d.querySelectorAll('script,link[rel=preconnect],link[rel=stylesheet],section.room[hidden],.msheet,dialog').forEach(e=>e.remove());return '<!doctype html>\\n'+d.documentElement.outerHTML}""")
        html = html.replace('<head>', '<head><!-- Static mock-up, Fable 0.49 entry A/B (option %s at %d px). Built by tests/reports/fable_049/entry_ab/build_entry_ab.py; not production code. --><style>%s</style>' % (name, w, FONTS), 1)
        html = html.replace('url(fonts/', 'url(../../../../fonts/').replace('url("fonts/', 'url("../../../../fonts/')
        (HERE / f'{name}_{w}.html').write_text(html, encoding='utf8')
    elif not phone:
        await pg.evaluate("()=>{const e=document.querySelector('.el-steps');window.scrollTo(0,e.getBoundingClientRect().top+scrollY-120)}"); await pg.wait_for_timeout(150)
        r = await pg.evaluate("()=>{const a=document.querySelector('.el-steps').getBoundingClientRect(),z=document.querySelector('.melentry').getBoundingClientRect();return {x:a.left-8,y:a.top-8,width:a.width+16,height:z.bottom-a.top+16}}")
        await pg.screenshot(path=str(P / 'a_step1_1366.png'), clip=r)
    await pg.close(); return m

async def sheet(b):
    pg = await b.new_page(viewport={'width': 1600, 'height': 1000}, device_scale_factor=1)
    await pg.goto((HERE / 'sheet_ab.html').as_uri()); await pg.wait_for_timeout(600)
    await pg.screenshot(path=str(HERE / 'sheet_ab.png'), full_page=True); await pg.close()

async def main():
    out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        if '--sheet' not in sys.argv:
            for name in SCENES:
                for w, h in [(1366, 768), (390, 844)]:
                    out[f'{name}_{w}'] = await shoot(b, name, SCENES[name], w, h)
            (HERE / 'parts' / 'metrics.json').write_text(json.dumps(out, indent=1))
            for k, v in out.items(): print(k, json.dumps({a: c for a, c in v.items() if c not in (None, [], 0)}))
        if (HERE / 'sheet_ab.html').exists(): await sheet(b)
        await b.close()
asyncio.run(main())
