"""Ear Lab melody desk test (register 0.48 item R2, release 0.47).
Run: python3 tests/earlab_r2_test.py <repo dir>
Drives melody questions at levels 1-3 at 1440 and 390 px: taps rungs and checks the stave (note count, solfa, order, fixed positions),
undo / redo / clear, the full state, the reveal (one stave if right or "Show me", two aligned staves if wrong), the listen-only rungs,
the playback follow, the letter-names toggle, staff-space and solfa size, the pinned phone stave, a live resize, and no sideways overflow.
"""
import sys, asyncio, pathlib, collections
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

FAILS = []; N = [0]; LEDGERS = [0]
def check(c, msg):
    N[0] += 1
    if not c: FAILS.append(msg)

SEED = """(s)=>{let a=s;return ()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}"""
NEWQ = """([lvl,seed])=>{const mk=%s;EAR.drill='mel';EAR.lvl.mel=lvl;EAR.q=earGen('mel',lvl,mk(seed));EAR.done=false;EAR.res=null;EAR.ans=[];HIST.ear.u=[];HIST.ear.r=[];renderEar();
 return{a:EAR.q.a,mode:EAR.q.mode,range:EAR.q.range}}""" % SEED
# everything the stave and ladder show, read from the DOM
STATE = """()=>{const svg=document.querySelector('#earMel svg');if(!svg)return null;const fr=document.querySelector('#earMel').getBoundingClientRect(),sr=svg.getBoundingClientRect();
 const vb=svg.viewBox.baseVal,k=sr.width/vb.width;const rows={};
 svg.querySelectorAll('text.melsol').forEach(t=>{const r=t.getAttribute('data-row'),b=t.getBoundingClientRect();(rows[r]=rows[r]||{notes:[],sol:[]}).sol.push({i:+t.getAttribute('data-mi'),t:t.textContent,fill:t.getAttribute('fill'),cx:b.x+b.width/2,fs:parseFloat(t.getAttribute('font-size'))*k})});
 svg.querySelectorAll('g.vf-stavenote[data-mi]').forEach(g=>{const r=g.getAttribute('data-row'),h=g.querySelector('.vf-notehead')||g,b=h.getBoundingClientRect();(rows[r]=rows[r]||{notes:[],sol:[]}).notes.push({i:+g.getAttribute('data-mi'),cx:b.x+b.width/2,cy:b.y+b.height/2})});
 const lines=[...svg.querySelectorAll('g.vf-stave')[0].querySelectorAll('path')].map(p=>p.getAttribute('d').match(/M[\\d.]+ ([\\d.]+)/)[1]*1);
 return{rows,ss:(lines[1]-lines[0])*k,staves:svg.querySelectorAll('g.vf-stave').length,slots:svg.querySelectorAll('rect.melslot').length,cur:svg.querySelectorAll('rect.melslot.cur').length,
  labels:[...svg.querySelectorAll('text:not(.melsol)')].map(t=>t.textContent),aria:document.querySelector('#earMel').getAttribute('aria-label'),frameR:fr.right,
  cardR:document.querySelector('#earMain .card').getBoundingClientRect().right,docW:document.documentElement.scrollWidth,vw:innerWidth,
  rungs:[...document.querySelectorAll('.earstep')].map(b=>({s:b.dataset.earsol,dis:b.disabled,last:b.classList.contains('last'),home:b.classList.contains('home'),now:b.classList.contains('now'),h:b.getBoundingClientRect().height,al:b.getAttribute('aria-label'),sm:!!b.querySelector('small'),hm:!!b.querySelector('.hm')})),
  listen:!!document.querySelector('.earlad.listen'),slotsOld:document.querySelectorAll('.earslots').length,strip:(document.querySelector('.melres .el-result')||{}).textContent||'',
  stripCls:(document.querySelector('.melres .el-result')||{}).className||'',lbl:document.querySelector('.melscore .lbl').textContent,
  btn:{chk:(document.querySelector('[data-earchk]')||{}).disabled,und:(document.querySelector('[data-hist="ear:u"]')||{}).disabled,red:(document.querySelector('[data-hist="ear:r"]')||{}).disabled}}}"""

