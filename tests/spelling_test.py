"""Theory spelling suite (charter suite 5: "Theory spelling: music21 suites for Keys and climbs 3-12").
Run: python3 tests/spelling_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

The app is loaded headless and offline through tests/harness/cjg.py. Data is pulled out of the page with the app's own
functions and from what the page actually renders; every expectation is re-derived here, in Python, with music21 and
this file's own tables. The app's own checkers are never used as the oracle.

Sections
  K  Keys & Scales room, Scales tab: every scale type x every tonic the room offers (the 17 pitch pads, every tonic
     reachable from the circle's mode chips, every enharmonic chip) x going up / coming down. Checks the spelled note
     names (music21 scales or interval tables), the MIDI pitch classes, the W/H step labels, the scale-degree numbers,
     the solfa (movable do, la-based minor, modes named from the parent major), the key-signature text and the key
     signature the staff is drawn with, theoretical keys flagged with the usual enharmonic tonic, and the chords of
     the key (roots, qualities, numerals) for every seven-note scale.
  C  Keys & the Circle tab: all 24 keys. Title, key signature, enharmonic twin, relative, parallel, neighbours, and
     the seven mode chips named from the parent major.
  I  Intervals tab: every start pad x every interval x up/down. The second note's spelling (music21 Interval),
     semitone count, interval number and the inversion.
  R  Climbs 3-8 (#climbs/3 ... #climbs/8): every example, builder combination, quiz and period progression the climb
     plays, in every key it offers, at Stages 4/5/6. Each chord's spelled notes and bass against music21
     RomanNumeral (secondary dominants, borrowed chords, N6, It/Fr/Ger augmented 6ths, cadential 6/4), and every
     SATB realisation: only chord tones, the right bass, root and 3rd present, voices in order.
  J  Climbs 9-11 (jazz): every token is checked against a chord symbol (root from music21 RomanNumeral, quality from
     the jazz suffix, notes from music21 ChordSymbol), and every voicing the climb draws or plays (guide tones,
     shells, rootless A/B, the reharmonisation voicings) uses only notes of the displayed chord symbol over the
     right bass. Climb 11's whole reharmonisation vocabulary is checked in every key.
  M  Climb 12: modal vamps on every tonic (music21 RomanNumeral and ChordSymbol), chromatic-mediant chains
     (music21 intervals), planing shapes (interval spelling), tintinnabuli (T-voice in the triad).
  R  R3 (0.47): the stave never receives more than a double accidental. Every scale, interval and Chords-room chord
     (every root spelling x every quality) whose spelling needs a triple sharp or flat is drawn without error, shows
     the enharmonic respelling (same pitch per music21, adjacent letter, at most a double accidental) and flags it
     in the frame (data-resp) with a visible "Theoretical spelling" note.
  D  Displayed labels in the climbs: every bar/numeral chip rendered shows a chord symbol whose root matches music21.

  G  R10 (0.48): no rendered label (Keys, Chords, climbs, and every room as first opened) spells a double accidental as two
     characters ("B♭b", "F♯♯", "Cbb", "C##", "♭♭7"): the page-side scanner walks every text node and title/aria-label/alt.

  X  page errors and exceptions thrown while rendering any climb state.

Counts on v0.46 (about 90 s): 43,847 checks. Keys room: 18 tonics x 17 scales x 2 directions = 612 scales
(612 each for spelling, pitch classes, steps, degrees and solfa; 508 key signatures + 104 theoretical keys; 436 staff
signatures; 5,238 chords of the key); circle 24 keys (315 checks); intervals 578 x 3. Climbs: 1,627 distinct
progressions captured from 2,007 renders plus builders and quizzes; 9,236 chord-vs-music21 checks, 6,120 SATB chords,
2,472 jazz voicings, 2,764 piano voicings, 1,248 climb-12 checks, 10,636 displayed labels.
Known failures are listed in KNOWN below (SP-2, SP-3; SP-1 was fixed in 0.47 by R3): they are reported but do not fail the run.
"""
import sys, asyncio, json, pathlib, collections, re, itertools, time

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import roman, key as m21key, pitch as m21pitch, interval as m21int, scale as m21scale, harmony, chord as m21chord

FAIL = collections.defaultdict(list)
KNOWNHIT = collections.defaultdict(list)
COUNT = collections.Counter()

# id -> (section, regex on the failure message, description). Matching failures are reported, not counted.
KNOWN = {}   # SP-2 (double accidentals in chord buttons) and SP-3 (circle parallel keys) were fixed in 0.48 (R10, R11)


def fail(sec, msg):
    for kid, (ks, rx, _) in KNOWN.items():
        if sec in ks and re.search(rx, msg):
            KNOWNHIT[kid].append(msg)
            return
    FAIL[sec].append(msg)


def ok(sec, label):
    COUNT[f'{sec}: {label}'] += 1


# ---------------------------------------------------------------- name helpers
def m21name(s):
    """'F♯' / 'F#' / 'B♭' / 'Bb' / 'B𝄫' / 'Bbb' -> music21 'F#', 'B-', 'B--'"""
    s = s.strip().replace('♯', '#').replace('♭', 'b').replace('𝄫', 'bb').replace('𝄪', '##')
    return s[0] + s[1:].replace('b', '-')


def appname(p):
    """music21 pitch/name -> app ASCII name ('B-' -> 'Bb')"""
    n = p if isinstance(p, str) else p.name
    return n.replace('-', 'b')


def P(s):
    return m21pitch.Pitch(m21name(s))


def key_of(tonic, mode):
    t = m21name(tonic)
    return m21key.Key(t.lower() if mode == 'min' else t)


# ---------------------------------------------------------------- scale oracle
IVL = {  # this file's own interval tables (used where music21 has no scale class)
    'mpent': ['P1', 'M2', 'M3', 'P5', 'M6'],
    'npent': ['P1', 'm3', 'P4', 'P5', 'm7'],
    'blues': ['P1', 'm3', 'P4', 'd5', 'P5', 'm7'],
    'whole': ['P1', 'M2', 'M3', 'A4', 'A5', 'm7'],
    'chrom': ['P1', 'A1', 'M2', 'A2', 'M3', 'P4', 'A4', 'P5', 'A5', 'M6', 'A6', 'M7'],          # sharps going up
    'chrom_down': ['P8', 'M7', 'm7', 'M6', 'm6', 'P5', 'd5', 'P4', 'M3', 'm3', 'M2', 'm2', 'P1'],  # flats coming down
    'phrd': ['P1', 'm2', 'M3', 'P4', 'P5', 'm6', 'm7'],
    'oct': ['P1', 'm2', 'A2', 'M3', 'A4', 'P5', 'M6', 'm7'],
}
M21SC = {'maj': m21scale.MajorScale, 'ion': m21scale.MajorScale, 'nmin': m21scale.MinorScale,
         'hmin': m21scale.HarmonicMinorScale, 'mmin': m21scale.MelodicMinorScale, 'dor': m21scale.DorianScale,
         'phr': m21scale.PhrygianScale, 'lyd': m21scale.LydianScale, 'mix': m21scale.MixolydianScale,
         'loc': m21scale.LocrianScale}


def expected_scale(tonic, sk, desc):
    """Spelled names, ascending from the tonic and including the octave (or descending when desc)."""
    t = P(tonic)
    t.octave = 4
    if sk in M21SC:
        if sk == 'mmin' and desc:
            names = [p.name for p in m21scale.MinorScale(t).getPitches(t, t.transpose('P8'))]
            return list(reversed(names))
        names = [p.name for p in M21SC[sk](t).getPitches(t, t.transpose('P8'))]
    elif sk == 'chrom' and desc:
        return [t.transpose(i).name for i in IVL['chrom_down']]
    else:
        names = [t.transpose(i).name for i in IVL[sk]] + [t.name]
    return list(reversed(names)) if desc else names


# Where "do" sits relative to the tonic, per scale (movable do, la-based minor, modes from the parent major)
DO_FROM_TONIC = {'maj': 'P1', 'ion': 'P1', 'mpent': 'P1', 'whole': 'P1', 'chrom': 'P1', 'oct': 'P1',
                 'nmin': 'm3', 'hmin': 'm3', 'mmin': 'm3', 'npent': 'm3', 'blues': 'm3',
                 'dor': '-M2', 'phr': '-M3', 'lyd': '-P4', 'mix': '-P5', 'loc': 'm2', 'phrd': '-M3'}
SOLFA = {'P1': 'do', 'A1': 'di', 'm2': 'ra', 'M2': 're', 'A2': 'ri', 'm3': 'ma', 'M3': 'mi', 'P4': 'fa', 'A4': 'fi',
         'd5': 'se', 'P5': 'so', 'A5': 'si', 'm6': 'le', 'M6': 'la', 'A6': 'li', 'm7': 'ta', 'M7': 'ti', 'd8': 'ti'}
