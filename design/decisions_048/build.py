#!/usr/bin/env python3
"""Decision sheet for CJG 0.48: Decision 5 (phone solfa ladder) and Decision 12 (a function colour for minor v and VII).
Run:  python3 build.py      (needs python playwright and Chrome; reads ../earlab_048 for the 0.48 Ear Lab components)

Writes  d5_A.html, d5_B.html, d5_C.html   the melody card at rung 3, mid-answer, one ladder treatment each
        sheet.html                         the one-page sheet (self-contained: fonts and phone shots inlined)
        png/                               sheet_1440.png, d5_[ABC]_390.png (phone view), d5_[ABC]_390_full.png (whole page)
The melody desk markup in assets/live_mel.html was captured from the running 0.48 app at 390 px (seeded question,
E minor, 4 of 6 notes written), so the stave and hand signs are the app's own."""
import base64, importlib.util, json, pathlib, re, sys

D = pathlib.Path(__file__).resolve().parent
EL = D.parent / 'earlab_048'
REPO = D.parent.parent
spec = importlib.util.spec_from_file_location('elbuild', EL / 'build.py'); E = importlib.util.module_from_spec(spec); spec.loader.exec_module(E)
sys.path.insert(0, str(D)); import colour as C

IV, MUTED, GOLD, GOLDHI, LINE = '#ece2c8', '#9c927c', '#c9a24a', '#f0d48a', '#2a2418'
VIEW = (390, 664)   # iPhone 14 class (390 x 844 screen) in Safari with its bars showing

# ====================================================================== Decision 5: the three ladders
LIVE = (D / 'assets/live_mel.html').read_text()
DESK = LIVE[LIVE.index('<div class="meldesk">'):]
LADDER = re.search(r'<div class="earlad".*?</div>(?=\s*<div class="melscore">)', DESK, re.S).group(0)
SCORE = re.search(r'<div class="melscore">.*?</svg></div></div>', DESK, re.S).group(0)
STEPS = re.findall(r'<button class="earstep.*?</button>', LADDER, re.S)


def ladder(kind):
    out = []
    for k, b in enumerate(STEPS):
        if kind == 'C':   # two columns, each note half a row above the next: 48 px targets on a 24 px pitch
            b = re.sub(r'style="grid-row:[^"]*"', f'style="grid-row:{k + 1}/span 2;grid-column:{1 if k % 2 == 0 else 2}"', b)
        out.append(b)
    return f'<div class="earlad lad{kind}" role="group" aria-label="Solfa ladder, high to low">{"".join(out)}</div>'


LAD_CSS = {
    'A': '.meldesk .earlad{grid-auto-rows:22.5px}',
    'B': ('.meldesk .earlad{grid-auto-rows:12.5px}.meldesk .earstep{font-size:14px;padding:0 10px 0 6px}.meldesk .earstep b{font-size:14px}'
          '.meldesk .hsw{width:40px;height:21px}.meldesk .hsi{max-width:40px;max-height:21px}.meldesk .hsw em{top:-5px;font-size:11px}'),
    'C': ('.meldesk .earlad{grid-template-columns:1fr 1fr;column-gap:6px;grid-auto-rows:24px}.meldesk .earstep{grid-column:auto;padding:0 8px 0 6px;gap:8px}'
          '.meldesk .hsw{width:60px;height:34px}.meldesk .hsi{max-width:60px;max-height:34px}.earstep .hm{letter-spacing:1px}'),
}
PANEL_CSS = ('.el-edit{margin-top:10px}.melnote{display:block;margin-top:10px;font-size:12.5px;color:var(--muted)}'
             '.melnote input{accent-color:var(--gold);margin-right:6px}')
MEL_TIPS = E.tips(['<b>Sing the home note.</b> Hold it in your head while the melody plays.',
                   '<b>Step or leap?</b> Trace the shape in the air before you tap anything.',
                   '<b>Sing it back with the hand signs.</b> Then check each note against the stave.'])


