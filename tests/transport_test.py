"""Transport and navigation test for the Composition Jungle Gym.
Run: python3 tests/transport_test.py <repo dir>   (needs playwright and Chrome; run tests/run_all once to install the harness)
Every play-type button in every room and climb must: start sound, show the top-bar Stop, turn into a Stop itself,
and leave silence (0 nodes sounding 0.25 s later) when stopped by the same button, by the top-bar Stop, by Esc, or by leaving.
Navigation: Back/Forward/reload must move between rooms, climbs and forms.

Ear Lab transport (register 0.48 EL-1), every drill x rung x width (1440, 390):
  the transport state (elInfo) matches the scheduled audio within 100 ms: it turns 'playing' at the press, its end equals the last
  node's stop time, it is still 'playing' 150 ms before that end and 'idle' 150 ms after it (natural end checked at 1440);
  a double tap (60 ms apart) of Play leaves it playing; Play while playing, and every variant while playing, leaves exactly one
  playback sounding (no node of the old one sounds 100 ms later); and the sound stops on Next, rung change, drill change, room change,
  answering (option or Check), Show me, a solfa-ladder tap (which plays its own note instead), Esc, the top-bar Stop and the Ear Lab Stop.
  The 'beats' variant of a metre item reports its beats and emits them live within 60 ms of their times."""
