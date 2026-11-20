"""Content lint (charter regression suite 8). No browser needed.
Run: python3 tests/content_lint.py <repo dir>      Prints a JSON report; exits 1 on any failure.

 1. US terms (L63): no US term on its own, for every pair in the shared term list (cadences, note and rest values, bar/measure,
    stave/staff, tone/semitone), in index.html and scores/meta.json; ordinary "half", "whole", "measure" (verb) and "staff"
    (people) are not flagged. The lint's own positive and negative cases run first.
 2. censor terms: no radio-edit / clean-version / instrumental-excerpt style advice in any song `suitability` string
 3. sources: every song entry has two sources, or one authoritative source (a URL); entries with no recorded
    sources are the known exceptions below (open question OQ6) and are counted, not failed
 3b. source links: every rendered source href is a bare URL (no spaces); the note text is shown beside it
 5. syllabus tags (0.49 C10): every outcome code used has NESA's wording, every code listed is used, element letters exist
 4. credits: NOTICE.md names every third-party source; the footer has a Credits link; the Credits panel (details#credits,
    not the footer line) holds the sound credits and
    include the score and hand-sign credits
"""
import sys, re, json, pathlib

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
INDEX = (REPO / 'index.html').read_text(encoding='utf-8')
META = (REPO / 'scores' / 'meta.json').read_text(encoding='utf-8')

# Known entries with no recorded sources (OQ6, Justin's open question): (song, artist)
KNOWN_NO_SOURCES = set()  # OQ6 closed (L69): every song entry now has real source URLs

report = {'censor_terms': {'failures': []},
          'sources': {'failures': []}, 'source_links': {'failures': []}, 'credits': {'failures': []}}


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


# ---------- 1. US terms (L63, IC_TERMS_048 S5): no US term on its own ----------
# Every term pair in the shared list (cadences, note and rest values, bar/measure, stave/staff, tone/semitone) is checked, in index.html
# and scores/meta.json. A US term is allowed only where it is labelled as the US term: inside a "(US: ...)" / "[US: ...]" bracket, in the
# term list's us:/usp: fields, straight after "US" ("the US half cadence", "= US authentic"), or in a code comment. Ordinary English is
# not a US term: "half" and "whole" count only with note/rest/step/cadence; "measure" only as a counted noun ("measure 4", "two measures",
# "the next measure"), never the verb; "staff" only in a music sense ("the treble staff", "staff lines"), never people ("staff room").
SEP = r"(?:[\s\u00a0]|&nbsp;|-)"
NUMW = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
UNITS = r"(?:cm|mm|km|kg|m|g|ml|l|hz|khz|db|px|pt|ms|s|%)"
US_ALONE = re.compile(
    # cadence names: "authentic" / "deceptive" only in a cadence sense (not "an authentic Baroque sound")
    r"\bauthentic(?=\s*(?:cadences?|closes?|endings?|resolutions?|and\s+plagal|or\s+plagal)\b|\s*[.,;:)\]]|\s*$)"
    r"|\bdeceptive(?=\s*(?:cadences?|closes?|endings?|resolutions?|progressions?|resolves?)\b|\s*[.,;:)\]]|\s*$)"
    r"|\bhalf" + SEP + r"cadences?\b"
    # note and rest values, spelled out or numbered ("8th note", "two sixteenths"); "whole note-for-note" is ordinary English
    r"|\b(?:quarter|eighth|sixteenth|thirty-second|half|whole)" + SEP + r"(?:notes?(?!-for-)|rests?)\b"
    r"|\b(?:8th|16th|32nd|64th)" + SEP + r"(?:notes?(?!-for-)|rests?)\b"
    r"|\b(?:eighth|sixteenth)s\b"
    r"|\b(?:whole|half)" + SEP + r"steps?\b"
    r"|\bstaffs\b|\bstaff(?=\s+(?:lines?|notation|position|paper)\b)"
    r"|\b(?:the|a|treble|bass|grand|alto|tenor|each|one|single|five-line|same|top|bottom|lower|upper)\s+staff\b(?!\s+(?:room|members?|meetings?|development|notes))"
    # measure as a counted noun ("measure 4", "measures 4-8", "measure one"), not the verb ("it measures 4 cm")
    r"|\bmeasures?\s+\d+(?:\s*[-\u2013]\s*\d+)?(?!\d)(?!\s*" + UNITS + r"\b)"
    r"|\bmeasures?\s+" + NUMW + r"\b"
    r"|\b\d+\s+measures?\b"
    r"|\bmeasures?\s+of\s+(?:rest|silence)\b"
    r"|\b(?:first|last|final|opening|closing|next|previous|second|third)\s+measures?\s+of\s+the\s+(?:song|piece|phrase|tune|verse|chorus|bridge|section|melody|excerpt|score|passage)\b"
    r"|\b(?:per|each|every|this|that|next|last|first|final|one|two|three|four|eight|twelve|sixteen|the|a)\s+measures?\b(?!\s+(?:of|the|every|each|how|a|an|it|its|your)\b)",
    re.I)