MAJ_SEMI = [0, 2, 4, 5, 7, 9, 11]


def do_of(tonic, sk):
    t = P(tonic)
    t.octave = 4
    iv = DO_FROM_TONIC[sk]
    return t.transpose(m21int.Interval(iv[1:]).reverse() if iv.startswith('-') else iv)


def solfa_of(do, name):
    d = m21pitch.Pitch(do.name)
    d.octave = 4
    n = m21pitch.Pitch(name)
    n.octave = 4
    if n < d:
        n.octave = 5
    iv = m21int.Interval(d, n)
    sn = iv.semiSimpleName if iv.semiSimpleName != 'P8' else 'P1'
    return SOLFA.get(sn, '?' + sn)


def degree_label(tonic, name):
    t = m21pitch.Pitch(m21name(tonic))
    t.octave = 4
    n = m21pitch.Pitch(name)
    n.octave = 4
    if n < t:
        n.octave = 5
    iv = m21int.Interval(t, n)
    gen = iv.generic.semiSimpleUndirected
    if gen == 8:
        gen = 1
    semis = iv.semitones % 12
    alt = semis - MAJ_SEMI[gen - 1]
    if alt > 6:
        alt -= 12
    if alt < -6:
        alt += 12
    return ('♯' * alt if alt > 0 else '♭' * -alt if alt < 0 else '') + str(gen)


def parent_major(tonic, sk):
    """Tonic of the major key whose signature the scale uses, or None (no key signature)."""
    off = {'maj': 'P1', 'ion': 'P1', 'mpent': 'P1', 'chrom': 'P1', 'nmin': 'm3', 'hmin': 'm3', 'mmin': 'm3',
           'npent': 'm3', 'blues': 'm3', 'dor': '-M2', 'phr': '-M3', 'lyd': '-P4', 'mix': '-P5', 'loc': 'm2',
           'phrd': 'm6'}.get(sk)
    if off is None:
        return None
    t = P(tonic)
    t.octave = 4
    return t.transpose(m21int.Interval(off[1:]).reverse() if off.startswith('-') else off).name


def enharmonic_alt(tonic, sk):
    """The usual enharmonic tonic: same pitch class, a neighbouring letter, at most one accidental, smallest signature."""
    t = P(tonic)
    best = None
    for e in [t.getHigherEnharmonic(), t.getLowerEnharmonic()]:
        if e is None or e.accidental is not None and abs(e.accidental.alter) > 1:
            continue
        pm = parent_major(e.name, sk)
        n = abs(m21key.Key(pm).sharps) if pm and abs(m21pitch.Pitch(pm).alter) <= 2 else 99
        if best is None or n < best[1]:
            best = (e.name, n)
    return best[0] if best and best[1] <= 7 else None


