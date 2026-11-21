# IC_C_ENG_049: independent check of C12, C23, C24, C25 (branch 049-c-eng)

**Independent check.** The checker did not build this work. Scope: commits `ebeb940..34871a3` against base `c49222f`. `index.html` was not edited.
The builder's report (`tests/reports/C_ENG_049_report.md`) was used only to find claims. Every number below was measured again by the checker.

Method. The app was loaded headless through `tests/harness` (the way the repo tests do it). The checker took four things from the app:
- the rung 1 pool (`earR1Pool`, `earR1Use`, `earR1Weights`);
- the rung 2 and rung 3 grids (`earR23Pool`, with the EAR23W weights);
- 20,000 seeded questions per rung from `earGen('cad', l)`, seeds 20261122, 20261123 and 20261124 (Lehmer RNG, as in the repo tests);
- `earNumFn` and `analyse()` for 678 numerals.

The same dump was taken from the base `index.html` (`c49222f`) for before-and-after numbers.

Every realisation was then checked by **the checker's own strict SATB checker**, written in Python. It does not call `checkSATB`, `earStrictChord` or `earStrictPair`. Chord spelling comes from music21 10.5 `RomanNumeral`; the voice-leading arithmetic was written for this check. The checker tests:

- ranges: B E2–D4, T C3–G4, A G3–D5, S C4–G5;
- crossing;
- S–A and A–T within an octave;
- the right bass note, no foreign notes, complete chords;
- no doubled leading note, secondary leading note or 7th; a 6/4 doubles its bass;
- no parallel or contrary 5ths, 8ves or unisons in any pair of voices;
- no direct 5th or 8ve in the outer voices with a soprano leap;
- no overlap;
- no leap of a 7th, a tritone, an augmented 2nd, or more than an octave;
- the leading note rises (in an inner voice it may fall to the 5th of a root-position I), and always rises into vi;
- 7ths fall by step, and secondary leading notes rise.

Tell measurement uses held-out best-guess accuracy (fit on one half, score on the other, both ways) against chance (the most common answer). Scripts were in `/tmp/ic049` (scratch; not committed).

## Verdicts

| item | verdict |
|---|---|
| C12 complete chords at rung 1 | **PASS** |
| C23 close spacing at rung 1, strict, V–vi pool ≥ 100, no spacing tell | **PASS** (one Should: the spacing boundary) |
| C23 V–vi pool = 108, all strict | **PASS** (108 = 108) |
| C25 no I⁶-type major chord with a doubled 3rd and no 5th; strict kept | **PASS** (the wider rule is also sound; see section 4) |
| C24 numeral → function, outside the key = X | **PASS**, with a flag: earNumFn and analyse() differ on 17 minor-key numerals, not 1 |
| Ladder rule (≤ 5 points over chance), rung 1, register, spacing, completeness | **PASS** |
| Ladder rule, rung 1, soprano line and tenor–soprano distance | **FAIL as the rule is written.** These tells existed before but grew with this change; needs a ruling |
| Ladder rule, rungs 2–3 spacing pattern | **FAIL as written.** The same failure was there before (not introduced) |
| Repo suites | **PASS**: unit_test 1,099 checks, 0 failures; earlab_test 0 failures; earlab_items_test 0 failures |

Note on earlab_items_test: the first run, alongside the other two suites, ended with a Chrome `TargetClosedError` (load on the machine). Run again on its own, it passed with 0 failures.

## 1. Strict SATB on every realisation (the checker's own rules)

| set | realisations | faults found |
|---|---|---|
| Rung 1 pool entries in use (`earR1Use`) | 2,094 (V–I 170, IV–I 764, I–V 764, IV–V 288, V–vi 108) | **0** |
| Rung 1 pool, all entries incl. switched-off | 2,398 | 304, all "incomplete final I (no 5th)" in V–I, all marked `inc` and **not in use** |
| Rung 1 questions, 20,000 | 20,000 | **0** |
| Rung 2 grid (EAR23W) | 9,600 (3,481 distinct) | 0 parallels, directs, overlaps, range, spacing, leading-note or 7th faults. Incomplete triads only (below) |
| Rung 2 questions, 20,000 | 20,000 | the same |
| Rung 3 grid / questions | 6,600 / 20,000 | the same; rung 3 questions are **identical to base** (20,000 / 20,000) |

