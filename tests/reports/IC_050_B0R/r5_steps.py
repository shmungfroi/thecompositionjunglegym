# R5: every tagged item has one level (1-7) and one step; steps rise with levels; property-by-property diff of tagged items old (0.49) vs new, except l/stp.
import json,sys
d=json.load(open(sys.argv[1]));new=d['new'];old=d['old'];bad=0
SK={'WARN'}  # song warnings: 'l' there is not a level
for n,v in new.items():
    if n in SK or 'err' in v: continue
    its=v['items'];nostp=[i['path'] for i in its if i.get('stp') is None];badl=[i['path'] for i in its if not(isinstance(i['l'],int) and 1<=i['l']<=7)]
    st=[i for i in its if i.get('stp') is not None];s=sorted(st,key=lambda i:i['stp']);rise=all(a['l']<=b['l'] for a,b in zip(s,s[1:]))
    # same step must not span two levels
    span={};[span.setdefault(i['stp'],set()).add(i['l']) for i in st];multi={k:v for k,v in span.items() if len(v)>1}
    print(f"{n:10} items {len(its):2} | no step {len(nostp):2} | level outside 1-7 {len(badl)} | steps rise with level {rise} | step spanning levels {multi or 'none'}")
    if nostp: print('      no step:',nostp[:12])
    if badl or not rise or multi: bad+=1
# s (semitones) unchanged
o={i['path']:i for i in old['IVS']['items']};print('interval semitones identical to 0.49:',all(o[i['path']]['s']==i['s'] for i in new['IVS']['items']))
# other property changes
for n in new:
    if n not in old or 'err' in new[n] or 'err' in old[n]: continue
    om={i['path']:i['props'] for i in old[n]['items']}
    for i in new[n]['items']:
        p=om.get(i['path'])
        if p is None: print('  new item',i['path']);continue
        for k in set(p)|set(i['props']):
            if k in('l','stp'): continue
            if p.get(k)!=i['props'].get(k): print(f"  CHANGED {i['path']}.{k}: {str(p.get(k))[:110]} -> {str(i['props'].get(k))[:110]}")
    lost=set(om)-{i['path'] for i in new[n]['items']}
    if lost: print('  items gone',n,lost)
print('sets failing:',bad)
