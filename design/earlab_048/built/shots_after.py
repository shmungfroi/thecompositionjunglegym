#!/usr/bin/env python3
"""Fable-fix (FR-1..19) after-shots of the built Ear Lab card in the same states and widths as design/earlab_048/png (Fable's mock-ups).
Run from the repo root:  python3 design/earlab_048_built/shots.py [state ...]
Each state is set up through the real app (EAR state, then the real renderEar), so these are the live card, not a mock-up."""
import sys, asyncio, pathlib
HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent.parent
sys.path.insert(0, str(REPO / 'tests' / 'harness'))
import cjg
from playwright.async_api import async_playwright

PRE = """(()=>{window.R=(s=>()=>(s=(s*16807)%%2147483647)/2147483647)(7);S.level=%(stage)d;document.querySelectorAll('#lvl button').forEach(b=>b.classList.toggle('on',+b.dataset.l===S.level));
 location.hash='ear';EAR.drill='%(d)s';EAR.lvl['%(d)s']=%(l)d;EAR.q=null;EAR.done=false;EAR.res=null;EAR.ans=[];EAR.all=false;EAR.st={};EAR.st['%(d)s']=%(st)s;room('ear');})()"""
RANS = "['e2','q','dq','s4','q','h']"
STATES = {
 'metre_idle': dict(d='metre', l=2, stage=4, st='{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}', js="renderEar()", widths=[1440, 390]),
 'metre_playing': dict(d='metre', l=2, stage=5, st='{n:8,ok:6,streak:2,best:4,shown:1,skipped:2}',
    js="EAR.q=earGenMetre(2,R,{m:'4/4',bpm:84});EAR.q.l=2;EAR.q.lvl=2;EAR.q.plays=0;renderEar();elPlay(EAR.q,'all')", wait=4300, widths=[1440, 390]),
 'metre_answered': dict(d='metre', l=2, stage=5, st='{n:8,ok:6,streak:2,best:4,shown:1,skipped:2}',
    js="EAR.q=earGenMetre(2,R,{m:'6/8',bpm:84});EAR.q.l=2;EAR.q.lvl=2;EAR.q.plays=1;earMark(false,'3/4');renderEar()", widths=[1440, 1366, 1024, 390]),
 'rhythm_answering': dict(d='rhy', l=3, stage=6, st='{n:6,ok:4,streak:1,best:3,shown:0,skipped:1}',
    js="EAR.q={d:'rhy',bars:2,a:%s,l:3,lvl:3,plays:2};EAR.ans=['e2','q','dq','s4'];renderEar()" % RANS, widths=[1440, 390]),
 'rhythm_countin': dict(d='rhy', l=3, stage=6, st='{n:6,ok:4,streak:1,best:3,shown:0,skipped:1}',
    js="EAR.q={d:'rhy',bars:2,a:%s,l:3,lvl:3,plays:1};EAR.ans=['e2','q','dq','s4'];renderEar();elPlay(EAR.q,'all')" % RANS, wait=1650, widths=[1440, 390]),
 'rhythm_rung1': dict(d='rhy', l=1, stage=4, st='{n:2,ok:2,streak:2,best:2,shown:0,skipped:0}',
    js="EAR.q={d:'rhy',bars:1,a:['e2','q','h'],l:1,lvl:1,plays:1};EAR.ans=['e2','q'];renderEar()", widths=[1440, 390]),
 'rhythm_checked': dict(d='rhy', l=3, stage=6, st='{n:6,ok:4,streak:1,best:3,shown:0,skipped:1}',
    js="EAR.q={d:'rhy',bars:2,a:%s,l:3,lvl:3,plays:2};earMark(false,['e2','q','dq','es2','q','h']);renderEar()" % RANS, widths=[1440, 1366, 1024, 390]),
 'cadence_r3_answered': dict(d='cad', l=3, stage=6, st='{n:14,ok:11,streak:0,best:6,shown:2,skipped:1}',
    js="let q;do{q=earGen('cad',3,R)}while(q.a!=='phrygian'||q.key.k!==2);q.plays=1;EAR.q=q;earMark(false,'plagal');renderEar()", widths=[1440, 1366, 1024, 390]),
 'cadence_r3_nearly': dict(d='cad', l=3, stage=6, st='{n:14,ok:11,streak:3,best:6,shown:2,skipped:1}',
    js="EAR_NEARLY=true;let q;do{q=earGen('cad',3,R)}while(q.a!=='phrygian'||q.key.k!==2);q.plays=1;EAR.q=q;const j=earJudge(q,'imperfect');earMark(j==='nearly'?'nearly':false,'imperfect');renderEar();EAR_NEARLY=false", widths=[1440, 390]),
 'bass_answered': dict(d='bass', l=3, stage=6, st='{n:5,ok:3,streak:1,best:2,shown:0,skipped:0}',
    js="let q;do{q=earGen('bass',3,R)}while(q.a.join()!=='I,ii,V,I');q.plays=1;EAR.q=q;earMark(false,['IV','V','I']);renderEar()", widths=[1440, 390]),
 'quality_answered': dict(d='qual', l=2, stage=6, st='{n:7,ok:5,streak:2,best:3,shown:0,skipped:0}',
    js="let q;do{q=earGen('qual',2,R)}while(q.a!=='m');q.plays=1;EAR.q=q;earMark(false,'dim');renderEar()", widths=[1440, 390]),
 'melody_answered': dict(d='mel', l=2, stage=6, st='{n:4,ok:3,streak:1,best:2,shown:0,skipped:0}',
    js="const q=earGen('mel',2,R);q.plays=1;EAR.q=q;const g=q.a.slice(1);g[2]=g[2]==='s'?'m':'s';earMark(false,g);renderEar()", widths=[1440, 390]),
 'tally_reset_confirm': dict(d='cad', l=3, stage=6, st='{n:15,ok:11,streak:3,best:6,shown:2,skipped:1}', js="EAR.resetAsk=true;renderEar()", widths=[1440, 390], clip='card'),
 'tally_reset_undo': dict(d='cad', l=1, stage=6, st='{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}', js="EAR.resetUndo={drill:'cad',st:{n:15,ok:11,streak:3,best:6,shown:2,skipped:1}};renderEar()", widths=[1440, 390], clip='card'),
 'tally_keys_name': dict(d='cad', l=1, stage=6, st='{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}',
    js="KS.tab='intervals';KS.gym.mode='name';KS.gym.st.name={n:12,ok:9,streak:4,best:5};location.hash='keys';room('keys');renderKeysRoom();newQ();renderGymUI()", widths=[1440, 390], clip='#ivGym'),
 'tally_keys_sing': dict(d='cad', l=1, stage=6, st='{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}',
    js="KS.tab='intervals';KS.gym.mode='sing';KS.gym.st.sing={n:8,ok:5,streak:2,best:3};location.hash='keys';room('keys');renderKeysRoom();renderGymUI()", widths=[1440, 390], clip='#ivGym'),
 'phone_dock': dict(d='rhy', l=3, stage=6, st='{n:6,ok:4,streak:1,best:3,shown:0,skipped:1}',
    js="EAR.q={d:'rhy',bars:2,a:%s,l:3,lvl:3,plays:1};EAR.ans=['e2','q','dq','s4'];renderEar();elPlay(EAR.q,'all')" % RANS, wait=1200, widths=[390], scroll=900, full=False),
 'metre_r3_54': dict(d='metre', l=3, stage=6, st='{n:8,ok:6,streak:2,best:4,shown:1,skipped:2}',
    js="EAR.q=earGenMetre(3,R,{m:'5/4',bpm:84});EAR.q.l=3;EAR.q.lvl=3;EAR.q.plays=1;earMark(false,'4/4');renderEar()", widths=[1440, 1024, 390]),
 'metre_r3_78': dict(d='metre', l=3, stage=6, st='{n:8,ok:6,streak:2,best:4,shown:1,skipped:2}',
    js="EAR.q=earGenMetre(3,R,{m:'7/8',bpm:84});EAR.q.l=3;EAR.q.lvl=3;EAR.q.plays=1;earMark(true,'7/8');renderEar()", widths=[1440, 390]),
 'metre_stage4_idle': dict(d='metre', l=2, stage=4, st='{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}', js="EAR.all=false;renderEar()", widths=[1440, 390]),
 'cad_interrupted': dict(d='cad', l=2, stage=5, st='{n:14,ok:11,streak:0,best:6,shown:2,skipped:1}',
    js="let q;do{q=earGen('cad',2,R)}while(q.a!=='interrupted');q.plays=1;EAR.q=q;earMark(false,'imperfect');renderEar()", widths=[1440, 1024, 390]),
 'cad_idle_key': dict(d='cad', l=3, stage=6, st='{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}', js="renderEar()", widths=[1440, 390]),
 'mel_wrong': dict(d='mel', l=2, stage=6, st='{n:4,ok:3,streak:1,best:2,shown:0,skipped:0}',
    js="const q=earGen('mel',2,R);q.plays=1;EAR.q=q;const g=q.a.slice(1);g[2]=g[2]==='s'?'m':'s';earMark(false,g);renderEar()", widths=[1440, 1024, 390]),
 'mel_answering': dict(d='mel', l=2, stage=6, st='{n:4,ok:3,streak:1,best:2,shown:0,skipped:0}',
    js="const q=earGen('mel',2,R);q.plays=1;EAR.q=q;EAR.ans=q.a.slice(1,3);renderEar()", widths=[390]),
 'bass_two_digit': dict(d='bass', l=3, stage=6, st='{n:58,ok:44,streak:12,best:21,shown:0,skipped:0}',
    js="let q;do{q=earGen('bass',3,R)}while(q.a.join()!=='I,ii,V,I');q.plays=1;EAR.q=q;earMark(false,['IV','V','I']);renderEar()", widths=[1440, 390]),
 'qual_idle': dict(d='qual', l=3, stage=6, st='{n:0,ok:0,streak:0,best:0,shown:0,skipped:0}', js="renderEar()", widths=[1440, 390]),
 'blind_wrong': dict(d='blind', l=1, stage=6, st='{n:3,ok:1,streak:0,best:1,shown:0,skipped:0}', js="EAR.q=null;renderEar()", widths=[1440]),
}


