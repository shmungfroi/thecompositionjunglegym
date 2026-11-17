"""Shared offline harness for the Composition Jungle Gym test suites.

Everything a suite needs is inside the repo: `tests/harness/package.json` pins VexFlow 4.2.3
(the version index.html loads from jsDelivr) and the two webfonts. Run `tests/run_all` once and it
installs them into tests/harness/node_modules. Pages are served from the repo at http://app/.
No network access is used while a suite runs: every other request is aborted.
"""
import pathlib, mimetypes, shutil

H = pathlib.Path(__file__).resolve().parent
NM = H / 'node_modules'
FONTS_CSS = """
@font-face{font-family:'Outfit';font-weight:300;src:url(/__f/outfit/files/outfit-latin-300-normal.woff2) format('woff2')}
@font-face{font-family:'Outfit';font-weight:400;src:url(/__f/outfit/files/outfit-latin-400-normal.woff2) format('woff2')}
@font-face{font-family:'Outfit';font-weight:600;src:url(/__f/outfit/files/outfit-latin-600-normal.woff2) format('woff2')}
@font-face{font-family:'Outfit';font-weight:700;src:url(/__f/outfit/files/outfit-latin-700-normal.woff2) format('woff2')}
@font-face{font-family:'Poiret One';font-weight:400;src:url(/__f/poiret-one/files/poiret-one-latin-400-normal.woff2) format('woff2')}
"""


def chrome():
    for c in ['/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser']:
        if pathlib.Path(c).exists():
            return c
    w = shutil.which('google-chrome') or shutil.which('chromium')
    return w  # None: let Playwright use its own bundled Chromium


def make_route(repo):
    repo = pathlib.Path(repo).resolve()

    async def route(r):
        u = r.request.url
        if '/__f/' in u:
            return await r.fulfill(path=str(NM / '@fontsource' / u.split('/__f/')[1]), content_type='font/woff2')
        if 'vexflow' in u:
            return await r.fulfill(path=str(NM / 'vexflow/build/cjs/vexflow.js'), content_type='application/javascript')
        if 'fonts.googleapis' in u:
            return await r.fulfill(body=FONTS_CSS, content_type='text/css')
        if u.startswith('http://app/'):
            p = repo / (u[len('http://app/'):].split('?')[0].split('#')[0] or 'index.html')
            if p.exists():
                return await r.fulfill(path=str(p), content_type=mimetypes.guess_type(str(p))[0] or 'text/html')
            return await r.fulfill(status=404)
        await r.abort()
    return route


async def launch(p, **kw):
    args = kw.pop('args', ['--autoplay-policy=no-user-gesture-required'])
    ex = chrome()
    return await p.chromium.launch(**({'executable_path': ex} if ex else {}), args=args, **kw)
