#!/usr/bin/env python3
# context grep: ctx.py FILE REGEX [before] [after] [max]
import re,sys
f,pat=sys.argv[1],sys.argv[2];b=int(sys.argv[3]) if len(sys.argv)>3 else 100;a=int(sys.argv[4]) if len(sys.argv)>4 else 100;mx=int(sys.argv[5]) if len(sys.argv)>5 else 80
n=0
for i,line in enumerate(open(f,encoding='utf8'),1):
    for m in re.finditer(pat,line):
        n+=1
        if n>mx: continue
        print(f"{i}: {line[max(0,m.start()-b):m.end()+a].rstrip()}")
print('matches:',n)
