# C_ENG_049 report: register 0.49 items C12, C23, C24, C25

Builder: Opus (engine). Branch `049-c-eng` (worktree `/home/claude/wt/c-eng`), from `049` @ `c49222f`. Not pushed, not merged.
Authority: Justin, 21 Nov 2026, decision log L101. All checks below are **self-checks** (builder's own; not independent).

## Commits

| commit | item |
|---|---|
| `ebeb940` | C24 earNumFn reads numerals as Analysis does; unit_test C9 extended |
| `99d5c82` | C12 + C23 rung 1: complete chords only, close spacing for all five models, weights refitted; earlab_test C/D, earlab_items_test K/K2 |
| `2c1ba60` | C25 strict first-inversion major triads; EAR23W regenerated; doubling checks in earlab_test and earlab_items_test |
| (this commit) | this report |

The C24 commit was self-checked alone (unit_test on that tree: 1,099 checks, 0 failures). The C12 + C23 commit was not run on its own; all
suites below were run on the final tree.

## C12: "always use the complete chord" (done; supersedes L95)

- `EARR1OPT.inc` is now `false` (it was `true` under L95, "incomplete tonic on"). The incomplete V–I entries stay in `earR1Pool` (flagged
  `inc`) so the switch still works, but no entry in use is incomplete. New helper `earR1Use(p,o)` applies the switches in the fit and in
  `earSATBPair`.
- Self-check (20,000 seeded rung 1 items, seed 53, held-out best guess vs chance): "final chord complete" **+15.9 points before → −1.0 after**
  (0 of 20,000 items now end incomplete; before, 3,262 did, all perfect).
- New checks: earlab_test C (every chord complete, a tell check on completeness), D (no incomplete entry in use, `inc` and `open` both off);
  earlab_items_test K (each chord complete; completeness tell), K2 (no incomplete chord with the soprano switch on or off).

## C23: close spacing at rung 1, all five models together (done)

- `earR1Pool` no longer drops close voicings (soprano within an octave of the tenor); close entries are marked `cl`. New switch
  `EARR1OPT.open` (default `false`; `true` restores open-only). It applies to all five models (V–I, IV–I, I–V, IV–V, V–vi) at once.
  Strict SATB is unchanged: the same chord and pair rules, upper voices within an octave, vi doubles its 3rd after V.
- Refit (`earR1Fit`): the spacing of both chords (open/close each) is a new balanced feature, and a 3 % mix with the plain draw inside each
  model (`EARR1OPT.mix=.03`) keeps every strict voicing in use (without it, 23 of the 108 V–vi voicings fell to zero weight).
- Pool (twelve keys): V–I 170 (complete), IV–I 764, I–V 764, IV–V 288, **V–vi 108** (was 28). App V–vi pool = independent exhaustive
  enumeration (`vvi_enum(k, open_only=False)`): **108 / 108**, all 108 carry weight. Entries in use with a close chord: V–I 95, IV–I 124,
  I–V 87, IV–V 72, V–vi 80. Distinct items drawn: interrupted 101 in 20,000 draws, 103 in the items test's 2,000 + register grid.
- Tells, rung 1 (self-check, 20,000 items, seed 53, held-out, points above chance; before = 049 @ c49222f):

| feature | before | after |
|---|---|---|
| spacing of first chord (open/close) | −1.0 (all open) | −0.6 |
| spacing of last chord | −1.0 (all open) | −0.8 |
| spacing of both chords | −1.0 | −0.8 |
| final chord complete | +15.9 | −1.0 |
| lowest + highest note, exact pair | +1.1 | +1.6 |
| span | +0.5 | +0.9 |
| first / last bass | +2.5 / +3.2 | +2.8 / +2.0 |
| first / last soprano | +0.7 / +1.7 | +0.7 / +2.0 |
| key | −0.1 | 0.0 |
| soprano solfa path (content, switch off) | +56.2 | +66.5 |
| tenor–soprano distance, first chord, exact (info) | +12.8 | +11.5 |
| tenor–soprano distance, last chord, exact (info) | +18.6 | +29.6 |

  Close-spaced items per answer (items test): perfect 53.8 %, plagal 53.5 %, imperfect 56.1 %, interrupted 55.8 %.
- New tell checks (margin 5 points): earlab_test C, rung 1: spacing of the first chord, the last chord, every chord, completeness (4 new;
  67 tell checks in all). earlab_items_test K: spacing first / last / both, final chord complete (4 new; 79 tell checks in all).
  The open-spacing assertions in K and K2 were replaced by "upper voices within an octave" and "complete chords".

## C25: rung 2 I⁶ doubling (done; wider than the 6 named)

- `earStrictChord` (strict rungs 2–3 and the bass drill): a major triad in first inversion must be complete and double its root or 5th,
  never its 3rd; vi / VI excepted (as specified). This is a hard rule.
- **Scope note for Justin.** The rule as specified ("no doubled 3rd in a major-chord first inversion") also re-voices complete I⁶ chords with a
  doubled 3rd, not just the 6 incomplete ones IC_REG_049 S1 named. Self-check on the full rung 2 grid (9,600 entries): before, **1,045 entries
  with a doubled 3rd** in I⁶ (1,036 complete; 9 with no 5th: the 6 named, 3rd doubled, and 3 with the 3rd tripled); after, **0**. 1,045 rung 2
  grid entries (404 distinct realisations) changed; every one of them had the fault, no other entry changed. Rung 3: 0 changed (it already
  had none). If Justin prefers the textbook allowance for a doubled 3rd in an inner voice, the rule narrows to "outer voices only" or
  "complete only".
- EAR23W regenerated with `tests/gen_cad23_weights.py` (index length unchanged; rung 2 weights changed because the realisations did; rung 3
  string identical). Rung 2 tells after (earlab_test, 5,000 items): exact pair 24.5 % vs 25.5 % (C_THEORY reported 24.3 %); span 25.7 % vs
  25.5 %. All 9,600 / 6,600 grid points still have a strict realisation (0 empty).
- New checks: earlab_test `dbl_check` (music21 reading) inside `vl_check` (sections A and B: 720 first-inversion major chords) and on all
  15,000 generated cadence questions in section C (2,178 chords); earlab_items_test `ic_errors` (section V runs it over every rung 1, 2, 3
  realisation the drill can draw and every bass progression × key × register).

## C24: earNumFn (done)

- `earNumFn` now reads a numeral through `parseRoman` + `analyse()` in C major / C minor (memoised): outside the key → X (analyse 'C'),
  respecting case, accidental, quality and mode; MD and D cases as before; secondary chords X.
- One strict refinement: `analyse()` tests the key by pitch class only, so it calls minor **vi** (A♭–C♭–E♭ in C minor) diatonic T because C♭
  sounds as the leading note B. earNumFn also checks spelling (every note on its own degree; in minor the 7th may be raised) and says X.
  **Flag:** `analyse()` itself still says T for that chord (outside my scope; not changed).
- Every numeral the Ear Lab currently uses (23, all rungs and drills) maps exactly as before: nothing on screen changes today. Changed
  readings include major i, II, III, VI, iv, ii°, iiø7, vii, I7, IV7, III+ → X; minor I, II, ii, iii, IV, vi, vii, I7, IV7, ii7, viiø7 → X;
  Vsus4 / V5 → D (were T).
- unit_test C9 extended: 35 more numerals (19 major, 16 minor) × 4 keys, root position and inverted, against the expected function and
  analyse() (minor vi the one listed exception). 1,099 checks, 0 failures.

## Tests (final tree, one at a time)

| suite | result |
|---|---|
| earlab_test | pass: 0 failures, 67 tell checks, V–vi 108 / 108, fixture coverage 732 / 732 |
| earlab_items_test | pass: 0 failures, 79 tell checks, strict rules on every realisation (rung 1 2,398; rung 2 9,600; rung 3 6,600; bass 1,980) |
| unit_test | pass: 1,099 checks, 0 failures |
| content_lint | pass |
| earlab_r2_test (extra) | pass: 1,666 checks, 0 failed |
| earlab_ui_test (extra) | 469 checks, 2 failed (FR-19 letter-names checkbox size at 1440 and 390 px); the **same 2 fail on 049 @ c49222f**, unrelated |

Not run: pageerrors_test, layout and the other suites (not asked; no UI change).

## Changed tests (to read before merging)

- earlab_items_test K2: the soprano-path ceiling with `RUNG1_SOP_BALANCE` off moved **from 86 % to 94 %** (measured 91.8 %). Cause: C12. A
  complete V–I can only have so–so, ti–do or re–mi on top (the incomplete tonic gave so–mi and re–do), so the top line says more. With the
  switch on it reads 83.5 %. The switch is still off (Justin has not ruled); turning it on is the fix if this matters.
- earlab_items_test K / K2: the open-spacing assertions were replaced (C23 makes close spacing legal).
- earlab_test D: the C4 check now compares with the open-or-close enumeration and has a floor of 100.

## Not done / uncertain (for Justin)

1. **Exact tenor–soprano distance of the last chord** (rung 1) predicts the answer 55 % vs 26 % (+29.6; it was +18.6 open-only). Open/close
   is balanced, but the exact semitone distance mostly follows each cadence's chord content (vi with a doubled 3rd, the tonic's
   spacing). I tried balancing it: it fell to about +14 but the register pair and span rose to about +7 (exact table), so I left it out.
   Not checked by any suite (reported as info in earlab_items_test). Needs a ruling: content or tell.