def sig_sharps(major_tonic):
    p = m21pitch.Pitch(major_tonic)
    fifths = {'F': -1, 'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5}[p.step] + 7 * int(p.alter)
    return fifths


def sig_text(n):
    if n == 0:
        return 'No sharps or flats'
    order = 'FCGDAEB' if n > 0 else 'BEADGCF'
    acc = '♯' if n > 0 else '♭'
    L = ' '.join(x + acc for x in order[:abs(n)])
    return f"{abs(n)} {'sharp' if n > 0 else 'flat'}{'s' if abs(n) > 1 else ''}: {L}"


def pretty(n):
    """music21 / ASCII name -> the app's display ('B-' -> 'B♭', 'F##' -> 'F𝄪')"""
    n = n.replace('-', 'b')
    n = re.sub(r'bb$', '𝄫', n)
    n = re.sub(r'##$', '𝄪', n)
    return n.replace('#', '♯').replace('b', '♭') if len(n) > 1 else n


def prettyname(n):
    return n[0] + pretty(n)[1:] if len(n) > 1 else n


# ---------------------------------------------------------------- chords of a scale
ROM = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']


def stacked_chord(names, i, sev):
    """music21 Chord of 3rds stacked on degree i of a 7-note scale (names = 7 spelled names)."""
    ps = []
    prev = None
    for j in ([0, 2, 4, 6] if sev else [0, 2, 4]):
        p = m21pitch.Pitch(names[(i + j) % 7])
        p.octave = 4
        while prev is not None and p <= prev:
            p.octave += 1
        ps.append(p)
        prev = p
    return ps


def chord_quality(ps):
    r = ps[0]
    ivs = [m21int.Interval(r, p).simpleName for p in ps[1:]]
    tri = {('M3', 'P5'): '', ('m3', 'P5'): 'm', ('m3', 'd5'): 'dim', ('M3', 'A5'): 'aug'}.get(tuple(ivs[:2]), '?')
    if len(ps) == 3:
        return tri
    s7 = ivs[2]
    return {('', 'M7'): 'maj7', ('', 'm7'): '7', ('m', 'm7'): 'm7', ('m', 'M7'): 'mMaj7', ('dim', 'm7'): 'm7b5',
            ('dim', 'd7'): 'dim7', ('aug', 'M7'): 'augMaj7'}.get((tri, s7), '?')


SYMSUF = {'': '', 'm': 'm', 'dim': 'dim', 'aug': 'aug', 'maj7': 'maj7', '7': '7', 'm7': 'm7', 'm7b5': 'm7♭5',
          'dim7': 'dim7', 'mMaj7': 'm(maj7)', 'augMaj7': 'aug(maj7)'}
NUMSUF = {'dim': '°', 'aug': '+', 'm7b5': 'ø7', 'dim7': '°7', 'maj7': 'maj7', '7': '7', 'm7': '7', 'mMaj7': '(maj7)',
          'augMaj7': '+maj7'}


# ================================================================= Keys room
KEYS_JS = r"""()=>{S.level=6;ROOM='keys';KS.tab='scales';renderKeysRoom();
 const cap=[];const dl=drawLine;window.drawLine=function(el,notes,clef,ksig,dur){if(el&&el.id==='ksStaff')cap.push({ksig:ksig||null,names:notes.map(n=>n.name)});return dl.apply(this,arguments)};
 const T=PADS.flat().slice(),circle=[];
 for(let i=0;i<12;i++)for(const mn of [false,true]){CSEL={i,minor:mn};renderCircle();__scan(document.body,`circle ${i} ${mn}`);const box=$('ksKeyInfo');
  circle.push({i,minor:mn,title:box.querySelector('.sym').textContent,ctx:box.querySelector('p.ctx').textContent,
   dd:[...box.querySelectorAll('dd')].map(e=>e.textContent),modes:[...box.querySelectorAll('.chips [data-kmode]')].map(b=>({v:b.dataset.kmode,t:b.textContent})),
   open:box.querySelector('button.mini[data-kmode]').dataset.kmode});
  box.querySelectorAll('[data-kmode]').forEach(b=>{const t=b.dataset.kmode.split('|')[0];if(!T.includes(t))T.push(t)})}
 KS.tab='scales';renderKeysRoom();
 const out=[];
 for(let ti=0;ti<T.length;ti++){const t=T[ti];for(const sc of SCALES)for(const desc of [false,true]){KS.tonic=t;KS.sc=sc.k;KS.desc=desc;cap.length=0;let err=null;try{renderScales();__scan(document.body,`scales ${t} ${sc.k} ${desc}`)}catch(e){err=String(e).slice(0,160)}
  const alt=document.querySelector('#ksSig [data-kst]');if(alt&&!T.includes(alt.dataset.kst))T.push(alt.dataset.kst);
  out.push({err,t,sc:sc.k,desc,hasDesc:!!sc.desc,name:$('ksName').textContent,
   tiles:[...document.querySelectorAll('#ksTiles .stile')].map(e=>({n:e.querySelector('b').textContent,so:e.querySelector('.so').textContent,d:e.querySelector('small').textContent,m:+e.dataset.m})),
   steps:[...document.querySelectorAll('#ksTiles .stp')].map(e=>e.textContent),
   sig:$('ksSig').textContent,sigRed:!!$('ksSig').querySelector('span[style*="red"]'),alt:alt?alt.dataset.kst:null,
   form:$('ksForm').textContent,sol:$('ksSol').textContent,staff:cap[cap.length-1]||null,resp:$('ksStaff').dataset.resp||'',svg:!!$('ksStaff').querySelector('svg'),
   ladder:[...document.querySelectorAll('#ksLadder .rung')].map(e=>({sy:e.querySelector('.sy').textContent,nm:e.querySelector('.nm').textContent,nb:e.querySelector('.nb').textContent})),
   chords:[...document.querySelectorAll('#ksChords .kchords')].map(row=>[...row.querySelectorAll('.kc')].map(b=>({num:b.querySelector('.rn').textContent,sym:b.querySelector('b').textContent})))})}}
 window.drawLine=dl;
 KS.tab='intervals';renderKeysRoom();const iv=[];
 for(const start of PADS.flat())for(const x of IVS)for(const dir of ['up','down']){KS.iv={start,k:x.k,dir};let err=null;try{renderIntervals();__scan(document.body,`intervals ${start} ${x.k} ${dir}`)}catch(e){err=String(e).slice(0,160)}
  iv.push({err,start,k:x.k,dir,name:$('ivName').textContent,sub:$('ivSub').textContent,dd:[...document.querySelectorAll('#ivFacts dd')].map(e=>e.textContent),
   kb:[...document.querySelectorAll('#ivKb .lit')].map(e=>+e.dataset.m),resp:$('ivStaff').dataset.resp||'',svg:!!$('ivStaff').querySelector('svg')})}
 return{tonics:T,scales:out,circle,iv,levels:SCALES.map(s=>[s.k,s.l]),ivlev:IVS.map(x=>[x.k,x.l])}}"""

CHORDS_JS = r"""()=>{S.level=6;location.hash='seed';room('seed');const out=[];const cap=[];const ds=drawStaff;
 window.drawStaff=function(el,notes){if(el&&el.id==='staff')cap.push(notes.map(n=>({n:n.name,o:n.oct,m:n.midi})));return ds.apply(this,arguments)};
 for(const L of 'CDEFGAB')for(const a of ['bb','b','','#','##'])for(const q of Q){S.root=L+a;S.q=q.k;cap.length=0;let err=null;try{render();__scan(document.body,`chords ${L+a} ${q.k}`)}catch(e){err=String(e).slice(0,160)}
  out.push({root:L+a,q:q.k,err,notes:cap[cap.length-1]||null,resp:$('staff').dataset.resp||'',svg:!!$('staff').querySelector('svg'),note:($('staff').querySelector('.sfnote')||{}).textContent||''})}
 window.drawStaff=ds;return out}"""


INVFRET_JS = r"""([inst,L])=>{S.level=6;location.hash='seed';room('seed');const out=[];
 for(const a of ['bb','b','','#','##'])for(const q of Q)for(let inv=0;inv<q.d.length;inv++){
  S.inst=inst;S.root=L+a;S.q=q.k;S.inv=inv;let err=null;try{render();__scan(document.body,`${inst} ${L+a} ${q.k} inv${inv}`)}catch(e){err=String(e).slice(0,160)}
  out.push({inst,root:L+a,q:q.k,inv,err,cap:$('invTxt').textContent,d:q.d[inv],board:[...document.querySelectorAll('.board svg text')].map(t=>t.textContent)})}
 S.inst='piano';S.inv=0;return out}"""


# R10 (0.48): no rendered label may spell a double accidental as two characters. The page-side scanner walks every text
# node (and title / aria-label / alt attributes) and records any "♭b", "♭♭", "♯♯", "♯#", "##" or a note letter followed by
# "bb" used as an accidental (so "Bbb", "Bbbm7", but not words such as "Abbey").
SCAN_JS = r"""()=>{window.__BAD=new Map();window.__N=0;
 window.__RX=/♭b|♭♭|♯♯|♯#|##|(^|[^A-Za-z])[A-G]bb(?=$|[^a-z]|m|M|maj|dim|aug|sus|add)/;
 window.__SEEN=new Set();
 const chk=(s,w)=>{if(window.__SEEN.has(s))return;if(window.__SEEN.size<200000)window.__SEEN.add(s);window.__N++;const m=window.__RX.exec(s);if(m){const k=s.slice(Math.max(0,m.index-12),m.index+16).replace(/\s+/g,' ');if(!window.__BAD.has(k))window.__BAD.set(k,w)}};
 window.__scan=function(root,w){root=root||document.body;const tw=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;
  while(n=tw.nextNode()){const p=n.parentNode;if(p&&/^(SCRIPT|STYLE)$/.test(p.nodeName))continue;chk(n.nodeValue,w||'')}
  root.querySelectorAll('[title],[aria-label],[alt]').forEach(e=>{for(const a of ['title','aria-label','alt'])if(e.hasAttribute(a))chk(e.getAttribute(a),(w||'')+' @'+a)})}}"""


def check_inversions(R):
    """0.48 fix round: the inversion caption and the fretboard labels spell a double flat as one glyph (a diminished 7th's
    bb7 is shown as the double-flat sign then 7, never as two flat signs)."""
    def degp(d):
        return d.replace('bb', '𝄫').replace('##', '𝄪').replace('b', '♭').replace('#', '♯')
    ORDN = ['', '1st', '2nd', '3rd', '4th', '5th', '6th']
    for r in R:
        where = f"{r['inst']} {r['root']} {r['q'] or 'major'} inversion {r['inv']}"
        if r['err']:
            fail('G', f"{where}: render throws: {r['err']}")
            continue
        want = 'Root position: the root is in the bass' if not r['inv'] else f"{ORDN[r['inv']]} inversion: the {degp(r['d'])} is in the bass"
        # the augmented-sixth chords list their notes in a different order from the inversions, so only the form is checked there
        if r['q'] in ('It+6', 'Fr+6', 'Ger+6'):
            if not re.fullmatch(r"Root position: the root is in the bass|(1st|2nd|3rd) inversion: the [♭♯𝄫𝄪]?\d is in the bass", r['cap']):
                fail('G', f"{where}: caption '{r['cap']}' is not in the usual form")
            else:
                ok('G', 'inversion captions (augmented sixths: form only)')
        elif r['cap'] != want:
            fail('G', f"{where}: caption '{r['cap']}' vs '{want}'")
        else:
            ok('G', 'inversion captions')
        bad = [t for t in r['board'] if re.search(r'♭b|♭♭|♯♯|♯#|bb|##', t)]
        if bad:
            fail('G', f"{where}: fretboard labels {bad[:3]} use two characters for a double accidental")
        else:
            ok('G', 'fretboard degree labels')


async def collect_scan(pg, where):
    bad = await pg.evaluate("()=>[[...window.__BAD.entries()],window.__N]")
    COUNT['G distinct rendered strings scanned for two-character double accidentals'] += bad[1]
    for k, w in bad[0]:
        fail('G', f"{where}: label text contains a two-character double accidental: '{k}' ({w})")


def accn(name):
    return name[1:].count('#') - name[1:].count('b')


def check_resp(sec, where, names, resp, note_ok=True):
    """R3: the stave never receives more than a double accidental. Every triple in `names` (app spelling, '#'/'b')
    must be flagged in the frame's data-resp as from>to, and the respelling must be the same pitch (music21) with
    at most a double accidental on an adjacent letter."""
    triples = sorted({n for n in names if abs(accn(n)) > 2})
    got = dict(x.split('>') for x in resp.split(',') if x) if resp else {}
    if not triples:
        if got:
            fail(sec, f"{where}: flagged {resp} but nothing needs a triple accidental")
        return
    COUNT['R3: stave views that reach a triple accidental'] += 1
    for t in triples:
        if t not in got:
            fail(sec, f"{where}: {t} reaches the stave unflagged")
            continue
        to = got[t]
        pa, pb = m21pitch.Pitch(t.replace('b', '-')), m21pitch.Pitch(to.replace('b', '-'))
        if pa.pitchClass != pb.pitchClass or abs(accn(to)) > 2 or (('CDEFGAB'.index(to[0]) - 'CDEFGAB'.index(t[0])) % 7) not in (1, 6):
            fail(sec, f"{where}: {t} respelled as {to}: not the same note on a neighbouring letter")
        else:
            ok(sec, 'triple accidental respelled and flagged')
    if not note_ok:
        fail(sec, f"{where}: no visible 'Theoretical spelling' note")


def check_chords_room(R):
    for r in R:
        where = f"Chords room {r['root']}{r['q']}"
        if r['err']:
            fail('R', f"{where}: throws while drawing: {r['err']}")
            continue
        if r['notes'] is None:
            continue
        ok('R', 'Chords room staves drawn')
        if not r['svg']:
            fail('R', f"{where}: no stave drawn")
        check_resp('R', where, [n['n'] for n in r['notes']], r['resp'], ('Theoretical spelling' in r['note']) or not r['resp'])


def ivname(iv):
    n = iv.generic.undirected
    if n == 8 and iv.name == 'P8':
        return 'octave'
    ordn = {1: '1st (unison)', 2: '2nd', 3: '3rd'}.get(n, f'{n}th')
    return f"{IVQ[iv.name[0]]} {ordn}"


IVQ = {'P': 'perfect', 'M': 'major', 'm': 'minor', 'A': 'augmented', 'd': 'diminished'}


def check_keys(D):
    # ---- K: scales
    for r in D['scales']:
        t, sk, desc = r['t'], r['sc'], r['desc']
        where = f"{prettyname(t)} {sk}{' down' if desc else ''}"
        exp = expected_scale(t, sk, desc)
        if r['err']:
            fail('K', f"{where}: the Scales tab throws while drawing: {r['err']}")
        if r.get('staff'):
            if not r['svg']:
                fail('K', f"{where}: no stave drawn")
            check_resp('K', where, r['staff']['names'], r['resp'])
        got = [m21name(x['n']) for x in r['tiles']]
        if got != exp:
            fail('K', f"{where}: spelled {' '.join(map(pretty, got))}, music21 {' '.join(map(pretty, exp))}")
        else:
            ok('K', 'scale spellings')
        # pitch classes and direction
        pcs = [x['m'] % 12 for x in r['tiles']]
        if pcs != [m21pitch.Pitch(n).pitchClass for n in got]:
            fail('K', f"{where}: sounding pitches {pcs} do not match the spelled names")
        else:
            ok('K', 'pitch classes')
        ms = [x['m'] for x in r['tiles']]
        mono = all(b > a for a, b in zip(ms, ms[1:])) if not desc else all(b < a for a, b in zip(ms, ms[1:]))
        if not mono or abs(ms[-1] - ms[0]) != 12:
            fail('K', f"{where}: pitches not a one-octave {'descending' if desc else 'ascending'} line: {ms}")
        steps = []
        for a, b in zip(ms, ms[1:]):
            s = abs(b - a)
            steps.append('S' if s == 1 else 'T' if s == 2 else 'T+S' if s == 3 else str(s))
        if steps != r['steps']:
            fail('K', f"{where}: step labels {r['steps']} vs {steps}")
        else:
            ok('K', 'step patterns')
        # degree numbers
        degs = [degree_label(t, n) for n in got]
        gotd = [x['d'] for x in r['tiles']]
        if gotd != degs:
            fail('K', f"{where}: degree labels {' '.join(gotd)} vs {' '.join(degs)}")
        else:
            ok('K', 'degree labels')
        # solfa
        do = do_of(t, sk)
        sol = [solfa_of(do, n) for n in got]
        gots = [x['so'] for x in r['tiles']]
        if gots != sol:
            fail('K', f"{where}: solfa {' '.join(gots)} vs {' '.join(sol)} (do = {pretty(do.name)})")
        else:
            ok('K', 'solfa')
        want = sol if (desc and r['hasDesc']) else (list(reversed(sol)) if desc else sol)[:-1]
        if r['sol'].split(' ') != want:
            fail('K', f"{where}: solfa line '{r['sol']}' vs {' '.join(want)}")
        # hand-sign ladder agrees with the tiles
        lad = sorted((x['nm'], x['sy']) for x in r['ladder'])
        if lad != sorted((x['n'], x['so']) for x in r['tiles']):
            fail('K', f"{where}: hand-sign ladder disagrees with the tiles")
        # key signature
        pm = parent_major(t, sk)
        txt = r['sig']
        if pm is None:
            if 'No key signature' not in txt or r['staff'] and r['staff']['ksig']:
                fail('K', f"{where}: should have no key signature: '{txt}'")
            else:
                ok('K', 'key signatures')
        else:
            n = sig_sharps(pm)
            theo = abs(n) > 7
            if theo:
                alt = enharmonic_alt(t, sk)
                good = 'theoretical' in txt.lower() and r['sigRed'] and f"{abs(n)} {'sharps' if n > 0 else 'flats'}" in txt \
                    and pretty(pm) in txt
                if not good:
                    fail('K', f"{where}: theoretical key ({pretty(pm)} major, {abs(n)} {'sharps' if n > 0 else 'flats'}) not flagged correctly: '{txt}'")
                elif (r['alt'] and m21name(r['alt'])) != alt:
                    fail('K', f"{where}: enharmonic offered {r['alt']}, expected {alt}")
                else:
                    ok('K', 'theoretical keys flagged with the enharmonic')
                if r['staff'] and r['staff']['ksig']:
                    fail('K', f"{where}: staff drawn with key signature {r['staff']['ksig']} for a theoretical key")
            else:
                if not txt.startswith(sig_text(n)):
                    fail('K', f"{where}: key signature '{txt}' vs '{sig_text(n)}'")
                elif sk not in ('maj', 'ion', 'mpent', 'chrom') and f'the key signature of {pretty(pm)} major' not in txt:
                    fail('K', f"{where}: '{txt}' should name {pretty(pm)} major as the parent")
                else:
                    ok('K', 'key signatures')
                if not r['staff'] or m21name(r['staff']['ksig'] or 'C') != pm:
                    fail('K', f"{where}: staff key signature {r['staff'] and r['staff']['ksig']} vs {pretty(pm)} major")
                else:
                    ok('K', 'staff key signatures')
        if r['staff'] and [m21name(x) for x in r['staff']['names']] != got:
            fail('K', f"{where}: staff notes {r['staff']['names']} differ from the tiles")
        # chords of the key
        if r['chords'] and not r['err'] and len(exp) == 8:
            names7 = exp[:7] if not desc else list(reversed(exp))[:7]
            if sk == 'mmin':
                names7 = expected_scale(t, 'mmin', False)[:7]
            minorish = sk in ('nmin', 'hmin', 'mmin')
            for row, sev in zip(r['chords'], [False, True]):
                for i, c in enumerate(row):
                    ps = stacked_chord(names7, i, sev)
                    q = chord_quality(ps)
                    root = ps[0].name
                    lower = q in ('m', 'dim', 'm7', 'mMaj7', 'm7b5', 'dim7')
                    num = ROM[i].lower() if lower else ROM[i]
                    if not minorish:
                        num = degree_label(t, root)[:-1] + num
                    num += NUMSUF.get(q, '')
                    sym = pretty(root) + SYMSUF.get(q, '?')
                    if c['sym'] != sym or c['num'] != num:
                        fail('K', f"{where}: chord {i+1}{' (7th)' if sev else ''} shows {c['num']} {c['sym']}, expected {num} {sym}")
                    else:
                        ok('K', 'chords of the key')

    # ---- C: circle
    CMAJ = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'Db', 'Ab', 'Eb', 'Bb', 'F']
    for c in D['circle']:
        i, mn = c['i'], c['minor']
        maj = m21key.Key(m21name(CMAJ[i]))
        k = maj.relative if mn else maj
        where = f"circle {pretty(k.tonic.name)} {'minor' if mn else 'major'}"
        exp_title = f"{pretty(k.tonic.name)} {'minor' if mn else 'major'}"
        if c['title'] != exp_title:
            fail('C', f"{where}: title '{c['title']}'")
        if not c['ctx'].startswith(sig_text(k.sharps)):
            fail('C', f"{where}: signature '{c['ctx']}' vs '{sig_text(k.sharps)}'")
        else:
            ok('C', 'key signatures')
        # enharmonic twin: same pitch class, other letter, signature 12 - n the other way
        m = re.search(r'also written as (\S+) (major|minor) \((\d+) (sharps|flats)\)', c['ctx'])
        if m:
            tw = m21key.Key(m21name(m.group(1)) if m.group(2) == 'major' else m21name(m.group(1)).lower())
            if tw.tonic.pitchClass != k.tonic.pitchClass or abs(tw.sharps) != int(m.group(3)) or \
                    (tw.sharps > 0) != (m.group(4) == 'sharps') or tw.mode != k.mode:
                fail('C', f"{where}: enharmonic twin text wrong: '{m.group(0)}'")
            else:
                ok('C', 'enharmonic twins')
        elif abs(k.sharps) >= 5:
            fail('C', f"{where}: no enharmonic twin given for a {abs(k.sharps)}-accidental key")
        rel, par, nb = c['dd'][0], c['dd'][1], c['dd'][2]
        R = k.relative
        if not rel.startswith(f"{pretty(R.tonic.name)} {'major' if mn else 'minor'}"):
            fail('C', f"{where}: relative '{rel}' vs {pretty(R.tonic.name)}")
        else:
            ok('C', 'relative keys')
        Pk = k.parallel
        if not par.startswith(f"{pretty(Pk.tonic.name)} {'major' if mn else 'minor'}"):
            fail('C', f"{where}: parallel '{par}' vs {pretty(Pk.tonic.name)}")
        elif abs(Pk.sharps) > 7:
            # R11 (0.48): flagged as a theoretical key, with the usual enharmonic equivalent
            eq = Pk.tonic.getEnharmonic()
            eqn = pretty(eq.name)
            word = 'sharps' if Pk.sharps > 0 else 'flats'
            if 'theoretical' not in par.lower() or f"{abs(Pk.sharps)} {word}" not in par or f"{eqn} {'major' if mn else 'minor'}" not in par:
                fail('C', f"{where}: parallel key {pretty(Pk.tonic.name)} {Pk.mode} is theoretical ({abs(Pk.sharps)} {word}) and is not flagged as such with {eqn} {'major' if mn else 'minor'}: '{par}'")
            elif m21key.Key(eq.name if mn else eq.name.lower()).sharps is not None and abs(m21key.Key(eq.name if mn else eq.name.lower()).sharps) > 7:
                fail('C', f"{where}: equivalent {eqn} is itself theoretical")
            else:
                ok('C', 'theoretical parallel keys flagged with the usual equivalent')
        else:
            ok('C', 'parallel keys')
        dom = k.tonic.transpose('P5')
        sub = k.tonic.transpose('P4')
        # neighbours: the key a perfect fifth up (dominant) and a fifth down (subdominant), spelled exactly as music21 spells them
        # (0.48 fix round: D-flat major's subdominant was shown as F-sharp, B-flat minor's as D-sharp)
        word = 'minor' if mn else 'major'
        mm = re.match(r'(\S+) (major|minor) \(one step clockwise.*\) · (\S+) (major|minor) \(one step back', nb)
        if not mm:
            fail('C', f"{where}: neighbours text '{nb}'")
        else:
            for got, gw, want, lab in [(mm.group(1), mm.group(2), dom, 'dominant'), (mm.group(3), mm.group(4), sub, 'subdominant')]:
                g = m21key.Key(m21name(got).lower() if mn else m21name(got))
                wk = m21key.Key(want.name.lower() if mn else want.name)
                if gw != word:
                    fail('C', f"{where}: {lab} key is called {gw}, the home key is {word}")
                elif abs(wk.sharps) <= 7 and got != pretty(want.name):
                    fail('C', f"{where}: {lab} key shows {got} {gw}, music21 spells it {pretty(want.name)}")
                elif g.tonic.pitchClass != want.pitchClass or abs(g.sharps) > 7:
                    fail('C', f"{where}: {lab} key {got} vs {pretty(want.name)}")
                else:
                    ok('C', 'neighbour keys (exact spelling)')
        # modes from the parent major
        names = [p.name for p in m21scale.MajorScale(maj.tonic).getPitches()[:7]]
        modes = ['ion', 'dor', 'phr', 'lyd', 'mix', 'nmin', 'loc']
        mnames = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian']
        syl = ['do', 're', 'mi', 'fa', 'so', 'la', 'ti']
        for j, ch in enumerate(c['modes']):
            want = f"{appname(names[j])}|{modes[j]}"
            if ch['v'] != want or not ch['t'].startswith(f"{pretty(names[j])} {mnames[j]}") or f'on {syl[j]}' not in ch['t']:
                fail('C', f"{where}: mode chip {j+1} '{ch['t']}' ({ch['v']}) vs {pretty(names[j])} {mnames[j]} on {syl[j]}")
            else:
                ok('C', 'mode chips')
        if c['open'] != f"{appname(k.tonic.name)}|{'nmin' if mn else 'maj'}":
            fail('C', f"{where}: 'Open in Scales' goes to {c['open']}")

    # ---- I: intervals
    for r in D['iv']:
        a = P(r['start'])
        a.octave = 4
        iv = m21int.Interval(r['k'])
        b = a.transpose(iv if r['dir'] == 'up' else iv.reverse())
        where = f"{prettyname(r['start'])} {r['k']} {r['dir']}"
        want_sub = f"{pretty(a.name)} {r['dir']} to {pretty(b.name)}"
        if r['err']:
            fail('I', f"{where}: the Intervals tab throws while drawing: {r['err']}")
        elif not r['svg']:
            fail('I', f"{where}: no stave drawn")
        else:
            check_resp('I', where, [appname(a.name), appname(b.name)], r['resp'])
        if r['sub'] != want_sub:
            fail('I', f"{where}: shows '{r['sub']}', music21 '{want_sub}'")
        else:
            ok('I', 'interval spellings')
        if r['name'] != ivname(iv):
            fail('I', f"{where}: name '{r['name']}' vs '{ivname(iv)}'")
        num, semis, qual = r['dd'][0], r['dd'][1], r['dd'][2]
        if semis.strip() != str(iv.semitones):
            fail('I', f"{where}: {semis} semitones, music21 {iv.semitones}")
        else:
            ok('I', 'semitone counts')
        gnum = iv.generic.undirected
        if not num.startswith(str(gnum)) or f"from {a.step} to {b.step}" not in num:
            fail('I', f"{where}: number text '{num}'")
        if not qual.startswith('octave' if r['k'] == 'P8' else IVQ[r['k'][0]]):
            fail('I', f"{where}: quality text '{qual}'")
        inv = iv.complement
        if not r['dd'][4].startswith(f"{ivname(inv)} ({inv.name})"):
            fail('I', f"{where}: inversion '{r['dd'][4]}' vs {ivname(inv)} ({inv.name})")
        else:
            ok('I', 'inversions')
        lit = sorted(r['kb'])
        if sorted([lit[0] % 12, lit[-1] % 12]) != sorted([a.pitchClass, b.pitchClass]) or abs(lit[-1] - lit[0]) != iv.semitones:
            fail('I', f"{where}: keyboard lights {lit} do not span {iv.semitones} semitones from {a.name}")


