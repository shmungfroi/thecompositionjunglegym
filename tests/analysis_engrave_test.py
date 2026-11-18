"""Analysis engraving test (0.47, S-3/S-6, A1-A11, register R1). Self-check written by the Analysis builder.
Run: python3 tests/analysis_engrave_test.py <repo dir>

All ten Analysis scores, every layer on, at 1440 x 900 and 390 x 900 (and 360 x 900, the narrowest common phone):
  A  staff-space: 7.2 px at 1440 (Verovio scale 40), 5.94 px at 390 (scale 33), +-0.15 px, measured on screen
  B  shown 1:1: the SVG is drawn at its engraved pixel size (no stretch), and the engraving matches the viewport
  C  vertical scroll only: nothing in the score box or the page overflows sideways
  D  at least 3 systems fully in view on desktop (or the whole score, if it has fewer)
  E  every overlay label (form, harmony, cadence) inside the frame; the first form label below the pinned section bar
  F  cadence tags: NSW names, two words ("Perfect cadence", ...), one per cadence whose label names one; K. 545 none
  G  no overlay or engraved text overlaps a notehead or another overlay label; overlay text >= 11 px (figures 9 px)
  H  section index beside the score on desktop, chip row on the phone; a jump brings the section's system to the top
     and the pinned bar shows it
  I  R1: Analysis playback. Every scheduled audio source is recorded (start and stop, as in the E6 blind-analysis
     test); each note stops no later than its written length + 150 ms, and every written note is played.
Also: the engraved bars and notes match scores/meta.json (ids), and no page errors.
"""
import sys, asyncio, json, pathlib, re, collections
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

SC = ['chorale', 'ohaupt', 'jesu', 'k331a', 'k331d', 'k545', 'maple', 'entertainer', 'chopin7', 'chopin20']
WIDTHS = {1440: (7.2, ''), 390: (5.94, '.p'), 360: (5.94, '.p')}
NSW = re.compile(r'^(Perfect|Imperfect|Plagal|Interrupted) cadence$')

MEASURE = r"""()=>{const box=document.getElementById('anScore'),svg=box&&box.querySelector('svg');if(!svg)return{err:'no svg'};
 const R=e=>{const r=e.getBoundingClientRect();return{l:r.left,t:r.top,r:r.right,b:r.bottom}};
 const st=svg.querySelector('g.staff'),ls=[...st.querySelectorAll(':scope>path')].map(p=>p.getBoundingClientRect().top+p.getBoundingClientRect().height/2).sort((a,b)=>a-b);
 const gaps=ls.slice(1).map((y,i)=>y-ls[i]);
 const ds=svg.querySelector('svg.definition-scale'),sr=svg.getBoundingClientRect();
 const px=t=>{const fs=parseFloat(t.getAttribute('font-size'));return fs*t.getScreenCTM().a};
 const ov=[...svg.querySelectorAll('text.anov')].map(t=>({cls:t.getAttribute('class'),txt:t.textContent,box:R(t),px:px(t),fig:[...t.querySelectorAll('tspan[font-size]')].map(px)}));
 const vt=[...svg.querySelectorAll('g.tempo text,g.dir text,g.mNum text,g.ending text,g.reh text')].filter(t=>t.textContent.trim()).map(t=>({cls:t.parentNode.getAttribute('class'),txt:t.textContent.trim(),box:R(t),px:Math.max(...[...t.querySelectorAll('tspan[font-size]')].map(px))}));
 const heads=[...svg.querySelectorAll('g.notehead')].map(R);
 const sys=[...svg.querySelectorAll('g.system')].map(R);
 const pin=document.getElementById('anPin'),wrap=document.getElementById('anWrap');
 return{gaps,svgW:sr.width,svgH:sr.height,attrW:svg.width.baseVal.value,vbW:ds.viewBox.baseVal.width,box:R(box),client:{w:box.clientWidth,h:box.clientHeight,sw:box.scrollWidth,sh:box.scrollHeight},
  ox:getComputedStyle(box).overflowX,pageSW:document.documentElement.scrollWidth,innerW:innerWidth,ov,vt,heads,sys,pin:pin?R(pin):null,pinTxt:pin?pin.textContent:'',
  side:wrap.classList.contains('side'),idx:[...document.querySelectorAll('#anIdx button')].map(b=>({txt:b.textContent,box:R(b)})),suf:AN.v&&AN.v.suf,
  bars:[...svg.querySelectorAll('g.measure')].map(g=>g.getAttribute('data-id')),notes:[...svg.querySelectorAll('g.note')].map(g=>g.getAttribute('data-id'))}}"""


