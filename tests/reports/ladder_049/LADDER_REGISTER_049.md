# Build register 0.49: Ear Lab ladders (melodic and rhythm dictation)

Engine designer (Opus), 20 Nov 2026. Branch `049-ladder-reg`. Status: **Drafted, for Justin's approval.** Nothing here is built in `index.html` (the 0.49 corrections C1–C11 run first).

Inputs: Justin's approved ladder framework (12 melody rungs, 10 rhythm rungs, rules); the approved rhythm names (RHYNAMES, Justin 20 Nov) plus the extension he approved at 21:24 and his tuplet and names-setting decisions at 21:31 (section 4); his Curwen chart (20 Nov) for chromatic spellings; `index.html` at 3a75172 (Ear Lab code read in full for `mel` and `rhy`); `tests/earlab_*.py`.

Evidence, all in this folder:

| file | what it proves |
|---|---|
| `ladder_proto.py` | Reference generators for melody rungs 1–11 and rhythm rungs 1–9 (+ the generated half of rhythm 10), pool counts, tell tests. Python model, not app code: the JS port must reproduce its rules, and its numbers are the port's acceptance targets. Run: `python3 tests/reports/ladder_049/ladder_proto.py --n 20000 --json …` (about 4 min). |
| `proto_output.txt`, `proto_results.json` | The 20,000-draw run quoted below: **0 tell failures** across 444 melody and 220 rhythm checks (after the fixes in 0.2). |
| `repertoire_scan.py`, `repertoire_scan.json` | Melody rung 12 (classical): excerpt supply in the ten licensed scores the app already plays. |

Facts here from memory or lookups are marked ⚠ where they need an independent check before use.

---

## 0. Ground truth: what Ear Lab melody and rhythm do now (0.48 / 3a75172)

### 0.1 Current code

**Melody** (`earGenMel`, `earMelOK`, `earMelRange`, index.html ~6981–7000; desk `earMelDeskHTML`, `earMelLadderHTML`, `earMelStave`; marking in `earCheck`):

| rung (EARSTAGE.mel) | mode, keys | range (index) | length | moves | start / end |
|---|---|---|---|---|---|
| 1 (St 4) | major, CKEYS2.maj = C D F G B♭ E♭ A | d..s | 5 crotchets | steps, repeats (not three in a row), s–m, m–d and back | d, m or s / d, m or s |
| 2 (St 5) | major, same keys | s,..l (**includes t, and f**) | 6 | steps, repeats, leaps between tonic-triad notes up to a 6th | d / d |
| 3 (St 6) | **la-based harmonic minor** (ESOLMIN has si), tonics A E D G C | m,..m | 7 | as rung 2, but f–si forbidden | l / l |

All notes are crotchets at 0.65 s each after the key-chord cue (`earKeyCue`, do from `earDo`). The first note is given; the student taps the hand-sign ladder; the stave shows "Write the melody · k of N notes". Marking is all or nothing (`earCheck`: every note equal); "Show me" = shown; the reveal lights each note and its ladder rung in time (`earMelFollow`).

**Rhythm** (`RCELL`, `earCells`, `earFill`, `earGenRhy`, `earSchedRhy`; entry tiles `earRhyTile`, names `RHYNAMES`):

| rung (EARSTAGE.rhy) | cells | metre, length | sound |
|---|---|---|---|
| 1 (St 4) | q e2 h | 4/4, 1 bar | clap, 72 bpm |
| 2 (St 4) | + s4, qr, dq | 4/4, 1 bar | tone, 100 bpm |
| 3 (St 5) | + es2, s2e, syn | 4/4, 2 bars | tone |

Units are semiquavers (16 to a bar). Minim-length cells start only on beats 1 or 3; a rest never opens a bar or ends the line. Marking compares the onset string (`rhyOnsets`, notes and rests), all or nothing; per-beat ticks in the result (`earRhyBeats`).

### 0.2 Findings in the current code (new rows for the register, status Drafted)

| id | finding (evidence) | consequence for 0.49 |
|---|---|---|
| LR-1 | **Rhythm rung 1 has 25 distinct items** (exact count: 5 × 5 half-bars of q/e2/h; `ladder_proto.exact_r1`). The ≥ 100 rule was never tested for rhythm (earlab_test D covers mel, qual, bass only). | Decision D1. Add a rhythm pool test. |
| LR-2 | Melody rung 2 includes low ti (t,) and fa; the new table puts t at rung 3. | Rung 2 rebuilt (section 2). |
| LR-3 | `earDo` places do differently for minor (63–74) and major (59–70), and CKEYS2.min tonics (A E D G C) give key signatures that are a subset of the major ones. Fine while no rung mixes modes; **in a mixed rung the cue register and the key signature would both give the mode away.** The prototype measured it: key signature predicted the mode at 61% against 51% chance (M10), and the octave of do at +6 to +7 points. | Rules MK and MR1 (section 1). |
| LR-4 | The melody desk shows the note count ("k of N notes"). From rung 4 (rhythm added) the count gives the rhythm away: with N shown, the rhythm of bar 1 is guessed at 23% against 13% chance (M4), and note 4 at 22% against 17%. | Rule MU1: from rung 4 the desk shows bars and beats, not notes. |
| LR-5 | `RCELL` units (semiquavers) cannot hold triplets, 6/8 dotted values in compound beats, quintuplets or septuplets. | Rule U: ticks of 420 per crotchet (section 3.0). |

### 0.3 How existing rungs map onto the new tables

**Melody**

| current | becomes | change |
|---|---|---|
| 1 | **new 1, unchanged** (the framework keeps it as built). Exact pool 274 lines. | none, apart from the Stage table length |
| 2 | **new 2** | Remove t, from the range (s, l, d r m f s l only); start may be s, d, m or s; ending stays d; Stage 5 → 4; the new-thing share applies (2/3 of items contain l, l, or s,). |
| 3 (harmonic minor, no rhythm) | **retired as a rung.** Its pitch rules (la-based minor with si, si → l, no f–si) move to new rung 7, which adds rhythm and 4 bars. | New rung 3 (major + t, 7–8 notes) takes the slot. Its nearest content (7 notes, no rhythm) is the closest difficulty, so a saved `EAR.lvl.mel = 3` lands there. |

**Rhythm**

| current cell / rung | new rung |
|---|---|
| q, e2, h (current 1) | 1 |
| qr (current 2) | **1** (moves down) |
| s4 (current 2) | 3 |
| dq (current 2), es2, s2e (current 3) | 4 |
| syn (current 3) | 6 |
| 2 bars (current 3) | 2 (from rung 2 every rung is 2 bars; rung 9 is 4 bars) |

