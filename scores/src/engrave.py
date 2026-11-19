"""Engrave the ten Analysis-room scores with Verovio from the licensed Humdrum sources in this folder.

Run from the repo root:   python3 scores/src/engrave.py          (needs: pip install verovio==6.4.1)

For each score it writes three engravings, all shown 1:1 (never stretched):
  scores/<key>.svg      desktop: Verovio scale 40 (staff-space 7.2 px), 880 px systems
  scores/<key>.t.svg    tablet:  scale 40, 560 px systems (panels narrower than 880 px, wider than a phone; fits 768 px portrait)
  scores/<key>.p.svg    phone:   scale 33 (staff-space 5.94 px), 336 px systems in an edge-to-edge phone frame (fits a 360 px screen; decision a); chorales on the phone at spacingLinear 0.3, spacingNonLinear 0.6 (decision b), spacingLinear 0.2, spacingNonLinear 0.5
House standard (SPEC, "House engraving standard"): Bravura; Verovio's embedded stylesheet stripped (colours and line
weights come from the app's CSS on .vrv); Humdrum instrument-name tokens blanked (no voice labels, no first-system
indent); chorales as closed score on a grand staff (Humdrum filter satb2gs); stave gap 6 staff-spaces (8 for the
chorales); between systems Verovio's minimum gap of 4 staff-spaces beyond each system's own notation plus room for the overlay
rows the app draws (design review FA-5, 19 Nov: tighter than the standard's 9 staff-spaces where the notes stay inside
the staves, so that 3 systems fit a 768-800 px tall screen); a one-bar last system is avoided where a slightly tighter spacing allows; text set in final px.

The app's analysis data (scores/meta.json) addresses notes and bars by the ids Verovio gives the UNFILTERED source
(note-L<line>F<field>, measure-L<line>). satb2gs rewrites the file, so for the chorales every note and bar of the
grand-staff engraving is given back its canonical id, matched by onset, pitch and duration. The script stops with an
error if any id cannot be matched, if the bar count changes, or if the notes no longer match meta.json's events.
"""
import json, re, sys, collections, pathlib
import verovio
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import credit  # embedded attribution (R14)

HERE = pathlib.Path(__file__).resolve().parent
SCORES = HERE.parent
SRC = {  # key: (file, repo, revision the app's ids were made from; see scores/src/README.md)
    'chorale': 'chor001.krn', 'ohaupt': 'chor080.krn', 'jesu': 'chor138.krn',
    'k545': 'sonata15-1.krn', 'k331a': 'sonata11-1a.krn', 'k331d': 'sonata11-1d.krn',
    'maple': 'mapleleaf.krn', 'entertainer': 'entertainer.krn',
    'chopin7': '028-1-BH-007.krn', 'chopin20': '028-1-BH-020.krn'}
CHORALES = {'chorale', 'ohaupt', 'jesu'}
VARIANTS = {  # suffix: (scale, system width px, extra options)
    '': (40, 880, {}),
    '.t': (40, 560, {}),
    '.p': (33, 336, {'spacingLinear': 0.2, 'spacingNonLinear': 0.5}),
}
LEFT_PX = 22  # room for the brace / bracket left of the staves (never clipped)
# overlay rows the app draws (final px): form rule + label above the system, harmony row, cadence-tag row below
ROW_ABOVE_FORM, ROW_HARM, ROW_CAD = 24, 20, 16
# final-px text sizes (SPEC, Text table)
PX = {'mNum': 11, 'tempo': 14, 'dir': 14, 'ending': 12, 'reh': 12, 'other': 12}


def prep(key, text):
    """Blank instrument-name tokens in place (same line count, so ids stay put); grand staff for the chorales."""
    out = []
    for ln in text.split('\n'):
        if ln.startswith('*') and not ln.startswith('**') and '*I' in ln:  # *I"name, *I'abbr, *Ipiano, *ICklav ...
            ln = '\t'.join('*' if t.startswith('*I') else t for t in ln.split('\t'))
        out.append(ln)
    t = '\n'.join(out)
    return t


