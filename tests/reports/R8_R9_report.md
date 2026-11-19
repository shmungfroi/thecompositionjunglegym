# R8, R9 (and R17) report: 0.48 correction register

Branch `048-r8r9`, from 0.47 (`ef97cdb`). Worktree `/home/claude/wt-r8r9`.

## R8: Analysis numerals and cadence labels re-read from the notes

### Method

`tests/numeral_reread.py` (re-runnable: `python3 tests/numeral_reread.py` checks `scores/meta.json`, `--write` writes, `--table` prints the table below).

1. **Reading the notes.** Each chorale's Humdrum file in `scores/src/` is read line by line. Every data line is a time slice, and each voice's sounding note is spelled from its `**kern` token, so a C♯ stays a C♯. music21 then reads the same file on its own (`converter.parse` and `chordify`). Every slice has to hold exactly the pitches music21 finds at that offset, or the script stops. All slices of all three chorales match.
2. **The chord at each label.** A label is anchored to a note, `note-L<line>F<field>`. Its chord is the slice at that line, minus any non-chord tones. Each non-chord tone, suspension or changed line is listed in the script's `DECIDE` table with the reason, and those reasons are the evidence column below. Nothing else is set by hand.
3. **The generator.** This replaces the hand labels and fixes how the old labels went wrong. music21 gives the root, the 3rd, 5th and 7th above it, and the inversion. The generator then writes:
   - case from the 3rd;
   - `°` for a diminished triad or 7th, `ø` for half-diminished, `+` for augmented;
   - an accidental on an altered root (`♯vi°`). The leading-note chord of a minor key is not marked;
   - figures 6, 64, 7, 65, 43, 42;
   - an applied chord as V/x or vii°/x. This happens when the chord is not in the key (natural, harmonic or melodic minor) and acts as V or vii° of the next chord with a different root. The target takes the home key's case;
   - a suspension as `V(4–3)` (or `V6(2–3)` for the bass 2–3). That label names the chord the suspension resolves into, so the resolution is not labelled again.
4. **Passing 7ths.** A 7th on a weak quaver stays out of the harmony row, because it is a passing note. In the cadence chords it shows as `V(7) – I`.
5. **Function data (approved scope).** Every harmony label now carries `f`, and the harmony row colours the numeral with the app's `FN` colours:
   - T green, PD gold, D red;
   - C violet for applied, chromatic and altered chords;
   - W (the minor v, R9) and S (the subtonic VII of a minor key) in the app's blue-grey subtonic colour.

   A legend under the score explains the colours, `(7)` and `(4–3)`. The final major I of a minor-key piece (Picardy third) stays T. A major I inside a minor-key phrase is C.
6. **Renderer.** In the harmony row, figures now stack before an applied chord's target (V⁶₅/V). Before, they only stacked at the end of a label, so `vii°65/vi` would have printed flat.

Only the three chorales have harmony labels. The scores have no labels baked into their SVGs: labels are overlays drawn from `meta.json`, so R8 needed no re-engraving. The cadence chords of K. 331 (theme and Var. III), Op. 28/7 and Op. 28/20 were checked against music21's chordify of the cadence bars. All agree with the notes: I⁶₄–V; V7–I after I⁶₄; i⁶₄–V(–i); vii°7/V–V; V7–I; V7/V–V; V7–i. They are unchanged.

### Every label checked (141 labels; 26 relabelled, 4 removed as the resolution of a suspension label; changes in bold)

Bar = the app's bar number ("upbeat" = the upbeat to a phrase). Line = the Humdrum line of the anchor note. f = the new function code.

