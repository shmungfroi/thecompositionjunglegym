"""Australian and US terms (0.48 R6, Justin's rule).
Run: python3 tests/terms_test.py <repo dir>

One shared term list in the page (TERMS) is checked against this file's own copy of the rule, then every room, climb, form, Analysis
score and Ear Lab drill is opened at Stages 4, 5 and 6, every visible button in the main panel is clicked once (so answer feedback
appears), and after every click the page is scanned:

  T1  the term list: perfect = authentic, imperfect = half, plagal, interrupted = deceptive; crotchet, quaver, minim, semibreve,
      semiquaver = quarter, eighth, half, whole, sixteenth note; bar = measure; stave = staff; tone = whole step; semitone = half step;
      and the one label "Perfect cadence, less final (US: imperfect authentic)" with its one-line note.
  T2  no US term on its own: with every "(US: ...)" bracket and the one-line note removed, no rendered text contains authentic,
      half cadence, deceptive, quarter/eighth/sixteenth/half/whole note, whole/half step, staff or measure (as a noun).
  T3  clutter rule: answer buttons, chips and options show the Australian term only (no "(US") and carry the US term in a title;
      headings that name a term carry both; the first mention of each term in each room carries both; scores (svg) carry the
      Australian term only.
  T4  "imperfect authentic" always comes with the note "US 'imperfect authentic' is still a perfect cadence; the Australian
      imperfect cadence is the US half cadence."; "Weaker perfect cadence" is gone.
  T6  (fix round) rests pair as units (crotchet rest = quarter rest); no pairing in "12-bar", "8-bar" or "bar by bar"; no back-to-back or
      nested brackets; one bracket per term per list (and per checker list); button hovers are rebuilt from the text, never stacked;
      the Gym cadence reader carries its bracket; "Perfect cadence, less final" is lower case in the middle of a sentence.
  T5  the pass is idempotent and every added bracket or hover is at least 11 px.
"""
import sys, os, asyncio, json, pathlib, re, collections
REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright

FAIL = collections.defaultdict(list)
COUNT = collections.Counter()

# this file's own copy of the rule (au, us)
RULE = {'iac': ('perfect cadence, less final', 'imperfect authentic'),
        'perfect': ('perfect cadence', 'authentic cadence'), 'imperfect': ('imperfect cadence', 'half cadence'),
        'plagal': ('plagal cadence', None), 'interrupted': ('interrupted cadence', 'deceptive cadence'),
        'crotchet': ('crotchet', 'quarter note'), 'quaver': ('quaver', 'eighth note'), 'minim': ('minim', 'half note'),
        'semibreve': ('semibreve', 'whole note'), 'semiquaver': ('semiquaver', 'sixteenth note'),
        'crest': ('crotchet rest', 'quarter rest'), 'qrest': ('quaver rest', 'eighth rest'), 'mrest': ('minim rest', 'half rest'),
        'sbrest': ('semibreve rest', 'whole rest'), 'sqrest': ('semiquaver rest', 'sixteenth rest'),
        'bar': ('bar', 'measure'), 'stave': ('stave', 'staff'), 'tone': ('tone', 'whole step'), 'semitone': ('semitone', 'half step')}
NOTE = "US 'imperfect authentic' is still a perfect cadence; the Australian imperfect cadence is the US half cadence."
IAC = 'Perfect cadence, less final (US: imperfect authentic)'


def fail(sec, msg):
    FAIL[sec].append(msg)


def ok(sec, label):
    COUNT[f'{sec}: {label}'] += 1


SC = ['chorale', 'ohaupt', 'jesu', 'k331a', 'k331d', 'k545', 'maple', 'entertainer', 'chopin7', 'chopin20']
FORMS = ['phrase', 'blues12', 'jazzblues', 'minblues', 'rhythm', 'rag', 'rondo', 'tv', 'sonata', 'sonrondo']


