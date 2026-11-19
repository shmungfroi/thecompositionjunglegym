# Independent check: R12 (branch `048-r12`, commit 8a0e7d2, against 0.47 `ef97cdb`)

Checker: independent; read-only on `/home/claude/wt-r12`. Method: read the rule cards (`C2RB`, `C3RB`, `C3MRB`) and the changed functions, then drove `c2Check`, `c2CantusCheck`, `c3Check`, `c3mCheck`, `c13Line`/`c13Answer` in headless Chrome (Playwright, local `http.server`, external requests blocked) on my own cases, old file and new file side by side. I did not use the builder's test file or its cases.

## Overall verdict

**PASS. All seven defects are fixed and no regressions were found. There are two residual gaps of the CP-6 kind, and three judgements need Justin's decision.**

| id | verdict |
|---|---|
| CP-1 third-species cambiata | **PASS** |
| CP-2 florid tied unison (H4) | **PASS** (severity is a judgement; see J1) |
| CP-3 cantus C6 | **PASS** |
| CP-4 three-voice M3 | **PASS** |
| CP-5 mixed V2 into the downbeat, model `lydhigh23` | **PASS** |
| CP-6 mixed successive downbeats | **PASS for 2nd and 3rd species.** Gaps remain in 4th species and at the 3rd-species entry (see "Other findings" 1 and 2) |
| C13-1 minor 7th at line ends | **PASS** |

---

## 1. Correct behaviour from the cards and Fux

- **S3c (cambiata):** four notes. Step down to a dissonant quarter, leap down a 3rd to a consonance, then step back up. The card says nothing about a fifth note, and in Fux the line is free after the step up. So once the step up comes, the figure is complete.
- **H4:** the tag reads "Must 1–3, 5 · Should 4". The text covers only new notes in 2nd/3rd species and says that in 4th species a unison is "allowed but use it sparingly". S5b says each note value keeps its own species rule, and a tied note is the 4th-species element. A tied unison in florid is therefore 4th-species behaviour. The tag and the text pull in different directions here.
- **C6:** "After a 5th, 6th or octave, turn back by step." So the line must turn back AND move by step, after all three intervals.
- **M3:** judge the outline of the two leaps. A 5th, 6th or octave is fine. A 7th, a tritone, or more than an octave gets a warning.
- **V2 / MX2:** consecutive perfect intervals by contrary motion between adjacent notes are a Must, so they apply from the last note of a bar into the downbeat. MX2 says "the same rules as two-voice species, now checked against both other voices". So downbeat-to-downbeat 5ths/8ves that involve the species voice follow S2c (2nd species), S3d (3rd species) and S4d (4th species: "5ths on the tied downbeats of a 5–6 chain are fine"), not V1/V2.
- **C13-1:** in minor, raise the 7th only when a real neighbouring note is the tonic. A missing neighbour (the start or end of the line) must not count as the tonic.

## 2. My test cases and results (old 0.47 → new 0.48)

### CP-1: species 3, Dorian, cantus below. Splices into model `dor3above`. Bar 4 is over D4. I filtered S3b at the dissonant note.
| case | expected | old | new |
|---|---|---|---|
| D5 C5 A4 B4, then leap up to D5 | pass | S3b err | **pass** |
| D5 C5 A4 B4, then leap down a 3rd | pass | S3b err | **pass** |
| D5 C5 A4 B4, then step up (5-note form) | pass | pass | pass |
| D5 C5 A4, line ends there (figure unfinished) | pass | pass | pass |
| cambiata across the barline (dissonance on beat 4, leap to the downbeat, step up) | pass | pass | pass |
| D5 C5 A4 F4 (leaps away after the 3rd) | flag | err | **err** |
| D5 C5 G4 (leap of a 4th from the dissonance) | flag | err | **err** |
| B4 C5 A4 B4 (steps UP into the dissonance) | flag | err | **err** |
| D5 C5 A4 G4 (steps down after the 3rd) | flag | err | **err** |
| F5 C5 D5 (leaps into the dissonance) | flag | err | **err** |

### CP-2: florid, Dorian above (model `dor5above`), filtered for H4
| case | expected | old | new |
|---|---|---|---|
| A4 (a 3rd over F4) tied into bar 7, a unison with A4 | report | nothing | **H4 warn** "the tied note makes a unison on the downbeat…" |
| new note D4 on the bar 4 downbeat, a unison | error | H4 err | H4 err |
| tied C5 (5th → 3rd) | nothing | nothing | nothing |
| tied A5 (10th → octave; an octave is not a unison) | nothing | nothing | nothing |
| the model itself | nothing | nothing | nothing |
| species 4 (`dor4above`), tied unison (for comparison) | warn | H4 warn | H4 warn (unchanged) |