def us_allowed(text, start):
    ls = text.rfind('\n', 0, start) + 1
    before = text[ls:start]
    for o, c in (('(US', ')'), ('[US', ']')):        # inside a US bracket on the same line
        i = before.rfind(o)
        if i != -1 and c not in before[i:]:
            return True
    if re.search(r"\bin the US\b[^.\n]*\b(?:called|known|named|termed|labelled|labeled)\b[^.\n]*$", before, re.I):   # "In the US this is called a half cadence."
        return True
    if re.search(r"\bus[p]?:'[^']*$", before):        # the term list's US field
        return True
    if re.search(r"\bUS:?\s+'?(?:imperfect\s+|Phrygian\s+)?$", before):   # "the US half cadence", "= US authentic", "US 'imperfect authentic'"
        return True
    # a code comment: // on this line (not a URL's ://), or inside /* ... */ or <!-- ... -->
    if re.search(r"(?:^|[\s;,{}()])//(?!/)", before.replace('://', ':__')):
        return True
    for o, c in (('/*', '*/'), ('<!--', '-->')):
        i = text.rfind(o, 0, start)
        if i != -1 and text.find(c, i) > start:
            return True
    return False


def us_alone(text):
    return [m for m in US_ALONE.finditer(text) if not us_allowed(text, m.start())]


# the lint's own cases live in tests/fixtures/us_probes.json (positives must be found, negatives must not); each is run through us_alone()
_FIX = json.loads((pathlib.Path(__file__).parent / 'fixtures' / 'us_probes.json').read_text(encoding='utf-8'))
US_CASES = [(t, 1) for t in _FIX['positive']] + [(t, 0) for t in _FIX['negative']]
report['us_terms'] = {'failures': [], 'cases_checked': len(US_CASES)}
for s, n in US_CASES:
    if len(us_alone(s)) != n:
        report['us_terms']['failures'].append({'lint case': s, 'expected': n, 'found': [m.group(0) for m in us_alone(s)]})
# a US bracket gives the whole US term: "(US: half)" or "(US: deceptive)" alone is a shortened term (L8)
US_SHORT = re.compile(r'[(\[]US:\s*(?:authentic|half|deceptive)\s*[.)\];,]|\((?:half|authentic|deceptive)\)', re.I)
for s, n in [(t, 1) for t in _FIX['short_positive']] + [(t, 0) for t in _FIX['short_negative']]:
    if len(US_SHORT.findall(s)) != n:
        report['us_terms']['failures'].append({'lint case (short)': s, 'expected': n})
for name, text in (('index.html', INDEX), ('scores/meta.json', META)):
    for m in US_SHORT.finditer(text):
        ls = text.rfind('\n', 0, m.start()) + 1
        report['us_terms']['failures'].append({'file': name, 'line': line_of(text, m.start()), 'why': 'shortened US term in a bracket',
                                               'text': text[max(ls, m.start() - 50):m.end() + 30].strip()})