Current rung 2 ≈ new 3–4 material in one bar; current rung 3 ≈ new 4 + syn. Saved levels keep their number (rhythm 2 → new 2, 3 → new 3). Stats (`EAR.st`) are per drill and carry over; the per-rung readiness record (section 5.3) starts empty.

**Approved names kept unchanged:** ta, ti-ti, ta-a, tika-tika, sa, tam-ti, ti-tika, tika-ti, syn-co-pa.

---

## 1. Rules for every rung of both ladders

**Stage filter.** `EARSTAGE.mel = [4,4,4,4,5,5,5,5,6,6,6,6]`, `EARSTAGE.rhy = [4,4,4,5,5,5,5,6,6,6]`. `earRungsShown`, `earHidden` and the drill strip loop over the length of the array (they are hard-coded to [1,2,3] now: replace with `EARSTAGE[d].map((_,i)=>i+1)`). Stage tags: Melodic dictation "Stage 4–6", Rhythm dictation "Stage 4–6" (EDR rows change from '4–5'). The other drills keep three rungs.

**One new thing, earlier material in the mix (rule N).** Each item of a rung with a new thing draws first whether it contains it: **2/3 contain it, 1/3 review earlier material in the same format** (same length, metres, bars). Proved: new share 65–68% on every rung. The review items keep the format the same, so length, metre and bars never say whether the new thing is there (all tell checks pass). The share is decision D2.