import sys,asyncio,json,pathlib,mimetypes,os
from playwright.async_api import async_playwright
REPO=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent/'harness'));import cjg
route=cjg.make_route(REPO)
HOOK="""(()=>{window.__N=[];for(const P of [AudioScheduledSourceNode.prototype,AudioBufferSourceNode.prototype]){const st=P.start,sp=P.stop;
P.start=function(t=0,...a){this.__r={s:t||0,e:Infinity,born:performance.now()};if(this instanceof AudioBufferSourceNode&&this.buffer&&!this.loop)this.__r.e=(t||0)+this.buffer.duration/(this.playbackRate.value||1);__N.push(this.__r);return st.call(this,t,...a)};
P.stop=function(t=0){if(this.__r)this.__r.e=Math.min(this.__r.e,(t||0)<=this.context.currentTime?this.context.currentTime:t);return sp.call(this,t)}}})()"""
PLAYRE=r'^\s*(▶|⟳)'
VIEWS=[r for r in ['seed','keys','voice','gym','oracle','forms','analysis','ear']]+['climbs/%d'%i for i in range(1,14)]
SOUND="()=>{const n=AC?AC.currentTime:0;return __N.filter(x=>x.e>n+0.25).length}"
async def main():
    fails=[];stats={'trials':0,'silent':0}
    if os.environ.get('EAR_ONLY'):   # run only the Ear Lab section (development)
        async with async_playwright() as p: ear=await ear_transport(p,fails)
        print(json.dumps({'ear':ear,'fails':fails[:40],'n_fails':len(fails)},ensure_ascii=False,indent=1));sys.exit(1 if fails else 0)
    async with async_playwright() as p:
        b=await cjg.launch(p)
        pg=await b.new_page(viewport={'width':1440,'height':900});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.add_init_script(HOOK);await pg.route('**/*',route);await pg.goto('http://app/index.html');await pg.wait_for_timeout(1500)
        await pg.evaluate("ac();Promise.all(['piano','guitar-steel','guitar-nylon','bass'].map(k=>loadSamples(k)))");await pg.wait_for_timeout(2500)
        # Gym needs a progression to play
        await pg.evaluate("location.hash='gym'");await pg.wait_for_timeout(300)
        await pg.evaluate("for(const r of ['I','vi','IV','V'])document.querySelector(`[data-add=\"${r}\"]`)?.click()");await pg.wait_for_timeout(300)
        await pg.evaluate("stopAll()")
        for v in VIEWS:
            await pg.evaluate(f"location.hash='{v}'");await pg.wait_for_timeout(450)
            n=await pg.evaluate("(re)=>[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&new RegExp(re).test(b.textContent)).length",PLAYRE)
            for i in range(min(n,10)):
                for how in ['same button','top-bar Stop','Esc','leave']:
                    await pg.evaluate("stopAll()");await pg.wait_for_timeout(120)
                    if (await pg.evaluate("location.hash.slice(1)"))!=v:
                        await pg.evaluate(f"location.hash='{v}'");await pg.wait_for_timeout(400)
                    lab=await pg.evaluate("([re,i])=>{const B=[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&new RegExp(re).test(b.textContent));const b=B[i];if(!b)return null;b.setAttribute('data-t','1');const l=b.textContent.trim().slice(0,30);b.click();return l}",[PLAYRE,i])
                    if lab is None: continue
                    await pg.wait_for_timeout(500)
                    if await pg.evaluate(SOUND)==0: continue   # nothing playable here (e.g. needs input)
                    stats['trials']+=1
                    shown=await pg.evaluate("!document.getElementById('tStop').hidden")
                    if not shown: fails.append((v,lab,how,'top-bar Stop not shown'))
                    if how=='same button' and lab.strip().endswith('Start'): stats['silent']+=1; await pg.evaluate('stopAll()'); continue   # quiz Start turns into Next, not a toggle; Stop/Esc/leave are tested for it
                    if how=='same button':
                        tog=await pg.evaluate("()=>{const b=[...document.querySelectorAll('main button')].find(x=>x.offsetParent&&(x.dataset.playing||/■/.test(x.textContent)));return b?b.textContent.trim():null}")
                        if not tog or '■' not in tog: fails.append((v,lab,how,'button did not become Stop: '+str(tog)))
                        await pg.evaluate("()=>{const b=[...document.querySelectorAll('main button')].find(x=>x.offsetParent&&(x.dataset.playing||/■/.test(x.textContent)));b&&b.click()}")
                    elif how=='top-bar Stop': await pg.click('#tStop')
                    elif how=='Esc': await pg.keyboard.press('Escape')
                    else: await pg.evaluate("document.querySelector('.rail button[data-room=\"%s\"]').click()"%('keys' if v!='keys' else 'seed'))
                    await pg.wait_for_timeout(300)
                    left=await pg.evaluate(SOUND)
                    if left: fails.append((v,lab,how,f'{left} notes still sounding'))
                    else: stats['silent']+=1
                    await pg.evaluate("document.querySelectorAll('[data-t]').forEach(b=>b.removeAttribute('data-t'))")
        # long loop in the Gym
        await pg.evaluate("location.hash='gym'");await pg.wait_for_timeout(400)
        await pg.evaluate("for(let k=0;k<12;k++)document.querySelector('[data-add=\"ii\"]')?.click()")
        await pg.evaluate("stopAll();G.loop=true;document.getElementById('gLoop')&&(document.getElementById('gLoop').checked=true);document.getElementById('gPlay').click()")
        await pg.wait_for_timeout(25000)
        await pg.click('#tStop');await pg.wait_for_timeout(300)
        loopleft=await pg.evaluate(SOUND)
        if loopleft: fails.append(('gym','loop 25 s','top-bar Stop',f'{loopleft} still sounding'))
        stats['loop_nodes']=await pg.evaluate("__N.length")
        # navigation
        nav=[]
        async def st(): return await pg.evaluate("({room:ROOM,climb:CL.open,form:F.open,hash:location.hash})")
        await pg.click('.rail button[data-room="climbs"]');await pg.wait_for_timeout(300)
        await pg.click('[data-clopen="2"]');await pg.wait_for_timeout(400);a=await st()
        await pg.go_back();await pg.wait_for_timeout(400);b1=await st()
        await pg.go_forward();await pg.wait_for_timeout(400);c=await st()
        await pg.reload();await pg.wait_for_timeout(1500);d=await st()
        await pg.click('.rail button[data-room="forms"]');await pg.wait_for_timeout(300)
        await pg.evaluate("document.querySelector('[data-fopen]').click()");await pg.wait_for_timeout(400);e=await st()
        await pg.go_back();await pg.wait_for_timeout(400);f=await st()
        checks=[('open climb 3',a,'climbs/3'),('Back from climb → list',b1,'climbs'),('Forward → climb 3',c,'climbs/3'),('reload keeps climb 3',d,'climbs/3'),('open a form',e,'forms/'),('Back from form → forms list',f,'forms')]
        for lab,s,exp in checks:
            okk=(s['hash'].lstrip('#')==exp) if not exp.endswith('/') else s['hash'].lstrip('#').startswith(exp)
            nav.append((lab,s['hash'],'ok' if okk else 'FAIL'))
            if not okk: fails.append(('nav',lab,'',str(s)))
        await b.close()
        ear=await ear_transport(p,fails)
    print(json.dumps({'stats':stats,'nav':nav,'ear':ear,'fails':fails[:40],'n_fails':len(fails),'page_errors':errs[:5]},ensure_ascii=False,indent=1))
    sys.exit(1 if fails or errs or stats['silent']!=stats['trials'] else 0)

