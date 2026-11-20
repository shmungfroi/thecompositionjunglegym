import json, pathlib, sys, asyncio
from playwright.async_api import async_playwright
H = pathlib.Path(__file__).resolve().parent
names = sys.argv[1:] or [p.stem for p in sorted((H / 'drawn').glob('*.json'))]
def svg(n, small=False, cls=''):
    d = json.loads((H / 'drawn' / f'{n}.json').read_text()); s = '_s' if small else ''
    return f'<svg class="{cls}" viewBox="0 0 80 64"><path d="{d["tone" + s]}" fill="currentColor" fill-opacity="{.2 if small else .17}"/><path d="{d["ink" + s]}" fill="currentColor"/></svg>'
cells = ''.join(f'<figure><div class="b">{svg(n)}</div><span class="s">{svg(n, True)}</span><span class="s d">{svg(n, True)}</span><span class="m">{svg(n)}</span> {n}</figure>' for n in names)
html = f'<body style="margin:8px;background:#f6f1e7;color:#221e1a;font:13px sans-serif"><style>figure{{display:inline-block;margin:2px;width:410px}}.b svg{{width:410px;height:328px;display:block}}.s svg{{width:42.5px;height:34px}}.s.d{{background:#12100b;color:#c9a24a;display:inline-block}}.m svg{{width:120px;height:96px}}</style>{cells}</body>'
(H / '_view.html').write_text(html)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox']); pg = await b.new_page(viewport={'width': 1260, 'height': 640})
        await pg.goto((H / '_view.html').as_uri()); await pg.screenshot(path='/tmp/hs/view.png', full_page=True); await b.close()
asyncio.run(main())