| Score | Bar | Line | Notes (bass up) | Old | New | f | Evidence from the notes |
|---|---|---|---|---|---|---|---|
| chorale | upbeat | 23 | G2 B3 D4 G4 | I | I | T | agrees with the notes |
| chorale | 1 | 25 | G3 B3 D4 G4 | I | I | T | agrees with the notes |
| chorale | 1 | 26 | E3 C4 E4 G4 | IV6 | IV6 | PD | agrees with the notes |
| chorale | 1 | 28 | F♯3 A3 D4 D5 | V6 | V6 | D | agrees with the notes |
| chorale | 2 | 30 | G3 D4 B4 | I | I | T | agrees with the notes |
| chorale | 2 | 31 | D3 F♯3 D4 B4 | iii6 | iii6 | T | agrees with the notes |
| chorale | 2 | 33 | E3 G3 B3 G4 | vi | vi | T | agrees with the notes |
| chorale | 3 | 35 | C3 C4 E4 G4 | IV | IV | PD | agrees with the notes |
| chorale | 3 | 37 | B2 C4 E4 G4 | IV42 | IV42 | PD | agrees with the notes |
| chorale | 3 | 39 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 4 | 41 | D3 D4 F♯4 A4 | V | V | D | agrees with the notes |
| chorale | 4 | 42 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 5 | 44 | F♯2 A3 D4 D5 | V6 | V6 | D | agrees with the notes |
| chorale | 5 | 45 | G2 B3 E4 D5 | vi65 | vi65 | T | agrees with the notes |
| chorale | 5 | 46 | A2 C4 F♯4 C5 | vii6 | **vii°6** | D | F♯–A–C over A: a diminished triad, so ° |
| chorale | 6 | 48 | B2 D4 G4 B4 | I6 | I6 | T | agrees with the notes |
| chorale | 6 | 49 | C3 E4 G4 A4 | ii65 | ii65 | PD | agrees with the notes |
| chorale | 6 | 50 | D3 D4 F♯4 A4 | V | V | D | agrees with the notes |
| chorale | 7 | 53 | G2 B3 D4 G4 | I | I | T | agrees with the notes |
| chorale | upbeat | 57 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 8 | 59 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 8 | 61 | A2 C4 E4 C5 | ii | ii | PD | agrees with the notes |
| chorale | 8 | 63 | B2 B3 G4 D5 | I6 | I6 | T | agrees with the notes |
| chorale | 9 | 66 | B2 B3 G4 D5 | I6 | I6 | T | agrees with the notes |
| chorale | 9 | 66 | B2 B3 G4 D5 | I6 | I6 | T | agrees with the notes |
| chorale | 9 | 70 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 10 | 73 | D3 D4 F♯4 A4 | V | V | D | agrees with the notes |
| chorale | 10 | 74 | E3 B3 E4 G4 | vi | vi | T | agrees with the notes |
| chorale | 11 | 76 | E3 G3 E4 B4 | vi | vi | T | agrees with the notes |
| chorale | 11 | 77 | D3 B3 F♯4 B4 | iii6 | iii6 | T | agrees with the notes |
| chorale | 11 | 79 | C3 E4 A4 C5 | ii6 | ii6 | PD | agrees with the notes |
| chorale | 12 | 81 | B2 D4 A4 D5 | iii7 | iii7 | T | agrees with the notes |
| chorale | 12 | 82 | B2 D4 G4 D5 | I6 | I6 | T | second chord of the beat: alto A falls to G over B (7–6): G–B–D over B |
| chorale | 12 | 84 | D3 D4 G4 C5 | iv | **V7(4–3)** | D | D–D–G–C: alto G is held over from the previous beat (prepared) and falls to F♯ on the next quaver: D–F♯–A–C with a 4–3 suspension. No 3rd on the beat, so not a minor iv |
| chorale | 13 | 87 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 13 | 89 | B2 D4 G4 B4 | I6 | I6 | T | agrees with the notes |
| chorale | 13 | 90 | G2 D4 F4 B4 | I7 | **V7/IV** | C | G–B–D–F (F natural on the beat, alto) resolving to C major: V7 of IV, as the cadence label already said; "I7" hid the F♮ |
| chorale | 14 | 93 | C3 C4 E4 G4 | IV | IV | PD | agrees with the notes |
| chorale | 14 | 94 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 15 | 96 | F♯2 D4 A4 D5 | V6 | V6 | D | agrees with the notes |
| chorale | 15 | 98 | G2 B3 A4 D5 | I | I | T | alto A is held over from the previous chord (9–8 suspension, falls to G) |
| chorale | 15 | 100 | A2 C4 F♯4 C5 | vii6 | **vii°6** | D | F♯–A–C over A: diminished, so ° |
| chorale | 16 | 102 | B2 D4 G4 B4 | I6 | I6 | T | agrees with the notes |
| chorale | 16 | 103 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 16 | 104 | D3 D4 F♯4 A4 | V | V | D | agrees with the notes |
| chorale | 17 | 107 | E3 B3 F♯4 G4 | vi | vi | T | alto F♯ is a 9–8 suspension tied over from bar 16, resolving to E on the next quaver |
| chorale | 17 | 109 | C3 C4 E4 G4 | IV | IV | PD | agrees with the notes |
| chorale | 17 | 111 | G2 A2 D4 G4 B4 | I | I | T | bass A on the beat is a passing note (C–B–A–G); the chord is G–B–D, G arriving in the bass on the next quaver |
| chorale | 18 | 114 | D3 D4 F♯4 A4 | V | V | D | agrees with the notes |
| chorale | 18 | 115 | G3 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 19 | 117 | G3 D4 A4 D5 | i | **V6(2–3)** | D | G–D–A–D: the bass G is tied from the previous I and falls to F♯ (a bass 2–3 suspension); the upper voices D–A–D are the dominant. No 3rd above G, so not a minor i |
| chorale | 19 | 118 | F♯3 D4 A4 D5 | V6 | **(removed: V6, covered by the suspension label)** | D | resolution of the bass 2–3 at line 117 (D–F♯–A over F♯); the suspension label names it |
| chorale | 19 | 119 | E3 E4 G4 C5 | IV6 | IV6 | PD | agrees with the notes |
| chorale | 20 | 122 | E3 E4 G4 B4 | vi | vi | T | agrees with the notes |
| chorale | 20 | 124 | C3 E4 G4 A4 | ii65 | ii65 | PD | agrees with the notes |
| chorale | 20 | 125 | D3 D4 F♯4 A4 | V | V | D | agrees with the notes |
| chorale | 21 | 128 | G2 B3 D4 G4 | I | I | T | agrees with the notes |
| ohaupt | upbeat | 22 | D3 A3 D4 F♯4 | I | I | T | agrees with the notes |
| ohaupt | 1 | 24 | G3 D4 B4 | IV | IV | PD | agrees with the notes |
| ohaupt | 1 | 25 | F♯3 A3 D4 A4 | I6 | I6 | T | agrees with the notes |
| ohaupt | 1 | 26 | B2 B3 D4 G4 | IV6 | IV6 | PD | agrees with the notes |
| ohaupt | 1 | 28 | D3 A3 E4 F♯4 | I | I | T | agrees with the notes |
| ohaupt | 2 | 31 | G2 B3 D4 E4 | ii65 | ii65 | PD | agrees with the notes |
| ohaupt | 2 | 32 | A2 A3 C♯4 E4 | V | V | D | agrees with the notes |
| ohaupt | 2 | 33 | D3 A3 D4 F♯4 | I | I | T | agrees with the notes |
| ohaupt | 2 | 34 | C♯3 A♯3 E4 C♯5 | v6 | **vii°6/vi** | C | A♯–C♯–E over C♯: diminished, A♯ is the leading note of B minor and resolves to B minor: vii°6/vi. "v6" dropped the ♯ and the ° |
| ohaupt | 3 | 36 | B2 B3 D4 D5 | vi | vi | T | agrees with the notes |
| ohaupt | 3 | 38 | D3 B3 F♯4 D5 | vi6 | vi6 | T | agrees with the notes |
| ohaupt | 3 | 40 | F♯3 B3 F♯4 C♯5 | vi64 | **V(4–3)/vi** | C | F♯–B–F♯–C♯: tenor B is held from the previous chord and falls to A♯ (4–3); the 6th of a 6/4 (D) is absent, so this is V of B minor with a suspended 4th, not vi⁶₄ |
| ohaupt | 3 | 42 | F♯2 A♯3 F♯4 C♯5 | III | **(removed: V/vi, covered by the suspension label)** | C | resolution of the 4–3 at line 40 (F♯–A♯–C♯ = V/vi, with a passing E); "III" hid the A♯ and the B-minor cadence |
| ohaupt | 4 | 45 | B2 B3 D4 B4 | vi | vi | T | agrees with the notes |
| ohaupt | upbeat | 49 | B2 B3 F♯4 D5 | vi | vi | T | agrees with the notes |
| ohaupt | 5 | 52 | E3 G3 E4 C♯5 | vii6 | **vii°6** | D | C♯–E–G over E: diminished, so ° |
| ohaupt | 5 | 54 | F♯3 D4 F♯4 A4 | I6 | I6 | T | agrees with the notes |
| ohaupt | 5 | 56 | G3 B3 D4 B4 | IV | IV | PD | agrees with the notes |
| ohaupt | 5 | 58 | E3 G3 G4 C♯5 | vii6 | **vii°6** | D | C♯–E–G over E (tenor A arrives on the second quaver): diminished, so ° |
| ohaupt | 6 | 61 | D3 B3 G4 D5 | IV64 | IV64 | PD | agrees with the notes |
| ohaupt | 6 | 62 | D3 A3 F♯4 D5 | I | I | T | second label of the bar: the 6/4 neighbour returns to D–A–F♯–D on beat 2 |
| ohaupt | 6 | 64 | D3 A3 F♯4 D5 | I | I | T | agrees with the notes |
| ohaupt | 6 | 65 | D3 D4 F♯4 A4 | I | I | T | agrees with the notes |
| ohaupt | 7 | 67 | G3 D4 G4 B4 | IV | IV | PD | agrees with the notes |
| ohaupt | 7 | 69 | E3 C4 F♯4 A4 | iii42 | **iiø42/ii** | C | E–C–F♯–A: F♯–A–C–E over E is the half-diminished ii of E minor in 4/2 (the bass then dips to D♯, vii°7 of E minor, before E minor arrives). C natural, so not iii⁴₂ of D major |
| ohaupt | 7 | 71 | E3 B3 F♯4 G4 | ii | ii | PD | alto F♯ is re-struck over E–G–B and falls to E: an appoggiatura (9–8) |
| ohaupt | 7 | 73 | G3 B3 E4 G4 | ii6 | ii6 | PD | agrees with the notes |
| ohaupt | 8 | 76 | B3 D♯4 F♯4 | VI | **V/ii** | C | B–D♯–F♯: B major, the V of E minor (ii of D). VI of D would be B minor |
| ohaupt | 8 | 77 | G♯3 B3 E4 D5 | II65 | **V65/V** | C | E–G♯–B–D over G♯, resolving to A: V⁶₅ of V |
| ohaupt | 9 | 79 | A3 E4 C♯5 | V | V | D | agrees with the notes |
| ohaupt | 9 | 81 | G♯3 B3 E4 E5 | II6 | II6 | C | agrees with the notes |
| ohaupt | 9 | 82 | F♯3 A3 F♯4 D5 | I6 | I6 | T | agrees with the notes |
| ohaupt | 9 | 84 | E3 C♯4 A4 C♯5 | V64 | V64 | D | agrees with the notes |
| ohaupt | 10 | 87 | D♯3 F♯4 A4 B4 | VI65 | **V65/ii** | C | B–D♯–F♯–A over D♯, resolving to E: V⁶₅ of ii |
| ohaupt | 10 | 88 | E3 E4 G♯4 B4 | II | **V/V** | C | E–G♯–B, resolving to A at the cadence: V/V (register item) |
| ohaupt | 10 | 89 | A2 E4 A4 C♯5 | V | V | D | agrees with the notes |
| ohaupt | 10 | 90 | D3 A3 D4 F♯4 | I | I | T | agrees with the notes |
| ohaupt | 11 | 93 | E3 G3 B3 G4 | ii | ii | PD | agrees with the notes |
| ohaupt | 11 | 95 | F♯3 A3 D4 F♯4 | I6 | I6 | T | agrees with the notes |
| ohaupt | 11 | 97 | A3 D4 E4 | i64 | **V(4–3)** | D | A–A–D–E: the alto D falls (through B) to C♯ on beat 4: V with a 4–3 suspension. No F♯, so not a 6/4 of D, and never a minor i |
| ohaupt | 11 | 99 | A2 A3 C♯4 A4 | V | **(removed: V, covered by the suspension label)** | D | resolution of the 4–3 at line 97: A major, the label V(4–3) names it |
| ohaupt | 12 | 101 | D3 A3 D4 F♯4 | I | I | T | agrees with the notes |
| jesu | 1 | 23 | E3 E4 G4 B4 | i | i | T | agrees with the notes |
| jesu | 1 | 25 | G3 D4 G4 B4 | III | III | T | agrees with the notes |
| jesu | 1 | 27 | C3 C4 E4 A4 | iv6 | iv6 | PD | agrees with the notes |
| jesu | 1 | 29 | E3 B3 E4 G4 | i | i | T | agrees with the notes |
| jesu | 2 | 31 | A2 C4 E4 F♯4 | ii65 | **iiø65** | PD | F♯–A–C–E over A: half-diminished, so ø |
| jesu | 2 | 32 | B2 B3 D♯4 F♯4 | V | V | D | agrees with the notes |
| jesu | 2 | 34 | E3 G3 B3 E4 | i | i | T | agrees with the notes |
| jesu | 3 | 36 | E3 E4 G4 B4 | i | i | T | agrees with the notes |
| jesu | 3 | 38 | G3 D4 G4 B4 | III | III | T | agrees with the notes |
| jesu | 3 | 39 | F♯3 A3 A4 C♯5 | ii | ii | PD | agrees with the notes |
| jesu | 3 | 41 | A3 C4 F♯4 D♯5 | vii43 | **vii°43** | D | D♯–F♯–A–C over A: fully diminished 7th, so ° |
| jesu | 4 | 43 | G♯3 B3 E4 E5 | I6 | I6 | C | agrees with the notes |
| jesu | 4 | 44 | A♯3 C♯4 F♯4 E5 | II65 | **V65/V** | C | F♯–A♯–C♯–E over A♯, resolving to B: V⁶₅ of V |
| jesu | 4 | 45 | B3 F♯4 D♯5 | V | V | D | agrees with the notes |
| jesu | 5 | 47 | G3 B3 G4 E5 | i6 | i6 | T | agrees with the notes |
| jesu | 5 | 49 | E3 E4 B4 G5 | i | i | T | agrees with the notes |
| jesu | 5 | 50 | B3 E4 B4 F♯5 | i64 | **V(4–3)** | D | B–E–B–F♯: tenor E falls to D♯ on beat 4 (4–3); no G, so not a minor i⁶₄ |
| jesu | 5 | 51 | B2 D♯4 A4 F♯5 | V7 | V7 | D | agrees with the notes |
| jesu | 6 | 54 | E3 B3 G4 E5 | i | i | T | agrees with the notes |
| jesu | 7 | 58 | E3 E4 G4 B4 | i | i | T | agrees with the notes |
| jesu | 7 | 60 | G3 B3 E4 B4 | i6 | i6 | T | agrees with the notes |
| jesu | 7 | 62 | C3 A3 E4 C5 | iv6 | iv6 | PD | agrees with the notes |
| jesu | 7 | 64 | E3 G3 G4 B4 | i | i | T | agrees with the notes |
| jesu | 8 | 66 | C♯3 E4 G4 A4 | IV65 | IV65 | PD | agrees with the notes |
| jesu | 8 | 67 | D3 D4 F♯4 A4 | VII | VII | S | agrees with the notes |
| jesu | 8 | 69 | G2 B3 D4 G4 | III | III | T | agrees with the notes |
| jesu | 9 | 71 | G3 D4 G4 B4 | III | III | T | agrees with the notes |
| jesu | 9 | 73 | E3 E4 G4 C♯5 | vi6 | **♯vi°6** | C | E–E–G–C♯: C♯–E–G over E, C♯ the raised 6th of E minor; it leads to F♯–A♯–D, so it is not vii° of the next chord: ♯vi°6 (ii°6 of B minor) |
| jesu | 9 | 74 | F♯3 A♯3 F♯4 D5 | VII6 | **VII+6** | C | F♯–A♯–D (A♯, not A): D–F♯–A♯ is an augmented triad, so VII+6, a chromatic chord. "VII6" (D–F♯–A) is not what sounds |
| jesu | 9 | 76 | D3 B3 F♯4 B4 | v6 | v6 | W | agrees with the notes |
| jesu | 10 | 78 | C♯3 A♯3 G4 E5 | iv65 | **vii°65/V** | C | A♯–C♯–E–G over C♯, resolving to B: vii°⁶₅ of V (register item) |
| jesu | 10 | 79 | D3 B3 F♯4 D5 | v6 | v6 | W | agrees with the notes |
| jesu | 10 | 81 | F♯3 B3 F♯4 C♯5 | v64 | **V(4–3)/V** | C | F♯–B–F♯–C♯: tenor B falls to A♯ on the next beat (4–3); no D, so not v⁶₄: V of V (F♯ major) with a suspended 4th |
| jesu | 10 | 82 | F♯3 A♯3 F♯4 C♯5 | II | **(removed: V/V, covered by the suspension label)** | C | beat 4 of bar 10: F♯–A♯–F♯–C♯ (alto E on the last quaver is a passing 7th), resolving to B major in bar 11: the resolution of the 4–3, so covered by V(4–3)/V |
| jesu | 11 | 85 | B2 F♯3 D♯4 B4 | V | V | D | agrees with the notes |
| jesu | 11 | 86 | B2 G♯3 D4 B4 | iii6 | **vii°6/iv** | C | G♯–B–D over B: diminished, G♯ the leading note of A, leading to A (through vii°⁴₃/iv): vii°6/iv (register item) |
| jesu | 11 | 88 | D3 G♯3 F4 B4 | iii43 | **vii°43/iv** | C | G♯–B–D–F over D, resolving to A–C♯–E: vii°⁴₃ of iv (register item). The A chord that follows has C♯ (IV6), see judgements |
| jesu | 12 | 90 | C♯3 A3 E4 A4 | IV6 | IV6 | PD | agrees with the notes |
| jesu | 12 | 92 | E3 B3 G4 | i | i | T | agrees with the notes |
| jesu | 12 | 94 | A♯2 C♯4 E4 F♯4 | II65 | **V65/V** | C | F♯–A♯–C♯–E over A♯, resolving to B: V⁶₅ of V |
| jesu | 12 | 95 | B2 B3 D♯4 F♯4 | V | V | D | agrees with the notes |
| jesu | 13 | 98 | E2 G♯3 B3 E4 | I | I | T | agrees with the notes |

