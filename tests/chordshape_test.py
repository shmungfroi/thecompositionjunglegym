"""Chord shapes test (charter suite 4): every chord shape the Seed Bank can show, checked against music21.
Run: python3 tests/chordshape_test.py <repo dir>      (needs playwright, Chrome and music21; tests/run_all installs the harness)

What it enumerates (by driving the app's own render path in the #seed room, then reading back what it drew):
  roots      the 17 picker roots (ROOTS) plus every other spelling the app can put in the Seed Bank through the
             "Neighbours in <key>" chips (e.g. E#, B#, Cb, F##), found by rendering renderClimb in all 24 keys
  qualities  every chord type available at Stage 6 (Q with l<=6: 20 types; the three augmented sixths are l:9 and the
             Seed Bank never shows them)
  inversions every inversion the selector offers (one per chord tone)
  shapes     piano Beginner (one hand 1-3-5) and Full (two hands); guitar and ukulele "Beginner shapes" and every extra
             shape in "More shapes" (exactly the list renderInst draws, read from #inst._vs); bass patterns (#inst._bp)

What it checks, independently (music21 Interval/Pitch/ChordSymbol and this file's own rules; never the app's checker):
  A  chord spelling: the formula of every type against a hand-written table and music21 ChordSymbol; every tone name
     against music21 transposition from the root; name+octave against the MIDI number; chord symbol and bass text
  B  piano Beginner: root/3rd(or sus)/5th only, in the inversion asked (capped at 2nd with the "needs the full chord"
     note), above middle C, standard RH/LH fingerings, "left out" list, lit keys and labels, played notes
  C  piano Full: bass note (F2-E3) is the inversion's bass, every chord tone once, right hand close from middle C,
     lit keys and labels, played notes
  D  guitar/ukulele: real tunings (EADGBE, re-entrant GCEA), fret->pitch, only chord tones, required tones present
     (only the perfect 5th of a 4+ note chord may be left out), "no 5th" and "N strings" labels honest, guitar bass note
     = the inversion's bass and the "Root/Bass on Nth string · fret n" label, four-fret reach, open strings only in
     first position, at most one muted inner string, fret-7 ceiling for Beginner shapes, fingerings playable (each
     finger on one fret, fingers in fret order, at most four, barres real), degree labels in the dots, "Open"/"barre"/
     "Root at fret" names honest, played notes
  E  bass: tuning EADG, fret->pitch, only chord tones, starts on the inversion's bass note, strings never move back,
     notes ascend, root-5th-octave patterns exact, arpeggios = every chord tone from the bass to its octave in one
     four-fret position (two positions only for dim7, with the shift labelled), one finger per fret, degree labels,
     every chord has at least one pattern, the bass "play" notes
Counts on v0.46: 21 roots (17 + B#, Cb, E#, F##) x 20 types x every inversion = 1,575 chords; 21,500 shapes checked
  (1,575 piano Beginner + 1,575 piano Full + 7,622 guitar + 6,893 ukulele + 3,835 bass patterns); 9,512 distinct fretted
  shapes when ukulele shapes are counted once per chord rather than per inversion. Run time about 45 s.
Exits 1 on any failure not listed in KNOWN (known app defects are reported under "known_failures").
"""
import sys, asyncio, json, pathlib, collections, time, re

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent / 'harness'))
import cjg
from playwright.async_api import async_playwright
from music21 import harmony, pitch as m21pitch, interval as m21interval

FAIL = collections.defaultdict(list)
COUNT = collections.Counter()
INFO = collections.defaultdict(list)
DISTINCT = set()  # fretted shapes once per chord (ukulele shapes do not depend on the inversion)
# known app defects: id -> (section, regex on the failure message). Reported, but they do not fail the run.
KNOWN = {
    # CS-K1: chord spellings needing a triple sharp or a quadruple flat (B#aug: F###, F##aug: C###, Cbdim7: Bbbbb) are
    # spelled correctly, but VexFlow rejects the key name, so render() throws in renderStaff and the Seed Bank stave
    # and climb panel are not drawn. Reach: Seed Bank, choose the key C# minor (B#), G# minor (F##) or Eb minor (Cb),
    # tap that root's neighbour chip, then tap the aug (or dim7 for Cb) quality pad.
    'CS-K1': ('A', r'^(B#aug|F##aug|Cbdim7) inv\d: the Seed Bank render throws: .*Invalid key name'),
}
KNOWN_HITS = collections.defaultdict(list)


