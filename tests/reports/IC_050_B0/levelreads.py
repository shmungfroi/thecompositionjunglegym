import re,sys
src=open(sys.argv[1],encoding='utf8').read()
pat=re.compile(sys.argv[2])
starts=[0]
for m in re.finditer('\n',src): starts.append(m.end())
import bisect
A=int(sys.argv[3]) if len(sys.argv)>3 else 70
for m in pat.finditer(src):
    ln=bisect.bisect_right(starts,m.start())
    a=max(starts[ln-1],m.start()-A); b=min(m.end()+A, starts[ln]-1 if ln<len(starts) else len(src))
    print(f"{ln}: …{src[a:m.start()]}⟦{m.group(0)}⟧{src[m.end():b]}…")