### Cadence chords (18 in the chorales; 9 changed)

| Score | Bar | Old | New | Evidence |
|---|---|---|---|---|
| chorale | 7 | V – I | **V(7) – I** | tenor C on the second quaver of V (D–C–B) is a passing 7th |
| chorale | 21 | V – I | **V(7) – I** | tenor C on the second quaver of V is a passing 7th |
| chorale | 4, 10, 18 | I – V (×3) | I – V | agree |
| chorale | 14 | V7/IV – IV | V7/IV – IV | alto F on the beat: a real 7th; agrees (the harmony row now says V7/IV too, not I7) |
| ohaupt | 2 | V – I | V – I | no 7th sounds; agrees |
| ohaupt | 4 | V/vi – vi | **V(7)/vi – vi** | F♯–A♯–C♯, alto E on the second quaver (F♯–E–D) is a passing 7th |
| ohaupt | 6 | V43 – I | V43 – I | the tenor A arrives on the second quaver of the vii°6 beat: V⁴₃; agrees |
| ohaupt | 8 | ii6 – VI | **ii6 – V/ii** | bar 7 beat 4: G–B–E–G = E minor over G (ii⁶ in D, i⁶ in E minor), bass passing A. Bar 8: B–B–D♯–F♯ = B major, V of E minor (V/ii in D). Not VI, because VI of D is B minor. Text now "Imperfect (half) cadence in E minor (i⁶–V there; the bass rises G–A–B, so not a Phrygian cadence)" |
| ohaupt | 10 | II – V | **V/V – V** | E–E–G♯–B resolving to A (register item) |
| ohaupt | 12 | V – I | V – I | no 7th; agrees |
| jesu | 2 | V – i | **V(7) – i** | tenor A on the second quaver of V (B–A–G) is a passing 7th |
| jesu | 4 | V65/V – V | V65/V – V | agrees |
| jesu | 6 | V7 – i | V7 – i | alto A on beat 4 is a real 7th (a crotchet on the beat); agrees |
| jesu | 8 | V/III – III | **V(7)/III – III** | D–D–F♯–A, soprano G on the second quaver is a passing 7th |
| jesu | 11 | V7/V – V | **V(7)/V – V** | F♯–A♯–C♯, alto E on the last quaver (F♯–E–D♯) is a passing 7th, not a chord 7th |
| jesu | 13 | V – I | **V(7) – I** | tenor A on the second quaver of V (B–A–G♯) is a passing 7th |

