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
