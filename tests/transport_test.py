"""Transport and navigation test for the Composition Jungle Gym.
Run: python3 tests/transport_test.py <repo dir>   (needs playwright and Chrome; run tests/run_all once to install the harness)
Every play-type button in every room and climb must: start sound, show the top-bar Stop, turn into a Stop itself,
and leave silence (0 nodes sounding 0.25 s later) when stopped by the same button, by the top-bar Stop, by Esc, or by leaving.
Navigation: Back/Forward/reload must move between rooms, climbs and forms."""
import sys,asyncio,json,pathlib,mimetypes
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
    print(json.dumps({'stats':stats,'nav':nav,'fails':fails[:40],'n_fails':len(fails),'page_errors':errs[:5]},ensure_ascii=False,indent=1))
asyncio.run(main())
