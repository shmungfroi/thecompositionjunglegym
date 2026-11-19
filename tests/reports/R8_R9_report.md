# R8, R9 and R17 report: 0.48 correction register

Branch `048-r8r9`, from 0.47 (`ef97cdb`). Worktree `/home/claude/wt-r8r9`.

## R8: Analysis numerals and cadence labels re-read from the notes

### Method

`tests/numeral_reread.py` is re-runnable. `python3 tests/numeral_reread.py` checks `scores/meta.json` against the notes, `--write` writes, and `--table` prints the tables below. After the independent check (`/home/claude/checks/IC_R8_R9_R17.md`), the fixes in the "Independent check" section were made in the generator, not by hand.

1. **Reading the notes.** Each chorale's Humdrum file in `scores/src/` is read line by line. Each data line is a time slice, and each voice's note is spelled from its `**kern` token. music21 reads the same file on its own (`converter.parse` + `chordify`), and every slice must hold the pitches music21 finds at that offset, or the script stops. All slices match.
2. **The chord at each label.** A label hangs on a note, `note-L<line>F<field>`. Its chord is that line's slice, minus non-chord tones. Each non-chord tone, suspension, changed line or applied target is listed in `DECIDE` with its reason; these are the evidence column below. Nothing else is set by hand.
3. **The generator.**
   - music21 gives the root, the 3rd, 5th and 7th above it, and the inversion.
   - Case comes from the 3rd.
   - Diminished gets °, half-diminished ø, augmented +.
   - An altered root carries its accidental (♯vi°). The leading-note chord of a minor key is not marked.
   - Figures are 6, 64, 7, 65, 43, 42.
4. **Applied chords.** A chord is applied if it leans on a leading note that is outside the key's natural scale (or is not in the key at all) and resolves as V or vii° to the next chord with a different root. So A–C♯–E–G → D in E minor is V⁶₅/VII. The target is written as the chord actually reached (A major: /IV; B minor: /v). The one exception: if the chord reached is itself applied, the home key's case is used, so O Haupt bar 10 stays V⁶₅/ii, not V⁶₅/V/V.
5. **Suspensions.** A suspension is named by the chord it resolves into, with its figure: V(4–3), V7(4–3), V6(2–3) (bass), I6(7–6), I(9–8). The resolution is not labelled again. A label repeated on the same note is dropped.
6. **Cadence chords.** These are generated from the harmony labels: the arrival chord's label, and the resolved chord of the label before it. `(7)` is added only when a **minor 7th above that chord's root** sounds after its onset and before the arrival. The checker found the earlier hand table had counted a 4th as a 7th in Jesu bar 8; the generated rule cannot do that. One decision: O Haupt bar 6 reads the chord before the arrival from bar 5 beat 4 (V⁴₃), because the label in between is a neighbour 6/4.
7. **Function data.** Every harmony label carries `f`, and the harmony row colours it with the app's `FN` colours:
   - T green, PD gold, D red;
   - C violet: applied, chromatic and altered chords;
   - W (minor v) and S (subtonic VII of a minor key): blue-grey, the app's existing subtonic colour. This awaits Justin.

   The final major I of a minor-key piece (Picardy) is T. A major I inside a minor phrase is C. The legend under the score explains the colours and the brackets: (7) a passing 7th; (4–3), (7–6), (9–8) a suspension; (2–3) a bass suspension.
8. **Renderer.** In the harmony row, the inversion figures now stack before a suspension bracket or an applied target: V⁷(4–3), V⁶(2–3), I⁶(7–6), V⁶₅/V. Before the check's fix, V7(4–3) and V6(2–3) printed flat.

Only the three chorales have harmony labels. Labels are overlays drawn from `meta.json`, not part of the engraved SVGs, so R8 needed no re-engraving. The cadence chords of K. 331 (theme, Var. III), Op. 28/7 and Op. 28/20 were checked once by hand with music21 chordify, and the independent check agreed: no change. `numeral_reread.py` only re-checks the chorale cadences.

### Every label checked, against 0.47 (141 labels: 29 relabelled, 6 removed; changes in bold)

