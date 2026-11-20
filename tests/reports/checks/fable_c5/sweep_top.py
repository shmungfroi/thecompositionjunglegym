"""Top bar swept 761..1300 px: as built, and with the proposed amendment (c5_6a.css) injected. index.html is not edited."""
import sys, asyncio, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent; REPO = HERE.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright
FIX = (HERE / 'c5_6a.css').read_text()
P = """()=>{const h=document.querySelector('header.top'),l=h.querySelector('.lvl'),lr=l.getBoundingClientRect(),on=l.querySelector('.on').getBoundingClientRect(),s=h.querySelector('.search').getBoundingClientRect(),j=h.querySelector('.jbtn').getBoundingClientRect(),t=h.querySelector('.t').getBoundingClientRect(),q=document.getElementById('q'),cs=getComputedStyle(q);
 const c=document.createElement('canvas').getContext('2d');c.font=cs.fontWeight+' '+cs.fontSize+' '+cs.fontFamily;const pw=c.measureText(q.placeholder).width,inner=q.clientWidth-parseFloat(cs.paddingLeft)-parseFloat(cs.paddingRight);
 return {lvl:[Math.round(lr.width),Math.round(lr.height)],lvlClip:on.right>lr.right+0.5||l.scrollWidth>l.clientWidth+1,search:Math.round(s.width),ph:pw<=inner+0.5,spill:Math.round(j.right-innerWidth),t:Math.round(t.width),over:document.documentElement.scrollWidth-innerWidth}}"""
async def run(b, fix, shots=()):
    R = {}
    pg = await b.new_page(viewport={'width': 1300, 'height': 768})
    await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(900)
    await pg.evaluate("()=>{S.level=6;location.hash='analysis';room('analysis')}"); await pg.wait_for_timeout(300)
    if fix: await pg.add_style_tag(content=FIX)
    for w in range(761, 1301):
        await pg.set_viewport_size({'width': w, 'height': 768}); await pg.wait_for_timeout(15)
        R[w] = await pg.evaluate(P)
        if w in shots: await pg.screenshot(path=str(HERE / f'c56_final_top_{w}.png'), clip={'x': 0, 'y': 0, 'width': w, 'height': 64})
    await pg.close(); return R
def bands(R, f):
    out = []; start = None
    for w in sorted(R):
        if f(R[w]):
            if start is None: start = w
            last = w
        elif start is not None: out.append((start, last)); start = None
    if start is not None: out.append((start, last))
    return out
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); res = {}
        # round 2: C5-6a is in index.html (4c42ff0), so only the build is swept; nothing is injected
        for fix in (False,):
            R = await run(b, fix, shots=(761, 777, 800, 811, 860, 861, 901, 938, 950, 973, 1023, 1024, 1180, 1181, 1280, 1281))
            k = 'built'
            res[k] = {'stage_switch_wrapped': bands(R, lambda m: m['lvl'][1] > 40), 'selected_stage_clipped': bands(R, lambda m: m['lvlClip']), 'placeholder_cut': bands(R, lambda m: not m['ph']),
                      'search_under_220': bands(R, lambda m: m['search'] < 220), 'bar_spills': bands(R, lambda m: m['spill'] > 0), 'min_search': min(m['search'] for m in R.values()),
                      'samples': {w: R[w] for w in (761, 777, 800, 811, 860, 861, 900, 901, 938, 950, 973, 1023, 1024, 1180, 1181, 1280, 1281)}}
        await b.close()
    (HERE / 'sweep_top.json').write_text(json.dumps(res, indent=1)); print(json.dumps({k: {x: v[x] for x in v if x != 'samples'} for k, v in res.items()}, indent=1))
    for k in res: print(k, json.dumps(res[k]['samples']))
asyncio.run(main())