def fail(sec, msg):
    for kid, (ks, rx) in KNOWN.items():
        if ks == sec and re.search(rx, msg):
            KNOWN_HITS[kid].append(msg)
            return
    FAIL[sec].append(msg)


# ---------- independent theory ----------
# chord formulas, written from the theory (not copied from the app at run time)
FORM = {'5': ['1', '5'], '': ['1', '3', '5'], 'm': ['1', 'b3', '5'], '7': ['1', '3', '5', 'b7'], 'sus2': ['1', '2', '5'],
        'sus4': ['1', '4', '5'], 'dim': ['1', 'b3', 'b5'], 'aug': ['1', '3', '#5'], 'maj7': ['1', '3', '5', '7'],
        'm7': ['1', 'b3', '5', 'b7'], '6': ['1', '3', '5', '6'], 'add9': ['1', '3', '5', '9'], 'madd9': ['1', 'b3', '5', '9'],
        'm6': ['1', 'b3', '5', '6'], 'm7b5': ['1', 'b3', 'b5', 'b7'], 'dim7': ['1', 'b3', 'b5', 'bb7'],
        '9': ['1', '3', '5', 'b7', '9'], 'maj9': ['1', '3', '5', '7', '9'], 'm9': ['1', 'b3', '5', 'b7', '9'],
        '7sus4': ['1', '4', '5', 'b7']}
IVL = {'1': 'P1', '2': 'M2', 'b3': 'm3', '3': 'M3', '4': 'P4', 'b5': 'd5', '5': 'P5', '#5': 'A5', '6': 'M6', 'bb7': 'd7',
       'b7': 'm7', '7': 'M7', '9': 'M9'}
M21FIG = {'5': 'C5', '': 'C', 'm': 'Cm', '7': 'C7', 'sus2': 'Csus2', 'sus4': 'Csus4', 'dim': 'Cdim', 'aug': 'Caug',
          'maj7': 'Cmaj7', 'm7': 'Cm7', '6': 'C6', 'add9': 'Cadd9', 'madd9': 'Cmadd9', 'm6': 'Cm6', 'm7b5': 'Cm7b5',
          'dim7': 'Cdim7', '9': 'C9', 'maj9': 'CM9', 'm9': 'Cm9', '7sus4': 'C7sus4'}