### CP-3: `c2CantusCheck`, filtered for C6
| line | expected | old | new |
|---|---|---|---|
| D4 F4 E4 D4 **A4 G4** … (5th up, step down) | pass | pass | pass |
| … D4 **A4 F4** … (5th, then back down a 3rd) | flag | **missed** | C6 |
| … D4 **A4 E4** … (5th, then back down a 4th) | flag | **missed** | C6 |
| … D4 **A4 D4** … (5th, then back a 5th) | flag | **missed** | C6 |
| … D4 **A4 B4** … (5th, then on up) | flag | C6 | C6 |
| … **A4 D4 E4** (5th down, step up) | pass | pass | pass |
| … **A4 D4 F4** (5th down, back up a 3rd) | flag | **missed** | C6 |
| E: E4 **C5 B4** (m6 up, step down) | pass | pass | pass |
| E: E4 **C5 A4** (m6, back down a 3rd) | flag | C6 | C6 |
| D4 **D5 C5** (octave, step) | pass | pass | pass |
| D4 **D5 A4** (octave, back down a 4th) | flag | C6 | C6 |
| D4 **G4 E4** (a 4th is not a large leap) | no C6 | none | none |

### CP-4: `c3Check`, Dorian, cantus low, top voice (one case in the middle voice), filtered for M3
| line | outline | expected | old | new |
|---|---|---|---|---|
| A3 D4 A4 | octave | pass | **warn** | pass |
| D4 A4 D5 | octave | pass | **warn** | pass |
| A4 D4 A3 (falling) | octave | pass | **warn** | pass |
| B3 D4 G4 / E4 G4 C5 / D4 F4 A4 | 6th / m6 / 5th | pass | pass | pass |
| D4 B4 D5 (6th + 3rd) | octave | pass (M1 flags the M6 separately) | warn | pass |
| B3 D4 F4 | d5 | flag | **missed** | M3 "outline a d5 (B3 to F4)" |
| F4 D4 B3 | d5 | flag | **missed** | M3 |
| B3 D4 F4 in the middle voice | d5 | flag | missed | M3 |
| D4 G4 C5 / D4 F4 C5 | m7 | flag | warn | M3 |
| D4 A4 E5 | M9 | flag | warn | M3 |
| A3 D4 **D4** A4 (repeat between) | – | no M3 | **warn** | none |
| D4 F4 **F4** C5 (repeat between) | – | no M3 | **warn** | none |
| B3 D4 F4 with an empty bar before F4 | – | no M3 | none | none |

