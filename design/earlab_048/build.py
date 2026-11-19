#!/usr/bin/env python3
"""Builds the static Ear Lab 0.48 mock-ups in this folder.  Run:  python3 build.py
Output: one plain .html per state (no script needed to view them).  Notation is drawn as inline SVG
from the Bravura outlines that VexFlow already ships (assets/glyphs.json), so production can draw the
same shapes with Vex.Flow.Glyph and needs no new font file."""
import json, pathlib, re

H = pathlib.Path(__file__).resolve().parent
G = json.load(open(H / 'assets/glyphs.json'))
FRAME = json.load(open(H / 'assets/frame.json'))
IV, MUTED, GOLD, GOLDHI, RED, GREEN, LINE = '#ece2c8', '#9c927c', '#c9a24a', '#f0d48a', '#c8473b', '#8fbf6a', '#2a2418'

# ------------------------------------------------------------------ icons
TICK = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 8.6l3.3 3.2L13 4.6" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>'
CROSS = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M4 4l8 8M12 4l-8 8" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
NEAR = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M3 6.2c2-2 3.4-1.6 5 0s3 2 5 0M3 10.6c2-2 3.4-1.6 5 0s3 2 5 0" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>'
EYE = '<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M1.5 8C3.3 5 5.5 3.6 8 3.6S12.7 5 14.5 8c-1.8 3-4 4.4-6.5 4.4S3.3 11 1.5 8z" fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="8" cy="8" r="2" fill="currentColor"/></svg>'


def play(state='ready', pct=0, cls='', tag='button'):
    """The one Play/Stop toggle.  state: ready | playing | loading.  pct: progress 0-100 (mock only; live it is a CSS animation)."""
    arc = f' style="stroke-dashoffset:{100 - pct};animation:none"' if state == 'playing' else ''
    lab = 'Stop' if state == 'playing' else 'Play'
    attrs = f'aria-label="{lab}" aria-pressed="{"true" if state == "playing" else "false"}"' if tag == 'button' else 'aria-hidden="true"'
    return (f'<{tag} class="el-play {state if state != "ready" else ""} {cls}" {attrs}>'
            f'<svg class="ring" viewBox="0 0 48 48" aria-hidden="true"><circle class="trk" cx="24" cy="24" r="22.5"/><circle class="arc" cx="24" cy="24" r="22.5" pathLength="100"{arc}/></svg>'
            '<svg class="ico play" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.2v11.6L14 8z" fill="currentColor"/></svg>'
            f'<svg class="ico stop" viewBox="0 0 16 16" aria-hidden="true"><rect x="2" y="2" width="12" height="12" rx="1.5" fill="currentColor"/></svg></{tag}>')


# ------------------------------------------------------------------ notation
S = 0.02376  # px per outline unit at VexFlow "point 33": a notehead 10.1 px wide, 8.6 px tall
HW = 425 * S


def glyph(name, x, y, fill=IV, s=S):
    return f'<path d="{G[name]}" transform="translate({x:.1f},{y:.1f}) scale({s},{-s})" fill="{fill}"/>'


RCELL = {'q': [(4, 0)], 'e2': [(2, 0), (2, 0)], 'h': [(8, 0)], 's4': [(1, 0)] * 4, 'qr': [(4, 1)], 'dq': [(6, 0), (2, 0)],
         'es2': [(2, 0), (1, 0), (1, 0)], 's2e': [(1, 0), (1, 0), (2, 0)], 'syn': [(2, 0), (4, 0), (2, 0)]}
RW = {k: sum(d for d, _ in v) for k, v in RCELL.items()}
RNAME = {'q': 'crotchet', 'e2': '2 quavers', 'h': 'minim', 's4': '4 semiquavers', 'qr': 'crotchet rest', 'dq': 'dotted crotchet, quaver',
         'es2': 'quaver, 2 semiquavers', 's2e': '2 semiquavers, quaver', 'syn': 'quaver, crotchet, quaver'}
TNAME = {'q': 'ta', 'e2': 'ti-ti', 'h': 'ta-a'}