def views():
    V = []
    for r in ['seed', 'keys', 'voice', 'oracle', 'climbs', 'forms', 'ear']:
        V.append((r, f"location.hash='{r}'"))
    V.append(('gym', "location.hash='gym';if(!P.length){for(const r of ['I','vi','ii','V','I','IV','V7','I'])document.querySelector(`[data-add=\"${r}\"]`)?.click()}"))
    for t in ['scales', 'circle', 'intervals']:
        V.append((f'keys/{t}', f"location.hash='keys';KS.tab='{t}';room('keys');renderKeysRoom()"))
    for k in range(1, 14):
        V.append((f'climbs/{k}', f"location.hash='climbs/{k}'"))
    for f in FORMS:
        V.append((f'forms/{f}', f"location.hash='forms/{f}'"))
    for s in SC:
        V.append((f'analysis/{s}', f"location.hash='analysis';AN.tab='score';AN.score='{s}';room('analysis')"))
    for d in ['metre', 'rhy', 'qual', 'cad', 'bass', 'mel', 'blind']:
        V.append((f'ear/{d}', f"location.hash='ear';EAR.drill='{d}';room('ear')"))
    return V


SKIP = "[data-clback],[data-earreset],[data-export],[data-import],[download],[data-del],[data-bin],[data-wipe],#jExport,#jImport,input[type=file]"

