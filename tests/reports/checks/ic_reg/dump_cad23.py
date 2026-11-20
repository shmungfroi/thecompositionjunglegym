"""IC_REG_049 probe: dump the rung 2/3 cadence pools (every weighted entry and its realisation) and a large seeded
sample of generated items, straight from the app. Output: /tmp/icreg/cad23.json"""
import asyncio, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'harness'))
import cjg
from playwright.async_api import async_playwright
REPO = pathlib.Path(__file__).resolve().parents[4]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 12000

async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(); await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1500)
        out = {}
        for l in (2, 3):
            out[f'pool{l}'] = await pg.evaluate("""(l)=>earR23Entries(l).filter(e=>e.w>0).map(e=>{const P=earCadM(l,e.t.split(' '),{k:e.k,mode:e.md},{b:e.b,s:e.s});return{md:e.md,a:e.a,t:e.t,k:e.k,b:e.b,s:e.s,w:e.w,ch:P.ch}})""", l)
            out[f'nzero{l}'] = await pg.evaluate("(l)=>earR23Entries(l).filter(e=>e.w===0).length", l)
            out[f'nidx{l}'] = await pg.evaluate("(l)=>earR23Index(l).length", l)
            out[f'keys{l}'] = await pg.evaluate("(l)=>({maj:earCadKeys(l,'maj'),min:earCadKeys(l,'min')})", l)
            out[f'gen{l}'] = await pg.evaluate("""([l,N,seed])=>{let s=seed;const R=()=>{s=(s*48271)%2147483647;return s/2147483647};const o=[];
              for(let i=0;i<N;i++){const q=earGen('cad',l,R);o.push({a:q.a,md:q.key.mode,k:q.key.k,t:q.rns.join(' '),ch:q.ch})}return o}""", [l, N, 90417 + l])
        out['cadt'] = await pg.evaluate("({2:CADT[2],3:CADT[3]})")
        out['tableOK'] = await pg.evaluate("({2:!!earR23Weights(2),3:!!earR23Weights(3)})")
        await b.close()
    pathlib.Path('/tmp/icreg').mkdir(exist_ok=True)
    json.dump(out, open('/tmp/icreg/cad23.json', 'w'))
    print({k: (len(v) if isinstance(v, list) else v) for k, v in out.items() if k != 'cadt'})
asyncio.run(main())
