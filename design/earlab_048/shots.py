#!/usr/bin/env python3
"""Screenshots of every mock-up at 1440 and 390 px (plus 1366x768 and 1024 for the layout check). Run after build.py."""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright
H = pathlib.Path(__file__).resolve().parent
PAGES = sys.argv[1:] or [p.stem for p in sorted(H.glob('*.html'))]
SIZES = [(1440, 900), (390, 844)]
EXTRA = {'metre_answered': [(1366, 768), (1024, 768)], 'rhythm_checked': [(1366, 768), (1024, 768)], 'cadence_r3_answered': [(1366, 768), (1024, 768)]}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
        for name in PAGES:
            for w, h in SIZES + EXTRA.get(name, []):
                if name == 'phone_dock' and w != 390: continue
                pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2 if w == 390 else 1)
                await pg.goto((H / f'{name}.html').as_uri()); await pg.wait_for_timeout(350)
                over = await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
                if over > 0: print('SIDEWAYS SCROLL', name, w, over)
                if name != 'phone_dock':  # grow the window to the page so the fixed rail runs the full height
                    ph = await pg.evaluate('document.documentElement.scrollHeight')
                    await pg.set_viewport_size({'width': w, 'height': max(h, ph)}); await pg.wait_for_timeout(150)
                await pg.screenshot(path=str(H / 'png' / f'{name}_{w}.png'), full_page=False)
                await pg.close()
        await b.close()
asyncio.run(main())