# page side: install the checker, run it after every click; violations are collected in window.__TV
CHK_JS = r"""(RULE)=>{window.__TV=new Map();window.__TN={scans:0,abbr:0,buttons:0,headings:0,scopes:0,svg:0};
 const US=/\b(authentic|half[- ]cadence|deceptive|(?:quarter|eighth|sixteenth|half|whole) (?:notes?|rests?)|quarters|eighths|sixteenths|whole steps?|half steps?|staffs?|measures?)\b/i;
 const add=(k,m)=>{const key=k+'|'+m;if(!window.__TV.has(key)&&window.__TV.size<200)window.__TV.set(key,1)};
 const strip=t=>t.replace(/\(US: [^)]*\)/g,' ').replace(/; US: [^)]*\)/g,')').replace(/US 'imperfect authentic' is still a perfect cadence; the Australian imperfect cadence is the US half cadence\./g,' ')
   .replace(/ = (?:US )?[A-Za-z ]*cadence/g,' ').replace(/measure every interval/g,' ').replace(/\s+/g,' ');
 const bracketed=a=>a.dataset.lit==='1'||(a.nextElementSibling&&a.nextElementSibling.classList.contains('tmus'))||!!a.closest('[data-notm]');
 window.__chk=function(where){termPass();const M=document.querySelector('main')||document.body;window.__TN.scans++;
  // T2: no US term on its own (rendered text outside scores, and every title that is not a US hover)
  const tw=document.createTreeWalker(M,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement&&n.parentElement.closest('svg,script,style,textarea')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
  let txt='',n;while((n=tw.nextNode()))txt+=n.nodeValue;
  const t=strip(txt),mm=US.exec(t);if(mm)add('T2',where+': "'+t.slice(Math.max(0,mm.index-50),mm.index+40)+'"');
  M.querySelectorAll('[title]').forEach(e=>{const ti=e.getAttribute('title').replace(/(^|\s*·\s*)US: [^·]*/g,' ');if(US.test(strip(ti)))add('T2',where+': title "'+e.getAttribute('title')+'"')});
  // T3 scores: the Australian term only inside svg
  M.querySelectorAll('svg').forEach(sv=>{const s=sv.textContent;window.__TN.svg++;if(/\(US/.test(s)||US.test(s.replace(/staff-space/g,'')))add('T3',where+': score text has a US term: "'+s.slice(0,80)+'"')});
  // T3 buttons, chips, options: the Australian term only; the US term in a title
  M.querySelectorAll('button,.chip,option,.pill,.fbar>small').forEach(b=>{const s=b.textContent;window.__TN.buttons++;
   if(/\(US/.test(s)&&!b.closest('[data-notm]'))add('T3',where+': button/chip shows a bracket: "'+s.trim().slice(0,70)+'"');
   for(const k in RULE){const [au,us]=RULE[k];if(!us)continue;let sx=k==='perfect'?s.replace(/perfect cadences?, less final/ig,''):s;if(!/rest$/.test(k))sx=sx.replace(/(crotchet|quaver|minim|semibreve|semiquaver) rests?/ig,'');
    if(!new RegExp('(?<![A-Za-z])'+(k==='tone'?'whole tone':au)+'s?(?![A-Za-z])'+(k==='bar'?'(?![- ]?(?:lines?|chart|graph))':k==='tone'?'(?![- ]scales?)':''),'i').test(sx)||(k==='bar'&&/(?<![A-Za-z])bars?(?![A-Za-z])/i.test(sx.replace(/\w+-bars?\b|\bby bar\b|\bbar by\b/gi,''))===false))continue;
    const el=b.closest('button,.chip,option,.pill,.fbar>small')||b,tl=el.getAttribute('title')||'';
    if(!tl.includes(us))add('T3',where+': "'+s.trim().slice(0,60)+'" has no US hover for '+au)}});
  // T3 headings: the first mention of a term in a heading carries both
  M.querySelectorAll('h1,h2,h3,h4,h5,h6,summary,th').forEach(h=>{const seen=new Set();h.querySelectorAll('abbr.tm').forEach(a=>{if(a.closest('button,.chip')||seen.has(a.dataset.k))return;seen.add(a.dataset.k);window.__TN.headings++;
    if(!bracketed(a))add('T3',where+': heading names "'+a.textContent+'" with no US bracket: "'+h.textContent.trim().slice(0,70)+'"')})});
  // T3 first mention of each term in each room (each open climb) carries both
  const sc=new Map();M.querySelectorAll('abbr.tm').forEach(a=>{if(a.closest('button,.chip'))return;const s=a.closest('#climbDetail,.room')||M;let m=sc.get(s);if(!m)sc.set(s,m=new Map());if(!m.has(a.dataset.k))m.set(a.dataset.k,a)});
  sc.forEach(m=>m.forEach(a=>{window.__TN.scopes++;if(!bracketed(a))add('T3',where+': first mention of "'+a.textContent+'" in the room has no US bracket: "'+(a.parentElement.textContent||'').trim().slice(0,70)+'"')}));
  // T4: imperfect authentic always with the note; Weaker perfect cadence is gone
  if(/Weaker perfect/i.test(M.textContent))add('T4',where+': "Weaker perfect cadence" is still shown');
  const w2=document.createTreeWalker(M,NodeFilter.SHOW_TEXT);let x;while((x=w2.nextNode())){if(/imperfect authentic/i.test(x.nodeValue)&&!x.parentElement.closest('[data-notm]')){
    const c=x.parentElement.closest('.iss,td,li,p,.card,div')||M;if(!/is still a perfect cadence/.test(c.textContent))add('T4',where+': "imperfect authentic" without the note: "'+c.textContent.trim().slice(0,90)+'"')}}
  // T6 (fix round)
  M.querySelectorAll('button,.chip,option,.pill,.fbar>small').forEach(b=>{if(b.closest('[data-notm]'))return;const tl=b.getAttribute('title')||'';
   if((tl.match(/US:/g)||[]).length>1)add('T6',where+': stacked hover "'+tl+'" on "'+b.textContent.trim().slice(0,40)+'"');
   if(b.dataset.us!==undefined){const L=[];TM_RX.lastIndex=0;let m;while((m=TM_RX.exec(b.textContent))){const k=Object.keys(m.groups).find(g=>m.groups[g]!==undefined),u=termUS(k,/s$/i.test(m[0]));if(u&&!L.includes(u))L.push(u)}
    if(!tl.endsWith('US: '+L.join(', ')))add('T6',where+': hover "'+tl+'" is not rebuilt from the text "'+b.textContent.trim().slice(0,40)+'" ('+L.join(', ')+')')}});
  M.querySelectorAll('abbr.tm').forEach(a=>{const k=a.dataset.k,prev=a.previousSibling&&a.previousSibling.nodeType===3?a.previousSibling.nodeValue:'',nxt=a.nextSibling&&a.nextSibling.nodeType===3?a.nextSibling.nodeValue:'';
   if(k==='bar'&&(/-$/.test(prev)||/\bby $/i.test(prev)||/^ by bar/i.test(nxt)))add('T6',where+': "bar" is paired inside a compound or idiom: "'+(a.parentElement.textContent||'').trim().slice(0,70)+'"');
   if((k==='crotchet'||k==='quaver'||k==='minim'||k==='semibreve'||k==='semiquaver')&&/^ rests?\b/.test(nxt))add('T6',where+': "'+a.textContent+' rest" is split into two terms');
   if(k==='tone'&&/^(?:[- ]?(?:colour|color)|[- ]scale)/i.test(nxt))add('T6',where+': "tone" paired inside "'+a.textContent+nxt.slice(0,10)+'"')});
  M.querySelectorAll('.tmus').forEach(u=>{const a=u.previousSibling,b=u.closest('p,li,td,th,dd,dt,h1,h2,h3,h4,h5,h6,summary,div,section,label,figcaption,caption')||M;
   let y=u,after='';while(y&&!y.nextSibling&&y.parentElement&&y.parentElement!==b)y=y.parentElement;if(y&&y.nextSibling)after=(y.nextSibling.textContent||'').slice(0,12);
   if(/^\s*\((?!US)/.test(after))add('T6',where+': back-to-back brackets: "'+(u.parentElement.textContent||'').trim().slice(0,80)+'"');
   try{const r=document.createRange();r.setStart(b,0);r.setEndBefore(u);const lead=r.toString().slice(-160);if(/\([^()]*$/.test(lead)&&!/^;/.test(u.textContent))add('T6',where+': bracket inside a bracket: "'+(lead+u.textContent).trim().slice(-80)+'"')}catch(e){}});
  const per=new Map();M.querySelectorAll('.tmus').forEach(u=>{const a=u.previousElementSibling;if(!a||!a.dataset)return;const L=u.closest('ul,ol')||(u.closest('.iss')&&u.closest('.iss').parentElement);if(!L)return;
   const key=a.dataset.k;let m=per.get(L);if(!m)per.set(L,m=new Set());if(m.has(key))add('T6',where+': "'+a.textContent+'" is bracketed twice in one list: "'+L.textContent.trim().slice(0,60)+'"');m.add(key)});
  if(/[a-z,;] Perfect cadence, less final/.test(M.textContent))add('T6',where+': capital P in the middle of a sentence: "'+(M.textContent.match(/.{25}[a-z,;] Perfect cadence, less final/)||[''])[0]+'"');
  const cd=document.getElementById('cad');if(cd&&cd.offsetParent&&/(?<![A-Za-z])(perfect|imperfect|plagal|interrupted) cadence/i.test(cd.textContent)&&!/plagal cadence/i.test(cd.textContent.slice(0,40))&&!cd.querySelector('.tmus,abbr[data-lit]'))add('T6',where+': the Gym cadence reader has no US bracket: "'+cd.textContent.slice(0,80)+'"');
  // T5: size
  document.querySelectorAll('abbr.tm,.tmus').forEach(e=>{if(!e.offsetParent)return;const px=parseFloat(getComputedStyle(e).fontSize);if(px<11)add('T5',where+': '+e.className+' is '+px+' px: "'+e.textContent+'"')});
  window.__TN.abbr+=document.querySelectorAll('abbr.tm').length}}"""


