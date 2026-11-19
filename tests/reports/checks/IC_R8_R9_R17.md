# Independent theory check: R8, R9, R17 (0.48 branch, frozen copy `/home/claude/wt-check-r8`, HEAD 1b3872f)

Checker: independent; nothing in the worktree was edited. Baseline for comparison: 0.47 = `ef97cdb`.
My own readings were made first (scripts and dumps in `/home/claude/checks/ic_r8/`). Only after that did I read the builder's `tests/reports/R8_R9_report.md`; that comparison is at the end.

## Verdicts

| Spec item | Verdict | In one line |
|---|---|---|
| R8 numerals match the notes | **FAIL** (small, fixable) | 2 labels are wrong: Jesu bar 8 cadence "V(7)/III" has no 7th; Jesu bar 11 "/iv" should be "/IV". 2 clean suspensions in BWV 269 are not labelled (bar 12, bar 15). The other ~130 labels are right. |
| R8 altered roots, °, ø, applied chords, no-third chords | PASS | ♯vi°6 has its accidental; every ° and ø is present and correct; the six no-third chords are now named by their resolution chord. |
| R8 passing 7ths as V(7) | **FAIL** on 1 of 7 | 6 correct; Jesu bar 8 "V(7)/III" is wrong (see D1). |
| R8 suspensions labelled | **FAIL** (partial) | 7 labelled correctly; BWV 269 bar 12 (7–6) is labelled as a chord "iii7", and bar 15 (9–8) is not labelled. |
| R8 cadence names (AU/UK, US in brackets, Phrygian) | PASS | All 31 cadences in the 7 scores that have them are named correctly. O Haupt bar 8 is correctly *not* Phrygian. |
| R8 function per numeral and colours | PASS, with 1 open decision | All 137 labels carry `f`, and the rendered colours match it. One deviation from the approved four colours: blue-grey for W/S (see section 4). |
| R8 legend text | PASS, 1 omission | It does not explain "(2–3)". |
| R9 chordInfo functions | PASS | Major vii°/vii°7/viiø7 are D (dom true). Minor v/v7 are W with the exact text and are not dominant. Minor VII/VII7 are S and not dominant. |
| R17 K. 331 Var. III anchors | PASS | All 4 sit on the arrival chord's onset. So do all 31 anchors in all scores. |
| R17 unison ids | PASS | All 1836 chorale note ids (9 engravings) are in their own voice's staff and layer. The 0.47 swaps (12 ids per engraving) are gone. |

## 1. Method

- I wrote my own Humdrum line parser (`ic_r8/kparse.py`). It gives each `note-L<line>F<field>` its onset, pitch and length. `ic_r8/dump.py` prints every label's anchor, its bar and beat, the sounding SATB, the notes later in that beat, and music21's `romanNumeralFromChord` reading of the onset sonority. I then read every labelled chorale beat myself from the voices, so music21 was only a cross-check. It misreads suspensions and incomplete chords, as expected.
- Piano-score cadences (K. 331 theme and Var. III, Op. 28/7, Op. 28/20): music21 `chordify` of the cadence bars (`ic_r8/cads.py`). K. 545, Maple Leaf and Entertainer have **no** cadence labels or numerals in `meta.json` (only form sections), so there is nothing to check there.
- Anchors: Verovio 6.4.1 `getMIDIValuesForElement` time for every cadence id, compared with `a` and with the chord sounding at `a` (`ic_r8/anchors.py`).
- Rendering: headless Chrome via the repo harness (`ic_r8/render.py`, `ic_r8/pos.py`). This read every drawn numeral, its computed fill, the legend HTML and the cadence tags, and called `chordInfo` for R9. Screenshots are in `ic_r8/shots/`.
- Voices: I parsed the 9 chorale SVGs myself, reading each note's staff position in its measure and the layer N suffix. I also ran `tests/score_ids_test.py`: 1836 ids, 31 anchors, 0 failures.

## 2. Disagreements, label by label (only disagreements, plus the items you asked about)

