# prints, for each hunk in a unified diff, the changed segments of paired -/+ lines with context
import sys,difflib,re
lines=open(sys.argv[1],encoding='utf8').read().split('\n')
lo=int(sys.argv[2]) if len(sys.argv)>2 else 0; hi=int(sys.argv[3]) if len(sys.argv)>3 else 10**9
CTX=int(sys.argv[4]) if len(sys.argv)>4 else 50
i=0;minus=[];plus=[]
def flush():
    global minus,plus
    n=max(len(minus),len(plus))
    for j in range(n):
        a=minus[j][1] if j<len(minus) else ''
        b=plus[j][1] if j<len(plus) else ''
        ln=(plus[j][0] if j<len(plus) else minus[j][0])
        sm=difflib.SequenceMatcher(None,a,b,autojunk=False)
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag=='equal':continue
            print(f"  [d{ln}] …{a[max(0,i1-CTX):i1]}⟦{a[i1:i2]}⟧→⟦{b[j1:j2]}⟧{a[i2:i2+CTX]}…")
    minus=[];plus=[]
for n,l in enumerate(lines,1):
    if n<lo or n>hi: continue
    if l.startswith('@@'):
        flush();print(l[:40])
    elif l.startswith('-') and not l.startswith('---'): minus.append((n,l[1:]))
    elif l.startswith('+') and not l.startswith('+++'): plus.append((n,l[1:]))
    else: flush()
flush()