async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        cur = ['load']
        pg.on('pageerror', lambda e: errs.append(f'{cur[0]}: {str(e)[:160]} @ {(getattr(e, "stack", "") or "").strip().splitlines()[1:3]}'))
        pg.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html')
        await pg.wait_for_timeout(1500)

        # ---- T1: the shared term list
        T = await pg.evaluate("()=>({terms:TERMS.map(t=>[t.k,t.au,t.us]),iac:TERM_IAC,note:TERM_NOTE})")
        got = {k: (a, u) for k, a, u in T['terms']}
        if got != RULE:
            fail('T1', f'term list differs from the rule: {got}')
        else:
            ok('T1', 'term list matches the rule')
        if T['iac'] != IAC:
            fail('T1', f"label '{T['iac']}'")
        if T['note'] != NOTE:
            fail('T1', f"note '{T['note']}'")
        src = (REPO / 'index.html').read_text(encoding='utf-8')
        if re.search(r'weaker perfect', src, re.I):
            fail('T4', 'index.html still contains "weaker perfect"')
        # hand-checks of the helpers
        H = await pg.evaluate("""()=>({d:termDual('crotchet'),dp:termDual('semitone',true),t:termTip('perfect'),n:termDual('plagal'),b:termDual('bar',true),s:termDual('stave',true)})""")
        exp = {'d': 'crotchet (US: quarter note)', 'dp': 'semitones (US: half steps)', 't': 'US: authentic cadence', 'n': 'plagal cadence',
               'b': 'bars (US: measures)', 's': 'staves (US: staffs)'}
        if H != exp:
            fail('T1', f'helpers: {H}')
        else:
            ok('T1', 'termDual / termTip')

        # ---- T2-T5: every view, every button
        await pg.evaluate(CHK_JS, RULE)
        for stage in [int(x) for x in os.environ.get('TERMS_STAGES', '4,5,6').split(',')]:
            await pg.evaluate(f"document.querySelector('#lvl button[data-l=\"{stage}\"]').click()")
            await pg.wait_for_timeout(200)
            for name, js in views():
                where = f'S{stage} {name}'
                cur[0] = where
                await pg.evaluate(js)
                await pg.wait_for_timeout(900 if name.startswith('analysis') else 350)
                await pg.evaluate(f"__chk({json.dumps(where)})")
                COUNT['views scanned'] += 1
                nb = await pg.evaluate(f"""(skip)=>[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&!b.disabled&&!b.matches(skip)).length""", SKIP)
                for i in range(min(nb, 40 if stage == 6 else 10)):
                    clicked = await pg.evaluate("""([i,skip])=>{const bs=[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&!b.disabled&&!b.matches(skip));const b=bs[i];if(!b)return false;b.click();return true}""", [i, SKIP])
                    if not clicked:
                        break
                    await pg.evaluate("stopAll()")
                    await pg.wait_for_timeout(40)
                    await pg.evaluate(f"__chk({json.dumps(where)})")
                    COUNT['clicks scanned'] += 1
                    # a click may navigate away: reopen the view
                    await pg.evaluate(js)
                    await pg.wait_for_timeout(120)
        tv = await pg.evaluate("()=>[[...window.__TV.keys()],window.__TN]")
        for k in tv[0]:
            sec, _, msg = k.partition('|')
            fail(sec, msg)
        for k, v in tv[1].items():
            COUNT[f'page scan: {k}'] = v
        # ---- T5 idempotence: a second pass changes nothing
        same = await pg.evaluate("""()=>{termPass();const a=document.querySelector('main').innerHTML;termPass();termPass();return a===document.querySelector('main').innerHTML}""")
        if not same:
            fail('T5', 'termPass() is not idempotent')
        else:
            ok('T5', 'termPass idempotent')
        # ---- the automatic pass: text drawn after load gets its brackets without a call
        auto = await pg.evaluate("""async()=>{const d=document.createElement('div');d.id='tmauto';
            d.innerHTML='<p>A crotchet then a quaver. A crotchet again.</p><button>minim</button><button>eighth: quavers</button>'
            +'<p id="a1">Hold a crotchet rest, then a quaver rest.</p><p id="a2">A 12-bar blues, an 8- to 16-bar phrase, played bar by bar.</p>'
            +'<p id="a3">Half the beat (quavers) and (the tempo is the dotted crotchet).</p>'
            +'<p id="a4">Go up a tone. It is a tone apart, a tone below home, or (a tone).</p><p id="a5">A steady tone, a chord tone, tone colour, the tone of voice, a whole-tone scale.</p>'
            +'<ul id="a6"><li>A dissonant minim.</li><li>Another minim.</li><li>A crotchet.</li></ul>';
            document.querySelector('main').appendChild(d);
            await new Promise(r=>setTimeout(r,400));
            const b2=d.querySelectorAll('button');const o={t:d.querySelector('p').textContent,bt:d.querySelector('button').title,b2:b2[1].title};
            for(const id of ['a1','a2','a3','a4','a5','a6']){const e=d.querySelector('#'+id);o[id]=e.textContent;o[id+'k']=[...e.querySelectorAll('abbr.tm')].map(a=>a.dataset.k+':'+a.textContent)}
            // the hover is rebuilt from the text: change the text, the title follows, and nothing stacks
            b2[1].textContent='crotchets';await new Promise(r=>setTimeout(r,300));o.b3=b2[1].title;
            b2[1].textContent='plain';await new Promise(r=>setTimeout(r,300));o.b4=b2[1].title||'(none)';
            d.remove();return o}""")
        exp = {'t': 'A crotchet (US: quarter note) then a quaver (US: eighth note). A crotchet again.', 'bt': 'US: half note', 'b2': 'US: eighth notes',
               'a1': 'Hold a crotchet rest (US: quarter rest), then a quaver rest (US: eighth rest).', 'a1k': ['crest:crotchet rest', 'qrest:quaver rest'],
               'a2': 'A 12-bar blues, an 8- to 16-bar phrase, played bar by bar.', 'a2k': [],
               'a3': 'Half the beat (quavers; US: eighth notes) and (the tempo is the dotted crotchet; US: quarter note).', 'a3k': ['quaver:quavers', 'crotchet:crotchet'],
               'a4': 'Go up a tone (US: whole step). It is a tone apart, a tone below home, or (a tone).', 'a4k': ['tone:tone'] * 4,
               'a5': 'A steady tone, a chord tone, tone colour, the tone of voice, a whole-tone scale.', 'a5k': [],
               'b3': 'US: quarter notes', 'b4': '(none)'}
        bad = {k: (auto.get(k), v) for k, v in exp.items() if auto.get(k) != v and True}
        if bad:
            fail('T6', f'automatic pass: {bad}')
        else:
            ok('T6', 'rests as units, no pairing in N-bar / bar by bar, merged parenthetical brackets, hover rebuilt from the text')
        ok('T6', "bare interval 'tone' is paired; sound, chord tone, tone colour, whole-tone scale are not")
        if auto['a6'].count('(US:') != 2 or auto['a6'].count('US: half note') != 1:
            fail('T6', f"one bracket per term per list: {auto['a6']}")
        else:
            ok('T6', 'one bracket per term per list')
        if auto['t'] != exp['t'] or auto['bt'] != 'US: half note':
            fail('T3', f'automatic pass: {auto}')
        else:
            ok('T3', 'text drawn after load is bracketed automatically (first mention per block, hover on buttons)')
        if errs:
            fail('X', f'page errors: {errs[:5]}')
        await b.close()
    report = {'counts': dict(sorted(COUNT.items())), 'failures': {k: v[:30] for k, v in FAIL.items()},
              'n_failures': sum(len(v) for v in FAIL.values())}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)


if __name__ == '__main__':
    asyncio.run(main())