def panel(kind):
    acts = '<button class="el-btn">Show me</button><button class="el-btn">Skip →</button>'
    extra = '<div class="el-vars"><span class="cap">Or just</span><button class="el-var">Without the key chord</button><button class="el-var">First note</button></div>'
    desk = (f'<div class="meldesk">{ladder(kind)}{SCORE}<div class="melacts">{E.EDIT(False)}'
            '<label class="melnote"><input type="checkbox"> show letter names</label></div></div>')
    body = (E.drills('mel') + '<div class="el-cols"><section class="card">' + E.head('Melodic dictation', 'Stage 4–6', 3, E.tally(7, 9, 2, 4))
            + '<p class="el-ask">The key chord plays first, then the melody. Tap each note on the solfa ladder.</p>'
            + E.stage('ready', 'Play again', 'Ready · played twice', acts, extra) + desk
            + E.foot('<b>9</b> answered · <b>1</b> shown · <b>0</b> skipped', name='Melodic dictation') + '</section>' + MEL_TIPS + '</div>')
    dock = ('<div class="el-dock show" role="region" aria-label="Ear Lab playback">' + E.play('ready') +
            '<div class="el-now ready"><b>Melodic dictation</b><span>Ready · played twice</span></div><button class="el-btn gold" disabled>Check</button></div>')
    html = E.page(f'Decision 5 · ladder {kind}', body, 6, False, dock)
    html = html.replace('href="assets/', 'href="../earlab_048/assets/').replace('</head>', f'<style>{PANEL_CSS}{LAD_CSS[kind]}</style></head>')
    # bring the stave to its pinned place under the top bar, as it is while a student is answering
    html = html.replace('</body>', '<script>addEventListener("load",()=>{if(location.hash==="#top")return;const d=document.querySelector(".meldesk"),t=document.querySelector(".top");'
                        'scrollTo(0,d.getBoundingClientRect().top+scrollY-t.getBoundingClientRect().bottom)})</script></body>')
    (D / f'd5_{kind}.html').write_text(html)


MEASURE = """()=>{const q=s=>document.querySelector(s),R=e=>e.getBoundingClientRect();const lad=R(q('.earlad')),sc=R(q('.melscore')),dock=R(q('.el-dock')),tab=R(q('.tabbar')),chk=R(q('.el-edit'));
 const steps=[...document.querySelectorAll('.earstep')].map(R);
 return{row:Math.round(steps[0].height*10)/10,w:Math.round(steps[0].width),lad:Math.round(lad.height),n:steps.length,staveBottom:Math.round(sc.bottom),dockTop:Math.round(dock.top),tabTop:Math.round(tab.top),
  seen:steps.filter(r=>r.top>=sc.bottom-12&&r.bottom<=dock.top).length,editSeen:chk.bottom<=dock.top,over:document.documentElement.scrollWidth-innerWidth,
  need:Math.round(lad.bottom-dock.top),vh:innerHeight}}"""


# ====================================================================== Decision 12: colour
EXIST = [('T', 'Tonic', '#8fbf6a'), ('PD', 'Predominant', '#c9a24a'), ('D', 'Dominant', '#c8473b'), ('C', 'Chromatic', '#a493d8')]
OLD = '#7fb3c8'
CANDS = [  # key, name, hex, one line
    ('1', 'Madder rose', '#bd6b97', 'The dominant’s red with the heat taken out: reads as a relative of V, which is what these chords are.'),
    ('2', 'Verdigris', '#6fdccf', 'The patina on old brass. The most separate of the three, but still a cool blue-green, the family you turned down.'),
    ('3', 'Shell', '#dfcdc3', 'Almost no colour: “no leading note, no colour”. Distinct from the four, but only a shade away from ordinary ivory text.'),
]
ROW = [('i', 'T'), ('iv', 'PD'), ('v', 'N'), ('VII', 'N'), ('III', 'T'), ('♭II<sup>6</sup>', 'C'), ('V', 'D'), ('i', 'T')]
# A minor, SATB, bass to soprano.  i  iv  v  VII  III  bII6  V  i
VOICES = [['A3', 'E4', 'A4', 'C5'], ['D3', 'F4', 'A4', 'D5'], ['E3', 'E4', 'G4', 'B4'], ['G3', 'D4', 'G4', 'B4'],
          ['C3', 'E4', 'G4', 'C5'], ['D3', 'D4', 'F4', 'Bb4'], ['E3', 'B3', 'E4', 'G#4'], ['A2', 'C4', 'E4', 'A4']]