# ================================================================= Climbs 3-12
CLIMBS_JS = r"""async()=>{
 const CAP=[],SEEN=new Set(),DOM=[],ERR=[];let CTX='';
 const nm=c=>{const C=chordOf(c.root,c.q,c.inv||0);return{root:c.root,q:c.q,inv:c.inv||0,rn:c.rn||null,names:C.tones.map(t=>t.name),bass:C.bass.name}};
 const put=o=>{const k=JSON.stringify(o);if(SEEN.has(k))return;SEEN.add(k);o.ctx=CTX;CAP.push(o)};
 const W=(name,post)=>{const f=window[name];window[name]=function(...a){const r=f.apply(this,a);try{post(a,r)}catch(e){ERR.push(CTX+' hook '+name+': '+e)}return r}};
 W('realise',(a,r)=>put({t:'real',str:a[0],key:{k:a[1].k,mode:a[1].mode},L:r.L.map(nm),sat:r.sat}));
 W('c4List',(a,r)=>put({t:'list',toks:a[0].bars.split(' '),key:a[0].k==='mblues'?{k:a[1].k,mode:'min'}:{k:a[1].k,mode:a[1].mode},L:r.map(nm)}));
 W('c5List',(a,r)=>put({t:'list',toks:r.list.map(c=>c.rn),key:{...r.key},L:r.list.map(nm)}));
 W('voiceProg',(a,r)=>put({t:'vp',L:a[0].map(nm),V:r.map(v=>({bass:v.bass.midi,rh:v.rh.map(x=>x.midi)}))}));
 W('c9List',(a,r)=>put({t:'jazz',toks:a[0].split(' '),key:{k:a[1].k,mode:a[1].mode},L:r.map(c=>({...nm(c),kind:c.kind}))}));
 W('c9Voice',(a,r)=>put({t:'c9v',vt:a[1],V:r.map(v=>({bass:v.bass.name,bm:v.bass.midi,up:v.up.map(n=>n.name),um:v.up.map(n=>n.midi),root:v.ch.root,kind:v.ch.kind,rn:v.ch.rn,sym:c9Sym(v.ch,a[1])}))}));
 W('c11Ch',(a,r)=>{if(r&&r.root)put({t:'jazz',toks:[a[0]],key:{k:a[1].k,mode:a[1].mode},L:[nm(r)]})});
 const scrape=key=>{__scan(document.querySelector('#climbDetail'),CTX);const bars=[...document.querySelectorAll('#climbDetail .bar')].map(e=>({b:(e.querySelector('b')||{}).textContent||'',s:(e.querySelector('span')||{}).textContent||''}));
  const rn=[...document.querySelectorAll('#climbDetail svg text.rnl')].map(e=>({s:e.dataset.rnraw,b:e.dataset.sym||''}));
  DOM.push({ctx:CTX,key:key?{k:key.k,mode:key.mode}:null,bars,rn})};
 const R=(key)=>{try{renderClimbDetail()}catch(e){ERR.push(CTX+': '+String(e).slice(0,200))}scrape(key)};
 const LV=[4,5,6];ROOM='climbs';
 const quiz=(fn,n)=>{for(let i=0;i<n;i++){try{fn()}catch(e){ERR.push(CTX+' quiz: '+String(e).slice(0,160))}stopAll()}};
 for(const lv of LV){S.level=lv;
  // climb 3
  CL.open=2;for(const key of CKEYS){CL.key={...key};for(const c of cadsFor(key.mode)){CL.ex=c.k;CTX=`c3 L${lv} ${keyName(key)} ${c.k}`;R(key)}}
  CTX=`c3 L${lv} quiz`;quiz(detNew,40);
  // climb 4
  CL.open=3;for(const key of C4KEYS){C4.key={...key};for(const x of C4EX.filter(x=>x.l<=lv)){C4.ex=x.k;CTX=`c4 L${lv} ${keyName(key)} ${x.k}`;R(x.k==='mblues'?{k:key.k,mode:'min'}:key)}}
  // climb 5
  CL.open=4;for(const key of C5KEYS){C5.key={...key};for(const f of C5FAM.filter(x=>x.l<=lv))for(const rot of (f.k==='pop'?[0,1,2,3]:[0])){C5.fam=f.k;C5.rot=rot;
   for(let v=0;v<16;v++){C5.v={inv:!!(v&1),pedal:!!(v&2),iv:!!(v&4),sus:!!(v&8)};CTX=`c5 L${lv} ${keyName(key)} ${f.k} rot${rot} v${v}`;if(v===0)R(f.k==='aeol'?{k:(key.k+9)%12,mode:'min'}:key);else{const{list}=c5List();voiceProg(list)}}}}
  C5.v={inv:false,pedal:false,iv:false,sus:false};
  // climb 6
  CL.open=5;for(const key of CKEYS){C6.key={...key};C6.walk=[0];for(const x of C6EX.filter(x=>x.l<=lv&&x[key.mode])){C6.ex=x.k;CTX=`c6 L${lv} ${keyName(key)} ${x.k}`;R(key)}
   CTX=`c6 L${lv} ${keyName(key)} walk`;for(let s=0;s<7;s++){try{c6Walk(mod(C6.walk[C6.walk.length-1]+3,7))}catch(e){ERR.push(CTX+': '+e)}}stopAll();R(key);C6.walk=[0]}
  CTX=`c6 L${lv} quiz`;quiz(c6QNew,40);
  // climb 7
  CL.open=6;for(const key of CKEYS){C7.key={...key};for(const x of C7EX.filter(x=>x.l<=lv&&x[key.mode])){C7.ex=x.k;CTX=`c7 L${lv} ${keyName(key)} ${x.k}`;R(key)}
   const n=c7Base(key.mode).length;for(let m=0;m<(1<<n);m++){C7.ins={};for(let i=0;i<n;i++)if(m&(1<<i))C7.ins[key.mode+i]=1;CTX=`c7 L${lv} ${keyName(key)} built ${c7Built(key.mode)}`;realise(c7Built(key.mode),key)}C7.ins={}}
  CTX=`c7 L${lv} quiz`;quiz(c7QNew,40);
  // climb 8
  CL.open=7;for(const key of CKEYS){C8.key={...key};for(const x of C8EX.filter(x=>x.l<=lv&&x[key.mode])){C8.ex=x.k;CTX=`c8 L${lv} ${keyName(key)} ${x.k}`;R(key)}
   const md=key.mode,sizes=C8SW[md].map(a=>a.filter(z=>(z.l||4)<=lv).length);
   const combos=sizes.reduce((acc,n)=>acc.flatMap(c=>[...Array(n).keys()].map(i=>c.concat([i]))),[[]]);
   for(const c of combos)for(const f of [0,1]){C8.sw={};c.forEach((i,j)=>C8.sw[md+j]=i);C8.sw[md+'f']=f;CTX=`c8 L${lv} ${keyName(key)} built ${c8Built(md)}`;realise(c8Built(md),key)}C8.sw={}}
  CTX=`c8 L${lv} quiz`;quiz(c8QNew,40);
  // climb 9
  CL.open=8;for(const key of C9KEYS){C9.key={...key};for(const x of C9EX.filter(x=>x.l<=Math.max(lv,5)&&x[key.mode]))for(const vt of ['guide','shell','rootless'])for(const st of ['A','B']){C9.ex=x.k;C9.vt=vt;C9.start=st;CTX=`c9 L${lv} ${keyName(key)} ${x.k} ${vt} ${st}`;R(key)}}
  CTX=`c9 L${lv} quiz`;quiz(c9QNew,40);
  // climb 10
  CL.open=9;for(const key of C9KEYS){C10.key={...key};for(const x of C10EX.filter(x=>x.l<=Math.max(lv,5)&&x[key.mode]))for(const sub of [false,true])for(const vt of ['guide','shell','rootless']){C10.ex=x.k;C10.sub=sub;C10.vt=vt;CTX=`c10 L${lv} ${keyName(key)} ${x.k} sub${+sub} ${vt}`;R(key)}
   for(let m=0;m<16;m++){C10.sw={};for(let i=0;i<4;i++)if(m&(1<<i))C10.sw[i+1]=1;CTX=`c10 L${lv} ${keyName(key)} built ${c10Built()}`;R(key)}C10.sw={}}
  CTX=`c10 L${lv} quiz`;quiz(c10QNew,40);
  // climb 11
  CL.open=10;for(const key of C11KEYS){C11.key={...key};for(const v of C11V.filter(v=>v.l<=Math.max(lv,4))){C11.ver=v.k;CTX=`c11 L${lv} ${keyName(key)} ${v.k}`;R(key);c11Voice(v.r.split(' ').map(r=>c11Ch(r,key)),c11Mel(key))}
   CTX=`c11 L${lv} ${keyName(key)} vocabulary`;[4,5,6].filter(l=>l<=lv).forEach(l=>C11VOC[l].forEach(r=>c11Ch(r,key)))}
  // climb 12
  CL.open=11;for(const tab of ['vamp','plane','med','static']){C12.tab=tab;CTX=`c12 L${lv} ${tab}`;R(null)}
 }
 S.level=6;const C12OUT={vamp:[],plane:[],cue:[],tin:[]};
 for(const m of C12MODES)for(const t of [0,2,4,5,7,9]){C12.mode=m.k;C12.tonic=t;const v=c12Vamp();C12OUT.vamp.push({mode:m.k,toks:m.r.split(' '),key:{k:t,mode:m.mode},L:v.L.map(nm),cols:v.cols,tn:v.tn,cn:v.cn.name,ch:m.ch});C12.tab='vamp';CTX=`c12 vamp ${m.k} ${t}`;R(null)}
 for(const sh of C12SHAPES)for(const pl of ['real','dia'])for(let mi=0;mi<C12MEL.length;mi++){C12.shape=sh.k;C12.plane=pl;C12.mel=mi;
  C12OUT.plane.push({shape:sh.k,plane:pl,mel:mi,ch:c12Plane().map(c=>({n:c.n,names:c.n.map((m,j)=>spell(c.li[j],m).name),mel:c.mel}))});C12.tab='plane';CTX=`c12 plane ${sh.k} ${pl} ${mi}`;R(null)}
 const MK=C12MED.map(x=>x.k);for(const a of MK)for(const b of [null,...MK])for(const c of (b?[null,...MK]:[null])){C12.cue=['I',a,b,c].filter(Boolean);const cue=c12Cue();C12OUT.cue.push({cue:C12.cue.slice(),chords:cue.map(x=>({root:x.root,q:x.q,lab:x.lab,names:chordOf(x.root,x.q,0).tones.map(t=>t.name)})),cols:c12CueCols(cue)})}
 C12.tab='med';CTX='c12 med';R(null);
 for(let l=0;l<C12TIN.length;l++)for(const pos of ['sup','inf','alt']){C12.tin={line:l,pos};C12OUT.tin.push({line:l,pos,v:c12Tin()})}
 stopAll();CL.open=null;
 return{CAP,DOM,ERR,C12:C12OUT}}"""