Bar = the app's bar ("upbeat" = upbeat to a phrase). Line = the Humdrum line of the anchor note. f = function. O Haupt bar 6, the second label "I", keeps its text but moves its anchor to the tenor A where its chord starts (note-L62F2, was L61F1), so it no longer crowds the IV⁶₄ label.

| Score | Bar | Line | Notes (bass up) | 0.47 | New | f | Evidence from the notes |
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
| chorale | 9 | 66 | B2 B3 G4 D5 | I6 | I6 | T | the same I6 twice on one note (duplicate data); one kept |
| chorale | 9 | 66 | B2 B3 G4 D5 | I6 | **(removed: I6, covered by the label before it)** | T | the same I6 twice on one note (duplicate data); one kept |
| chorale | 9 | 70 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 10 | 73 | D3 D4 F♯4 A4 | V | V | D | agrees with the notes |
| chorale | 10 | 74 | E3 B3 E4 G4 | vi | vi | T | agrees with the notes |
| chorale | 11 | 76 | E3 G3 E4 B4 | vi | vi | T | agrees with the notes |
| chorale | 11 | 77 | D3 B3 F♯4 B4 | iii6 | iii6 | T | agrees with the notes |
| chorale | 11 | 79 | C3 E4 A4 C5 | ii6 | ii6 | PD | agrees with the notes |
| chorale | 12 | 81 | B2 D4 A4 D5 | iii7 | **I6(7–6)** | T | B–D–A–D: the alto A is prepared (sounds in the chord before) and falls to G on the next quaver over the same B: a 7–6 suspension over I6. B–D–A has no F♯, so it is not a iii7 chord |
| chorale | 12 | 82 | B2 D4 G4 D5 | I6 | **(removed: I6, covered by the label before it)** | T | the resolution of the 7–6 (G–B–D over B): covered by I6(7–6) |
| chorale | 12 | 84 | D3 D4 G4 C5 | iv | **V7(4–3)** | D | D–D–G–C: alto G is held over from the previous beat (prepared) and falls to F♯ on the next quaver: D–F♯–A–C with a 4–3 suspension. No 3rd on the beat, so not a minor iv |
| chorale | 13 | 87 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 13 | 89 | B2 D4 G4 B4 | I6 | I6 | T | agrees with the notes |
| chorale | 13 | 90 | G2 D4 F4 B4 | I7 | **V7/IV** | C | G–B–D–F (F natural on the beat, alto) resolving to C major: V7 of IV, as the cadence label already said; "I7" hid the F♮ |
| chorale | 14 | 93 | C3 C4 E4 G4 | IV | IV | PD | agrees with the notes |
| chorale | 14 | 94 | G2 D4 G4 B4 | I | I | T | agrees with the notes |
| chorale | 15 | 96 | F♯2 D4 A4 D5 | V6 | V6 | D | agrees with the notes |
| chorale | 15 | 98 | G2 B3 A4 D5 | I | **I(9–8)** | T | G–B–A–D: the alto A is held over (dotted) from the V6 on beat 1 and falls to G on the next quaver over the same G bass: I with a 9–8 suspension |
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
| chorale | 19 | 118 | F♯3 D4 A4 D5 | V6 | **(removed: V6, covered by the label before it)** | D | resolution of the bass 2–3 at line 117 (D–F♯–A over F♯); the suspension label names it |
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
| ohaupt | 3 | 42 | F♯2 A♯3 F♯4 C♯5 | III | **(removed: V/vi, covered by the label before it)** | C | resolution of the 4–3 at line 40 (F♯–A♯–C♯ = V/vi, with a passing E); "III" hid the A♯ and the B-minor cadence |
| ohaupt | 4 | 45 | B2 B3 D4 B4 | vi | vi | T | agrees with the notes |
| ohaupt | upbeat | 49 | B2 B3 F♯4 D5 | vi | vi | T | agrees with the notes |
| ohaupt | 5 | 52 | E3 G3 E4 C♯5 | vii6 | **vii°6** | D | C♯–E–G over E: diminished, so ° |
| ohaupt | 5 | 54 | F♯3 D4 F♯4 A4 | I6 | I6 | T | agrees with the notes |
| ohaupt | 5 | 56 | G3 B3 D4 B4 | IV | IV | PD | agrees with the notes |
| ohaupt | 5 | 58 | E3 G3 G4 C♯5 | vii6 | **vii°6** | D | C♯–E–G over E (tenor A arrives on the second quaver): diminished, so ° |
| ohaupt | 6 | 61 | D3 B3 G4 D5 | IV64 | IV64 | PD | agrees with the notes |
| ohaupt | 6 | 62 | D3 A3 F♯4 D5 | I | I | T | beat 2: the 6/4 neighbour returns to D–A–F♯–D; label moved to the tenor A (note-L62F2) where this chord starts |
| ohaupt | 6 | 64 | D3 A3 F♯4 D5 | I | I | T | agrees with the notes |
| ohaupt | 6 | 65 | D3 D4 F♯4 A4 | I | I | T | agrees with the notes |
| ohaupt | 7 | 67 | G3 D4 G4 B4 | IV | IV | PD | agrees with the notes |
| ohaupt | 7 | 69 | E3 C4 F♯4 A4 | iii42 | **iiø42/ii** | C | E–C–F♯–A: F♯–A–C–E over E is the half-diminished ii of E minor in 4/2 (the bass then dips to D♯, vii°7 of E minor, before E minor arrives). C natural, so not iii⁴₂ of D major |
| ohaupt | 7 | 71 | E3 B3 F♯4 G4 | ii | ii | PD | alto F♯ is re-struck over E–G–B and falls to E: an appoggiatura (9–8) |
| ohaupt | 7 | 73 | G3 B3 E4 G4 | ii6 | ii6 | PD | agrees with the notes |
| ohaupt | 8 | 76 | B3 D♯4 F♯4 | VI | **V/ii** | C | B–D♯–F♯: B major, the V of E minor (ii of D). VI of D would be B minor |
| ohaupt | 8 | 77 | G♯3 B3 E4 D5 | II65 | **V65/V** | C | E–G♯–B–D over G♯, resolving to A major: V⁶₅ of V |
| ohaupt | 9 | 79 | A3 E4 C♯5 | V | V | D | agrees with the notes |
| ohaupt | 9 | 81 | G♯3 B3 E4 E5 | II6 | II6 | C | agrees with the notes |
| ohaupt | 9 | 82 | F♯3 A3 F♯4 D5 | I6 | I6 | T | agrees with the notes |
| ohaupt | 9 | 84 | E3 C♯4 A4 C♯5 | V64 | V64 | D | agrees with the notes |
| ohaupt | 10 | 87 | D♯3 F♯4 A4 B4 | VI65 | **V65/ii** | C | B–D♯–F♯–A over D♯, resolving to E major, which is itself V/V: written V⁶₅/ii (home-key case) rather than V⁶₅/V/V (kept as the checker advised) |
| ohaupt | 10 | 88 | E3 E4 G♯4 B4 | II | **V/V** | C | E–G♯–B, resolving to A at the cadence: V/V (register item) |
| ohaupt | 10 | 89 | A2 E4 A4 C♯5 | V | V | D | agrees with the notes |
| ohaupt | 10 | 90 | D3 A3 D4 F♯4 | I | I | T | agrees with the notes |
| ohaupt | 11 | 93 | E3 G3 B3 G4 | ii | ii | PD | agrees with the notes |
| ohaupt | 11 | 95 | F♯3 A3 D4 F♯4 | I6 | I6 | T | agrees with the notes |
| ohaupt | 11 | 97 | A3 D4 E4 | i64 | **V(4–3)** | D | A–A–D–E: the alto D falls (through B) to C♯ on beat 4: V with a 4–3 suspension. No F♯, so not a 6/4 of D, and never a minor i |
| ohaupt | 11 | 99 | A2 A3 C♯4 A4 | V | **(removed: V, covered by the label before it)** | D | resolution of the 4–3 at line 97: A major, the label V(4–3) names it |
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
| jesu | 4 | 44 | A♯3 C♯4 F♯4 E5 | II65 | **V65/V** | C | F♯–A♯–C♯–E over A♯, resolving to B major: V⁶₅ of V |
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
| jesu | 8 | 66 | C♯3 E4 G4 A4 | IV65 | **V65/VII** | C | A–C♯–E–G over C♯: a dominant 7th; C♯ (not in E natural minor) rises to D, G falls to F♯: V⁶₅ of VII (D major), the same pattern as V⁶₅/V elsewhere. Chromatic, so colour |
| jesu | 8 | 67 | D3 D4 F♯4 A4 | VII | VII | S | agrees with the notes |
| jesu | 8 | 69 | G2 B3 D4 G4 | III | III | T | agrees with the notes |
| jesu | 9 | 71 | G3 D4 G4 B4 | III | III | T | agrees with the notes |
| jesu | 9 | 73 | E3 E4 G4 C♯5 | vi6 | **♯vi°6** | C | E–E–G–C♯: C♯–E–G over E, C♯ the raised 6th of E minor; it leads to F♯–A♯–D, so it is not vii° of the next chord: ♯vi°6 (ii°6 of B minor) |
| jesu | 9 | 74 | F♯3 A♯3 F♯4 D5 | VII6 | **VII+6** | C | F♯–A♯–D (A♯, not A): D–F♯–A♯ is an augmented triad, so VII+6, a chromatic chord. "VII6" (D–F♯–A) is not what sounds |
| jesu | 9 | 76 | D3 B3 F♯4 B4 | v6 | v6 | W | agrees with the notes |
| jesu | 10 | 78 | C♯3 A♯3 G4 E5 | iv65 | **vii°65/v** | C | A♯–C♯–E–G over C♯, resolving to B minor (v6): vii°⁶₅ of v, the target written as the chord reached |
| jesu | 10 | 79 | D3 B3 F♯4 D5 | v6 | v6 | W | agrees with the notes |
| jesu | 10 | 81 | F♯3 B3 F♯4 C♯5 | v64 | **V(4–3)/V** | C | F♯–B–F♯–C♯: tenor B falls to A♯ on the next beat (4–3); no D, so not v⁶₄: V of V (F♯ major) with a suspended 4th |
| jesu | 10 | 82 | F♯3 A♯3 F♯4 C♯5 | II | **(removed: V/V, covered by the label before it)** | C | beat 4 of bar 10: F♯–A♯–F♯–C♯ (alto E on the last quaver is a passing 7th), resolving to B major in bar 11: the resolution of the 4–3, so covered by V(4–3)/V |
| jesu | 11 | 85 | B2 F♯3 D♯4 B4 | V | V | D | agrees with the notes |
| jesu | 11 | 86 | B2 G♯3 D4 B4 | iii6 | **vii°6/IV** | C | G♯–B–D over B: diminished, G♯ the leading note of A; leads (through vii°⁴₃) to A major (C♯, labelled IV6): vii°6/IV |
| jesu | 11 | 88 | D3 G♯3 F4 B4 | iii43 | **vii°43/IV** | C | G♯–B–D–F over D, resolving to A–C♯–E (A major, IV6): vii°⁴₃/IV |
| jesu | 12 | 90 | C♯3 A3 E4 A4 | IV6 | IV6 | PD | agrees with the notes |
| jesu | 12 | 92 | E3 B3 G4 | i | i | T | agrees with the notes |
| jesu | 12 | 94 | A♯2 C♯4 E4 F♯4 | II65 | **V65/V** | C | F♯–A♯–C♯–E over A♯, resolving to B major: V⁶₅ of V |
| jesu | 12 | 95 | B2 B3 D♯4 F♯4 | V | V | D | agrees with the notes |
| jesu | 13 | 98 | E2 G♯3 B3 E4 | I | I | T | agrees with the notes |

