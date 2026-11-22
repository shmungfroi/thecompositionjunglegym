#!/usr/bin/env python3
"""Builds the three 0.50 mock-ups (static HTML) into /home/claude/fable050/. Mock-ups only: the CSS under test is assets/levels050.css."""
import pathlib, html
H = pathlib.Path(__file__).resolve().parent.parent

LV = [None, ('First steps', 'Stage 4'), ('Foundation', 'Stage 4'), ('Developing', 'Stage 5'), ('Intermediate', 'Stage 5'),
      ('Senior', 'Stage 6'), ('Advanced', 'Stage 6'), ('Extension', 'Stage 6 Extension')]
CAR = '<svg class="car" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4"/></svg>'

ICON = {
 'seed': '<path d="M12 21V11M12 11c0-4 3-7 7-7 0 4-3 7-7 7zM12 14c0-3-2.5-5.5-6-5.5 0 3 2.5 5.5 6 5.5z"/>',
 'keys': '<path d="M4 18c3-6 5-10 8-12 3 2 5 6 8 12M7 12h10"/>',
 'voice': '<path d="M3 17c4-1 5-6 9-6s5 5 9 4M3 10c4 0 5-4 9-4s5 3 9 2"/><circle cx="12" cy="11" r="1.4"/><circle cx="12" cy="6" r="1.4"/>',
 'climbs': '<path d="M5 21l5-8 4 4 5-11M15 6h4v4"/>',
 'forms': '<rect x="3" y="5" width="5" height="14" rx="1"/><rect x="10" y="5" width="4" height="14" rx="1"/><rect x="16" y="5" width="5" height="14" rx="1"/>',
 'analysis': '<circle cx="10" cy="10" r="6"/><path d="M14.5 14.5L20 20M7 10h6M10 7v6"/>',
 'ear': '<path d="M8 18c0 2 1.5 3 3 3s2.5-1.5 3-3c.6-1.8 4-3.5 4-8a6 6 0 0 0-12 0"/><path d="M10 10a2 2 0 1 1 4 0c0 1.5-2 2-2 3.5"/>',
 'gym': '<path d="M4 21V5M20 21V5M4 9h16M4 14h16M4 19h16M12 5v16"/>',
 'oracle': '<rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1"/><circle cx="15" cy="15" r="1"/><circle cx="15" cy="9" r="1"/><circle cx="9" cy="15" r="1"/>',
 'more': '<circle cx="5" cy="12" r="1.6"/><circle cx="12" cy="12" r="1.6"/><circle cx="19" cy="12" r="1.6"/>',
}
NAME = {'seed': 'Chords', 'keys': 'Keys', 'voice': 'Voices', 'climbs': 'Climbs', 'forms': 'Forms', 'analysis': 'Analysis', 'ear': 'Ear Lab', 'gym': 'Gym', 'oracle': 'Oracle'}
def svg(k): return f'<svg viewBox="0 0 24 24">{ICON[k]}</svg>'

def rail(room):
    def b(k): return f'<button{" class=\"on\"" if k == room else ""} data-room="{k}">{svg(k)}<small>{NAME[k]}</small></button>'
    return ('<nav class="rail" aria-label="Rooms">\n <div class="logo disp">❦</div>\n <div class="lv">Library</div>\n ' + b('seed') + b('keys') +
            '\n <div class="lv">Voicing</div>\n ' + b('voice') + '\n <div class="lv">Compose</div>\n ' + ''.join(b(k) for k in ['climbs', 'forms', 'analysis', 'ear', 'gym', 'oracle']) + '\n</nav>')

def hint(l, cur): return f'≈ {cur} {LV[l][1]}' if cur else ''