KEYN = {'maj': ['C', 'Db', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B'],
        'min': ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'G#', 'A', 'Bb', 'B']}   # this file's own table of key names


def mkey(k):
    return key_of(KEYN[k['mode']][k['k']], k['mode'])


def kname(k):
    return f"{pretty(KEYN[k['mode']][k['k']])} {'major' if k['mode'] == 'maj' else 'minor'}"


TOKRX = re.compile(r'^([b#]?)(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)([^/:]*)(?:/([^:]+))?(?::(\d))?$')
JAZZQ = {('', True): '', ('', False): 'm', ('7', True): '7', ('7', False): 'm7', ('maj7', True): 'maj7', ('maj7', False): 'maj7',
         ('ø7', False): 'm7b5', ('°', False): 'dim', ('o', False): 'dim', ('°7', False): 'dim7', ('9', True): '9',
         ('9', False): 'm9', ('6', True): '6', ('6', False): 'm6', ('sus4', True): 'sus4', ('+', True): 'aug',
         ('maj9', True): 'M9'}


def figure(tok):
    """'ii°:1' -> 'iio6', 'I:2' -> 'I64', 'V7/V' -> 'V7/V', 'bII:1' -> 'bII6'"""
    rn, _, inv = tok.partition(':')
    rn = rn.replace('°', 'o')
    if inv in ('1', '2', '3'):
        base, slash, sec = rn.partition('/')
        if '7' in base:
            base = base.replace('7', {'1': '65', '2': '43', '3': '42'}[inv], 1)
        else:
            base = base + {'1': '6', '2': '64'}[inv]
        rn = base + slash + sec
    return rn