for name, text in (('index.html', INDEX), ('scores/meta.json', META)):
    for m in us_alone(text):
        ls = text.rfind('\n', 0, m.start()) + 1
        report['us_terms']['failures'].append({'file': name, 'line': line_of(text, m.start()),
                                               'text': text[max(ls, m.start() - 50):m.end() + 30].strip()})

# ---------- song data ----------
m = re.search(r'^const SONGS=(\{.*\});?\s*$', INDEX, re.M)
SONGS = json.loads(m.group(1)) if m else {}
entries = [(q, x) for q, v in SONGS.items() for x in v]
report['song_entries'] = len(entries)
if not entries:
    report['sources']['failures'].append('SONGS data not found')

# ---------- 2. censor terms ----------
CENSOR_TERMS = re.compile(
    r'radio[- ]edit|clean (radio )?(version|edit)|edited version|instrumental( excerpt| version| only)?|'
    r'shorter edit|skip (the|that|this|it)|play only|only play|intro only|just the intro|use (the )?riff|'
    r'use this track only|check with your school|check the lyric sheet|lyric sheet|handle with care|'
    r'consider an?|\bmute\b|bleep|censor|swap (in|for)|rather than the lyric|^\s*(mild )?flag\b', re.I)
for q, x in entries:
    s = str(x.get('suitability') or '')
    hit = CENSOR_TERMS.search(s)
    if hit:
        report['censor_terms']['failures'].append({'song': x['song'], 'artist': x['artist'], 'term': hit.group(0), 'text': s})

# ---------- 3. sources ----------
exceptions_seen = set()
for q, x in entries:
    key = (x['song'], x['artist'])
    srcs = x.get('sources') or []
    urls = [u for u in srcs if re.match(r'https?://', str(u))]
    good = len(srcs) >= 2 and len(urls) >= 1 or len(urls) >= 1 and len(srcs) == 1
    if good and not any('already verified' in str(u) for u in srcs):
        continue
    if any('already verified' in str(u) for u in srcs):
        report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'sources': srcs, 'why': 'placeholder source text'})
        continue
    if key in KNOWN_NO_SOURCES:
        exceptions_seen.add(key)
        continue
    report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'sources': srcs})
# 0.48 (E): an entry with exactly one source that is a Hooktheory page must say so on the card (where-text) and in the source note.
for q, x in entries:
    srcs = x.get('sources') or []
    if len(srcs) == 1 and 'hooktheory.com' in str(srcs[0]):
        if 'as transcribed on hooktheory' not in str(x.get('where', '')).lower():
            report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'why': 'single Hooktheory source, where-text lacks "as transcribed on Hooktheory"'})
        if 'single community transcription' not in str(srcs[0]):
            report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'why': 'single Hooktheory source, source note lacks "a single community transcription"'})
# Nothing Else Matters add9 placement rests on Hooktheory alone (the second source does not give the placement).
for q, x in entries:
    if x['song'] == 'Nothing Else Matters' and q == 'add9' and 'as transcribed on hooktheory' not in x['where'].lower():
        report['sources']['failures'].append({'song': x['song'], 'why': 'add9 placement not labelled as Hooktheory-only'})
# 0.48 (E, app-wide): the same rule for the Keys-room scale songs (SCSONGS, written as "let SCSONGS={...},IVSONGS={...};").
_ms = re.search(r'^let SCSONGS=(\{.*\}),IVSONGS=\{', INDEX, re.M)
if _ms:
    _sc = json.loads(_ms.group(1))
    report['scsong_entries'] = sum(len(v) for v in _sc.values())
    for q, v in _sc.items():
        for x in v:
            srcs = x.get('sources') or []
            if len(srcs) == 1 and 'hooktheory.com' in str(srcs[0]):
                if 'as transcribed on hooktheory' not in str(x.get('where', '')).lower():
                    report['sources']['failures'].append({'scale': q, 'song': x['song'], 'why': 'SCSONGS single Hooktheory source, where-text lacks "as transcribed on Hooktheory"'})
                if 'single community transcription' not in str(srcs[0]):
                    report['sources']['failures'].append({'scale': q, 'song': x['song'], 'why': 'SCSONGS single Hooktheory source, source note lacks "a single community transcription"'})