def lvlist(level, cur, idp=''):
    rows = []
    for l in range(1, 8):
        st = 'now' if l == level else ('ahead' if l > level else '')
        h = f'<small>≈ {LV[l][1]}</small>' if cur else '<small></small>'
        rows.append(f'<button class="lvopt{" upto" if l <= level else ""}" role="radio" aria-checked="{"true" if l == level else "false"}" tabindex="{0 if l == level else -1}" data-l="{l}">'
                    f'<span class="lvm lg {st}" aria-hidden="true">{l}</span><b><span class="sr">Level {l}, </span>{LV[l][0]}</b>{h}</button>')
    head = f'<div class="lvhd"><span class="lbl" id="{idp}lvLbl">Your level</span>{"<small>≈ " + cur + " syllabus</small>" if cur else ""}</div>'
    return (head + f'<div class="lvlist" role="radiogroup" aria-labelledby="{idp}lvLbl">' + ''.join(rows) + '</div>'
            '<p class="lvnote">What is new at your level comes first in every list. Nothing is hidden.</p>'
            f'<div class="lvcur"><label for="{idp}lvCur">Curriculum</label><select id="{idp}lvCur"><option value="nsw"{"" if cur else ""}>NSW (Stages 4–6)</option><option value=""{"" if cur else " selected"}>None</option></select></div>')

def lvbtn(level, cur, expanded=False):
    h = f'<small>{hint(level, cur)}</small>' if cur else ''
    lab = f'Your level: {level}, {LV[level][0]}' + (f', about {cur} {LV[level][1]}' if cur else '') + '. Change level'
    return (f'<button class="lvbtn" id="lvBtn" aria-haspopup="true" aria-expanded="{"true" if expanded else "false"}" aria-controls="lvPop" aria-label="{lab}" title="Your level">'
            f'<span class="lvm lg now" aria-hidden="true">{level}</span><span class="lvbtn-t"><b>{LV[level][0]}</b>{h}</span>{CAR}</button>')

def top(crumb, level=5, cur='NSW', pop=False, stop=False):
    return f'''<header class="top">
 <span class="t disp"><span class="tw">COMPOSITION </span>JUNGLE GYM</span>
 <span class="crumb">{crumb}</span>
 <form class="search" id="searchForm"><input id="q" placeholder="Type a chord: Bm7, E♭9…" autocomplete="off"><button>Find</button></form>
 <div class="lvc" id="lvl">{lvbtn(level, cur, pop)}
  <div class="lvpop" id="lvPop" role="dialog" aria-label="Your level"{"" if pop else " hidden"}>{lvlist(level, cur)}</div>
 </div>
 <button class="tstop" id="tStop"{"" if stop else " hidden"} title="Stop all sound (Esc)">■ Stop</button>
 <button class="jbtn" id="openJ" aria-label="Journal"><span class="ji" aria-hidden="true">✎</span><span class="jt">Journal</span></button>
</header>'''

def tabbar(room):
    tabs = ['seed', 'voice', 'climbs', 'gym']
    b = ''.join(f'<button data-room="{k}"{" class=\"on\"" if k == room else ""}>{svg(k)}<span>{NAME[k]}</span></button>' for k in tabs)
    return f'<nav class="tabbar" aria-label="Rooms">{b}<button id="tbMore" aria-haspopup="dialog"{" class=\"on\"" if room not in tabs else ""}>{svg("more")}<span>More</span></button></nav>'

def msheet(room, level, cur, show=False):
    rooms = ''.join(f'<button data-room="{k}"{" class=\"on\"" if k == room else ""}>{svg(k)}{NAME[k]}</button>' for k in ['keys', 'forms', 'analysis', 'ear', 'oracle'])
    return (f'<div class="msheet" id="msheet"{"" if show else " hidden"}><div class="msb" role="dialog" aria-label="More"><div class="msh"><span class="disp">More rooms</span><button class="mini" id="msClose" aria-label="Close">✕</button></div>'
            f'<div class="msg" id="msRooms">{rooms}</div><div class="mslv" id="msLvl">{lvlist(level, cur, "ms")}</div>'
            '<button class="jbtn" id="msJ" style="margin-top:16px;width:100%"><span class="ji" aria-hidden="true">✎</span>Journal</button></div></div>')

