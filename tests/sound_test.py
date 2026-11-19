"""Sound test (charter regression suite 9).
Run: python3 tests/sound_test.py <repo dir>

1. Every sample set the app declares (SMP: piano, guitar-steel, guitar-nylon, bass) loads: every note file listed exists
   and decodes.
2. Pitch: each decoded sample's fundamental (autocorrelation over 0.15-0.65 s of the note, in the browser) is within
   35 cents of the MIDI note its file name claims, octave errors included as failures.
3. Synth fallback: with the sample files blocked, tone() still sounds (oscillator nodes start) and nothing throws.

4. EL-3 metre: every metre at 60, 90 and 120 bpm, rendered offline through the app's own scheduler (elRender): 0.6 s of silence before
   the first click and no count-in; whole bars sounding at least 10 s; the last event is a downbeat; the click levels (measured above
   600 Hz, so the downbeat's bass note is left out) step down at least 4 dB from downbeat to secondary accent to beat to subdivision,
   and every event of a class is louder than every event of the class below.
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


# ---------------------------------------------------------------- register 0.48: offline renders of the Ear Lab and Analysis playback
DSP = r"""
const BQ=(x,b,a)=>{const y=new Float32Array(x.length);let x1=0,x2=0,y1=0,y2=0;for(let i=0;i<x.length;i++){const v=b[0]*x[i]+b[1]*x1+b[2]*x2-a[1]*y1-a[2]*y2;x2=x1;x1=x[i];y2=y1;y1=v;y[i]=v}return y};
const BIQ=(type,f,sr,Q=Math.SQRT1_2)=>{const w=2*Math.PI*f/sr,c=Math.cos(w),al=Math.sin(w)/(2*Q),a0=1+al;
 return type==='hp'?[[(1+c)/2/a0,-(1+c)/a0,(1+c)/2/a0],[1,-2*c/a0,(1-al)/a0]]:[[(1-c)/2/a0,(1-c)/a0,(1-c)/2/a0],[1,-2*c/a0,(1-al)/a0]]};
const FILT=(x,type,f,sr,n=2)=>{let y=x;for(let i=0;i<n;i++){const[b,a]=BIQ(type,f,sr);y=BQ(y,b,a)}return y};
const ENV=(x,sr,win=.002,hop=.001)=>{const W=Math.round(win*sr),H=Math.round(hop*sr),o=[];for(let s=0;s+W<=x.length;s+=H){let e=0;for(let i=s;i<s+W;i++)e+=x[i]*x[i];o.push(Math.sqrt(e/W))}return o};
const LUFS=(x,sr)=>{let y=BQ(x,[1.53512485958697,-2.69169618940638,1.19839281085285],[1,-1.69065929318241,.73248077421585]);y=BQ(y,[1,-2,1],[1,-1.99004745483398,.99007225036621]);
 const B=Math.round(.4*sr),H=Math.round(.1*sr),z=[];for(let s=0;s+B<=y.length;s+=H){let e=0;for(let i=s;i<s+B;i++)e+=y[i]*y[i];z.push(e/B)}
 const L=v=>-.691+10*Math.log10(v);let g=z.filter(v=>L(v)>-70);if(!g.length)return -99;const m=g.reduce((a,b)=>a+b,0)/g.length,rel=L(m)-10;g=g.filter(v=>L(v)>rel);return L(g.reduce((a,b)=>a+b,0)/g.length)};