def classical(tok, k):
    """music21 RomanNumeral: (spelled names, bass name)"""
    r = roman.RomanNumeral(figure(tok), mkey(k))
    return [p.name for p in r.pitches], r.bass().name


def symbolic(tok, k):
    """Jazz / chord-symbol convention: root from music21 RomanNumeral, quality from the suffix, notes from ChordSymbol."""
    m = TOKRX.match(tok)
    if not m:
        raise ValueError(f'cannot parse token {tok}')
    acc, num, suf, sec, inv = m.groups()
    up = num == num.upper()
    bare = acc + num + (('/' + sec) if sec else '')
    root = roman.RomanNumeral(bare.replace('°', 'o'), mkey(k)).root()
    q = JAZZQ.get((suf.replace('M7', 'maj7').replace('Δ', 'maj7'), up))
    if q is None:
        raise ValueError(f'unknown quality {suf} in {tok}')
    cs = harmony.ChordSymbol(root.name + q)
    names = [p.name for p in cs.pitches]
    order = [cs.root(), cs.third if q != 'sus4' else cs.getChordStep(4), cs.fifth, cs.seventh]
    i = int(inv or 0)
    bass = order[i].name if order[i] is not None else None
    return names, bass


def sym_names(sym):
    """Displayed chord symbol ('G7♭9♭13', 'Cmaj9', 'Bm7♭5') -> music21 names"""
    s = sym.replace('♭', 'b').replace('♯', '#').replace('𝄫', 'bb').replace('𝄪', '##')
    m = re.match(r'^([A-G](?:bb|##|b|#)?)(.*)$', s)
    root, suf = m.groups()
    suf = {'maj9': 'M9'}.get(suf, suf)
    return [p.name for p in harmony.ChordSymbol(m21name(root) + suf).pitches]