2. Soprano solfa path at rung 1 rises with C12 (above).
3. Rungs 2–3 spacing pattern of every chord predicts +6.7 (rung 2) and +13.8 (rung 3) points (info line in earlab_test). It was the same
   on 049 (+7.9 / +13.8), so it is not new and was not in scope.
4. C25 re-voiced 1,045 rung 2 entries, not 6 (scope note above).
5. `analyse()` minor vi reading (C24 note).
6. No listening check.

## C31–C35 (Justin 21 Nov 2026, decision log L108)

Builder: Opus (engine), same branch and worktree. All checks below are **self-checks** (the builder's own, not independent).
"Before" = this branch at `fa5fe9d` (C12/C23/C24/C25 in place). Sampled tells: 20,000 seeded questions per rung (seeds 20261122–4,
Lehmer RNG, as the IC used), held-out best guess minus chance, in points. "Exact" tells are computed from the weights themselves
(the limit of the sampled measure as the sample grows; tests/cadweights_lp.py explains it).

| commit | content |
|---|---|
| `2578727` | C31–C35 code and tests (index.html, tests/cadweights_lp.py, tests/gen_cad1_weights.py, gen_cad23_weights.py, earlab_test, earlab_items_test, unit_test) |
| (this commit) | this section |

### Method change (read before merging)

The browser's iterative fit (IPF) could not balance features whose values the chords themselves split between answers (the top line),
and at rung 3 minor it did not converge once spacing and completeness were added. Both tables are now fitted offline by **linear
programming** (scipy/HiGHS) in `tests/cadweights_lp.py`:
1. caps on the register-type features; 2. the listed residue features made as small as possible; 3. the weights moved as little as
possible (L1) from an anchor (rung 1: the old earR1Fit weights; rungs 2–3: the plain draw), so variety is kept. The plain-draw mix stays
in every weight (rung 1 3 %, rungs 2–3 10 %), so every strict voicing keeps weight > 0.
- **New table `EAR1W`** (rung 1, 2,094 entries × 3 characters) written by `tests/gen_cad1_weights.py`; `earR1Table()` reads it,
  `earR1Fit()` stays as the fallback when the table is stale and as the generator's anchor. `RUNG1_SOP_BALANCE` on still gives the 0.48 fit.
- `EAR23W` is now written by `tests/gen_cad23_weights.py` with the LP; `earR23Fit` stays in the app as the stale-table fallback.
- The two generators need numpy + scipy (the suites do not).

### C31 rung 1 top line and tenor–soprano gap (Must)

Floors (exact; the least each feature can reach on its own from the strict pool, with the 3 % mix): soprano degree of the last chord
+25.0, of the first chord +25.1, soprano line (both degrees) +38.1; tenor–soprano gap last +0.6, first +0.1. The 25-point floors are forced
by the chords: the last chord is I, V or vi and V (so ti re) and vi (la do mi) share no note, so imperfect and interrupted can never share a
final top note; the same holds for the first chord (V, IV or I).

Jointly, with the register held (exact caps), the pool cannot reach those floors together: with every register feature ≤ 4 points the
soprano line cannot go below about **+55**, and the last chord's tenor–soprano gap cannot go below about **+17** while the last soprano degree
is at its floor (the span and the exact lowest/highest pair are what bind; measured by LP, scratch). At register ≤ 3 the shared-chord
pairs could not be held (perfect vs plagal rose to +13), so the register cap is 4 (exact), and the K tells are now measured on 10,000 items
so sampling noise stays inside the 5-point margin.

| feature (rung 1) | before (sampled) | after (sampled) | after (exact) | floor alone (exact) |
|---|---|---|---|---|
| soprano line (both degrees) | +66.7 | **+56.7** | +56.8 | +38.1 (≈ +55 with register held) |
| soprano degree, last chord | +41.4 | **+24.8** | +25.3 | +25.0 |
| soprano degree, first chord | +35.2 | **+27.6** | +27.8 | +25.1 |
| soprano motion (semitones) | +34.1 | +28.3 | | |
| tenor–soprano gap, last chord | +29.9 | **+20.1** | +20.6 | +0.6 (≈ +17 with the rest held) |
| tenor–soprano gap, first chord | +11.3 | **+7.4** | +7.3 | +0.1 |
| perfect vs plagal, final I's top degree (chance 50 %) | 85.2 % | **54.2 %** | 53.8 % | 50 % |
| perfect vs plagal, final I's tenor–soprano gap | 85.8 % | **54.5 %** | 54.0 % | |
| perfect vs interrupted, V's top degree | 61.7 % | **54.2 %** | 54.0 % | |
| perfect vs interrupted, V's tenor–soprano gap | 60.8 % | **53.6 %** | 54.0 % | |
| perfect vs plagal, exact final I voicing | (IC +38.7 exact) | +5.8 (items test) | +7.0 | +0.4 |
| perfect vs interrupted, exact V voicing | 64.3 % (IC) | +5.3 (items test) | +6.1 | +0.3 |
| register: lowest+highest / span / first, last bass / first, last soprano / key | +1.8 / −0.1 / +2.4, +2.1 / +1.5, +2.0 / +0.4 | +3.7 / +3.9 / +3.0, +3.8 / +3.0, +3.3 / +3.5 | ≤ +4.0 each | |
| spacing of both chords (C32 definition) | +5.9 | +3.5 | | |
| final chord complete | −0.2 | −0.2 | | |

So: **every register, spacing and shared-chord top-note/gap feature is ≤ 5 points; the residues** are the soprano line (+56.7), the first
and last soprano degree (+27.6 / +24.8; the last is at its floor), the last chord's tenor–soprano gap (+20.1) and the first chord's (+7.4),
and the exact voicing of a shared chord (+5–7). The register tells rose from about +2 to about +3.5 (still under 5): that is the cost of
the top-line balance. Variety: all 108 V–vi voicings (and every other strict voicing) have weight > 0; effective number of voicings per model
V–I 74, IV–I 88, I–V 49, IV–V 50, V–vi 58 (before 64 / 113 / 72 / 68 / 59). Complete chords (C12) and close spacing for all five models (C23)
unchanged; close-spaced share by answer 37–44 % (the C32 boundary moved the exact octave to open).

New checks, earlab_items_test K: soprano line, final and first soprano degree, soprano motion, both tenor–soprano gaps (each against its
exact level + 3 points), perfect/plagal and perfect/interrupted soprano degree and gap (5-point tells), exact shared-chord voicing (exact
level + 3). K2: the default (EAR1W) must now tell less than the switch on (it does: path 80.6 % vs 84.8 %, last degree 49.5 % vs 61.0 %);
the path ceiling comes down from 94 % to 84 %.

### C32 close spacing = soprano–tenor less than an octave

`const EAR_CLOSE_LT=12` and `earClose(v)` (close when S–T < 12; exactly an octave is open), used by the rung 1 pool (`cl`), the rung 1 fit,
`earSATB`'s open-only option, both generators and the tests (earlab_test reads `earClose`, earlab_items_test reads `EAR_CLOSE_LT`).
earlab_test C has a boundary check (12 → open, 11 → close). Rung 1 spacing of both chords under this definition: **+5.9 → +3.5** (sampled;
IC measured +6.1). Changing the constant needs both generators rerun.

### C33 rungs 2–3 spacing pattern and completeness

- Cause of the rung 3 completeness tell: the cadential 6/4 model I⁶₄–V7–I always ended on the incomplete tonic (100 % of its grid
  points), which no weighting can fix. `earSATB` (strict) now prefers a complete final root-position tonic whenever one can be reached and
  falls back to the incomplete one otherwise: all rung 2 and rung 3 finals that can be complete now are (rung 3 major imperfect keeps 7 %
  final V without its 5th, not a tonic). No grid point lost its realisation (9,600 / 6,600, 0 missing).
- EAR23W regenerated by LP with the spacing pattern (earClose) and final completeness added to the balanced features (smallest common cap
  per mode: rung 2 1.0 / 1.1, rung 3 3.2 / 3.1 points; cap used max(3, that + 0.5)).

| tell (sampled) | rung 2 before → after | rung 3 before → after |
|---|---|---|
| spacing pattern, every chord (C32 definition) | +13.2 → **+2.7** | +4.8 → **+2.8** |
| same, old ≤ 12 definition (as the IC measured) | +8.3 → +10.6 | +15.1 → +14.7 (not the definition in force) |
| final chord complete | +2.9 → **−0.4** | +8.1 → **−0.1** |
| lowest+highest / span | −0.3 / 0.0 → +1.6 / +1.5 | +3.7 / +3.7 → +3.0 / +2.4 |

New checks, earlab_test C: spacing of every chord and "mode and spacing" at rungs 1–3 (were rung 1 only), final chord complete and "mode and
final chord complete" at rungs 1–3; 76 tell checks in all (67 before).

### C34 root-position triads with a doubled 3rd and no 5th

`earStrictChord`: a root-position triad (any strict-item chord: IV, vi, III, VI, a final I or i …) may not double its 3rd and leave out
its 5th; vi/VI after V keep their doubled 3rd with the 5th. Before: 273 rung 2 grid entries (IV in I IV ii⁶ V I …) and 304 rung 3 (final i
after V7, root and 3rd doubled) had one; after: 0 / 0, no grid point unrealised; distinct realisations rung 2 3,481 → 3,374, rung 3 1,509 →
1,495 (before the C33 completeness change). New checks: earlab_test `dbl_check` (22,140 root-position triads in sections A, 46,986 in the
15,000 generated questions of section C), earlab_items_test `ic_errors` (every rung 1, 2, 3 realisation and every bass progression × key ×
register).

### C35 analyse() checks spelling

`analyse()` now calls a chord diatonic only if every note is spelled on its own scale degree (raised 7th allowed in minor), and borrowed
only if spelled in the parallel key. The 17 minor numerals read as the Ear Lab map does (X / 'C'); unit_test C9 has them (16 added, vi was
there) × 4 keys, root and inverted, with the old minor-vi exception removed: **1,163 checks, 0 failures** (1,099 before).
- Analysis scores: every harmony label in scores/meta.json (135, all ten scores) read through parseRoman + analyse() before and after:
  **0 change**. (The scores' colours are stored in meta.json by tests/numeral_reread.py, so the app's analyse() does not recolour them anyway.)
- Wider scan (every root letter with ♮, ♭, ♯, 𝄫, 𝄪 × every quality × 24 keys, 19,320 chords): 228 change function. 132 are the 11
  spelled-outside-the-key qualities per minor key (ii°7, iv°, ivø7, iv°7, V+, vi, vi°, vi add9, vi6, vi°7, VII+ on enharmonic roots: T/PD/D →
  C, correct by spelling); 96 are augmented-6th chords on odd roots (e.g. "It+6" built on G in C, which sounds as V7 but is spelled with E♯),
  D/MD → C, which is right for an augmented sixth. 132 more keep their function and only lose the "borrowed" flag (e.g. iv° with C♭ in C
  major is not borrowed from C minor). The numerals the app itself offers (diatonic lists, colour chords, Ear Lab) are unchanged.

### Tests (final tree, run one at a time)

| suite | result |
|---|---|
| earlab_test | pass: 0 failures, 76 tell checks, C34 22,140 + 46,986 triads, V–vi 108 / 108, fixture coverage 732 / 732 |
| earlab_items_test | pass: 0 failures, 91 tell checks (rung 1 tells on 10,000 items), strict rules on every realisation (rung 1 2,398; rung 2 9,600; rung 3 6,600; bass 1,980) |
| earlab_r2_test | pass: 1,666 checks, 0 failed |
| unit_test | pass: 1,163 checks, 0 failures |
| content_lint | pass |
| analysis_engrave_test | pass: 0 failures |

One earlab_items_test run ended with "Target crashed" (machine load) and was rerun. Not run: earlab_ui_test, pageerrors, layout and the
other suites (no UI change).

### Not done / for Justin

1. **Residues (C31)**: the soprano line (+56.7), last chord's tenor–soprano gap (+20.1) and exact shared-chord voicing (+5–7) stay above
   5 points; the floors and the joint limits are above. Lowering them further raises the register tells past 5. If Justin wants the gap
   or the line lower, the trade is the register cap (e.g. 5 instead of 4).
2. Rungs 2–3 also show a last-chord tenor–soprano gap tell (+20.1 / +18.6) and last soprano degree (+25.9 / +19.8; the latter is the
   cadence content). Not in C33's scope; not balanced.
3. The generators need scipy; the method changed from IPF to LP (above).
4. The C33 completeness fix changes realisations (complete final tonic preferred) at rungs 2 and 3, not only weights.
5. No listening check. C25 strict rule unchanged (follow-up open with Justin).