def more_glyphs():
    """Clefs, semibreve and accidentals from the Bravura outlines in VexFlow 4.2.3 (the font the app already draws with)."""
    cache = D / 'assets/glyphs_extra.json'
    if cache.exists(): return json.loads(cache.read_text())
    src = (REPO / 'tests/harness/node_modules/vexflow/build/cjs/vexflow-font-bravura.js').read_text()
    def conv(o):
        t, i, out = o.split(), 0, []
        while i < len(t):
            c = t[i]
            if c in 'ml': out.append(f'{c.upper()}{t[i+1]} {t[i+2]}'); i += 3
            elif c == 'q': out.append(f'Q{t[i+3]} {t[i+4]} {t[i+1]} {t[i+2]}'); i += 5
            elif c == 'b': out.append(f'C{t[i+3]} {t[i+4]} {t[i+5]} {t[i+6]} {t[i+1]} {t[i+2]}'); i += 7
            else: out.append('Z'); i += 1
        return ''.join(out)
    G = {}
    for n in ('gClef', 'fClef', 'noteheadWhole', 'accidentalSharp', 'accidentalFlat'):
        G[n] = conv(re.search(n + r'["\']?:\s*\{[^{}]*?["\']?o["\']?:\s*["\']([^"\']+)["\']', src).group(1))
    cache.write_text(json.dumps(G)); return G


GX = None
STEP = {'C': 0, 'D': 1, 'E': 2, 'F': 3, 'G': 4, 'A': 5, 'B': 6}


def strip(colours, sp=6.0, size=20, w=392):
    """A grand-staff strip (semibreves, SATB) with the numeral row beneath.  colours: function key -> hex."""
    s = sp / 360; x0, dx = 62, (w - 62 - 14) / len(ROW)
    yT, yB = 16 + 4 * sp, 16 + 4 * sp + 9.5 * sp + 4 * sp  # y of the bottom line of each staff (E4, G2)
    ink, ln = 'rgba(236,226,200,.45)', []
    for y0 in (yT, yB):
        ln += [f'<path d="M8 {y0 - i * sp:.1f}H{w - 8}" stroke="{ink}" stroke-width="1"/>' for i in range(5)]
    ln.append(f'<path d="M8 {yT - 4 * sp:.1f}V{yB:.1f}M{w - 8} {yT - 4 * sp:.1f}V{yB:.1f}" stroke="rgba(236,226,200,.7)" stroke-width="1.2"/>')
    g = lambda name, x, y: f'<path d="{GX[name]}" transform="translate({x:.1f},{y:.1f}) scale({s:.5f},{-s:.5f})" fill="{IV}"/>'
    ln += [g('gClef', 16, yT - sp), g('fClef', 16, yB - 3 * sp)]
    hw = 620 * s  # semibreve width
    for i, ch in enumerate(VOICES):
        cx = x0 + dx * i + dx / 2
        for v, p in enumerate(ch):
            m = re.match(r'([A-G])([#b]?)(\d)', p); st = int(m.group(3)) * 7 + STEP[m.group(1)]
            base, ref = (yT, 4 * 7 + 2) if v >= 2 else (yB, 2 * 7 + 4)
            y = base - (st - ref) * sp / 2
            for k in range(ref + 10, st + 1, 2):  # ledger lines above the staff
                ln.append(f'<path d="M{cx - hw / 2 - 3:.1f} {base - (k - ref) * sp / 2:.1f}h{hw + 6:.1f}" stroke="rgba(236,226,200,.7)" stroke-width="1"/>')
            for k in range(ref - 2, st - 1, -2):  # and below
                ln.append(f'<path d="M{cx - hw / 2 - 3:.1f} {base - (k - ref) * sp / 2:.1f}h{hw + 6:.1f}" stroke="rgba(236,226,200,.7)" stroke-width="1"/>')
            ln.append(g('noteheadWhole', cx - hw / 2, y))
            if m.group(2): ln.append(g('accidentalSharp' if m.group(2) == '#' else 'accidentalFlat', cx - hw / 2 - 9, y))
        if i: ln.append(f'<path d="M{x0 + dx * i:.1f} {yT - 4 * sp:.1f}V{yT:.1f}M{x0 + dx * i:.1f} {yB - 4 * sp:.1f}V{yB:.1f}" stroke="rgba(236,226,200,.28)" stroke-width="1"/>')
    h = yB + 12
    nums = ''.join(f'<span style="left:{x0 + dx * i + dx / 2:.1f}px;color:{colours[f]}">{n}</span>' for i, (n, f) in enumerate(ROW))
    return (f'<div class="ds-strip" style="width:{w}px"><svg width="{w}" height="{h:.0f}" viewBox="0 0 {w} {h:.0f}" role="img" aria-label="A minor: i, iv, v, VII, III, flat II first inversion, V, i">{"".join(ln)}</svg>'
            f'<div class="ds-nums" style="font-size:{size}px;height:{size * 1.5:.0f}px"><em>a:</em>{nums}</div></div>')


