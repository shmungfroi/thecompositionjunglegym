"""Embedded attribution for the engraved score SVGs (R14).

`credit_block(key, meta)` builds a <desc> + <metadata> pair from scores/meta.json's "src" line (the same text the
app's Credits panel and NOTICE.md carry). `embed(svg, key, meta)` inserts it into an engraved SVG, replacing any
earlier credit, and touches nothing else (the drawing is unchanged). engrave.py calls it on every engraving;
`python3 scores/src/credit.py` re-applies it to the SVGs already in scores/ without re-engraving.
"""
import json, pathlib, re
from xml.sax.saxutils import escape

SCORES = pathlib.Path(__file__).resolve().parent.parent
LICENCE = {  # licence name -> (url, repository licence text in scores/src/licences)
    'CC BY-NC-SA 4.0': 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
    'CC BY 4.0': 'https://creativecommons.org/licenses/by/4.0/'}
MARK = 'data-credit="cjg"'


def licence_of(src):
    for name in LICENCE:  # longest first is not needed: 'CC BY-NC-SA 4.0' is tested before 'CC BY 4.0'
        if name in src:
            return name
    raise SystemExit('no known licence in src line: ' + src)


def credit_block(key, meta):
    m = meta[key]
    lic = licence_of(m['src'])
    text = f"{m['t']}. {m['src']} Licence: {lic}, {LICENCE[lic]}. Full credits: NOTICE.md and the app's Credits panel."
    return (f'<desc {MARK}>{escape(text)}</desc>'
            f'<metadata {MARK}><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
            f'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:cc="http://creativecommons.org/ns#">'
            f'<cc:Work rdf:about=""><dc:title>{escape(m["t"])}</dc:title>'
            f'<dc:source>{escape(m["src"])}</dc:source>'
            f'<dc:rights>{escape(text)}</dc:rights>'
            f'<cc:license rdf:resource="{LICENCE[lic]}"/></cc:Work></rdf:RDF></metadata>')


def embed(svg, key, meta):
    svg = re.sub(r'<(desc|metadata) data-credit="cjg">.*?</\1>', '', svg, flags=re.S)
    i = svg.index('>') + 1  # end of the opening <svg ...> tag
    return svg[:i] + credit_block(key, meta) + svg[i:]


if __name__ == '__main__':
    meta = json.load(open(SCORES / 'meta.json'))
    for key in meta:
        for suf in ('', '.t', '.p'):
            p = SCORES / f'{key}{suf}.svg'
            p.write_text(embed(p.read_text(), key, meta))
            print('credited', p.name)