Bars use the source's bar numbers, which are the app's. Voices are listed bass, tenor, alto, soprano (B T A S).

| # | Score | Bar.beat (line) | meta.json | Notes (B T A S) | My reading | Who is right, and why |
|---|---|---|---|---|---|---|
| D1 | jesu | cadence bar 8 (L69, ch) | `V(7)/III – III` | bar 8 b2: D3 D4 F♯4 A4. On 2.5 the soprano moves A→**G** (line 68) | **V/III – III** (or VII – III) | **Meta is wrong.** The 7th of D is C, and no C sounds. The soprano G over D is a 4th: an anticipation of the soprano's G in the III chord. The builder calls it "a passing 7th", which is a counting error. 0.47 had it right (`V/III – III`). |
| D2 | jesu | 11.3 (L86), 11.4 (L88) | `vii°6/iv`, `vii°43/iv` | B2 G♯3 D4 B4 → D3 G♯3 F4 B4 → bar 12: C♯3 A3 E4 A4 (labelled **IV6**) | **vii°6/IV, vii°43/IV** | **Meta is wrong in case only.** The tonicised chord is A **major** (C♯), and the very next label says IV6. Standard practice is to write the target as it sounds, so /IV. The builder used a "home-key case" rule instead, which leaves "/iv" right beside "IV6": a contradiction a student will see. G♯–B–D–F is the minor-mode (fully diminished) vii°7 of A, used before a major chord. That is normal, and it doesn't change the target. /III is wrong, since G♯°7 has nothing to do with G. "/V of something" is wrong too: A acts as IV here and goes on to i, not to D. |
| D3 | chorale | 12.1 (L81, two labels) | `iii7` then `I6` (same anchor) | B2 D4 **A4** D5. The alto A is re-struck from bar 11 b3 (prepared) and falls to G on beat 2 (line 82) | **I6 with a 7–6 suspension**, e.g. `I6(7–6)` | **Meta is inconsistent with its own rule.** Every other suspension is named by the chord it resolves into (V(4–3), V6(2–3)). Here the suspended sonority gets its own chord name, "iii7". B–D–A has no F♯, and the A is a textbook prepared 7–6, so "iii7" invents a chord. Fix: one label, `I6(7–6)`, and drop the second I6. |
| D4 | chorale | 15.2 (L98) | `I` | G2 B3 **A4** D5. Alto A is dotted from V6 on beat 1 (prepared) and falls to G on 2.5 | `I(9–8)` | **Missing suspension label.** The builder's own evidence note says "9–8 suspension", but the label is plain I. The spec says suspensions are labelled. |
| D5 | jesu | 8.1 (L66) | `IV65` (PD, gold) | C♯3 E4 G4 A4 → D3 D4 F♯4 A4 → G2 B3 D4 G4 | **V⁶₅/VII** (C, violet) | **Pitch-correct, but it hides the function.** A–C♯–E–G is a dominant 7th: C♯ rises to D and G falls to F♯. That is an applied dominant resolving to D, the same pattern labelled V⁶₅/V in O Haupt bar 8. Gold PD is defensible only if you think in G major (V/V of III). I recommend V⁶₅/VII. Not a hard error. |
| D6 | jesu | 8.2 (L67) vs cadence ch | numeral `VII` (S), cadence `V(7)/III – III` | as D1 | make the two agree | The numeral row says VII and the cadence table says V/III for the same chord. Either is defensible, but a student sees two names. Recommended: keep the numeral VII (its S text already says it "leads to III, acting as the dominant of the relative major"). Write the cadence as `VII – III (V–I in G major)`. Failing that, write the numeral as V/III. |
| D7 | jesu | 10.1 (L78) | `vii°65/V` | C♯3 A♯3 G4 E5 → bar 10.2: v6 (D3 B3 F♯4 D5, **B minor**) | `vii°65/v` (if D2's rule is adopted) | Consistency only. The chord resolves to B **minor** (labelled v6), so by the as-it-sounds rule it is /v. Under the builder's home-key-case rule it stays /V, but that rule is what produces D2's contradiction. Choose one rule for both. |
| D8 | ohaupt | 10.1 (L87) | `V65/ii` | D♯3 F♯4 A4 B4 → E3 E4 G♯4 B4 (labelled V/V, **E major**) | `V65/ii` acceptable; strictly `V⁶₅/V/V` | Same principle as D7. B7 resolves to E **major**, not E minor (ii). V65/ii is a common teaching shorthand. Leave it, or note it, rather than nest three levels for Year 11. Low priority. |
| D9 | chorale | 9.1 (L66, twice) | `I6`, `I6` (same id) | B2 B3 G4 D5; beat 2 (L68) B2 D4 G4 D5 is I6 again; 2.5: AA d f♯ c'' = V43 | one `I6` | Duplicate data. The renderer drops a repeated label, so nothing shows wrong, but the duplicate should go. Optional: show the passing V⁴₃ (I6–V43–I bass B–A–G). |
| D10 | ohaupt | 7.3 (L71) | `ii` | E3 B3 **F♯4** G4. Alto F♯ prepared on b2, re-struck, falls to E on b4 as the bass moves to G | `ii` acceptable; `ii(9)` optional | The builder calls this an appoggiatura. It is prepared in the same voice, so it is a re-struck suspension, but the resolution comes with a bass change (9 to 6). Leaving it unlabelled is defensible. Low priority. The same applies to BWV 269 bar 17.1 vi (alto F♯ tied, 9 over E, resolving as the bass passes to D). |

### Specific items asked about

| Item | meta.json | Verdict |
|---|---|---|
| O Haupt bar 2.4 (L34) | `vii°6/vi` | **Agree.** C♯3 A♯3 E4 C♯5: A♯–C♯–E over C♯, the leading-note triad of B minor, resolving to vi on bar 3.1. (0.47 "v6" was wrong.) |
| O Haupt bar 3.3 (L40) | `V(4–3)/vi` | **Agree.** F♯3 **B3** F♯4 C♯5. Tenor B is prepared on beat 2 and falls to A♯ on beat 4 over FF♯. There is no D, so it is not vi64. |
| O Haupt bar 6 cadence | `V43 – I` (numeral row shows vii°6 on 5.4) | **Agree.** On 5.4.5 the tenor A turns E–G–C♯ into A–C♯–E–G over E = V⁴₃, which resolves to the tonic bass D with IV⁶₄ above (a plagal neighbour), then I. Not a plagal cadence: correct. It gets no NSW cadence tag (honest). Optional: show "vii°6 (V⁴₃)" in the numeral row so the two layers agree. |
| O Haupt bar 7 | IV, `iiø42/ii`, ii, ii6 | **Agree.** 7.2: E3 C4 F♯4 A4 is F♯–A–C–E over E, so iiø⁴₂ of E minor, with C natural. The bass dips to D♯ on 2.5 (vii°7/ii, unlabelled, fine). For 7.3 see D10. |
| O Haupt bar 8 cadence | `ii6 – V/ii`, "Imperfect (half) cadence in E minor (i⁶–V there; the bass rises G–A–B, so not a Phrygian cadence)" | **Agree on every point.** 7.4: G3 B3 E4 G4 = E minor over G (ii6 in D, i6 in E). The bass runs E–F♯–G–A–B in quavers, then B major (B3 B3 D♯4 F♯4). A Phrygian cadence needs iv6–V with the bass falling a semitone (C–B in E minor). Here the bass rises a step, A–B, so this is a plain imperfect cadence. |
| O Haupt bar 9.2 (L81) | `II6` (C) | **Agree.** G♯3 B3 E4 E5 = E major over G♯, but it moves to I6 (F♯ bass), not to V. It is a chromatic passing chord, not an applied dominant, so II6 (not V6/V) is the honest label. It turns into an applied chord only on 9.3.5 (F♯ B G♯ D = viiø42/V → V64), which is unlabelled; fine. |
| O Haupt bar 10 cadence | `V/V – V` | **Agree.** 10.2: E3 E4 G♯4 B4 → 10.3: AA E4 A4 C♯5. Imperfect (half) cadence. For 10.1 see D8. |
| Jesu bar 8 | `IV65`, `VII`, `III` | See D5 and D6. The chords are right; the names hide the A7→D→G applied chain. |
| Jesu bar 9.2 (L73) | `♯vi°6` (C) | **Agree.** E3 E4 G4 C♯5: C♯–E–G over E, with the raised 6th. In context it is ii°6 of B minor (the key tonicised next). Either name is right, and ♯vi°6 carries its accidental as the spec requires. |
| Jesu bar 9.3 (L74) | `VII+6` (C) | **Accept, with a note.** F♯3 A♯3 F♯4 D5: D–F♯–A♯ really is an augmented triad over F♯, so the label is pitch-exact. Functionally it is III+6 of B minor, the dominant-colour augmented chord: V of B with D as a 6th, which leaps to B rather than resolving. The bass then passes E (V⁴₂-like) to D (v6). For students, an explanatory note ("the A♯ is B minor's leading note") would help more than a different symbol. |
| Jesu bar 10.1 (L78) | `vii°65/V` | **Agree on the chord** (A♯–C♯–E–G over C♯). For the case, see D7. |
| Jesu bar 10.3 (L81) | `V(4–3)/V` | **Agree.** F♯3 B3 F♯4 C♯5. Tenor B is prepared and falls to A♯ on beat 4. Alto E on 4.5 is the passing 7th, and the cadence ch `V(7)/V – V` is right. |
| Jesu bar 11.3, 11.4 | `vii°6/iv`, `vii°43/iv` | **Disagree: /IV.** See D2. |

Everything else agrees, checked label by label: all 56 BWV 269, 40 O Haupt and 41 Jesu labels, and their inversion figures. That includes the BWV 269 iii6 readings on 2.2 and 11.2. The soprano B over D is consonant, so iii6 is fine, though V(6–5) would also do. It also includes V6(2–3) on 19.1: G is tied in the bass, and D–A over it resolves to V6 when the bass falls to F♯. And V7(4–3) on 12.3: alto G is prepared, falls to F♯ on 3.5, with C in the soprano.

## 3. Cadences in all scores

| Score | Bar | meta.json ch / name | Notes at the cadence | Verdict |
|---|---|---|---|---|
| BWV 269 | 4, 10, 18 | I – V, Imperfect (half) | I on 3.3 / 9.3 / 17.3 → D–D–F♯–A | Agree |
| BWV 269 | 7, 21 | V(7) – I, Perfect | tenor D–C on the V beat = passing 7th | Agree |
| BWV 269 | 14 | V7/IV – IV, Perfect in C (tonicisation) | G–D–F–B (alto F♮ on the beat) → C | Agree |
| O Haupt | 2, 12 | V – I, Perfect | no 7th sounds | Agree |
| O Haupt | 4 | V(7)/vi – vi, Perfect in B minor | alto E on 3.4.5 = passing 7th of F♯ | Agree |
| O Haupt | 6 | V43 – I (no NSW name) | see above | Agree |
| O Haupt | 8 | ii6 – V/ii, Imperfect in E minor, not Phrygian | see above | Agree |
| O Haupt | 10 | V/V – V, Imperfect | see above | Agree |
| Jesu | 2 | V(7) – i, Perfect | tenor B–A = passing 7th | Agree. The title says "(V–I)" in a minor key; cosmetic. |
| Jesu | 4 | V65/V – V, Imperfect | A♯ C♯ F♯ E → B B F♯ D♯; the bass **rises** A♯–B, so not Phrygian | Agree |
| Jesu | 6 | V7 – i, Perfect | alto A is a real 7th on beat 4 | Agree |
| Jesu | 8 | **V(7)/III – III**, Perfect in G | no C sounds | **Disagree: V/III – III** (D1) |
| Jesu | 11 | V(7)/V – V, Imperfect | alto E on 10.4.5 = passing 7th | Agree. It could also be heard as a perfect cadence in the tonicised B minor with a Picardy third; "half cadence in the home key" is the simpler teaching reading. |
| Jesu | 13 | V(7) – I, Perfect with Picardy third | tenor B–A = passing 7th; E G♯ B E | Agree |
| K. 331 theme | 4, 12 | I64 – V, Imperfect | ii6 (bar 4) / vii°7-type (bar 12) → I⁶₄ (1.5) → V (2.5) | Agree |
| K. 331 theme | 8, 18 | V7 – I, Perfect | I⁶₄ → V7 (1.0) → I (1.5) | Agree |
| K. 331 Var. III | 4 | i64 – V, Imperfect | E3 A4 C5 (1.5) → E G♯ B (2.5) | Agree |
| K. 331 Var. III | 8, 18 | i64 – V – i, Perfect | LH E–C–A–C (i⁶₄) → E–B with G♯ (V) → A (1.5) | Agree |
| K. 331 Var. III | 12 | vii°7/V – V, Imperfect | D♯3 under A–C (+B, D figuration) → E G♯ B | Agree (no 6/4 here, rightly) |
| Op. 28/7 | 7, 15 | V7 – I, Perfect | E7 (5–6 / 14) → A bass on the downbeat, with D–G♯ appoggiaturas resolving on the semiquaver | Agree. The two titles differ ("(V–I)" vs "(V7–I)"); cosmetic. |
| Op. 28/20 | 4 | V7/V (♭5) – V, Imperfect | D7 → G → D–F♯–C (+B) with A♭ on the semiquaver (French-sixth sound) → G | Agree. The notation would read better as "V⁷♭⁵/V" or "V7/V (with ♭5: a French-sixth sound)". |
| Op. 28/20 | 8, 12 | V7 – i, Perfect | A♭ – D♭ (Neapolitan, root position) – G7 with E♭ appoggiatura – c | Agree |
| K. 545, Maple, Entertainer | – | no cadence labels | – | Nothing to check (form sections only) |

There are no Phrygian cadences in this corpus. Every candidate's bass rises (O Haupt 8, Jesu 4, K. 331 Var. III bar 12), and the app labels none of them Phrygian. Names are UK/AU throughout. The US name appears in brackets only as "(half)". "Perfect" never carries "(authentic)", which is consistent with "where the app shows them".

## 4. Functions, colours, legend (rendered at 1440×900)

- **Colours on screen.** T `#8fbf6a`, PD `#c9a24a`, D `#c8473b`, C `#a493d8` (violet), W and S `#7fb3c8` (blue-grey). Every drawn numeral's computed fill matches its `f`. No label lacks `f`. `FN.C` is defined later in the file (line 1812), so violet does apply.
- **Function assignments.** All are sound, apart from D5 (IV65 gold; better V⁶₅/VII violet) and D6. Picardy I = T, the major I inside a minor phrase = C, iii/III/vi/VI = T, and passing V64 = D are all defensible school conventions.
- **Legend.** "Numeral colours: tonic · predominant · dominant (V and vii°, with the leading note) · colour (applied and chromatic chords, such as V/V) · no leading note (the minor v and the subtonic VII of a minor key). (7) marks a passing 7th; (4–3) a suspension." It is accurate, but it doesn't explain **(2–3)** (bass suspension, BWV 269 bar 19). Add "(2–3) a bass suspension".
- **The blue-grey (W/S) decision.** It is a fifth colour beyond the approved four. My recommendation is to **keep it as a separate fifth class, and get Justin's explicit approval**, rather than fold it into the four:
  - Folding the minor v into red contradicts R9.
  - Folding it into violet ("applied/chromatic") is wrong, because natural-minor v and VII are diatonic.
  - Green or gold would be wrong functionally.
  - The Chord Library chips (`homes()`) and `chordInfo`/FNAME already treat W and S as their own class, so a fifth colour keeps the app consistent with itself.

  Two caveats:
  1. Violet vs blue-grey is the least separable pair after green/gold. My rough CVD simulation (Machado 2009, full severity, sRGB approximation) gives ΔE ≈ 37 normally, ≈ 22 protan, ≈ 16 deutan. Green vs gold is weaker still under protan (≈ 11), and that pair is in the approved set anyway. The numerals carry the information as well, so colour is never the only cue.
  2. If Justin wants exactly four colours, the least-wrong mapping is S → violet when VII acts as V/III (label it so), and the minor v → a neutral (uncoloured) numeral.
- **Typography (renderer).** `V7(4–3)` and `V6(2–3)` print flat ("V7(4–3)", "V6(2–3)") because the figure regex only matches figures at the end of a label or before "/". `V⁶₅/V`, `iiø⁴₂/ii` and similar stack correctly. Two numeral sizes therefore sit side by side. Fix the regex to allow a parenthesised tail.
- **Shared anchors.** O Haupt bar 6 "IV⁶₄ I" and BWV 269 bar 12 "iii⁷ I⁶" share one anchor note and are spread apart. On screen the second label sits roughly, but not exactly, under the second beat, and the pair looks cramped (`ic_r8/shots/ohaupt_dup.png`, `chorale_dup.png`). Anchor the second label to a note on beat 2: O Haupt L62F2; BWV 269, if kept, L82F3.

## 5. R9: chordInfo (called in the page; C major, A minor, E minor; triads and 7ths; diatonic lists plus extras)

| Chord | f / FNAME | dom | Spec | |
|---|---|---|---|---|
| major vii°, vii°7, viiø7 | D, "pull · dominant" | true | D | PASS |
| major V, V7 | D | true | D | PASS |
| minor v, v7 | W, "minor v · weak pull (no leading note)" | false | that exact text, not D | PASS |
| minor VII, VII7 | S, "modal · subtonic" | false | not D (P2-4) | PASS |
| minor V, V7, vii°, vii°7 | D | true | D | PASS |
| minor viiø7 (G♯ B D F♯ in A minor) | C, colour | false | not specified | Note: arguably D (it has the leading note), but it is rare. Not a fail. |
| major v (borrowed), ♭VII | C | false | – | Fine |

All other degrees are T/PD as expected. I checked root position only, in three keys. The builder's unit test covers more keys and the inversions. I did not check the Keys-room scale chords or the `homes()` chips separately.

## 6. R17

- **K. 331 Var. III anchors.** Verovio onset = `a` for all four, and the chord sounding there is the arrival:
  - bar 4: L77F2S2 at 9583 ms on E–G♯–B (V);
  - bar 8: L126F2S2 at 18750 on A (i);
  - bar 12: L188F3 at 29583 on V;
  - bar 18: L265F2S2 at 43750 on A1/A (i).

  The 0.47 anchors (L78F1, L129F1, L268F1) were inside the figuration, 209–625 ms late. All 31 cadence anchors across the scores sit on their arrival (±2 ms). Op. 28/7's anchors are on the bass arrival; the soprano G♯/D there are appoggiaturas that resolve a semiquaver later, which is acceptable.
- **Unisons.** By my own parse, every note id in `chorale/ohaupt/jesu{,.t,.p}.svg` sits in the right staff (upper or lower) and the right layer (N1/N2) for its field. That is 1836 notes and 0 misplaced. The same parse of the 0.47 SVGs finds exactly the swapped pairs: BWV 269 L30; O Haupt L24, L76, L79, L97; Jesu L45. `tests/score_ids_test.py` passes. Harmony labels anchored on the tenor at those unisons (L24F2, L30F2, L45F2, L76F2, L79F2, L97F2) are at the same x as the bass, so nothing moves.

## 7. Suspension notation: V(4–3), V7(4–3), V6(2–3)

- `V(4–3)` and `V(4–3)/vi` are standard and unambiguous. They match the UK/AMEB/HSC habit of a bracketed figure after the numeral. They are also consistent with the app's other bracket, "(7)": brackets mean "a non-chord-tone decoration of this chord". **Keep.**
- `V7(4–3)` is clear in meaning but, as drawn, the "7" prints flat at numeral size (see section 4). Render it as V⁷(4–3).
- `V6(2–3)` is the weakest of the three. On the beat the bass is still G, so "V6" describes the chord *after* the bass falls, and a student can easily read the "6" and "2–3" as one figure ("six-two-three"). It is acceptable notation (Kostka–Payne write the bass suspension as 2–3 under V⁶), but add "(2–3) = bass suspension: the bass is held over and falls" to the legend, and stack the 6.
- Whatever style you choose, apply it everywhere: D3 (I6(7–6)) and D4 (I(9–8)) need it. Stacked ⁴⁻³ figures are not necessary for students. The bracket form is fine once the renderer stacks the inversion figure.

## 8. Recommendations, in priority order

1. Jesu cadence bar 8: `V(7)/III – III` → `V/III – III`. Better, align it with the numeral row: `VII – III (V–I in G major)` (D1, D6).
2. Jesu bar 11: `vii°6/iv`, `vii°43/iv` → `vii°6/IV`, `vii°43/IV`. Adopt the as-it-sounds rule for applied-chord targets. If adopted, Jesu 10.1 becomes `vii°65/v` (D2, D7).
3. BWV 269 bar 12: replace `iii7` + `I6` with one `I6(7–6)`. Bar 15.2: `I` → `I(9–8)` (D3, D4).
4. Jesu bar 8.1: `IV65` (PD) → `V⁶₅/VII` (C) (D5).
5. Renderer: stack the figure in `V7(4–3)` and `V6(2–3)`. Legend: add "(2–3) a bass suspension".
6. Remove the duplicate `I6` at BWV 269 L66F1. Give a second label that shares an anchor its own beat-2 anchor.
7. Ask Justin to approve the blue-grey W/S class explicitly (recommended: keep it). Optionally run a proper CVD check on violet vs blue-grey.
8. Optional:
   - O Haupt 10.1: note that V⁶₅/ii resolves to E major (V/V).
   - O Haupt 5.4: "vii°6 (V⁴₃)".
   - Op. 28/20 bar 4: notation "V⁷♭⁵/V".
   - Consistent cadence titles: "(V7–I)" vs "(V–I)"; "V–i" in minor.

## 9. Comparison with the builder's report (read after my readings)

- **We agree on:**
  - all the register items: O Haupt vii°6/vi, V/ii, V65/V, V/V, iiø42/ii; Jesu ♯vi°6, vii°65/V, the added ° and ø;
  - all six no-third relabellings;
  - O Haupt bar 8 not being Phrygian;
  - O Haupt 6 V43;
  - II6 at O Haupt 9.2;
  - every piano-score cadence;
  - R9 and R17 in full.
- **We disagree on:**
  - **Jesu bar 8 "V(7)/III".** The builder's evidence ("soprano G on the second quaver is a passing 7th") is a factual error: G is a 4th above D.
  - **/iv vs /IV.** The builder flagged this as a judgement and chose the home-key case. I judge that wrong because it contradicts the adjacent IV6.
  - **BWV 269 bars 12 and 15.** The builder's own evidence column names the 7–6 and the 9–8, but the labels don't show them, against the spec's "suspensions labelled".
  - **IV65.** The builder offers V⁶₅/VII as "also correct". I recommend it, for consistency with O Haupt's V⁶₅/V.
- The builder's "Judgements for Justin" 1–9 are fair framings. My answers are in sections 2, 4 and 7.
- The builder's note that the colours were never looked at on screen is now covered: I rendered them and confirmed every fill matches its `f`.

## Artefacts

- `/home/claude/checks/ic_r8/kparse.py`, `dump.py`, `cads.py`, `anchors.py`, `render.py`, `pos.py`: the scripts.
- `/home/claude/checks/ic_r8/render.json`: drawn numerals, fills, legend and the R9 output.
- `/home/claude/checks/ic_r8/shots/`: full-page renders of the three chorales and crops of the shared-anchor spots.