def sol(st, row='0'): return [s['t'] for s in sorted(st['rows'][row]['sol'], key=lambda s: s['i'])]

async def run(p, w):
    b = await cjg.launch(p)
    ctx = await b.new_context(viewport={'width': w, 'height': 900})
    pg = await ctx.new_page()
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
    await pg.route('**/*', cjg.make_route(REPO))
    await pg.goto('http://app/index.html#ear'); await pg.wait_for_timeout(1200)
    await pg.evaluate("()=>{window.__T=[];const o=window.c2Tone;window.c2Tone=(m,...a)=>{__T.push(m)}}")
    want_ss = 6.5 if w < 500 else 7.0
    for lvl in (1, 2, 3):
        for seed in (3, 8, 21):
            tag = f'{w}px L{lvl} seed{seed}'
            q = await pg.evaluate(NEWQ, [lvl, seed]); a = q['a']; n = len(a)
            st = await pg.evaluate(STATE)
            check(st['staves'] == 1 and st['slotsOld'] == 0, f'{tag}: one stave, no old solfa boxes')
            check(sol(st) == [a[0]] and len(st['rows']['0']['notes']) == 1, f'{tag}: only the given note at the start')
            check(st['slots'] == n - 1 and st['cur'] == 1, f'{tag}: {n-1} empty places, one gold')
            check(abs(st['ss'] - want_ss) < .1, f'{tag}: staff-space {st["ss"]:.2f} != {want_ss}')
            check(all(abs(s['fs'] - 12.5) < .1 for s in st['rows']['0']['sol']), f'{tag}: solfa 12.5 px')
            check(st['frameR'] <= st['cardR'] + .5 and st['docW'] <= st['vw'], f'{tag}: no sideways overflow (doc {st["docW"]}, vw {st["vw"]}, frame {st["frameR"]:.0f} card {st["cardR"]:.0f})')
            check(all(r['h'] >= (43.9 if w < 500 else 46.9) for r in st['rungs']), f'{tag}: ladder rows >= 44 px on phones (47 on desktop), tall ({min(r["h"] for r in st["rungs"]):.1f})')
            exp_n = q['range'][1] - q['range'][0] + 1
            check(len(st['rungs']) == exp_n, f'{tag}: one rung per step')
            homes = [r for r in st['rungs'] if r['hm']]
            check(len(homes) == 1 and homes[0]['home'] and 'home note' in homes[0]['al'] and homes[0]['s'] == ('l,' if q['mode'] == 'min' else 'd'), f'{tag}: home rung marked ({[h["s"] for h in homes]})')
            x0 = st['rows']['0']['notes'][0]['cx']
            # tap the first n-1 answers, checking the stave after every tap
            prev = None
            for i in range(1, n):
                await pg.click(f'.earstep[data-earsol="{a[i]}"]'); st = await pg.evaluate(STATE)
                check(sol(st) == a[:i + 1], f'{tag}: solfa after tap {i}: {sol(st)} vs {a[:i+1]}')
                nt = sorted(st['rows']['0']['notes'], key=lambda x: x['i'])
                check(len(nt) == i + 1, f'{tag}: {i+1} noteheads after tap {i}')
                check(st['slots'] == n - 1 - i, f'{tag}: empty places after tap {i}')
                check(abs(nt[0]['cx'] - x0) < .5, f'{tag}: first note did not move')
                if prev: check(all(abs(nt[j]['cx'] - prev[j]) < .5 for j in range(len(prev))), f'{tag}: earlier notes stayed put at tap {i}')
                prev = [x['cx'] for x in nt]
                check([r['s'] for r in st['rungs'] if r['last']] == [a[i]], f'{tag}: last-tapped rung gold at tap {i}')
                for j in range(len(nt)):
                    s_ = sorted(st['rows']['0']['sol'], key=lambda s: s['i'])[j]
                    check(abs(s_['cx'] - nt[j]['cx']) <= 2, f'{tag}: solfa {j} within 2 px of its notehead ({s_["cx"]-nt[j]["cx"]:.1f})')
                if i == 2:
                    # contour: a higher rung gives a higher notehead
                    pass
            # pitch order on the stave follows the ladder
            order = [q_ for q_ in [x['s'] for x in st['rungs']]]
            ys = {x['i']: x['cy'] for x in st['rows']['0']['notes']}
            for i in range(n):
                for j in range(n):
                    if order.index(a[i]) < order.index(a[j]): check(ys[i] <= ys[j] + .01, f'{tag}: notehead height order {a[i]} vs {a[j]}')
            check(st['cur'] == 0 and st['btn']['chk'] is False and all(r['dis'] for r in st['rungs']), f'{tag}: full: no gold place, rungs disabled, Check enabled')
            # undo / redo / clear
            await pg.click('[data-hist="ear:u"]'); st = await pg.evaluate(STATE)
            check(sol(st) == a[:n - 1] and st['slots'] == 1 and st['cur'] == 1, f'{tag}: undo redraws')
            await pg.click('[data-hist="ear:r"]'); st = await pg.evaluate(STATE)
            check(sol(st) == a, f'{tag}: redo redraws')
            await pg.click('[data-earclr]'); st = await pg.evaluate(STATE)
            check(sol(st) == [a[0]] and st['slots'] == n - 1 and not st['btn']['chk'] is False, f'{tag}: clear leaves the given note')
            for i in range(1, n): await pg.click(f'.earstep[data-earsol="{a[i]}"]')
            if seed == 3:
                await pg.check('#earLet'); st = await pg.evaluate(STATE)
                check(all(r['sm'] for r in st['rungs']) and sol(st) == a, f'{tag}: letter names toggle shows letters, stave intact')
                await pg.uncheck('#earLet')
            # playback during the question must not light anything (it would give the answer away)
            await pg.evaluate("earPlay('nokey')"); await pg.wait_for_timeout(900)
            check(await pg.evaluate("document.querySelectorAll('#earMain .now').length") == 0, f'{tag}: no follow highlight before the reveal')
            await pg.evaluate("stopAll()")
            # reveal correct
            await pg.click('[data-earchk]'); st = await pg.evaluate(STATE)
            check(st['staves'] == 1 and st['stripCls'].endswith('ok') and 'Correct' in st['strip'] and 'Every note right' in st['strip'], f'{tag}: correct -> one stave, green strip')
            check(st['listen'] and not any(r['dis'] for r in st['rungs']), f'{tag}: reveal ladder lit and listen-only')
            check(f'The melody: {" ".join(a)}.' == st['aria'], f'{tag}: frame aria-label {st["aria"]}')
            check(sol(st) == a, f'{tag}: reveal solfa')
            lg = await pg.evaluate("""()=>{const svg=document.querySelector('#earMel svg'),k=svg.getBoundingClientRect().width/svg.viewBox.baseVal.width;
              const L=[...svg.querySelectorAll('.vf-stavenote > path')].map(p=>[p.getAttribute('stroke'),p.getAttribute('stroke-width')*k]);
              const S=svg.querySelector('g.vf-stave>path');return{L,sl:[S.getAttribute('stroke'),S.getAttribute('stroke-width')*k]}}""")
            check(lg['sl'][0] == 'rgba(236,226,200,.45)' and abs(lg['sl'][1] - 1) < .05, f'{tag}: staff lines 1 px at 45%: {lg["sl"]}')
            LEDGERS[0] += len(lg['L'])
            check(all(l[0] == 'rgba(236,226,200,.7)' and abs(l[1] - 1.2) < .05 for l in lg['L']), f'{tag}: ledger lines 70% ivory 1.2 px: {lg["L"][:2]}')
            ans_before = await pg.evaluate("JSON.stringify([EAR.ans,EAR.res,EAR.st.mel])")
            await pg.evaluate("__T.length=0"); r = a[2]
            await pg.click(f'.earstep[data-earsol="{r}"]')
            exp = await pg.evaluate("(r)=>eSolMidi(eSolParse(r),EAR.q.key)", r)
            check(await pg.evaluate("__T.slice()") == [exp], f'{tag}: listen-only rung plays {exp}')
            check(await pg.evaluate("JSON.stringify([EAR.ans,EAR.res,EAR.st.mel])") == ans_before, f'{tag}: listen-only rung does not change the answer')
            # reveal wrong: two notes differ
            await pg.evaluate(NEWQ, [lvl, seed])
            wrong = await pg.evaluate("""()=>{const q=EAR.q,lad=[];for(let k=q.range[1];k>=q.range[0];k--)lad.push(eSolTxt(eSolOf(k,q.mode)));
              const ans=q.a.slice(1);const idx=[0,ans.length-1];for(const i of idx){const c=lad.indexOf(ans[i]);ans[i]=lad[c>0?c-1:c+1]}return ans}""")
            for x in wrong: await pg.click(f'.earstep[data-earsol="{x}"]')
            await pg.click('[data-earchk]'); st = await pg.evaluate(STATE)
            nd = sum(1 for i, x in enumerate(wrong) if x != a[i + 1])
            check(st['staves'] == 2 and st['labels'][:2] == ['YOU WROTE', 'THE MELODY'] and st['stripCls'].endswith('bad'), f'{tag}: wrong -> two labelled staves, red strip ({st["staves"]}, {st["labels"]})')
            check(st['strip'].startswith('Not this time') and ('After note' in st['strip'] or 'You heard the shape' in st['strip']), f'{tag}: wrong strip text (0.48: the teaching sentence): {st["strip"]}')
            check(sol(st, '0') == [a[0]] + wrong and sol(st, '1') == a, f'{tag}: both rows solfa')
            red = [s['i'] for s in st['rows']['0']['sol'] if s['fill'] == '#d15e5d']
            check(red == [i + 1 for i, x in enumerate(wrong) if x != a[i + 1]], f'{tag}: only wrong notes red ({red})')
            check(not any(s['fill'] == '#d15e5d' for s in st['rows']['1']['sol']), f'{tag}: the melody row has no red')
            r0 = sorted(st['rows']['0']['notes'], key=lambda x: x['i']); r1 = sorted(st['rows']['1']['notes'], key=lambda x: x['i'])
            check(all(abs(r0[i]['cx'] - r1[i]['cx']) < .5 for i in range(n)), f'{tag}: two staves share every note x')
            check(abs(st['ss'] - want_ss) < .1 and st['docW'] <= st['vw'] and st['frameR'] <= st['cardR'] + .5, f'{tag}: wrong reveal size and no overflow')
            # show me
            await pg.evaluate(NEWQ, [lvl, seed]); await pg.click('[data-earshow]'); st = await pg.evaluate(STATE)
            check(st['staves'] == 1 and st['strip'].startswith('Shown') and sol(st) == a, f'{tag}: show me -> one stave')
    # playback follow at the reveal (once per width, level 1)
    for rm in (False, True):
        await pg.emulate_media(reduced_motion='reduce' if rm else 'no-preference')
        q = await pg.evaluate(NEWQ, [1, 5]); await pg.click('[data-earshow]')
        await pg.evaluate("""()=>{window.__S=[];window.__anim=0;new MutationObserver(()=>{const r=document.querySelector('.earstep.now'),n=document.querySelector('#earMel .vf-stavenote.now'),t=document.querySelector('#earMel text.now');
          const k=(r?r.dataset.earsol:'-')+'|'+(n?n.getAttribute('data-mi'):'-')+'|'+(t?t.getAttribute('data-mi'):'-');if(!__S.length||__S[__S.length-1]!==k)__S.push(k);__anim=Math.max(__anim,document.getAnimations().filter(a=>a.effect&&a.effect.target&&a.effect.target.closest&&a.effect.target.closest('.meldesk')).length)}).observe(document.querySelector('#earMain'),{subtree:true,attributes:true,attributeFilter:['class']})}""")
        await pg.evaluate("window.c2Tone=()=>{};earPlay('nokey')"); await pg.wait_for_timeout(5200)
        seq = [s for s in await pg.evaluate("__S") if s != '-|-|-']
        want = [f'{x}|{i}|{i}' for i, x in enumerate(q['a'])]
        check(seq == want, f'{w}px reduced={rm}: follow sequence {seq} vs {want}')
        check(await pg.evaluate("__anim") == 0, f'{w}px reduced={rm}: no animation running during follow')
        await pg.evaluate("stopAll();earMelNowClear()")
    await pg.emulate_media(reduced_motion='no-preference')
    if w < 500:
        await pg.evaluate(NEWQ, [2, 8]); await pg.evaluate("document.querySelectorAll('.earstep')[3].click()")
        r = await pg.evaluate("""()=>{const s=document.querySelector('.melscore').getBoundingClientRect(),l=document.querySelector('.earlad').getBoundingClientRect();
          const top=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--top'));scrollTo(0,scrollY+l.bottom-300);const s2=document.querySelector('.melscore').getBoundingClientRect();return{above:s.bottom<=l.top+8,top,s2:s2.top}}""")
        await pg.wait_for_timeout(200)
        r2 = await pg.evaluate("document.querySelector('.melscore').getBoundingClientRect().top")
        cover = await pg.evaluate("""()=>{const t=parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--top'));const e=document.elementFromPoint(200,t+2);return !!(e&&e.closest('.melscore'))}""")
        check(cover, f'{w}px: no strip of the ladder shows between the top bar and the pinned stave (FR-20)')
        # FR-19: the result strip is outside the pinned block, between it and the ladder
        await pg.evaluate(NEWQ, [2, 8]); await pg.evaluate("""()=>{const q=EAR.q;EAR.ans=q.a.slice(1).map((x,i)=>i===0?q.a[2]:x);EAR.done=true;EAR.res={ok:false,kind:'miss',given:EAR.ans.slice()};renderEar()}""")
        f19 = await pg.evaluate("""()=>{scrollTo(0,0);const e=document.querySelector('.el-result'),s=document.querySelector('.melscore').getBoundingClientRect(),l=document.querySelector('.earlad').getBoundingClientRect(),r=e.getBoundingClientRect();return{inside:!!e.closest('.melscore'),between:r.top>=s.bottom-8&&r.bottom<=l.top+1,r:[r.top,r.bottom],s:[s.top,s.bottom],l:[l.top]}}""")
        check(not f19['inside'] and f19['between'], f'{w}px: result strip outside the pinned block, between stave and ladder (FR-19) {f19}')
        await pg.evaluate(NEWQ, [2, 8]); await pg.evaluate("document.querySelectorAll('.earstep')[3].click()")
        check(r['above'], f'{w}px: stave above the ladder'); check(r['top'] - .5 <= r2 < r['top'] + 12, f'{w}px: stave pinned under the top bar ({r2} vs --top {r["top"]})')
    else:
        # live resize across 760 px redraws at the phone staff-space
        await pg.evaluate(NEWQ, [2, 8]); await pg.set_viewport_size({'width': 390, 'height': 900}); await pg.wait_for_timeout(500)
        st = await pg.evaluate(STATE); check(abs(st['ss'] - 6.5) < .1 and st['docW'] <= 390, f'resize to 390 redraws at 6.5 px ({st["ss"]:.2f}, doc {st["docW"]})')
        await pg.set_viewport_size({'width': 1440, 'height': 900}); await pg.wait_for_timeout(500)
        st = await pg.evaluate(STATE); check(abs(st['ss'] - 7) < .1, f'resize back redraws at 7 px ({st["ss"]:.2f})')
    check(LEDGERS[0] > 0, f'{w}px: at least one ledger line was exercised')
    check(not errs, f'{w}px page errors: {errs[:3]}')
    await b.close()

async def main():
    async with async_playwright() as p:
        for w in (1440, 390): await run(p, w)
    print(f'{N[0]} checks, {len(FAILS)} failed')
    for f in FAILS[:40]: print('FAIL', f)
    sys.exit(1 if FAILS else 0)
asyncio.run(main())