**O Haupt bar 8, settled:** E minor i⁶ goes to V, written ii⁶ – V/ii in D. It is **not** a Phrygian cadence. A Phrygian cadence is iv⁶–V in minor, with the bass falling a semitone. Here the bass rises G–A–B.

**The independent check's list, confirmed by the notes:**
- O Haupt bar 2: v6 → vii°6/vi.
- Jesu bar 9: vi6 → ♯vi°6.
- Jesu bar 10: iv65 → vii°65/V.
- Jesu bar 11: iii6 → vii°6/iv and iii43 → vii°43/iv.
- vii43 and vii6 now have ° (Jesu bar 3; BWV 269 bars 5, 15; O Haupt bar 5 twice).

**No-third chords given lowercase numerals.** The check counted three. There are six:
- BWV 269 bar 12 "iv" (D–G–C): a 4–3 suspension.
- BWV 269 bar 19 "i" (G–D–A): a bass 2–3 suspension.
- O Haupt bar 3 "vi64" (F♯–B–C♯): 4–3.
- O Haupt bar 11 "i64" (A–D–E): 4–3.
- Jesu bar 5 "i64" (B–E–F♯): 4–3.
- Jesu bar 10 "v64" (F♯–B–C♯): 4–3.

Each is now named by the chord it resolves into, with the suspension shown.