def numrow(colours, size, w=392, label='', cls=''):
    x0, dx = 62, (w - 62 - 14) / len(ROW)
    nums = ''.join(f'<span style="left:{x0 + dx * i + dx / 2:.1f}px;color:{colours[f]}">{n}</span>' for i, (n, f) in enumerate(ROW))
    return f'<div class="ds-nums {cls}" style="width:{w}px;font-size:{size}px;height:{max(22, size * 1.45):.0f}px"><i>{label}</i>{nums}</div>'


def cols(new, kind='normal'):
    c = {k: C.sim(h, kind) for k, _, h in EXIST}; c['N'] = C.sim(new, kind); return c


def cand_card(key, name, hx, line, pick):
    r = C.report(hx)
    ink = {k: C.darken_for(h, C.IVORY) for k, _, h in EXIST}; ink['N'] = C.darken_for(hx, C.IVORY)
    sw = ''.join(f'<span class="ds-sw"><b style="background:{h}"></b><small>{k}</small></span>' for k, _, h in EXIST)
    sw += f'<span class="ds-sw new"><b style="background:{hx}"></b><small>new</small></span>'
    sims = ''.join(numrow(cols(hx, k), 16, cls='sim') + f'<div class="ds-gap"><b>{lab}</b> · new colour is closest to {dict((a, b) for a, b, _ in EXIST)[r["gap"][k][1]].lower()}, ΔE {r["gap"][k][0]:.0f}</div>'
                   for k, lab in (('deutan', 'Deuteranopia'), ('protan', 'Protanopia'), ('tritan', 'Tritanopia')))
    asis = dict(cols(hx)); worst = min(r['contrast'].values())
    return f'''<section class="card ds-cand{' is-pick' if pick else ''}">
 <div class="ds-ch"><span class="ds-n disp">{key}</span><div><h3 class="disp">{name}</h3><code>{hx}</code></div>{'<span class="ds-rec">Recommended</span>' if pick else ''}</div>
 <p class="ds-line">{line}</p>
 <div class="ds-sws">{sw}</div>
 {strip(cols(hx))}
 {numrow(cols(hx), 16, label='16 px')}{numrow(cols(hx), 14, label='14 px')}
 <div class="ds-cap">As three kinds of colour-blindness see it</div>
 {sims}
 <div class="ds-cap">On ivory (selected chips; the app has no light theme)</div>
 <div class="ds-iv">{numrow(asis, 16, label='as is')}{numrow(ink, 16, label='deepened')}</div>
 <dl class="ds-facts"><div><dt>Contrast on the ground</dt><dd>{worst:.1f} : 1 <em>{'passes' if worst >= 4.5 else 'fails'} 4.5</em></dd></div>
 <div><dt>Smallest gap to the four</dt><dd>ΔE {r['min']:.0f} <em>{r['gap'][min(r['gap'], key=lambda k: r['gap'][k][0])][1]}, {dict(normal='typical vision', deutan='deuteranopia', protan='protanopia', tritan='tritanopia')[min(r['gap'], key=lambda k: r['gap'][k][0])]}</em></dd></div>
 <div><dt>Gap to plain ivory text</dt><dd>ΔE {C.de00(hx, IV):.0f}</dd></div>
 <div><dt>On ivory</dt><dd>{r['on_ivory']:.1f} : 1 as is · use <code>{ink['N']}</code></dd></div></dl>
</section>'''