def inter(a, b):
    return max(0, min(a['r'], b['r']) - max(a['l'], b['l'])) * max(0, min(a['b'], b['b']) - max(a['t'], b['t']))


async def main():
    fails, count = [], collections.Counter()

    def fail(sec, msg):
        fails.append(f'{sec}: {msg}')

    meta = json.load(open(REPO / 'scores' / 'meta.json'))
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for W, (ss, suf) in WIDTHS.items():
            pg = await b.new_page(viewport={'width': W, 'height': 900})
            errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.add_init_script("""(()=>{window.__N=[];for(const P of [AudioScheduledSourceNode.prototype,AudioBufferSourceNode.prototype]){const st=P.start,sp=P.stop;
              P.start=function(t=0,...a){this.__r={s:t||0,e:Infinity,k:this instanceof AudioBufferSourceNode?'smp':'osc'};__N.push(this.__r);return st.call(this,t,...a)};
              P.stop=function(t=0){if(this.__r)this.__r.e=Math.min(this.__r.e,t);return sp.call(this,t)}}})()""")
            await pg.route('**/*', cjg.make_route(REPO))
            await pg.goto('http://app/index.html')
            await pg.wait_for_timeout(1500)
            await pg.evaluate("document.fonts&&document.fonts.load(\"700 14px 'EB Garamond'\")")
            for k in SC:
                m = meta[k]
                await pg.evaluate(f"location.hash='analysis';AN.tab='score';AN.score='{k}';AN.layers={{harm:true,cad:true,form:true}};room('analysis')")
                await pg.wait_for_function("document.querySelector('#anScore svg')&&document.querySelector('#anScore text.anov, #anScore svg')", timeout=15000)
                await pg.wait_for_timeout(700)
                await pg.evaluate("document.getElementById('anScore').closest('section').scrollIntoView();window.scrollBy(0,-70)")
                await pg.wait_for_timeout(150)
                r = await pg.evaluate(MEASURE)
                tag = f'{k} @{W}'
                count['views'] += 1
                if r.get('err'):
                    fail('A', f'{tag}: {r["err"]}')
                    continue
                # A staff-space
                g = sum(r['gaps']) / len(r['gaps'])
                count['staff-spaces measured'] += 1
                if abs(g - ss) > 0.15:
                    fail('A', f'{tag}: staff-space {g:.2f} px, expected {ss} +-0.15')
                # B 1:1 and the engraving for this viewport
                if abs(r['svgW'] - r['attrW']) > 0.5:
                    fail('B', f'{tag}: drawn {r["svgW"]:.1f} px wide, engraved {r["attrW"]} px (stretched)')
                if r['suf'] != suf:
                    fail('B', f'{tag}: engraving "{r["suf"]}" picked, expected "{suf}"')
                # C vertical scroll only
                if r['client']['sw'] > r['client']['w'] + 0.5 or r['ox'] not in ('hidden', 'clip'):
                    fail('C', f'{tag}: score box scrolls sideways (scrollWidth {r["client"]["sw"]} > {r["client"]["w"]}, overflow-x {r["ox"]})')
                if r['pageSW'] > r['innerW']:
                    fail('C', f'{tag}: page is {r["pageSW"]} px wide in a {r["innerW"]} px viewport')
                if r['svgW'] > r['box']['r'] - r['box']['l'] - 2 * 16 - 2 + 0.5:
                    fail('C', f'{tag}: score {r["svgW"]:.0f} px does not fit the frame')
                # D systems in view (desktop)
                if W >= 900:
                    top, bot = r['pin']['b'] if r['pin'] else r['box']['t'], r['box']['t'] + r['client']['h']
                    full = sum(1 for s in r['sys'] if s['t'] >= top - 1 and s['b'] <= bot + 1)
                    need = min(3, len(r['sys']))
                    count['systems in view checked'] += 1
                    if full < need:
                        fail('D', f'{tag}: {full} systems fully in view, need {need}')
                # E labels inside the frame
                fl, fr = r['box']['l'] + 1, r['box']['r'] - 1
                for o in r['ov']:
                    count['overlay labels'] += 1
                    bx = o['box']
                    if bx['l'] < fl or bx['r'] > fr:
                        fail('E', f'{tag}: label "{o["txt"]}" outside the frame horizontally ({bx["l"]:.0f}-{bx["r"]:.0f} vs {fl:.0f}-{fr:.0f})')
                    if bx['t'] < r['box']['t'] + 1:
                        fail('E', f'{tag}: label "{o["txt"]}" above the frame')
                forms = [o for o in r['ov'] if 'anlab' in o['cls']]
                if m['sections'] and not forms:
                    fail('E', f'{tag}: no form labels drawn')
                if forms and r['pin']:
                    f0 = min(forms, key=lambda o: o['box']['t'])
                    if f0['box']['t'] < r['pin']['b'] - 0.5:
                        fail('E', f'{tag}: first form label "{f0["txt"]}" is under the pinned bar')
                # F cadence tags
                tags = [o for o in r['ov'] if 'ancad' in o['cls']]
                want = sum(1 for c in m['cads'] if re.match(r'^(Perfect|Imperfect|Plagal|Interrupted)\b', c['t']))
                for o in tags:
                    count['cadence tags'] += 1
                    if not NSW.match(o['txt']):
                        fail('F', f'{tag}: cadence tag "{o["txt"]}" is not a two-word NSW name')
                if len(tags) != want:
                    fail('F', f'{tag}: {len(tags)} cadence tags, expected {want}')
                if k == 'k545' and tags:
                    fail('F', f'{tag}: K. 545 has no cadence data but shows tags')
                # G overlaps and sizes
                texts = r['ov'] + r['vt']
                for o in texts:
                    for h in r['heads']:
                        if inter(o['box'], h) > 1.5:
                            fail('G', f'{tag}: text "{o["txt"]}" overlaps a notehead')
                            break
                    count['text-notehead pairs checked'] += len(r['heads'])
                for i, a in enumerate(r['ov']):
                    for c in r['ov'][i + 1:]:
                        if inter(a['box'], c['box']) > 2:
                            fail('G', f'{tag}: "{a["txt"]}" overlaps "{c["txt"]}"')
                for o in r['ov']:
                    if o['px'] < 11 - 0.05:
                        fail('G', f'{tag}: "{o["txt"]}" at {o["px"]:.1f} px (< 11)')
                    for f in o['fig']:
                        if abs(f - 9) > 0.1:
                            fail('G', f'{tag}: figure in "{o["txt"]}" at {f:.1f} px (expected 9)')
                for o in r['vt']:
                    if o['px'] < 11 - 0.05:
                        fail('G', f'{tag}: engraved text "{o["txt"]}" ({o["cls"]}) at {o["px"]:.1f} px (< 11)')
                # ids match meta.json
                if r['bars'] != [x[1] for x in m['measures']]:
                    fail('ids', f'{tag}: bar ids differ from meta.json')
                need_ids = {x['id'] for x in m['labels']} | {x['id'] for x in m['cads']}
                if need_ids - set(r['notes']):
                    fail('ids', f'{tag}: {len(need_ids - set(r["notes"]))} overlay anchors missing')
                # H index and jump
                if (W >= 900) != r['side']:
                    fail('H', f'{tag}: index {"beside" if r["side"] else "above"} the score')
                n_idx = len(m['sections']) or len(m['cads'])
                if len(r['idx']) != n_idx:
                    fail('H', f'{tag}: {len(r["idx"])} index entries, expected {n_idx}')
                for it in r['idx']:
                    if it['box']['b'] - it['box']['t'] < 32 - 0.5:
                        fail('H', f'{tag}: index entry "{it["txt"]}" is {it["box"]["b"]-it["box"]["t"]:.0f} px tall (< 32)')
                if n_idx > 1:
                    j = n_idx - 1
                    await pg.evaluate(f"document.querySelector('#anIdx [data-anjump=\"{j}\"]').click()")
                    await pg.wait_for_timeout(1500)
                    await pg.wait_for_function("(()=>{const b=document.getElementById('anScore');const v=b.scrollTop;return new Promise(r=>setTimeout(()=>r(b.scrollTop===v),300))})()", timeout=8000)
                    jr = await pg.evaluate("""(j)=>{const m=AN.meta[AN.score],it=anIndex(m)[j],box=document.getElementById('anScore'),g=box.querySelector(`[data-id="${m.measures[it.mi][1]}"]`),s=g.closest('g.system'),
                        br=box.getBoundingClientRect(),sr=s.getBoundingClientRect(),pin=document.getElementById('anPin');return{rel:sr.top-br.top,h:box.clientHeight,pin:pin.textContent,lab:it.lab,atEnd:box.scrollTop+box.clientHeight>=box.scrollHeight-2}}""", j)
                    count['index jumps'] += 1
                    if not (jr['rel'] <= jr['h'] / 3 or jr['atEnd']):
                        fail('H', f'{tag}: jump to "{jr["lab"]}" left its system at {jr["rel"]:.0f} px of {jr["h"]}')
                    if jr['lab'] not in jr['pin'] and not jr['atEnd']:
                        fail('H', f'{tag}: pinned bar shows "{jr["pin"]}" after jumping to "{jr["lab"]}"')
                # I R1 playback note lengths (desktop pass only; the audio path is the same at every width)
                if W == 1440:
                    if not await pg.evaluate("!!(SBUF.piano&&Object.keys(SBUF.piano).length)"):
                        await pg.evaluate("ac();loadSamples('piano')")
                        await pg.wait_for_timeout(3000)
                    res = await pg.evaluate("""()=>{stopAll();__N.length=0;AN.speed=1;anPlay();const n=__N.map(x=>({s:x.s,e:x.e,k:x.k}));stopAll();return n}""")
                    # a sampled note is one buffer source; a note outside the sample range falls back to the synth (two oscillators, same start and stop)
                    nodes = [x for x in res if x['k'] == 'smp']
                    oc = collections.Counter((x['s'], x['e']) for x in res if x['k'] == 'osc')
                    for (s0, e0), n in oc.items():
                        nodes += [{'s': s0, 'e': e0, 'k': 'osc'}] * (n // 2)
                        count['R1 synth-fallback notes'] += n // 2
                    t0 = min(x['s'] for x in nodes)
                    written = collections.defaultdict(list)
                    for ms, pp, d in m['events']:
                        written[ms].append(d)
                    onsets = sorted(written)
                    played = collections.defaultdict(int)
                    for x in nodes:
                        rel = (x['s'] - t0) * 1000 + onsets[0]
                        o = min(onsets, key=lambda q: abs(q - rel))
                        if abs(o - rel) > 3:
                            fail('I', f'{tag}: a note starts at {rel:.0f} ms where the score has none')
                            continue
                        played[o] += 1
                        count['R1 notes timed'] += 1
                        if x['e'] == float('inf'):
                            fail('I', f'{tag}: a note at {o} ms has no release')
                        elif (x['e'] - x['s']) > max(written[o]) / 1000 + 0.15 + 1e-6:
                            fail('I', f'{tag}: a note at {o} ms sounds {(x["e"]-x["s"]):.2f} s; written {max(written[o])/1000:.2f} s')
                    if sum(played.values()) != len(m['events']):
                        fail('I', f'{tag}: {sum(played.values())} notes played, {len(m["events"])} written')
                await pg.evaluate("stopAll()")
            if errs:
                fail('errors', f'@{W}: ' + '; '.join(errs[:5]))
            await pg.close()
        await b.close()
    print(json.dumps({'counts': count, 'failures': len(fails)}, indent=1))
    for f in fails[:80]:
        print('FAIL', f)
    if len(fails) > 80:
        print(f'... and {len(fails) - 80} more')
    sys.exit(1 if fails else 0)

asyncio.run(main())