def toolkit(opts, data):
    tk = verovio.toolkit()
    tk.setOptions(opts)
    if not tk.loadData(data):
        raise SystemExit('Verovio could not load the data')
    # Common time. K. 545, O Haupt, Jesu meine Freude and Op. 28/20 mark it *met(c). Verovio 6.4.1 turns that into a
    # meterSig sym="common" with visible="false" plus an empty mensur, so no time signature is drawn. Fix it in the
    # MEI (the source files stay untouched): make the common-time meterSig visible, drop the empty mensur, reload.
    # Element ids are carried over unchanged in the MEI, so meta.json's ids still match.
    mei = tk.getMEI()
    fixed = re.sub(r'(<meterSig [^>]*sym="common"[^>]*?) visible="false"', r'\1', mei)
    fixed = re.sub(r'<mensur xml:id="[^"]*" */>', '', fixed)
    if fixed != mei:
        tk = verovio.toolkit()
        tk.setOptions(opts)
        if not tk.loadData(fixed):
            raise SystemExit('Verovio could not reload the corrected MEI')
    return tk


def note_table(tk):
    """id -> (onset ms, midi pitch, duration ms) for every sounding note."""
    tm = tk.renderToTimemap({'includeRests': False})
    on, out = {}, {}
    for e in tm:
        for i in e.get('on', []):
            on[i] = e['tstamp']
        for i in e.get('off', []):
            if i in on:
                out[i] = (round(on[i]), tk.getMIDIValuesForElement(i)['pitch'], round(e['tstamp'] - on[i]))
    return out


# satb2gs puts soprano and alto on the upper staff (layers 1, 2) and tenor and bass on the lower (layers 1, 2); the
# canonical ids name the Humdrum field: F1 bass, F2 tenor, F3 alto, F4 soprano
GS_FIELD = {('1', '1'): '4', ('1', '2'): '3', ('2', '1'): '2', ('2', '2'): '1'}


def gs_voices(tk):
    """grand-staff note id -> canonical field number, from the staff and layer the note sits in"""
    out = {}
    for st in re.finditer(r'<staff [^>]*n="(\d)"[^>]*>(.*?)</staff>', tk.getMEI(), re.S):
        for ly in re.finditer(r'<layer [^>]*n="(\d)"[^>]*>(.*?)</layer>', st.group(2), re.S):
            for nid in re.findall(r'<note [^>]*xml:id="([^"]+)"', ly.group(2)):
                out[nid] = GS_FIELD.get((st.group(1), ly.group(1)))
    return out


def id_map(canon_tk, gs_tk, canon_svg, gs_svg):
    """map grand-staff ids -> canonical ids (notes by onset/pitch/duration, bars by order).
    Where two voices sound the same note together (a tenor-bass unison), onset, pitch and duration cannot tell them
    apart: the voice decides (0.48 fix R17: six unisons had the tenor's id on the bass note and the reverse)."""
    a, b = note_table(canon_tk), note_table(gs_tk)
    voice = gs_voices(gs_tk)
    pool = collections.defaultdict(list)
    for i, k in sorted(a.items()):
        pool[k].append(i)
    m = {}
    for i, k in sorted(b.items()):
        if not pool.get(k):
            raise SystemExit(f'no canonical note for {i} {k}')
        same = [c for c in pool[k] if re.search(r'F(\d)', c).group(1) == voice.get(i)]
        if len(pool[k]) > 1 and not same:
            raise SystemExit(f'{i} {k}: no canonical note in voice {voice.get(i)} among {pool[k]}')
        pick = same[0] if same else pool[k][0]
        pool[k].remove(pick)
        m[i] = pick
    if any(pool.values()):
        raise SystemExit('canonical notes left unmatched: ' + str([v for v in pool.values() if v][:5]))
    ma = re.findall(r'data-id="(measure-[^"]+)"', canon_svg)
    mb = re.findall(r'data-id="(measure-[^"]+)"', gs_svg)
    if len(ma) != len(mb):
        raise SystemExit(f'bar count changed under satb2gs: {len(ma)} -> {len(mb)}')
    m.update(dict(zip(mb, ma)))
    return m


