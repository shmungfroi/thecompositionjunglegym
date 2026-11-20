"""IC_REG_049 probe C7b: run the two-voice checker (c2Check) on mutated models of every mode, species 1-5, above and below, and
scan every message for leftover wording faults: 'Bars N–N', 'altered', 'N-fold', bare 15th, 'a augmented', undefined/NaN, and
S3d messages (species 3 and 5) for their wording."""
import asyncio, sys, pathlib, re, collections, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'harness'))
import cjg
from playwright.async_api import async_playwright
REPO = pathlib.Path(__file__).resolve().parents[4]
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(); await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#gym'); await pg.wait_for_timeout(1000)
        r = await pg.evaluate("""()=>{let s=777;const R=()=>{s=(s*48271)%2147483647;return s/2147483647};const msgs=[];let runs=0;
          for(const M of C2M)for(const sp of [1,2,3,4,5])for(const pos of ['above','below']){const m=c2Model(M,sp,pos);if(!m)continue;const rows=c2Rows(M,pos);
            for(let t=0;t<150;t++){const cp=m.cp.slice();const k=1+Math.floor(R()*3);for(let j=0;j<k;j++){const i=Math.floor(R()*cp.length);cp[i]=rows[Math.floor(R()*rows.length)]+(R()<.15?7:0)}
              let res;try{res=c2Check(M,sp,pos,cp,m.br)}catch(e){msgs.push({sp,pos,sev:'THROW',rule:'',msg:String(e)});continue}runs++;
              for(const x of res.iss)msgs.push({sp,pos,sev:x.sev,rule:x.rule,msg:x.msg})}}
          return{runs,msgs}}""")
        await b.close(); return r
R = asyncio.run(main())
M = R['msgs']; print('checker runs', R['runs'], 'messages', len(M), 'distinct', len({m['msg'] for m in M}))
pats = {'Bars N–N': r'Bars (\d+)–\1\b', 'altered': r'altered', 'N-fold': r'\d-fold', 'bare 15th': r'\b15th', 'a augmented/a octave': r'\ba (augmented|octave|11th|18th)', 'an non-vowel': r'\ban (major|minor|perfect|diminished|doubly|double|unison|\d)(?!1th|8th)',
        'undefined/NaN': r'undefined|NaN|null', 'thrown': r'Error'}
for k, pt in pats.items():
    hit = [m for m in M if re.search(pt, m['msg'])]
    print(f'{k:22s} {len(hit)}', hit[0]['msg'][:160] if hit else '')
s3d = collections.Counter((m['sp'], re.sub(r'Bars \d+–\d+: ', '', m['msg'])) for m in M if m['rule'] == 'qbeat')
for (sp, t), c in s3d.most_common(): print('S3d', sp, c, t[:150])
tri = [m['msg'] for m in M if 'through a tritone' in m['msg']]; print('M6 outline messages', len(tri), 'single-bar form', sum(1 for t in tri if t.startswith('Bar ')), [t[:60] for t in tri if t.startswith('Bar ')][:2])
dbl = [m['msg'] for m in M if 'double octave' in m['msg']][:3]; print('double octave examples', dbl)
json.dump({'runs': R['runs'], 'n': len(M), 's3d': [[a, b, c] for (a, b), c in s3d.items()]}, open('/tmp/icreg/c7msg.json', 'w'), indent=1)