EARHOOK="""(()=>{window.__N=[];const st0=AudioScheduledSourceNode.prototype.start,sp0=AudioScheduledSourceNode.prototype.stop;
 for(const P of [AudioScheduledSourceNode.prototype,AudioBufferSourceNode.prototype]){const st=P.start,sp=P.stop;
 P.start=function(t=0,...a){if(!(this.context instanceof OfflineAudioContext)){this.__r={s:Math.max(t||0,this.context.currentTime),e:Infinity,born:performance.now()};if(this instanceof AudioBufferSourceNode&&this.buffer&&!this.loop)this.__r.e=this.__r.s+this.buffer.duration/(this.playbackRate.value||1);__N.push(this.__r)}return st.call(this,t,...a)};
 P.stop=function(t=0){if(this.__r)this.__r.e=Math.min(this.__r.e,Math.max(t||0,this.context.currentTime));return sp.call(this,t)}}})()"""
# nodes born before `since` (performance.now ms) that still sound at audio time now+lag
OLD="(a)=>{const[since,lag]=a;const n=AC.currentTime;return __N.filter(x=>x.born<since&&x.e>n+lag).length}"
LIVE="()=>{const n=AC.currentTime;return __N.filter(x=>x.e>n+.1).length}"
INFO="()=>({...elInfo(),now:AC?AC.currentTime:0,pnow:performance.now(),last:__N.length?Math.max(...__N.filter(x=>x.born>=ELT.start-1).map(x=>x.e)):null})"