## R9: function labels (`chordInfo`, `analyse`, chord library, Keys room)

Changes in `index.html`:
- **`analyse()`.** The minor v (no leading note) gets the new function code `W`. A vii° or vii°7 in a major key that carries the leading note gets `D`; before, the borrowed vii°7 was C, colour.
- **`chordInfo().dom`.** Now true for diatonic V or vii° with the leading note, as before, and also for chords that `analyse()` marks D. So the major key's vii°7 is dominant. The minor v / v7 and VII / VII7 are still not dominant, which keeps P2-4 as it was.
- **`FNAME.W`** = "minor v · weak pull (no leading note)". Before, the minor v read "pull · dominant".
- **`FTXT.W`.** Explains the minor v in the chord library's key context. **`FN.W`** uses the blue-grey of the subtonic (S).
- **`homes()`.** The chord library's key chips no longer call the minor v dominant.
- **Keys room scale chords.** The natural or melodic minor v is now W, not D, and VII is S, not D. That is the same fault, so it is fixed in the same way.

Tests, added to `tests/unit_test.py` (section R9):
- `chordInfo()` on every degree of major and minor, with triads and 7ths, in 5 major and 5 minor keys, each in 3 inversions.
- It asserts the function code, `dom`, the FNAME text for the minor v, and that no non-D chord reads "· dominant".
- The P2-4 test no longer skips vii°7 in major: it now asserts dom = true.

