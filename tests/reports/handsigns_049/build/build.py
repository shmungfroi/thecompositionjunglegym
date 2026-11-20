#!/usr/bin/env python3
"""Builds the 0.49 hand-sign deliverables (round 2) from the drawings ink.py leaves in build/drawn/:
svg/ (the full drawings), svg/small/ (the simplified small-size drawings from the same posed hand), sheet.html,
ladder_mock.html, ladder_full.html. Order: python3 ink.py (about 6 minutes), python3 build.py, python3 shots.py."""
import pathlib, json
H = pathlib.Path(__file__).resolve().parent; R = H.parent
F = '../../../design/earlab_048/fonts'
FONTS = ''.join(f"@font-face{{font-family:'Outfit';font-weight:{w};src:url({F}/outfit-latin-{w}-normal.woff2) format('woff2')}}" for w in (300, 400, 600)) + \
        f"@font-face{{font-family:'Poiret One';src:url({F}/poiret-one-latin-400-normal.woff2) format('woff2')}}"
TOK = ":root{--ink:#0b0906;--panel:#12100b;--panel2:#17140e;--line:#2a2418;--gold:#c9a24a;--goldhi:#f0d48a;--ivory:#ece2c8;--muted:#9c927c;--red:#c8473b;--green:#8fbf6a;--violet:#a493d8;--paper:#f6f0e2;--pink:#1d1a14}"
ORDER = ['do', 'di', 'ra', 're', 'ri', 'me', 'mi', 'fa', 'fi', 'se', 'so', 'si', 'le', 'la', 'li', 'te', 'ti']
NAMES = {'di': 'di (raised do)', 'ri': 'ri (raised re)', 'fi': 'fi (raised fa)', 'si': 'si (raised so)', 'li': 'li (raised la)', 'te': 'te (lowered ti)',
         'le': 'le (lowered la)', 'se': 'se (lowered so)', 'me': 'me (lowered mi)', 'ra': 'ra (lowered re)'}
_D = {}
def drawn(n):
    if n not in _D: _D[n] = json.loads((H / 'drawn' / f'{n}.json').read_text())
    return _D[n]
def svg(n, small=False):
    d = drawn(n); s = '_s' if small else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 64" role="img" aria-label="{NAMES.get(n, n)} hand sign">'
            f'<path d="{d["tone" + s]}" fill="currentColor" fill-opacity="{".2" if small else ".17"}"/><path d="{d["ink" + s]}" fill="currentColor"/></svg>')
def sign(n, weight='ladder', cls=''):
    """weight 'ladder' = the simplified small-size drawing; anything else = the full drawing"""
    return svg(n.replace("'", ''), small=(weight == 'ladder')).replace('<svg ', f'<svg class="hsg {cls}" ', 1)

GEST = {
 "do'": 'the do fist again, at the forehead', 'ti': 'first finger points up and forward; the other fingers curled', 'la': 'hand hangs loose from the wrist, palm down, fingers drooping',
 'so': 'open hand on its edge, palm towards you, thumb on top', 'fa': 'loose fist, thumb pointing down towards mi', 'mi': 'flat hand, level, palm down',
 're': 'flat hand slanting upward, palm down', 'do': 'closed fist, palm down, knuckles forward',
 'di': 'the do fist tipped up', 'ri': 'the re slant, steeper', 'fi': 'the fa hand turned over: thumb up', 'si': 'the so hand lifted, fingers opening',
 'li': 'the la hand turned up: palm cupped upward', 'te': 'the ti finger pointing down', 'le': 'the la hand dropped: fingers hang straight down',
 'se': 'the so hand tipped down, palm open', 'me': 'the mi hand sloping down', 'ra': 'the re hand with the thumb let fall'}