else:
    report['sources']['failures'].append('SCSONGS data not found for the Hooktheory label check')
report['sources']['known_exceptions_count'] = len(exceptions_seen)
report['sources']['known_exceptions_listed'] = len(KNOWN_NO_SOURCES)
report['sources']['known_exceptions_now_sourced'] = sorted(' / '.join(k) for k in KNOWN_NO_SOURCES - exceptions_seen)

def href_of(h):
    m = re.search(r'href="([^"]*)"', h)
    return m.group(1).replace('&amp;', '&') if m else None


# ---------- 3b. rendered source links (0.48 SRCFIX): every href is a bare URL, the note is shown as text ----------
# Runs the page's own srcItem() under node on every source string in SONGS and SCSONGS.
import subprocess
fm = re.search(r'^function srcItem\(u\)\{.*$', INDEX, re.M)
em = re.search(r'^const esc=.*$', INDEX, re.M)
sm = re.search(r'^let SCSONGS=(\{.*\});?\s*$', INDEX, re.M)
if not (fm and em and sm):
    report['source_links']['failures'].append('srcItem / esc / SCSONGS not found')
else:
    js = (em.group(0) + '\n' + fm.group(0) + '\nconst S=' + sm.group(1) + ';const T=' + json.dumps(SONGS) + ';\n'
          'const all=[];for(const D of [T,S])for(const k in D)for(const x of D[k])for(const u of (x.sources||[]))all.push(u);\n'
          'console.log(JSON.stringify(all.map(u=>[u,srcItem(u)])))')
    try:
        out = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)
        report['source_links']['rendered'] = len(out)
        for u, h in out:
            for href in re.findall(r'href="([^"]*)"', h):
                if not re.fullmatch(r'https?://[^\s"]+', href):
                    report['source_links']['failures'].append({'source': u, 'href': href})
            mu = re.match(r'(.*?)(https?://\S+)(.*)$', u, re.S)
            if mu:
                if href_of(h) != mu.group(2):
                    report['source_links']['failures'].append({'source': u, 'why': 'href is not the first URL token'})
                for part in (mu.group(1).strip().rstrip(':'), mu.group(3).strip()):
                    if len(part) > 30 and part.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;') not in h:
                        report['source_links']['failures'].append({'source': u, 'why': 'note text not shown'})
            elif 'href=' in h:
                report['source_links']['failures'].append({'source': u, 'why': 'link made from a source with no URL'})
    except Exception as e:
        report['source_links']['failures'].append(f'node check failed: {e}')

# ---------- 4. credits ----------
NEED = ['Bach chorales', 'Mozart', 'Joplin', 'Craig Stuart Sapp', 'CC BY-NC-SA 4.0', 'Chopin', 'Op. 28 Nos. 7 and 20',
        'Fryderyk Chopin Institute', 'NIFC', 'CC BY 4.0', 'VCSL', 'CC0', 'FluidR3_GM', 'Frank Wen', 'CC BY 3.0', 'Curwen',
        'Kodály Music Education Institute of Australia', 'KMEIA', '2003', 'VexFlow', 'MIT', 'jsDelivr', 'Outfit',
        'Poiret One', 'SIL', 'OFL', 'Verovio', 'LGPL', 'non-commercial',
        "First Editions of Fryderyk Chopin's Music", 'Copyright 2017-2021 The Fryderyk Chopin Institute (https://nifc.pl)',
        'https://chopinscores.org', 'Copyright (C) 2009 Craig Stuart Sapp', 'Copyright (C) 2004-2018 Craig Stuart Sapp',
        'Copyright (C) 2004-2021 Craig Stuart Sapp', 'licenses/by/3.0/us/', 'Leipzig', 'Bravura',
        'permission confirmed by Justin Ossher', 'github.com/craigsapp/bach-370-chorales',
        'github.com/craigsapp/mozart-piano-sonatas', 'github.com/craigsapp/joplin', 'chopin-first-editions']
