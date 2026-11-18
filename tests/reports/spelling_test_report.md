# spelling_test.py: report (charter suite 5, theory spelling)

Run: `python3 tests/spelling_test.py <repo dir>`. Against v0.46: **exit 0, 43,847 checks, 0 new failures, 3 known failures (SP-1, SP-2, SP-3)**. Run time is about 90 s.

The test loads the app headless and offline through `tests/harness/cjg.py`. It reads its data from what the page renders and from the app's own functions, which it wraps so it can record every progression a climb realises or plays. Every expected value is worked out again in Python, with music21 and the suite's own tables. The test never uses the app's own checkers to decide a result.

## Covered (counts)
| Area | What is checked | Checks |
|---|---|---|
| K: Scales tab | 18 tonics (17 pads plus E♯, which the circle's mode chips reach) × 17 scales × up/down = 612. Checks spelling (music21 scale classes, or interval tables for pentatonic, blues, whole-tone, chromatic, Phrygian dominant and octatonic), MIDI pitch classes, W/H steps, degree labels, solfa (movable do, la-based minor, modes from the parent major), the solfa line and the hand-sign ladder | 612 each |
| | Key-signature text and the parent key | 508 |
| | Theoretical keys: flagged, with the usual enharmonic chip and no staff signature (G♭ melodic minor passes) | 104 |
| | Staff key signature and staff notes | 436 |
| | Chords of the key for every 7-note scale: root, quality, numeral and symbol | 5,238 |
| C: Circle | 24 keys. Checks the signature, enharmonic twin, relative and parallel keys, dominant and subdominant neighbours, and the seven mode chips (named from the parent major) | 315 |
| I: Intervals | 17 pads × 17 intervals × up/down. Checks the spelling against a music21 Interval, the semitones, the number, the quality and the inversion | 578 × 3 |
| R: Climbs 3–8 | Every example, in every offered key, at Stages 4/5/6. Also climb 7's 64 V7/x builder combinations, every climb 8 swap combination (including the forced N6/It6 → I⁶₄ option), the climb 6 walk, the climb 3 period, and 40 runs of each quiz. Each chord is checked against music21 RomanNumeral (secondaries, vii°7/V, borrowed chords, N6, It/Fr/Ger, cadential 6/4) | 6,120 classical + 1,924 symbol (climb 4 blues and climb 5 loops use dominant-7 symbol conventions) |
| | SATB: chord tones only, the right bass, root and 3rd present, voices in order | 6,120 |
| | Piano voicings (voiceProg) | 1,560 |
| J: Climbs 9–11 | Jazz tokens are checked against chord symbols: root from a music21 RomanNumeral, quality from the jazz suffix, notes from a music21 ChordSymbol | 1,192 |
| | Guide-tone, shell and rootless A/B voicings: only notes of the displayed symbol (13, 7♭9♭13, maj9 …), root in the bass, and the symbol contains the numeral's 7th chord. Covers every example × voicing type × start, the climb 10 substitution builder (16 combinations) and quizzes | 2,472 |
| | Climb 11's whole reharmonisation vocabulary in every key | included in the 1,192 |
| M: Climb 12 | Modal vamps on 6 tonics (chords, voicings, character note); chromatic-mediant chains up to 4 chords (music21 intervals); planing shapes (interval names, diatonic planing); tintinnabuli | 2,292 |
| D: Labels | Every bar and numeral chip rendered in climbs 3–11 shows a chord-symbol root that matches music21 | 10,636 |
| X | Page errors and exceptions during any render | none |

## Defects found (recorded as `known_failures`, app not changed)
- **SP-1: some spellings crash the staff.** These spellings need a triple sharp or flat, and VexFlow throws "Invalid key name", which stops the tab rendering. The spelling itself agrees with music21. To reproduce:
  - `#keys`, Stage 5 or above, tonic A♯ (or E♯, reached from the F♯-major circle chip), Chromatic.
  - The same with E♯ Octatonic.
  - Intervals tab: A♯ up A6, or G♭ down A6.
  - 6 cases in all.
- **SP-2: double accidentals display wrongly in chord buttons.** The chords-of-the-key buttons show "B♭bmaj7" and "F♯♯m" instead of "B𝄫maj7" and "F𝄪m". `pretty()` only converts a double accidental at the end of a string, so a chord symbol with a suffix keeps the ASCII form. 306 buttons are affected, for example D♭ natural minor VImaj7, C♯ Lydian ♯iv°, and D♯ major iii and vii°.
- **SP-3: some parallel keys are theoretical but not flagged.** The circle gives the parallel of D♭ major as D♭ minor, of G♯ minor as G♯ major, and of D♯ minor as D♯ major. These keys need 8–9 accidentals and the app neither flags them nor offers C♯ minor, A♭ major or E♭ major. This is a judgement call, so you may prefer to drop it.

## Not covered
- The rendered SVG of the staves: the test checks the notes and key signatures passed to `drawLine`, not the engraving.
- The Ear Lab and Gym intervals, which the Ear Lab suite covers.
- Climbs 1, 2 and 13.
- Voice-leading rules beyond chord membership and bass. Parallels and doubling are the Ear Lab and SATB suites' job.
- Climb 12's static-harmony tab beyond the check that it renders without errors.
- How a theoretical key is presented beyond the flag, the enharmonic chip and the absence of a key signature.