**Keys (rule MK).** The key **signature** (do's pitch class) is drawn first from the Stage's set, for every mode; the tonic follows from the mode (la = do + 9 semitones, re for Dorian, so for Mixolydian). Sets: Stage 4 = up to 3 sharps or flats (C G D A F B♭ E♭, today's CKEYS2.maj); Stage 5 adds E and A♭; Stage 6 adds B and D♭. Never draw minor tonics from their own list (LR-3).

**Register (rules MR1, MR2).** do's MIDI depends on the key signature alone: do = 60 + pitch class (C4–B4), the same for every mode, item and the key cue. Every melody rung's range is capped at s,..d' (do − 5 to do + 12 semitones; minor s,..l with si, in harmonic and melodic minor; modal items inside the same span), so every item sits in G3–B5 (55–83) and the octave never varies. A per-item octave choice measured as a tell (+5 to +7 points on the mode and the new thing, given the key signature). earlab_test G's floor (55) stands; its ceiling becomes 83.

**Tempo.** Melody: drawn per item, 72–96 crotchets a minute (dotted crotchets 48–64 in 6/8), never from the content. Rungs 1–3 keep the 0.65 s step as built. Rhythm: as built (72 at rung 1, 100 from rung 2, or the student's own choice of 72 or 100), plus a drawn 66–100 when the student has not chosen. Playing time then depends only on bars, metre (shown) and tempo (drawn): no tell.

**What is shown (given information).** Key signature and clef; the metre; the bar outline (bars, with an anacrusis bar drawn short when there is one, decision D9); the first note (pitch and, from rung 4, its length). From rung 4 **not** the note count (LR-4, rule MU1).

**Tell tests (method; all in `ladder_proto.py`, to be ported to `earlab_test.py` section C).** For each rung, 20,000 seeded items. A tell is a feature that improves the best guess of an answer target by more than **5 points** over what the screen already gives. Formally: accuracy of the majority answer per (given, feature) value against accuracy per given value alone; given = the metre for rhythm and bar-rhythm targets, the key signature for register features, nothing otherwise.
- Melody features: key signature; octave of the melody against the cue; note count (rungs 1–3, where it is shown); tempo (8-bpm bands); metre; anacrusis.
- Melody targets: notes 2, 3, 4 and the penultimate note (solfa); contains the new thing; variant (tune type, mode, modulation kind); rhythm of bar 1.
- Rhythm features: tempo (8-bpm bands); playing time (whole seconds); the tone's pitch; anacrusis.
- Rhythm targets: first, second and last cell; contains a new cell (hidden content: a new metre is shown on screen, so it is not a target); the metre (reported as information only).
- Result of the 20,000-draw run: **0 failures** (36–42 checks per melody rung, 20–25 per rhythm rung). One reported for information only: with the metre hidden, tempo would not predict it (rhythm rung 2: 48% against 48%).

**Pools (rule P).** "Distinct" = distinct as written (solfa + rhythm + metre + anacrusis; for rhythm, cells + metre + grouping + anacrusis + swing/backbeat). A transposition or a tempo change is not a new item. 20,000 draws per rung; where the sample saturates the count is exact.

---

## 2. Melody ladder

Notation for all rungs: treble clef, key signature, the shared ENG layer (`earMelStave`), solfa under each note (movable do, la-based minor), hand signs on the ladder (Curwen, KMEIA drawings, with Kodály's orientation: raised notes point up, lowered down, per Justin's chart). Chromatic spellings (Justin's chart, 20 Nov): **sharps di ri fi si li, flats te le se me ra**. Playback: piano, key cue (tonic chord, at do = 60 + pc) then the melody; "Hear it again", "First note", "No key chord" as now; the answer stops the sound; at the reveal each note and its ladder rung light in time.

Common entry UI from rung 4 (melody with rhythm): see decision D3. Marking for all rungs: see decision D4 (recommended: all or nothing for the score, a per-note pitch and rhythm detail in the result, "x of y notes" in the journal).

### M1 · Stage 4 · as built
- **Generator:** major, d..s, 5 crotchets; steps, repeats (never three in a row), s–m and m–d both ways; starts and ends on d, m or s. No change.
- **Pool:** 274 exact (every line the rules allow; the 20,000-draw sample found 256).
- **Tells:** 36 checked, 0 failed. Key is drawn independently (7 keys).
- **Marking:** every note right (octave included). No partial credit.
- **UI:** ladder d..s as now.

### M2 · Stage 4 · + l, low l, low s; leaps in the tonic triad; 6 notes
- **Generator:** major; range s, l, d r m f s l (no t, LR-2). Moves: steps, repeats, leaps between s, d m s up to a 6th (s,–m), never a leap from or to l / l, (a step). Starts on s, d, m or s; ends on d. New thing (2/3 of items): at least one of l, l,, s,. Review items (1/3) use d..s only.
- **Pool:** 1,091 distinct in 20,000.
- **Tells:** 36 checked, 0 failed (incl. octave against the cue, note count, the new thing).
- **Marking, notation:** as M1. **UI:** ladder s,..l (8 rungs; home d marked).
- Note: l,–d (the minor 3rd at the heart of la-pentatonic songs) is a leap outside the tonic triad, so the approved wording keeps it out until rung 5.

### M3 · Stage 4 · + t (and t,), up to d'; pentatonic and diatonic tunes; 7–8 notes
- **Generator:** major, s,..d'. Each item is pentatonic (d r m s l and octaves; moves by pentatonic step, m–s and l–d' count as steps) or diatonic. The new thing (t) is in 2/3 of items: they are the diatonic ones; the 1/3 review items are pentatonic. t moves to d or steps down to l; the penultimate t always goes to d. Leaps: tonic triad (s, d m s d') up to a 6th. Ends on d or d'. Length 7 or 8, drawn independently.
- **Pool:** 10,948 distinct in 20,000 (unsaturated).
- **Tells:** 36 checked, 0 failed (length against the tune type and the new thing included).
- **UI:** ladder s,..d' (11 rungs). Note count shown (all crotchets).

### M4 · Stage 4 · rhythm added: crotchets, quavers, minims; 2/4 and 4/4; 2 bars
- **Generator:** pitch rules of M3 (pentatonic 1/3, diatonic with t 2/3: the new thing here is rhythm, so the pitch mix stays as M3). Rhythm: metre 2/4 or 4/4; bar 1 from {ta, ti-ti, ta-a} on the beat (ta-a on beats 1 or 3); the last bar ends on a long final note: 4/4 = two of (ta, ti-ti) then ta-a; 2/4 = ta-a, or ta ta. At least 5 notes. The final note is the tonic (d or d').
- **Pool:** 15,334 distinct in 20,000.
- **Tells:** 42 checked, 0 failed; bar-1 rhythm tested given the metre.
- **Rule MU1:** the desk shows "bar 1 of 2, beat 3" and empty bar outlines, not the note count.
- **Marking:** a note is right when its pitch and its onset and length are right; the item is right when every note is (D4 for partial credit). A tie-free sound-equivalent spelling (ta vs. ti tied to ti) is not possible with this vocabulary.
- **Notation:** stems, beams per beat (quaver pairs beamed), minims. Time names under the stave at the reveal (RHYNAMES).

### M5 · Stage 5 · la-pentatonic, then natural minor (la-based); 2 bars
- **Generator:** 2/3 minor items, half la-pentatonic (l, d r m s l with s,; pentatonic steps incl. l,–d and m–s), half natural minor (s,..l: l, t, d r m f s l). Home la; ends on l, or l. Leaps within l d m. 1/3 review items: M4 major. Rhythm as M4. Key cue: the minor tonic chord (la-do-mi) at do = 60 + pc (MR1), so the cue's register never tells major from minor.
- **Pool:** 17,348 distinct in 20,000.
- **Tells:** 42 checked, 0 failed (key signature and cue octave against the mode included: the LR-3 fix).
- **UI:** ladder s,..l with home la marked (the label "home" moves to la, as rung 3 does now).

### M6 · Stage 5 · all diatonic leaps incl. the dominant triad (s–t–r); 3/4 and 6/8; anacrusis; 4 bars
- **Generator:** major or natural minor (half each). Leaps of a 3rd to a 6th and the octave, between any scale notes; the dominant triad outlined (s,–t,–r, s–t–r'); the tritone only as t–f / f–t inside a dominant-7th outline, resolving inward next (f → m, t → d). 7ths excluded (D6). New thing (2/3): at least one leap outside the tonic triad. Rhythm: metres 2/4, 3/4, 4/4, 6/8; 4 bars; simple cells ta, ti-ti, ta-a, ta-a-a (3/4 only, from beat 1); compound cells tam, ti-ti-ti, ta ti, ta-a-a (whole 6/8 bar). Anacrusis in 30% of items (one beat or a quaver; one quaver in 6/8); the last bar is shortened by the anacrusis length, so the playing time never tells. At least 9 notes.
- **Pool:** 20,000 distinct in 20,000 (pitch lines 19,996).
- **Tells:** 42 checked, 0 failed.
- **Count-in:** one full bar, then the anacrusis on its own beat (pulse on).
- **UI:** ladder s,..d'; bar outline shows the short first bar (D9).

### M7 · Stage 5 · harmonic and melodic minor (si; fi and si); 4 bars
- **Generator:** la-based minor, s,..l (si, below la, allowed). 2/3 new-thing items: harmonic (si, si → l always) or melodic (rising f→fi→si→l, falling s f natural; fi → si always). 1/3 review: natural minor. Rhythm as M6. f–si (the augmented 2nd): D7.
- **Pool:** 20,000 distinct in 20,000.
- **Tells:** 42 checked, 0 failed.
- **UI:** ladder gains si (and fi) beside so (fa); a raised-note rung is drawn as a half-step rung between so and la (two signs: so, si). Hand signs: si points up (chart).
- **Marking:** si written as s (or fi as f) is a wrong note (the feedback names it: "you wrote so; it was raised: si").

### M8 · Stage 5 · modes from the parent major (Dorian on re, Mixolydian on so); te, fi; 4 bars
- **Generator (four kinds in the 2/3 new-thing share, a quarter each):**
  - Dorian on re, parent-major solfa: home r, ends on r; no alterations; s,..d'.
  - Mixolydian on so: home s, ends on s.
  - Major with **te** (lowered ti, Justin's chart spelling): te falls to l (the ♭7 colour, e.g. d te l s).
  - Major with **fi**: fi rises to s (the leading note of the dominant).
  - Review 1/3: major or natural minor.
- Rhythm as M6.
- **Key cue for the modes:** D7b, recommendation: the mode's own tonic triad (r-f-l, s-t-r') at the fixed do register, with "Dorian on re" / "Mixolydian on so" shown above the stave.
- **Pool:** 20,000 distinct in 20,000. **Tells:** 42 checked, 0 failed.
- **UI:** ladder with te and fi rungs; the home label on r or s.

### M9 · Stage 6 · modulation to the dominant and the relative; do re-assigned at the pivot; 8 bars
- **Generator:** two 4-bar phrases joined at a pivot note (the last note of phrase 1, a note common to both keys; never fa going to V). Four kinds, a quarter each:
  - major → dominant: **do re-assigned**: new do = old so; old fi = new ti.
  - major → relative minor: **do stays** (la-based minor: the home moves d → l and si appears). No re-assignment.
  - minor → relative major: do stays.
  - minor → dominant minor: new la = old mi, so do re-assigned (new do = old so; old ri = new si).
  - Phrase 1 uses M3/M5 rules, phrase 2 M3/M7 rules. Rhythm: M6 cells plus tam-ti, 8 bars, at least 16 notes.
- **Important (D8):** with la-based minor, the relative modulations never re-assign do. "do re-assigned at the pivot" applies to the two dominant kinds only.
- **Pool:** 20,000 distinct in 20,000. **Tells:** 42 checked, 0 failed (modulation kind against key, register and length).
- **Entry UI:** a "New key from here" control marks the pivot note; from there the ladder relabels (new do) and the stave writes the pivot's double name (e.g. "s = d") under it. For the relative kinds the student marks the pivot too (the home note moves), but the ladder keeps its syllables and only moves "home".
- **Marking:** pitches are compared as sounds (each note's spelling in the key in force where the student puts the pivot). The pivot is right if marked on the true pivot note or on any note in the run of notes common to both keys immediately before the first note that belongs only to the new key. Both phrases right + pivot in that window = right.

### M10 · Stage 6 · all chromatic syllables as passing and neighbour notes; 8 bars
- **Generator:** an M6-style diatonic line (major or minor), then chromatic notes inserted (2/3 of items, at least one): rising passing notes raised (d di r, r ri m, f fi s, s si l, l li t); falling passing notes lowered (t te l, l le s, s se f, m me r, r ra d); lower chromatic neighbours raised (r di r, s fi s, l si l). Each insertion splits a crotchet into two quavers, so the rhythm stays in the rung's vocabulary.
- **Pool:** 20,000 distinct in 20,000. **Tells:** 42 checked, 0 failed.
- **UI:** a chromatic ladder (all twelve, the diatonic rungs full width and the chromatic ones as half rungs, up-pointing signs for sharps on the right, down for flats on the left, as on Justin's chart). Spelling follows direction; marking accepts only the spelling the rule above gives (fi rising, se falling); the feedback explains why when the pitch is right but the spelling is not. Should an enharmonic spelling with the right pitch count as Nearly? Recommendation in D4.

### M11 · Stage 6 · two-part: melody plus bass; 4–8 bars
- **Generator:** melody from M6/M10 rules (major or minor, 3/4 or 4/4, 4 or 8 bars drawn independently). Bass: one note per minim (4/4) or dotted minim (3/4), chord roots and first inversions of I IV V vi ii (minor: i iv V VI ii°), ending V–I (V–i). Outer-voice checks, reusing the climb-2 counterpoint checker: no parallel 5ths or octaves, no direct 5ths or octaves into a strong beat with a soprano leap, no crossing, the leading note in the bass rises. (The prototype bass is a placeholder for pool counting only; the build uses the checker.)
- **Pool:** 20,000 distinct in 20,000 (unsaturated even before the bass).
- **Tells:** 42 checked, 0 failed on the melody. Add for the bass: the bass's first and last notes against the length and key.
- **Notation:** grand staff (treble + bass), bass solfa under the lower stave.
- **Playback:** piano melody, bass samples (FluidR3 bass, already shipped) for the lower part; variants "Melody only", "Bass only", "Both".
- **Entry UI:** a part switch (Melody / Bass); the ladder reprints two octaves lower for the bass; the bass's first note given as well.
- **Marking:** each part marked separately; the item is right when both are (D4).

### M12 · Stage 6 · real repertoire, classical and contemporary
**Classical (playable): the ten licensed scores** (`scores/`, CC BY-NC-SA 4.0 / CC BY 4.0, NOTICE.md). `repertoire_scan.py` reads each Humdrum source (melody = the highest part; the top note at each onset; ties merged) and keeps 2- and 4-bar windows that: have 5–24 notes; contain no rest longer than a beat; have no leap over an octave; end on a tonic-triad note; and give each window a level (the lowest rung whose material covers it).

| | windows kept (sliding, overlapping) |
|---|---|
| all ten scores | **323** (every score contributes; Maple Leaf 133, Entertainer 56, K. 545 37, K. 331 theme 20, Chopin Op. 28/7 20, Jesu 15, Chopin 20 16, chorale BWV 269 19, O Haupt 13, K. 331 var. III 5) |
| by level | rung 3: 24 · rung 6: 87 · rung 7: 98 · rung 8: 51 · rung 10: 63 |

Overlapping windows are not all distinct items: phrase-aligned, non-overlapping excerpts are about a third (≈ 100). **Rung 12 is curated, not generated**, so the ≥ 100 rule does not bind; the build should hand-pick about **40–60 phrase excerpts** from this list using each score's own key and section data in `meta.json` (`sections`, `cads`). The scan's per-window keys come from automatic analysis and are not reliable (it read the K. 331 theme's first bars as B minor). Each pick goes through the independent theory check.
- Playback: the score's own note events (`AN.meta[score].events`), top line only (variant "Melody alone") and full texture (variant "With the accompaniment"); the key cue first. **UI and marking:** as M6–M10 (tied notes merged; ornaments and grace notes left out of the answer and played).

**Contemporary (links only; the app can't play them):** the student opens the link at the timestamp, listens, then writes the phrase in the app; the app shows the key signature, the metre and the first note, and marks against a stored transcription (solfa + rhythm). Candidates in section 6. Storing short transcriptions of copyright melodies is decision D13.

---

## 3. Rhythm ladder

### 3.0 Common to every rung
- **Units (rule U, LR-5):** ticks, **420 to a crotchet** (the LCM of 12, 5 and 7: semiquaver 105, quaver 210, triplet quaver 140, quintuplet semiquaver 84, septuplet semiquaver 60). The prototype uses 12 (no 5- or 7-tuplets in it). `RCELL.u`, `earFill`, `rhyOnsets`, `earRhyBeats`, `earRhySVG` and the result marks change from 16-per-bar to ticks.
- **Metre** shown (signature drawn); bars shown as outlines with beat placeholders (FR-12 as now).
- **Sound:** clap at rung 1, tone from rung 2 (approved); one bar of woodblock count-in; pulse switchable.
- **Notation:** the one-line rhythm stave (approved); stick notation at rung 1 as now.
- **Entry:** tiles per cell with their time name underneath (approved: names on every tile at every rung); compound-time tiles appear only in compound metres; tuplets are tiles with the bracket and figure.
- **Marking (all rungs):** right when the sounding pattern (onsets of notes and rests, held lengths) is the same as the answer, bar by bar. Where two notations sound the same, the rung's notation rule decides which is right; the other is "Nearly" only where this register says so (D11). Per-beat ticks in the result as now.
- **Fill rules (RF):** a cell starts on a beat (simple: a crotchet beat; compound: a dotted-crotchet beat); two-beat cells (ta-a, tam-ti, syn-co-pa) only on strong beats, so the middle of a 4/4 bar stays visible; ta-a-a from beat 1 (3/4, 4/4); ta-a-a-a only as a whole 4/4 bar; no bar is all rest.

### R1 · Stage 4 · crotchet, quaver pair, minim, crotchet rest; 4/4; 1 bar
- **Generator:** one 4/4 bar of ta / ti-ti / sa per beat or ta-a on beats 1 or 3; a rest may fall on any beat (the pulse carries on); never a silent bar.
- **Pool:** **99 exact** (100 four-beat bars less the silent one). With 0.48's rest rule (no rest first or last) 49; as built today 25. Below 100 under any rule: **decision D1**.
- **Tells:** 20 checked, 0 failed. **Sound:** clap, 72 bpm. **Names:** ta, ti-ti, ta-a, sa (approved).

### R2 · Stage 4 · + semibreve, dotted minim; 2/4 and 3/4; 2 bars
- **Generator:** metre 2/4, 3/4 or 4/4; 2 bars; new cells ta-a-a-a (whole 4/4 bar), ta-a-a (beat 1 of 3/4 or 4/4). New thing = the new cells (2/3); the new metres are on screen, so they are not a hidden "new thing".
- **Pool:** 5,658 distinct in 20,000. **Tells:** 25 checked, 0 failed.
- **Names:** ta-a-a-a (semibreve), ta-a-a (dotted minim): approved 21:24.

### R3 · Stage 4 · + four semiquavers
- **Generator:** R2 + tika-tika on any beat. **Pool:** 7,649 / 20,000. **Tells:** 25 / 0.

### R4 · Stage 5 · + dotted crotchet–quaver, quaver–two semiquavers, two semiquavers–quaver, quaver rest
- **Generator:** R3 + tam-ti (beats 1 or 3), ti-tika, tika-ti, and the quaver-rest cells "sa ti" (rest on the beat) and "ti sa" (rest on the half-beat).
- **Pool:** 12,311 / 20,000. **Tells:** 25 / 0.
- **Names:** tam-ti, ti-tika, tika-ti (approved); quaver rest **sa** (half a beat: "ti sa", "sa ti"), approved 21:24.

### R5 · Stage 5 · 6/8: the six standard cells
- **Cells (one dotted-crotchet beat each):** tam (dotted crotchet), ti-ti-ti (three quavers), ta ti (crotchet–quaver), ti ta (quaver–crotchet), tim-ka-ti (dotted quaver–semiquaver–quaver), tika-tika-tika (six semiquavers). Approved 21:24. Plus, as review across a whole bar, the dotted minim (ta-a-a, named by value).
- **Generator:** 2/3 of items in 6/8 (2 bars), 1/3 in a simple metre with R4 material.
- **Pool:** 6,981 / 20,000. **Tells:** 25 / 0.
- **Tiles:** the six compound tiles replace the simple ones when the metre is 6/8; beams group by the dotted crotchet.

### R6 · Stage 5 · syncopation: quaver–crotchet–quaver, ties across the beat, anticipations of beats 1 and 3
- **Cells:** syn-co-pa (beats 1–2 or 3–4); the same sound across beats 2–3, written ti ti⌒ti ti with the tie at the bar's middle (the notation rule there); anticipations: a quaver on 2& tied over to beat 3, or on 4& tied over to the next bar's beat 1 (never after the last bar).
- **Names:** by the approved tie rule, a tied note is held on the vowel of the first note, no new syllable: anticipation "ti ti-i…"; across the bar's middle "ti ti-i ti". **Flag (D11):** the tied form across beats 2–3 sounds exactly like syn-co-pa; the approved rule names it "ti ti-i ti". Recommendation in D11.
- **Generator:** R5 vocabulary (simple and 6/8) + these; 2/3 contain one.
- **Pool:** 13,795 / 20,000. **Tells:** 25 / 0.
- **Marking:** a crotchet across the middle of a 4/4 bar where the answer has the tie is Nearly (right sound, notation that hides the beat), not right (D11).

### R7 · Stage 5 · triplets, dotted quaver–semiquaver, anacrusis, 12/8
- **Cells:** tri-o-la (triplet quavers in one beat); tim-ka (dotted quaver–semiquaver); 12/8 uses the six compound cells. Anacrusis in 30% of items (quaver or crotchet; quaver in compound), the last bar shortened by the same length.
- **Names:** tri-o-la (Kodály) **or ta-ki-ta** under the "Kodály with konnakol tuplets" setting (Justin 21:31, section 4.3); tim-ka (approved 21:24).
- **Pool:** 16,589 / 20,000. **Tells:** 25 / 0 (anacrusis given the metre included).

### R8 · Stage 6 · swing, backbeat patterns, tresillo (3+3+2), Charleston
- **Generator:** 4/4, 2 bars, R7 simple cells plus:
  - **tresillo** (dotted crotchet, dotted crotchet, crotchet; one bar), named beat by beat: **tam ti-i ta** (tam-ti, the ti held over beat 3 on its vowel, then ta);
  - **Charleston** (dotted crotchet, quaver on 2&, minim rest): **tam ti sa-a**;
  - **swing:** written straight quavers, played long-short (2:1); the names stay ti-ti, with a "swung" label on the stave (approved). The swing marking (♫ = ♩♪³) printed above the stave;
  - **backbeat:** the rhythm is played over a snare on beats 2 and 4 (kick on 1 and 3) as context: the student still writes one line (the tone). This is my reading of the approved row; D14.
- **Pool:** 18,935 / 20,000. **Tells:** 25 / 0.
- **Marking:** swing items marked on the straight notation (a swung pair written as triplet crotchet–quaver is Nearly).
- **Optional, not in the approved table:** ti-kam (semiquaver–dotted quaver, the Scotch snap), approved as a name; it fits here (pop and rap vocals) if Justin wants it at a rung.

### R9 · Stage 6 · 5/4 and 7/8 with groupings; 4 bars (+ quintuplets and septuplets, proposed)
- **Generator:** 2/3 of items in 5/4 (3+2 or 2+3) or 7/8 (2+2+3, 3+2+2, 2+3+2); 1/3 review in 2/4, 3/4, 4/4, 6/8. 4 bars. 5/4 bars fill as a 3/4 group plus a 2/4 group (cells never cross the grouping). 7/8: each 2-group is ti-ti, ta or ti sa / sa ti; each 3-group is ti-ti-ti, tam, ta ti or ti ta.
- **Names:** groups as ti-ti / ti-ti-ti (approved); held values by note value (ta, tam).
- **Grouping shown:** the beam groups and a dashed group line on the stave; the beat lane's grouping picture (`elPicSVG`) above.
- **Pool:** 19,989 / 20,000. **Tells:** 25 / 0.
- **Quintuplets and septuplets (decided, Justin 21:31: rung 9, with 5/4 and 7/8):** quintuplet semiquavers in one crotchet beat (**ta-da-ki-na-dom**, Justin's spelling) and septuplet semiquavers in one beat, named as usual in konnakol by their grouping: **ta-ki-ta ta-ka-di-mi** (3+4) or **ta-ka-di-mi ta-ki-ta** (4+3); the beaming (and a dashed sub-group mark) shows which grouping. They enter only in 4/4 and 5/4 items, at most one per bar, on a beat, in about 1/3 of the new-thing items (the other 2/3 carry the new metres). Needs rule U (420 ticks). Not in the prototype's counts; they can only add items. Tells to add: tempo and playing time against tuplet presence, given the metre.
- **Marking of tuplets:** right when the tuplet's onsets are right; 3+4 written for a 4+3 septuplet sounds the same (seven even notes) and is right: the grouping is an accent pattern, so the generator plays the first note of each group slightly louder (+3 dB) and the answer's grouping must match the accents (wrong grouping = Nearly).

### R10 · Stage 6 · two-part rhythm (kick and snare against a riff); grooves from real recordings
- **Generated part:** two lines on a two-line rhythm stave (upper: snare + kick as drum notation on one line with stems down for kick, up for snare; lower: the riff as a tone). 2 bars of 4/4. Kick on a quaver grid, always on beat 1, never on the snare's beats 2 and 4 (so both are heard); snare backbeat, or backbeat + a 4& pickup; riff from R6 vocabulary.
- **Pool (exact for the drums):** 32 kick patterns a bar × 2 snare patterns → 4,096 two-bar drum parts, × 3,977 distinct riff bars sampled. Far over 100.
- **Tells to test in the build:** tempo and playing time against the riff's first cell and against kick density; the riff's tone pitch against its rhythm.
- **Entry UI:** a part switch (Drums / Riff); drum tiles: kick quaver, kick crotchet, snare crotchet, rest; names: the same time names per part (flag 4.2 (5)).
- **Marking:** each part separately; right when both are.
- **Recordings:** a curated set with links and timestamps (section 6), marked like M12's contemporary items.

---

## 4. Time names

### 4.1 The approved set (Justin 20 Nov; extension approved 21:24), mapped to every cell in sections 2–3

| cell | name | rung |
|---|---|---|
| crotchet | ta | R1 |
| two quavers | ti-ti | R1 |
| minim | ta-a | R1 |
| crotchet rest | sa | R1 |
| minim rest | sa-a | R8 (Charleston) |
| dotted minim | ta-a-a | R2 (also the whole 6/8 bar) |
| semibreve | ta-a-a-a | R2 |
| four semiquavers | tika-tika | R3 |
| dotted crotchet–quaver | tam-ti | R4 |
| quaver–two semiquavers / two semiquavers–quaver | ti-tika / tika-ti | R4 |
| quaver rest (half beat) | sa ("ti sa", "sa ti") | R4 |
| 6/8 and 12/8, per dotted-crotchet beat | tam · ti-ti-ti · ta ti · ti ta · tim-ka-ti · tika-tika-tika | R5, R7 |
| quaver–crotchet–quaver | syn-co-pa | R6 |
| ties | held on the vowel of the first note (no new syllable) | R6 |
| triplet | tri-o-la (optional ta-ki-ta) | R7 |
| dotted quaver–semiquaver / semiquaver–dotted quaver | tim-ka / ti-kam | R7 / (R8 optional) |
| swing | the straight names + "swung" | R8 |
| tresillo / Charleston | beat by beat: tam ti-i ta / tam ti sa-a | R8 |
| 5/4 and 7/8 groups | ti-ti / ti-ti-ti per group | R9 |
| quintuplet | ta-da-ki-na-dom | R9 (Justin 21:31) |
| septuplet | ta-ki-ta ta-ka-di-mi (3+4) / ta-ka-di-mi ta-ki-ta (4+3), following the grouping | R9 (Justin 21:31) |

### 4.2 Cells the approved set does not cover yet (flags)
1. **Syncopation tied across the bar's middle** (sounds as syn-co-pa; the tie rule gives "ti ti-i ti"). D11.
2. **Compound rests:** a dotted-crotchet rest (a whole 6/8 beat) and a quaver rest inside a compound beat (e.g. ti sa ti). The approved rest rule (sa, sa-a by value) suggests "sa-a" for the dotted crotchet? A rest of 1½ beats has no "by value" name in the set. Recommendation: dotted-crotchet rest = **sam** (as tam is to ta); quaver rest inside a compound beat = sa ("ti sa ti"). Only needed if compound rests enter (they are not in R5's six cells; recommended: keep them out until Justin names them).
3. **Triplet with a rest** (e.g. tri-sa-la): not generated; keep out.
4. **Quintuplets and septuplets under the default "Kodály names" setting.** Justin's setting lists ta-da-ki-na-dom and the septuplet names under the konnakol option; the Kodály set has no names for 5- and 7-tuplets. Recommendation: under "Kodály names" the tiles show the figure only (5, 7) with "five" / "seven" spoken in the feedback, and the konnakol names appear only in the konnakol setting; the alternative (konnakol names in both settings) is one line in the table. To confirm with Justin.
5. **Drum parts at R10:** whether kick and snare lines use time names, or a drum vocal (e.g. "dum" / "ka") as in beatbox and konnakol. Recommended: time names, the same rule as every other part.

### 4.3 The rhythm-names setting (decided, Justin 21:31: "an important part of my methodology which is intercultural")
- One Ear Lab setting, **Rhythm names: "Kodály names" (default) or "Kodály with konnakol tuplets"**, saved in `cjg_ear` (`EAR.names`, values `'k'` / `'kk'`).
- "Kodály with konnakol tuplets" changes only the tuplet names: triplet **ta-ki-ta** (in place of tri-o-la), quintuplet **ta-da-ki-na-dom**, septuplet **ta-ki-ta ta-ka-di-mi** (3+4) / **ta-ka-di-mi ta-ki-ta** (4+3) following the grouping. Every other cell keeps its Kodály name.
- Build: one table per setting, `RHYNAMES` and `RHYNAMES_KK = {...RHYNAMES, tri:'ta-ki-ta', q5:'ta-da-ki-na-dom', q7_34:'ta-ki-ta ta-ka-di-mi', q7_43:'ta-ka-di-mi ta-ki-ta'}`; `earRhyTile` and the reveal read the table for the setting; the journal line records which names were in use. Names are labels, never answers: the setting changes no marking.
- The setting sits with the rhythm drill's listening options (pulse, tempo) and is shown from the first rung that has a tuplet (R7), so Stage 4 students never see an option they can't use yet.

---

## 5. Shared UI, state and tests

### 5.1 Rung choice and "ready for the next rung?"
- The rung strip lists every rung shown by the Stage filter (1–12 / 1–10; on phones a scrollable strip with the current rung in view). Free choice of rung as now.
- **Readiness:** per drill and rung, a ring buffer of the last 10 *answered* outcomes (ok / miss). When 8 of the last 10 are ok and a higher rung is shown at this Stage, the result panel adds one line: "Ready for the next rung? Rung n+1: <its new thing>", with a button that moves there (no automatic move). What counts: D10.
- Saved as `EAR.rd[drill][rung] = [1,0,1,…]` (last 10) in `cjg_ear`.

### 5.2 Desk changes
- Melody from rung 4: duration palette + ladder (D3); bar outline with the first note given (pitch and length); "bar b of n, beat k" in place of "k of N notes" (MU1); the student's notes appear on the stave as entered (approved); undo/redo as now.
- Rhythm: tiles grouped by family (simple / compound / tuplets), only the rung's tiles shown; the metre decides which family is live.

### 5.3 Tests to add (port of the prototype)
- `earlab_test` D: pool ≥ 100 distinct per generated rung (melody 2–11, rhythm 2–10; melody 1 ≥ 100 as built; rhythm 1 per D1).
- `earlab_test` C: the tell table above, rung by rung, 5,000 seeded items, margin 5 points over the given-information baseline.
- New-thing share 0.60–0.73 per rung; review items in the same format.
- Range G3–B5; do = 60 + pc for every mode (MR1).
- Rhythm notation rules RF; anacrusis shortens the last bar by the same length.
- Time names: every tile at every rung has a name from the one table (extends earlab_ui_test C to 10 rungs and the konnakol setting).
- M9 pivot window; M11 counterpoint checker on every item (seeded 2,000).

---

## 6. Candidate recordings (links and timestamps only; the app does not play them)

Every row needs an **independent source check** before use (IC): the timestamp, the key, the transcription, and content suitability. Links marked ✓ were confirmed as the official upload's ID through a web search today (mirror pages list the official title with that ID); "page" means a confirmed page about the recording, with the official video still to be located. Timestamps are from memory: **all ⚠**.

### 6.1 Melody rung 12, contemporary (era span to the present)

| # | recording | year | link | excerpt ⚠ | rung material |
|---|---|---|---|---|---|
| 1 | The Beatles, "Hey Jude" | 1968 | page: https://www.thebeatles.com/hey-jude-0 | 0:00–0:12, first vocal phrase | major, leaps in the tonic triad (M6) |
| 2 | Bill Withers, "Lean on Me" | 1972 | page: https://en.wikipedia.org/wiki/Lean_on_Me_(song) | first verse, ~0:10 | stepwise major (M4) |
| 3 | The White Stripes, "Seven Nation Army" (the riff) | 2003 | ✓ https://www.youtube.com/watch?v=0J2QdDbelmY | riff from 0:00 | natural minor (M5) |
| 4 | Adele, "Someone Like You" | 2011 | ✓ https://www.youtube.com/watch?v=hLQl3WQQoQ0 | verse 1, ~0:13 | major (M6) |
| 5 | Vance Joy, "Riptide" (Australian) | 2013 | page: https://en.wikipedia.org/wiki/Riptide_(Vance_Joy_song) | chorus, ~0:45 | major (M4–M6) |
| 6 | Ed Sheeran, "Shape of You" (the marimba riff) | 2017 | ✓ https://www.youtube.com/watch?v=JGwWNGJdvx8 | intro riff, 0:00 (the video has a spoken/visual intro: check) | minor pentatonic (M5) |
| 7 | Tones and I, "Dance Monkey" (Australian) | 2019 | page: https://en.wikipedia.org/wiki/Dance_Monkey | first verse hook | minor (M5–M7) |
| 8 | Olivia Rodrigo, "drivers license" | 2021 | page: https://en.wikipedia.org/wiki/Drivers_License_(song) | verse 1, ~0:16 | major (M6) |

Gap: nothing from 2023–2026 confirmed yet (the span reaches the present; IC to add one or two recent picks under the C11 song rule: two sources or one authoritative).

### 6.2 Rhythm rung 10, grooves

| # | recording | year | link | excerpt ⚠ | what to write |
|---|---|---|---|---|---|
| 1 | Queen, "We Will Rock You" | 1977 | page: https://en.wikipedia.org/wiki/We_Will_Rock_You | 0:00, stomp-stomp-clap | kick ti-ti, snare ta, per bar |
| 2 | Michael Jackson, "Billie Jean" | 1982 | ✓ https://www.youtube.com/watch?v=Zi_XLOBDo_Y | drum intro, then the bass riff enters (the video's timing differs from the album: check) | kick 1 and 3, snare 2 and 4, against the bass riff |
| 3 | The White Stripes, "Seven Nation Army" | 2003 | ✓ https://www.youtube.com/watch?v=0J2QdDbelmY | the kick under the riff, opening section | kick crotchets against the riff |
| 4 | Daft Punk, "Get Lucky" | 2013 | page: https://en.wikipedia.org/wiki/Get_Lucky_(Daft_Punk_song) | opening groove | backbeat against the guitar riff (syncopated, R6 cells) |
| 5 | Ed Sheeran, "Shape of You" | 2017 | ✓ https://www.youtube.com/watch?v=JGwWNGJdvx8 | the tresillo riff, then the beat | tresillo (tam ti-i ta) against the backbeat |
| 6 | Billie Eilish, "bad guy" | 2019 | page: https://en.wikipedia.org/wiki/Bad_Guy_(Billie_Eilish_song) | opening: four-on-the-floor kick, snaps, the bass riff | kick crotchets, snaps 2 and 4, bass riff |

Source pages found in today's search: [Billie Jean (mirror listing of the official video ID)](https://videohighlight.com/v/Zi_XLOBDo_Y), [Seven Nation Army (mirror listing)](https://videohighlight.com/v/0J2QdDbelmY), [Shape of You (mirror listing)](https://videohighlight.com/v/JGwWNGJdvx8), [Someone Like You (mirror listing)](https://videohighlight.com/v/hLQl3WQQoQ0), [The Beatles, Hey Jude music video page](https://www.thebeatles.com/hey-jude-0), [We Will Rock You (Wikipedia)](https://www.wikipedia.org/wiki/We_Will_Rock_You), [Riptide (Wikipedia)](https://en.wikipedia.org/wiki/Riptide_(Vance_Joy_song)), [Dance Monkey (Wikipedia)](https://en.wikipedia.org/wiki/Dance_Monkey), [Drivers License (Wikipedia)](https://en.wikipedia.org/wiki/Drivers_License_(song)), [Lean on Me (Wikipedia)](https://en.wikipedia.org/wiki/Lean_on_Me_(song)), [Get Lucky (Wikipedia)](https://www.Wikipedia.com/wiki/Get_Lucky_(Daft_Punk_song)), [Bad Guy (Wikipedia)](https://www.wikiwand.com/en/Bad_Guy_(Billie_Eilish_song)).

Content notes (IC to confirm): "Billie Jean" (paternity accusation), "bad guy" (mild menace), "Shape of You" (mild romantic/physical lyric). The excerpts are instrumental or opening phrases.

---

## 7. Decisions for Justin

Each has a recommendation. Everything else in this register follows from the approved framework or from Justin's decisions of 20 Nov (names 21:24, tuplets and the names setting 21:31).

**D1 · Rhythm rung 1 pool.** One bar of 4/4 with ta, ti-ti, ta-a, sa allows at most 99 bars (100 less the silent one), below the ≥ 100 rule. (a) Keep 1 bar, allow a rest on any beat, accept 99 with a no-repeat window of the last 30 items. (b) Make rung 1 two bars (9,801). **Recommend (a):** four-beat patterns are the Kodály starting unit, and 99 with no repeats in 30 is as good in practice as 100.

**D2 · New-thing share.** **Recommend 2/3** of items contain the rung's new thing and 1/3 review earlier material in the same format. (Alternatives: 1/2, which makes the new thing less likely to be guessed but less practised; or every item, which makes "where is the new thing?" a guess.)

**D3 · Entering melodies with rhythm (rung 4 on).** (a) A duration palette (ta, ti-ti halves, ta-a …) that stays selected, then tap the ladder: each tap writes a note of that length, like notation software. (b) Two passes: tap the rhythm first on the one-line stave (as the rhythm drill does), then fill the pitches onto it. **Recommend (b):** it reuses the rhythm drill's entry and teaches the Kodály order (rhythm, then pitch); the feedback can mark rhythm and pitch separately.

**D4 · Partial credit.** **Recommend:** all or nothing for the score (as every drill now); the result shows each note's pitch and rhythm ticks; "x of y notes right" goes in the journal line. No Nearly for melodies, except M10, where the right pitch with the other spelling (fi for se) would be Nearly (streak kept, not scored).

**D5 · The augmented 2nd (f–si) in harmonic minor (M7).** Current code forbids it. **Recommend: allow it** in harmonic-minor items (it is the sound that defines the scale), as a step, no more than once per item.

**D6 · "All diatonic leaps" at rung 6.** **Recommend:** 3rds to 6ths and the octave; the tritone only as t–f inside a dominant-7th outline that resolves; 7ths left out (Stage 6 material).

**D7 · Modal items (M8): solfa and key cue.** The approved framework says parent-major solfa (Dorian on re, Mixolydian on so). Confirm, and the cue: **recommend** the mode's own tonic triad as the cue (r-f-l, s-t-r'), with "Dorian on re" / "Mixolydian on so" shown.

**D8 · Modulation kinds (M9).** In la-based minor the relative modulations keep do (only the home note moves). **Recommend** all four kinds (to V and to the relative, from major and from minor), with the pivot marked in all four but do re-assigned only for the dominant kinds.

**D9 · Anacrusis shown or found by ear.** An upbeat and a first bar that opens with rests sound the same after a count-in. **Recommend: show it** (the bar outline draws the short first bar); the skill is placing the upbeat's notes.

**D10 · What counts towards "8 of the last 10".** **Recommend:** answered items only (right or wrong); Shown, Skipped and Nearly do not enter the window.

**D11 · Tied syncopation across the bar's middle (R6).** It sounds as syn-co-pa; by the approved tie rule it is named "ti ti-i ti". (a) Name by notation: "ti ti-i ti" (the tie rule, consistent with anticipations). (b) Name by sound: "syn-co-pa" wherever it is heard. **Recommend (a)** on the tile and the stave, with the feedback saying "it sounds like syn-co-pa, written with a tie because it crosses the middle of the bar"; a plain syn-co-pa (crotchet across the middle) for it is Nearly.

**D12 · (decided by Justin 21:31, recorded in sections 3 R9 and 4.3: quintuplets and septuplets at rung 9; konnakol septuplet names by grouping; the "Kodály names" / "Kodály with konnakol tuplets" setting.)** One open point remains, flag 4.2 (4): what the 5- and 7-tuplet tiles show under the default "Kodály names" setting. Recommend: the figure only (5, 7), with the konnakol names in the konnakol setting.

**D13 · Recordings: transcriptions and playback.** Contemporary items in M12 and R10 need a stored transcription (a few bars of solfa and rhythm) to mark against, and the student plays the link in another tab. Storing short melodic transcriptions for non-commercial education is likely within fair dealing for education, but it is a legal judgement, not mine ⚠. **Recommend:** store only the excerpt's notes (no lyrics, no audio), one phrase per song, credit the recording, and have the IC check each one; or leave contemporary items as "listen and compare with the shown answer" (unmarked) until checked.

**D14 · Backbeat at rung 8.** The approved row lists "backbeat patterns" for a one-line rung, while two-part rhythm is rung 10. (a) The backbeat is context: snare on 2 and 4 (kick on 1 and 3) plays under the line the student writes. (b) The student writes the backbeat itself (kick and snare) on the one line, as a two-sound line. **Recommend (a):** it keeps rung 8 one-line and leaves writing drum parts to rung 10.
