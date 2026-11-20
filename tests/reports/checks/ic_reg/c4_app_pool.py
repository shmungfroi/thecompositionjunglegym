"""IC_REG_049 probe C4b: the app's rung 1 V–vi pool and draws against the independent enumeration (c4_vvi_enum.py)."""
import asyncio, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'harness'))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cjg
from playwright.async_api import async_playwright
REPO = pathlib.Path(__file__).resolve().parents[4]
src = open(pathlib.Path(__file__).resolve().parent / 'c4_vvi_enum.py').read().split('for name, var in')[0]; E = {}; exec(src, E)
mine = set()
for k in range(12):
    LN = (k + 11) % 12; V = [(k + 7) % 12, LN, (k + 2) % 12]; vi = [(k + 9) % 12, k, (k + 4) % 12]
    for P in [v for v in E['voicings'](V, V[0]) if [m % 12 for m in v].count(LN) == 1]:
        for N in [v for v in E['voicings'](vi, vi[0]) if [m % 12 for m in v].count(k) == 2]:
            if E['pair_ok'](P, N, LN, {}): mine.add((k, P, N))
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(); await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""()=>{let s=4242;const R=()=>{s=(s*48271)%2147483647;return s/2147483647};const g=[];
          for(let i=0;i<40000;i++){const q=earGen('cad',1,R);if(q.a==='interrupted')g.push(q.key.k+'|'+q.ch.map(v=>v.join(',')).join('|'))}
          return{pool:earR1Pool().filter(p=>p.t==='V vi').map(p=>[p.k,p.ch]),gen:g}}""")
        await b.close(); return r
R = asyncio.run(main())
app = {(k, tuple(c[0]), tuple(c[1])) for k, c in R['pool']}
drawn = collections.Counter(R['gen'])
print('app pool', len(app), 'mine', len(mine), 'equal', app == mine)
print('interrupted items drawn', len(R['gen']), 'distinct voicings drawn', len(drawn), 'min/max per voicing', min(drawn.values()), max(drawn.values()))