def base_opts(scale, width, extra, spacing_system, staff_gap, margins):
    o = {'svgHtml5': True, 'svgRemoveXlink': True, 'font': 'Bravura', 'scale': scale,
         'pageWidth': round(width * 100 / scale), 'pageMarginLeft': round(LEFT_PX * 100 / scale), 'pageMarginRight': 0,
         'pageMarginTop': round(margins[0] * 100 / scale), 'pageMarginBottom': round(margins[1] * 100 / scale),
         'svgFormatRaw': True, 'xmlIdSeed': 1,
         'pageHeight': 60000, 'adjustPageHeight': True, 'breaks': 'auto', 'header': 'none', 'footer': 'none',
         'spacingStaff': staff_gap, 'spacingSystem': spacing_system, 'justifyVertically': False,
         'mnumInterval': 0, 'minLastJustification': 0.8}
    o.update(extra)
    return o


def post(svg, scale, idm):
    """strip the embedded stylesheet, give canonical ids back, set text in final px."""
    # drop Verovio's stylesheet, but keep its embedded Bravura @font-face: dynamics such as "f stacc." are set as
    # SMuFL text and need it (outlines elsewhere are paths, not text)
    svg = re.sub(r'<style[^>]*>(?!\s*@font-face).*?</style>', '', svg, flags=re.S)
    # NIFC editorial notes to the encoders (!LO:TX:...:problem) are not part of the score
    svg = re.sub(r'<g [^>]*class="dir problem"[^>]*>.*?</g>', '', svg, flags=re.S)
    # Verovio's stylesheet hid its expansion/section placeholders; with the stylesheet gone, remove them
    svg = re.sub(r'<g [^>]*class="[^"]*\bplaceholder\b[^"]*"[^>]*?(?:/>|>(?:<ellipse[^>]*/>)?</g>)', '', svg)
    if idm:
        svg = re.sub(r'data-id="([^"]+)"', lambda mm: f'data-id="{idm.get(mm.group(1), mm.group(1))}"', svg)
    upx = scale / 100 / 10  # screen px per SVG user unit inside the definition-scale viewBox (unit 10 per px at 100)

    def resize(mm):
        size = PX.get(mm.group(2).split()[0], PX['other'])
        return mm.group(1) + re.sub(r'<tspan font-size="\d+px"', f'<tspan font-size="{round(size / upx)}px"', mm.group(3))
    svg = re.sub(r'(<g [^>]*class="(mNum[^"]*|tempo|dir|ending|reh)"[^>]*>)(.*?</g>)', resize, svg, flags=re.S)
    # words inside dynamics ("stacc.") in final px; the SMuFL glyph tspans (font-family="Bravura") keep their size
    svg = re.sub(r'(<g [^>]*class="dynam"[^>]*>)(.*?</g>)',
                 lambda mm: mm.group(1) + re.sub(r'<tspan font-size="\d+px"', f'<tspan font-size="{round(PX["dir"] / upx)}px"', mm.group(2)), svg, flags=re.S)
    return svg