# ====================================================================== the sheet
def b64(p, mime): return f'data:{mime};base64,' + base64.b64encode(pathlib.Path(p).read_bytes()).decode()


def fonts():
    f = EL / 'fonts'; g = REPO / 'fonts/eb-garamond'
    face = lambda fam, wt, p, st='normal': f"@font-face{{font-family:'{fam}';font-weight:{wt};font-style:{st};src:url({b64(p, 'font/woff2')}) format('woff2')}}"
    return ''.join([face('Outfit', 300, f / 'outfit-latin-300-normal.woff2'), face('Outfit', 400, f / 'outfit-latin-400-normal.woff2'),
                    face('Outfit', 600, f / 'outfit-latin-600-normal.woff2'), face('Poiret One', 400, f / 'poiret-one-latin-400-normal.woff2'),
                    face('EB Garamond', 500, g / 'eb-garamond-latin-500-normal.woff2')])


SHEET_CSS = (D / 'assets/sheet.css')


def phone(kind, title, m, lines, verdict, pick=False):
    li = ''.join(f'<li><b>{a}</b>{b}</li>' for a, b in lines)
    return f'''<div class="ds-opt{' is-pick' if pick else ''}">
 <div class="ds-oh"><span class="ds-n disp">{kind}</span><div><h3 class="disp">{title}</h3><span class="ds-meta">{m['n']} notes · rows {m['row']:.0f} px · ladder {m['lad']} px tall</span></div>{'<span class="ds-rec">Recommended</span>' if pick else ''}</div>
 <div class="ds-phone"><div class="ds-status"><span>9:41</span><i></i><span class="r"><svg viewBox="0 0 44 12" width="44" height="12"><path d="M1 11V8M5 11V6M9 11V4M13 11V1" stroke="#ece2c8" stroke-width="2.4" stroke-linecap="round"/><rect x="22" y="1.5" width="19" height="9" rx="2.5" fill="none" stroke="#ece2c8" stroke-opacity=".5"/><rect x="23.5" y="3" width="13" height="6" rx="1.2" fill="#ece2c8"/></svg></span></div>
  <img src="{b64(D / f'png/d5_{kind}_390.png', 'image/png')}" width="390" height="{VIEW[1]}" alt="Option {kind}: the melody card on a phone">
  <div class="ds-safari"><div class="pill">Composition Jungle Gym</div><div class="bar"><svg viewBox="0 0 250 22"><g fill="none" stroke="#9c927c" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4l-7 7 7 7M68 4l7 7-7 7M125 3v11M120 7l5-4 5 4M117 11v8h16v-8M177 5h14v14h-14zM184 5v14M236 5h10v10h-10zM232 9v10h10"/></g></svg></div><i></i></div></div>
 <ul class="ds-gl">{li}</ul>
 <p class="ds-verdict">{verdict}</p>
</div>'''


