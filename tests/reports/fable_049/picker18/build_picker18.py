"""Fable, 18-rung picker preview for 0.50 (decision log L103). index.html is not edited.
Builds option A (one row, all rungs) and option B (Stage menus) inside the live app at the same moment:
melodic dictation, 18 rungs, Stage switch on 6, on rung 14, seven rungs reached, rung 15 suggested.
Writes {a,b}_{1366,390}.html (static; one small inline script so they can be clicked), PNG renders, parts/ for the sheet,
parts/metrics.json (sizes at 1440, 1366, 1024, 390 and the keyboard run for B) and sheet_picker18.png.
Run from the repo root: python3 tests/reports/fable_049/picker18/build_picker18.py [--sheet]"""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent; F49 = HERE.parent; REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
CSS = (F49 / 'c5.css').read_text() + (F49 / 'ladder049.css').read_text() + (HERE / 'picker18.css').read_text()
JS = (F49 / 'mock.js').read_text() + (HERE / 'picker18.js').read_text(); BEH = (HERE / 'picker18_behaviour.js').read_text()
FONTS = "".join("@font-face{font-family:'%s';font-weight:%s;src:url(../../../../design/earlab_048/fonts/%s) format('woff2')}\n" % t for t in [
    ('Outfit', 300, 'outfit-latin-300-normal.woff2'), ('Outfit', 400, 'outfit-latin-400-normal.woff2'), ('Outfit', 600, 'outfit-latin-600-normal.woff2'),
    ('Outfit', 700, 'outfit-latin-700-normal.woff2'), ('Poiret One', 400, 'poiret-one-latin-400-normal.woff2')])
ST = {'n': 23, 'ok': 17, 'streak': 3, 'best': 6, 'shown': 1, 'skipped': 0}
PRE = "()=>{EAR.drill='mel';EAR.lvl.mel=3;EAR.q=earGen('mel',3,R);EAR.q.plays=1;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar()}"
O = "{cur:14,done:[7,8,9,10,12,13,14],sug:15,last:[1,1,0,1,1,1,1,0,1,1]%s}"
SCENES = {'a': ('a', ''), 'a_open5': ('a', ',open:5'), 'b': ('b', ''), 'b_open': ('b', ',open:6')}
MEASURE = """()=>{const B=s=>{const e=document.querySelector(s);if(!e||!e.offsetParent)return null;const r=e.getBoundingClientRect();return [Math.round(r.width*10)/10,Math.round(r.height*10)/10]};
  const all=s=>[...new Set([...document.querySelectorAll(s)].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return Math.round(r.width*10)/10+'x'+Math.round(r.height*10)/10}))];
  const small=[];document.querySelectorAll('#earCard .el-head button').forEach(e=>{if(!e.offsetParent)return;const r=e.getBoundingClientRect();if(r.height<43.5||r.width<43.5)small.push(e.className+':'+e.textContent.trim().slice(0,10)+':'+Math.round(r.width)+'x'+Math.round(r.height))});
  const tiny=[];document.querySelectorAll('#earCard .el-head *').forEach(e=>{if(!e.offsetParent||e.closest('svg'))return;if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;const fs=parseFloat(getComputedStyle(e).fontSize);if(fs<10.95)tiny.push(e.className+':'+fs)});
  const hd=document.querySelector('#earCard .el-head'),cs=getComputedStyle(document.getElementById('earCard')),m=document.querySelector('.el-smm:not([hidden])');
  return {card_inner:Math.round(hd.getBoundingClientRect().width),head:B('#earCard .el-head'),picker:B('.el-rp.r18,.el-sm'),rungline:B('.el-rungline'),rung_btn:all('.el-band button'),tab:all('.el-bandtab'),stage_btn:all('.el-smb'),menu:B('.el-smm:not([hidden])'),menu_item:all('.el-smm:not([hidden]) .el-smi'),
   menu_bottom:m?Math.round(m.getBoundingClientRect().bottom):null,viewport:[innerWidth,innerHeight],over:document.documentElement.scrollWidth-innerWidth,under_44:[...new Set(small)],tiny:[...new Set(tiny)]}}"""
KEYS = """async()=>{const log=[],A=()=>{const a=document.activeElement;return a.classList.contains('el-smb')?'button '+a.querySelector('.st').textContent:a.classList.contains('el-smi')?'rung '+a.dataset.earlv:a.tagName},open=()=>[...document.querySelectorAll('.el-smb[aria-expanded=true]')].map(b=>b.querySelector('.st').textContent).join()||'none';
  const k=(key,el)=>{(el||document.activeElement).dispatchEvent(new KeyboardEvent('keydown',{key,bubbles:true,cancelable:true}));log.push(key.replace(' ','Space')+' → focus '+A()+', open: '+open())};
  const b=[...document.querySelectorAll('.el-smb')];b[2].focus();log.push('focus Stage 6 button');
  k('ArrowDown');k('ArrowDown');k('ArrowUp');k('ArrowUp');k('ArrowUp');k('End');k('Home');k('8');k('ArrowLeft');k('ArrowDown');k('Escape');k('Enter');k('ArrowDown');k(' ');
  log.push('after Space: Stage 5 button reads "'+b[1].querySelector('.v').textContent+'", Stage 6 reads "'+b[2].querySelector('.v').textContent+'", checked: '+[...document.querySelectorAll('.el-smi[aria-checked=true]')].map(x=>x.dataset.earlv).join());
  k('ArrowUp');k('Tab');
  const roles={button:[b[0].getAttribute('aria-haspopup'),b[0].hasAttribute('aria-controls'),b[0].getAttribute('aria-label')],menu:document.getElementById('p18m6').getAttribute('role'),item:[...new Set([...document.querySelectorAll('.el-smi')].map(x=>x.getAttribute('role')))],item_label:document.querySelector('.el-smi[data-earlv="15"]').getAttribute('aria-label')};
  return {log,roles}}"""

