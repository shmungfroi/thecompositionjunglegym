# Independent theory check: Ear Lab cadence and chord-quality items (register 0.48: EL-7, R4, EL-6, EL-10)

Checked copy: `/home/claude/wt-check-el` (frozen, HEAD `aa05aa8`, the 0.48 merge; baseline 0.47 = `ef97cdb`). Read-only, nothing edited.
Method: the app's own generators (`earGen`) were called in headless Chrome with seeded RNGs and the voicings exported. Everything below was
checked with my own code (`/home/claude/checks/ic/`: `vl.py` voice-leading checker, `cat.py` category checks, `tells.py` tell analysis,
`ui.py` browser flow). I did not use the app's `chordIssues`/`pairIssues` checker. I read the builder's report only after I had formed this view.

Samples: cadence rung 1, 3,000 + 12,000 items; rung 3, 3,000 + 20,000 items; chord quality, 1,500 per rung (+3,000 at rung 1).

## Verdict per spec

| Spec | Verdict | One-line reason |
|---|---|---|
| EL-7 rung 1: content, open voicing, strict SATB | **PASS** | 15,000 items, 0 strict errors; every chord is open; every item is the right two chords in a major key |
| EL-7 rung 1: balance and no tells | **PASS, with one note** | Balanced 25/25/25/25. No absolute feature exceeds chance by 10 points; the last chord's outer-voice span in octaves is +7 |
| EL-7 rung 1: "one right answer" | **Note** | With "Without the key chord", I–V and IV–I can be identical audio (96 voicings) |
| R4 rung 3: six answers, categories correct | **PASS** | Every Phrygian, 6/4 and interrupted item is what it claims (details below) |
| R4 rung 3: strict SATB | **FAIL (minor, 2.3 % of items)** | Bass leaps of a 7th, 6/4 chords that double the 4th rather than the bass, fi that does not rise |
| R4 rung 3: mode tell, 6/4 bass, ≥100 items, one answer | **PASS** | Mode predicts 16.0 % vs 18.4 % chance; 6/4 bass line identical to the perfect one; min 163 distinct per button; no shared audio |
| R4 feedback: solfa (la-based minor) | **FAIL (copy)** | The Phrygian feedback says "(le–so)" and the 6/4 says "bass so". In la-based minor these are fa–mi and mi |
| EL-6 chord quality | **PASS** | Rungs 1–3 are all root position, close, with correct intervals; aug and dim7 text is correct in the browser |
| EL-10 scoring | **PASS** | Show me, skip, undo after marking and reset with inline confirm and Undo all behave as specified, with no browser dialog |

## 1. Voice leading (my checker)

My rules: all four voices in range (B E2–D4, T C3–G4, A G3–D5, S C4–G5). No crossing or overlap. S–A and A–T no more than an octave apart.
No parallel or contrary 5ths, 8ves or unisons on any pair. No hidden 5ths or 8ves in the outer voices with a soprano leap. The leading note
rises in outer voices and always rises into vi/VI; in an inner voice it may fall only to the 5th of I. Every 7th falls by step. A secondary
leading note (fi) rises. No doubled leading note or doubled 7th. 6/4 chords double the bass. No augmented 2nd. No leap of a 7th or of more than
an octave. Every chord has its root and 3rd (and its 7th for V7).

**Rung 1: 0 errors in 15,000 items.** Advisory only: the 5th is omitted from V or I in about 6 % of items (tripled root). The final major I
doubles its 3rd in 178 of 12,000 items, mostly in plagal IV–I, e.g. Db: IV `Db3 Ab3 F4 F5`. This is legal but weak.

**Rung 3: 453 of 20,000 items (2.27 %) break a strict rule.** By answer: cad64 177/3,662, imperfect 133/3,670, plagal 86/3,670,
Phrygian 57/1,669. Perfect and interrupted had none. The builder's report says rung 3 passes the independent strict rules, so these are new.

| Error | Count /20k | Where | Example |
|---|---|---|---|
| Bass leaps a 7th (iv → i⁶) | 225 | `i:1` models: imperfect `i iv i6 ii°6 V`, Phrygian `i iv i6 iv6 V`, plagal `I IV I6 IV I` / minor | B minor Phrygian: bass E2 → D3 (minor 7th up). C minor imperfect: F2 → Eb3 |
| 6/4 doubles the 4th (do), not the bass | 177 | `I IV I6/4 V7 I` and the minor form | A major: I⁶₄ `E3 A3 C#4 A4`; the soprano's A then leaps a 5th down to the 7th D4. Bb minor: `F3 Bb3 Db4 Bb4` |
| fi (raised 4th) in V7/V does not rise | 51 | `I IV ii6 V7/V V` | A major: V7/V `B2 D#4 A4 F#5` → V `E2 B3 G#4 E5`: the tenor's D# falls a 3rd to B |