MOCKCSS = '''
/* mock-up scaffolding only (not part of the build) */
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.room{display:block}
.mk{margin:34px 0 12px;padding:8px 12px;border-left:2px solid var(--violet);background:rgba(164,147,216,.08);font-size:12.5px;line-height:1.45;color:#c9bfea;max-width:900px}
.mk b{font-weight:600;color:#e3dcf7}
'''
def page(title, room, crumb, body, level=5, cur='NSW', pop=False, stop=False, sheet=False, extra_css='', js=''):
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="assets/fonts.css"><link rel="stylesheet" href="assets/app.css"><link rel="stylesheet" href="assets/levels050.css">
<style>{MOCKCSS}{extra_css}</style></head>
<body>
{rail(room)}
{tabbar(room)}
{msheet(room, level, cur, sheet)}
{top(crumb, level, cur, pop, stop)}
<main>
{body}
</main>
<script>{js}</script>
</body></html>'''

# ---------------------------------------------------------------- shared content
CHORDS = [  # (suffix, name, level, step) from the app's Q table (050-levels); levels 6–7 are illustrative (Chord Library expansion)
 ('', 'major', 1, 1), ('m', 'minor', 1, 1), ('5', 'power chord', 1, 2),
 ('sus2', 'sus 2nd', 2, 3), ('sus4', 'sus 4th', 2, 3), ('7', 'dominant 7th', 2, 4),
 ('dim', 'diminished', 3, 5), ('aug', 'augmented', 3, 5), ('maj7', 'major 7th', 3, 6), ('m7', 'minor 7th', 3, 6),
 ('6', 'major 6th', 4, 7), ('m6', 'minor 6th', 4, 7), ('add9', 'added 9th', 4, 8), ('madd9', 'minor add 9', 4, 8), ('7sus4', '7th sus 4th', 4, 9), ('m7♭5', 'half-dim 7th', 4, 10),
 ('dim7', 'dim 7th', 5, 11), ('9', 'dominant 9th', 5, 12), ('maj9', 'major 9th', 5, 12), ('m9', 'minor 9th', 5, 12),
 ('13', 'dominant 13th', 6, 13), ('7♭9', '7th, flat 9', 6, 14), ('7♯9', '7th, sharp 9', 6, 14), ('7♯11', '7th, sharp 11', 6, 15),
 ('maj7♯11', 'major 7th, sharp 11', 7, 16), ('7alt', 'altered dominant', 7, 17),
]
def lvlst_chords(level, sel='m7', root='B', ahead_open=False, idp=''):
    new = [c for c in CHORDS if c[2] == level]; met = [c for c in CHORDS if c[2] < level]; ah = [c for c in CHORDS if c[2] > level]
    def row(c): return f'<button class="lvrow{" on" if c[0] == sel else ""}" role="option" aria-selected="{"true" if c[0] == sel else "false"}" data-pq="{c[0]}"><b>{root}{c[0]}</b><span>{c[1]}</span></button>'
    def grp(cs, cls):
        out = []
        for l in sorted({c[2] for c in cs}):
            out.append(f'<div class="lvgrp" role="group" aria-label="Level {l}, {LV[l][0]}"><span class="lvm {cls}" title="Level {l} · {LV[l][0]}" aria-hidden="true">{l}</span>' + ''.join(row(c) for c in cs if c[2] == l) + '</div>')
        return ''.join(out)
    h = f'<div class="lvlst" id="{idp}qualList" role="listbox" aria-label="Chord type">'
    h += (f'<section class="lvband new" aria-label="New at Level {level}, {LV[level][0]}"><h3 class="lvbh"><span class="lvm now" aria-hidden="true">{level}</span>New at Level {level}<span class="n">{len(new)}</span></h3>'
          + (''.join(row(c) for c in new) if new else f'<p class="lvnone">No new chord types at Level {level}. Everything you have met is below.</p>') + '</section>')
    if met:
        lo, hi = met[0][2], met[-1][2]
        h += f'<details class="lvband met" open><summary class="lvbh">{CAR}Earlier levels · {lo if lo == hi else f"{lo} to {hi}"}<span class="n">{len(met)}</span></summary>{grp(met, "")}</details>'
    if ah:
        lo, hi = ah[0][2], ah[-1][2]
        h += f'<details class="lvband ahead"{" open" if ahead_open else ""}><summary class="lvbh">{CAR}Ahead of you · {lo if lo == hi else f"{lo} to {hi}"}<span class="n">{len(ah)}</span></summary>{grp(ah, "ahead")}</details>'
    return h + '</div>'

FORMS = [  # (key, title, family, level, blurb, live). Levels here are illustrative: the real tags come from CJG_Retag_06_Forms.
 ('phrase', 'Phrase, period and sentence', 'Foundations', 2, 'The building blocks under every form: the phrase, the question-and-answer period, and the sentence (idea, repeat, drive to the cadence).', 1),
 ('blues12', '12-bar blues', 'Blues and jazz', 2, 'Three four-bar lines: say it, say it again over IV, then answer it. The form under blues, rock and roll, and much of jazz.', 1),
 ('rondo', 'Rondo', 'Classical', 3, 'A refrain that keeps coming home between contrasting episodes: ABACA or ABACABA.', 1),
 ('tv', 'Theme and variations', 'Classical', 3, 'One theme, transformed again and again: decorated, re-harmonised, changed in mode, metre or texture.', 1),
 ('jazzblues', 'Jazz blues', 'Blues and jazz', 4, 'The same twelve bars with jazz moves inside: a ii–V into IV, a passing diminished chord, and a ii–V turnaround.', 1),
 ('minblues', 'Minor blues', 'Blues and jazz', 4, 'Twelve bars in a minor key. The ♭VI7 that slides down to V7 in bars 9–10 is its signature.', 1),
 ('rag', 'Rag', 'Rag', 4, 'A march form with several strains, usually AABBACCDD, with a trio in the subdominant.', 1),
 ('rhythm', 'Rhythm changes', 'Blues and jazz', 5, '32 bars, AABA, built on the chords of Gershwin\'s "I Got Rhythm": the second great jazz form after the blues.', 1),
 ('sonata', 'Sonata form', 'Classical', 5, 'Exposition, development, recapitulation: two key areas in conflict, then resolved.', 1),
 ('sonrondo', 'Sonata-rondo', 'Classical', 6, 'ABACABA, where C works like a development and the second B returns in the home key.', 1),
 ('fugue', 'Fugue', 'Counterpoint', 6, 'Built in climb 13: canon and invention, then the modal or tonal fugue.', 0),
]
def forms_gallery(level, ahead_open=False):
    new = [f for f in FORMS if f[3] == level]; met = [f for f in FORMS if f[3] < level]; ah = [f for f in FORMS if f[3] > level]
    def full(f): return (f'<div class="climb {"" if f[5] else "dim"}"><h4 style="padding-right:0">{f[1]}</h4><div class="st">{f[2]}</div><p>{f[4]}</p><div class="stat {"live" if f[5] else ""}">{"Open" if f[5] else "Coming in climb 13"}</div>'
                         + (f'<div class="go" style="margin-top:10px"><button class="mini gold" data-fopen="{f[0]}">Open this form →</button></div>' if f[5] else '') + '</div>')
    def cmp(f, cls):
        mark = f'<span class="lvm {cls}" title="Level {f[3]} · {LV[f[3]][0]}" aria-hidden="true">{f[3]}</span>'
        tx = f'<span class="tx"><b>{f[1]}</b><small>{f[2]}{"" if f[5] else " · coming in climb 13"}</small></span>'
        if f[5]: return f'<button class="climb cmp" data-fopen="{f[0]}" aria-label="{html.escape(f[1])}, Level {f[3]}, open">{mark}{tx}<span class="arr" aria-hidden="true">→</span></button>'
        return f'<div class="climb cmp dim" aria-label="{html.escape(f[1])}, Level {f[3]}">{mark}{tx}</div>'
    def n(x): return f'{len(x)} form{"" if len(x) == 1 else "s"}'
    h = '<div class="lvlst cards" id="formsList">'
    h += (f'<section class="lvband new"><h3 class="lvch"><span class="disp">New at your level</span><small>Level {level} · {LV[level][0]} · {n(new)}</small></h3>'
          + (f'<div class="climbs">{"".join(full(f) for f in new)}</div>' if new else f'<p class="lvnone">No new forms at Level {level}. Everything you have met is below.</p>') + '</section>')
    if met:
        lo, hi = met[0][3], met[-1][3]
        h += f'<details class="lvband met" open><summary class="lvch"><span class="disp">Earlier levels</span><small>Levels {lo} to {hi} · {n(met)} · in order</small>{CAR}</summary><div class="climbs cmp">{"".join(cmp(f, "") for f in met)}</div></details>'
    if ah:
        lo, hi = ah[0][3], ah[-1][3]
        h += f'<details class="lvband ahead"{" open" if ahead_open else ""}><summary class="lvch"><span class="disp">Ahead of you</span><small>Level{"" if lo == hi else "s"} {lo if lo == hi else f"{lo} to {hi}"} · {n(ah)}</small>{CAR}</summary><div class="climbs cmp">{"".join(cmp(f, "ahead") for f in ah)}</div></details>'
    return h + '</div>'

SYL_FORMS = '<div class="sylbar"><details class="syl"><summary><span class="sylk">Syllabus</span><span>Structure</span><span class="sylsep">|</span><span>Compositional</span><span class="sylmore">2 outcomes</span></summary></details></div>'
def forms_head(): return ('<div class="head"><div><div class="kicker">Compose · the shapes music is built in</div><h1 class="disp">Forms</h1>'
                          '<p class="sub">How a piece is laid out in time: sections, repeats, keys and arrivals. Each form follows the same path as the climbs: ask, hear, understand, see, try, make.</p></div></div>')

# ---------------------------------------------------------------- 1. level control
LC_JS = '''
/* mock only: ?lv=1..7 &cur=none &open=0 &stop=1 &sheet=1 are read by build.py variants; this script just makes the control work */
const btn=document.getElementById('lvBtn'),pop=document.getElementById('lvPop');
btn.addEventListener('click',()=>{if(matchMedia('(max-width:760px)').matches){document.getElementById('msheet').hidden=false;return}const o=btn.getAttribute('aria-expanded')!=='true';btn.setAttribute('aria-expanded',o);pop.hidden=!o;if(o)pop.querySelector('[aria-checked=true]').focus()});
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!pop.hidden){pop.hidden=true;btn.setAttribute('aria-expanded','false');btn.focus()}});
document.getElementById('msClose').addEventListener('click',()=>document.getElementById('msheet').hidden=true);
document.getElementById('tbMore').addEventListener('click',()=>document.getElementById('msheet').hidden=false);
'''
def build_level_control():
    body = '<section class="room" id="room-forms">' + SYL_FORMS + forms_head() + forms_gallery(5) + '</section>'
    variants = {
        'mock_level_control': dict(pop=True, stop=False, sheet=True),          # primary: popover open (desktop), More sheet open (phone)
        'mock_level_control_closed': dict(pop=False, stop=True, sheet=False),   # closed, Stop showing: the tightest top bar
        'mock_level_control_L4_nocur': dict(pop=True, stop=True, sheet=True, level=4, cur=''),   # longest name, curriculum None
    }
    for name, kw in variants.items():
        lvl = kw.pop('level', 5); cur = kw.pop('cur', 'NSW')
        b = '<section class="room" id="room-forms">' + SYL_FORMS + forms_head() + forms_gallery(lvl) + '</section>'
        (H / f'{name}.html').write_text(page('Mock · level control', 'forms', 'Compose · <b>Forms</b>', b, level=lvl, cur=cur, js=LC_JS, **kw), encoding='utf-8')

# ---------------------------------------------------------------- 2. ordering
ORD_CSS = '''
/* mock scaffolding for the Chord Library side panel (layout B). Only .lvlst and its children are specified in DESIGN_050. */
.sidegrid{display:grid;grid-template-columns:312px minmax(0,1fr);gap:18px;align-items:start}
.pkside{position:sticky;top:calc(var(--top) + 14px);display:flex;flex-direction:column;max-height:calc(100vh - var(--top) - 28px);margin:0;padding:16px 14px 14px 16px}
.pkside .plbl{display:block;flex:none;padding:0;margin:0 0 8px}
.pkside .roots{gap:6px 7px;margin-bottom:16px}
.pkside .rp,.pkside .rk{width:39px;height:42px}.pkside .rp{font-size:17px;border-radius:10px}.pkside .rk button{font-size:12.5px;border-radius:7px}
.pkside .qscroll{flex:1 1 auto;min-height:0;overflow-y:auto;margin:0 -8px 0 0;padding:0 8px 2px 0;scrollbar-width:thin;scrollbar-color:var(--line) transparent}
.pkside .invs{display:flex;flex-wrap:wrap;gap:6px;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
.pkside .ip{padding:5px 12px;font-size:12.5px}
.seedmock .big{font-size:86px;line-height:1;color:var(--goldhi);font-weight:400;margin:6px 0 8px}
.seedmock .nm{color:var(--muted);font-size:17px;margin:0 0 14px}
.phoneonly{display:none}
@media (max-width:760px){
 .sidegrid{grid-template-columns:1fr}.pkside{display:none}.phoneonly{display:block}
 .qsel{display:flex;align-items:center;gap:10px;width:100%;min-height:48px;padding:6px 14px;border:1px solid var(--gold);border-radius:12px;background:rgba(201,162,74,.14);text-align:left}
 .qsel b{font-size:16px;font-weight:600;color:var(--goldhi)}.qsel small{color:var(--muted);font-size:12.5px}.qsel .lvm{margin-left:auto}.qsel .car{flex:none;width:10px;height:6px;fill:none;stroke:var(--muted);stroke-width:1.5}
 .sheetmock{position:relative;margin:14px -14px 0;background:#14110b;border-top:1px solid var(--gold);border-radius:18px 18px 0 0;padding:16px 16px 20px}
}
'''
def roots(sel='B'):
    nat = ['C', 'D', 'E', 'F', 'G', 'A', 'B']; acc = [('C♯', 'D♭'), ('D♯', 'E♭'), ('F♯', 'G♭'), ('G♯', 'A♭'), ('A♯', 'B♭')]
    order = ['C', 0, 'D', 1, 'E', 'F', 2, 'G', 3, 'A', 4, 'B']
    return ''.join(f'<button class="rp{" on" if x == sel else ""}">{x}</button>' if isinstance(x, str) else f'<div class="rk"><button>{acc[x][0]}</button><button>{acc[x][1]}</button></div>' for x in order)
def build_ordering():
    for name, lvl, ahead in [('mock_ordering', 5, False), ('mock_ordering_L2_open', 2, True)]:
        sel = '9' if lvl == 5 else '7'
        selc = next(c for c in CHORDS if c[0] == sel)
        side = (f'<aside class="card pkside" aria-label="Pick a chord"><span class="plbl">Root</span><div class="roots">{roots()}</div><span class="plbl">Chord type</span>'
                f'<div class="qscroll">{lvlst_chords(lvl, sel, ahead_open=ahead)}</div>'
                '<div class="invs"><button class="ip on">Root position</button><button class="ip">1st inversion</button><button class="ip">2nd</button><button class="ip">3rd</button></div></aside>')
        seed = (f'<div class="card seedmock"><div class="lbl" style="color:var(--gold);letter-spacing:3px;font-weight:600">The seed</div><div class="big">B{sel}</div><p class="nm">B {"dominant ninth" if sel == "9" else "dominant seventh"}</p>'
                '<p class="sub">(The rest of the Chord Library page sits here, unchanged: the seed, the instrument, the keys it belongs to.)</p></div>')
        phone = (f'<div class="phoneonly"><span class="plbl" style="display:block;margin-bottom:8px">Chord type</span><button class="qsel" aria-haspopup="dialog"><b>B{sel}</b><small>{selc[1]}</small><span class="lvm {"now" if selc[2] == lvl else ""}" aria-hidden="true">{selc[2]}</span>{CAR}</button>'
                 f'<div class="mk"><b>Phone.</b> Tapping the button opens the chord-type sheet (same component as the More sheet). Shown open, in flow, below.</div>'
                 f'<div class="sheetmock" role="dialog" aria-label="Chord type"><div class="msh"><span class="disp">Chord type</span><button class="mini" aria-label="Close">✕</button></div>{lvlst_chords(lvl, sel, ahead_open=ahead, idp="ph")}</div></div>')
        body = ('<section class="room" id="room-seed"><div class="head"><div><div class="kicker">Library · every chord, how it\'s built, how it sounds, where it lives</div><h1 class="disp">Chord Library</h1>'
                '<p class="sub">Pick a seed. See it on your instrument, hear it, read it, then find the keys it belongs to and the jobs it does there.</p></div></div>'
                f'<div class="sidegrid">{side}<div>{seed}{phone}</div></div></section>'
                f'<div class="mk"><b>The same rule on a card gallery (Forms).</b> New at your level: full cards. Everything else: compact cards in level order, each with its level mark. Above your level: folded, one tap to open.</div>'
                '<section class="room" id="room-forms" style="margin-top:8px">' + forms_head() + forms_gallery(lvl, ahead) + '</section>')
        (H / f'{name}.html').write_text(page('Mock · ordering rule', 'seed', f'Library · <b>B{sel}</b>', body, level=lvl, extra_css=ORD_CSS, js=LC_JS), encoding='utf-8')

# ---------------------------------------------------------------- 3. rungs
def rung_picker(built, level, cur_rung, done=(), sug=None, open_level=None, curric='NSW'):
    open_level = open_level or (cur_rung - 1) // 3 + 1
    h = '<div class="el-rp7" role="group" aria-label="Rung">'
    for l in range(1, 8):
        rs = [3 * (l - 1) + s for s in (1, 2, 3)]; has = [r for r in rs if r in built]
        cls = ['el-lg'] + (['you'] if l == level else []) + (['none'] if not has else []) + (['open'] if l == open_level else [])
        tcls = ['el-ltab'] + (['you'] if l == level else []) + (['none'] if not has else []) + (['has'] if cur_rung in rs else []) + (['sug'] if sug in rs else [])
        tl = f'Level {l}, {LV[l][0]}' + (', your level' if l == level else '') + (f', rungs {rs[0]} to {rs[2]}' if has else ', not yet written') + (', suggested next' if sug in rs else '')
        h += f'<div class="{" ".join(cls)}" role="group" aria-label="Level {l}, {LV[l][0]}">'
        h += f'<button class="{" ".join(tcls)}" data-band="{l}" aria-expanded="{"true" if l == open_level else "false"}" aria-label="{tl}"><b>{l}</b></button>'
        h += f'<span class="el-lgcap" data-notm>{"<span class=\"lvm now\" aria-hidden=\"true\">" + str(l) + "</span>" if l == level else "<i>" + str(l) + "</i>"} {LV[l][0]}</span><div class="el-lgr">'
        i = 0
        while i < 3:
            r = rs[i]
            if r in built:
                c = ' '.join(x for x in ['on' if r == cur_rung else '', 'done' if r in done else '', 'sug' if r == sug else ''] if x)
                al = f'Rung {r}, Level {l}' + (', 8 of the last 10 reached' if r in done else '') + (', suggested next' if r == sug else '')
                h += f'<button data-earlv="{r}" aria-pressed="{"true" if r == cur_rung else "false"}" aria-label="{al}" class="{c}">{r}</button>'; i += 1
            else:
                j = i
                while j < 3 and rs[j] not in built: j += 1
                n = j - i; al = f'Rung {rs[i]}, not yet written' if n == 1 else f'Rungs {rs[i]} to {rs[j-1]}, not yet written'
                h += f'<span class="el-ny" style="--n:{n}" role="img" aria-label="{al}">not yet</span>'; i = j
        h += '</div>'
        you = ' · <em>your level</em>' if l == level else ''
        h += f'<p class="el-lcap" data-notm><b>Level {l} · {LV[l][0]}</b>{you}</p></div>'
    return h + '</div>'

def ear_card(title, tag, built, level, cur_rung, done, sug, what, last, score, open_level=None, ask='', cid='earCard'):
    l = (cur_rung - 1) // 3 + 1
    dots = ''.join(f'<span class="{"r" if x == 1 else "e" if x is None else ""}"></span>' for x in last + [None] * (10 - len(last)))
    rl = (f'<p class="el-rungline" data-notm><span><b>Rung {cur_rung} of 21</b> · Level {l}, {LV[l][0]} <span style="white-space:nowrap">(≈ NSW {LV[l][1]})</span> · {what}</span>'
          f'<span class="el-last10" role="img" aria-label="Last {len(last)} answers on this rung: {sum(last)} right">Last 10 <i>{dots}</i></span></p>')
    tally = (f'<div class="el-tally" role="status"><div class="el-score"><b>{score[0]}</b><span>of {score[1]}</span></div></div>' if score else
             '<div class="el-tally is-new" role="status"><div class="el-score"><b>–</b><span>no answers yet</span></div></div>')
    return (f'<section class="card" id="{cid}"><div class="el-head long"><div><div class="el-tag">{tag}</div><h2 class="el-title">{title}</h2></div>{tally}'
            f'<div class="el-rungrow">{rung_picker(built, level, cur_rung, done, sug, open_level)}{rl}</div></div>'
            f'<p class="el-ask">{ask}</p>'
            '<div class="el-stage"><button class="el-play" aria-label="Play" aria-pressed="false"><svg class="ring" viewBox="0 0 48 48" aria-hidden="true"><circle class="trk" cx="24" cy="24" r="22.5"></circle><circle class="arc" cx="24" cy="24" r="22.5" pathLength="100"></circle></svg><svg class="ico play" viewBox="0 0 16 16" aria-hidden="true"><path d="M4 2.2v11.6L14 8z" fill="currentColor"></path></svg></button><div class="el-now ready"><b>Play</b><span>Press play to hear the next one</span></div><div class="el-acts"></div></div></section>')

RUNG_JS = LC_JS + '''
document.addEventListener('click',e=>{const t=e.target.closest('.el-ltab');if(!t)return;const rp=t.closest('.el-rp7');rp.querySelectorAll('.el-lg').forEach(g=>{const o=g===t.parentElement;g.classList.toggle('open',o);g.querySelector('.el-ltab').setAttribute('aria-expanded',o)})});
'''
def build_rungs():
    drills = [('Pulse and metre', '6 rungs'), ('Rhythm dictation', '10 rungs'), ('Chord quality', '6 rungs'), ('Cadences', '4 rungs'), ('Bass and numerals', '3 rungs'), ('Melodic dictation', '12 rungs'), ('Blind analysis', '3 rungs'), ('Intervals', '6 rungs'), ('Sing it back', '6 rungs')]
    tabs = '<div class="el-drills" role="tablist" aria-label="Ear Lab drills">' + ''.join(f'<button class="el-drill{" on" if n == "Melodic dictation" else ""}" role="tab" aria-selected="{"true" if n == "Melodic dictation" else "false"}"><b>{n}</b><small>{s}</small></button>' for n, s in drills) + '</div>'
    mel_built = {1, 2, 3, 4, 5, 7, 8, 10, 11, 13, 14, 16}
    tips = ('<section class="card" id="earTips"><h3>Listening for it</h3><ol class="el-tips"><li><b>Sing it back in solfa before you answer.</b> The key chord plays first and the first note is always given.</li>'
            '<li><b>Movable do.</b> Do is home in a major key; in a minor key the home is la, and si is the raised 7th that leads up to la.</li></ol></section>')
    def body(variant):
        if variant == 'a':
            mel = ear_card('Melodic dictation', 'Rungs 1 to 16 · 12 written', mel_built, 4, 10, {1, 2, 3, 4, 5, 7, 8}, 11, 'eight bars of 2/4, 3/4, 4/4 or 6/8 · adds leaps of a 6th', [1, 1, 0, 1, 1, 1, 1], (6, 7), ask='The key chord plays first and the first note is given. Write the rest in solfa.')
            cad = ear_card('Cadences', 'Rungs 10 to 16 · 4 written', {10, 11, 13, 16}, 4, 10, set(), None, 'perfect or plagal, in root position', [], None, ask='The key chord plays first, then a short phrase. How does the phrase end?', cid='earCard2')
            cad3 = ear_card('Cadences', 'Rungs 10 to 16 · 4 written', {10, 11, 13, 16}, 2, 10, set(), None, 'perfect or plagal, in root position', [], None, open_level=2, ask='The key chord plays first, then a short phrase. How does the phrase end?', cid='earCard3')
            return ('<section class="room" id="room-ear"><div class="head"><div><div class="kicker">Compose · hear it before you write it</div><h1 class="disp">Ear Lab</h1>'
                    '<p class="sub">Nine drills, from the beat to cadences in real scores. Every question is generated and marked by the same engines that run the rest of the Gym, so the answers always match what you hear.</p></div></div>'
                    f'<div id="earMain" class="el">{tabs}<div class="el-cols">{mel}{tips}</div>'
                    '<div class="mk"><b>A drill with few rungs written.</b> Cadences has four rungs so far (10, 11, 13, 16). Whole levels with nothing written read “not yet” once; the ladder keeps its shape. Learner at Level 4.</div>'
                    f'<div class="el-cols">{cad}<div></div></div>'
                    '<div class="mk"><b>Phone and tablet only: a level with nothing written, opened.</b> Same drill, learner at Level 2, Level 2 tab open. (On a laptop this card looks like the one above.)</div>'
                    f'<div class="el-cols">{cad3}<div></div></div></div></section>')
    (H / 'mock_rungs.html').write_text(page('Mock · 21-rung picker', 'ear', 'Compose · <b>Ear Lab</b>', body('a'), level=4, js=RUNG_JS), encoding='utf-8')

build_level_control(); build_ordering(); build_rungs()
print('built')
