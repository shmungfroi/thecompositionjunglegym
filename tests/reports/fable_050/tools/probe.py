import sys, json
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:8765/index.html#'+sys.argv[1]); pg.wait_for_timeout(2000)
    print(json.dumps(pg.evaluate(sys.argv[2]),indent=1)[:6000])
    b.close()
