import sys, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for w,h in [(1440,900),(1366,768),(1280,800),(1100,800),(1024,768),(900,800),(820,1000),(768,1000),(390,844),(360,740)]:
        pg=b.new_page(viewport={'width':w,'height':h})
        pg.goto('http://localhost:8765/index.html#ear'); pg.wait_for_timeout(1200); pg.click('text=Melodic dictation'); pg.wait_for_timeout(300)
        r=pg.evaluate("()=>{const e=document.querySelector('.el-rungrow'),c=e.closest('.card')||e.parentElement.parentElement;return [Math.round(e.getBoundingClientRect().width),Math.round(c.getBoundingClientRect().width)]}")
        pg.goto('http://localhost:8765/index.html#forms'); pg.wait_for_timeout(600)
        f=pg.evaluate("()=>{const g=document.querySelector('#room-forms .climbs');return [Math.round(g.getBoundingClientRect().width),getComputedStyle(g).gridTemplateColumns]}")
        print(w,r,f); pg.close()
    b.close()
