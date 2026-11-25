"""Ordering test (0.50 V3). Run: python3 tests/ordering_test.py <repo dir>

At every level 1-7, for every banded list in the app (chord types, scales, intervals, voicing types, cadences, the climb
example pickers, Forms, Climbs, Analysis scores), open the list and check against the source data:
  - the "New at your level" band holds exactly the items with l == level;
  - "Earlier levels" holds exactly the items with l < level, in ascending l (then ascending stp);
  - "Ahead of you" holds exactly the items with l > level, in ascending l (then ascending stp);
  - no item is missing or duplicated.
Also checks: Earlier open and Ahead folded by default, an empty New band shows the .lvnone line, fold state is remembered
(cjg_fold_<id>) across a re-render, a chord searched above the level opens the Ahead band, selects the row and does not
change the level, and the selected item is never inside a closed band.
"""
import sys, asyncio, json, pathlib
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

# (list element id, JS that opens the page showing it, JS giving the source items [{id,l,stp}])
LISTS = [
    ('qualList', "location.hash='seed';room('seed')", "qualItems().map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('ksList', "KS.tab='scales';location.hash='keys';room('keys');renderKeysRoom()", "SCALES.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('ivList', "KS.tab='intervals';location.hash='keys';room('keys');renderKeysRoom()", "IVS.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('vlList', "location.hash='voice';room('voice')", "Object.entries(VTYPES).map(([k,v])=>({id:k,l:v.l||1,stp:v.stp||0}))"),
    ('c3List', "location.hash='climbs/3'", "CADS.filter(c=>c[CL.key.mode]).map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c4List', "location.hash='climbs/4'", "C4EX.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c5List', "location.hash='climbs/5'", "C5FAM.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c6List', "location.hash='climbs/6'", "C6EX.filter(x=>x[C6.key.mode]).map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c7List', "location.hash='climbs/7'", "C7EX.filter(x=>x[C7.key.mode]).map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c8List', "location.hash='climbs/8'", "C8EX.filter(x=>x[C8.key.mode]).map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c9List', "location.hash='climbs/9'", "C9EX.filter(x=>x[C9.key.mode]).map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c10List', "location.hash='climbs/10'", "C10EX.filter(x=>x[C10.key.mode]).map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c11List', "location.hash='climbs/11'", "C11V.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c12mList', "location.hash='climbs/12';C12.tab='vamp';renderClimb12()", "C12MODES.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c12sList', "location.hash='climbs/12';C12.tab='plane';renderClimb12()", "C12SHAPES.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c1List', "location.hash='climbs/1'", "C1M.map(x=>({id:x.k,l:x.l||1,stp:x.stp||0}))"),
    ('c2mList', "location.hash='climbs/2'", "C2M.concat(C2OWN?[C2OWN]:[]).map(x=>({id:String(x.k),l:x.l||1,stp:x.stp||0}))"),
    ('c2sList', "location.hash='climbs/2'", "C2SP.map(x=>({id:String(x.k),l:x.l||1,stp:x.stp||0}))"),
    ('formsList', "location.hash='forms'", "FORMS.map(x=>({id:x.live?x.k:x.t,l:x.l||1,stp:x.stp||0}))"),
    ('climbsGal', "location.hash='climbs'", "CLIMBS.map((c,i)=>({id:String(i),l:clInfo(i).l,stp:i}))"),
    ('anList', "AN.tab='score';location.hash='analysis';room('analysis')", "Object.entries(ANLV).map(([k,v])=>({id:k,l:v[0],stp:v[1]}))"),
]

# read a rendered list: the id and level of every item in each band, in DOM order
READ = """(id)=>{const root=document.getElementById(id);if(!root)return null;
 const ATTRS=['pq','ksc','kiv','vt','clex','c4ex','c5fam','c6ex','c7ex','c8ex','c9ex','c10ex','c11v','c12m','c12s','c1m','c2m','c2s','fopen','clopen','ansc'];
 const idOf=b=>{for(const a of ATTRS)if(b.dataset[a]!==undefined)return b.dataset[a];const t=b.querySelector('b,h4');return t?t.textContent:null};
 const items=el=>[...el.querySelectorAll('[data-pq],[data-ksc],[data-kiv],[data-vt],[data-clex],[data-c4ex],[data-c5fam],[data-c6ex],[data-c7ex],[data-c8ex],[data-c9ex],[data-c10ex],[data-c11v],[data-c12m],[data-c12s],[data-c1m],[data-c2m],[data-c2s],[data-fopen],[data-clopen],[data-ansc],.climb.dim')].filter(b=>!b.closest('summary'));
 const lvOf=b=>{const g=b.closest('.lvgrp');if(g)return +g.getAttribute('aria-label').match(/Level (\\d)/)[1];const m=b.querySelector('.lvm');if(m)return +m.textContent;return null};
 const out={};
 for(const k of ['new','met','ahead']){const band=root.querySelector('.lvband.'+k);if(!band){out[k]=null;continue}
  out[k]={open:band.tagName==='SECTION'?true:band.open,items:items(band).map(b=>({id:idOf(b),l:k==='new'?S.level:lvOf(b)})),none:!!band.querySelector('.lvnone')}}
 return out}"""


def check(level, lid, src, got, fails):
    def bad(m):
        fails.append(f'L{level} {lid}: {m}')
    if got is None:
        return bad('list not found in the page')
    exp_new = [x for x in src if x['l'] == level]
    exp_met = sorted([x for x in src if x['l'] < level], key=lambda x: (x['l'], x['stp']))
    exp_ah = sorted([x for x in src if x['l'] > level], key=lambda x: (x['l'], x['stp']))
    seen = []
    for key, exp in (('new', exp_new), ('met', exp_met), ('ahead', exp_ah)):
        band = got.get(key)
        ids = [i['id'] for i in band['items']] if band else []
        if not exp:
            if band and band['items']:
                bad(f'{key} band should be empty, has {ids}')
            if key == 'new' and band and not band['none']:
                bad('empty New band lacks the .lvnone line')
            continue
        if not band:
            bad(f'{key} band missing, expected {len(exp)} items')
            continue
        if set(ids) != {x['id'] for x in exp}:
            bad(f'{key} band holds {sorted(ids)}, expected {sorted(x["id"] for x in exp)}')
        lv = [i['l'] for i in band['items']]
        if key != 'new' and lv != sorted(lv):
            bad(f'{key} band is not in ascending level order: {lv}')
        if key != 'new':
            want = [x['id'] for x in exp]
            if ids != want:
                bad(f'{key} band order {ids}, expected {want}')
        for i in band['items']:
            if key == 'new' and i['l'] not in (level,):
                bad(f'new band item {i["id"]} marked level {i["l"]}')
            if key == 'met' and not i['l'] < level:
                bad(f'earlier band item {i["id"]} marked level {i["l"]}')
            if key == 'ahead' and not i['l'] > level:
                bad(f'ahead band item {i["id"]} marked level {i["l"]}')
        seen += ids
    if len(seen) != len(set(seen)):
        bad('an item appears twice')
    if len(seen) != len(src):
        bad(f'{len(seen)} items shown, {len(src)} in the data')


async def main():
    fails, checks, skipped = [], 0, []
    async with async_playwright() as p:
        b = await cjg.launch(p)
        ctx = await b.new_context(viewport={'width': 1366, 'height': 900})
        await ctx.route('**/*', cjg.make_route(REPO))
        pg = await ctx.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://app/index.html')
        await pg.wait_for_timeout(900)
        read = READ
        for level in range(1, 8):
            await pg.evaluate(f"lvlSet({level})")
            for lid, opener, srcjs in LISTS:
                await pg.evaluate(opener)
                await pg.wait_for_timeout(120)
                if lid in ('c2mList', 'c2sList'):
                    present = await pg.evaluate(f"!!document.getElementById('{lid}')")
                    if not present:
                        # the chips live on the workshop tabs; open the first tab that has them
                        for tab in ['cp', 'cantus', 'workshop', 'species']:
                            await pg.evaluate(f"if(typeof C2!=='undefined')C2.tab='{tab}';renderClimb2()")
                            if await pg.evaluate(f"!!document.getElementById('{lid}')"):
                                break
                src = await pg.evaluate(srcjs)
                got = await pg.evaluate(f"({read})('{lid}')")
                if got is None and lid in ('c2mList', 'c2sList'):
                    skipped.append(f'L{level} {lid}')
                    continue  # list not on the default tab of climb 2
                check(level, lid, src, got, fails)
                checks += 1
        # --- behaviour checks ---
        await pg.evaluate("lvlSet(1);S.q='';localStorage.removeItem('cjg_fold_qualList');location.hash='seed';room('seed');render()")
        beh = await pg.evaluate("""(()=>{const d=document.querySelector('#qualList details.lvband.ahead'),m=document.querySelector('#qualList details.lvband.met');
          return {ahead_closed:!d.open,met_open:m?m.open:null}})()""")
        if beh['ahead_closed'] is not True:
            fails.append('Ahead band is not folded by default')
        if beh['met_open'] is not None and beh['met_open'] is not True:
            fails.append('Earlier band is not open by default')
        # search above the level
        await pg.evaluate("document.getElementById('q').value='Bm7b5';document.getElementById('searchForm').requestSubmit()")
        await pg.wait_for_timeout(300)
        r = await pg.evaluate("""(()=>{const on=document.querySelector('#qualList .lvrow.on'),d=on&&on.closest('details');return {level:S.level,q:S.q,inAhead:!!(d&&d.classList.contains('ahead')),open:!!(d&&d.open),saved:localStorage.getItem('cjg_fold_qualList')}})()""")
        if r['level'] != 1:
            fails.append(f'searching a chord above the level changed the level to {r["level"]}')
        if not (r['inAhead'] and r['open']):
            fails.append(f'searched chord (above the level) not shown in an open Ahead band: {r}')
        if r['saved'] and '"ahead":1' in r['saved']:
            fails.append('forced-open Ahead band was saved as the learner\'s choice')
        # fold memory: close Earlier, re-render, still closed
        await pg.evaluate("lvlSet(3);localStorage.removeItem('cjg_fold_qualList');render()")
        await pg.evaluate("document.querySelector('#qualList details.lvband.met').open=false")
        await pg.wait_for_timeout(200)
        await pg.evaluate("render()")
        r2 = await pg.evaluate("[document.querySelector('#qualList details.lvband.met').open,localStorage.getItem('cjg_fold_qualList')]")
        if r2[0] is not False or '"met":0' not in (r2[1] or ''):
            fails.append(f'fold state not remembered: {r2}')
        await b.close()
    print(json.dumps({'checks': checks, 'skipped': skipped, 'failures': fails, 'page_errors': errs}, indent=1))
    sys.exit(1 if fails or errs else 0)

asyncio.run(main())
