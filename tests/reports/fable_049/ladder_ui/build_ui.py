"""Fable 0.49, ladder UI part 2: build the mock-ups from the live app (index.html is not edited).
Each scene loads the app, puts the Ear Lab in a real state, injects c5.css + fn049.css + ladder049.css + ladder_ui.css,
swaps in the new markup (../mock.js, ladder_ui.js, scenes.js), measures it, and writes PNG renders (png/) and a static,
script-free HTML copy (mocks/) at 1366x768 and 390x844. Measurements go to png/metrics.json.
Run from the repo root: python3 tests/reports/fable_049/ladder_ui/build_ui.py [scene ...]"""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent; F49 = HERE.parent; REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
CSS = ''.join((p).read_text() for p in [F49 / 'c5.css', F49 / 'fn049.css', F49 / 'ladder049.css', HERE / 'ladder_ui.css'])
JS = (F49 / 'mock.js').read_text() + (HERE / 'ladder_ui.js').read_text() + (HERE / 'scenes.js').read_text()
SIZES = [(1366, 768), (390, 844)]
UP = '../../../../../'
FONTS = "".join("@font-face{font-family:'%s';font-weight:%s;src:url(%sdesign/earlab_048/fonts/%s) format('woff2')}\n" % (a, b, UP, c) for a, b, c in [
    ('Outfit', 300, 'outfit-latin-300-normal.woff2'), ('Outfit', 400, 'outfit-latin-400-normal.woff2'), ('Outfit', 600, 'outfit-latin-600-normal.woff2'),
    ('Outfit', 700, 'outfit-latin-700-normal.woff2'), ('Poiret One', 400, 'poiret-one-latin-400-normal.woff2')])
MEL = "()=>{EAR.drill='mel';EAR.lvl.mel=2;EAR.q=earGen('mel',2,R);EAR.q.plays=1;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar()}"
RHY = "()=>{EAR.drill='rhy';EAR.lvl.rhy=3;EAR.q=earGen('rhy',3,R);EAR.q.plays=1;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar()}"
SCENES = {'pal_r6_24': MEL, 'pal_r6_68': MEL, 'res_r6': MEL, 'a2_r7': MEL, 'mut_r9': MEL, 'rhy_r9': RHY, 'pal7_r12': MEL, 'lad_chr': MEL}
ENTRY = {'pal_r6_24', 'pal_r6_68', 'mut_r9', 'pal7_r12'}
MEASURE = """()=>{const B=s=>{const e=document.querySelector(s);if(!e)return null;const r=e.getBoundingClientRect();return r.width?[Math.round(r.width),Math.round(r.height)]:null};
  const all=s=>[...new Set([...document.querySelectorAll(s)].filter(e=>e.getClientRects().length).map(e=>{const r=e.getBoundingClientRect();return Math.round(r.width)+'x'+Math.round(r.height)}))];
  const small=[];document.querySelectorAll('#earCard button, #earCard label.note, #earCard a').forEach(e=>{if(!e.getClientRects().length||e.closest('.el-foot'))return;const r=e.getBoundingClientRect();if(r.height<43.5||r.width<43.5)small.push((e.className||e.parentElement.className)+':'+e.textContent.trim().slice(0,10)+':'+Math.round(r.width)+'x'+Math.round(r.height))});
  const tiny=[];document.querySelectorAll('#earCard *').forEach(e=>{if(!e.getClientRects().length)return;if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()))return;let fs=parseFloat(getComputedStyle(e).fontSize);const sv=e.closest('svg');
    if(sv&&e.dataset&&e.dataset.px)fs=+e.dataset.px;else if(sv){const vb=sv.viewBox&&sv.viewBox.baseVal;if(vb&&vb.width)fs*=sv.getBoundingClientRect().width/vb.width;const k=+sv.dataset.k;if(k&&!(vb&&vb.width))fs*=k}
    if(fs<10.95)tiny.push((e.className.baseVal!==undefined?e.className.baseVal:e.className)+':'+e.textContent.trim().slice(0,12)+':'+fs.toFixed(1))});
  const clip=[];document.querySelectorAll('#earCard .earstep, #earCard .el-len, #earCard .el-tile, #earCard .el-mut, #earCard .el-seg button, #earCard .el-answer .pt').forEach(e=>{if(e.scrollWidth>e.clientWidth+1)clip.push((e.className)+':'+e.textContent.trim().slice(0,14)+':'+e.scrollWidth+'>'+e.clientWidth)});
  const card=document.querySelector('#earCard').getBoundingClientRect(),out=[];document.querySelectorAll('#earCard *').forEach(e=>{if(!e.getClientRects().length||e.closest('svg')&&e.tagName!=='svg')return;const r=e.getBoundingClientRect();if(r.width&&(r.right>card.right+.5||r.left<card.left-.5))out.push((e.className.baseVal!==undefined?e.className.baseVal:e.className)+':'+Math.round(r.left)+'-'+Math.round(r.right))});
  return {card:B('#earCard'),head:B('#earCard .el-head'),desk:B('.meldesk'),hold:B('.melhold'),score:B('.melscore'),svg:B('#earMel svg'),pal:B('.el-pal'),len:all('.el-len'),mut:B('.el-mut'),undo1:B('.el-undo1'),sysmap:all('.el-sysmap button'),
   lad:B('.melentry .earlad'),lads:all('.melentry .earlad'),row:all('.melentry .earlad>.earstep'),half:all('.earhalf .earstep'),res:B('.el-result'),answer:B('.el-answer'),gap:B('.el-gap'),markkey:B('.el-markkey'),seg:all('.grp.set .el-seg button'),set:B('.grp.set'),vars:B('.el-vars'),
   tiles:all('.el-tile'),tup:all('.el-tile.tup'),rsvg:all('.el-rhy svg').slice(0,8),tfams:B('.el-tfams'),
   over:document.documentElement.scrollWidth-innerWidth,small:[...new Set(small)],tiny:[...new Set(tiny)],clip:[...new Set(clip)],outside:[...new Set(out)].slice(0,8)}}"""