async def main(names):
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for name in names:
            st = STATES[name]
            for w in st['widths']:
                h = 768 if w in (1366, 1024) else 900 if w == 1440 else 844
                pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2 if w == 390 else 1)
                errs = []
                pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
                await pg.route('**/*', cjg.make_route(REPO))
                await pg.goto('http://app/index.html'); await pg.wait_for_timeout(1000)
                await pg.evaluate(PRE % dict(d=st['d'], l=st['l'], stage=st['stage'], st=st['st']))
                await pg.evaluate("()=>{" + st['js'] + "}")
                await pg.wait_for_timeout(st.get('wait', 600))
                if st.get('full', True):
                    ph = await pg.evaluate('document.documentElement.scrollHeight')
                    await pg.set_viewport_size({'width': w, 'height': max(h, ph)}); await pg.wait_for_timeout(200)
                if st.get('scroll'):
                    await pg.evaluate(f"scrollTo(0,{st['scroll']})"); await pg.wait_for_timeout(500)
                over = await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
                path = HERE / 'png_after' / f'{name}_{w}.png'
                if st.get('clip'):
                    sel = '#earCard' if st['clip'] == 'card' else st['clip']
                    el = await pg.query_selector(sel)
                    await el.screenshot(path=str(path))
                else:
                    await pg.screenshot(path=str(path))
                print(name, w, 'sideways' if over > 0 else 'ok', errs)
                await pg.close()
        await b.close()

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:] or list(STATES)))