### Cadence chords (18 in the chorales, generated; 9 changed from 0.47)

| Score | Bar | 0.47 | New | Evidence |
|---|---|---|---|---|
| chorale | 4 | I – V | I – V | no 7th sounds in the chord before the arrival |
| chorale | 7 | V – I | **V(7) – I** | passing 7th (C) after the onset of the chord before the arrival |
| chorale | 10 | I – V | I – V | no 7th sounds in the chord before the arrival |
| chorale | 14 | V7/IV – IV | V7/IV – IV | the 7th sounds with the chord |
| chorale | 18 | I – V | I – V | no 7th sounds in the chord before the arrival |
| chorale | 21 | V – I | **V(7) – I** | passing 7th (C) after the onset of the chord before the arrival |
| ohaupt | 2 | V – I | V – I | no 7th sounds in the chord before the arrival |
| ohaupt | 4 | V/vi – vi | **V(7)/vi – vi** | passing 7th (E) after the onset of the chord before the arrival |
| ohaupt | 6 | V43 – I | V43 – I | bar 5 beat 4: E–A–G–C♯ (the tenor A on the second quaver turns vii°6 into V⁴₃), resolving to the tonic bass D with a IV⁶₄ neighbour above, then I: V⁴₃–I, not a plagal cadence |
| ohaupt | 8 | ii6 – VI | **ii6 – V/ii** | bar 7 beat 4: G–B–E–G = E minor over G (ii⁶ in D, i⁶ in E minor), bass passing A; bar 8: B–B–D♯–F♯ = B major, V of E minor. Not Phrygian: that needs iv⁶–V with the bass falling a semitone; here the bass rises G–A–B |
| ohaupt | 10 | II – V | **V/V – V** | no 7th sounds in the chord before the arrival |
| ohaupt | 12 | V – I | V – I | no 7th sounds in the chord before the arrival |
| jesu | 2 | V – i | **V(7) – i** | passing 7th (A) after the onset of the chord before the arrival |
| jesu | 4 | V65/V – V | V65/V – V | the 7th sounds with the chord |
| jesu | 6 | V7 – i | V7 – i | the 7th sounds with the chord |
| jesu | 8 | V/III – III | **VII – III** | no 7th sounds in the chord before the arrival |
| jesu | 11 | V7/V – V | **V(7)/V – V** | passing 7th (E) after the onset of the chord before the arrival |
| jesu | 13 | V – I | **V(7) – I** | passing 7th (A) after the onset of the chord before the arrival |