def cell_marks(cell, x, u, top, base, stick=False, ink=IV):
    """One cell's notes.  x = left edge of the cell's first sixteenth; u = px per sixteenth; top = stem top; base = notehead centre."""
    out, pos, stems = [], 0, []
    for d, rest in RCELL[cell]:
        nx = x + pos * u + 6
        if rest:
            out.append(glyph('restQuarter', nx, base, ink))
        else:
            sx = nx + HW - .65
            if stick and d < 8:
                sx = nx + HW / 2
                out.append(f'<line x1="{sx:.1f}" y1="{base + 4.5}" x2="{sx:.1f}" y2="{top}" stroke="{ink}" stroke-width="1.6" stroke-linecap="round"/>')
            else:
                out.append(glyph('noteheadHalf' if d == 8 else 'noteheadBlack', nx, base, ink))
                out.append(f'<line x1="{sx:.1f}" y1="{base - 1.5}" x2="{sx:.1f}" y2="{top}" stroke="{ink}" stroke-width="1.3"/>')
            if d == 6:
                out.append(glyph('augmentationDot', nx + HW + 3, base - 4.3, ink))
            stems.append((sx, d))
        pos += d
    short = [i for i, (sx, d) in enumerate(stems) if d <= 2]
    if len(short) == len(stems) and len(stems) > 1:  # e2, s4, es2, s2e: one beam group
        a, b = stems[0][0], stems[-1][0]
        out.append(f'<rect x="{a - .65:.1f}" y="{top}" width="{b - a + 1.3:.1f}" height="4" fill="{ink}"/>')
        for i in range(len(stems) - 1):
            if stems[i][1] == 1 and stems[i + 1][1] == 1:
                out.append(f'<rect x="{stems[i][0] - .65:.1f}" y="{top + 6.5}" width="{stems[i + 1][0] - stems[i][0] + 1.3:.1f}" height="4" fill="{ink}"/>')
    else:  # lone quavers (dq, syn) carry a flag
        for sx, d in stems:
            if d == 2:
                if stick:
                    out.append(f'<path d="M{sx:.1f} {top}l7 8" stroke="{ink}" stroke-width="1.6" stroke-linecap="round" fill="none"/>')
                else:
                    out.append(glyph('flag8thUp', sx - .65, top, ink))
    return ''.join(out)


def rhy(cells, u=18, bars=1, total=None, sig=True, stick=False, ruler=True, strip=True, cursor=False, marks=None,
        countin=0, ink=IV, strip_col=None, first_beat=1, final=True, label=None):
    """A one-line rhythm stave with its sound strip.  cells: what is written; bars: how many bars this line holds.
    marks: per beat True/False (comparison).  countin: n numerals lit (1-4).  Geometry is in SPEC.md section 6."""
    X0 = 34 if sig else 10
    BG = 16  # gap taken by a barline between bars
    top, base, sy = 26, 60, 76
    Wd = X0 + bars * 16 * u + (bars - 1) * BG + 14
    Ht = 88
    o = [f'<svg viewBox="0 0 {Wd} {Ht}" width="{Wd}" height="{Ht}" role="img" aria-label="{label or "rhythm"}">']
    barx = lambda b: X0 + b * (16 * u + BG)
    if marks:
        for i, ok in enumerate(marks):
            if not ok:
                b, k = divmod(i, 4)
                o.append(f'<rect x="{barx(b) + k * 4 * u}" y="0" width="{4 * u}" height="{Ht}" rx="6" fill="rgba(200,71,59,.13)"/>')
    if not stick:
        o.append(f'<line x1="4" y1="{base}" x2="{Wd - 6}" y2="{base}" stroke="#c9b98f" stroke-opacity=".55" stroke-width="1"/>')
    if sig:
        o.append(glyph('timeSig4', 6, base - 8.6, ink) + glyph('timeSig4', 6, base + 8.6, ink))
    for b in range(bars):
        for k in range(4):
            cx = barx(b) + k * 4 * u + 6 + HW / 2
            lit = countin and b == 0 and k < countin
            now = countin and b == 0 and k == countin - 1
            col = GOLDHI if lit else MUTED
            if marks:
                okb = marks[b * 4 + k]
                col = GREEN if okb else RED
                p = 'M-3 0l2.2 2.2L3.4 -2.6' if okb else 'M-2.6 -2.6l5.2 5.2M2.6 -2.6l-5.2 5.2'
                o.append(f'<path d="{p}" transform="translate({cx + 11:.1f},9)" fill="none" stroke="{col}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>')
            if ruler:
                if now:
                    o.append(f'<circle cx="{cx:.1f}" cy="9" r="9" fill="rgba(240,212,138,.16)" stroke="{GOLDHI}" stroke-width="1"/>')
                o.append(f'<text x="{cx:.1f}" y="13" text-anchor="middle" font-family="Outfit" font-size="{12.5 if lit else 11}" font-weight="{600 if lit else 400}" fill="{col}">{k + 1}</text>')
        if b < bars - 1:
            bx = barx(b) + 16 * u + BG / 2 - 1
            o.append(f'<line x1="{bx}" y1="{base - 17}" x2="{bx}" y2="{base + 17}" stroke="{ink}" stroke-width="1"/>')
    if final:
        ex = Wd - 6
        o.append(f'<line x1="{ex - 6}" y1="{base - 17}" x2="{ex - 6}" y2="{base + 17}" stroke="{ink}" stroke-width="1"/><rect x="{ex - 3}" y="{base - 17}" width="3.5" height="34" fill="{ink}"/>')
    pos = 0
    sc = strip_col or ink
    for c in cells:
        b, p = divmod(pos, 16)
        x = barx(b) + p * u
        o.append(cell_marks(c, x, u, top, base, stick, ink))
        if strip:
            q = 0
            for d, rest in RCELL[c]:
                xx = x + q * u + 2.5
                if rest:
                    o.append(f'<line x1="{xx + 1:.1f}" y1="{sy + 3}" x2="{xx + d * u - 6:.1f}" y2="{sy + 3}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="2 5" stroke-linecap="round"/>')
                else:
                    o.append(f'<rect x="{xx:.1f}" y="{sy}" width="{d * u - 5:.1f}" height="6" rx="3" fill="{sc}" fill-opacity=".8"/>')
                q += d
        pos += RW[c]
    tot = total if total is not None else bars * 16
    if cursor and pos < tot:
        b, p = divmod(pos, 16)
        x = barx(b) + p * u
        o.append(f'<line x1="{x + 1}" y1="{top - 4}" x2="{x + 1}" y2="{sy + 8}" stroke="{GOLD}" stroke-width="1.5" stroke-linecap="round"/>')
        o.append(f'<path d="M{x - 3.5} {top - 9}h9l-4.5 5.5z" fill="{GOLD}"/>')
        k = pos
        while k < tot:  # the beats still to fill: empty slots on the sound strip
            b, p = divmod(k, 16)
            o.append(f'<rect x="{barx(b) + p * u + 3}" y="{sy + .5}" width="{4 * u - 6}" height="5" rx="2.5" fill="none" stroke="#7a6e55" stroke-width="1" stroke-dasharray="2 3"/>')
            k += 4
    o.append('</svg>')
    return ''.join(o)