Doubling profile at rung 1 (in use): vi after V doubles its 3rd in all 108 V–vi (the textbook treatment). Root-position I, IV and V double the 5th in 372, 262 and 227 entries; all others double the root. No doubled leading note and no doubled 3rd in a major triad.

Incomplete triads at rungs 2–3. These were there before and are outside C12, which is rung 1 only. They are not errors in strict style, but some are weak:
- final I/i after V7 with a tripled root (standard): 611 per 20,000 questions at rung 2 and 1,351 at rung 3;
- **mid-phrase root-position triads with a doubled 3rd and no 5th**, at rung 2: vi after I 122, IV after iii 98, III after i 52, IV after I 46, VI after i 39. That is **376 of 20,000 questions (1.9 %)**; it was 483 before, and C25 removed 64 of them, all I⁶;
- a final V with no 5th: 24 per 20,000 (rung 2);
- rung 3: final i after V7 with root and 3rd each doubled and no 5th, 1,087 per 20,000.

## 2. C12 and C23 at rung 1

- C12: **0 of 20,000** questions have an incomplete chord (base: 3,251, all perfect). `EARR1OPT` = `{inc:false, open:false, mix:0.03}`.
- C23: close spacing (S–T ≤ 12, the app's definition) is used for all five models. In-use entries with at least one close chord: V–I 95, IV–I 547, I–V 547, IV–V 194, V–vi 80. Questions with a close chord, by answer: perfect 55.8 %, plagal 55.6 %, imperfect 56.7 %, interrupted 54.1 %.
- **V–vi pool.** The checker enumerated every strict V–vi in all 12 keys, open or close, with vi doubling its 3rd: **108 = the app's 108**, with no difference either way. All 108 have weight; 102 distinct came up in 20,000 questions. Six more appear if the bass may go up to D4 (each is B3/C4 → C♯4/D4). The app's rung 1 bass ceiling is C4, so they are rightly out. Another 63 strict V–vi voicings double the root of vi; they are excluded by design (Could, below).

## 3. Tells (20,000 seeded questions per rung; accuracy vs chance; points over chance)

Rung 1 (chance 25.2 %):

| feature | after | before (c49222f) |
|---|---|---|
| final chord complete | 24.0 (**−1.2**) | 40.3 (+15.1) |
| spacing, first chord (S–T ≤ 12 = close) | 24.5 (−0.7) | 24.0 (all open) |
| spacing, last chord | 24.5 (−0.7) | 24.0 |
| spacing, both chords | 25.0 (−0.2) | 24.0 |
| spacing, both chords, **Kostka–Payne boundary (close = S–T < 8ve)** | 31.3 (**+6.1**) | 24.0 |
| last-chord doubling pattern | 24.0 (−1.2) | 40.3 (+15.1) |
| lowest / highest note | 26.5 / 26.3 (+1.3 / +1.1) | 26.3 / 25.7 |
| lowest + highest pair / span | 27.3 / 25.7 (+2.1 / +0.5) | 26.2 / 24.0 |
| first / last bass | 27.9 / 27.3 (+2.7 / +2.1) | 27.9 / 28.7 |
| first / last soprano (pitch) | 26.3 / 26.7 (+1.1 / +1.5) | 26.1 / 27.0 |
| key | 25.0 (−0.2) | 24.8 |
| **soprano line (degrees)** | 91.5 (**+66.3**) | 81.8 (+56.6) |
| soprano last degree | 66.6 (+41.4) | 55.6 (+30.4) |
| soprano motion (semitones) | 59.1 (+33.9) | 54.9 (+29.7) |
| **tenor–soprano semitones, last chord** | 55.3 (**+30.1**) | 43.2 (+18.0) |
| tenor–soprano semitones, first chord | 36.3 (+11.1) | 38.0 (+12.8) |
| tenor–soprano, both chords | 67.7 (+42.5) | 49.1 (+23.9) |

Answers that share a chord (chance 50 %). These show what a voicing gives away beyond the chords themselves:

- **perfect vs plagal (both end on I).** From the final I's soprano degree: **85.0 %** (base 64.9 %). From its tenor–soprano distance: 85.5 % (base 64.9 %). Spacing 49.1 % and doubling 49.7 % are at chance.
- Cause: perfect plays so–so in 73 % of questions and re–mi in 1 %, yet the pool has the three V–I soprano paths about equally (56 / 59 / 55). Plagal ends on mi in 58 % and on so in 3 %. The refit, not the theory, sets these shares. The tenor–soprano distance tell is mostly the same information as the soprano degree.
- perfect vs interrupted (both start on V), from V's voicing: soprano degree 59.8 % (base 59.6 %); exact V voicing 64.3 % (base 62.1 %).
- plagal vs IV–V (both start on IV): at chance.

Rungs 2–3, spacing pattern of every chord (chance 25.5 % / 18.5 %):

| feature | rung 2 after / before | rung 3 after / before |
|---|---|---|
| spacing pattern, all chords | 33.4 / 33.1 (**+7.9**) | 33.5 / 33.5 (**+15.0**) |
| spacing pattern, 4-chord items / 5-chord items | +7.5 / +8.8 | n/a / +15.0 |
| spacing, last chord | 27.2 (+1.7) | 21.5 (+3.0) |
| final chord complete | 28.7 (+3.2) | 27.8 (**+9.3**) |
| tenor–soprano, last chord | 44.6 (+19.1) | 38.9 (+20.4) |
| lowest + highest pair | 25.4 (−0.1) | 21.8 (+3.3) |

## 4. C25: is a doubled 3rd in a major first-inversion triad an error?

What the check found: C25 removes every doubled 3rd from major first-inversion triads at rungs 2–3:
- **0** in the 9,600 rung 2 grid entries and in 20,000 rung 2 questions;
- before: 2,924 such chords in 20,000 questions, 64 of them with no 5th (the named fault). The doubled 3rd sat in T 1,586, A 788, S 549, A+S 1;
- all 9,600 / 6,600 grid points still realise;
- rung 2 distinct items: 2,386 now, 2,366 before;
- rung 3 is unchanged.

Pedagogy:
- **The textbooks disagree.** Aarden & von Hippel's survey of harmony texts (Music Theory Online 10.2, 2004, Table 2.1.3a) lists the first-inversion rules:
  - "root above fifth" or "no third": 10 theorists each (Rimsky-Korsakov, Tchaikovsky, Stainer and others);
  - "depends on quality": 8;
  - "double the soprano": 5, Aldwell & Schachter among them, with quality dependence;
  - "double the third": 1 (DeLone);
  - no rule: Kostka & Payne. Their practice, as also taught in the Iowa State *Comprehensive Musicianship* text, is that any non-tendency tone may be doubled in a major or minor 6 chord.
- **Common school rule sets are stricter.** Open Music Theory and Puget Sound *Music Theory for the 21st-Century Classroom* both teach "do not double the bass" in first inversion. The exceptions are ii°6 / vii°6 (double the bass) and consecutive 6 chords, which alternate.
- **NSW.** The checker found no NESA HSC document that sets a four-part doubling rule. It did not look up an AMEB source either, so NSW classroom practice is not cited here.
- **Conclusion.** A doubled 3rd in a major 6 chord is **not an error** in common-practice style. Most strict pedagogy treats it as **a weakness to avoid in student models**. It is least objectionable in an inner voice reached by step or contrary motion, and most audible as an outer-voice octave (bass and soprano). The 6 named chords (3rd doubled, **no 5th**) are a real fault: incomplete and with a doubled 3rd at once.
- **Recommended rule (precise):** "In a major triad in first inversion, the chord is complete, and the root or the 5th is doubled; the 3rd (the bass) is never doubled. (vii°6 and ii°6 double the bass; vi/VI after V are root position and keep their own rule.)" This is the builder's rule. It matches the majority of strict texts, costs no variety (above), and is the safest model for Stage 6 students. **Keep it.**
- **Alternative, if Justin wants the textbook latitude:** "the 3rd may be doubled only in the tenor or alto, never in the soprano, and only with the 5th present." Applied to the base, that would bring back about 2,374 of the 2,924 chords. It also needs a check that the doubled 3rd is reached by step or contrary motion.

## 5. C24: numeral → function

- No numeral the Ear Lab uses changed reading (16 numerals across EARRN and the bass drill, base vs new).
- Of 678 numerals tried (3 accidentals × 14 cases × 8 suffixes × 2 modes, plus secondaries), earNumFn and its inverted form (`:1`) always agree.
- The builder lists **only minor vi** where earNumFn ≠ analyse(). The checker found **17**, all in minor and all for the same reason: analyse() tests the key by pitch class, so a note spelled outside the key passes if it sounds like a harmonic-minor note. They are:
  - with C♭ = B: vi, vi°, vi°7, VI°, VI°7, iv°, IV°, ivø7, IVø7, iv°7, IV°7, ii°7, II°7;
  - with D♯ = E♭: V+, v+;
  - with D♯ / F𝄪: vii+, ♯VII+.

  earNumFn says X for all 17, which is right by spelling; analyse() says T, PD or D. None is used today.
- Case and mode are respected: major iv, i, II, III, VI, vii → X; minor I, IV, ii, iii, vi → X; minor III+ stays T.
- Two readings follow earlier decisions rather than a strict reading of C24. Both match Analysis:
  - **major vii°7 (B–D–F–A♭)** stays D, although its A♭ is borrowed from the minor (C9: "vii°7 stays D");
  - **major ♭VII and v** are MD while MD_MAJOR is on.
- Parser quirk (not C24): in minor, `#vii°` parses as B♯–D♯–F♯ (→ X) and `♭VI` as A𝄫. These are odd notations, not used anywhere.

## Musts / Shoulds / Coulds

**Musts (before merge)**
1. Justin rules on the rung 1 **soprano / tenor–soprano tell**. As the ladder rule is written (a feature the screen does not show), it fails: soprano line +66.3, last soprano degree +41.4, tenor–soprano last chord +30.1. **Perfect vs plagal from the final I's soprano alone: 85 % (was 65 %)**. The jump comes from the C12 and C23 refit (perfect so–so 73 %, re–mi 1 %), not from the theory. If it is a tell: balance the last soprano degree inside the fit (or turn RUNG1_SOP_BALANCE on, and re-measure the register tells). If it is content (the melody is part of the cadence): record that in the decision log, so the ladder rule has a stated exception.

**Shoulds**
1. Fix analyse() to check spelling as earNumFn does, so the two agree, as C24 asks. Then add the 17 numerals above to unit_test C9; the test currently lists vi as the only exception.
2. Spacing boundary. With Kostka & Payne's definition (close = soprano–tenor **less** than an octave), the rung 1 spacing of both chords predicts **+6.1**. With the app's (≤ an octave) it is −0.2. The difference is the chords at exactly an octave: 0 % of perfect, 7.4 % of interrupted. Balance the exact-octave case too, or the four-way pattern (o/8ve/c), or state the definition in the decision log.
3. Rungs 2–3 spacing pattern (+7.9 / +15.0) and rung 3 final-chord completeness (+9.3) break the ladder rule. Both were there before 049-c-eng and are out of this scope; register them for the next pass.
4. Rung 2 mid-phrase root-position triads with a doubled 3rd and **no 5th** (IV, vi, III, VI): 1.9 % of questions. The C25 logic (complete chord; no doubled 3rd in a major triad unless it is vi/VI after V) applies equally to root-position IV and III. Extend it.

**Coulds**
1. The 63 strict V–vi voicings that double vi's root would widen the interrupted pool. Textbook practice prefers the doubled 3rd, so this is optional.
2. Keep the scope note in the decision log: C25 as built re-voiced 1,045 rung 2 grid entries, not 6. Recommendation: keep it (section 4).
3. Parser notation for `#vii°` and `♭VI` in minor (section 5).

## Sources (pedagogy)
- Aarden & von Hippel, "Rules for Chord Doubling (and Spacing): Which Ones Do We Need?", *Music Theory Online* 10.2 (2004), §2.1 and Table 2.1.3a: https://mtosmt.org/issues/mto.04.10.2/mto.04.10.2.aarden_hippel_2.1.3.php
- Puget Sound, *Music Theory for the 21st-Century Classroom*, "Voice Leading First Inversion Triads" and "Summary of Doubling Rules": https://musictheory.pugetsound.edu/mt21c/VoiceLeadingFirstInversionTriads.html, https://musictheory.pugetsound.edu/mt21c/SummaryOfDoublingRules.html
- Minnesota State, *First-Year Music Theory*, voice-leading chapter: https://minnstate.pressbooks.pub/firstyearmusictheory/chapter/voice-leading/10
- Iowa State, *Comprehensive Musicianship* 10.3: https://iastate.pressbooks.pub/comprehensivemusicianship/chapter/10-3-part-writing-first-inversion-triads-and-suspensions-tutorial/
- Aldwell & Schachter and Kostka & Payne are cited through the MTO survey; the checker did not consult the books directly here. The Kostka & Payne definition of close and open structure is quoted from memory: "close: less than an octave between soprano and tenor".

## Re-check: C31–C35 (independent check, 21 Nov 2026; branch at `ec07784`, L108)

What this covers: commits `2578727` and `ec07784` against `fa5fe9d`. The builder's C31–C35 section was used only to find claims. Every number below was measured again with the checker's own code, all of it in `/tmp/ic049` (scratch, not committed):
- the same strict SATB checker as above;
- held-out tell measurement on 20,000 seeded questions per rung, with the same seeds as before;
- a new pool enumerator and linear-programming (LP) floor solver, `lp_floor.py` and `lp2.py`. They use scipy HiGHS and are written apart from `tests/cadweights_lp.py`, which was not read or run.

"Before" means `fa5fe9d`. The close-spacing boundary is C32's: close when the soprano is less than an octave above the tenor.

### Verdicts

| item | verdict |
|---|---|
| Strict SATB, rungs 1–3, including re-voiced chords (C33 complete final tonic, C34) | **PASS**: 0 faults |
| C31 top line and tenor–soprano gap balanced; register still ≤ 5 | **PASS** against Justin's L108 terms. Residues remain (below) |
| C31 claim "the residues are the floor under the register cap" | **TRUE for the current pool** (within 1.4 points). **Not the limit of the music**: a larger strict pool does much better (below) |
| C32 close = S–T < octave (`EAR_CLOSE_LT = 12`) | **PASS**: 12 → open, 11 → close; rung 1 spacing tell +2.8 |
| C33 rungs 2–3 spacing pattern and final completeness | **PASS** |
| C34 no root-position triad with a doubled 3rd and no 5th | **PASS**: 0 at rungs 2 and 3, grid and questions |
| C35 Analysis reads spelling; 228 changed readings; no score label changes | **PASS**: all three claims confirmed |
| Suites, run one at a time | **PASS**: unit_test 1,163 checks, 0 failures; analysis_engrave_test 0 failures; earlab_test 0 failures (76 tell checks); earlab_items_test 0 failures (91 tell checks) |

### Strict SATB (the checker's own rules)

- **Rung 1: 0 faults.**
  - My own enumeration of the strict rung 1 pool (same rules: ranges, one 3rd or two in vi after V, complete chords, the leading note rises in every voice in V–I) gives **2,094 voicings, identical one for one** to the app's pool in use.
  - The 20,000 questions have 0 faults and 0 incomplete chords.
  - V–vi is still 108 / 108, all with weight; 105 distinct came up.
- **Rung 2: 0 faults** in the 9,600 grid entries (3,376 distinct) and in 20,000 questions.
- **Rung 3: 0 faults** in the 6,600 grid entries (1,504 distinct) and in 20,000 questions.
- **C34:** 0 triads with a doubled 3rd and no 5th anywhere. Before: 376 rung 2 questions in 20,000, and 1,087 final minor tonics at rung 3.
- **Incomplete triads still used:** all are root tripled, 3rd once, no 5th. This is acceptable in strict style.
  - Rung 2: V 61, VI 6 (per 20,000).
  - Rung 3: final V after V7/V, 83 (0.4 %). A half cadence ending on an incomplete V is a weakness, not an error (Could).
- **C33:** every rung 2 and rung 3 final tonic that can be complete now is. Rung 3 final completeness predicts nothing (+0.3).
- **Root-position doubled 3rd with the 5th kept**, outside vi/VI after V: rung 2 IV 100, III 90, VI 811 (mostly next to V in minor, the usual reason); rung 3 IV 28, iv 81. This is a weakness in a major triad (IV, III), not an error (Could).

### Tells, rung 1 (sampled, 20,000; points over chance 25.2 %)

| feature | before | after | builder (after) |
|---|---|---|---|
| soprano line | +66.3 | **+56.0** | +56.7 |
| soprano degree, first / last chord | +34.8 / +41.4 | **+27.5 / +24.7** | +27.6 / +24.8 |
| soprano motion | +33.9 | +27.8 | +28.3 |
| tenor–soprano gap, first / last chord | +11.1 / +30.1 | **+7.4 / +19.9** | +7.4 / +20.1 |
| both gaps together | +42.5 | +35.7 | |
| spacing of first / last / both chords (C32) | +3.1 / +3.4 / +6.1 | **−0.4 / +3.1 / +2.8** | +3.5 (both) |
| final chord complete | −1.2 | −1.2 | |
| lowest / highest / pair / span | +1.3 / +1.1 / +2.1 / +0.5 | +3.3 / +1.4 / **+3.9** / +3.5 | ≤ +4 |
| first / last bass, first / last soprano, key | +2.7 / +2.1, +1.1 / +1.5, −0.2 | +3.7 / +3.5, +2.6 / +3.3, +3.5 | ≤ +4 |

The exact tells, computed by the checker from the app's EAR1W weights, match the builder's:

| feature | exact tell |
|---|---|
| soprano line | +56.8 |
| last soprano degree | +25.3 |
| first soprano degree | +27.8 |
| tenor–soprano gap, last chord | +20.6 |
| tenor–soprano gap, first chord | +7.3 |
| every register feature and spacing of both chords | ≤ +4.0 |

Shared-chord tells (sampled; chance 50.2 %):
- **Perfect vs plagal**, from the final I: soprano degree 53.0 % (was 85.0), tenor–soprano gap 53.5 % (was 85.5), spacing 50.1 %, doubling 49.7 %. **The exact bass + soprano pitches of the final I: 57.1 % (+6.9).**
- **Perfect vs interrupted**, from the V: soprano degree 53.7 % (was 59.8), tenor–soprano gap 53.7 %. **The exact V voicing: 56.0 % (+5.8)**; the builder reports +5–7 for the exact shared-chord voicing.
- Plagal vs IV–V, from the IV: at chance (+1.2).

### Tells, rungs 2–3 (sampled, 20,000; chance 25.5 % / 18.5 %)

| feature | rung 2 before → after | rung 3 before → after |
|---|---|---|
| spacing pattern, every chord (C32) | +12.7 → **+1.8** | +6.1 → **+2.9** |
| same, by number of chords (4 / 5) | +0.9 / +3.0 | n/a / +2.9 |
| spacing and mode together | +14.9 → +2.1 | +6.6 → +3.0 |
| final chord complete (and with mode) | +3.2 → **+0.1** (+0.1) | +9.3 → **+0.3** (0.0) |
| lowest + highest / span / last bass / last soprano | −0.1 / −0.2 / 0.0 / +0.1 → +2.5 / +1.7 / +2.9 / +2.0 | +3.3 / +3.2 / +2.6 / +2.4 → +2.6 / +2.5 / +3.1 / +3.5 |
| tenor–soprano gap, last chord | +19.1 → +20.1 | +20.4 → +19.4 |
| soprano degree, last chord | +24.6 → +25.6 | +25.6 → +19.5 |
| soprano degree / gap, first chord | −0.4 / −0.7 → −0.4 / +0.3 | +2.9 / +2.8 → +1.8 / +2.9 |

The old ≤ 12 spacing definition, which is no longer in force, still reads +10.2 at rung 2 and +14.7 at rung 3. Under C32 the octave counts as open, so this is expected.

### Is +56.7 line / +20.1 last gap the floor? (C31 claim)

The checker built its own LP. It uses the same exact-tell measure as the builder (sum over values of the largest share, divided by the number of answers, minus chance). Its constraints are:
- the 3 % plain mix;
- I–V and IV–V at half each in imperfect;
- the register features (lowest, highest, the pair, span, first and last bass, first and last soprano, key, spacing of both chords) capped;
- the shared-chord soprano and gap tells (perfect/plagal, perfect/interrupted) at most 4.

Exact tells (points):

| pool (all strict, complete chords) | voicings | register cap | best line | best last gap | both at once (line / gap) |
|---|---|---|---|---|---|
| **as in the app** | 2,094 | 4 | 55.4 | 19.2 | **55.4 / 19.2** |
| as in the app | 2,094 | 5 | 53.4 | 18.2 | 53.4 / 18.2 |
| as in the app | 2,094 | none | 38.1 | 0.6 | 40.8 / 16.1 |
| + bass up to D4 | 2,178 | 4 | 55.4 | 19.2 | 55.4 / 19.2 |
| + vi after V may double its root | 2,153 | 4 | 55.4 | 15.3 | 55.4 / 15.3 |
| **+ frustrated leading note in V–I** | 2,427 (V–I 170 → 503) | 4 | **46.7** | **1.5** | **46.7 / 2.8** |
| all three | 2,586 | 4 | 46.7 | 0.2 | 46.7 / 0.7 |

In the table, "frustrated leading note" means the leading note in an inner voice falls to the 5th of I, which gives a complete I. For every row, the first and last soprano degree, the first gap and the shared-chord tells are held at or below the app's levels.

- **With the app's pool and cap 4, the builder is honest.** The app (line +56.8, gap +20.6) is within 1.4 points of the best trade-off the LP can find (+55.4 / +19.2). Raising the register cap to 5 buys only 2 points on the line and 1 on the gap. The soprano line's content floor (+38.1, the chords alone) matches the builder's.
- **It is not the limit of strict style.** The constraint that binds is a rung 1 rule: in V–I the leading note rises in *every* voice, because the feedback says so. With that rule, a complete final I can only be voiced a few ways.
  - Allowing the textbook frustrated leading note (Aldwell & Schachter and Kostka & Payne both allow it in an inner voice in V–I; the app's own strict rules at rungs 2–3 already allow it) gives, with the register still capped at 4:
    - **soprano line +46.7** (from +56.8);
    - **last gap +2.8** (from +20.6);
    - shared-chord tells 0–4.
  - Adding root-doubled vi after V as well takes the last gap to +0.7.
  - Raising the bass ceiling to D4 does not help.
- The cost is the rung 1 feedback sentence ("the leading note rises to the home note"). It would need to say that the leading note rises in the top voice and may fall to *so* in an inner voice. Rungs 2–3 already work that way. This is Justin's decision. The checker found no other pool change that helps.

### C32, C34, C35 details

- **C32.** `EAR_CLOSE_LT = 12`; `earClose([48,60,64,72])` = false (octave = open); `earClose([48,60,64,71])` = true. The pool's close-spaced entries went from 1,463 to 1,285 (the exact-octave ones moved to open). Close share by answer is 41–45 %.
- **C35, scan.** The checker ran its own scan over every root letter × (♮, ♭, ♯, 𝄫, 𝄪) × every app quality (plus It/Fr/Ger+6) × 24 keys: 19,320 chords, through analyse() on `fa5fe9d` and on `ec07784`.
  - **228 change function**, as claimed: 180 in minor and 48 in major. All become C.
    - 132 are minor-key chords spelled outside the key: dim7 36, dim 24, aug 24, m7b5 12, m 12, madd9 12, m6 12.
    - 96 are augmented sixths on odd roots: It+6 48, Ger+6 48.
  - **132 more** keep their function and only lose `borrowed`. These are major-key chords spelled with notes outside the parallel minor (e.g. iv° F–A♭–C♭). Their function is already C, so `isCol` is unchanged.
  - Real augmented sixths on ♭VI, ♯IV and II are unchanged.
- **C35, app numerals.** No numeral the app offers changes: diatonic and colour palettes, 744 readings in 24 keys, identical before and after.
- **C35, scores.** **No Analysis score label changes.** All 135 harmony labels in `scores/meta.json`, read through parseRoman + analyse(), give identical results before and after. The score view colours labels from the stored `f` (index.html, the `l.f` line in the harmony layer), not from analyse().
  - Pre-existing, not new: the stored `f` and analyse() differ on 3 labels. These are deliberate numeral_reread decisions.

### Musts / Shoulds / Coulds (re-check)

**Musts:** none. C31–C35 are built as approved, strict and tested.

**Shoulds**
1. **Justin decides on the frustrated leading note at rung 1** (section above). It is the one change that lowers the residual top-line tells substantially:
   - last gap +20.6 → about +3;
   - soprano line +56.8 → about +47;
   - register stays ≤ 4, and the style stays strict and textbook.

   If he declines, record in the decision log that +56.8 / +20.6 is the accepted residue for this pool. The builder's floor claim is true for that pool.
2. The exact final-I pitches (bass + soprano) for perfect vs plagal (+6.9), and the exact V voicing for perfect vs interrupted (+5.8), are just over 5. They are pitch-level details, but a cap on the shared chord's exact outer voices would close them.
3. Rungs 2–3 still have last-chord soprano degree (+25.6 / +19.5) and last tenor–soprano gap (+20.1 / +19.4) tells. The builder notes these as outside C33. They are mostly cadence content, but the same LP treatment as C31 applies when Justin wants it.

**Coulds**
1. The rung 3 final V after V7/V without its 5th (0.4 %), and rung 2 major root-position IV / III with a doubled 3rd (about 1 %): prefer complete voicings or a root/5th doubling where the grid allows.
2. Keep the LP generators' scipy dependency noted in the charter's test section (the suites do not need it).