HEIGHT = {'do': 'waist', 're': 'stomach', 'mi': 'lower chest', 'fa': 'upper chest', 'so': 'shoulder', 'la': 'chin', 'ti': 'eye level', "do'": 'forehead'}
DEG = {'do': 'goldhi', "do'": 'goldhi', 're': 'green', 'mi': 'green', 'fa': 'green', 'so': 'ivory', 'la': 'red', 'ti': 'red'}
DIA = ["do'", 'ti', 'la', 'so', 'fa', 'mi', 're', 'do']; UP = ['li', 'si', 'fi', 'ri', 'di']; DOWN = ['te', 'le', 'se', 'me', 'ra']
CHROMA = ["do'", 'ti', 'te', 'la', 'le', 'so', 'se', 'fa', 'mi', 'me', 're', 'ra', 'do']       # descending, flats
CHROMA_UP = ["do'", 'ti', 'li', 'la', 'si', 'so', 'fi', 'fa', 'mi', 'ri', 're', 'di', 'do']    # sharps
col = lambda n: f"var(--{DEG.get(n, 'violet')})"

def write_svgs():
    (R / 'svg' / 'small').mkdir(parents=True, exist_ok=True)
    for n in ORDER:
        (R / 'svg' / f'{n}.svg').write_text(svg(n) + '\n'); (R / 'svg' / 'small' / f'{n}.svg').write_text(svg(n, True) + '\n')

def sheet():
    big = lambda L: ''.join(f'<figure class="big"><div style="color:{col(n)}">{sign(n, "full")}</div><figcaption><b>{n}</b><span>{GEST[n]}</span></figcaption></figure>' for n in L)
    def sizes(theme):
        rows = ''
        for n in DIA[::-1] + UP[::-1] + DOWN[::-1]:
            c = col(n) if theme == 'dark' else '#1d1a14'
            rows += (f'<tr><th>{n}</th><td style="color:{c}">{sign(n, "ladder", "s1")}</td><td style="color:{c}">{sign(n, "ladder", "s2")}</td>'
                     f'<td style="color:{c}">{sign(n, "full", "s3")}</td><td class="one">{sign(n, "ladder", "s1")}</td></tr>')
        ink = 'gold' if theme == 'dark' else 'ink, one colour'
        return (f'<div class="szs {theme}"><table><thead><tr><th></th><th>42 × 34<br><small>phone ladder · small drawing</small></th><th>50 × 40<br><small>desktop ladder · small drawing</small></th>'
                f'<th>120 × 96<br><small>card · full drawing</small></th><th>42 × 34<br><small>{ink}</small></th></tr></thead>{rows}</table></div>')
    pairs = [('re', 'ti'), ('fa', 'ti'), ('re', 'ri'), ('mi', 'me'), ('re', 'ra'), ('so', 'si'), ('so', 'se'), ('la', 'le'), ('la', 'li'), ('fa', 'fi'), ('ti', 'te'), ('do', 'di')]
    pr = lambda th: ''.join(f'<span class="pair">{sign(a, "ladder", "s1")}{sign(b, "ladder", "s1")}<small>{a} · {b}</small></span>' for a, b in pairs)
    html = f'''<!doctype html><html lang="en-AU"><meta charset="utf-8"><title>Hand signs · design sheet 0.49</title><style>{FONTS}{TOK}
*{{box-sizing:border-box}}body{{margin:0;background:var(--ink);color:var(--ivory);font:300 15px/1.45 Outfit,system-ui,sans-serif;padding:34px 40px 60px;max-width:1366px}}
h1{{font:400 34px "Poiret One",Outfit,sans-serif;letter-spacing:3px;color:var(--goldhi);margin:0 0 4px;text-transform:uppercase}}
h2{{font:600 12px Outfit;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin:38px 0 12px}}
p{{margin:0 0 8px;max-width:820px}}.note{{color:var(--muted);font-size:13px}}
.hsg{{display:block}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}}.grid.c5{{grid-template-columns:repeat(5,1fr)}}
.big{{margin:0;background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:14px;padding:14px 14px 12px}}
.big svg{{width:100%;height:auto}}.big b{{font:400 22px "Poiret One";letter-spacing:1px;color:var(--goldhi);margin-right:10px}}.big span{{color:var(--muted);font-size:13px}}
.big figcaption{{border-top:1px solid var(--line);padding-top:8px;margin-top:6px;min-height:52px}}
.two{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}.szs{{border:1px solid var(--line);border-radius:14px;padding:10px 18px 14px;background:var(--panel)}}
.szs.light{{background:var(--paper);color:#1d1a14;border-color:#d9cfb6}}.szs table{{border-collapse:collapse;width:100%}}
.szs th{{font:400 12px Outfit;letter-spacing:.5px;text-align:left;padding:4px 8px;color:inherit}}.szs thead th{{color:var(--muted);border-bottom:1px solid var(--line);vertical-align:bottom}}
.szs.light thead th{{color:#6d6452;border-color:#d9cfb6}}.szs tbody th{{font:italic 400 16px Outfit;width:44px}}.szs td{{padding:3px 8px;vertical-align:middle}}
.s1{{width:42.5px;height:34px}}.s2{{width:50px;height:40px}}.s3{{width:120px;height:96px}}.szs.dark .one{{color:var(--gold)}}.szs.light .one{{color:#1d1a14}}
.pairs{{display:flex;flex-wrap:wrap;gap:10px}}.pair{{display:inline-flex;align-items:center;gap:6px;padding:6px 12px;border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--gold)}}
.pair small{{color:var(--muted);font-size:12px;margin-left:4px}}.pairs.light .pair{{background:var(--paper);border-color:#d9cfb6;color:#1d1a14}}.pairs.light small{{color:#6d6452}}
</style>
<h1>Hand signs</h1><p class="note">Composition Jungle Gym · design sheet for approval · 0.49 · round 2 · drawn from a posed anatomical hand · one right hand, the signer's own view, wrist from the right. Colour is the degree colour; every drawing is a single colour. The two ladder sizes use the simplified small-size drawing made from the same hand.</p>
<h2>The scale · do to do′</h2><div class="grid">{big(DIA[::-1])}</div>
<h2>Raised · the parent sign turned up</h2><div class="grid c5">{big(UP[::-1])}</div>
<h2>Lowered · the parent sign turned down</h2><div class="grid c5">{big(DOWN[::-1])}</div>
<h2>Signs that must not be confused · at the phone ladder size (42 × 34)</h2><div class="pairs">{pr('dark')}</div><div class="pairs light" style="margin-top:10px">{pr('light')}</div>
<h2>Three sizes · dark and light</h2><div class="two">{sizes('dark')}{sizes('light')}</div>
</html>'''
    (R / 'sheet.html').write_text(html)