def tile(cell, u=14, stick=False, named=False, disabled=False):
    w = RW[cell] * u
    base = 44
    svg = (f'<svg viewBox="0 0 {w} 56" width="{w}" height="56" aria-hidden="true">'
           + ('' if stick else f'<line x1="0" y1="{base}" x2="{w}" y2="{base}" stroke="#c9b98f" stroke-opacity=".3"/>')
           + cell_marks(cell, -2.5 if RW[cell] == 4 else 2, u, 12, base, stick) + '</svg>')
    if cell in ('q', 'qr', 'h'):  # single symbols sit centred in the tile
        svg = (f'<svg viewBox="0 0 {w} 56" width="{w}" height="56" aria-hidden="true">'
               + ('' if stick else f'<line x1="0" y1="{base}" x2="{w}" y2="{base}" stroke="#c9b98f" stroke-opacity=".3"/>')
               + cell_marks(cell, (w - HW) / 2 - 6, u, 12, base, stick) + '</svg>')
    nm = f'<small>{TNAME[cell]}</small>' if named and cell in TNAME else ''
    return f'<button class="el-tile" style="width:{w}px" aria-label="{RNAME[cell]}" title="{RNAME[cell]}" {"disabled" if disabled else ""}>{svg}{nm}</button>'


def sig_svg(n, d):
    s = S * 1.05
    def num(v, y):
        ds = str(v)
        wd = sum({'1': 300}.get(c, 470) for c in ds) * 1.44 * s
        x = (26 - wd) / 2
        out = ''
        for c in ds:
            out += f'<path d="{G["timeSig" + c]}" transform="translate({x:.1f},{y}) scale({s},{-s})"/>'
            x += {'1': 300}.get(c, 470) * 1.44 * s
        return out
    return f'<svg class="sig" viewBox="0 0 26 44" aria-hidden="true">{num(n, 11.5)}{num(d, 32.5)}</svg>'


def pic_svg(beats, sub):
    """The beat picture in a metre cell: a large dot for each beat, small dots for how it splits."""
    step, gap, x, o = 10, 8, 5, []
    for b in range(beats):
        o.append(f'<circle cx="{x}" cy="8" r="4.6"/>')
        for s in range(1, sub):
            o.append(f'<circle cx="{x + s * step}" cy="8" r="2.3" fill-opacity=".8"/>')
        x += sub * step + gap
    w = x - gap - step + 5 + 2
    return f'<svg class="pic" viewBox="0 0 {w} 16" aria-hidden="true">{"".join(o)}</svg>'


def beats_svg(beats, sub, acc, bars=4, now=None):
    step, o, parts = 11, [], []
    for bar in range(bars):
        w = beats * sub * step + 16
        s = [f'<svg viewBox="0 0 {w} 36" width="{w}" height="36" aria-hidden="true"><line x1="1" y1="2" x2="1" y2="22" stroke="#5a5040"/>']
        for b in range(beats):
            x = 12 + b * sub * step
            r = {2: 5.5, 1: 4.2, 0: 3.4}[acc[b]]
            on = now == (bar, b)
            if on:
                s.append(f'<circle cx="{x}" cy="12" r="9.5" fill="rgba(240,212,138,.16)" stroke="{GOLDHI}"/>')
            s.append(f'<circle cx="{x}" cy="12" r="{r}" fill="{GOLDHI if on else GOLD}" fill-opacity="{1 if acc[b] else .7}"/>')
            for k in range(1, sub):
                s.append(f'<circle cx="{x + k * step}" cy="12" r="1.7" fill="{MUTED}"/>')
            s.append(f'<text x="{x}" y="34" text-anchor="middle" font-family="Outfit" font-size="11" fill="{GOLDHI if on else MUTED}">{b + 1}</text>')
        s.append('</svg>')
        parts.append(''.join(s))
    return f'<div class="el-beats {"two" if beats * sub > 6 else ""}" role="img" aria-label="Four bars, the beats shown">' + ''.join(parts) + '</div>'