async def page(b, kind, extra, w, h, dsf=2):
    pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=dsf); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    await pg.add_style_tag(content=CSS); await pg.add_script_tag(content=JS)
    await pg.evaluate("()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='ear';EAR.all=false;EAR.st={};room('ear');window.earPlay=()=>{};window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11)}")
    await pg.evaluate(PRE); await pg.wait_for_timeout(900)
    await pg.evaluate("(a)=>{MK.tally(a[0]);P18.head(a[1],eval('('+a[2]+')'))}", [ST, kind, O % extra]); await pg.wait_for_timeout(250)
    card = await pg.query_selector('#earCard'); await card.evaluate("e=>window.scrollTo(0,e.getBoundingClientRect().top+scrollY-(innerWidth<761?104:70))"); await pg.wait_for_timeout(150)
    return pg, errs

async def shoot(b, name, w, h):
    kind, extra = SCENES[name]; pg, errs = await page(b, kind, extra, w, h); m = await pg.evaluate(MEASURE); m['errors'] = errs; P = HERE / 'parts'; phone = w < 761
    if w in (1366, 390):
        await pg.screenshot(path=str(P / f'{name}_{w}_screen.png') if name == 'a_open5' else str(HERE / f'{name}_{w}.png'))
        r = await pg.evaluate("(hh)=>{const c=document.getElementById('earCard').getBoundingClientRect();return innerWidth<761?{x:0,y:0,width:innerWidth,height:hh}:{x:c.left-14,y:c.top-14,width:c.width+28,height:hh}}", 640 if phone else (470 if name == 'b_open' else 300))
        await pg.screenshot(path=str(P / f'{name}_{w}.png'), clip=r)
        if name == 'a' and not phone:
            r = await pg.evaluate("()=>{const a=document.querySelector('.el-rp').getBoundingClientRect(),c=document.querySelectorAll('.el-band')[2].getBoundingClientRect();return {x:c.left-90,y:a.top-10,width:c.width+100,height:a.height+20}}")
            await pg.screenshot(path=str(P / 'a_close_1366.png'), clip=r)
        if name == 'b' and not phone:
            r = await pg.evaluate("()=>{const a=document.querySelector('.el-sm').getBoundingClientRect(),c=document.querySelectorAll('.el-smb')[2].getBoundingClientRect();return {x:c.left-90,y:a.top-10,width:c.width+100,height:a.height+20}}")
            await pg.screenshot(path=str(P / 'b_close_1366.png'), clip=r)
        if name in ('a', 'b'):
            html = await pg.evaluate("""()=>{const d=document.cloneNode(true);d.querySelectorAll('script,link[rel=preconnect],link[rel=stylesheet],section.room[hidden],.msheet,dialog').forEach(e=>e.remove());return '<!doctype html>\\n'+d.documentElement.outerHTML}""")
            html = html.replace('<head>', '<head><!-- Static mock-up, Fable, 18-rung picker option %s at %d px (0.50 preview). Built by tests/reports/fable_049/picker18/build_picker18.py; not production code. The one script at the foot is picker18_behaviour.js, so the picker can be clicked. --><style>%s</style>' % (name.upper(), w, FONTS), 1)
            html = html.replace('url(fonts/', 'url(../../../../fonts/').replace('url("fonts/', 'url("../../../../fonts/').replace('</body>', '<script>' + BEH + '</script></body>')
            (HERE / f'{name}_{w}.html').write_text(html, encoding='utf8')
    if name == 'b' and w == 1366:
        await pg.add_script_tag(content=BEH); m['keyboard'] = await pg.evaluate(KEYS)
    await pg.close(); return m

async def sheet(b):
    pg = await b.new_page(viewport={'width': 1600, 'height': 1000}, device_scale_factor=1)
    await pg.goto((HERE / 'sheet_picker18.html').as_uri()); await pg.wait_for_timeout(600)
    await pg.screenshot(path=str(HERE / 'sheet_picker18.png'), full_page=True); await pg.close()

async def main():
    out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        if '--sheet' not in sys.argv:
            for name in SCENES:
                for w, h in [(1440, 900), (1366, 768), (1024, 768), (390, 844)]:
                    out[f'{name}_{w}'] = await shoot(b, name, w, h)
            (HERE / 'parts' / 'metrics.json').write_text(json.dumps(out, indent=1))
            for k, v in out.items(): print(k, json.dumps({a: c for a, c in v.items() if c not in (None, [], 0) and a != 'keyboard'}))
            print(json.dumps(out['b_1366']['keyboard'], indent=1))
        if (HERE / 'sheet_picker18.html').exists(): await sheet(b)
        await b.close()
asyncio.run(main())
