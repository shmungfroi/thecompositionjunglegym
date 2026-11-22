#!/usr/bin/env python3
"""PNG renders of the mock-ups. Usage: shots.py [name ...]. Also reports sideways scroll, text under 11 px and small tap targets."""
import sys, pathlib, json
from playwright.sync_api import sync_playwright
H = pathlib.Path(__file__).resolve().parent.parent
SIZES = [(1440, 900), (1366, 768), (1280, 800), (1024, 768), (390, 844)]
PLAN = {  # name: (sizes, full page?)
 'mock_level_control': (SIZES, False),
 'mock_level_control_closed': (SIZES + [(820, 1000)], False),
 'mock_level_control_L4_nocur': ([(1366, 768), (1024, 768), (390, 844)], False),
 'mock_ordering': ([s for s in SIZES if s[0] != 1280], True),
 'mock_ordering_L2_open': ([(1366, 768), (390, 844)], True),
 'mock_rungs': ([s for s in SIZES if s[0] != 1280] + [(1280, 800), (820, 1000)], True),
}
CHECK = """()=>{const out={small:[],tap:[],over:document.documentElement.scrollWidth-innerWidth};
 const vis=e=>{const r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width>0&&r.height>0&&s.visibility!=='hidden'&&s.display!=='none'&&!e.closest('[hidden]')};
 document.querySelectorAll('body *').forEach(e=>{if(!vis(e))return;if(e.closest('.sr'))return;
  const own=[...e.childNodes].some(n=>n.nodeType===3&&n.nodeValue.trim());if(own){const f=parseFloat(getComputedStyle(e).fontSize);if(f<11)out.small.push((e.className||e.tagName)+':'+f+':'+e.textContent.trim().slice(0,20))}});
 if(innerWidth<=760)document.querySelectorAll('button,select,summary,a,input').forEach(e=>{if(!vis(e))return;let r=e.getBoundingClientRect();const a=getComputedStyle(e,'::after');let h=r.height,w=r.width;
   if(a.content!=='none'&&a.position==='absolute'&&e.classList.contains('lvbtn')){h+=12;w+=8}
   if(h<43.5||w<43.5)out.tap.push((e.className||e.id||e.tagName)+':'+Math.round(w)+'x'+Math.round(h)+':'+e.textContent.trim().slice(0,14))});
 out.small=[...new Set(out.small)];out.tap=[...new Set(out.tap)];return out}"""
names = sys.argv[1:] or list(PLAN)
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--no-sandbox'])
    for name in names:
        sizes, full = PLAN[name]
        for w, h in sizes:
            pg = b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2 if w == 390 else 1)
            pg.goto((H / f'{name}.html').as_uri()); pg.wait_for_timeout(400)
            r = pg.evaluate(CHECK)
            print(name, w, 'over', r['over'], '| <11px', r['small'][:8], '| tap<44', r['tap'][:12])
            if full and w <= 900:  # grow the window to the page so fixed bars sit at the true top and bottom
                ph = pg.evaluate('document.documentElement.scrollHeight'); pg.set_viewport_size({'width': w, 'height': max(h, ph)}); pg.wait_for_timeout(200)
            pg.screenshot(path=str(H / 'png' / f'{name}_{w}.png'), full_page=full)
            pg.close()
    b.close()
