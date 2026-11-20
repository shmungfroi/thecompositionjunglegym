"""IC_REG_049 probe C3b: same seeded sample and held-out tell measure on a given app copy (used for the pre-fix baseline,
index.html at 6fc4392, served from a scratch folder). Usage: baseline_cad23.py <app_dir> <N>"""
import asyncio, json, sys, pathlib, collections, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'harness'))
import cjg
from playwright.async_api import async_playwright
APP, N = sys.argv[1], int(sys.argv[2])
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(); await pg.route('**/*', cjg.make_route(APP))
        await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1500)
        G = {}
        for l in (2, 3):
            G[l] = await pg.evaluate("""([l,N,seed])=>{let s=seed;const R=()=>{s=(s*48271)%2147483647;return s/2147483647};const o=[];
              for(let i=0;i<N;i++){const q=earGen('cad',l,R);o.push({a:q.a,md:q.key.mode,k:q.key.k,ch:q.ch})}return o}""", [l, N, 90417 + l])
        await b.close()
    return G
G = asyncio.run(main())
F = {'lo': lambda c: min(m for v in c for m in v), 'hi': lambda c: max(m for v in c for m in v),
     'lo,hi': lambda c: (min(m for v in c for m in v), max(m for v in c for m in v)), 'lastB': lambda c: c[-1][0], 'lastS': lambda c: c[-1][3], 'firstB': lambda c: c[0][0]}
for l in (2, 3):
    S = G[l]; random.Random(5).shuffle(S); A, B = S[:len(S)//2], S[len(S)//2:]
    out = {}
    for n, f in F.items():
        T = collections.defaultdict(collections.Counter); Mo = collections.defaultdict(collections.Counter)
        for q in A: T[(q['md'], f(q['ch']))][q['a']] += 1; Mo[q['md']][q['a']] += 1
        hit = sum((T.get((q['md'], f(q['ch']))) or Mo[q['md']]).most_common(1)[0][0] == q['a'] for q in B)
        base = sum(Mo[q['md']].most_common(1)[0][0] == q['a'] for q in B)
        out[n] = round(100 * (hit - base) / len(B), 2)
    print(f'rung {l} held-out gain (pts, mode+feature vs mode):', out, 'keys', {md: len({q["k"] for q in S if q["md"] == md}) for md in ('maj', 'min')})