nt = REPO / 'NOTICE.md'
if not nt.exists():
    report['credits']['failures'].append('NOTICE.md missing')
else:
    notice = nt.read_text(encoding='utf-8')
    for t in NEED:
        if t.lower() not in notice.lower() and not (t == 'OFL' and 'open font licence' in notice.lower()):
            report['credits']['failures'].append(f'NOTICE.md does not mention "{t}"')
ftm = re.search(r'<footer>(.*?)</footer>', INDEX, re.S)
# R7 (0.48): the footer line no longer carries the sample-library credits; the Credits panel (details#credits) holds them all.
fm = re.search(r'<details[^>]*id="credits"[^>]*>(.*?)</details>', INDEX, re.S)
if not ftm:
    report['credits']['failures'].append('footer not found')
elif not fm:
    report['credits']['failures'].append('Credits panel (details#credits) not found')
else:
    foot = fm.group(1)
    line = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', ftm.group(1).replace(fm.group(0), '')))
    for t in ['FluidR3', 'Frank Wen', 'CC BY 3.0', 'VCSL', 'Steinway']:
        if t in line:
            report['credits']['failures'].append(f'footer line still carries the sample credit "{t}" (it belongs in the Credits panel)')
    if not re.search(r'<summary[^>]*>\s*Credits\s*</summary>|<a [^>]*>\s*Credits\s*</a>|<button[^>]*>\s*Credits\s*</button>', ftm.group(1)):
        report['credits']['failures'].append('footer has no Credits link')
    for t in ['VCSL', 'Steinway B', 'CC0', 'FluidR3_GM', 'Frank Wen', 'CC BY 3.0', 'midi-js-soundfonts']:
        if t not in foot:
            report['credits']['failures'].append(f'Credits panel does not mention "{t}"')
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', foot.replace('<br>', ' '))).replace('&amp;', '&')
    for t in ['Sapp', 'Chopin Institute', 'NIFC', 'Curwen', 'Kodály Music Education Institute of Australia', 'KMEIA', 'used with permission',
              'CC BY-NC-SA 4.0', 'CC BY 4.0', 'Verovio',
              "First Editions of Fryderyk Chopin's Music", 'Copyright 2017-2021 The Fryderyk Chopin Institute (https://nifc.pl)',
              'https://chopinscores.org', 'Copyright (C) 2009 Craig Stuart Sapp', 'Copyright (C) 2004-2018 Craig Stuart Sapp',
              'Copyright (C) 2004-2021 Craig Stuart Sapp', 'Leipzig', 'Bravura']:
        if t not in text:
            report['credits']['failures'].append(f'on-screen credits do not mention "{t}"')

# on-screen links, README pointer, meta.json licence on every score
for u in ['creativecommons.org/licenses/by-nc-sa/4.0/', 'creativecommons.org/licenses/by/4.0/', 'creativecommons.org/licenses/by/3.0/us/',
          'creativecommons.org/publicdomain/zero/1.0/', 'github.com/craigsapp/bach-370-chorales', 'github.com/craigsapp/mozart-piano-sonatas',
          'github.com/craigsapp/joplin', 'github.com/pl-wnifc/humdrum-chopin-first-editions']:
    if fm and u not in fm.group(1):
        report['credits']['failures'].append(f'on-screen credits have no link to {u}')
rd = REPO / 'README.md'
if not rd.exists() or 'NOTICE.md' not in rd.read_text(encoding='utf-8'):
    report['credits']['failures'].append('README.md does not point to NOTICE.md')
try:
    for k, v in json.loads(META).items():
        if 'src' in v and not re.search(r'Analysis layer[^.]*\(CC BY(-NC-SA)? 4\.0\)|Form layer[^.]*\(CC BY(-NC-SA)? 4\.0\)', v['src']):
            report['credits']['failures'].append(f'meta.json {k}: src does not state the annotation layer licence')
except Exception as e:
    report['credits']['failures'].append(f'meta.json unreadable: {e}')