STICKY = """()=>{const h=document.querySelector('.melhold').getBoundingClientRect(),dock=document.querySelector('.el-dock.show'),floor=innerHeight-68,dk=dock?dock.getBoundingClientRect().top:floor,
  rows=[...document.querySelectorAll('.melentry .earlad>.earstep,.melentry .earhalf')].map(e=>e.getBoundingClientRect());
  return {hold_top:Math.round(h.top),hold_bottom:Math.round(h.bottom),hold_h:Math.round(h.height),room_above_tabs:Math.round(floor-h.bottom),rows_total:rows.length,rows_above_tabs:rows.filter(r=>r.top>=h.bottom-.5&&r.bottom<=floor+.5).length,rows_clear_of_play_bar:rows.filter(r=>r.top>=h.bottom-.5&&r.bottom<=dk+.5).length}}"""

async def shoot(b, name, w, h):
    pg = await b.new_page(viewport={'width': w, 'height': h}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    await pg.add_style_tag(content=CSS); await pg.add_script_tag(content=JS)
    await pg.evaluate("()=>{S.level=6;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===6));location.hash='ear';EAR.all=false;EAR.st={};room('ear');window.earPlay=()=>{};window.R=(s=>()=>(s=(s*16807)%2147483647)/2147483647)(11)}")
    await pg.evaluate(SCENES[name]); await pg.wait_for_timeout(900)
    phone = w < 761
    await pg.evaluate("([n,ph])=>SCN[n](ph)", [name, phone]); await pg.wait_for_timeout(300)
    m = await pg.evaluate(MEASURE); m['errors'] = errs
    card = await pg.query_selector('#earCard')
    await card.evaluate("e=>window.scrollTo(0,e.getBoundingClientRect().top+scrollY-(innerWidth<761?104:70))"); await pg.wait_for_timeout(150)
    await pg.screenshot(path=str(HERE / 'png' / f'{name}_{w}.png'))
    if phone and name in ENTRY:   # the entry as it is used: the score and palette held under the top bar, the ladder beneath
        await pg.evaluate("()=>{const e=document.querySelector('.melentry');window.scrollTo(0,e.getBoundingClientRect().top+scrollY-document.querySelector('.melhold').getBoundingClientRect().height-parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--top'))-10)}"); await pg.wait_for_timeout(250)
        m['sticky'] = await pg.evaluate(STICKY)
        await pg.screenshot(path=str(HERE / 'png' / f'{name}_{w}_entry.png'))
    if phone and name in ('res_r6', 'a2_r7'):
        await pg.evaluate("()=>{const e=document.querySelector('.melres');window.scrollTo(0,e.getBoundingClientRect().top+scrollY-110)}"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=str(HERE / 'png' / f'{name}_{w}_result.png'))
    if phone and name == 'rhy_r9':
        await pg.evaluate("()=>{const e=document.querySelector('.el-tfams');window.scrollTo(0,e.getBoundingClientRect().top+scrollY-430)}"); await pg.wait_for_timeout(200)
        await pg.screenshot(path=str(HERE / 'png' / f'{name}_{w}_entry.png'))
    await pg.add_style_tag(content='.tabbar,header.top,.el-dock{display:none!important}.melhold{position:static!important}')   # whole-card render: fixed bars out of the way
    await card.screenshot(path=str(HERE / 'png' / f'{name}_{w}_card.png'))
    await pg.evaluate("document.querySelectorAll('style').forEach(s=>{if(s.textContent.startsWith('.tabbar,header.top,.el-dock'))s.remove()})")
    html = await pg.evaluate("""()=>{const d=document.cloneNode(true);d.querySelectorAll('script,link[rel=preconnect],link[rel=stylesheet],section.room[hidden],.msheet,dialog').forEach(e=>e.remove());return '<!doctype html>\\n'+d.documentElement.outerHTML}""")
    html = html.replace('<head>', '<head><!-- Static mock-up, Fable 0.49 ladder UI (%s at %d px). Built by tests/reports/fable_049/ladder_ui/build_ui.py; not production code. --><style>%s</style>' % (name, w, FONTS), 1)
    html = html.replace('url(fonts/', 'url(%sfonts/' % UP).replace('url("fonts/', 'url("%sfonts/' % UP)
    (HERE / 'mocks' / f'{name}_{w}.html').write_text(html, encoding='utf8')
    await pg.close(); return m

async def main():
    want = sys.argv[1:] or list(SCENES); out = {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for name in want:
            for w, h in SIZES: out[f'{name}_{w}'] = await shoot(b, name, w, h)
        await b.close()
    mp = HERE / 'png' / 'metrics.json'; old = json.loads(mp.read_text()) if mp.exists() else {}; old.update(out); mp.write_text(json.dumps(old, indent=1))
    for k, v in out.items(): print(k, json.dumps({a: c for a, c in v.items() if c not in (None, [], 0)}))
asyncio.run(main())
