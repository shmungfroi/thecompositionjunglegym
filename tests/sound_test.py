"""Sound test (charter regression suite 9).
Run: python3 tests/sound_test.py <repo dir>

1. Every sample set the app declares (SMP: piano, guitar-steel, guitar-nylon, bass) loads: every note file listed exists
   and decodes.
2. Pitch: each decoded sample's fundamental (autocorrelation over 0.15-0.65 s of the note, in the browser) is within
   35 cents of the MIDI note its file name claims, octave errors included as failures.
3. Synth fallback: with the sample files blocked, tone() still sounds (oscillator nodes start) and nothing throws.
"""
import sys, asyncio, json, pathlib, math
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

PITCH = """async()=>{const out={};const A=new OfflineAudioContext(1,44100,44100);
 for(const k of Object.keys(SMP)){const S=SMP[k];out[k]=[];
  for(const n of smpNotes(k)){let r={n,ok:false};try{const buf=await fetch(S.dir+n+'.mp3').then(x=>{if(!x.ok)throw new Error('HTTP '+x.status);return x.arrayBuffer()}).then(b=>A.decodeAudioData(b));
    const d=buf.getChannelData(0),sr=buf.sampleRate,s0=Math.floor(.15*sr),N=Math.min(Math.floor(.5*sr),d.length-s0-1);
    const f0=440*Math.pow(2,(n-69)/12);let best=0,bl=0;const lo=Math.floor(sr/(f0*1.35)),hi=Math.ceil(sr/(f0/1.35));
    // normalised autocorrelation around the expected period only would hide octave errors, so search a wide band and
    // take the strongest peak, then refine it
    const LO=Math.max(8,Math.floor(sr/(f0*2.2))),HI=Math.min(N-1,Math.ceil(sr/(f0/2.2)));
    for(let L=LO;L<=HI;L++){let a=0,e1=0,e2=0;for(let i=0;i<N-L;i+=2){a+=d[s0+i]*d[s0+i+L];e1+=d[s0+i]*d[s0+i];e2+=d[s0+i+L]*d[s0+i+L]}const c=a/Math.sqrt(e1*e2+1e-12);if(c>best){best=c;bl=L}}
    // prefer the shortest lag whose correlation is close to the best (avoids picking a multiple of the period)
    for(let m=4;m>=2;m--){const L=Math.round(bl/m);if(L<LO)continue;let a=0,e1=0,e2=0;for(let i=0;i<N-L;i+=2){a+=d[s0+i]*d[s0+i+L];e1+=d[s0+i]*d[s0+i];e2+=d[s0+i+L]*d[s0+i+L]}if(a/Math.sqrt(e1*e2+1e-12)>best*.9){bl=L;break}}
    // parabolic refinement
    const ac=L=>{let a=0;for(let i=0;i<N-L;i+=2)a+=d[s0+i]*d[s0+i+L];return a};const y0=ac(bl-1),y1=ac(bl),y2=ac(bl+1),dl=(y0-y2)/(2*(y0-2*y1+y2)||1);
    const f=sr/(bl+(isFinite(dl)?dl:0));r={n,ok:true,f,cents:1200*Math.log2(f/f0),dur:buf.duration,corr:best}}catch(e){r.err=String(e)}out[k].push(r)}}return out}"""


async def main():
    fails, counts = [], {}
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page()
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html')
        await pg.wait_for_timeout(1200)
        res = await pg.evaluate(PITCH)
        for k, rows in res.items():
            counts[k] = len(rows)
            ok_rows = [r for r in rows if r['ok']]
            counts[k + ' max |cents|'] = round(max(abs(r['cents']) for r in ok_rows), 1) if ok_rows else None
            for r in rows:
                if not r['ok']:
                    fails.append(f"{k} {r['n']}: does not load ({r.get('err')})")
                elif abs(r['cents']) > 35:
                    fails.append(f"{k} {r['n']}: sounds {r['f']:.1f} Hz, {r['cents']:+.0f} cents from MIDI {r['n']} (corr {r['corr']:.2f})")
        # app-side loading
        await pg.evaluate("ac();Object.keys(SMP).forEach(k=>loadSamples(k))")
        await pg.wait_for_timeout(4000)
        loaded = await pg.evaluate("Object.fromEntries(Object.keys(SMP).map(k=>[k,SBUF[k]?Object.keys(SBUF[k]).length:0]))")
        for k, n in loaded.items():
            if n != counts.get(k):
                fails.append(f'{k}: the app loaded {n} of {counts.get(k)} samples')
        await b.close()
        # synth fallback: block the audio files
        b = await cjg.launch(p)
        pg = await b.new_page()
        errs2 = []
        pg.on('pageerror', lambda e: errs2.append(str(e)[:200]))
        route = cjg.make_route(REPO)

        async def blocked(r):
            if '/audio/' in r.request.url:
                return await r.fulfill(status=404)
            return await route(r)
        await pg.add_init_script("""(()=>{window.__O=0;const P=OscillatorNode.prototype,st=P.start;P.start=function(...a){__O++;return st.apply(this,a)}})()""")
        await pg.route('**/*', blocked)
        await pg.goto('http://app/index.html')
        await pg.wait_for_timeout(1200)
        n = await pg.evaluate("(async()=>{ac();await new Promise(r=>setTimeout(r,800));__O=0;['piano','guitar-steel','guitar-nylon','bass','pluck'].forEach(k=>tone(60,ac().currentTime+.05,k));tone(64,ac().currentTime+.05,'piano',1,.4);await new Promise(r=>setTimeout(r,200));stopAll();return __O})()")
        if n < 6:
            fails.append(f'synth fallback: only {n} oscillators started for 6 notes with samples blocked')
        if errs or errs2:
            fails.append(f'page errors: {(errs + errs2)[:3]}')
        await b.close()
    print(json.dumps({'samples': counts, 'failures': fails[:25], 'n_failures': len(fails)}, indent=1))
    sys.exit(1 if fails else 0)

asyncio.run(main())