# ------------------------------------------------------------------ page pieces
DRILLS = [('metre', 'Pulse and metre', 'Stage 4–5', 4), ('rhy', 'Rhythm dictation', 'Stage 4–5', 4), ('qual', 'Chord quality', 'Stage 4–6', 4),
          ('cad', 'Cadences', 'Stage 5–6', 5), ('bass', 'Bass and numerals', 'Stage 5–6', 5), ('mel', 'Melodic dictation', 'Stage 4–6', 4),
          ('blind', 'Blind analysis', 'Stage 5–6', 5)]


def drills(on, stage=6):
    vis = [d for d in DRILLS if d[3] <= stage]
    h = ''.join(f'<button class="el-drill {"on" if k == on else ""}" role="tab" aria-selected="{"true" if k == on else "false"}"><b>{n}</b><small>{t}</small></button>' for k, n, t, _ in vis)
    if len(vis) < len(DRILLS):
        h += f'<button class="el-all">{len(DRILLS) - len(vis)} more for Stage 5–6 · show all</button>'
    return f'<div class="el-drills" role="tablist" aria-label="Ear Lab drills">{h}</div>'


def tally(ok, n, streak, best, label='correct'):
    if n == 0:
        return ('<div class="el-tally is-new" role="status" aria-label="Score: no answers yet"><div class="el-score"><b>–</b><span>no answers yet</span></div></div>')
    return (f'<div class="el-tally" role="status" aria-label="Score {ok} of {n}, streak {streak}, best {best}"><div class="el-score"><b>{ok}</b><span>of {n}</span></div>'
            f'<div class="el-side"><div>Streak <b>{streak}</b></div><div>Best <b>{best}</b></div></div></div>')


def head(title, tag, rung, t, rungs=3, note=''):
    rb = ''.join(f'<button class="{"on" if i == rung else ""}" aria-pressed="{"true" if i == rung else "false"}">Rung {i}</button>' for i in range(1, rungs + 1))
    more = '<button class="el-all" style="margin-left:2px">show all rungs</button>' if rungs < 3 else ''
    return (f'<div class="el-head"><div><div class="el-tag">{tag}</div><h2 class="el-title">{title}</h2></div>{t}'
            f'<div class="el-rungrow"><div class="el-rungs" role="group" aria-label="Rung">{rb}</div>{more}<span class="el-rungnote">{note}</span></div></div>')


def stage(state, label, sub, acts, extra='', pct=0):
    return (f'<div class="el-stage">{play(state, pct)}<div class="el-now {state}" aria-live="polite"><b>{label}</b><span>{sub}</span></div>'
            f'<div class="el-acts">{acts}</div>{extra}</div>')


def foot(stats, mode='idle', name='Cadences'):
    if mode == 'confirm':
        r = f'<span class="el-confirm">Reset the {name} score?<button class="el-btn sm danger">Reset</button><button class="el-btn sm">Keep it</button></span>'
    elif mode == 'undo':
        r = '<span class="el-confirm">Score reset.<button class="el-btn sm">Undo</button></span>'
    else:
        r = '<button class="el-btn sm">Reset score</button>'
    return f'<div class="el-foot"><span class="stats">{stats}</span><span class="sp"></span>{r}<button class="el-btn sm">Save to journal</button></div>'


def tips(items, tail=''):
    return ('<section class="card"><h3>Listening for it</h3><ol class="el-tips">' + ''.join(f'<li>{x}</li>' for x in items) + '</ol>'
            + (f'<p>{tail}</p>' if tail else '') + '</section>')


def badge(kind):
    return {'ans': f'<span class="el-badge">{TICK}<span>Answer</span></span>', 'mine': f'<span class="el-badge">{CROSS}<span>Your answer</span></span>',
            'both': f'<span class="el-badge">{TICK}<span>Your answer</span></span>', 'near': f'<span class="el-badge">{NEAR}<span>Your answer</span></span>'}[kind]