CLASSICAL = ('c3', 'c6', 'c7', 'c8')


def check_chords(cap, sec):
    """cap: {'toks', 'key', 'L'} with L the app's chords. Compare names and bass against the oracle."""
    k = cap['key']
    toks = cap['toks']
    if len(toks) != len(cap['L']):
        fail(sec, f"{cap['ctx']}: {len(toks)} tokens but {len(cap['L'])} chords")
        return []
    exp = []
    conv = 'classical' if cap['ctx'].split()[0] in CLASSICAL else 'symbol'
    for tok, c in zip(toks, cap['L']):
        if cap['ctx'].startswith('c5') and ':' not in tok and c['inv']:
            tok = f"{tok}:{c['inv']}"   # climb 5's 'V in first inversion' variant keeps the label V and sets the inversion
        try:
            if conv == 'classical' or re.match(r'^(It|Fr|Ger)6$', tok):
                names, bass = classical(tok, k)
            else:
                try:
                    names, bass = symbolic(tok, k)
                except ValueError:
                    names, bass = classical(tok, k)
        except Exception as e:
            fail(sec, f"{cap['ctx']}: oracle cannot read '{tok}' ({e})")
            exp.append(None)
            continue
        got = [m21name(n) for n in c['names']]
        where = f"{cap['ctx']} [{kname(k)}] {tok}"
        if sorted(got) != sorted(names):
            fail(sec, f"{where}: app spells {' '.join(map(pretty, got))}, music21 {' '.join(map(pretty, names))}")
        elif bass and m21name(c['bass']) != bass:
            fail(sec, f"{where}: bass {pretty(m21name(c['bass']))}, music21 {pretty(bass)}")
        else:
            ok(sec, f"chords vs music21 ({conv})")
        exp.append((names, bass))
    return exp


def pcs_of(names):
    return {m21pitch.Pitch(n).pitchClass for n in names}


def check_satb(cap, exp, sec):
    sat = cap['sat']
    if sat is None:
        fail(sec, f"{cap['ctx']} [{kname(cap['key'])}] '{cap['str']}': no SATB realisation")
        return
    if len(sat) != len(exp):
        fail(sec, f"{cap['ctx']}: {len(sat)} SATB chords for {len(exp)} tokens")
        return
    toks = cap['str'].split(' ')
    for i, (col, e) in enumerate(zip(sat, exp)):
        if e is None:
            continue
        names, bass = e
        pcs = pcs_of(names)
        where = f"{cap['ctx']} [{kname(cap['key'])}] SATB chord {i+1} {toks[i]}"
        have = {m % 12 for m in col}
        bad = []
        if not have <= pcs:
            bad.append(f"non-chord notes {sorted(have - pcs)}")
        if bass and col[0] % 12 != m21pitch.Pitch(bass).pitchClass:
            bad.append(f"bass pc {col[0] % 12} should be {pretty(bass)}")
        if not re.match(r'^(It|Fr|Ger)6$', toks[i]):
            r = roman.RomanNumeral(figure(toks[i]), mkey(cap['key'])) if cap['ctx'].split()[0] in CLASSICAL else None
            if r is not None:
                need = {r.root().pitchClass, r.third.pitchClass}
                if not need <= have:
                    bad.append('root or 3rd missing')
        if any(col[v] > col[v + 1] for v in range(3)):
            bad.append(f'voices out of order {col}')
        if bad:
            fail(sec, f"{where}: {'; '.join(bad)}")
        else:
            ok(sec, 'SATB chords (chord tones, bass, root+3rd, order)')