const DB=v=>20*Math.log10(v+1e-12);
"""
METRE_JS = DSP + r"""async()=>{const out=[];const sr=24000;
 for(const m of Object.keys(METRES))for(const bpm of [60,90,120]){let s=3;const R=()=>{s=(s*16807)%2147483647;return s/2147483647};
  // a question as the generator makes it, at a fixed tempo
  let q;for(let k=0;k<400;k++){q=earGenMetre(3,R);if(q.a===m)break}const sc=q.bpm/bpm;q={...q,bpm,len:q.len*sc,ev:q.ev.map(e=>({...e,t:e.t*sc}))};
  const r=await elRender(q,'all',{sr}),x=r.buf.getChannelData(0),ev=r.info.events;
  let first=-1;for(let i=0;i<x.length;i++)if(Math.abs(x[i])>1e-4){first=i/sr;break}
  const hp=FILT(x,'hp',600,sr,3),lv=ev.map(e=>{const a=Math.round(e.t*sr),b=Math.min(x.length,a+Math.round(.06*sr));let p=0;for(let i=a;i<b;i++)p=Math.max(p,Math.abs(hp[i]));return{a:e.a,db:DB(p)}});
  const barLen=q.len/4,last=ev[ev.length-1],span=last.t-ev[0].t;
  out.push({m,bpm,first,lead:r.info.lead,span,bars:span/barLen,lastA:last.a,lastBar:last.bar,nb:ev.filter(e=>e.a===2).length,lv,beats:(r.info.beats||[]).length,nbeats:ev.filter(e=>e.a>=0).length})}
 return out}"""
async def render_tests(p, fails, counts):
    b = await cjg.launch(p)
    errs = []
    pages = []

    async def fresh():
        # a fresh page per section: thousands of offline contexts in one page can exhaust the renderer
        if pages:
            await pages.pop().close()
        pg = await b.new_page()
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.add_init_script("""(()=>{window.__N=[];for(const P of [AudioScheduledSourceNode.prototype,AudioBufferSourceNode.prototype]){const st=P.start,sp=P.stop;
          P.start=function(t=0,...a){if(!(this.context instanceof OfflineAudioContext)){this.__r={s:t||0,e:Infinity,k:this instanceof AudioBufferSourceNode?'smp':'osc'};__N.push(this.__r)}return st.call(this,t,...a)};
          P.stop=function(t=0){if(this.__r)this.__r.e=Math.min(this.__r.e,t);return sp.call(this,t)}}})()""")
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#ear')
        await pg.wait_for_timeout(1200)
        pages.append(pg)
        return pg
    pg = await fresh()
    # EL-3
    rows = await pg.evaluate(METRE_JS)
    steps = {}
    for r in rows:
        tag = f"metre {r['m']} at {r['bpm']} bpm"
        counts['metre renders'] = counts.get('metre renders', 0) + 1
        if not (.595 <= r['first'] <= .62) or abs(r['lead'] - .6) > 1e-6:
            fails.append(f"{tag}: first sound at {r['first']:.3f} s (lead-in should be 0.6 s of silence)")
        if r['span'] < 10 - 1e-6 or abs(r['bars'] - round(r['bars'])) > 1e-6:
            fails.append(f"{tag}: sounds {r['span']:.2f} s = {r['bars']:.2f} bars (whole bars, at least 10 s)")
        if r['lastA'] != 2:
            fails.append(f'{tag}: the last event is not a downbeat')
        if r['beats'] != r['nbeats']:
            fails.append(f"{tag}: the beats hook reports {r['beats']} beats, {r['nbeats']} were played")
        cls = {}
        for e in r['lv']:
            cls.setdefault(e['a'], []).append(e['db'])
        order = [a for a in (2, 1, 0, -1) if a in cls]
        for hi, lo in zip(order, order[1:]):
            mh, ml = sum(cls[hi]) / len(cls[hi]), sum(cls[lo]) / len(cls[lo])
            k = f'{hi}>{lo}'
            steps[k] = min(steps.get(k, 99), round(mh - ml, 1))
            if mh - ml < 4 or min(cls[hi]) <= max(cls[lo]):
                fails.append(f'{tag}: accent step {k} is {mh-ml:.1f} dB (min {min(cls[hi]):.1f} vs max {max(cls[lo]):.1f})')
    counts['metre smallest accent step (dB)'] = steps
    if errs:
        fails.append(f'render page errors: {errs[:3]}')
    await b.close()


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
        await render_tests(p, fails, counts)
    print(json.dumps({'samples': counts, 'failures': fails[:40], 'n_failures': len(fails)}, indent=1))
    sys.exit(1 if fails else 0)

asyncio.run(main())