def ladder_mock():
    def lad(L, home='do', letters=None):
        h = ''
        for n in L:
            b = n[0] if n in DIA else n
            h += f'<button class="earstep{" home" if n == home else ""}"><span class="hsw">{sign(n)}</span><b>{b + ("′" if n.endswith(chr(39)) else "")}</b>{"<span class=hm>home</span>" if n == home else ""}</button>'
        return f'<div class="earlad">{h}</div>'
    keys = ''.join(f'<div class="rung" style="--c:{col(n)}"><span class="sy">{n.replace(chr(39), "")}</span><span class="nb">{d}</span><span class="nm">{nm}</span><span class="hsk">{sign(n)}</span><span class="hs">{GEST[n]}</span></div>'
                   for n, d, nm in zip(DIA, '1 7 6 5 4 3 2 1'.split(), 'C B A G F E D C'.split()))
    html = f'''<!doctype html><html lang="en-AU"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Hand-sign ladder · mock-up 0.49</title><style>{FONTS}{TOK}
*{{box-sizing:border-box}}body{{margin:0;background:var(--ink);color:var(--ivory);font:300 15px/1.4 Outfit,system-ui,sans-serif;padding:22px}}
h2{{font:600 12px Outfit;letter-spacing:3px;text-transform:uppercase;color:var(--gold);margin:0 0 12px}}.note{{color:var(--muted);font-size:13px;margin:8px 0 0}}
.card{{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin-bottom:18px}}
.wrap{{display:grid;grid-template-columns:repeat(3,292px) minmax(0,1fr);gap:22px;align-items:start}}
.earlad{{display:grid;grid-auto-rows:52px}}
.earstep{{display:flex;align-items:center;gap:12px;margin:1.5px 0;padding:0 12px 0 8px;border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--ivory);font:300 16px Outfit;text-align:left}}
.earstep b{{font-weight:400;min-width:30px}}.earstep .hm{{margin-left:auto;font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted)}}.earstep.home{{box-shadow:inset 3px 0 0 var(--gold)}}
.hsw{{display:inline-flex;width:56px;height:44px;align-items:center;justify-content:center;color:var(--gold);flex:none}}.hsw svg{{width:55px;height:44px}}
.ladder{{display:flex;flex-direction:column;gap:3px}}.rung{{display:grid;grid-template-columns:52px 24px 30px 50px 1fr;gap:8px;align-items:center;padding:2px 10px;border-left:3px solid var(--c);background:#0e0c08;border-radius:0 8px 8px 0;font-size:14px}}
.rung .sy{{font-style:italic;color:var(--c);font-size:16px}}.rung .nb{{color:var(--muted)}}.rung .hs{{color:var(--muted);font-size:12.5px}}.hsk{{color:var(--c);display:flex}}.hsk svg{{width:50px;height:40px}}
@media (max-width:760px){{body{{padding:14px}}.wrap{{display:block}}.wrap>*{{margin-bottom:16px}}.earlad{{grid-auto-rows:44px}}.earstep{{margin:0}}.hsw{{width:46px;height:36px}}.hsw svg{{width:45px;height:36px}}
 .rung{{grid-template-columns:44px 18px 22px 44px 1fr}}.hsk svg{{width:42.5px;height:34px}}}}
</style>
<div class="wrap">
<div class="card"><h2>Ear Lab ladder · major</h2>{lad(DIA)}</div>
<div class="card"><h2>With flats · coming down</h2>{lad(CHROMA)}</div>
<div class="card"><h2>With sharps · going up</h2>{lad(CHROMA_UP)}</div>
<div class="card"><h2>Sing it · hand signs (Keys room)</h2><div class="ladder">{keys}</div><p class="note">The sign joins the words; the row keeps its height.</p>
<h2 style="margin-top:22px">La-based minor</h2>{lad(['la', 'si', 'so', 'fa', 'mi', 're', 'do', 'ti', 'la'][0:8], home='la')}</div>
</div></html>'''
    (R / 'ladder_mock.html').write_text(html)

