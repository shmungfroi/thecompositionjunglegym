#!/usr/bin/env python3
"""The real app (index.html untouched) with the new signs swapped in at run time, for the mock-up renders only.
Ear Lab melody desk and Keys room at 1366x768 and 390."""
import asyncio, sys, json, pathlib
H = pathlib.Path(__file__).resolve().parent; REPO = H.parents[3]
sys.path.insert(0, str(REPO / 'tests' / 'harness')); import cjg, build
from playwright.async_api import async_playwright
SG = {n: build.sign(n) for n in build.ORDER}
KEY = {'d': 'do', 'r': 're', 'm': 'mi', 'f': 'fa', 's': 'so', 'l': 'la', 't': 'ti', 'si': 'si'}
JS = """([SG,KEY,GEST])=>{const st=document.createElement('style');st.textContent='.meldesk .hsw{width:56px;height:44px;color:var(--gold)}.meldesk .hsw svg{width:55px;height:44px;display:block}@media (max-width:760px){.meldesk .hsw{width:46px;height:36px}.meldesk .hsw svg{width:45px;height:36px}}.rung{grid-template-columns:52px 24px 30px 50px 1fr!important;padding:2px 10px!important}.rung .hsk{color:var(--c);display:flex}.rung .hsk svg{width:50px;height:40px}';document.head.appendChild(st);
 document.querySelectorAll('.meldesk .earstep').forEach(b=>{const s=b.dataset.earsol.replace(/[,']/g,''),w=b.querySelector('.hsw');if(w&&SG[KEY[s]||s])w.innerHTML=SG[KEY[s]||s]});
 document.querySelectorAll('#ksLadder .rung').forEach(r=>{const n=r.querySelector('.sy').textContent.trim();if(!SG[n]||r.querySelector('.hsk'))return;const k=document.createElement('span');k.className='hsk';k.innerHTML=SG[n];r.insertBefore(k,r.querySelector('.hs'))})}"""
async def main():
    async with async_playwright() as p:
        b = await cjg.launch(p)
        for w, h, d in [(1366, 768, 1), (390, 844, 2)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=d)
            pg = await ctx.new_page(); await pg.route('**/*', cjg.make_route(REPO)); await pg.goto('http://app/index.html'); await pg.wait_for_timeout(1000)
            await pg.evaluate("document.querySelector('.rail button[data-room=keys]').click()"); await pg.wait_for_timeout(400)
            await pg.evaluate(JS, [SG, KEY, build.GEST]); await pg.evaluate("document.getElementById('ksLadder').closest('.card').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(200)
            await pg.screenshot(path=str(H.parent / 'png' / f'app_keys_{w}.png'))
            await pg.evaluate("document.querySelector('.rail button[data-room=ear]').click()"); await pg.wait_for_timeout(400)
            await pg.evaluate("document.querySelector('[data-eardr=mel]').click()"); await pg.wait_for_timeout(400)
            await pg.evaluate("(document.querySelector('[data-earlv=\"3\"]')||{click(){}}).click()"); await pg.wait_for_timeout(300)
            await pg.evaluate("(document.querySelector('[data-earnew]')||document.querySelector('[data-earplay]')).click()"); await pg.wait_for_timeout(900)
            await pg.evaluate("window.elStop&&elStop()"); await pg.wait_for_timeout(200)
            await pg.evaluate(JS, [SG, KEY, build.GEST])
            r = await pg.evaluate("(()=>{const L=document.querySelector('.meldesk .earlad');L.scrollIntoView({block:'center'});const s=[...L.querySelectorAll('.earstep')];return {n:s.length,row:s[0].getBoundingClientRect().height,over:document.documentElement.scrollWidth-innerWidth}})()")
            print(w, json.dumps(r)); await pg.wait_for_timeout(200)
            await pg.screenshot(path=str(H.parent / 'png' / f'app_earlab_{w}.png')); await ctx.close()
        await b.close()
asyncio.run(main())