def check_climbs(D):
    for e in D['ERR']:
        fail('X', e)
    real = [c for c in D['CAP'] if c['t'] == 'real']
    for c in real:
        c['toks'] = c['str'].split(' ')
        sec = 'R'
        exp = check_chords(c, sec)
        if exp:
            check_satb(c, exp, sec)
    for c in D['CAP']:
        if c['t'] in ('list', 'jazz'):
            sec = 'J' if c['ctx'].split()[0] in ('c9', 'c10', 'c11') else 'M' if c['ctx'].startswith('c12') else 'R'
            check_chords(c, sec)
        elif c['t'] == 'vp':
            sec = 'J' if c['ctx'].split()[0] in ('c9', 'c10', 'c11') else 'M' if c['ctx'].startswith('c12') else 'R'
            for i, (ch, v) in enumerate(zip(c['L'], c['V'])):
                pcs = pcs_of([m21name(n) for n in ch['names']])
                have = {m % 12 for m in v['rh']}
                if not have <= pcs or v['bass'] % 12 != m21pitch.Pitch(m21name(ch['bass'])).pitchClass:
                    fail(sec, f"{c['ctx']}: piano voicing {i+1} {pretty(ch['root'])}{ch['q']} has {sorted(have)} over bass {v['bass']}")
                else:
                    ok(sec, 'piano voicings (chord tones over the right bass)')
        elif c['t'] == 'c9v':
            for i, v in enumerate(c['V']):
                where = f"{c['ctx']} voicing {i+1} {v['rn']} = {v['sym']}"
                try:
                    names = sym_names(v['sym'])
                except Exception as e:
                    fail('J', f"{where}: oracle cannot read the symbol ({e})")
                    continue
                up = [m21name(n) for n in v['up']]
                bad = []
                if not set(up) <= set(names):
                    bad.append(f"notes {' '.join(map(pretty, sorted(set(up) - set(names))))} not in {v['sym']} ({' '.join(map(pretty, names))})")
                if m21name(v['bass']) != m21name(v['root']) or v['bm'] % 12 != m21pitch.Pitch(m21name(v['root'])).pitchClass:
                    bad.append(f"bass {v['bass']} is not the root {v['root']}")
                if [m % 12 for m in v['um']] != [m21pitch.Pitch(n).pitchClass for n in up]:
                    bad.append('sounding pitches differ from the spelling')
                if names[0] != m21name(v['root']):
                    bad.append(f"symbol root {names[0]} is not the chord root {v['root']}")
                # the extended symbol must contain the 7th chord the numeral asks for
                base = {'m7': 'm7', 'm7b5': 'm7b5', 'maj7': 'maj7', '7': '7', '7b9': '7'}[v['kind']]
                bn = [p.name for p in harmony.ChordSymbol(m21name(v['root']) + base).pitches]
                if not set(bn) <= set(names):
                    bad.append(f"{v['sym']} does not contain {v['root']}{base}")
                if c['vt'] in ('guide', 'shell'):
                    if len(up) != 2:
                        bad.append(f'{len(up)} upper notes for a {c["vt"]} voicing')
                if bad:
                    fail('J', f"{where}: {'; '.join(bad)}")
                else:
                    ok('J', 'jazz voicings vs chord symbols')
    # ---- climb 12
    C = D['C12']
    for v in C['vamp']:
        cap = {'ctx': f"c12 vamp {v['mode']}", 'toks': v['toks'], 'key': v['key'], 'L': v['L']}
        check_chords(cap, 'M')
        for i, col in enumerate(v['cols']):
            ch = v['L'][i % len(v['L'])]
            names = [m21name(n) for n in ch['names']]
            try:
                symn = sym_names(col['sym'])
            except Exception as e:
                fail('M', f"c12 vamp {v['mode']} {kname(v['key'])}: cannot read symbol {col['sym']} ({e})")
                continue
            have = {m % 12 for m in col['n']}
            if sorted(symn) != sorted(names) or not have <= pcs_of(names) or col['bass'] % 12 != m21pitch.Pitch(names[0]).pitchClass:
                fail('M', f"c12 vamp {v['mode']} {kname(v['key'])}: column {i+1} {col['sym']} has {sorted(have)} over {col['bass']}")
            else:
                ok('M', 'vamp voicings')
        # character note
        mk = {'dor': 'dorian', 'mix': 'mixolydian', 'aeo': 'aeolian', 'lyd': 'lydian', 'phr': 'phrygian'}[v['mode']]
        sc = {'dorian': m21scale.DorianScale, 'mixolydian': m21scale.MixolydianScale, 'aeolian': m21scale.MinorScale,
              'lydian': m21scale.LydianScale, 'phrygian': m21scale.PhrygianScale}[mk](P(v['tn']))
        deg = int(re.sub(r'\D', '', v['ch']))
        want = sc.pitchFromDegree(deg).name
        if m21name(v['cn']) != want:
            fail('M', f"c12 vamp {v['mode']} on {v['tn']}: character note {v['cn']} vs {pretty(want)}")
        else:
            ok('M', 'modal character notes')
    MED = {'iii': ('M3', 'm'), 'vi': ('M6', 'm'), 'III': ('M3', ''), 'bIII': ('m3', ''), 'VI': ('M6', ''), 'bVI': ('m6', '')}
    for c in C['cue']:
        prev = P('C')
        for i, ch in enumerate(c['chords'][1:]):
            iv, q = MED[c['cue'][i + 1]]
            want = prev.transpose(iv)
            names = [p.name for p in harmony.ChordSymbol(want.name + q).pitches]
            if m21name(ch['root']) != want.name or ch['q'] != q or sorted(map(m21name, ch['names'])) != sorted(names):
                fail('M', f"c12 mediants {'-'.join(c['cue'])}: chord {i+2} {ch['root']}{ch['q']} vs {pretty(want.name)}{q}")
            else:
                ok('M', 'chromatic mediant roots')
            prev = want
        for i, (col, ch) in enumerate(zip(c['cols'], c['chords'])):
            if not {m % 12 for m in col['n']} <= pcs_of(map(m21name, ch['names'])) or col['bass'] % 12 != m21pitch.Pitch(m21name(ch['root'])).pitchClass:
                fail('M', f"c12 mediants {'-'.join(c['cue'])}: voicing {i+1} wrong")
    SHAPE = {'tri': ['m6', 'P4'], 'org': ['P8', 'P4'], 'q3': ['m7', 'P4'], 'dom9': ['M9', 'm7', 'M3'], 'sowhat': ['P12', 'M9', 'M6', 'M3']}
    for pl in C['plane']:
        for i, ch in enumerate(pl['ch']):
            where = f"c12 planing {pl['shape']} {pl['plane']} melody {pl['mel']} chord {i+1}"
            names = ch['names']
            ps = []
            bad = []
            for n, m in zip(names, ch['n']):
                p = m21pitch.Pitch(m21name(n))
                p.octave = None
                if p.pitchClass != m % 12:
                    bad.append(f'{n} is not MIDI {m}')
                ps.append(m21pitch.Pitch(m21name(n), octave=(m - int(p.alter)) // 12 - 1))
            if pl['plane'] == 'real':
                got = [m21int.Interval(p, ps[-1]).name for p in ps[:-1]]
                if got != SHAPE[pl['shape']]:
                    bad.append(f"intervals below the tune {got} vs {SHAPE[pl['shape']]}")
            else:
                if any(len(n) > 1 for n in names):
                    bad.append(f'diatonic planing has accidentals {names}')
            if bad:
                fail('M', f"{where}: {'; '.join(bad)}")
            else:
                ok('M', 'planing spellings')
    for t in C['tin']:
        for i, x in enumerate(t['v']):
            if x['t'] % 12 not in (9, 0, 4):
                fail('M', f"c12 tintinnabuli line {t['line']} {t['pos']} note {i+1}: T-voice {x['t']} not in the A minor triad")
            else:
                ok('M', 'tintinnabuli T-voice')
    # ---- D: displayed labels
    check_dom(D['DOM'])


DISP = re.compile(r'^([♭♯]?)(VII|VI|IV|V|III|II|I|vii|vi|iv|v|iii|ii|i)')


def check_dom(DOM):
    for d in DOM:
        if not d['key']:
            continue
        items = [(x['s'], x['b']) for x in d['bars']] + [(x['s'], x['b']) for x in d['rn']]
        for rn, sym in items:
            rn = rn.strip()
            m = DISP.match(rn)
            if not m or not sym or re.match(r'^(It|Fr|Ger)', rn):
                continue
            sec = re.search(r'/([♭♯]?[IViv]+)', rn)
            bare = m.group(1).replace('♭', 'b').replace('♯', '#') + m.group(2) + ('/' + sec.group(1).replace('♭', 'b').replace('♯', '#') if sec else '')
            try:
                root = roman.RomanNumeral(bare, mkey(d['key'])).root().name
            except Exception:
                continue
            ms = re.match(r'^([A-G](?:𝄫|𝄪|♭|♯)?)', sym.strip())
            if not ms:
                fail('D', f"{d['ctx']}: label '{rn}' shows no chord symbol ('{sym}')")
                continue
            if m21name(ms.group(1)) != root:
                fail('D', f"{d['ctx']} [{kname(d['key'])}]: label {rn} shows {sym}, music21 root {pretty(root)}")
            else:
                ok('D', 'displayed chord labels')


# ================================================================= main
async def main():
    t0 = time.time()
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#keys')
        await pg.wait_for_timeout(1500)
        await pg.evaluate(SCAN_JS)
        D = await pg.evaluate(KEYS_JS)
        await collect_scan(pg, 'Keys room')
        COUNT['tonics offered in the Scales tab'] = len(D['tonics'])
        check_keys(D)
        await pg.evaluate(SCAN_JS)
        R = await pg.evaluate(CHORDS_JS)
        await collect_scan(pg, 'Chords room')
        COUNT['Chords room chords drawn (root spellings x qualities)'] = len(R)
        check_chords_room(R)
        await pg.evaluate(SCAN_JS)
        IV = []
        for inst in ('guitar', 'uke', 'bass'):
            for L in 'CDEFGAB':
                IV += await pg.evaluate(INVFRET_JS, [inst, L])
        await collect_scan(pg, 'Chords room inversions and fretboards')
        COUNT['G inversion and fretboard renders (instrument x root x quality x inversion)'] = len(IV)
        check_inversions(IV)
        await pg.goto('http://app/index.html#climbs/3')
        await pg.wait_for_timeout(1200)
        await pg.evaluate(SCAN_JS)
        C = await pg.evaluate(CLIMBS_JS)
        await collect_scan(pg, 'Climbs')
        COUNT['climb progressions captured'] = len([c for c in C['CAP'] if c['t'] in ('real', 'list', 'jazz')])
        COUNT['climb renders'] = len(C['DOM'])
        check_climbs(C)
        await pg.wait_for_timeout(300)
        # every room as first opened, at every level
        for lv in (4, 5, 6):
            await pg.goto('http://app/index.html#seed')
            await pg.wait_for_timeout(500)
            await pg.evaluate(SCAN_JS)
            await pg.evaluate(f"()=>{{S.level={lv};for(const r of ['seed','keys','voice','climbs','forms','analysis','ear','gym','oracle']){{try{{room(r);__scan(document.body,'room '+r)}}catch(e){{}}}}}}")
            await collect_scan(pg, f'rooms at level {lv}')
        if errs:
            for e in errs[:10]:
                fail('X', f'page error: {e}')
        await b.close()
    COUNT['seconds'] = round(time.time() - t0)
    report = {'counts': dict(sorted(COUNT.items())),
              'n_checks': sum(v for k, v in COUNT.items() if ':' in k),
              'failures': {k: v[:25] for k, v in FAIL.items()},
              'n_failures': sum(len(v) for v in FAIL.values()),
              'known_failures': {k: {'description': KNOWN[k][2], 'hits': len(v), 'examples': v[:5]} for k, v in KNOWNHIT.items()}}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)


if __name__ == '__main__':
    asyncio.run(main())
