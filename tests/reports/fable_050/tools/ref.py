import sys, json
from playwright.sync_api import sync_playwright
OUT='/home/claude/fable050/ref/'
F='http://localhost:8765/design/earlab_048/fonts/'
CSS=''.join(f"@font-face{{font-family:'Outfit';font-weight:{w};src:url({F}outfit-latin-{w}-normal.woff2) format('woff2')}}" for w in (300,400,600,700))+f"@font-face{{font-family:'Poiret One';font-weight:400;src:url({F}poiret-one-latin-400-normal.woff2) format('woff2')}}"
SIZES=[(1440,900),(1366,768),(1280,800),(1024,768),(390,844)]
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    for room in ['seed','forms','ear']:
        for w,h in SIZES:
            pg=b.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
            pg.goto(f'http://localhost:8765/index.html#{room}'); pg.add_style_tag(content=CSS); pg.wait_for_timeout(1500)
            if room=='ear':
                pg.click('text=Melodic dictation'); pg.wait_for_timeout(500)
            if room=='seed':
                pg.evaluate("document.getElementById('tStop').hidden=false")
                m=pg.evaluate("""()=>[...document.querySelectorAll('header.top>*')].map(e=>{const r=e.getBoundingClientRect();return [e.className||e.id,Math.round(r.left),Math.round(r.width),Math.round(r.height)]})""")
                print(w,json.dumps(m))
            pg.screenshot(path=f'{OUT}{room}_{w}.png'); pg.close()
    b.close()