def sheet(M):
    A, B, Cc = M['A'], M['B'], M['C']
    see = lambda m: f'{m["seen"]} of {m["n"]} notes' if m['seen'] < m['n'] else f'all {m["n"]} notes'
    d5 = (phone('A', '44 px rows', A, [
            ('Tap accuracy', f' Full-size targets, {A["row"]:.0f} × {A["w"]} px.'),
            ('Scrolling', f' Here {see(A)} show under the stave; the lowest {A["n"] - A["seen"]} and Undo/Clear need a {A["need"]} px scroll. Check stays in the dock.' if A['seen'] < A['n'] else ' None for the ladder here.'),
            ('Stave and ladder', ' Stave stays pinned. The ladder is the single column students know from the classroom tone ladder.')],
            'What 0.48 already does, give or take 3 px.', True)
          + phone('B', '24 px rows', B, [
            ('Tap accuracy', f' Poor. {B["row"]:.0f} px rows are about half a fingertip; a slip lands a step out, which is exactly the mistake the drill marks.'),
            ('Scrolling', ' None. Ladder, Undo and Clear all show at once.'),
            ('Stave and ladder', ' Everything in view, but the hand signs shrink to 21 px and stop being readable.')],
            'Smaller than anything else in the Ear Lab. I would not ship it.')
          + phone('C', 'Two columns', Cc, [
            ('Tap accuracy', f' Full-size targets, {Cc["row"]:.0f} × {Cc["w"]} px, each half a row above the next.'),
            ('Scrolling', ' None. Ladder, Undo and Clear all show at once.'),
            ('Stave and ladder', ' Costs the single column: the eye zigzags, steps cross the gap and thirds stack (m–d–l, on the left). New to every student; “home” has less room.')],
            'Keeps the targets and loses the height. Worth building only if scrolling proves a problem in class.'))
    cands = ''.join(cand_card(k, n, h, l, k == '1') for k, n, h, l in CANDS)
    ex = {k: C.report(h, {a: b for a, _, b in EXIST if a != k}) for k, _, h in EXIST}
    old = C.report(OLD)
    html = f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CJG 0.48 · two decisions to see</title>
<style>{fonts()}{(EL / 'assets/app.css').read_text()}{SHEET_CSS.read_text()}</style></head><body class="ds-body">
<div class="ds">
<header class="ds-top"><div><div class="kicker">Composition Jungle Gym · 0.48 · for Justin</div><h1 class="disp">Two decisions to see</h1></div>
 <p class="sub">Decision 5, the solfa ladder on phones, and Decision 12, a colour for minor v and VII. Everything shown is measured from the mock-ups in this folder.</p></header>

<section class="ds-sec"><div class="ds-sh"><span class="ds-num disp">5</span><div><h2 class="disp">The solfa ladder on phones</h2>
 <p>Melodic dictation, rung 3, E minor, four notes written. A 390 × 844 phone in Safari with its bars showing, which leaves {VIEW[1]} px for the page.</p></div></div>
 <p class="ds-fix"><b>A correction to my spec first.</b> I wrote that 44 px rows would be “up from 24”. That was wrong. The app’s 24 px is a grid track and each note spans two, so the ladder you have now already has <b>47 px</b> rows: 384 px tall at rung 3 (8 notes), 432 px at rung 2 (9 notes), measured in the running app at 390 px. So A is close to what ships today, and B would be a new, smaller ladder, not a return to 0.47.</p>
 <div class="ds-opts">{d5}</div>
 <div class="ds-call"><span class="kicker">Recommendation</span><p><b>A. Keep the single column at full height.</b> It is the tone ladder students already sing from, the targets are safe, and the cost is one short scroll for the bottom two notes while the browser bars are up. Once the bars tuck away (about 80 px more) this eight-note ladder fits whole; the nine-note ladder at rung 2 still needs a short scroll unless the app is opened from the home screen. Check is always in reach in the dock. Nothing in the app has to change: the 47 px rows it has now already meet the rule, and I will correct the spec. Hold C in reserve: it is the only way to get full targets with no scroll, but it changes the picture of the ladder, so it should be your call as the Kodály teacher, not a layout fix I slip in.</p></div>
</section>