MET = [('2/4', 2, 2, [2, 0]), ('3/4', 3, 2, [2, 0, 0]), ('4/4', 4, 2, [2, 0, 1, 0]), ('6/8', 2, 3, [2, 0]), ('9/8', 3, 3, [2, 0, 0]), ('12/8', 4, 3, [2, 0, 1, 0])]
METN = {'2/4': 'Simple duple', '3/4': 'Simple triple', '4/4': 'Simple quadruple', '6/8': 'Compound duple', '9/8': 'Compound triple', '12/8': 'Compound quadruple'}


def metre_grid(ans=None, mine=None, wait=False):
    def cell(m):
        k, b, s, _ = m
        n, d = k.split('/')
        cls, bd = '', ''
        if ans:
            cls = 'is-ans' if k == ans else 'is-mine' if k == mine else 'is-dim'
            bd = badge('both' if k == ans == mine else 'ans') if k == ans else badge('mine') if k == mine else ''
        return (f'<button class="el-opt el-mcell {cls}" aria-label="{METN[k]}, {n} {d}" {"disabled" if ans or wait else ""}>{sig_svg(n, d)}{pic_svg(b, s)}{bd}</button>')
    h = ('<div class="corner"></div><div class="el-mh">Duple<small>2 beats in a bar</small></div><div class="el-mh">Triple<small>3 beats in a bar</small></div><div class="el-mh">Quadruple<small>4 beats in a bar</small></div>'
         '<div class="el-mr">Simple<small>each beat splits in two</small></div>' + ''.join(cell(m) for m in MET[:3])
         + '<div class="el-mr">Compound<small>each beat splits in three</small></div>' + ''.join(cell(m) for m in MET[3:]))
    return f'<div class="el-lbl">Your answer</div><div class="el-mgrid el-opts {"wait" if wait else ""}" style="display:grid" role="group" aria-label="Metre">{h}</div>'


METRE_TIPS = tips(['<b>Find the heavy click.</b> It marks beat 1. Tap it on your knee.',
                   '<b>Count to the next heavy click.</b> Two, three or four beats give you duple, triple or quadruple.',
                   '<b>Listen inside one beat.</b> Two even sounds is simple. Three is compound, with a rolling, skipping feel.'],
                  'The speed changes every time (60–120 beats a minute), so fast or slow is never a clue. 6/8 is two beats of three quavers, not six beats.')
RHY_TIPS = tips(['<b>Keep the pulse.</b> Tap the four beats with one hand while you listen.',
                 '<b>Say it back.</b> Use time names (ta, ti-ti, ta-a) or count 1 &amp; 2 &amp; before you write anything.',
                 '<b>Write one beat at a time.</b> Each tile is as wide as it is long, so a full bar fills the line.'],
                'The bar under the notes shows how long each sound lasts. A dashed gap is a rest. Dotted crotchet + quaver is long-short across two beats; quaver, crotchet, quaver is short-long-short.')
CAD_TIPS = tips(['<b>Start with the last chord.</b> Home (I), the dominant (V), or somewhere else (vi)?',
                 '<b>Then the chord before it.</b> V before I is perfect; IV before I is plagal.',
                 '<b>Follow the bass.</b> Sing the last two bass notes. Fa falling a semitone to mi in a minor key is the Phrygian cadence.',
                 '<b>Listen for a delay.</b> A cadential 6/4 holds the dominant bass under I, then V, before the close.'],
                'Australian names are used here. US names: perfect = authentic, imperfect = half, interrupted = deceptive.')


def page(title, body, stage_on=6, sounding=False, dock='', scroll=0):
    top = FRAME['top'].replace(' class="on"', '').replace(f'data-l="{stage_on}"', f'data-l="{stage_on}" class="on"')
    top = top.replace('id="tStop"', 'id="tStop"' + ('' if sounding else ' hidden'))
    js = f'<script>scrollTo(0,{scroll})</script>' if scroll else ''
    return f'''<!doctype html>
<html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ear Lab 0.48 mock-up · {title}</title>
<link rel="stylesheet" href="assets/fonts.css"><link rel="stylesheet" href="assets/app.css"><link rel="stylesheet" href="assets/earlab048.css">
</head><body class="{"ear-sounding" if sounding else ""}">
{FRAME['rail']}
{top}
<main><section class="room" id="room-ear">
{FRAME['head']}
<div id="earMain" class="el">
{body}
</div></section></main>
{dock}
{FRAME['tab']}
{js}</body></html>'''


VARS_RHY = lambda pulse='on', speed='normal', sound='tone': (
    '<div class="el-vars"><span class="cap">Pulse</span><div class="el-seg" role="group" aria-label="Pulse">'
    f'<button aria-pressed="{"true" if pulse == "on" else "false"}">On</button><button aria-pressed="{"true" if pulse != "on" else "false"}">Off</button></div><span class="gap"></span>'
    '<span class="cap">Speed</span><div class="el-seg" role="group" aria-label="Speed">'
    f'<button aria-pressed="{"true" if speed == "steady" else "false"}">Steady · 72</button><button aria-pressed="{"true" if speed == "normal" else "false"}">Normal · 100</button></div>'
    f'<span class="gap"></span><span class="fix">Sound: {sound}</span></div>')

