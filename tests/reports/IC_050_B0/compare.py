import json,sys
D=json.load(open(sys.argv[1]))
old,new=D['old'],D['new']
bad=0
for n in new:
    b=new[n]
    if 'err' in b:
        a=old.get(n,{}); 
        # raw compare for un-evaluable literals: show l: tokens
        import re
        print(f"## {n} (raw, line {b['line']}): l tokens old={re.findall(r'[,{]l:(\d+)',a.get('raw',''))} new={re.findall(r'[,{]l:(\d+)',b['raw'])} stp={re.findall(r'stp:(\d+)',b['raw'])}")
        continue
    a=old.get(n,{'items':[]}); ai=a.get('items',[])
    print(f"## {n} line {b['line']}")
    for i,it in enumerate(b['items']):
        o=ai[i] if i<len(ai) and ai[i]['path']==it['path'] else next((x for x in ai if x['path']==it['path']),None)
        diffs=[]
        if o:
            for k in set(o['props'])|set(it['props']):
                if k in('l',):continue
                if o['props'].get(k)!=it['props'].get(k): diffs.append(f"{k}: {str(o['props'].get(k))[:40]} -> {str(it['props'].get(k))[:40]}")
        nd=[d for d in diffs if not d.startswith('stp:')]
        if nd: bad+=1
        print(f"  {it['path'][:60]:60} n={str(it.get('n'))[:34]:34} l {o['l'] if o else '-'}->{it['l']} stp={it.get('stp')} s={it.get('s')} {'OTHER PROPS CHANGED: '+'; '.join(nd) if nd else ''}{'' if o else ' (no old match)'}")
print('items with non-level property changes:',bad)
