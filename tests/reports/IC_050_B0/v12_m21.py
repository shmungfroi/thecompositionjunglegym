# V12 music21 check of the climb 9 minor-key dominant voicing by level, and of the corrected ii-V-i text claim.
import json,sys
from music21 import pitch, interval, key as m21key, chord, note
D=json.load(open(sys.argv[1]))
def P(n):
    n=n.rstrip('0123456789'); return pitch.Pitch(n[0]+n[1:].replace('♭','-').replace('b','-').replace('♯','#'))
print('major check (must be unchanged 13th/9th forms):',[(x['rn'],x['notes']) for x in D['majCheck']])
bad=0; seen=set()
for r in D['rows']:
    tonic={9:'a',2:'d',7:'g',0:'c'}[r['key']]; k=m21key.Key(tonic); root=P(r['root']); desc=[]; simple=[]
    for n in r['notes']:
        p=P(n); iv=interval.Interval(note.Note(root.name+'2'),note.Note(p.name+'4')); simple.append(iv.simpleName)
        deg=k.getScaleDegreeAndAccidentalFromPitch(p)
        desc.append(f"{p.name}: {iv.simpleName} above {root.name}, degree {deg[0]}{'' if deg[1] is None else '('+deg[1].name+')'}")
    exp=sorted(['M3','P5','m7','m2']) if r['lv']<7 else sorted(['M3','m6','m7','m2'])
    ok=sorted(simple)==exp and r['ext']==('7♭9' if r['lv']<7 else '7♭9♭13') and r['kind']=='7b9' and len(r['notes'])==4
    bad+=0 if ok else 1
    t=(r['lv']>=7,r['key'],r['start'])
    if t not in seen and r['lv'] in(4,7):
        seen.add(t); print(f"L{r['lv']} {tonic} minor, first chord {r['start']}: V={r['root']} symbol {r['sym']} form {r['form']} notes {r['notes']} -> {'; '.join(desc)} {'OK' if ok else 'BAD'}")
print('rows checked (levels 1-7 x 4 minor keys x 2 starts):',len(D['rows']),'bad:',bad)
k=m21key.Key('a'); E=note.Note('E3')
for nm,lab in [('F4','new text: b9 of E7'),('C5','new text: b13 of E7'),('F4','old text "le" in A minor (b6 of A)'),('G4','old text "ta" in A minor (b7 of A)')]:
    print(f"{lab}: {nm[:-1]} is {interval.Interval(E,note.Note(nm)).name} above E; degree {k.getScaleDegreeAndAccidentalFromPitch(pitch.Pitch(nm))[0]} of A minor")