The O Haupt bar 8 cadence text is now "Imperfect (half) cadence in E minor (i⁶–V there; the bass rises G–A–B, so not a Phrygian cadence)".

**O Haupt bar 8, settled:** E minor i⁶ goes to V, written ii⁶ – V/ii in D. It is **not** a Phrygian cadence, because the bass rises G–A–B. A Phrygian cadence is iv⁶–V with the bass falling a semitone.

**No-third chords given lowercase numerals.** There were six, not three. Each is now named by the chord it resolves into:

| Bar | 0.47 label | Notes | New |
|---|---|---|---|
| BWV 269 bar 12 | iv | D–G–C | V7(4–3) |
| BWV 269 bar 19 | i | G–D–A | V6(2–3) |
| O Haupt bar 3 | vi64 | F♯–B–C♯ | V(4–3)/vi |
| O Haupt bar 11 | i64 | A–D–E | V(4–3) |
| Jesu bar 5 | i64 | B–E–F♯ | V(4–3) |
| Jesu bar 10 | v64 | F♯–B–C♯ | V(4–3)/V |

### Independent check (IC_R8_R9_R17): R8 fixes, made in the generator

| # | Point | Fix |
|---|---|---|
| 1 | Jesu bar 8 cadence had no 7th (soprano G over D is a 4th, anticipating G) | Cadence chords are now generated, and (7) needs a minor 7th above the root. Jesu bar 8 is now **VII – III**, matching the numeral row. The other five V(7)s were re-derived by the rule, and each has a real minor 7th: C over D, E over F♯, A over B. |
| 2 | Jesu bar 11: the target is A major | The target is written as the chord reached: **vii°6/IV, vii°43/IV**. By the same rule, Jesu bar 10 is **vii°65/v** (it resolves to B minor). O Haupt bar 10 V65/ii is left as is: the chord it reaches (E major) is itself applied. |
| 3 | BWV 269 bar 12: "iii7" then "I6" | One label, **I6(7–6)** (prepared alto A falls to G over B). |
| 4 | BWV 269 bar 15: 9–8 not shown | **I(9–8)**. |
| 5 | Jesu bar 8 "IV65" | **V⁶₅/VII**, colour (C♯ is outside E natural minor and rises to D). |
| 6 | O Haupt bar 10 V65/ii | Left as is. |
| 7 | V7(4–3), V6(2–3) printed flat | The renderer's figure pattern now allows a suspension bracket after the figures. |
| 8 | Legend lacked (2–3) | The legend now reads "(4–3), (7–6), (9–8) a suspension (a held note that falls to a chord note); (2–3) a bass suspension (the bass is held and falls)". |
| also | Duplicate label and crowded anchor | The duplicate BWV 269 bar 9 I6 was dropped. The O Haupt bar 6 "I" was moved to note-L62F2 (checker's D9 and section 4). |

Not changed (the checker marked these optional or acceptable):
- the 9 over E in O Haupt bar 7 and BWV 269 bar 17, which resolves with a bass change;
- "vii°6 (V⁴₃)" in O Haupt bar 5;
- an explanatory note for VII+6.

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

## R17: K. 331 Var. III cadence anchors; tenor–bass unison ids (separate commit)

**Cadence anchors.** Three K. 331 Var. III cadences were anchored to a note in the arrival bar's semiquaver figuration, not to the arrival chord. Each is now anchored to the top note of the arrival chord. The arrival times (`a`) were already right, checked with music21: V at bar 4 beat 2, i at bars 8 and 18.

| Cadence | Old anchor (onset) | New anchor (onset) | Arrival `a` |
|---|---|---|---|
| bar 4, i64 – V | note-L78F1 (9792 ms, +209) | note-L77F2S2 (9583 ms, B4 of E–G♯–B) | 9583 |
| bar 8, i64 – V – i | note-L129F1 (19375 ms, +625) | note-L126F2S2 (18750 ms, A5 of the A chord) | 18750 |
| bar 18, i64 – V – i | note-L268F1 (44375 ms, +625) | note-L265F2S2 (43750 ms, A5) | 43750 |

Bar 12 (note-L188F3) and all the other scores' anchors were already on the arrival (all 31 checked).

**Unison ids.** `engrave.py` maps the grand-staff (satb2gs) notes back to the canonical ids by onset, pitch and length. Where two voices sound the same note together, it took the first candidate, and in six places the tenor's id went on the bass note and the reverse:
- BWV 269 bar 2 (G3);
- O Haupt bar 1 (G3), bar 8 (B3), bar 9 (A3), bar 11 (A3);
- Jesu bar 4 (B3).

Each is wrong in all three engravings, 36 notes in all. `id_map` now reads each grand-staff note's staff and layer from Verovio's MEI and picks the candidate of the same voice:
- upper staff: layer 1 soprano (F4), layer 2 alto (F3);
- lower staff: layer 1 tenor (F2), layer 2 bass (F1).

It stops if no candidate of that voice exists. The nine chorale engravings were re-rendered with the existing pipeline (`python3 scores/src/engrave.py`, Verovio 6.4.1). The files differ from 0.47 only in F1/F2 note ids; with those ids masked, they are byte-identical. The other 21 engravings came out byte-identical. `scores/src/README.md` documents the fix.

**Test.** New suite `tests/score_ids_test.py`, added to `tests/run_all` after `unit_test`. It needs no browser.
- **ids:** every note in the nine chorale engravings carries the id of the voice whose staff and layer it sits in. 1836 notes are checked.
- **anchor:** every cadence anchor starts at the cadence's arrival `a`, within 2 ms, and a note starts at `a`. 31 cadences are checked.

Against the 0.47 files the test fails on all 36 swapped ids and the 3 late anchors.

## Suite results (R17 commit)

| Suite | Result |
|---|---|
| unit | pass, 637 checks, 0 failures |
| score_ids (new) | pass: 1836 note ids, 31 cadence anchors, 0 failures |
| content_lint | pass |
| analysis_engrave | pass, 0 failures (70 views, 1899 overlay labels, 2,492,409 text–notehead pairs) |
| pageerrors | pass, 0 errors (153 views, 4244 clicks) |
| `tests/numeral_reread.py` | 0 differences (137 labels, 18 cadences) |

## Independent-check fix round (third commit): suites and Ear Lab expectations

**Every V(7), re-checked from the voices.** Each one is a stepwise falling passing 7th, a minor 7th above the root, sounding after the chord's onset. None is a chord 7th.

| Cadence | Voice | Line | Verdict |
|---|---|---|---|
| BWV 269 bar 7 | tenor | D–C–B | passing 7th |
| BWV 269 bar 21 | tenor | D–C–B | passing 7th |
| O Haupt bar 4 | alto | F♯–E–D | passing 7th |
| Jesu bar 2 | tenor | B–A–G | passing 7th |
| Jesu bar 11 | alto | F♯–E–D♯ | passing 7th |
| Jesu bar 13 | tenor | B–A–G♯ | passing 7th |
| Jesu bar 8 | – | no C anywhere | **no 7th**: the soprano A–G over D is a 4th anticipating III. Now VII – III |

**`tests/earlab_test.py` (blind analysis, E3).** It hard-coded the 0.47 cadence chords. Its expectations are now the verified labels, with the evidence in a comment:

| Cadence | Old expectation | New expectation | Verdict |
|---|---|---|---|
| Jesu bar 11 (cadence 5) | V7/V – V | V(7)/V – V | **passing 7th** (alto F♯–E–D♯ on the last quaver); not a chord 7th |
| O Haupt bar 4 (cadence 2) | V/vi – vi | V(7)/vi – vi | **passing 7th** (alto F♯–E–D, second quaver of beat 4) |
| Jesu bar 8 (cadence 4) | V/III – III | VII – III | **7th absent**: no C sounds |

| Suite | Result |
|---|---|
| unit | pass, 637 checks |
| score_ids | pass, 0 failures |
| content_lint | pass |
| analysis_engrave | pass, 0 failures (1892 overlay labels, 2,490,806 text–notehead pairs) |
| pageerrors | pass, 0 errors (153 views, 4244 clicks) |
| earlab (`tests/run_all earlab`: earlab_test and earlab_r2_test) | pass, 0 failures |
| `tests/numeral_reread.py` | 0 differences (135 labels, 18 cadences) |

## Not done

- The harmony-row colours and the new legend were checked by the suites (no overlap; labels inside the frame; figures 9 px) but not looked at on screen by a person. Contrast was not measured: the blue-grey (#7fb3c8) and violet are the colours the app already uses on the same dark panel.
- Only the three chorales have a harmony layer. The other scores' cadence chords were re-read and need no change. `numeral_reread.py` checks the chorale cadences automatically; the piano scores' cadences were checked once, by hand, with music21 chordify.
- `meta.json` `src` lines still say the analysis layer was "computed by the app". It is now generated by `tests/numeral_reread.py` from the notes, with the listed decisions. That wording was left for Justin.

## Judgements for Justin

1. **Colours for W and S.** The minor v (W) and the subtonic VII (S) share the app's existing blue-grey. They are kept for now, on the coordinator's instruction. The approval named four colours, and these two fit none of them: R9 says the minor v is not D, and they are diatonic, so not colour. The independent check recommends keeping a fifth class with your approval. Its four-colour fallback is S → violet where VII acts as V/III, and the minor v uncoloured.
2. **Suspension labels.** They are written as V(4–3), V7(4–3), V(4–3)/vi, V6(2–3), I6(7–6) and I(9–8), and the resolution chord is not labelled again.
3. **O Haupt bar 7 (line 69).** iiø⁴₂/ii: what sounds on the beat. The bass then dips to D♯, which briefly makes vii°7/ii.
4. **O Haupt bar 9 (line 81), II6.** E major over G♯ goes to D/F♯, not A, so it is not applied. It stays II6, colour. The checker agreed.
5. **O Haupt bar 10, V65/ii.** It resolves to E major, which is itself V/V. It is written in the home key's case rather than V⁶₅/V/V. The coordinator said to leave it.
6. **Jesu bar 9, VII+6** (D–F♯–A♯). A literal reading of the augmented chord. It could also be heard as V of B minor with the D as a 6th.
7. **O Haupt bar 5 (line 58), vii°6.** It stands before a cadence labelled V⁴₃–I, because the tenor A arrives on the second quaver.
