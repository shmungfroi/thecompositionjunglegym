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
  T5  the pass is idempotent and every added bracket or hover is at least 11 px.
  T6  (0.48 R6 fix round, the independent check IC_R6) on every scan:
      H1  every term in prose and feedback (outside buttons, chips, options and scores) is marked, so the Gym cadence reader
          (#cad) carries its brackets; no hover names a US term that the element's CURRENT text does not contain (stale or
          piled-up hovers), and every term on a button has its hover in the right form (plural, rest);
      H2  no bracket or hover on "bar" in an N-bar compound (12-bar blues, 8-bar phrase, 8- to 16-bar) or in "bar by bar";
      M1  the bare interval "a tone" (down a tone, a tone below, (or a tone)) is paired; M2  the Keys step letters are T / S,
          not W / H, and "half-whole" never stands alone; M3  a rest is paired with a US rest ("crotchet rest" = quarter rest);
      M4  one bracket per term per checker list (.c2iss, .checker, .fchk); answer 6 (19 Nov): bar and stave carry the
          bracket only in headings and at the first mention in each room;
      L1  no back-to-back brackets "(US: ...) (" and no bracket nested inside a bracket; L3 no "Perfect cadence, less final"
          with a capital mid-sentence; L4 no "= US"; L5 a hover naming "imperfect authentic" carries the note; L7 no dotted
          underline under a term whose bracket is showing.
      L8 (0.48 merge) a hand-written bracket after a term names the full US term ("imperfect cadence (US: half)" fails);
      C1 (0.48 merge) a short cadence answer button ("Perfect", "Imperfect", "Interrupted" beside other cadence names in one answer
          group) carries the FULL US term on hover ("US: authentic cadence"), never a shortened one ("US: authentic").
      M1i (IC_TERMS_048 M1) a heading kept free of brackets (data-notm, e.g. the Ear Lab answer headline) that names a term
          still has the US term on screen in its own panel (outside screen-reader-only text);
      M3i (IC_TERMS_048 M3) a button whose own title names an Australian term ("crotchet" on a rhythm tile) carries its US hover;
      M4i (IC_TERMS_048 M4) the circle of fifths prints a minor key's neighbour keys as minor keys (lower case or "minor");
      S2  a dotted value pairs with a dotted US value ("dotted crotchet" = "dotted quarter note").
      Targeted cases run first: the Gym reader fed I-IV-V-I, I-IV-I, I-V, V6-I and an empty progression; a page fragment
      with the exact strings the independent check quoted; buttons whose text changes; every Ear Lab cadence feedback
      sentence (right, wrong, Nearly on and off) for every answer pair; the Ear Lab rung 3 cadence buttons.
  Each Stage runs on a fresh page (TERMS_PAGE=stage, default; =view a fresh page per view; =one the old single page).
  TERMS_FAST=1 runs T1, the targeted T6 cases and every view at Stage 6 without the click sweep (about 2 minutes).
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
 const US=/\b(authentic|half[- ]cadence|deceptive|(?:quarter|eighth|sixteenth|half|whole) notes?|quarters|eighths|sixteenths|whole steps?|half steps?|staffs?|measures?)\b/i;
 const add=(k,m)=>{const key=k+'|'+m;if(!window.__TV.has(key)&&window.__TV.size<200)window.__TV.set(key,1)};
 const strip=t=>t.replace(/\(US: [^)]*\)/g,' ').replace(/\[US: [^\]]*\]/g,' ').replace(/US 'imperfect authentic' is still a perfect cadence; the Australian imperfect cadence is the US half cadence\./g,' ')
   .replace(/ = (?:US )?[A-Za-z ]*cadence/g,' ').replace(/measure every interval/g,' ').replace(/\s+/g,' ');
 // this file's own finder for the Australian terms (independent of the page's TERMS rx)
 const FIND={iac:/(?<![A-Za-z])perfect cadences?, less final(?![A-Za-z])/gi,perfect:/(?<![A-Za-z])perfect cadences?(?!, less final)(?![A-Za-z])/gi,
  imperfect:/(?<![A-Za-z])imperfect cadences?(?![A-Za-z])/gi,interrupted:/(?<![A-Za-z])interrupted cadences?(?![A-Za-z])/gi,
  crotchet:/(?<![A-Za-z])(?:dotted )?crotchets?(?: rests?)?(?![A-Za-z])/gi,quaver:/(?<![A-Za-z])(?:dotted )?quavers?(?: rests?)?(?![A-Za-z])/gi,minim:/(?<![A-Za-z])(?:dotted )?minims?(?: rests?)?(?![A-Za-z])/gi,
  semibreve:/(?<![A-Za-z])(?:dotted )?semibreves?(?: rests?)?(?![A-Za-z])/gi,semiquaver:/(?<![A-Za-z])(?:dotted )?semiquavers?(?: rests?)?(?![A-Za-z])/gi,
  bar:/(?<![-\u2011A-Za-z])(?<!bars? by[- ])bars?(?![- ]by[- ]bars?\b)(?![- ]?(?:lines?|chart|graph))(?![A-Za-z])/gi,stave:/(?<![A-Za-z])staves?(?![A-Za-z])/gi,
  tone:/(?<![A-Za-z])(?:whole tones?(?![- ]scales?)|(?<=\ba )tone(?=$|\)| (?:higher|lower|above|below|under|apart|up|down)\b))(?![A-Za-z])/gi,
  semitone:/(?<![A-Za-z])semitones?(?![A-Za-z])/gi};
 const usOf0=(k,w)=>{const u=RULE[k][1];if(!u)return null;const pl=/s$/i.test(w);if(/rests?$/i.test(w))return u.replace(/ note$/,' rest')+(pl?'s':'');return pl?(k==='stave'?'staffs':u+'s'):u};
 const usOf=(k,w)=>{const u=usOf0(k,w);return u&&/^dotted /i.test(w)?'dotted '+u:u};   // S2: a dotted value stays dotted
 const termsIn=t=>{const o=[];for(const k in FIND){if(!RULE[k][1])continue;FIND[k].lastIndex=0;let m;while((m=FIND[k].exec(t)))o.push([k,m[0],m.index])}return o};
 const BTN='button,[role="button"],.chip,option,.pill,.fbar>small';
 // C1: a button whose own text is just the short cadence name, in an answer group with at least one other cadence name, stands for the term
 const SHORTCAD={perfect:'perfect',imperfect:'imperfect',interrupted:'interrupted'},CADNAMES=/^(perfect|plagal|imperfect|interrupted|phrygian|cadential\b.*)$/i;
 // the name on the button, without a status badge the card adds after an answer ("Your answer", "Answer")
 const nameOf=b=>{const c=b.cloneNode(true);c.querySelectorAll('.el-badge').forEach(x=>x.remove());return c.textContent.trim()};
 const shortCad=b=>{const w=nameOf(b).toLowerCase();if(!SHORTCAD[w]||!b.parentElement)return null;
  const sib=[...b.parentElement.children].filter(x=>x!==b&&x.matches(BTN)&&CADNAMES.test(nameOf(x)));return sib.length?SHORTCAD[w]:null};
 // 0.49 C14: a hover reads "Australian (US: American)"; a hover with no title of its own stays "US: American" (then the dot only joins the L5 note)
 const usList=ti=>{const t=ti||'',br=[...t.matchAll(/\(US: ([^)]*)\)/g)];if(br.length)return br.flatMap(x=>x[1].split(', ')).map(x=>x.replace(/^\d+ /,''));   // 0.49 RC: a "Term: reason" hover has one bracket for each clause (L63)   // the C13 count is checked by the tile table, not here
 const seg=t.split(' · ').filter(x=>/^US: /.test(x));return seg.length?seg[seg.length-1].slice(4).split(', '):[]};
 const ownText=e=>{const w=document.createTreeWalker(e,NodeFilter.SHOW_TEXT);let t='',n;while((n=w.nextNode()))if(!n.parentElement.closest('[data-notm]')&&n.parentElement.closest(BTN)===e)t+=n.nodeValue+' ';return t};
 // a bracket follows the term, or (0.48 R6 fix) sits inside the term's own following bracket: "Perfect cadence (US: authentic cadence; V–I)"
 const merged=a=>{let h=a,m=a.nextSibling;const sk=()=>{while(m&&m.nodeType===3&&m.nodeValue==='')m=m.nextSibling};sk();
  while(!m&&h.parentElement&&/^(B|I|EM|STRONG)$/.test(h.parentElement.nodeName)){h=h.parentElement;m=h.nextSibling;sk()}
  return !!m&&m.nodeType===3&&(/^\s*\(US[:\s]/.test(m.nodeValue)||/^\s*\($/.test(m.nodeValue)&&!!m.nextSibling&&m.nextSibling.nodeType===1&&m.nextSibling.classList.contains('tmus'))};
 const bracketed=a=>a.dataset.lit==='1'||(a.nextSibling&&a.nextSibling.nodeType===1&&a.nextSibling.classList.contains('tmus'))||merged(a)||!!a.closest('[data-notm]');
 window.__chk=function(where){termPass();const M=document.querySelector('main')||document.body;window.__TN.scans++;
  // T2: no US term on its own (rendered text outside scores, and every title that is not a US hover)
  const tw=document.createTreeWalker(M,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement&&n.parentElement.closest('svg,script,style,textarea,.el-key2')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
  let txt='',n;while((n=tw.nextNode()))txt+=n.nodeValue;
  const t=strip(txt),mm=US.exec(t);if(mm)add('T2',where+': "'+t.slice(Math.max(0,mm.index-50),mm.index+40)+'"');
  M.querySelectorAll('[title]').forEach(e=>{const ti=e.getAttribute('title').replace(/\s*\(US: [^)]*\)/g,' ').replace(/(^|\s*·\s*)US: [^·]*/g,' ');if(US.test(strip(ti)))add('T2',where+': title "'+e.getAttribute('title')+'"')});
  // T3 scores: the Australian term only inside svg
  M.querySelectorAll('svg').forEach(sv=>{const s=sv.textContent;window.__TN.svg++;if(/\(US/.test(s)||US.test(s.replace(/staff-space/g,'')))add('T3',where+': score text has a US term: "'+s.slice(0,80)+'"')});
  // T3 buttons, chips, options: the Australian term only; the US term in a title
  M.querySelectorAll(BTN).forEach(b=>{const s=b.textContent;window.__TN.buttons++;if(b.closest('svg,[data-notm]'))return;
   if(/\(US/.test(s))add('T3',where+': button/chip shows a bracket: "'+s.trim().slice(0,70)+'"');
   const el=b,tl=el.getAttribute('title')||'',got=usList(tl),want=new Set(termsIn(ownText(el)).map(([k,w])=>usOf(k,w)));
   const sc=shortCad(el);if(sc)want.add(RULE[sc][1]);
   // M3i: terms named in the button's own title (the part that is not the US hover or the IAC note) need their US hover too
   const appT=tl.replace(/\s*\(US: [^)]*\)/g,'').split(' · ').filter(x=>!/^US: /.test(x)&&!/is still a perfect cadence/.test(x)).join(' · ');
   // (bar and stave are scoped: a later mention needs no pairing, so a hover that merely mentions a bar is left alone)
   termsIn(appT).forEach(([k,w])=>{const u=usOf(k,w);if(u&&k!=='bar'&&k!=='stave'&&!want.has(u)){want.add(u);if(!got.includes(u))add('T3',where+': button titled "'+appT.slice(0,60)+'" names a term with no US hover "US: '+u+'" (M3i; title "'+tl+'")')}});
   got.forEach(u=>{if(/^(authentic|half|deceptive)$/i.test(u))add('T6',where+': shortened US term on hover (C1) "US: '+u+'" on "'+s.trim().slice(0,60)+'"; expected the full term')});
   // T3 / T6 M3: every term on the button has its hover, in the right form (plural, rest)
   want.forEach(u=>{if(!got.includes(u))add('T3',where+': "'+s.trim().slice(0,60)+'" has no hover "US: '+u+'" (title "'+tl+'")')});
   // T6 H1/H2: no hover names a US term the current text does not contain (stale, piled up, or a wrong N-bar pairing)
   // 0.49 RC (L63, self-check): a "Term: reason" hover pairs each term with the bracket right after its own clause. The bar named in the reason may carry its bracket
   // (a hover is read alone); every other US term must still come from the button's own text or title, and each clause's bracket holds only that clause's terms
   const allowed=new Set([...want,...termsIn(appT).map(([k,w])=>usOf(k,w)).filter(Boolean)]);
   {const pm=/^(.*?)(?: \(US: ([^)]*)\))?: (.*)$/.exec(tl);if(pm&&/\(US: [^)]*\)[^()]*\(US: /.test(tl)){const own=termsIn(pm[1]).map(([k,w])=>usOf(k,w)).sort().join(', '),b1=(pm[2]||'').split(', ').sort().join(', ');
     if(own!==b1)add('T6',where+': hover pairs the wrong terms in its first bracket: "'+tl+'"');
     const lr=[...pm[3].matchAll(/\(US: ([^)]*)\)/g)],rt=termsIn(pm[3].replace(/\s*\(US: [^)]*\)/g,'')).map(([k,w])=>usOf(k,w)).sort().join(', ');
     if(lr.length!==1||lr[0][1].split(', ').sort().join(', ')!==rt)add('T6',where+': hover pairs the wrong terms in its second bracket: "'+tl+'"')}}
   got.forEach(u=>{if(!allowed.has(u))add('T6',where+': stale or wrong hover "US: '+u+'" on "'+s.trim().slice(0,60)+'" (title "'+tl+'")')});
   if(got.includes('imperfect authentic')&&!/is still a perfect cadence/.test(tl))add('T6',where+': hover "imperfect authentic" without the note (L5): "'+s.trim().slice(0,60)+'"')});
  // T6 H1: every term in prose and feedback is marked (so it carries a bracket or a tap hover); buttons, chips and scores excepted
  {const tw=document.createTreeWalker(M,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement&&n.parentElement.closest('svg,script,style,textarea,input,abbr.tm,.tmus,[data-notm],'+BTN)?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});let n;
   while((n=tw.nextNode())){const f=termsIn(n.nodeValue);if(f.length){const [k,w]=f[0];add('T6',where+': "'+w+'" is not marked (no bracket, no tap hover): "'+(n.parentElement.closest('div,p,li,td')||n.parentElement).textContent.trim().slice(0,90)+'"')}}}
  // T6 M3 / plurals: the hover on a marked term is in the right form
  M.querySelectorAll('abbr.tm').forEach(a=>{const k=a.dataset.k;if(!RULE[k]||!RULE[k][1])return;const u=usOf(k,a.textContent);if(a.title!=='US: '+u)add('T6',where+': "'+a.textContent+'" has the hover "'+a.title+'", expected "US: '+u+'"')});
  // T6 H2: no bracket after an N-bar compound or inside "bar by bar"
  {const mm=/(?:\d|[A-Za-z])[-\u2011] ?bars? (?:\(US|\[US)|bars? \(US: measures?\) by bar|by bar \(US/i.exec(txt);if(mm)add('T6',where+': N-bar compound or "bar by bar" carries a bracket: "'+txt.slice(Math.max(0,mm.index-40),mm.index+40)+'"')}
  M.querySelectorAll('abbr.tm[data-k="bar"]').forEach(a=>{const p=a.previousSibling;if(p&&p.nodeType===3&&/[-\u2011]$/.test(p.nodeValue))add('T6',where+': "bar" after a hyphen is marked as a term: "'+(a.parentElement.textContent||'').trim().slice(0,70)+'"')});
  // T6 L1: no back-to-back and no nested brackets
  {const mm=/\(US: [^)]*\)\s*\(/.exec(txt);if(mm)add('T6',where+': back-to-back brackets: "'+txt.slice(Math.max(0,mm.index-50),mm.index+60)+'"')}
  // nested: a round "(US: ...)" bracket inside an open bracket of its own text block (paragraph, list item, cell, feedback box)
  M.querySelectorAll('.tmus').forEach(sp=>{if(!/^ \(US/.test(sp.textContent))return;const blk=sp.parentElement.closest('p,li,td,th,dd,dt,h1,h2,h3,h4,h5,h6,summary,label,figcaption,caption,div')||M;
   const r=document.createRange();r.setStart(blk,0);r.setEndBefore(sp);const q=r.toString();if((q.match(/\(/g)||[]).length>(q.match(/\)/g)||[]).length)add('T6',where+': nested brackets: "'+q.slice(-60)+sp.textContent+'"')});
  // T6 M4: one bracket per term per checker list; answer 6: bar and stave bracketed only in headings and at the first mention in each room
  M.querySelectorAll('.c2iss,.checker,.fchk').forEach(L=>{const c={};L.querySelectorAll('abbr.tm').forEach(a=>{if(bracketed(a)&&a.dataset.lit!=='1'){c[a.dataset.k]=(c[a.dataset.k]||0)+1}});
   for(const k in c)if(c[k]>1)add('T6',where+': "'+k+'" is bracketed '+c[k]+' times in one checker list: "'+L.textContent.trim().slice(0,80)+'"')});
  {const rc=new Map();M.querySelectorAll('abbr.tm[data-k="bar"],abbr.tm[data-k="stave"]').forEach(a=>{if(!bracketed(a)||a.dataset.lit==='1'||a.closest('h1,h2,h3,h4,h5,h6,summary,th,caption,.disp,.kicker,.lbl'))return;
   const r=a.closest('#climbDetail,.room')||M,key=a.dataset.k;let m=rc.get(r);if(!m)rc.set(r,m={});m[key]=(m[key]||0)+1;if(m[key]===2)add('T6',where+': "'+a.textContent+'" bracketed again after the first mention in the room: "'+(a.parentElement.textContent||'').trim().slice(0,70)+'"')})}
  // T6 M2: Australian step letters; L3: no capital mid-sentence; L4: "US" once in the climb 3 row
  M.querySelectorAll('.stp').forEach(e=>{if(/^(W|H|W\+H)$/.test(e.textContent.trim()))add('T6',where+': step letter "'+e.textContent+'" is a US abbreviation (use T / S)')});
  if(/(?:^|[^A-Za-z(])[WH] = (?:whole|semi|half|tone)/.test(t))add('T6',where+': step legend uses W / H');
  if(/half[–-]whole/i.test(t))add('T6',where+': "half–whole" stands on its own');
  {const mm=/[a-z,;:] Perfect cadence, less final/.exec(txt);if(mm)add('T6',where+': capital mid-sentence (L3): "'+txt.slice(Math.max(0,mm.index-40),mm.index+40)+'"')}
  if(/= US /.test(txt))add('T6',where+': "= US" (US twice in the climb 3 row)');
  // T6 L8: a hand-written bracket after a term names the full US term, in the right form
  M.querySelectorAll('abbr.tm').forEach(a=>{if(a.dataset.lit!=='1'||a.closest('[data-notm]'))return;const k=a.dataset.k;if(!RULE[k]||!RULE[k][1])return;
   let h=a,m=a.nextSibling;while(!m&&h.parentElement&&/^(B|I|EM|STRONG)$/.test(h.parentElement.nodeName)){h=h.parentElement;m=h.nextSibling}
   const nx=m&&m.nodeType===3?m.nodeValue:'',c=/^\s*[(\[]US:\s*([^);\]]*)/.exec(nx);if(!c)return;const want=usOf(k,a.textContent),gotU=c[1].split(',')[0].trim();
   if(gotU!==want)add('T6',where+': hand-written bracket after "'+a.textContent+'" reads "US: '+c[1]+'", expected "US: '+want+'" (L8): "'+(a.parentElement.textContent||'').trim().slice(0,80)+'"')});
  // T6 L7: no dotted underline where the bracket shows
  M.querySelectorAll('abbr.tm').forEach(a=>{if(a.offsetParent&&bracketed(a)&&!a.closest('[data-notm]')&&getComputedStyle(a).textDecorationLine!=='none')add('T6',where+': "'+a.textContent+'" is underlined although its bracket shows (L7)')});
  // M1i: a heading kept clean of brackets (data-notm) that names a term: the US term must be on screen in its panel, outside
  // screen-reader-only text and outside data-notm (so it is the term pass's bracket, or a hand-written one in the prose)
  M.querySelectorAll('[data-notm]').forEach(h=>{if(!h.matches('h1,h2,h3,h4,h5,h6,[role="heading"]')||h.closest('svg'))return;const f=termsIn(h.textContent);if(!f.length)return;
   const box=h.closest('.el-result,.card,section,.room')||M,tw=document.createTreeWalker(box,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.parentElement.closest('[data-notm],.el-sr,script,style,svg,button')?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT});
   let vis='',n;while((n=tw.nextNode()))vis+=n.nodeValue;window.__TN.notmHeads=(window.__TN.notmHeads||0)+1;
   f.forEach(([k,w])=>{const u=usOf(k,w);if(u&&!new RegExp('[(\\[]US: (?:[^)\\]]*, )?'+u.replace(/s$/,'')+'s?\\b','i').test(vis))add('T3',where+': heading "'+h.textContent.trim().slice(0,50)+'" (no bracket by design) and no "US: '+u+'" anywhere on screen in its panel (M1i): "'+vis.trim().slice(0,90)+'"')})});
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
  // T5: size
  document.querySelectorAll('abbr.tm,.tmus').forEach(e=>{if(!e.offsetParent)return;const px=parseFloat(getComputedStyle(e).fontSize);if(px<11)add('T5',where+': '+e.className+' is '+px+' px: "'+e.textContent+'"')});
  window.__TN.abbr+=document.querySelectorAll('abbr.tm').length}}"""


# ---- T6 targeted cases. Each: (label, js returning a value, expected value)
FRAG = """<h3 id="f_h">Level 3 · Forms · 12-bar blues</h3>
<div class="room"><p id="f_p1">Compose an 8- to 16-bar melody, and choose, bar by bar, when to use it. Compose an 8-bar phrase.</p></div>
<p id="f_p2">Twelve bars make the form.</p>
<p id="f_p3">Perfect cadence (V–I) at the end, and a semitone (K1) in the bass.</p>
<p id="f_p4">Listen for the Phrygian cadence (an imperfect cadence in minor, iv⁶–V).</p>
<h4 id="f_h4">ii–Vs down a tone</h4>
<p id="f_p5">A major chord a tone below home. Then a minor ii–V a tone lower (bigger than a tone). Chord tone, tone colour, the common tone; from rung 2 a tone, because a clap can't.</p>
<ul class="c2iss" id="f_l"><li>A dissonant minim must be a passing note.</li><li>A dissonant minim must be a passing note.</li><li>A dissonant crotchet on beat 2.</li><li>A dissonant crotchet on beat 4.</li></ul>
<div class="fchk" id="f_c"><div class="iss">Bar 7, beat 3: a 5th.</div><div class="iss">Bars 6–7: 5ths on two downbeats.</div><div class="iss">from bar 14 the bass leaps.</div></div>
<button id="b1">crotchet rest</button><button id="b2">2 quavers</button><button id="b3">4 semiquavers</button><button id="b4">Twelve-bar blues</button>
<p id="f_p6">A dotted crotchet and a quaver. You heard the 7th a tone under the octave.</p>
<button id="b8" data-tt title="dotted crotchet, quaver"><b>ta</b></button><button id="b5">perfect cadence</button><button id="b6" title="own">minim</button><button class="chip" id="b7">Perfect cadence, less final</button>"""

TARGETS = [
    ('H2 heading "12-bar blues" has no bracket', "()=>$('f_h').textContent", 'Level 3 · Forms · 12-bar blues'),
    ('H2/L2 "8- to 16-bar", "bar by bar", "8-bar" have no bracket', "()=>$('f_p1').textContent",
     'Compose an 8- to 16-bar melody, and choose, bar by bar, when to use it. Compose an 8-bar phrase.'),
    ('H2 plain "Twelve bars" keeps its bracket', "()=>$('f_p2').textContent", 'Twelve bars (US: measures) make the form.'),
    ('L1 back-to-back brackets merge', "()=>$('f_p3').textContent", 'Perfect cadence (US: authentic cadence; V–I) at the end, and a semitone (US: half step; K1) in the bass.'),
    ('L1 a bracket inside a bracket is square', "()=>$('f_p4').textContent",
     'Listen for the Phrygian cadence (an imperfect cadence [US: half cadence] in minor, iv⁶–V).'),
    ('M1 heading "down a tone" pairs', "()=>$('f_h4').textContent", 'ii–Vs down a tone (US: whole step)'),
    ('M1 bare interval "a tone" pairs once per block; chord tone, tone colour, common tone and a pitched tone do not', "()=>$('f_p5').textContent",
     "A major chord a tone (US: whole step) below home. Then a minor ii–V a tone lower (bigger than a tone). Chord tone, tone colour, the common tone; from rung 2 a tone, because a clap can't."),
    ('M1 every interval "a tone" is marked', "()=>[...$('f_p5').querySelectorAll('abbr.tm')].map(a=>a.textContent+'|'+a.title).join(', ')",
     'tone|US: whole step, tone|US: whole step, tone|US: whole step'),
    ('M4 one bracket per checker list', "()=>$('f_l').querySelectorAll('.tmus').length", 2),
    ('answer 6: bar locators in feedback after the first mention in the room carry no bracket', "()=>$('f_c').querySelectorAll('.tmus').length", 0),
    ('answer 6: bar locators are still marked (tap hover)', "()=>$('f_c').querySelectorAll('abbr.tm[data-k=bar]').length", 3),
    ('M3 rest button hover', "()=>$('b1').title", 'US: quarter rest'),
    ('M3 plural button hover', "()=>[$('b2').title,$('b3').title]", ['US: eighth notes', 'US: sixteenth notes']),
    ('H2 "Twelve-bar blues" button has no measure hover', "()=>$('b4').getAttribute('title')", None),
    ('L5 IAC chip hover carries the note', "()=>$('b7').title",
     "US: imperfect authentic · US 'imperfect authentic' is still a perfect cadence; the Australian imperfect cadence is the US half cadence."),
    ('S2/S1 dotted value pairs dotted; "a tone under" pairs', "()=>$('f_p6').textContent",
     'A dotted crotchet (US: dotted quarter note) and a quaver (US: eighth note). You heard the 7th a tone (US: whole step) under the octave.'),
    ('M3 a button whose own title names a term (data-tt) gets the US hover', "()=>$('b8').title", 'dotted crotchet, quaver (US: dotted quarter note, eighth note)'),
    ('L7 no underline under a bracketed term', "()=>getComputedStyle($('f_p2').querySelector('abbr.tm')).textDecorationLine", 'none'),
]
# buttons whose text changes: the hover is rebuilt, not added to (H1)
CHANGE = [
    ('H1 hover rebuilt when the text loses its term', "async()=>{$('b5').textContent='Add two or more chords';await new Promise(r=>setTimeout(r,300));return $('b5').getAttribute('title')}", None),
    ('H1 hover rebuilt when the text changes term, keeping the app title', "async()=>{$('b6').textContent='semibreve';await new Promise(r=>setTimeout(r,300));return $('b6').title}", 'own (US: whole note)'),
    ('H1 hover follows a title the app changes', "async()=>{$('b6').title='new';$('b6').textContent='minims';await new Promise(r=>setTimeout(r,300));return $('b6').title}", 'new (US: half notes)'),
]
GYM = [  # (progression [(numeral, inversion)], text the reader must show)
    ([('I', 0), ('IV', 0), ('V', 0), ('I', 0)], 'Perfect cadence (US: authentic cadence).'),
    ([('I', 0), ('IV', 0), ('I', 0)], 'gentler than a perfect cadence (US: authentic cadence)'),
    ([('I', 0), ('V', 0)], 'Imperfect cadence (US: half cadence).'),
    ([('I', 0), ('IV', 0), ('V', 0), ('vi', 0)], 'Interrupted cadence (US: deceptive cadence).'),
    ([('V', 1), ('I', 0)], "This one is a perfect cadence, less final (US: imperfect authentic). US 'imperfect authentic' is still a perfect cadence"),
    ([], "Add two or more chords"),
]


async def targeted(pg):
    await pg.evaluate("""(h)=>{const d=document.createElement('div');d.className='room';d.id='tmfrag';d.innerHTML=h;document.querySelector('main').appendChild(d);termPass()}""", FRAG)
    for lab, js, want in TARGETS:
        got = await pg.evaluate(js)
        if got != want:
            fail('T6', f'{lab}: got {got!r}, expected {want!r}')
        else:
            ok('T6', lab)
    for lab, js, want in CHANGE:
        got = await pg.evaluate(js)
        if got != want:
            fail('T6', f'{lab}: got {got!r}, expected {want!r}')
        else:
            ok('T6', lab)
    await pg.evaluate("__chk('T6 fragment')")
    await pg.evaluate("$('tmfrag').remove()")
    # every Ear Lab cadence feedback sentence (right; wrong; Nearly on and off), every answer x given pair, as feedback in a room
    n = await pg.evaluate("""async()=>{const SIX=['perfect','plagal','imperfect','interrupted','phrygian','cad64'],o=[];
        for(const a of SIX){let q=null;for(let i=0;i<4000&&!q;i++){const x=earGen('cad',3);if(x&&x.a===a)q=x}if(!q)continue;const min=q.key.mode==='min';
          o.push(earCadRight(a,q,min));for(const g of SIX)if(g!==a){o.push(earCadWrong(a,g,q,min,null));o.push(earCadWrong(a,g,q,min,{kind:'nearly'}))}}
        const d=document.createElement('div');d.className='room';d.id='tmear';d.innerHTML=o.map(t=>'<div class="el-teach"><p>'+t+'</p></div>').join('');
        document.querySelector('main').appendChild(d);termPass();return o.length}""")
    COUNT['T6 Ear Lab cadence feedback sentences checked'] = n
    if n < 60:
        fail('T6', f'Ear Lab cadence feedback: only {n} sentences built')
    short = await pg.evaluate(r"()=>[...document.querySelectorAll('#tmear p')].map(p=>p.textContent).filter(t=>/[(\[]US: (half|authentic|deceptive)[)\]]/.test(t))")
    if short:
        fail('T6', f'L8 Ear Lab feedback with a shortened US bracket: {short[:2]}')
    else:
        ok('T6', 'L8 Ear Lab cadence feedback: no shortened US bracket')
    await pg.evaluate("__chk('T6 Ear Lab cadence feedback')")
    await pg.evaluate("$('tmear').remove()")
    # C1: the Ear Lab rung 3 cadence buttons: short Australian names, the full US term on hover
    eb = await pg.evaluate("""()=>new Promise(res=>{const L0=EAR.lvl.cad;location.hash='ear';EAR.drill='cad';EAR.lvl.cad=3;room('ear');
        setTimeout(()=>{const r=[...document.querySelectorAll('#earMain [data-earans]')].map(b=>[b.textContent.trim(),b.getAttribute('title')]);EAR.lvl.cad=L0;room('ear');res(r)},400)})""")
    want_eb = [['Perfect', 'US: authentic cadence'], ['Plagal', None], ['Imperfect', 'US: half cadence'], ['Interrupted', 'US: deceptive cadence'],
               ['Phrygian', None], ['Cadential 64', None]]
    if eb != want_eb:
        fail('T6', f'C1 Ear Lab rung 3 cadence buttons: got {eb}, expected {want_eb}')
    else:
        ok('T6', 'C1 Ear Lab cadence buttons carry the full US term on hover')
    # 0.49 C2: the Ear Lab rhythm card's own prompt carries the first mention of bar in the room, with both terms; later mentions only hover
    for lv in (1, 2, 3):
        rb = await pg.evaluate("""(lv)=>new Promise(res=>{const L0=EAR.lvl.rhy;location.hash='ear';EAR.drill='rhy';EAR.lvl.rhy=lv;room('ear');
            setTimeout(()=>{const a=[...document.querySelectorAll('#room-ear abbr.tm[data-k="bar"]')],ask=document.querySelector('#earCard .el-ask'),
              r={first:a[0]?!!a[0].closest('.el-ask'):false,txt:ask?ask.textContent:'',later:a.slice(1).filter(x=>x.nextSibling&&x.nextSibling.className==='tmus').length};EAR.lvl.rhy=L0;room('ear');res(r)},500)})""", lv)
        want = ('two bars (US: measures)' if lv >= 2 else 'one bar (US: measure)')
        if not rb['first'] or want not in rb['txt'] or rb['later']:
            fail('T3', f'C2 Ear Lab rhythm card rung {lv}: first mention of bar not bracketed in the prompt (or bracketed again later): {rb}')
        else:
            ok('T3', 'C2 Ear Lab rhythm card prompt: first mention of bar carries both terms (rungs 1-3)')
    # IC_TERMS_048 M1: every Ear Lab cadence and blind result panel (rungs 1-3, every given answer, shown, Nearly on and off), as drawn by
    # the card, with its clean headline: the US term must be on screen in the panel (M1i in __chk)
    np = await pg.evaluate("""async()=>{await earLoadBlind();const N0=EAR_NEARLY,o=[];
        try{for(const l of [1,2,3])for(let i=0;i<60;i++){const q=earGen('cad',l);for(const g of [null,...q.opts])for(const nf of [true,false]){EAR_NEARLY=nf;
            const j=g===null?'shown':earJudge(q,g),kind=g===null?'shown':j==='correct'?'ok':j==='nearly'?'nearly':'miss';o.push(earResultHTML(q,earTeachCad(q,{kind,given:g})))}}
          for(const x of EAR.blind){const q={d:'blind',...x,a:x.cat,l:3,lvl:3};for(const g of [null,...earBlindCats(3)]){const j=g===null?'shown':earJudge(q,g),
            kind=g===null?'shown':j==='correct'?'ok':j==='nearly'?'nearly':'miss';o.push(earResultHTML(q,earTeachCad(q,{kind,given:g})))}}}finally{EAR_NEARLY=N0}
        const d=document.createElement('div');d.id='tmpanels';d.innerHTML=o.map(h=>'<div class="room">'+h.replace(/id="earResult"/,'')+'</div>').join('');
        document.querySelector('main').appendChild(d);termPass();return o.length}""")
    COUNT['T6 M1i Ear Lab result panels drawn'] = np
    await pg.evaluate("__chk('T6 Ear Lab result panels')")
    miss = await pg.evaluate("""()=>[...document.querySelectorAll('#tmpanels .el-result')].filter(r=>{const h=r.querySelector('.el-answer').textContent;
        const m=/^(Perfect|Imperfect|Interrupted) cadence/.exec(h);if(!m)return false;const u={Perfect:'authentic',Imperfect:'half',Interrupted:'deceptive'}[m[1]]+' cadence';
        return !r.querySelector('.el-teach').textContent.includes('US: '+u)}).map(r=>r.querySelector('.el-answer').textContent+' | '+r.querySelector('.el-teach').textContent).slice(0,3)""")
    if miss:
        fail('T6', f'M1i Ear Lab panels whose teaching sentence gives no US term: {miss}')
    else:
        ok('T6', 'M1i every Ear Lab cadence/blind panel names the cadence with its US term')
    await pg.evaluate("$('tmpanels').remove()")
    # IC_TERMS_048 M3: the rhythm tiles (rungs 1-3) carry the US term on hover
    tiles = await pg.evaluate("""()=>new Promise(res=>{const L0=EAR.lvl.rhy;location.hash='ear';EAR.drill='rhy';EAR.q=null;EAR.done=false;const o={};let l=1;
        const step=()=>{EAR.lvl.rhy=l;room('ear');EAR.q=earGen('rhy',l);EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();setTimeout(()=>{document.querySelectorAll('#earMain [data-earcell]').forEach(b=>o[b.dataset.earcell]=b.getAttribute('title'));
          if(++l<=3)step();else{EAR.lvl.rhy=L0;EAR.q=null;EAR.done=false;room('ear');res(o)}},300)};step()})""")
    want_t = {'q': 'crotchet (US: quarter note)', 'e2': '2 quavers (US: 2 eighth notes)', 'h': 'minim (US: half note)', 's4': '4 semiquavers (US: 4 sixteenth notes)',
              'qr': 'crotchet rest (US: quarter rest)', 'dq': 'dotted crotchet, quaver (US: dotted quarter note, eighth note)',
              'w': 'semibreve (US: whole note)', 'hd': 'dotted minim (US: dotted half note)',
              'es2': 'quaver, 2 semiquavers (US: eighth note, 2 sixteenth notes)', 's2e': '2 semiquavers, quaver (US: 2 sixteenth notes, eighth note)',
              'syn': 'quaver, crotchet, quaver (US: eighth note, quarter note, eighth note)'}  # R2 S-T1: one US name per value
    bad_t = {k: v for k, v in tiles.items() if want_t.get(k) != v}
    if bad_t or not tiles:
        fail('T6', f'M3i rhythm tile hovers: {bad_t or tiles}')
    else:
        ok('T6', f'M3i rhythm tiles carry the US term on hover ({len(tiles)} cells)')
    # IC_TERMS_048 M4: the circle of fifths, all 24 keys: a minor key's neighbours read as minor keys, a major key's as major
    circ = await pg.evaluate("""()=>{location.hash='keys';KS.tab='circle';room('keys');renderKeysRoom();const o=[];
        for(const mn of [false,true])for(let i=0;i<12;i++){CSEL={i,minor:mn};renderCircle();const dd=[...document.querySelectorAll('#ksKeyInfo dd')][2];o.push([mn,dd?dd.textContent:''])}
        CSEL={i:0,minor:false};renderCircle();return o}""")
    cb = []
    for mn, t in circ:
        m = re.match(r'(\S+)( major| minor)? \(one step clockwise.*\) · (\S+)( major| minor)? \(one step back', t)
        if not m:
            cb.append(t); continue
        for got, mw in ((m.group(1), m.group(2)), (m.group(3), m.group(4))):
            read = mw.strip() if mw else ('minor' if got[0].islower() else 'major')
            if read != ('minor' if mn else 'major'):
                cb.append(t)
    if cb:
        fail('T6', f'M4i circle neighbours read in the wrong mode ({len(cb)}): {cb[:2]}')
    else:
        ok('T6', 'M4i circle neighbours read as the right mode (24 keys)')
    # ... and still after an answer, when the card adds its "Your answer" / "Answer" badges to the buttons
    ea = await pg.evaluate("""()=>new Promise(res=>{const L0=EAR.lvl.cad;EAR.drill='cad';EAR.lvl.cad=3;let q;do{q=earGen('cad',3)}while(q.a!=='perfect');
        EAR.q=q;EAR.done=false;EAR.res=null;EAR.ans=[];renderEar();document.querySelector('#earMain [data-earans="imperfect"]').click();
        setTimeout(()=>{const r=Object.fromEntries([...document.querySelectorAll('#earMain [data-earans]')].map(b=>[b.dataset.earans,b.getAttribute('title')]));
          __chk('T6 Ear Lab cadence answered');EAR.lvl.cad=L0;EAR.q=null;EAR.done=false;EAR.res=null;room('ear');res(r)},400)})""")
    want_ea = {'perfect': 'US: authentic cadence', 'plagal': None, 'imperfect': 'US: half cadence', 'interrupted': 'US: deceptive cadence', 'phrygian': None, 'cad64': None}
    if ea != want_ea:
        fail('T6', f'C1 Ear Lab cadence buttons after an answer: got {ea}, expected {want_ea}')
    else:
        ok('T6', 'C1 Ear Lab cadence buttons keep the full US hover after an answer (badges shown)')
    # the Gym cadence reader (#cad) is answer feedback: brackets, and no hover that piles up
    await pg.evaluate("location.hash='gym'")
    await pg.wait_for_timeout(500)
    for prog, want in GYM:
        r = await pg.evaluate("""(q)=>new Promise(res=>{P.length=0;for(const [n,i] of q)P.push({...parseRoman(n,K),inv:i,beats:gBar()});renderGym();
            setTimeout(()=>{const c=document.getElementById('cad');res({t:c.textContent,ti:c.getAttribute('title')})},300)})""", prog)
        lab = 'Gym reader ' + ('–'.join(n + ('6' if i else '') for n, i in prog) or 'empty')
        if want not in r['t'] or (r['ti'] and 'US:' in r['ti']):
            fail('T6', f"H1 {lab}: shows '{r['t'][:160]}' with title {r['ti']!r}; expected '{want}' and no US hover")
        else:
            ok('T6', 'H1 Gym cadence reader brackets its feedback (no stale hover)')
        await pg.evaluate(f"__chk({json.dumps('T6 ' + lab)})")
    await pg.evaluate("P.length=0;saveP();renderGym()")


async def open_page(b, errs, cur):
    """A fresh page (its own browser context, so its own renderer) with the app loaded and the checker installed."""
    pg = await b.new_page(viewport={'width': 1440, 'height': 900})
    pg.on('pageerror', lambda e: errs.append(f'{cur[0]}: {str(e)[:160]} @ {(getattr(e, "stack", "") or "").strip().splitlines()[1:3]}'))
    pg.on('dialog', lambda d: asyncio.ensure_future(d.dismiss()))
    await pg.route('**/*', cjg.make_route(REPO))
    await pg.goto('http://app/index.html')
    await pg.wait_for_timeout(1500)
    await pg.evaluate(CHK_JS, RULE)
    return pg


async def collect(pg):
    """Move the page's violations and scan counts into FAIL / COUNT (each page keeps its own window.__TV and __TN)."""
    tv = await pg.evaluate("()=>[[...window.__TV.keys()],window.__TN]")
    for k in tv[0]:
        sec, _, msg = k.partition('|')
        if msg not in FAIL[sec]:
            fail(sec, msg)
    for k, v in tv[1].items():
        COUNT[f'page scan: {k}'] += v


async def main():
    # 0.49: one long page crashed the renderer ("Target crashed") on the full run. Each Stage now gets a fresh page
    # (TERMS_PAGE=stage, the default), or each view its own (TERMS_PAGE=view); TERMS_PAGE=one keeps the old single page.
    # The checks, views, clicks and their order are the same in every mode.
    mode = os.environ.get('TERMS_PAGE', 'stage')
    async with async_playwright() as p:
        b = await cjg.launch(p)
        errs = []
        cur = ['load']
        pg = await open_page(b, errs, cur)

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

        # ---- T2-T6: the checker is installed by open_page
        # ---- T6 targeted cases (0.48 R6 fix round): the strings the independent check IC_R6 quoted
        await targeted(pg)
        # ---- T2-T6: every view, every button
        fast = os.environ.get('TERMS_FAST') == '1'
        stages = [6] if fast else [int(x) for x in os.environ.get('TERMS_STAGES', '4,5,6').split(',')]

        async def fresh():
            nonlocal pg
            if mode == 'one':
                return
            await collect(pg)
            await pg.context.close()
            pg = await open_page(b, errs, cur)
            COUNT['self-check fresh pages opened'] += 1

        async def set_stage(stage):
            await pg.evaluate(f"document.querySelector('#lvl button[data-l=\"{stage}\"]').click()")
            await pg.wait_for_timeout(200)

        for stage in stages:
            if mode == 'stage':
                await fresh()
            await set_stage(stage)
            for name, js in views():
                where = f'S{stage} {name}'
                if mode == 'view':
                    await fresh()
                    await set_stage(stage)
                cur[0] = where
                await pg.evaluate(js)
                await pg.wait_for_timeout(900 if name.startswith('analysis') else 350)
                await pg.evaluate(f"__chk({json.dumps(where)})")
                COUNT['views scanned'] += 1
                nb = 0 if fast else await pg.evaluate(f"""(skip)=>[...document.querySelectorAll('main button')].filter(b=>b.offsetParent&&!b.disabled&&!b.matches(skip)).length""", SKIP)
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
        await collect(pg)
        # ---- T5 idempotence: a second pass changes nothing (on the page the last sweep used)
        same = await pg.evaluate("""()=>{termPass();const a=document.querySelector('main').innerHTML;termPass();termPass();return a===document.querySelector('main').innerHTML}""")
        if not same:
            fail('T5', 'termPass() is not idempotent')
        else:
            ok('T5', 'termPass idempotent')
        # ---- the automatic pass: text drawn after load gets its brackets without a call
        auto = await pg.evaluate("""async()=>{const d=document.createElement('div');d.id='tmauto';d.innerHTML='<p>A crotchet then a quaver. A crotchet again.</p><button>minim</button>';document.querySelector('main').appendChild(d);
            await new Promise(r=>setTimeout(r,400));const t=d.textContent,bt=d.querySelector('button').title;d.remove();return{t,bt}}""")
        if auto['t'] != 'A crotchet (US: quarter note) then a quaver (US: eighth note). A crotchet again.minim' or auto['bt'] != 'US: half note':
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
