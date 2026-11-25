# R6: split rungs: content, pools, key bands, tells. Input from r6_ear_gen.js
import json,sys,collections
D=json.load(open(sys.argv[1]));M=D['meta'];C=collections.Counter
print('EARSLOT',M['EARSLOT']);print('EARSTAGE',M['EARSTAGE']);print('by place',M['byPlace']);print('next rung (internal)',M['next']);print('earBase mel13,cad4,mel5,cad2',M['base'])
print('cad keys rung2 maj',M['cadKeys']['maj2'],'min',M['cadKeys']['min2'])
def pa(rows,feat,ans):
    half=[rows[0::2],rows[1::2]];hit=0
    for tr,te in((half[0],half[1]),(half[1],half[0])):
        by=collections.defaultdict(C);tot=C(ans(r) for r in tr)
        for r in tr: by[feat(r)][ans(r)]+=1
        d=tot.most_common(1)[0][0]
        for r in te:
            c=by.get(feat(r));hit+=(c.most_common(1)[0][0] if c else d)==ans(r)
    return hit/len(rows),C(ans(r) for r in rows).most_common(1)[0][1]/len(rows)
print('\n== CADENCES')
for l in (1,2,3,4):
    rr=[r for r in D['cad'] if r['l']==l]
    ids={(r['k'],r['md'],' '.join(r['rns']),json.dumps(r['ch'])) for r in rr};models={(r['md'],' '.join(r['rns'])) for r in rr}
    print(f"rung {l}: n {len(rr)} | content rung {C(r['cl'] for r in rr)} | .rung {C(r['rung'] for r in rr)} | modes {dict(C(r['md'] for r in rr))} | keys {len({(r['k'],r['md']) for r in rr})} | answers {dict(C(r['a'] for r in rr))} | chords/len {dict(C(len(r['rns']) for r in rr))} | models {len(models)} | distinct sounding items {len(ids)} | options {C(json.dumps(r['opts'],ensure_ascii=False)[:90] for r in rr).most_common(1)[0][0]}")
F={'key':lambda r:r['k'],'n chords':lambda r:len(r['ch']),'second chord':lambda r:r['rns'][1],'first chord':lambda r:r['rns'][0],'lowest (exact)':lambda r:min(sum(r['ch'],[])),'highest (exact)':lambda r:max(sum(r['ch'],[])),
 'lowest+highest':lambda r:(min(sum(r['ch'],[])),max(sum(r['ch'],[]))),'span':lambda r:max(sum(r['ch'],[]))-min(sum(r['ch'],[])),'first bass':lambda r:r['ch'][0][0],'last bass':lambda r:r['ch'][-1][0],
 'first soprano':lambda r:r['ch'][0][3],'last soprano':lambda r:r['ch'][-1][3],'opening voicing':lambda r:tuple(r['ch'][0]),'key+n':lambda r:(r['k'],len(r['ch'])),'key+last bass':lambda r:(r['k'],r['ch'][-1][0]),
 'opening voicing rel. to key':lambda r:tuple((x-r['k'])%12 for x in r['ch'][0])+(r['ch'][0][3]-r['ch'][0][0],)}
for l in (2,4):
    rr=[r for r in D['cad'] if r['l']==l];print(f' tells rung {l} (held-out accuracy minus chance, points; margin 5):')
    for n,f in F.items():
        a,c=pa(rr,f,lambda r:r['a']);flag='  <-- OVER' if a>c+0.05 else ''
        note=' (degree of the last bass / key together IS the cadence, not a tell)' if n=='key+last bass' else ''
        print(f"    {n:28} {100*(a-c):+5.1f}{flag}{note}")
print('\n== MELODY')
SEMI={'d':0,'r':2,'m':4,'f':5,'s':7,'l':9,'t':11,'fi':6,'si':8,'te':10,'ta':10,'di':1,'ri':3,'li':10,'ra':1,'me':3,'se':6,'le':8}
def syl(s): return s.rstrip(",'")
for l in (4,5,13,6,7):
    rr=[r for r in D['mel'] if r['l']==l];nw=[r for r in rr if r['nw']];rv=[r for r in rr if not r['nw']]
    def sset(rows): return C(s for r in rows for s in set(map(syl,r['sol'])))
    print(f"rung {l} (place {M['EARSLOT']['mel'][l-1]}, level {M['EARSTAGE']['mel'][l-1]}): n {len(rr)} | content rung {dict(C(r['cl'] for r in rr))} | distinct ids {len({r['id'] for r in rr})} | new share {len(nw)/len(rr):.3f} | do keys {sorted(C(r['do'] for r in rr))} | metres {dict(C(r['metre'] for r in rr))}")
    print(f"     new items: variants {dict(C(r['v'] for r in nw))} | modes {dict(C(r['mode'] for r in nw))} | syllables used {sorted(sset(nw))} | final {dict(C(syl(r['sol'][-1]) for r in nw))}")
    print(f"     review items: variants {dict(C(r['v'] for r in rv))} | syllables {sorted(sset(rv))} | final {dict(C(syl(r['sol'][-1]) for r in rv))}")
    if l==13:
        noft=[r for r in nw if not ({'f','t'}&set(map(syl,r['sol'])))];print(f"     natural-minor items with neither fa nor ti (sound la-pentatonic): {len(noft)} of {len(nw)} = {len(noft)/len(nw):.1%}")
    if l==5:
        bad=[r for r in nw if {'f','t'}&set(map(syl,r['sol']))];print(f"     la-pentatonic items containing fa or ti: {len(bad)}")
print('\n== dictation keys by rung level (do pitch classes drawn)')
for l in (1,2,3,4,5,6,7,8,9,10,11,13):
    rr=[r for r in D['mel'] if r['l']==l];ks=sorted({r['do'] for r in rr});st=M['EARSTAGE']['mel'][l-1];print(f"  mel rung {l:2} place {M['EARSLOT']['mel'][l-1]:2} level {st}: {len(ks)} keys {ks} | allowed {sorted(M['LADKEYS'][str(st)])} | inside {set(ks)<=set(M['LADKEYS'][str(st)])} | all used {set(ks)==set(M['LADKEYS'][str(st)])}")
