from playwright.sync_api import sync_playwright
O='/home/claude/fable050/ref/html/'
with sync_playwright() as p:
    b=p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
    pg=b.new_page(viewport={'width':1440,'height':900})
    pg.goto('http://localhost:8765/index.html#ear'); pg.wait_for_timeout(1500); pg.click('text=Melodic dictation'); pg.wait_for_timeout(400)
    open(O+'ear.html','w').write(pg.evaluate("document.getElementById('room-ear').outerHTML"))
    pg.goto('http://localhost:8765/index.html#seed'); pg.wait_for_timeout(1000)
    open(O+'seed.html','w').write(pg.evaluate("document.getElementById('room-seed').outerHTML"))
    pg.goto('http://localhost:8765/index.html#forms'); pg.wait_for_timeout(800)
    open(O+'forms.html','w').write(pg.evaluate("document.getElementById('room-forms').outerHTML"))
    pg.close()
    pg=b.new_page(viewport={'width':390,'height':844})
    pg.goto('http://localhost:8765/index.html#forms'); pg.wait_for_timeout(1200)
    open(O+'tabbar.html','w').write(pg.evaluate("document.querySelector('.tabbar').outerHTML+'\\n'+document.getElementById('msheet').outerHTML"))
    b.close()
