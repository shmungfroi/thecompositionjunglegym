#!/usr/bin/env python3
"""PNG renders: sheet, ladder mock-ups (1366x768 and 390), per-sign PNGs (ink, transparent, 600 px tall), the full ladder."""
import asyncio, pathlib, build, gen
from playwright.async_api import async_playwright
H = pathlib.Path(__file__).resolve().parent; R = H.parent; P = R / 'png'
async def main():
    P.mkdir(exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1366, 'height': 768}); await pg.goto((R / 'sheet.html').as_uri()); await pg.wait_for_timeout(400)
        await pg.screenshot(path=str(P / 'sheet_1366.png'), full_page=True); await pg.close()
        for w, h, d in [(1366, 768, 1), (390, 844, 2)]:
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=d); await pg.goto((R / 'ladder_mock.html').as_uri()); await pg.wait_for_timeout(400)
            over = await pg.evaluate('document.documentElement.scrollWidth-innerWidth'); print('mock', w, 'sideways overflow', over)
            await pg.screenshot(path=str(P / f'ladder_mock_{w}.png'), full_page=True); await pg.close()
        pg = await b.new_page(viewport={'width': 750, 'height': 600})
        for n in gen.ORDER + ["do'"]:
            s = build.sign(n, 'mid')
            await pg.set_content(f'<body style="margin:0;color:#1d1a14"><style>svg{{width:750px;height:600px;display:block}}</style>{s}</body>')
            await pg.screenshot(path=str(P / f'{"do-high" if n == "do" + chr(39) else n}.png'), omit_background=True)
        await pg.close()
        pg = await b.new_page(viewport={'width': 1200, 'height': 900}); await pg.goto((R / 'ladder_full.html').as_uri()); await pg.wait_for_timeout(400)
        await (await pg.query_selector('#L')).screenshot(path=str(P / 'ladder_full.png'), omit_background=True); await pg.close()
        await b.close()
asyncio.run(main())