Cause (from the code, not changed): rung 3 is realised by `earSATB`, which drops voicings with checker *errors* plus contrary 5ths/8ves and
overlaps, but not checker *warnings*. Rung 1's `earSATBPair` drops warnings too, which is why rung 1 is clean. The 6/4 doubling and the
fi resolution do not appear to be checker rules at all.

Recommendation: in `earSATB`, at rung 3, also reject warnings (7th leaps at least). Add two hard filters: a 6/4 chord must double its
bass, and a secondary leading note must rise by a semitone. Also prefer a tripled root over a doubled major 3rd in the final I. 546 of
20,000 rung 3 items end on a doubled-3rd major tonic, e.g. C major cad64 ends `C3 E3 C4 E4`. The builder flagged this for minor only.

## 2. Are the categories what they claim?

| Check | Result |
|---|---|
| Rung 1: exact pairs V–I / IV–I / I–V or IV–V / V–vi, major, root position | 15,000/15,000 |
| Rung 1 open voicing (S – T > octave) on every chord | 30,000/30,000 chords |
| Interrupted: 3rd of vi (VI) doubled after V | rung 1 751/751; rung 3 549/549 (both modes) |
| Phrygian: minor key | 249/249 |
| Phrygian: iv⁶ then V root position | 249/249 |
| Phrygian: bass falls exactly one semitone, b6̂ → 5̂ | 249/249 (soprano rises against it in 152) |
| Cad 6/4: the 6/4 is I/i in second inversion, preceded by IV/iv | 552/552 |
| Cad 6/4: bass on 5̂ in the 6/4 and in the V that follows, then I | 552/552 (held 541, drops an octave 11) |
| Cad 6/4: the 6th and 4th both fall by step to 5 and 3 in every voice | 528/552. The other 24 double the 4th and one copy leaps (see §1) |
| Pitch-class content of every chord matches its numeral (my own table, not the app's) | all items, both rungs |

The 6/4 is presented correctly as a dominant event: feedback says "over the bass so, a 6/4 chord falls to 5/3 as it becomes V".
The numeral shown is I⁶₄, as in the approved spec.

**Solfa in R4 feedback (FAIL against "movable do, la-based minor").** `CADFAM.phrygian` says "with the bass falling a semitone (le–so)".
That is do-based minor. With la-based minor, which the app states at line 876 and uses in the melody drill, the Phrygian bass is
**fa–mi**. `CADFAM.cad64` says "over the bass so". That is right in major but wrong for the minor 6/4 items, where the bass is **mi**.
Recommendation: make both texts mode-aware, or use degree numbers (6̂–5̂, 5̂).

## 3. Tell analysis (my own predictor: 5-fold held-out, most common answer per feature value)

Chance = share of the most common answer. "Content" features (scale degrees relative to the key) are the music itself and are expected to predict.

| Feature | Rung 1 (chance 25.0 %) | Rung 3 (chance 18.4 %) |
|---|---|---|
| mode | 23.3 | 16.0 |
| chord count / phrase length | 23.3 (always 2) | 17.0 (always 5) |
| key | 19.8 | 14.0 |
| first bass note (MIDI) | 23.7 | 13.4 |
| last bass note (MIDI) | 24.6 | 18.8 |
| first soprano (MIDI) | 29.9 | 20.2 |
| last soprano (MIDI) | 28.3 | 21.7 |
| lowest note | 27.0 | 17.9 |
| highest note | 25.7 | 23.4 |
| mean pitch | 26.1 | 21.0 |
| last chord S–B span, octaves only (pure register size) | **31.8 (+6.8)** | **26.2 (+7.8)** |
| (content) last bass degree / bass line | 74.2 / 100 | 54.0 / 80.8 |

No register, key, length or mode feature is more than 10 points above chance, so nothing meets the flag threshold. Two were tested with a
too-wide feature and flagged at first, then explained:
- "(lowest, highest) in 3-semitone bins" gave 35.4 % at rung 1. That pair carries the outer-voice interval, which is harmony.
- "Last-chord S–B span in semitones" gave 48.3 % at rung 1 and 30.7 % at rung 3. A span of 27 (a minor 10th + octave) occurs only in
  interrupted items, so this is hearing a minor chord, which is content.

With the span reduced to whole octaves (pure size), the excess is +6.8 / +7.8. At rung 1, wide final chords lean perfect (517 vs 321
interrupted at 2+ octaves). At rung 3, Phrygian finals are wide in 80 % of items. This is above the builder's own 5-point margin but under
10, and the builder's tell list does not include it. Recommendation: add outer-voice span to the register cost or to the tell tests.

Balance: rung 1 is 25/25/25/25. Rung 3 is 18.4 % for each of five answers and 8.3 % for Phrygian, because Phrygian is minor-only and the
mode is drawn 50/50. This meets the spec (mode does not predict above chance), but a student meets the Phrygian button about half as often.
If you want equal exposure, give minor a 2:1 Phrygian weight or draw the answer first and then the mode. Re-test the mode tell after either change.

Distinct items (20,000 rung 3): Phrygian 163, perfect 161, cad64 260, interrupted 234, imperfect 282, plagal 326. Every button is ≥ 100: **PASS**.
No voicing occurs under two different answers at rung 3.

6/4 bass motion: in each mode, the whole degree-bass-line `1 4 5 5 1` is shared exactly by perfect and cad64 (301/301 major, 251/251 minor).
The bass alone cannot separate them: **PASS**.

**Rung 1 note, one right answer:** 96 voicings occur as both imperfect I–V in key *k* and plagal IV–I in key *k*+7, e.g.
`[[47,54,66,75],[54,54,66,70]]`. The key chord tells them apart, so a question heard with the key chord has one answer. The cadence drill
also offers "Without the key chord" at rung 1, though. Any replay that way makes every rising-5th pair (I–V vs IV–I) undecidable.
Recommendation: hide "Without the key chord" at rung 1, or play the key chord again before the pair.

## 4. Builder's judgements

(a) **Cadential 6/4 only decorates a perfect cadence: acceptable.** I⁶₄–V–I is the textbook and HSC form, and the reason given holds: an
imperfect I⁶₄–V ending would be the only ending with the bass held on 5̂, so the bass would give it away. The feedback still says the 6/4
can decorate an imperfect cadence. Suggest the imperfect form for a later rung or the blind-analysis drill, not as a gap here.

(b) **Chord quality rung 1 = 48 voicings, interrupted rung 1 = 28: acceptable for a drill, with a caveat.** 48 is every item the rung can
produce (2 qualities × 12 roots × 2 registers, confirmed). For a major/minor discrimination the risk of memorising is negligible. Interrupted:
I confirmed 28 over 12,000 items, 1–4 per key; Ab major has only one voicing. The V–vi sound itself is the cue, so memorisation adds little.
Raising it would mean relaxing open spacing for vi, and the spacing would then become a tell, so I agree with leaving it.

(c) **Family answers marked wrong with an explanation: works as specified (browser-verified), but it is a pedagogical call.** "Imperfect"
for a Phrygian, or "Perfect" for I⁶₄–V7–I, is a true statement and would earn marks in an HSC answer. The app counts it as a miss, so the
streak resets, and the banner says "Not this time." even though the explanation then says "you heard the right kind of ending".
Recommendation: keep it marked not-exact, but use a different banner ("Close: right family") and consider the `near` kind the builder
mentions, so it does not reset the streak. Otherwise acceptable.

(d) **Drill change mid-question = skipped; Stage change = not: acceptable and consistent.** Verified in the browser: leaving the chord
quality drill unanswered added 1 to `skipped`. Switching Stage 6 → 5 with a rung 3 cadence question open kept the same question,
`earLvl()` = 3, and changed no stats.

## 5. Browser spot checks (EL-6, EL-10) — all PASS, no page errors, no dialogs

- EL-6 rung 1 offers Major/Minor only; items have `inv` 0. At rungs 1–3 (1,500 each) my interval check found every chord root position,
  close and correct, with lowest note C♯3–C5.
- Augmented: "Augmented, spelled from E: E G♯ B♯. It is symmetrical: … no root position or inversion." Dim7: the same form. Neither names an
  inversion. Other qualities say "(on G, root position)".
- Show me after a right answer: n 1, streak 1, shown 1, n unchanged. Next unanswered: skipped 1, streak kept, "· skipped 1" in the stats line.
- Family answers (Imperfect for Phrygian, Perfect for 6/4): n +1, ok +0, feedback includes the family sentence. Rung 3 shows six buttons.
- Reset: inline "Reset the chord quality score to zero? [Reset] [Keep it]". Reset zeroes all six fields, then "Score reset. [Undo]" restores
  them exactly. Keep it changes nothing. No `dialog` event.
- Undo after marking (rhythm drill): the Undo button is gone, Ctrl+Z leaves the answer unchanged, and the history is empty.
- Rung change mid-question: skipped +1, n unchanged.

Minor EL-6 copy point: roots Db/Ab/Eb/C/F/Bb give double-flat spellings in feedback (e.g. dim7 on Db: "Db Fb Abb Cbb"; dim on Eb:
"Eb Gb Bbb"), and B/F♯ augmented gives double sharps. These are correct, but heavy for Stage 4–5. Consider C♯/G♯/D♯ roots for the
diminished qualities.

## Recommendations, in priority order

1. Rung 3 realisation: reject 7th leaps, require 6/4 chords to double the bass, require fi to rise (≈2.3 % of items affected).
2. R4 feedback solfa: la-based minor, so Phrygian bass fa–mi and minor 6/4 bass mi (or use scale-degree numbers).
3. Hide or rework "Without the key chord" at cadence rung 1 (I–V and IV–I become identical).
4. Family answers: a "Close" banner and, ideally, a `near` kind that keeps the streak.
5. Optional: prefer a tripled root to a doubled major 3rd in the final tonic; add outer-voice span to the tell tests; even out Phrygian exposure.
