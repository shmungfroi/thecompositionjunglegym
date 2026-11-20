"""IC_REG_049 probe C4: independent exhaustive count of strict open-spaced V–vi voicings in the twelve major keys.
Written from the rule text only (no app code): voices B 40-60, T 48-67, A 55-74, S 60-79 (the app's SATB ranges), no crossing,
S-A and A-T within an octave, open spacing S-T > 12, complete triads, V with one 3rd (leading note not doubled), vi after V with its
3rd doubled (root and 5th once), the leading note rises a semitone in every voice, no parallel or contrary 5ths/8ves/unisons, no
overlap, no hidden 5th/8ve in the outer voices with a soprano leap, no leap of a 7th, a tritone or more than an octave.
Variants show how the count moves when one condition is relaxed."""
import itertools, collections
RG = {'B': (40, 60), 'T': (48, 67), 'A': (55, 74), 'S': (60, 79)}
def voicings(pcs, bass, *, open_=True, comp=True):
    out = []
    for b in range(*RG['B'][:1], RG['B'][1] + 1):
        if b % 12 != bass: continue
        for t in range(RG['T'][0], RG['T'][1] + 1):
            if t % 12 not in pcs or t < b: continue
            for a in range(max(t, RG['A'][0]), RG['A'][1] + 1):
                if a % 12 not in pcs or a - t > 12: continue
                for s in range(max(a, RG['S'][0]), RG['S'][1] + 1):
                    if s % 12 not in pcs or s - a > 12: continue
                    if open_ and s - t <= 12: continue
                    if not open_ and s - t > 12: continue
                    v = (b, t, a, s)
                    if comp and set(m % 12 for m in v) != set(pcs): continue
                    out.append(v)
    return out
def pair_ok(P, N, LN, var):
    for j in range(4):
        d = abs(N[j] - P[j])
        if d > 12 or d in (10, 11) or d == 6: return False
    for j in range(3):
        if N[j] > P[j + 1] or N[j + 1] < P[j]: return False
    for x, y in itertools.combinations(range(4), 2):
        i0, i1 = (P[y] - P[x]) % 12, (N[y] - N[x]) % 12
        if i0 == i1 and i0 in (0, 7) and P[x] != N[x] and P[y] != N[y]:
            if var.get('allow_contrary') and (N[x] - P[x]) * (N[y] - P[y]) < 0: continue
            return False
    io = (N[3] - N[0]) % 12; dS, dB = N[3] - P[3], N[0] - P[0]
    if io in (0, 7) and dS * dB > 0 and abs(dS) > 2 and (P[3] - P[0]) % 12 != io: return False
    for j in range(4):
        if P[j] % 12 == LN and N[j] - P[j] != 1: return False
    return True
def count(var):
    tot = 0; per = {}
    for k in range(12):
        V = [(k + 7) % 12, (k + 11) % 12, (k + 2) % 12]; vi = [(k + 9) % 12, k, (k + 4) % 12]; LN = (k + 11) % 12
        Cv = [v for v in voicings(V, V[0], open_=var.get('open', True)) if [m % 12 for m in v].count(LN) == 1]
        Cn = [v for v in voicings(vi, vi[0], open_=var.get('open', True)) if var.get('vi_any') or [m % 12 for m in v].count(k) == 2]
        n = sum(1 for P in Cv for N in Cn if pair_ok(P, N, LN, var)); per[k] = n; tot += n
    return tot, per
for name, var in [('approved: open, strict', {}), ('close spacing instead (S-T <= 12)', {'open': False}),
                  ('open or close', None), ('open, vi any doubling', {'vi_any': True}), ('open, contrary 5ths/8ves allowed', {'allow_contrary': True})]:
    if var is None:
        a, pa = count({}); b, pb = count({'open': False}); print(f'{name:40s} {a + b}'); continue
    t, per = count(var); print(f'{name:40s} {t}  per key {per}')
