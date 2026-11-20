"""IC_REG_049 probe C11: render the Chord Library minor-triad card and read the Dance Monkey song card as a student sees it."""
import asyncio, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3] / 'harness'))
import cjg
from playwright.async_api import async_playwright
REPO = pathlib.Path(__file__).resolve().parents[4]
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p); pg = await b.new_page(viewport={'width': 1440, 'height': 1000}); await pg.route('**/*', cjg.make_route(REPO))
        await pg.goto('http://app/index.html#seed'); await pg.wait_for_timeout(1200)
        r = await pg.evaluate("""()=>{S.q='m';renderSongs();const el=[...document.querySelectorAll('*')].filter(e=>e.children.length<40&&/Dance Monkey/.test(e.textContent)).sort((a,b)=>a.textContent.length-b.textContent.length)[0];
          let c=el;for(let i=0;i<4&&c.parentElement&&c.textContent.length<300;i++)c=c.parentElement;return{txt:c?c.innerText:null,warn:/⚠/.test(c?c.innerText:''),links:c?[...c.querySelectorAll('a')].map(a=>a.href):[]}}""")
        await b.close(); print(r)
asyncio.run(main())