EDIT = lambda full: ('<div class="el-edit"><button class="el-btn sm">↶ Undo</button><button class="el-btn sm" disabled>↷ Redo</button><button class="el-btn sm">Clear</button><span class="sp"></span>'
                     f'<button class="el-btn gold" {"" if full else "disabled"}>Check</button></div>')


def build():
    P = {}
    # ---------------- metre
    mh = lambda t, stage_n=5: head('Pulse and metre', 'Stage 4–5', 2, t, rungs=3 if stage_n >= 5 else 2)
    ask = '<p class="el-ask">How many beats in a bar? Does each beat split in two or in three?</p>'
    P['metre_idle'] = (drills('metre', 4) + '<div class="el-cols"><section class="card">' + mh(tally(0, 0, 0, 0), 4) + ask
                       + stage('ready', 'Play', 'Press play to hear the first one', '') + metre_grid(wait=True)
                       + foot('No answers yet') + '</section>' + METRE_TIPS + '</div>', 4, False)
    P['metre_playing'] = (drills('metre', 5) + '<div class="el-cols"><section class="card">' + mh(tally(6, 8, 2, 4)) + ask
                          + stage('playing', 'Stop', 'Playing · 0:04 of 0:11', '<button class="el-btn">Show me</button><button class="el-btn">Skip →</button>', pct=38)
                          + metre_grid() + foot('<b>8</b> answered · <b>1</b> shown · <b>2</b> skipped', name='Pulse and metre') + '</section>' + METRE_TIPS + '</div>', 5, True)
    res = ('<div class="el-result bad" role="status"><div class="el-mark">' + CROSS + '</div><div><div class="el-verdict">Not this time</div>'
           '<div class="el-answer" role="heading" aria-level="3">Compound duple <small>6/8</small></div></div><button class="el-btn gold">Next →</button>'
           '<div class="el-body"><p class="el-teach">You heard six quavers in every bar, and that is right. In 3/4 they fall in twos, making three beats. Here they fall in threes, so there are only two beats in a bar.</p>'
           '<div class="el-replays"><button class="el-replay">' + play(tag='span') + '<span>Hear it again with the beats shown</span></button>'
           '<button class="el-btn">Hear 3/4 at the same speed</button></div>' + beats_svg(2, 3, [2, 0]) + '</div></div>')
    P['metre_answered'] = (drills('metre', 5) + '<div class="el-cols"><section class="card">' + mh(tally(6, 9, 0, 4)) + ask + res
                           + metre_grid('6/8', '3/4') + foot('<b>9</b> answered · <b>1</b> shown · <b>2</b> skipped', name='Pulse and metre') + '</section>' + METRE_TIPS + '</div>', 5, False)
    # ---------------- rhythm
    rh = lambda t, r=3: head('Rhythm dictation', 'Stage 4–5', r, t)
    ANS = ['e2', 'q', 'dq', 's4', 'q', 'h']
    MINE = ['e2', 'q', 'dq', 'es2', 'q', 'h']
    R3 = ['q', 'e2', 's4', 'qr', 'es2', 's2e', 'h', 'dq', 'syn']

    def rhy_answering(countin=0, playing=False):
        st = (stage('playing', 'Stop', 'Count-in · 3' if countin else 'Playing · 0:03 of 0:07', '<button class="el-btn">Show me</button><button class="el-btn">Skip →</button>', VARS_RHY(), pct=22 if countin else 45)
              if playing else stage('ready', 'Play again', 'Ready · played twice', '<button class="el-btn">Show me</button><button class="el-btn">Skip →</button>', VARS_RHY()))
        wide = f'<div class="el-rhy wide">{rhy(ANS[:4], 18, 2, cursor=True, countin=countin, label="Your rhythm so far: 5 of 8 beats")}</div>'
        nar = (f'<div class="el-rhy narrow">{rhy(ANS[:3], 17, 1, cursor=False, countin=countin, final=False, label="Bar 1")}'
               f'{rhy(ANS[3:4], 17, 1, cursor=True, label="Bar 2")}</div>')
        tl = ''.join(tile(c, disabled=(c in ('h', 'dq', 'syn'))) for c in R3)
        return (drills('rhy') + '<div class="el-cols"><section class="card">' + rh(tally(4, 6, 1, 3))
                + '<p class="el-ask">Four clicks count you in, then the rhythm plays on one note. Write what you hear.</p>' + st
                + '<div class="el-lbl">Your rhythm · 5 of 8 beats</div>' + wide + nar
                + f'<div class="el-lbl">Add the next beat</div><div class="el-tiles">{tl}</div>' + EDIT(False)
                + foot('<b>6</b> answered · <b>0</b> shown · <b>1</b> skipped', name='Rhythm dictation') + '</section>' + RHY_TIPS + '</div>')
    P['rhythm_answering'] = (rhy_answering(), 6, False)
    P['rhythm_countin'] = (rhy_answering(3, True), 6, True)
    mk = [True] * 4 + [False] + [True] * 3
    cmp_w = (f'<div class="el-cmp wide"><div class="who">You wrote</div>{rhy(MINE, 18, 2, marks=mk, label="You wrote")}'
             f'<div class="who ans">It was</div>{rhy(ANS, 18, 2, ruler=False, strip_col=GOLD, label="It was")}</div>')
    cmp_n = (f'<div class="el-cmp narrow"><div class="who">You wrote · bar 1</div>{rhy(MINE[:3], 17, 1, marks=mk[:4], final=False)}<div class="who ans">It was</div>{rhy(ANS[:3], 17, 1, ruler=False, strip_col=GOLD, final=False)}'
             f'<div class="who">You wrote · bar 2</div>{rhy(MINE[3:], 17, 1, marks=mk[4:])}<div class="who ans">It was</div>{rhy(ANS[3:], 17, 1, ruler=False, strip_col=GOLD)}</div>')
    res = ('<div class="el-result bad" role="status"><div class="el-mark">' + CROSS + '</div><div><div class="el-verdict">Not this time</div>'
           '<div class="el-answer" role="heading" aria-level="3">7 of 8 beats match</div></div><button class="el-btn gold">Next →</button>'
           '<div class="el-body"><p class="el-teach">Bar 1 is exactly right, dotted rhythm and all. In bar 2, beat 1, you wrote a quaver and two semiquavers (long-short-short). Listen for four even sounds there: four semiquavers.</p></div>'
           + cmp_w + cmp_n +
           '<div class="el-body"><div class="el-replays"><button class="el-replay">' + play(tag='span') + '<span>Hear bar 2, beat 1: yours, then the answer</span></button>'
           '<button class="el-btn">Hear it all, following the notes</button></div></div></div>')
    P['rhythm_checked'] = (drills('rhy') + '<div class="el-cols"><section class="card">' + rh(tally(4, 7, 0, 3))
                           + '<p class="el-ask">Four clicks count you in, then the rhythm plays on one note. Write what you hear.</p>' + res
                           + foot('<b>7</b> answered · <b>0</b> shown · <b>1</b> skipped', name='Rhythm dictation') + '</section>' + RHY_TIPS + '</div>', 6, False)
    R1 = ['e2', 'q']
    P['rhythm_rung1'] = (drills('rhy', 4) + '<div class="el-cols"><section class="card">' + head('Rhythm dictation', 'Stage 4–5', 1, tally(2, 2, 2, 2), rungs=2)
                         + '<p class="el-ask">Four clicks count you in, then the rhythm is clapped. Write what you hear.</p>'
                         + stage('ready', 'Play again', 'Ready · played once', '<button class="el-btn">Show me</button><button class="el-btn">Skip →</button>', VARS_RHY('on', 'steady', 'clap'))
                         + '<div class="el-lbl">Your rhythm · 2 of 4 beats</div>'
                         + f'<div class="el-rhy">{rhy(R1, 18, 1, stick=True, cursor=True, label="Your rhythm so far")}</div>'
                         + '<div class="el-lbl">Add the next beat</div><div class="el-tiles named">' + ''.join(tile(c, stick=True, named=True) for c in ['q', 'e2', 'h']) + '</div>' + EDIT(False)
                         + foot('<b>2</b> answered · <b>0</b> shown · <b>0</b> skipped', name='Rhythm dictation') + '</section>' + RHY_TIPS + '</div>', 4, False)
    # ---------------- cadences, rung 3
    CN = [('perfect', 'Perfect'), ('plagal', 'Plagal'), ('imperfect', 'Imperfect'), ('interrupted', 'Interrupted'), ('phrygian', 'Phrygian'),
          ('cad64', 'Cadential <span class="fig"><i>6</i><i>4</i></span>')]
    US = {'perfect': 'US: authentic', 'imperfect': 'US: half', 'interrupted': 'US: deceptive'}

    def cad_opts(ans, mine, near=False):
        h = ''
        for k, n in CN:
            cls = 'is-ans' if k == ans else ('is-near' if near else 'is-mine') if k == mine else 'is-dim'
            bd = badge('ans') if k == ans else badge('near' if near else 'mine') if k == mine else ''
            h += f'<button class="el-opt {cls}" disabled {f"""title="{US[k]}" """ if k in US else ""}>{bd}<span>{n}</span></button>'
        return f'<div class="el-lbl">Your answer</div><div class="el-opts" role="group" aria-label="Cadence">{h}</div>'
    chords = ('<div class="el-chords" aria-label="i, III, iv first inversion, V in D minor">'
              f'<div class="el-ch" style="--fc:var(--green)">i<small>tonic</small></div><div class="el-ch" style="--fc:var(--green);margin-right:6px">III<small>tonic</small></div>'
              '<div class="el-cad" data-l="the cadence"><div class="el-ch" style="--fc:var(--gold)">iv<sup>6</sup><small>bass fa</small></div>'
              '<div class="el-ch" style="--fc:var(--red)">V<small>bass mi</small></div></div><span class="el-key">in D minor</span></div>')

    def cad_res(kind, verdict, mark, teach):
        return (f'<div class="el-result {kind}" role="status"><div class="el-mark">{mark}</div><div><div class="el-verdict">{verdict}</div>'
                '<div class="el-answer" role="heading" aria-level="3">Phrygian cadence</div></div><button class="el-btn gold">Next →</button>'
                f'<div class="el-body"><p class="el-teach">{teach}</p>' + chords +
                '<div class="el-replays"><button class="el-replay">' + play(tag='span') + '<span>Hear the last two chords, slowly</span></button>'
                '<button class="el-btn">Bass only</button><button class="el-btn">The whole phrase</button></div></div></div>')
    ch = lambda t: head('Cadences', 'Stage 5–6', 3, t)
    cask = '<p class="el-ask">The key chord plays first, then a short phrase. How does the phrase end?</p>'
    P['cadence_r3_answered'] = (drills('cad') + '<div class="el-cols"><section class="card">' + ch(tally(11, 15, 0, 6)) + cask
                                + cad_res('bad', 'Not this time', CROSS, 'You heard the subdominant, and it is there: iv is the chord before the end. But the phrase does not come home to i. It stops on V, with the bass stepping down a semitone, fa to mi. That falling semitone is the Phrygian cadence, a kind of imperfect cadence <span class="us">(US: half)</span>.')
                                + cad_opts('phrygian', 'plagal') + foot('<b>15</b> answered · <b>2</b> shown · <b>1</b> skipped') + '</section>' + CAD_TIPS + '</div>', 6, False)
    P['cadence_r3_nearly'] = (drills('cad') + '<div class="el-cols"><section class="card">' + ch(tally(11, 15, 3, 6)) + cask
                              + cad_res('near', 'Nearly', NEAR, 'You heard it stop on V, and that is right: this is an imperfect cadence <span class="us">(US: half)</span>. It is the special kind. In a minor key the bass steps down a semitone, fa to mi (iv<sup>6</sup> to V), and that is called a Phrygian cadence.')
                              + cad_opts('phrygian', 'imperfect', True) + foot('<b>15</b> answered · <b>2</b> shown · <b>1</b> skipped') + '</section>' + CAD_TIPS + '</div>', 6, False)
    # ---------------- the tally, in its three homes, and the Reset states
    kq = lambda title, sub, t: (f'<section class="card"><div class="el-head" style="margin-bottom:0"><div><div class="el-tag">Keys · interval gym</div><h2 class="el-title">{title}</h2>'
                                f'<p class="note" style="margin:8px 0 0">{sub}</p></div>{t}</div></section>')
    P['tally'] = ('<div style="display:grid;gap:18px;max-width:820px">'
                  '<section class="card">' + head('Cadences', 'Stage 5–6', 3, tally(11, 15, 3, 6)) + foot('<b>15</b> answered · <b>2</b> shown · <b>1</b> skipped') + '</section>'
                  '<section class="card">' + head('Cadences', 'Stage 5–6', 1, tally(0, 0, 0, 0)) + foot('No answers yet') + '</section>'
                  '<section class="card">' + head('Cadences', 'Stage 5–6', 3, tally(11, 15, 3, 6)) + foot('<b>15</b> answered · <b>2</b> shown · <b>1</b> skipped', 'confirm') + '</section>'
                  '<section class="card">' + head('Cadences', 'Stage 5–6', 3, tally(0, 0, 0, 0)) + foot('No answers yet', 'undo') + '</section>'
                  + kq('Hear it · name it', 'Uses the intervals for your stage.', tally(9, 12, 4, 5)) + kq('Sing it back', 'Sung in tune, within 30 cents.', tally(5, 8, 2, 3)) + '</div>', 6, False)
    # ---------------- phone: the docked toggle
    dock = ('<div class="el-dock show" role="region" aria-label="Ear Lab playback">' + play('playing', 45) +
            '<div class="el-now playing"><b>Rhythm dictation</b><span>Playing · 0:03 of 0:07</span></div><button class="el-btn gold" disabled>Check</button></div>')
    P['phone_dock'] = (rhy_answering(0, True), 6, True, dock, 660)
    for k, v in P.items():
        body, st, snd = v[0], v[1], v[2]
        html = page(k.replace('_', ' '), body, st, snd, v[3] if len(v) > 3 else '', v[4] if len(v) > 4 else 0)
        (H / f'{k}.html').write_text(html)
    return list(P)


if __name__ == '__main__':
    print(build())