def verify(key, svg, meta, tk_canon):
    m = meta[key]
    want_bars = [x[1] for x in m['measures']]
    got_bars = re.findall(r'data-id="(measure-[^"]+)"', svg)
    if got_bars != want_bars:
        raise SystemExit(f'{key}: bars differ from meta.json ({len(got_bars)} vs {len(want_bars)})')
    ids = set(re.findall(r'data-id="(note-[^"]+)"', svg))
    need = {x['id'] for x in m.get('labels', [])} | {x['id'] for x in m.get('cads', [])}
    miss = need - ids
    if miss:
        raise SystemExit(f'{key}: overlay anchors missing from the engraving: {sorted(miss)[:5]}')
    if not re.search(r'class="meterSig"><use href="#E0[89]', svg):
        raise SystemExit(f'{key}: no time signature drawn')
    ev = sorted(note_table(tk_canon).values())
    me = sorted(tuple(x) for x in m['events'])
    pool = collections.defaultdict(list)  # meta.json rounds onsets down, Verovio to nearest: allow 2 ms
    for x in me:
        pool[x[1]].append(x)
    bad = []
    for a in ev:
        hit = next((b for b in pool[a[1]] if abs(a[0] - b[0]) <= 2 and abs(a[2] - b[2]) <= 2), None)
        if hit is None:
            bad.append(a)
        else:
            pool[a[1]].remove(hit)
    if len(ev) != len(me) or bad:
        raise SystemExit(f'{key}: notes differ from meta.json events: {len(ev)} vs {len(me)}, first diffs {bad[:3]}')
    return len(got_bars), len(ids)


def main():
    meta = json.load(open(SCORES / 'meta.json'))
    keys = sys.argv[1:] or list(SRC)
    report = {}
    for key in keys:
        raw = prep(key, (HERE / SRC[key]).read_text())
        m = meta[key]
        above = ROW_ABOVE_FORM if m['sections'] else 0
        below = (ROW_HARM if m['labels'] else 0) + (ROW_CAD if m['cads'] else 0)
        staff_gap = 16 if key in CHORALES else 12
        for suf, (scale, width, extra) in VARIANTS.items():
            half_space_px = 9 * scale / 100  # one MEI unit (half a staff-space) in px
            spacing_system = 8 + round((above + below) / half_space_px)
            ex = dict(extra)
            if key in CHORALES and suf == '.p':  # decision (b): wider phone spacing so numerals sit under their chords
                ex.update({'spacingLinear': 0.3, 'spacingNonLinear': 0.6})
            opts = base_opts(scale, width, ex, spacing_system, staff_gap, (max(6, 8 + above), 8 + below))
            # avoid a one-bar last system: step spacingLinear down by 0.01, at most 5 times
            lin0 = opts.get('spacingLinear', 0.25)
            for step in range(6):
                opts['spacingLinear'] = round(lin0 - 0.01 * step, 2)
                tk_c = toolkit(opts, raw)
                canon = tk_c.renderToSVG(1)
                parts = canon.split('data-class="system"')
                if len(parts) <= 2 or parts[-1].count('data-class="measure"') > 1:
                    break
            if step == 5 and parts[-1].count('data-class="measure"') == 1:
                opts['spacingLinear'] = lin0
                tk_c = toolkit(opts, raw)
                canon = tk_c.renderToSVG(1)
            if tk_c.getPageCount() != 1:
                raise SystemExit(f'{key}{suf}: more than one page')
            idm = None
            svg = canon
            if key in CHORALES:
                tk_g = toolkit(opts, raw + ('' if raw.endswith('\n') else '\n') + '!!!filter: satb2gs\n')
                svg = tk_g.renderToSVG(1)
                idm = id_map(tk_c, tk_g, canon, svg)
            svg = post(svg, scale, idm)
            svg = credit.embed(svg, key, meta)  # R14: source edition + licence inside every SVG
            bars, notes = verify(key, svg, meta, tk_c)
            (SCORES / f'{key}{suf}.svg').write_text(svg)
            wh = re.search(r'<svg width="(\d+)px" height="(\d+)px"', svg)
            report[f'{key}{suf}'] = {'bars': bars, 'notes': notes, 'width': int(wh.group(1)), 'height': int(wh.group(2)),
                                    'systems': svg.count('class="system"'), 'kB': len(svg) // 1024}
            print(key + suf, report[key + suf])
    return report


if __name__ == '__main__':
    main()
