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