<section class="ds-sec"><div class="ds-sh"><span class="ds-num disp">12</span><div><h2 class="disp">A colour for minor v and VII</h2>
 <p>Numerals under the SATB scores take the colour of their function. In a minor key, v and VII have no leading note, so they are not dominant red. They were blue-grey <code>{OLD}</code>, which you turned down. Three others, each next to the four you have.</p></div></div>
 <div class="ds-cands">{cands}</div>
 <div class="ds-two">
  <div class="ds-call"><span class="kicker">Recommendation</span><p><b>1. Madder rose <code>#bd6b97</code></b>, deepened to <code>{C.darken_for('#bd6b97', C.IVORY)}</code> on ivory. It sits beside the dominant’s red as its cooler relative, which is the theory: same region of the key, without the semitone pull. It clears 4.5 : 1 on every ground and stays apart from the other four for all three kinds of colour-blindness. Verdigris measures a little further apart, but it is the nearest thing here to the blue-grey you rejected. Shell fails for a different reason: beside ivory text it stops looking like a category.</p></div>
  <div class="ds-call"><span class="kicker">What to call it</span><p><b>“Modal dominant”</b>, short code <b>MD</b>, with the plain word <b>“soft pull”</b> to sit beside home, away and pull. It says what the chords are (built on the dominant side of the key, from the unraised 7th) without claiming one school’s label. The note behind it can name the traditions: function theory calls v the minor dominant and VII its relative; many English-language texts call VII the subtonic chord; in modal, folk and rock harmony the two are the ordinary closing chords. Second choice: “subtonic chords”.</p></div>
 </div>
 <p class="ds-foot">ΔE is CIEDE2000 between the candidate and its nearest neighbour among the four, after simulating each kind of colour-blindness (Machado et al. 2009, full severity); above about 10 two colours are easy to tell apart. For scale, the old blue-grey scored ΔE {old['min']:.0f}. Two things about the existing four turned up on the way and are outside this decision: tonic green and predominant gold are only ΔE {ex['T']['gap']['deutan'][0]:.0f} apart under deuteranopia, and dominant red is {min(ex['D']['contrast'].values()):.1f} : 1 on the darkest panel, under the 4.5 line. The numerals differ by their letters as well, so neither blocks 0.48.</p>
</section>
</div></body></html>'''
    (D / 'sheet.html').write_text(html)


def main():
    global GX
    from playwright.sync_api import sync_playwright
    GX = more_glyphs(); (D / 'png').mkdir(exist_ok=True)
    for k in 'ABC': panel(k)
    M = {}
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for k in 'ABC':
            pg = b.new_page(viewport={'width': VIEW[0], 'height': VIEW[1]}, device_scale_factor=2)
            pg.goto((D / f'd5_{k}.html').as_uri()); pg.wait_for_timeout(500)
            M[k] = pg.evaluate(MEASURE); pg.screenshot(path=str(D / f'png/d5_{k}_390.png'))
            pg.goto((D / f'd5_{k}.html').as_uri() + '#top'); pg.reload(); pg.wait_for_timeout(400)
            pg.screenshot(path=str(D / f'png/d5_{k}_390_full.png'), full_page=True); pg.close()
            if M[k]['over'] > 0: print('SIDEWAYS SCROLL', k, M[k]['over'])
        (D / 'assets/measured.json').write_text(json.dumps(M, indent=1))
        sheet(M)
        pg = b.new_page(viewport={'width': 1440, 'height': 900})
        pg.goto((D / 'sheet.html').as_uri()); pg.wait_for_timeout(700)
        over = pg.evaluate('document.documentElement.scrollWidth-innerWidth')
        small = pg.evaluate("""()=>[...document.querySelectorAll('.ds *')].filter(e=>e.children.length===0&&e.textContent.trim()&&parseFloat(getComputedStyle(e).fontSize)<11&&!e.closest('svg')&&e.tagName!=='SUP').map(e=>e.className+':'+getComputedStyle(e).fontSize).slice(0,8)""")
        pg.screenshot(path=str(D / 'png/sheet_1440.png'), full_page=True)
        print('sheet 1440: sideways', over, 'text under 11 px', small)
        pg.set_viewport_size({'width': 390, 'height': 844}); pg.wait_for_timeout(300)
        print('sheet 390: sideways', pg.evaluate('document.documentElement.scrollWidth-innerWidth'))
        b.close()
    for k, m in M.items(): print(k, m)


if __name__ == '__main__':
    main()