def ladder_full():
    rows = [("do'", None, None), (None, 'te', 'li'), ('la', None, None), (None, 'le', 'si'), ('so', None, None), (None, 'se', 'fi'), ('fa', None, None), ('mi', None, None), (None, 'me', 'ri'), ('re', None, None), (None, 'ra', 'di'), ('do', None, None)]
    rows.insert(1, ('ti', None, None))
    cell = lambda n, c: f'<div class="c {c}" style="grid-row:{{r}}/span 2">{sign(n, "full")}<b>{n.replace(chr(39), "′")}</b></div>' if n else ''
    h, r = '', 1
    for d, fl, sh in rows:
        if d: h += cell(d, 'd').format(r=r); nxt = r + 2
        else: h += cell(fl, 'f').format(r=r - 1) + cell(sh, 's').format(r=r - 1); nxt = r
        r = nxt
    # semitone neighbours (ti-do, mi-fa) sit a full step apart here like the others: an even ladder, as the brief asks
    html = f'''<!doctype html><html><meta charset="utf-8"><style>{FONTS}
body{{margin:0;background:transparent;color:#1d1a14;font:400 30px Outfit,sans-serif}}#L{{display:inline-grid;grid-template-columns:300px 300px 300px;grid-auto-rows:92px;column-gap:40px;padding:20px 30px 30px}}
.h{{font:600 20px Outfit;letter-spacing:5px;text-transform:uppercase;text-align:center;align-self:end;padding-bottom:14px;grid-row:1}}
.c{{display:flex;align-items:center;gap:14px}}.c svg{{width:200px;height:160px;flex:none}}.c b{{font:400 34px "Poiret One",Outfit}}.f{{grid-column:1}}.d{{grid-column:2}}.s{{grid-column:3}}
</style><div id="L"><div class="h f">Lowered ♭</div><div class="h d">The scale</div><div class="h s">Raised ♯</div>{h.replace('grid-row:', 'grid-row:calc(1 + ').replace('/span 2', ')/span 2')}</div></html>'''
    (R / 'ladder_full.html').write_text(html)

if __name__ == '__main__':
    write_svgs(); sheet(); ladder_mock(); ladder_full(); print('built')