Against 0.47 the new tests fail, for example "maj0 vii°7: dom=False, expected True" and "function C (colour), expected D".

## Suite results (R8 + R9 commit)

| Suite | Result |
|---|---|
| unit (`tests/run_all unit`) | pass, 637 checks, 0 failures |
| content_lint | pass |
| analysis_engrave | pass, 0 failures (70 views, 1899 overlay labels, 210 cadence tags, 2,492,409 text–notehead pairs). The first run, before suspension labels covered their resolutions, failed E on the phone (the Jesu bar 9 label pushed past the frame). A second run timed out waiting for the score under machine load (other agents testing) and passed when run again. |
| pageerrors | pass, 0 errors (153 views, 4244 clicks, 881 random clicks) |
| `tests/numeral_reread.py` | 137 labels and 18 cadences, 0 differences |

## Judgements for Justin

1. **Colours for W and S.** The minor v (W) and the subtonic VII (S) share the app's existing blue-grey. The approval named four colours (T, PD, D, colour). These two do not fit any of the four, and R9 says the minor v is not D. Do you want them violet instead?
2. **Suspension labels.** I wrote them as `V(4–3)`, `V7(4–3)`, `V(4–3)/vi` and `V6(2–3)`, and the resolution chord is not labelled again. An alternative is stacked ⁴⁻³ figures, which would need renderer work.
3. **O Haupt bar 7 (line 69).** E–C–F♯–A is labelled iiø⁴₂/ii: half-diminished ii of E minor over an E bass. The bass then dips to D♯, which briefly makes vii°7/ii. Either reading fits; I used what sounds on the beat.
4. **O Haupt bar 9 (line 81), "II6".** E major over G♯ goes on to D/F♯, not A, so it is not applied. It stays II6 (colour), while the same chord in bar 10 resolves and is V/V.
5. **Jesu bar 8, "IV65"** (A–C♯–E–G resolving to D, then G). It is kept as IV⁶₅ (predominant, melodic-minor 6th). V⁶₅/VII would also be correct.
6. **Jesu bar 11, "vii°6/iv" and "vii°43/iv"** (as the register asked). The chord they lead to is A major (C♯), which is IV6. The target is written in the home key's case, iv.
7. **Jesu bar 9, "VII+6"** (D–F♯–A♯). This is a literal reading of the augmented chord. It could also be heard as V of B minor with the D as a 6th.
8. **O Haupt bar 5 (line 58), vii°6 before the cadence labelled V⁴₃–I.** The tenor A arrives on the second quaver. The row shows the beat's first chord and the cadence names the whole beat.
9. **The renderer still positions** "I6" and "I" labels that share an anchor with an earlier chord (BWV 269 bar 12; O Haupt bar 6) by spreading them. Their anchors were not moved.
