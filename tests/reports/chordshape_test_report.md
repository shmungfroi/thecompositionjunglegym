# chordshape_test.py — report (charter suite 4, run against branch v0.46)

Run: `python3 tests/chordshape_test.py <repo dir>` (exits 0 on v0.46; known defects are listed under `known_failures`). Run time is about 40–90 s.

## What it covers
The suite runs the app's own Seed Bank render path (`render`, `renderInst`) for every chord, then reads back what was drawn: the lit piano keys, `#inst._vs`, `#inst._bp`, the dot labels, the shape names and sub-labels, and the notes that `instMidis` plays. It checks all of this in Python against music21 and its own rules. It never uses the app's own checks (`frHasChord` and the rest) to decide whether something passes.

- **Roots:** the 17 picker roots, plus B#, Cb, E# and F##. These four can only reach the Seed Bank through the "Neighbours in key" chips. The suite finds them by running `renderClimb` in all 24 keys.
- **Types:** the 20 types available at Stage 6. The It+6, Fr+6 and Ger+6 chords are l:9, and `fillSelects` drops them in the Seed Bank, so they are not covered.
- **Inversions:** every inversion. That gives 1,575 chords.
- **A. Spelling:** the formula table is checked against music21 ChordSymbol. Every tone name is checked against music21 transposition from the root. Each name+octave must equal its MIDI number. The chord symbol, the slash bass and the bass text are checked too.
- **B. Piano Beginner:** only R/3rd (or sus)/5th; the inversion rotation, capped at 2nd with the "needs the full chord" note; above middle C; standard RH/LH fingering; the "left out" list; lit keys and labels; the notes played.
- **C. Piano Full:** the left-hand bass in F2–E3 is the inversion's bass; every tone appears once; the right hand is close position from C4; lit keys; the notes played.
- **D. Guitar and ukulele:** the tunings EADGBE and re-entrant GCEA (checked against `TUN` and music21), and fret→pitch.
  - Notes: only chord tones sound, and only the perfect 5th of a chord with 4+ notes may be missing. The "no 5th" and "N strings" labels must be honest.
  - Bass and labels: on guitar, the lowest note must be the inversion's bass and match the "Root/Bass on Nth string · fret n" label.
  - Reach: at most a four-fret span; open strings only in first position (chart-library shapes are exempt, as in the app); at most one muted inner string.
  - Beginner view: the `FR_CEIL`=7 ceiling, at most 4 shapes, and at most 8 extra shapes in "More shapes".
  - Fingering: each finger on one fret, fingers in fret order, real barres.
  - Names: degree labels in the dots, and honest "Open", "barre" and "Root at fret" names.
- **E. Bass:** the EADG tuning and fret→pitch; patterns only use chord tones and start on the inversion's bass; strings never move backwards; notes ascend.
  - Root–5th–octave patterns must be exact.
  - Arpeggios must contain every chord tone from the bass to its octave, in one four-fret position. Two positions are allowed only for dim7, and the shift must be labelled.
  - One finger per fret, degree labels, at least one pattern per chord, and the bass play notes.

## Counts (v0.46)
- 1,575 piano Beginner and 1,575 piano Full shapes.
- 7,622 guitar shapes (3,024 Beginner + 4,598 More).
- 6,893 ukulele shapes (3,541 + 3,352).
- 3,835 bass patterns.
- **21,500 shapes in total.** This counts 9,512 distinct fretted shapes, because ukulele shapes do not depend on the inversion but are counted once per inversion in the total.

**Compared with the old 8,158:** that suite is lost, so its exact basis can't be reconstructed. This suite counts more ways:
- once per inversion, for every instrument;
- both piano modes;
- every "More shapes" extra as well as the Beginner shapes;
- bass patterns;
- the four extra roots.

The difference comes from counting more, not from more shapes appearing in the app.

**Mutation check:** I ran a temporary copy with three faults injected: the ukulele G string retuned, a chart shape edited, and the m7b5 formula changed. It failed in every section.

## Defects found
- **CS-K1 (listed under known_failures; 10 hits):** B#aug, F##aug and Cbdim7 need a triple sharp or a quadruple flat (F###, C###, B𝄫𝄫). The app spells them correctly, but VexFlow rejects the key name, so `render()` throws in `renderStaff`. The stave and the climb panel are not drawn, and there is a page error.
  - To reproduce: in the Seed Bank, choose the key C# minor (for B#), G# minor (for F##) or Eb minor (for Cb). Tap the neighbour chip for that root, then tap the aug pad (or the dim7 pad for Cb).
  - Or in the console: `S.root='B#';S.q='aug';render()`.

No other failures.

## Observations (reported in `info`, not failures)
- **794 Beginner shapes leave out the 5th**, for example guitar C7 x32310 and C6 x32210. That is allowed, but the "no 5th" tag only appears in the More view.
- **The ukulele chart shape Fmaj7 5500** (also shown for E#maj7) has open strings with a fret-5 grip. The app permits this for charted shapes.

## Not covered
- Augmented sixths in the Seed Bank (they are unreachable there).
- Roots that only the Gym progression could send to the Seed Bank (for example Fb).
- The "Chord tones across the neck" board.
- Stave rendering beyond the throw: no pixel or notation check.
- Audio samples.
- Whether the ukulele "inversion" claim is musically right. The app states that inversions sound the same on ukulele, and the suite does not check bass notes for ukulele.