TUNE = {k: [m21pitch.Pitch(n).midi for n in v] for k, v in
        {'guitar': ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'], 'uke': ['G4', 'C4', 'E4', 'A4'], 'bass': ['E1', 'A1', 'D2', 'G2']}.items()}
GSTR = ['6th', '5th', '4th', '3rd', '2nd', '1st']
UKS = ['G', 'C', 'E', 'A']
BSN = ['E', 'A', 'D', 'G']


def m21name(n):  # app 'Bb' -> music21 'B-'
    return n[0] + n[1:].replace('b', '-')


def appname(n):  # music21 'B-' -> app 'Bb'
    return n[0] + n[1:].replace('-', 'b')


def unpretty(s):
    return s.replace('𝄪', '##').replace('𝄫', 'bb').replace('♯', '#').replace('♭', 'b')


def dlab(d):
    # 0.48 (R6 H3, approved): doubly altered degrees are shown with the single glyphs 𝄫 and 𝄪
    return d.replace('bb', '𝄫').replace('##', '𝄪').replace('b', '♭').replace('#', '♯')


def expected_chord(root, qk):
    rp = m21pitch.Pitch(m21name(root) + '4')
    out = []
    for d in FORM[qk]:
        p = m21interval.Interval(IVL[d]).transposePitch(rp)
        out.append({'d': d, 'name': appname(p.name), 'pc': p.pitchClass, 'semis': p.midi - rp.midi})
    return out


def midi_of(name, octv):
    return m21pitch.Pitch(m21name(name) + str(octv)).midi


def formula_crosscheck():
    for qk, fig in M21FIG.items():
        cs = harmony.ChordSymbol(fig)
        got = sorted(appname(p.name) for p in cs.pitches)
        mine = sorted(t['name'] for t in expected_chord('C', qk))
        COUNT['A formulas cross-checked with music21 ChordSymbol'] += 1
        if got != mine:
            fail('A', f'formula table vs music21 ChordSymbol {fig}: {mine} vs {got}')


# ---------- page extraction ----------
JS = r"""(roots)=>{const out=[];const tx=e=>e?e.textContent:'';
 const lit=()=>[...document.querySelectorAll('#pno .lit')].map(e=>({m:+e.dataset.m,lab:tx(e.querySelector('.lab')),fg:tx(e.querySelector('.fg'))}));
 const nt=n=>({d:n.d,name:n.name,midi:n.midi,oct:n.oct});
 const dots=b=>[...b.querySelectorAll('svg text')].filter(t=>t.getAttribute('font-weight')==='700').map(t=>t.textContent);
 for(const root of roots)for(const q of Q.filter(q=>q.l<=6))for(let inv=0;inv<q.d.length;inv++){
  Object.assign(S,{root,q:q.k,inv,level:6,vi:0,dots:'deg',more:false,inst:'piano',pmode:'beg'});
  let rerr=null;try{render()}catch(e){rerr=String(e.message||e).slice(0,160)}const c=chord();
  const R={root,q:q.k,inv,rerr,formula:q.d,sym:$('sym').textContent,bassTxt:$('bassTxt').textContent,tones:c.tones.map(nt),bassName:c.bass.name};
  const B=beginnerNotes(c);
  R.pbeg={notes:B.notes.map(nt),rh:B.rh,lh:B.lh,left:B.left.map(t=>t.d),lit:lit(),note:tx(document.querySelector('#inst .begnote')),play:instMidis(c).m};
  S.pmode='full';renderInst(c);
  R.pfull={notes:voicing(c).map(nt),lit:lit(),play:instMidis(c).m};
  for(const inst of ['guitar','uke']){S.inst=inst;S.vi=0;S.more=false;renderInst(c);const beg=($('inst')._vs||[]).map(v=>v.fr.join());
   S.more=true;S.vi=0;renderInst(c);const vs=$('inst')._vs||[],boxes=[...document.querySelectorAll('#inst .vbox')];
   R[inst]={beg,empty:!!document.querySelector('#inst .empty'),shapes:vs.map((v,i)=>{S.vi=i;const F=vFingers(v),b=boxes[i];
    return{fr:v.fr,more:!!v.more,cur:!!v.cur,name:tx(b&&b.querySelector('.nm')),small:tx(b&&b.querySelector('small')),dots:b?dots(b):null,fing:F.fing,barre:F.barre,play:instMidis(c).m}})}}
  S.inst='bass';S.more=false;S.vi=0;renderInst(c);const BP=$('inst')._bp||[],bb=[...document.querySelectorAll('#inst .vbox')];
  R.bass={play:instMidis(c).m,pats:BP.map((p,i)=>({nm:p.nm,sub:p.sub,shift:p.shift||0,notes:p.notes.map(n=>({s:n.s,f:n.f,m:n.m,d:n.d,fg:n.fg})),dots:bb[i]?dots(bb[i]):null}))};
  out.push(R)}
 S.inst='piano';S.more=false;return out}"""

JS_EXTRA_ROOTS = r"""()=>{const got=new Set();S.level=6;S.root='C';S.q='';S.inv=0;
 for(let k=0;k<12;k++)for(const mode of ['maj','min']){S.key={k,mode};renderClimb(chord());
  document.querySelectorAll('#neigh [data-go],#sameRoot [data-go]').forEach(b=>got.add(b.dataset.go.split('|')[0]))}
 S.key=null;return{all:[...got],roots:ROOTS,tun:TUN,ceil:FR_CEIL}}"""


# ---------- checks ----------
def check_chord(R, E):
    where = f"{R['root']}{R['q']} inv{R['inv']}"
    COUNT['A chords (root x type x inversion)'] += 1
    if R.get('rerr'):
        fail('A', f"{where}: the Seed Bank render throws: {R['rerr']}")
    if R['formula'] != FORM[R['q']]:
        fail('A', f"{where}: app formula {R['formula']} vs {FORM[R['q']]}")
    names = [t['name'] for t in R['tones']]
    if names != [e['name'] for e in E]:
        fail('A', f"{where}: spelled {names}, music21 says {[e['name'] for e in E]}")
    r0 = R['tones'][0]['midi']
    for t, e in zip(R['tones'], E):
        if midi_of(t['name'], t['oct']) != t['midi']:
            fail('A', f"{where}: {t['name']}{t['oct']} is not MIDI {t['midi']}")
        if t['midi'] - r0 != e['semis']:
            fail('A', f"{where}: {t['d']} is {t['midi'] - r0} semitones above the root, should be {e['semis']}")
    bass = E[R['inv']]['name']
    want = R['root'] + R['q'] + ('/' + bass if R['inv'] else '')
    if unpretty(R['sym']) != want:
        fail('A', f"{where}: symbol shows {R['sym']!r}, expected {want}")
    if unpretty(R['bassTxt']) != bass or R['bassName'] != bass:
        fail('A', f"{where}: bass shown {R['bassTxt']!r}/{R['bassName']}, expected {bass}")


def note_ok(sec, where, n, E):
    e = next((x for x in E if x['pc'] == n['midi'] % 12), None)
    if e is None:
        fail(sec, f"{where}: {n['name']} (MIDI {n['midi']}) is not in the chord")
        return None
    if n['name'] != e['name'] or n['d'] != e['d']:
        fail(sec, f"{where}: MIDI {n['midi']} shown as {n['name']} ({n['d']}), should be {e['name']} ({e['d']})")
    if midi_of(n['name'], n['oct']) != n['midi']:
        fail(sec, f"{where}: {n['name']}{n['oct']} is not MIDI {n['midi']}")
    return e


def check_lit(sec, where, lit, notes, fingers=None):
    if sorted(x['m'] for x in lit) != sorted(n['midi'] for n in notes):
        fail(sec, f"{where}: lit keys {sorted(x['m'] for x in lit)} vs notes {[n['midi'] for n in notes]}")
        return
    for x in lit:
        i = next(i for i, n in enumerate(notes) if n['midi'] == x['m'])
        if unpretty(x['lab']) != notes[i]['name']:
            fail(sec, f"{where}: key {x['m']} labelled {x['lab']!r}, note is {notes[i]['name']}")
        if fingers is not None and x['fg'] != str(fingers[i]):
            fail(sec, f"{where}: key {x['m']} finger {x['fg']!r}, expected {fingers[i]}")


def check_piano(R, E):
    where = f"{R['root']}{R['q']} inv{R['inv']}"
    pcs = {e['pc'] for e in E}
    deg = {e['d']: e for e in E}
    # B beginner
    P = R['pbeg']
    COUNT['B piano beginner shapes'] += 1
    w = where + ' piano beginner'
    for n in P['notes']:
        note_ok('B', w, n, E)
    ms = [n['midi'] for n in P['notes']]
    if ms != sorted(ms) or len(set(ms)) != len(ms):
        fail('B', f'{w}: notes not ascending {ms}')
    if not ms or not 60 <= ms[0] <= 71 or ms[-1] > 84:
        fail('B', f'{w}: not one hand just above middle C {ms}')
    if R['q'] == '5':
        R5 = [deg['1']['pc'], deg['5']['pc']]
        want = [R5[0], R5[1], R5[0]] if R['inv'] == 0 else [R5[1], R5[0], R5[1]]
        if [m % 12 for m in ms] != want:
            fail('B', f'{w}: power chord notes {ms}')
    else:
        third = next(d for d in FORM[R['q']] if d in ('3', 'b3', '2', '4'))
        fifth = next(d for d in FORM[R['q']] if d in ('5', 'b5', '#5'))
        tri = ['1', third, fifth]
        k = min(R['inv'], 2)
        want = [deg[d]['pc'] for d in tri[k:] + tri[:k]]
        if [m % 12 for m in ms] != want:
            fail('B', f"{w}: notes {[n['name'] for n in P['notes']]}, expected {[deg[d]['name'] for d in tri[k:] + tri[:k]]}")
        if sorted(P['left']) != sorted(d for d in FORM[R['q']] if d not in tri):
            fail('B', f"{w}: 'left out' {P['left']}")
        if P['left'] and 'Left out for now' not in P['note']:
            fail('B', f'{w}: tones left out but not said')
        if R['inv'] > 2 and 'needs the full chord' not in P['note']:
            fail('B', f'{w}: inversion {R["inv"]} capped at 2nd without saying so')
        rh = {0: [1, 3, 5], 1: [1, 2, 5], 2: [1, 3, 5]}[k]
        lh = {0: [5, 3, 1], 1: [5, 3, 1], 2: [5, 2, 1]}[k]
        if P['rh'] != rh or P['lh'] != lh:
            fail('B', f"{w}: fingering RH {P['rh']} LH {P['lh']}, standard is RH {rh} LH {lh}")
    check_lit('B', w, P['lit'], P['notes'], P['rh'])
    if P['play'] != ms:
        fail('B', f"{w}: plays {P['play']} but shows {ms}")
    # C full
    P = R['pfull']
    COUNT['C piano full shapes'] += 1
    w = where + ' piano full'
    for n in P['notes']:
        note_ok('C', w, n, E)
    ms = [n['midi'] for n in P['notes']]
    if ms[0] % 12 != E[R['inv']]['pc'] or not 41 <= ms[0] <= 52:
        fail('C', f"{w}: left-hand bass {P['notes'][0]['name']} ({ms[0]}), expected {E[R['inv']]['name']} in F2-E3")
    if sorted(m % 12 for m in ms) != sorted(pcs) :
        fail('C', f'{w}: not every chord tone exactly once {ms}')
    rh = ms[1:]
    if rh != sorted(rh) or (rh and (rh[0] < 60 or rh[-1] - rh[0] > 12)):
        fail('C', f'{w}: right hand not close from middle C {rh}')
    check_lit('C', w, P['lit'], P['notes'])
    if P['play'] != ms:
        fail('C', f"{w}: plays {P['play']} but shows {ms}")


def fingering_ok(fr, fing, barre):
    used = {}
    for f, g in zip(fr, fing):
        if f > 0:
            if g in ('', None):
                return 'a fretted string has no finger'
            if g == 'T':
                continue
            if g not in (1, 2, 3, 4):
                return f'finger {g!r}'
            if used.setdefault(g, f) != f:
                return f'finger {g} on two frets'
        elif g not in ('', None):
            return 'finger on an open or muted string'
    order = sorted((f, g) for f, g in zip(fr, fing) if f > 0 and g != 'T')
    for (f1, g1), (f2, g2) in zip(order, order[1:]):
        if f2 > f1 and g2 < g1:
            return f'finger {g2} at fret {f2} is behind finger {g1} at fret {f1}'
    if barre:
        seg = fr[barre['from']:barre['to'] + 1]
        if any(f < barre['fret'] for f in seg) or fr[barre['from']] != barre['fret'] or fr[barre['to']] != barre['fret']:
            return f'barre {barre} not under the strings {fr}'
    return None


def check_fretted(R, E, inst, ceil):
    where = f"{R['root']}{R['q']} inv{R['inv']} {inst}"
    tun = TUNE[inst]
    pcs = {e['pc'] for e in E}
    deg_of = {e['pc']: e['d'] for e in E}
    five = next((e['pc'] for e in E if e['d'] == '5'), None)
    optional = {five} if five is not None and len(E) > 3 else set()
    D = R[inst]
    sh = D['shapes']
    if not sh:
        fail('D', f'{where}: no shape at all')
        return
    beg = [s for s in sh if not s['more']]
    if [','.join(map(str, s['fr'])) for s in beg] != D['beg']:
        fail('D', f'{where}: "More shapes" does not start with the Beginner list')
    if len(beg) > 4 or len(sh) - len(beg) > 8:
        fail('D', f'{where}: {len(beg)} beginner / {len(sh) - len(beg)} more shapes (limits 4 / 8)')
    low_avail = sum(1 for s in sh if min([f for f in s['fr'] if f > 0] or [0]) <= ceil)
    for i, s in enumerate(sh):
        COUNT[f"D {inst} shapes ({'more' if s['more'] else 'beginner'})"] += 1
        fr = s['fr']
        DISTINCT.add((inst, R['root'], R['q'], R['inv'] if inst == 'guitar' else '-', tuple(fr)))
        w = f"{where} shape {i + 1} {''.join('x' if f < 0 else str(f) if f < 10 else f'({f})' for f in fr)}"
        if len(fr) != len(tun):
            fail('D', f'{w}: {len(fr)} strings')
            continue
        snd = [None if f < 0 else tun[j] + f for j, f in enumerate(fr)]
        S_ = [m for m in snd if m is not None]
        have = {m % 12 for m in S_}
        if have - pcs:
            fail('D', f'{w}: sounds {sorted(have - pcs)} outside the chord')
        miss = pcs - have - optional
        if miss:
            fail('D', f"{w}: required tone(s) {[deg_of[p] for p in miss]} missing")
        no5 = five is not None and five not in have
        if 'no 5th' in s['small'] and not no5:
            fail('D', f'{w}: labelled "no 5th" but the 5th sounds')
        if s['more'] and no5 and 'no 5th' not in s['small']:
            fail('D', f'{w}: leaves out the 5th without the "no 5th" label')
        if no5 and not s['more']:
            INFO['beginner shapes without the 5th (no label in Beginner view)'].append(w)
        if s['more']:
            m = re.search(r'(\d+) strings', s['small'])
            if not m or int(m.group(1)) != len(S_):
                fail('D', f"{w}: label {s['small']!r} vs {len(S_)} strings sounding")
        fd = [f for f in fr if f > 0]
        if any(f > 15 for f in fr):
            fail('D', f'{w}: beyond fret 15')
        if fd and max(fd) - min(fd) > 3:
            fail('D', f'{w}: stretch of {max(fd) - min(fd) + 1} frets')
        if 0 in fr and fd and max(fd) > 4:
            # the app's rule (frReal: open strings only in first position) applies to movable and searched shapes;
            # shapes from the published-chart library (FCUR) are taken as charted, e.g. ukulele Fmaj7 5500
            if s['cur']:
                INFO['chart-library shapes with open strings above fret 4 (allowed: charted)'].append(w)
            else:
                fail('D', f'{w}: open strings with fretted notes above fret 4')
        first, last = next(j for j, f in enumerate(fr) if f >= 0), max(j for j, f in enumerate(fr) if f >= 0)
        inner = sum(1 for j in range(first, last + 1) if fr[j] < 0)
        if inner > 1:
            fail('D', f'{w}: {inner} muted inner strings')
        if inst == 'uke' and len(S_) < 4:
            fail('D', f'{w}: ukulele shape with {len(S_)} strings')
        if not s['more'] and fd and min(fd) > ceil and low_avail >= 2:
            fail('D', f'{w}: Beginner shape above the fret-{ceil} ceiling although lower shapes exist')
        why = fingering_ok(fr, s['fing'], s['barre'])
        if why:
            fail('D', f'{w}: fingering {s["fing"]}: {why}')
        want_dots = [dlab(deg_of.get(snd[j] % 12, '?')) for j, f in enumerate(fr) if f > 0]
        if s['dots'] != want_dots:
            fail('D', f"{w}: dot labels {s['dots']} vs degrees {want_dots}")
        if s['play'] != S_:
            fail('D', f"{w}: plays {s['play']} vs fret->pitch {S_}")
        nm, sub = s['name'], s['small']
        if nm.startswith('Open') and 0 not in fr:
            fail('D', f'{w}: named {nm!r} with no open string')
        if 'barre' in nm.lower() and not s['barre']:
            fail('D', f'{w}: named {nm!r} but has no barre')
        if inst == 'guitar':
            lo = min(S_)
            if lo % 12 != E[R['inv']]['pc']:
                fail('D', f"{w}: lowest note {lo} is not the bass {E[R['inv']]['name']}")
            m = re.match(r'(Root|Bass) on (\w+) string(?: · fret (\d+))?', sub)
            if not m:
                fail('D', f'{w}: sub-label {sub!r}')
            else:
                j = GSTR.index(m.group(2)) if m.group(2) in GSTR else -1
                if (m.group(1) == 'Root') != (R['inv'] == 0) or j < 0 or snd[j] != lo:
                    fail('D', f'{w}: {sub!r} but the lowest note is on string {GSTR[snd.index(lo)]}')
                if m.group(3) and int(m.group(3)) != fr[j]:
                    fail('D', f'{w}: {sub!r} but that string is at fret {fr[j]}')
        else:
            if sub.startswith('Open strings ring') and 0 not in fr:
                fail('D', f'{w}: {sub!r} with no open string')
            m = re.match(r'Root at fret (\d+), (\w) string', sub)
            if m and (fr[UKS.index(m.group(2))] != int(m.group(1)) or snd[UKS.index(m.group(2))] % 12 != E[0]['pc']):
                fail('D', f'{w}: {sub!r} is not the root')
            m = re.search(r'Barre at fret (\d+)', sub)
            if m and (not s['barre'] or s['barre']['fret'] != int(m.group(1))):
                fail('D', f'{w}: {sub!r} but barre is {s["barre"]}')


def check_bass(R, E):
    where = f"{R['root']}{R['q']} inv{R['inv']} bass"
    tun = TUNE['bass']
    pcs = {e['pc'] for e in E}
    deg_of = {e['pc']: e['d'] for e in E}
    bpc = E[R['inv']]['pc']
    B = R['bass']
    pl = B['play']
    if not pl or pl[0] % 12 != bpc or not 28 <= pl[0] <= 39 or {m % 12 for m in pl} != pcs:
        fail('E', f'{where}: bass play button notes {pl}')
    if not B['pats']:
        fail('E', f'{where}: no bass pattern')
    for i, p in enumerate(B['pats']):
        COUNT['E bass patterns'] += 1
        w = f"{where} pattern {i + 1} ({p['nm']})"
        N = p['notes']
        for n in N:
            if n['f'] < 0 or n['f'] > 17 or tun[n['s']] + n['f'] != n['m']:
                fail('E', f"{w}: string {BSN[n['s']]} fret {n['f']} is not MIDI {n['m']}")
            if n['m'] % 12 not in pcs:
                fail('E', f"{w}: {n['m']} not a chord tone")
            elif n['d'] != deg_of[n['m'] % 12]:
                fail('E', f"{w}: {n['m']} labelled {n['d']}, is the {deg_of[n['m'] % 12]}")
        ms = [n['m'] for n in N]
        if ms != sorted(set(ms)):
            fail('E', f'{w}: not ascending {ms}')
        if [n['s'] for n in N] != sorted(n['s'] for n in N):
            fail('E', f'{w}: strings move backwards')
        if N[0]['m'] % 12 != bpc:
            fail('E', f'{w}: starts on {N[0]["m"]}, not the bass note {E[R["inv"]]["name"]}')
        if not p['sub'].startswith(f"From the {BSN[N[0]['s']]} string"):
            fail('E', f"{w}: {p['sub']!r} but starts on the {BSN[N[0]['s']]} string")
        want_dots = [dlab(n['d']) if True else '' for n in N if n['f'] > 0]
        if p['dots'] is not None and p['dots'] != want_dots:
            fail('E', f"{w}: dot labels {p['dots']} vs {want_dots}")
        segs = [N] if not p['shift'] else [N[:p['shift']], N[p['shift']:]]
        for sg in segs:
            fd = [n for n in sg if n['f'] > 0]
            if fd:
                if max(n['f'] for n in fd) - min(n['f'] for n in fd) > 3:
                    fail('E', f'{w}: more than one four-fret position')
                offs = {n['f'] - n['fg'] for n in fd}
                if len(offs) != 1 or not all(1 <= n['fg'] <= 4 for n in fd):
                    fail('E', f"{w}: not one finger per fret {[(n['f'], n['fg']) for n in fd]}")
            if any(n['fg'] != 0 for n in sg if n['f'] == 0):
                fail('E', f'{w}: open string with a finger')
        m = re.match(r'Root–(.+)th–octave', p['nm'])
        if m:
            fdeg = next((e for e in E if e['d'] in ('5', 'b5', '#5')), None)
            if R['inv'] or not fdeg or unpretty(m.group(1)) != fdeg['d'] or ms != [ms[0], ms[0] + fdeg['semis'], ms[0] + 12]:
                fail('E', f'{w}: notes {ms}')
        elif p['nm'].startswith('Arpeggio'):
            want = [x for x in range(ms[0], ms[0] + 13) if x % 12 in pcs]
            if ms != want:
                fail('E', f'{w}: {ms}, expected every chord tone bass to octave {want}')
            two = p['nm'] == 'Arpeggio · two positions'
            if two and (R['q'] != 'dim7' or f"shift before note {p['shift'] + 1}" not in p['sub']):
                fail('E', f"{w}: two positions {p['sub']!r}")
            if not two and p['shift']:
                fail('E', f'{w}: shift in a one-position pattern')
        else:
            fail('E', f"{w}: unknown pattern name")


async def main():
    t0 = time.time()
    formula_crosscheck()
    async with async_playwright() as p:
        b = await cjg.launch(p)
        pg = await b.new_page(viewport={'width': 1440, 'height': 900})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#seed')
        await pg.wait_for_timeout(1500)
        meta = await pg.evaluate(JS_EXTRA_ROOTS)
        for k in TUNE:
            if meta['tun'][k] != TUNE[k]:
                fail('D', f"{k} tuning {meta['tun'][k]} vs {TUNE[k]}")
        roots = list(meta['roots']) + sorted(r for r in meta['all'] if r not in meta['roots'])
        COUNT['roots (17 picker + neighbour-chip spellings)'] = len(roots)
        COUNT['extra roots: ' + ' '.join(r for r in roots if r not in meta['roots'])] = 1
        recs = []
        for r in roots:
            recs += await pg.evaluate(JS, [r])
        if errs:
            fail('A', f'page errors: {errs[:5]}')
        await b.close()
    for R in recs:
        E = expected_chord(R['root'], R['q'])
        check_chord(R, E)
        check_piano(R, E)
        for inst in ('guitar', 'uke'):
            check_fretted(R, E, inst, meta['ceil'])
        check_bass(R, E)
    shapes = sum(v for k, v in COUNT.items() if k.startswith(('B ', 'C ', 'D ', 'E ')))
    COUNT['TOTAL shapes checked'] = shapes
    COUNT['distinct fretted shapes (ukulele counted once per root x type, not per inversion)'] = len(DISTINCT)
    report = {'counts': dict(COUNT), 'seconds': round(time.time() - t0, 1),
              'info': {k: {'n': len(v), 'first': v[:10]} for k, v in INFO.items()},
              'known_failures': {k: {'n': len(v), 'first': v[:5]} for k, v in KNOWN_HITS.items()},
              'failures': {k: v[:25] for k, v in FAIL.items()}, 'n_failures': sum(len(v) for v in FAIL.values())}
    print(json.dumps(report, indent=1, ensure_ascii=False))
    sys.exit(1 if report['n_failures'] else 0)

asyncio.run(main())