# lyric lint: content-warning text must describe, not quote (no quoted words, no known lyric words)
WARN_TEXT = []
wm = re.search(r'const WARN=\{(.*?)\};', INDEX, re.S)
if wm:
    WARN_TEXT += re.findall(r"n:'((?:[^'\\]|\\.)*)'", wm.group(1))
WARN_TEXT += [str(x.get('suitability') or '') for _, x in entries]
for mm in re.finditer(r'"content": \{[^{}]*?"note": "((?:[^"\\]|\\.)*)"', INDEX):
    WARN_TEXT.append(mm.group(1))
QUOTED = re.compile(r"(^|[\s(])(['\"\u2018\u201c])[^'\"\u2019\u201d]{2,}(['\"\u2019\u201d])(?![A-Za-z])")
LYRICWORD = re.compile(r'libido|mulatto|pissed|deaf, dumb|white boy|\bdamn\b', re.I)
report['lyric_words'] = {'failures': []}
for s in WARN_TEXT:
    if QUOTED.search(s) or LYRICWORD.search(s):
        report['lyric_words']['failures'].append(s)


# ---------- 6. song rules (0.49 C11): one entry per genre slot per chord type, approved slot order, at least one post-2015 song ----------
report['song_rules'] = {'failures': []}
_SL = ['Blues/jazz', 'Pop', 'Rock', 'Musical theatre', 'Metal', 'Australian pick']
for q, v in SONGS.items():
    sl = [x['slot'] for x in v]
    if len(set(sl)) != len(sl):
        report['song_rules']['failures'].append(f'chord {q!r}: a slot is used twice: {sl}')
    if any(x not in _SL for x in sl):
        report['song_rules']['failures'].append(f'chord {q!r}: unknown slot in {sl}')
    elif sl != sorted(sl, key=_SL.index):
        report['song_rules']['failures'].append(f'chord {q!r}: slots are not in the approved genre order: {sl}')
_post = sorted({(x['song'], x['year']) for _, x in entries if int(x['year']) > 2015})
report['song_rules']['post_2015'] = [f'{a} ({b})' for a, b in _post]
if not _post:
    report['song_rules']['failures'].append('no song after 2015 (L70: span up to the present)')

# 0.49 C18 slot honesty: a song in the Metal slot must be metal, not a genre fallback; a slot is either filled or a declared gap, never both.
_FB = re.compile(r"fallback|stand-in|not (?:a )?metal|isn.t metal|rather than metal|no (?:famous|clean)[^.]*metal|hard rock|britpop|jazz", re.I)
def metal_slot_dishonest(x):
    """True if a Metal-slot entry is a labelled stand-in: it has a fallback note, or its own fallback, recording or suitability text says it is not metal."""
    if x.get('slot') != 'Metal':
        return False
    if x.get('fallback'):
        return True
    return bool(_FB.search(' '.join(str(x.get(k) or '') for k in ('fallback', 'recording', 'suitability'))))
_mg = re.search(r'^const SONGGAPS=(\{.*?\});', INDEX, re.M)
SONGGAPS = json.loads(_mg.group(1)) if _mg else {}
if not _mg:
    report['song_rules']['failures'].append('SONGGAPS data not found')
for q, v in SONGS.items():
    for x in v:
        if metal_slot_dishonest(x):
            report['song_rules']['failures'].append(f'chord {q!r}: Metal slot holds a genre fallback ({x["song"]}); show it as a SONGGAPS gap instead')
    filled = {x['slot'] for x in v}
    for g in SONGGAPS.get(q, []):
        if g in filled:
            report['song_rules']['failures'].append(f'chord {q!r}: slot {g!r} is both filled and declared a gap')
# fixtures: each case must give the stated verdict (guards against the check going dead again)
for _c in json.loads((pathlib.Path(__file__).parent / 'fixtures' / 'slot_honesty.json').read_text(encoding='utf-8')):
    if metal_slot_dishonest(_c['entry']) != _c['must_fail']:
        report['song_rules']['failures'].append(f'slot-honesty fixture {_c["name"]!r}: expected must_fail={_c["must_fail"]}')