### CP-5: mixed, 2nd species (model `dorlow02`: top in 2nd species, middle in whole notes, cantus bass)
| case | expected | old | new |
|---|---|---|---|
| weak A5 (12th over D4) → downbeat D5 (5th over G4), contrary | V2 | **missed** | V2 "consecutive 5ths by contrary motion … from the last note of the bar into the downbeat" |
| weak E6 (8ve over the middle voice's E5) → downbeat F5 (unison with F5), contrary | V2 | **missed** | V2 |
| weak D5 (5th over G4) → downbeat C5 (5th over F4), similar | V1 | V1 | V1 |
| weak 12th → downbeat 8ve, contrary | nothing | nothing | nothing |
| weak 10th → downbeat 5th, contrary | nothing | nothing | nothing |
| whole-note voice vs cantus, 5ths on successive downbeats | V1 | V1 | V1 |
| the model itself | nothing | nothing | nothing |

### CP-6: mixed. 2nd species uses `dorlow02`, 3rd species uses `dorlow03`.
| case | expected | old | new |
|---|---|---|---|
| sp2, 5ths with the cantus on bars 6–7, weak beat moves a step | S2c err | V1 err | **S2c err** |
| same, weak beat moves a 3rd | S2c err | V1 err | **S2c err** |
| same, weak beat leaps a 4th | nothing | V1 err | **nothing** |
| sp2, 8ves on bars 6–7, weak beat leaps a 4th | nothing | V1 err | **nothing** |
| sp2, 8ves, weak beat moves a step | S2c err | V1 err | **S2c err** |
| sp2, weak beat not yet written | (judgement) | V1 err | nothing (waits) |
| sp3, 5ths with the cantus on two downbeats | S3d warn | V1 err | **S3d warn** |
| sp3, 8ves on two downbeats | S3d warn | V1 err | **S3d warn** |
| sp3, penultimate downbeat 8ve → final 8ve | (judgement) | V1 err | S3d warn |
| whole-note voice vs cantus (not the species voice) | V1 | V1 | V1 |

### C13-1: `c13Line` / `c13Answer`, tonal system
| line | expected | old | new |
|---|---|---|---|
| A minor: G alone | G | G♯ | **G** |
| A minor: G E A (starts on the 7th, then E) | G | G♯ | **G** |
| A minor: C B G (ends on the 7th) | G | G♯ | **G** |
| C♯ minor: C♯ E G♯ B (ends on the 7th) | B | B♯ | **B** |
| E♭ minor: D♭ F G♭ E♭ (starts on the 7th) | D♭ | D | **D♭** |
| A minor: A G A / C B A G / G A C | G♯ | G♯ | G♯ |
| A minor: G (held) A, and G (rest) A | G♯ | G♯ | G♯ |
| real answer of G A C E A | D♯ E G B E | same | same |
| real answer of G B C A | D F♯ G E | D♯… | **D…** |
| real answer of A C B G | ends D | D♯ | **D** |
| tonal answer of A E C B G | ends D | D♯ | **D** |
| C major: E D B | B | B | B |

## 3. Replacement `lydhigh23`

- The old model, run under the new checker, now shows its V2 ("consecutive octaves by contrary motion between the bottom and middle voices, bars 1–2"). That confirms the defect.
- The new model has **no errors**. Its one warning is a T6 unison (middle and cantus on G4, bar 3).
- **Begins correctly:** the bass enters on F3, the final. Opening chord F3/F4/F4.
- **Ends correctly:** final chord F3/C4/F4. The cantus falls G4→F4 and the bass rises E3→F3. That is the Lydian semitone, so no ficta is needed, and none is applied.
- **Mode respected:** no accidentals anywhere. B♮ appears in the cantus and the bass.
- **Musically sensible.** The weak-beat dissonances are neighbour notes, passing notes, or two cambiatas (bars 3→4 and 9→10, each with the dissonance on beat 4 leaping to the next downbeat, which S3c allows). The bass range is A2–A3. The one leap of a 5th (D3→A3, bars 7→8) turns back by step.
- Minor points:
  - The bar 4 downbeat is D3/F4/B4, a diminished 6/3 with a tritone between the upper voices. T1 allows this "sparingly". The mixed checker doesn't warn about upper-voice tritones; the first-species checker does.
  - The bar 7 chord is B2/D4/D5, a bare 3rd.
  - Neither is wrong.

## 4. Regressions

- **Every built-in model, old vs new** (71 two-voice, 18 three-voice, 108 mixed, 6 cantus lines, plus the climb 13 built-in subjects with tonal answers in all 24 keys = 299 items). Only two outputs changed:
  - `m:lydhigh23`: the replaced model (see above).
  - **`2:lyd5above` now shows `H4 warn` (attack 12)**, a tied unison in the florid model. This is correct under the new CP-2 behaviour, but the builder's report says "No other models changed" and doesn't mention it. A model students copy now carries a warning. Either accept it (other models also carry warnings, e.g. `dor4above` S4f) or re-pick that model.
  - No model has an error. The climb 13 subjects and answers are unchanged in every key.
- **Random mutation diff:** 10,160 cases (40 mutations of each two-voice model, 60 of each three-voice model, 30 of each mixed model, 3,000 random cantus lines). Every difference between old and new falls in the expected categories: +C6 (1,072), M3 changes (−58 / +17), +H4 warn (49), −S3b (17), and mixed V1/V2 → V2/S2c/S3d. No other rule code moved, apart from mutations of the replaced `lydhigh23` itself.
- **Not done:** a timing run of `c3mSolve` across all modes. It exceeded my 10-minute limit with both files loaded, so I abandoned it. I have no evidence either way on solver speed or coverage under the new rules. The builder's sweep claims it is fine.

## 5. The builder's judgements

**J1. CP-2: tied unison in florid is a warning, not an error.** I agree that this is the musically right reading: S5b says each value keeps its own species rule, and the tied note is a 4th-species element, which H4 itself allows "sparingly". But it contradicts the H4 tag ("Must 1–3, **5**"), and the brief is that the checker follows the rule book. **Recommendation:** keep the warning and fix the card in the same release. Tag: "Must 1–3, 5 (new notes) · Should 4, and tied notes in 5". Add a sentence to the text: "In florid counterpoint a tied note may make a unison, as in fourth species; use it sparingly." Without the card change, a student or teacher reading the card sees Must and the checker shows Should.

**J2. CP-6: S3d warns on the step into the final bar in mixed species; the two-voice checker does not.** The card has no exception, and the warning is actionable (choose a 3rd or 6th on the penultimate downbeat). I checked all 24 two-voice 3rd/5th-species models: none has the same perfect interval on the penultimate downbeat and the final. So removing the two-voice exclusion (`v.a!==N-1` in `c2Check`'s S3d block) changes no model. **Recommendation:** make the two checkers agree by following the card in both: drop the final-bar exclusion in `c2Check`. Leaving them different is the one outcome I'd avoid, because students meet both climbs.

**J3. CP-6: S2c waits until the weak-beat note is written.** I agree. The two-voice checker behaves the same way. S2c depends on the size of the weak-beat move, so it can't be judged before that note exists. Once the note is written, the error appears. No change.

**J4. New wording.**
- CP-2: "the tied note makes a unison on the downbeat. As in fourth species it is allowed, but use it sparingly." Accurate given J1. It contradicts the card tag until the card is fixed.
- CP-4: "two leaps the same way in the top voice outline a d5 (B3 to F4). Two leaps in one direction should outline a chord: a 5th, 6th or octave." Accurate and matches the card. However, "a d5", "a m7" and "a M9" are code abbreviations. They match the two-voice message, but a student reads them as jargon. **Suggest** spelling them out ("a diminished 5th") in both the two-voice and three-voice messages.
- CP-5: "consecutive 5ths by contrary motion … from the last note of the bar into the downbeat". Accurate.
- CP-6: the S2c message is accurate (it fires only when the weak-beat move is a step or a 3rd). The S3d message is accurate, including "many teachers…", since the card's source is "later teaching".
- **Australian terms:**
  - Spelling is fine ("neighbour"; no US spellings in the new text).
  - The new S3d message says "**The quarters in between** soften them", and the new Understand sentence follows climb 2's "half note / quarter / whole note" vocabulary. NESA and Australian classrooms use crotchet / minim / semibreve / quaver, and the app itself uses "crotchet" and "quaver" in other rooms.
  - This is not new to R12: climb 2 uses US note names throughout. But the new message inherits it.
  - **Recommend** a separate register item to move climb 2 (cards, messages, Understand text) to crotchet/minim/semibreve/quaver. The fix belongs in a sweep, not in R12 alone.

## 6. Other findings

1. **Mixed 4th species still breaks S4d. This is a residual of CP-6's class.**
   - (a) 5ths on the tied downbeats of a 5–6 chain get **V1 errors**. Test: `ionlow04`, top voice A4 / B4 / C5 tied over C4 / D4 / E4. Result: "V1 err, Bars 2–3: parallel 5ths between the top and bottom voices". S4d explicitly says these are fine.
   - (b) The opposite also happens: 5ths on successive **after-beats** (a 6–5 chain, D5 / C5 / B4 over G4 / F4 / E4) are **not reported at all**. In `c3mCheck`, the weak-beat→downbeat loop skips tied notes, and the downbeat loop never looks at beat 2. S4d (a Must) is not implemented in mixed species.
   - The builder deliberately left 4th species on V1/V2, but MX2 ("the same rules as two-voice species") covers it. **Recommend** a follow-up item: in mixed 4th species, apply S4d between the species voice and each other voice. That means no V1 on tied downbeats of a 5–6 chain, and S4d errors for after-beat 5ths/8ves. Also extend the new Understand sentence to cover 4th species.
2. **Mixed 3rd species: the bar 1 entry is checked against the bar 2 downbeat as first species.**
   - Test: `dorlow03`, entry A4 (5th over D4), then G4 F4, then C5 on the bar 2 downbeat (5th over F4). Result: "**V1 err**, parallel 5ths".
   - The two notes are not adjacent (two quarters lie between them), and the two-voice checker reports nothing here.
   - In 2nd species the entry is adjacent to the downbeat, so V1 is right there.
   - **Recommend** treating the 3rd-species entry like the two-voice checker: no V1; at most S3d.
3. **Chromatic clashes between voices are not detected (present in 0.47 too; not R12).** In 8 built-in models, the raised leading note in one voice sounds against the natural 7th in another, at the same moment, in the penultimate bar:
   - `aeolow12` (G♯4/G4), `aeomid03` (G4/G♯2), `aeomid23` (G4/G♯3), `dorlow02` (C6/C♯5), `dorlow04` (C♯5/C5)
   - first species: `mixlow` (F5/F♯4), `aeolow` (G5/G♯4), `dorlow` (C6/C♯5)
   - Cause: the upper-voice dissonance test checks only 2nds and 7ths (`g7===2||7`), so augmented unisons and diminished octaves pass. The ficta in `c3Notes`/`c3mNotes` raises one voice without looking at the others.
   - Fux would not write these. **Recommend** a new Must item: treat any non-perfect unison or octave (A1, d8 and compounds) between any two voices as a dissonance, and fix the 8 models.
4. **Duplicate messages:** at the 2nd-species entry (bar 1 → bar 2), parallels are reported twice, once by each loop in `c3mCheck`. This was already true in 0.47, and R12 extends it to V2. Cosmetic.
5. **Melodic rules missing in mixed species:** `c3mCheck` implements M1, M4 and M7 only. M2 (recover leaps), M3 (two leaps) and M6 (tritone outline) are never checked for either voice, although the rule book applies them to species 1–5. `C3MCODE` even maps `recover` to M2, but nothing emits it. This is outside R12; flag it for the register.
6. `n3` is now an unused variable in `c2Check` species 3. The builder notes this; it is harmless.

## Memory note
None.
