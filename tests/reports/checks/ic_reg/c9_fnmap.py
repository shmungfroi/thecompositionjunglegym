"""IC_REG_049 probe C9: the Ear Lab function map (earNumFn) against Analysis (analyse().f) for every numeral in 12 major and
12 minor keys, and the colours each uses. Analysis 'C' (chromatic) corresponds to Ear Lab 'X' (outside the key)."""
import asyncio, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'harness'))
import cjg
from playwright.async_api import async_playwright
REPO = pathlib.Path(__file__).resolve().parents[4]
MAJ = ['I', 'ii', 'iii', 'IV', 'V', 'V7', 'vi', 'vii°', 'vii°7', 'v', 'v7', 'bVII', 'bVII7', 'iv', 'bVI', 'bIII', 'ii°', 'II', 'III', 'i', 'VII']
MIN = ['i', 'ii°', 'iiø7', 'III', 'iv', 'v', 'v7', 'V', 'V7', 'VI', 'VII', 'VII7', 'vii°', 'vii°7', 'bVII', 'ii', 'IV', 'I']
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(); await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""([MAJ,MIN])=>{const o=[];for(const [mode,L] of [['maj',MAJ],['min',MIN]])for(let k=0;k<12;k++){const key={k,mode};
            for(const rn of L){const ch=cadList(rn,key)[0];if(!ch||!ch.root){o.push({mode,k,rn,an:null});continue}
              const an=withKey(key,()=>analyse(ch,key));o.push({mode,k,rn,an:an.f,num:an.num,ear:earNumFn(rn.replace(/^b/,'♭'),mode)})}}
            return{o,MD_MAJOR,ELFN,FN,usedSites:[...document.documentElement.outerHTML.matchAll(/earNumFn\\(([^)]*)\\)/g)].map(m=>m[1])}}""", [MAJ, MIN])
        await b.close(); return r
R = asyncio.run(main())
print('MD_MAJOR', R['MD_MAJOR']); print('ELFN', R['ELFN']); print('FN', R['FN'])
agg = {}
for x in R['o']:
    k = (x['mode'], x['rn']); agg.setdefault(k, set()).add((x['an'], x['ear'], x.get('num')))
mism = []
for (mode, rn), s in agg.items():
    fs = {(a, e) for a, e, n in s}
    ok = all((a == e) or (a == 'C' and e == 'X') for a, e in fs)
    print(f'{mode:3s} {rn:6s} analysis/ear {sorted(fs)} {"" if ok else "  <-- differs"}')
    if not ok: mism.append((mode, rn, sorted(fs)))
print('calls of earNumFn without the mode:', [c for c in R['usedSites'] if ',' not in c])
json.dump({'mism': mism, 'agg': {f'{a}|{b}': sorted(map(list, s)) for (a, b), s in agg.items()}}, open('/tmp/icreg/c9.json', 'w'), indent=1, default=str)