for q, g in SONGGAPS.items():
    if q not in SONGS or any(x not in _SL for x in g):
        report['song_rules']['failures'].append(f'SONGGAPS has an unknown chord type or slot: {q!r} {g}')

# ---------- 5. syllabus tags (0.49 C10): every code used has NESA's wording; every code listed is used; element letters exist ----------
# NESA outcome wording, read from curriculum.nsw.edu.au outcomes pages on 20 Nov 2026 (Music 1, Music 2, Music Extension 11-12 (2025)).
NESA_WORDING = {
 'MU1-11L-01': 'describes the ways Music context and Music language shape music',
 'MU1-11L-02': 'uses aural skills to identify and describe features of music',
 'MU1-11C-01': 'uses Compositional language to create musical ideas',
 'MU1-12L-01': 'analyses the ways Music context and Music language shape music',
 'MU1-12L-02': 'uses aural skills to analyse features of music',
 'MU2-11L-01': 'analyses the ways Music context and Music language shape meaning in musical pieces',
 'MU2-11L-02': 'analyses music and musical evidence to communicate ideas and perspectives',
 'MU2-11C-01': 'analyses and notates compositions using Music language',
 'MU2-11C-02': 'composes music with stylistic understanding of Compositional language and expressive intent',
 'MU2-12L-01': 'evaluates the ways Music context and Music language shape meaning and expressive intent in musical pieces',
 'MU2-12L-02': 'analyses music and musical evidence to communicate ideas and perspectives',
 'MU2-12C-01': 'evaluates and notates compositions using Music language',
 'MU2-12C-02': 'composes music with stylistic understanding of Compositional language and expressive intent',
 'MUE-12L-01': 'analyses musical intent and effect based on score study, recordings, composer and performer commentary'}
report['syllabus_tags'] = {'failures': []}
try:
    _ts = INDEX[INDEX.index('const SYLE={'):INDEX.index('const SYLS6=')]
    _js = _ts + '\nconsole.log(JSON.stringify({SYLE,SYLO,SYLM}))'
    _d = json.loads(subprocess.run(['node', '-e', _js], capture_output=True, text=True, check=True).stdout)
    _used = set()
    for k, m in _d['SYLM'].items():
        for c in m['o']:
            _used.add(c)
            if c not in _d['SYLO']:
                report['syllabus_tags']['failures'].append(f'{k}: outcome {c} has no wording in SYLO')
        if len(set(m['o'])) != len(m['o']):
            report['syllabus_tags']['failures'].append(f'{k}: duplicate outcome code')
        for x in m['e']:
            if x not in _d['SYLE']:
                report['syllabus_tags']['failures'].append(f'{k}: unknown element letter {x}')
        if len(set(m['e'])) != len(m['e']):
            report['syllabus_tags']['failures'].append(f'{k}: duplicate element letter')
    for c in _d['SYLO']:
        if c not in _used:
            report['syllabus_tags']['failures'].append(f'{c} is defined but attached to nothing')
        if c in NESA_WORDING and _d['SYLO'][c] != NESA_WORDING[c]:
            report['syllabus_tags']['failures'].append(f'{c}: wording differs from NESA: {_d["SYLO"][c]}')
    for c in NESA_WORDING:
        if c not in _d['SYLO']:
            report['syllabus_tags']['failures'].append(f'{c} is missing from SYLO')
    for need in ('Melody', 'Harmony'):
        if need not in _d['SYLE'].values():
            report['syllabus_tags']['failures'].append(f'element {need} missing from SYLE')
    report['syllabus_tags']['rooms_checked'] = len(_d['SYLM'])
    report['syllabus_tags']['codes'] = len(_d['SYLO'])
except Exception as e:
    report['syllabus_tags']['failures'].append(f'tag check failed: {e}')

report['passed'] = not any(report[k]['failures'] for k in ('us_terms', 'censor_terms', 'sources', 'source_links', 'credits', 'lyric_words', 'syllabus_tags', 'song_rules'))
print(json.dumps(report, ensure_ascii=False, indent=1))
sys.exit(0 if report['passed'] else 1)
