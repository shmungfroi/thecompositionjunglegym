# R9: tagged items a 0.49 learner had at or below their stage that now sit ABOVE their migrated level (still reachable in the "Ahead of you" band).
import json,sys
d=json.load(open(sys.argv[1]));MIG={4:2,5:4,6:5}
for st,lv in MIG.items():
    out=[]
    for n,v in d['new'].items():
        if n in('WARN',) or 'err' in v or n not in d['old'] or 'err' in d['old'][n]: continue
        om={i['path']:i['l'] for i in d['old'][n]['items']}
        for i in v['items']:
            ol=om.get(i['path'])
            if ol is not None and ol<=st and i['l']>lv: out.append(f"{i['path']} ({ol}->{i['l']})")
    print(f"old Stage {st} -> Level {lv}: {len(out)} items now above the learner's level");print('   ',', '.join(out))