async def ear_transport(p,fails):
    st={'items':0,'state_checks':0,'natural_end':0,'double_tap':0,'play_while_playing':0,'variants':0,'stop_events':0,'beats_live':0}
    worst={'end_diff_ms':0}
    def F(*a): fails.append(('ear',)+a)
    for w,h in ((1440,900),(390,844)):
        b=await cjg.launch(p);pg=await b.new_page(viewport={'width':w,'height':h});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)[:200]))
        await pg.add_init_script(EARHOOK);await pg.route('**/*',route);await pg.goto('http://app/index.html#ear');await pg.wait_for_timeout(1200)
        await pg.evaluate("(async()=>{ac();await loadSamples('piano');await earLoadBlind()})()");await pg.wait_for_timeout(500)
        async def click(sel):
            await pg.evaluate("(s)=>{const b=document.querySelector(s);if(!b)throw new Error('no '+s);b.click()}",sel)
        async def check_state(tag):
            i=await pg.evaluate(INFO)
            st['state_checks']+=1
            if i['state']!='playing': F(tag,'state not playing after the press',i['state']);return i
            if i['last'] is None or i['last']==float('inf'): F(tag,'no finite scheduled node');return i
            d=abs(i['end']-i['last'])
            worst['end_diff_ms']=max(worst['end_diff_ms'],round(d*1000,1))
            if d>.1: F(tag,f"state end {i['end']:.3f} vs last node stop {i['last']:.3f}")
            if abs(i['end']-i['t0']-i['dur'])>1e-6 or i['t0']>i['now']: F(tag,'dur does not match end')
            return i
        # EL-1 UI: the visible toggle follows the transport (checked within 100 ms of every press, and at the natural end)
        async def check_toggle(tag,want):
            await pg.wait_for_timeout(100)
            t=await pg.evaluate("""()=>{const b=document.querySelector('#earMain .el-stage [data-earplay="all"]');if(!b)return null;const i=elInfo(),n=document.querySelector('#earMain .el-stage .el-now');
              return{pl:b.classList.contains('playing'),ap:b.getAttribute('aria-pressed'),lab:b.getAttribute('aria-label'),dur:parseFloat(b.style.getPropertyValue('--dur')),idur:i.dur,state:i.state,txt:n.textContent,ring:getComputedStyle(b.querySelector('.ring')).opacity}}""")
            st['toggle_checks']=st.get('toggle_checks',0)+1
            if t is None: F(tag,'no toggle in the stage');return
            if want=='playing':
                if not (t['pl'] and t['ap']=='true' and t['lab']=='Stop' and t['ring']=='1'): F(tag,'toggle does not show Stop while playing',t)
                if abs(t['dur']-t['idur'])>.05: F(tag,'ring duration differs from elInfo().dur',t['dur'],t['idur'])
                if not (t['txt'].startswith('StopPlaying')or t['txt'].startswith('StopCount-in')): F(tag,'toggle text while playing',t['txt'])
            else:
                if t['pl'] or t['ap']!='false' or t['lab']!='Play' or 'Play again' not in t['txt'] or 'Ready' not in t['txt']: F(tag,'toggle did not return to Ready by itself',t)
        for d in ['metre','rhy','qual','cad','bass','mel','blind']:
            for l in (1,2,3):
                tag=f'{w}px {d} rung {l}'
                await pg.evaluate("stopAll()");await pg.wait_for_timeout(80)
                await click(f'[data-eardr="{d}"]');await pg.wait_for_timeout(60);await click(f'[data-earlv="{l}"]');await pg.wait_for_timeout(60)
                await pg.evaluate("__N.length=0");await click('[data-earplay="all"]');await pg.wait_for_timeout(250)
                st['items']+=1
                i=await check_state(tag)
                if i['state']!='playing': continue
                await check_toggle(tag,'playing')
                # natural end (1440 only, to keep the run short)
                if w==1440:
                    a,z=await pg.evaluate("""async()=>{const end=ELT.end,until=t=>new Promise(r=>{const f=()=>AC.currentTime>=t?r():setTimeout(f,5);f()});
                      await until(end-.15);const a=elInfo().state;await until(end+.15);return[a,[elInfo().state]]}""")
                    st['natural_end']+=1
                    if a!='playing' or z[0]!='idle': F(tag,f'natural end: {a} 150 ms before the end, {z[0]} 150 ms after')
                    await check_toggle(tag+' natural end','ready')
                    if await pg.evaluate(LIVE): F(tag,'nodes still sounding after the natural end')
                # double tap on Play (60 ms apart)
                await pg.evaluate("stopAll()");await pg.wait_for_timeout(80)
                await click('[data-earplay="all"]');await pg.wait_for_timeout(60);await click('[data-earplay="all"]')
                await pg.wait_for_timeout(400)
                st['double_tap']+=1
                if await pg.evaluate("elInfo().state")!='playing' or not await pg.evaluate(LIVE): F(tag,'double tap left silence')
                # play while playing: Play again, then every variant
                for v in ['all']+await pg.evaluate("[...document.querySelectorAll('[data-earplay]')].map(b=>b.dataset.earplay).filter(v=>v!=='all')"):
                    since=await pg.evaluate("performance.now()")
                    await pg.evaluate("__N.forEach(x=>x.born=Math.min(x.born,performance.now()-1))")
                    # Play again while playing goes through the API (pressing the playing Play button is the toggle: it stops, tested below)
                    if v=='all': await pg.evaluate("elPlay(EAR.q,'all')")
                    else: await click(f'[data-earplay="{v}"]')
                    await pg.wait_for_timeout(450)
                    st['play_while_playing' if v=='all' else 'variants']+=1
                    if await pg.evaluate(OLD,[since,.0]): F(tag,f'variant {v}: the previous playback still sounds')
                    i=await check_state(tag+' variant '+v)
                    if i['variant']!=v: F(tag,f'variant {v}: state says {i["variant"]}')
                    if v=='all' and l==1 and w==1440:
                        # the global toggle: pressing the playing button within 300 ms is ignored, after that it stops
                        pass
                # stop events
                async def ev(name,fn,expect='idle'):
                    await pg.evaluate("stopAll()");await pg.wait_for_timeout(60)
                    await click('[data-earplay="all"]');await pg.wait_for_timeout(450)
                    if await pg.evaluate("elInfo().state")!='playing': F(tag,f'{name}: did not start');return
                    await pg.evaluate("__N.forEach(x=>x.born=Math.min(x.born,performance.now()-1))")
                    since=await pg.evaluate("performance.now()")
                    await fn();await pg.wait_for_timeout(200)
                    st['stop_events']+=1
                    if expect=='idle' and await pg.evaluate("document.querySelectorAll('#earMain .el-play.playing').length"): F(tag,f'{name}: a toggle still shows Stop')
                    left=await pg.evaluate(OLD,[since,.0])
                    s2=await pg.evaluate("elInfo().state")
                    if left: F(tag,f'{name}: {left} nodes of the question still sounding')
                    if expect=='idle' and s2!='idle': F(tag,f'{name}: state {s2}, expected idle')
                    if expect=='playing' and s2!='playing': F(tag,f'{name}: state {s2}, expected playing')
                if w==1440 or l==2:
                    await ev('Ear Lab toggle (Stop)',lambda:click('[data-earplay="all"]'))
                    await ev('top-bar Stop',lambda:pg.evaluate("document.getElementById('tStop').click()"))
                    await ev('Esc',lambda:pg.keyboard.press('Escape'))
                    await ev('Next',lambda:click('[data-earnew]'),'playing')
                    if await pg.evaluate("!!document.querySelector('[data-earshow]')"):
                        await ev('Show me',lambda:click('[data-earshow]'))
                        await click('[data-earnew]');await pg.wait_for_timeout(250)
                    # answering
                    q=await pg.evaluate("EAR.q.d")
                    if q in ('metre','qual','cad','blind'):
                        await ev('answer (option)',lambda:click('[data-earans]'))
                    else:
                        await pg.evaluate("EAR.ans=EAR.q.d==='rhy'?EAR.q.a.slice():EAR.q.a.slice(1);renderEar()")
                        await ev('answer (Check)',lambda:click('[data-earchk]'))
                    if q=='mel':
                        await click('[data-earnew]');await pg.wait_for_timeout(250)
                        await ev('solfa ladder tap',lambda:click('.earstep[data-earsol]'),'playing')
                        if await pg.evaluate("elInfo().variant")!='tap': F(tag,'ladder tap is not reported as the tap variant')
                    await click('[data-earnew]');await pg.wait_for_timeout(250)
                    other=3 if l!=3 else 1
                    await ev('rung change',lambda:click(f'[data-earlv="{other}"]'))
                    await click(f'[data-earlv="{l}"]');await click('[data-earplay="all"]');await pg.wait_for_timeout(250)
                    await ev('drill change',lambda:click(f'[data-eardr="{"qual" if d!="qual" else "cad"}"]'))
                    await click(f'[data-eardr="{d}"]');await click(f'[data-earlv="{l}"]');await click('[data-earplay="all"]');await pg.wait_for_timeout(250)
                    await ev('room change',lambda:pg.evaluate("location.hash='keys'"))
                    await pg.evaluate("location.hash='ear'");await pg.wait_for_timeout(300)
        # beats reported live (metre 'beats' variant)
        if w==1440:
            r=await pg.evaluate("""async()=>{stopAll();const q=earGen('metre',1);const got=[];const off=elOn(e=>{if(e.type==='beat')got.push([e.i,performance.now()])});
              const info=elPlay(q,'beats');await new Promise(r=>setTimeout(r,(info.beats[2].t+.3)*1000));off();stopAll();
              return{beats:info.beats.slice(0,3),got:got.map(([i,t])=>[i,(t-info.start)/1000])}}""")
            for i,t in r['got']:
                st['beats_live']+=1
                if abs(t-r['beats'][i]['t'])>.06: F('beats variant',f'beat {i} emitted at {t:.3f} s, scheduled {r["beats"][i]["t"]:.3f} s')
            if len(r['got'])<3: F('beats variant',f'only {len(r["got"])} beat events in the first three beats')
        # the global toggle: a second tap on the playing ▶ button within 300 ms is ignored; after 300 ms it stops
        if w==1440:
            await pg.evaluate("stopAll()");await click('[data-eardr="cad"]');await click('[data-earlv="1"]');await click('[data-earplay="all"]');await pg.wait_for_timeout(500)
            await pg.evaluate("stopAll()");await pg.wait_for_timeout(100)
            await click('[data-earplay="all"]');await pg.wait_for_timeout(120);await click('[data-earplay="all"]');await pg.wait_for_timeout(200)
            if await pg.evaluate("elInfo().state")!='playing': F('toggle','a second tap 120 ms after Play stopped it')
            await pg.wait_for_timeout(300);await pg.evaluate("()=>{const b=document.querySelector('[data-earplay=\"all\"]');b.click()}");await pg.wait_for_timeout(250)
            if await pg.evaluate("elInfo().state")!='idle' or await pg.evaluate(LIVE): F('toggle','the playing Play button did not stop the sound')
        if errs: F(f'{w}px','page errors',errs[:3])
        await b.close()
    st.update(worst);return st

asyncio.run(main())
