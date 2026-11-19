# Independent check: Ear Lab theory accuracy and marking, CJG 0.48

Build checked: `/home/claude/wt-check-int`, detached at `fde5842` (read-only). Scratch and scripts: `/home/claude/checks/ear/`.
Method: the repo harness (`tests/harness/cjg.py`, Chrome, Playwright) with my own xorshift seeds; my own checkers (music21 for chord
spelling, my own voice-leading, fact and tell code). I did not reuse `earlab_items_test` section P. I formed every verdict below before
reading `EL_logic_048_report.md`, `EL_reconcile_048_report.md` and `EL_fablefix_report.md`; the comparison is in the last section.

Scripts: `dump.py` (generates items in the page, answers every option, captures the result panel's head/teach/chord strip),
`cadcheck.py`, `metrecheck.py`, `qualcheck.py`, `rhycheck.py`, `melcheck.py`, `basscheck.py`, `tells.py`, `ui.py` (real clicks on the
card), `render.py` (offline render of all eight metres), `tiles.py`. Screenshots: `metre_grid_r3.png`, `cad_nearly.png`, `tiles_r3.png`.

## Verdict table

| Area | Verdict | Counts |
|---|---|---|
| Cadence answers (my own category from the last chords vs `q.a`), music21 spelling and bass of every chord | PASS | 10,400 items (rungs 1/2/3: 2,600/3,600/4,200), 0 errors |
| Cadence rung shape (rung 1 major, two chords, open voicing, four answers; rung 3 five chords from I–IV / i–iv, six buttons) | PASS | 0 errors |
| Judging: correct / Nearly / wrong for every option | PASS | 10,400 items x 5–7 options, 0 errors. Nearly only for Phrygian->Imperfect and 6/4->Perfect at rung 3; reverse cases wrong; I⁶₄–V–vi with "Cadential 6/4" wrong (flag false) |
| Tally effects in the running card (real clicks) | PASS | 16 scripted steps + flag toggle: Nearly gold, streak kept, not in answered/score, "· n nearly" in foot; wrong resets streak; Shown and Skipped counted, streak kept |
| Cadence teaching sentences true of the item | PASS with one Could | 60,400 sentences (75 distinct templates); 63 sentences in 9 items (0.2% of rung 3) say the bass "stays on" the dominant where it drops an octave |
| Cadential 6/4 chip label | FAIL (Should) | Hover gives both readings on all 7,238 6/4 chips; but in all 5,404 cadential-6/4-answer items the chip reads "bass so/mi", not "cadential 6/4" |
| Strict voice leading, cadences | PASS rung 1 and 3, FAIL rung 2 (Should) | rung 1 0/2,600, rung 3 0/4,200; rung 2 35/3,600 items (1.0%) |
| Strict voice leading, bass and numerals realisations | FAIL (Should) | 23/800 items (2.9%) |
| Harmonic successions (common practice) | FAIL (Should) | ii⁶–IV / ii°⁶–iv in 340/3,000 rung 2 cadence items (11%) |
| Metre: grid per rung, accent pattern and subdivisions from the click events, audio accent levels | PASS | 1,800 items x 4 bars, 0 errors; 8 metres rendered: down > accent > beat > split, 5 dB steps |
| Metre: new 5/4 and 7/8 wording vs playback and theory | PASS | 5/4 accents [beat 1 heavy, beat 4 lighter accent] = 3+2; 7/8 accents on quavers 1, 3, 5 = 2+2+3 |
| Metre: answer-grid layout | FAIL (Must) | 5/4 sits under the column header "Duple · 2 beats in a bar" on every rung 3 question |
| Metre: other teaching sentences | PASS with one Should | 72 (answer, given) cases all true of the metre; "You heard six quavers in every bar" vs randomly dropped subdivisions |
| Chord quality (root position, close, two registers, spelling, sentences) | PASS | 1,600 items, 0 errors; 53 sentence cases all true |
| Rhythm dictation (marking, sentences, tile names) | PASS | 800 items, 2,356 wrong-answer sentences, 0 errors |
| Melodic dictation (movable do, la-based minor, octave marks, sentences) | PASS | 600 items, 0 errors |
| Bass and numerals (answers, successions, bass solfa, sentences) | PASS | 800 items, 368 distinct sentences, 0 false |
| Blind analysis sentences | FAIL (Should) | "the leading note rises to the home note" false for 2 of 17 perfect excerpts; "V to I" shown for 4 minor-key "V–i" excerpts |
| Tells | PASS apart from the two known ones | see section 7 |

## 1. Musts

**M1. Metre grid: 5/4 sits in the "Duple · 2 beats in a bar" column.**
Evidence: `earMetreGridHTML` puts `['Irregular','uneven groupings',['5/4','7/8']]` under the three column headers (Duple / Triple /
Quadruple, with "2 / 3 / 4 beats in a bar"). In the running card at rung 3, 5/4 is at x=273 (the Duple column) and 7/8 at x=483
(Triple) (`ui_log.txt`, `metre_grid_r3.png`). The 5/4 teaching sentence says "Five beats in a bar", the cell's own picture shows five
beats, and `METRES['5/4'].b` is 5. So on every rung 3 metre question the grid tells a Stage 5 student that 5/4 has 2 beats in a bar.
(7/8 under Triple is consistent: the app treats it as three unequal beats, `b:3`, and the sentence says the beats are not the same length.)
Fix: give the Irregular row cells that do not sit under the beat-count headers. For example, let the two cells span the row with no
column meaning, add a sub-caption in each cell ("5 beats, 3+2" and "3 uneven beats, 2+2+3"), or close the header row before the Irregular
row. If Justin prefers the "two unequal beats" reading of 5/4, then the sentence, the picture and `METRES` must all change to match.

## 2. Shoulds

**S1. Rung 2 cadence realisations break strict rules (35 of 3,600 items, 1.0%).**
- Tenor leaps an augmented 4th, VI–V in minor: `cad:2:112` E minor `i VI V i`, voicing `[[52,59,64,67],[48,60,64,67],[47,54,63,71],[52,55,64,71]]`:
  tenor C4 (60) to F♯3 (54). Same in `i VI V VI` (E minor) and in G minor (E♭4 to A3). 19 items.
- Bass leaps a minor 7th: C minor `i iv i:1 iv i`, bass F2 (41) to E♭3 (51); G major `I vi V7 I` / `I vi V7 vi`, bass E2 (40) to D3 (50). 8 items in the 3,000 sample, more in the first.
Rung 2 is not run through the strict rules (`earCadProg` uses `strict` only at rung 3). The brief says strict voice leading must pass for
chorale realisations; the code comment limits strict to rung 3. If rung 2 counts as a chorale realisation, this is a Must.
Fix: run rung 2 through `earSATB(...,{strict:true,rns})` (with an opening voicing as `earCad3Open`), or at least add the tritone leap and
the 7th leap to its rejections, and re-check the balance/tell tests.

**S2. Bass and numerals realisations break strict rules (23 of 800 items, 2.9%).**
- The raised 4th (fi) of V7/V does not rise (16 items). Example `bass:3:53` F major `I vi V7/V V`, `[[41,57,65,72],[50,57,65,74],[43,59,65,74],[48,55,64,72]]`:
  tenor B3 (59, fi) falls to G3 (55) instead of rising to C4. Also A major `I IV V7/V V`, B♭ major `I vi V7/V V`, A♭ major `I V7/V V I`.
- Bass leaps a minor 7th, vi up to V (7 items): G major `I vi V vi`, bass E2 (40) to D3 (50).
Fix: realise the bass drill with the strict rung 3 rules (they already contain "the raised 4th of V7/V rises a semitone" and the 7th leap).

**S3. ii⁶–IV (ii°⁶–iv) in rung 2 cadence models (340 of 3,000 items, 11%).**
Models `I ii:1 IV I`, `I vi ii:1 IV I`, `i ii°:1 iv i`, `i VI ii°:1 iv i` (plagal) and `I ii:1 IV V`, `i ii°:1 iv V` (imperfect) move
ii(6) back to IV. In common-practice harmony this is a retrogression (pre-dominant moves forward ii→V; IV→ii is normal, ii→IV is not).
The app's own bass drill forbids it (`EBALLOW.ii = ['V','V7/V']`), so the two drills teach different rules.
Fix: replace these with IV–ii⁶ or other forward successions of the same length (keeping the "same second chord in every category" balance).

**S4. Cadential 6/4 chip in cadential-6/4-answer items reads "bass so", not "cadential 6/4".**
`earChordRowHTML` labels the 6/4 chip "cadential 6/4" only when it is outside the cadence bracket (that is, only in the interrupted-through-6/4
items). In every item whose answer is Cadential 6/4 (5,404 chips in my samples), the chip inside "THE CADENCE" bracket reads "I⁶₄ · bass so"
(`cad_nearly.png`). The hover is right everywhere (both readings, Ic and part of the dominant). The brief says the chip is labelled
"cadential 6/4". The reconcile report says this was deliberate. Fix: label it "cadential 6/4" in the bracket too (the bass solfa can move
to the hover, or show both: "cadential 6/4 · so"), or have Justin confirm the current split.

**S5. Blind analysis: two generic sentences are false for real excerpts.**
For blind items `earCadFacts` has no voicing, so the generic "V to I: the leading note rises to the home note and the bass lands there"
is shown for every perfect cadence. Checked against `scores/meta.json` events at the cadence arrival:
- `chorale` bar 14, "Perfect cadence in C major (a tonicisation)", V7/IV–IV: the leading note B falls (B4 to G4); none rises to C.
- `jesu` bar 6, "Perfect cadence (V–I)", V7–i: D♯4 falls to B3 (the inner-voice leading note drops to the 5th); the soprano comes F♯5–E5.
- (`chopin7` bars 7 and 15: G♯4 is held over the arrival and rises to A4 half a beat later; true only loosely.)
- For the minor excerpts `jesu` bars 2 and 6 and `chopin20` bars 8 and 12 (chords "V7 – i") the sentence says "V to I".
Fix: for blind items, store per-cadence facts (leading-note rise, bass move, mode) in `meta.json` and choose the sentence from them, or use a
neutral sentence ("V to the home chord: the phrase closes."), and pass the mode so minor items say "V to i".

**S6. Metre: "You heard six quavers in every bar, and that is right."** (given 6/8 for 3/4, or 3/4 for 6/8)
Each subdivision click is played with probability 0.75 (`earGenMetre`), so in about 97% of these items not every bar has six sounding
quavers (3/4 bars have all three splits only 42% of the time; four bars together 3%). The metric fact is right, the "you heard" is not.
Fix: "Each bar holds six quavers, and that is right." (or play every split).

## 3. Coulds

- **C1. Cadential 6/4 bass drops an octave into V in 7 of 3,000 rung 3 items** (B♭ major and A major `I IV I:2 V I`, B♭ minor `i iv i:2 V i`;
  e.g. A major `[52,52,61,69] -> [40,52,59,68]`: bass E3 to E2). The sentences "the bass reaches the dominant early and stays on it" and
  "the bass is already on the dominant" are true of the degree, not the pitch. Fix: prefer a same-pitch bass for I⁶₄–V in `earCad3Open`/`earSATB`
  (the register search can avoid it), or say "stays on so".
- **C2. Register tells at cadence rungs 2 and 3**, in addition to the known rung 1 one: the exact lowest+highest note pair beats chance by
  +10.3 (rung 2) and +11.7 (rung 3) points, and the exact span by +6 to +9; at 4-semitone bands both fall to +1 to +5 (shuffled-answer
  baseline -0.4 to -1.5). Not perceptible at that resolution; note it with the rung 1 item.
- **C3. "Shown" uses the same gold as "Nearly"** (border rgba(201,162,74,.55) for both). Not wrong, but a student may read a Shown panel as
  a near miss. A neutral colour for Shown would separate them.
- **C4. `earAnsTxt` is dead code** (defined, never called). It still holds the older `CADFAM` text ("the decorated approach to V in a perfect
  or imperfect cadence ..."). Remove, so a later change does not revive unchecked text.
- **C5. Chip function labels**: iii, III, vi and VI chips read "tonic". Standard as tonic substitutes, but it is one tradition; the hover
  could say "tonic substitute" as the 6/4 hover does for its two readings.
- **C6. Compound metres**: the first split after each downbeat starts while the downbeat's low tone (0.25 s) is still sounding, so its peak
  reads up to 4.5 dB louder than the other splits (`render.py`). Inaudible as an accent in practice; listed for completeness.

## 4. Marking and tallies (detail)

`ui.py` clicks the real card at Stage 6, cadences rung 3 (log in `ui_log.txt`):
right, right -> streak 2; Phrygian answered Imperfect -> "Nearly", class `near`, gold (201,162,74), option `is-near`, stats n 2 ok 2 streak 2,
nearly 1, foot "2 answered · 1 nearly · 0 shown · 0 skipped"; cadential 6/4 answered Perfect -> Nearly likewise; Imperfect answered Phrygian
-> "Not this time", streak 0; Perfect answered Cadential 6/4 -> wrong; I IV I:2 V vi answered Cadential 6/4 -> wrong, with "You heard the
cadential 6/4, and it is there ... The answer names the cadence: Cadential 6/4 is the answer only when the 6/4 leads into a perfect cadence";
the same answered Interrupted -> correct with the 6/4-on-the-way sentence; Show me -> shown +1, n unchanged; Skip after a play -> skipped +1,
streak unchanged (1 stays 1). With `CAD64_INT_NEARLY=true` the same item gives Nearly (nearly +1). No page errors.
Rung 3 buttons: Perfect, Plagal, Imperfect, Interrupted, Phrygian, Cadential 6/4; key line "Perfect = US authentic · Imperfect = US half ·
Interrupted = US deceptive" (NSW-first names, US on hover and in the key line).

## 5. Metre (detail)

From the click events (1,800 items, every bar): 2/4 [down, beat]; 3/4 [down, beat, beat]; 4/4 and 12/8 [down, beat, accent, beat];
6/8 and 9/8 on the 3-way split; 5/4 [down, beat, beat, accent, beat] = 3+2; 7/8 quavers [down, ·, accent, ·, accent, ·, ·] = 2+2+3, every
quaver sounding. Every split falls on the half (simple, 5/4) or third (compound) of its beat. Offline render: downbeat -10 dB, accent -15,
beat -20, split -25 (5 dB steps, plus distinct pitches 1568/1175/988/784 Hz and a low tone on the downbeat), so the labelled accents are
what is heard. 5/4 sentence ("heaviest click on beat 1 and a lighter one on beat 4: 3+2") and 7/8 sentence ("seven quavers ... grouped 2+2+3
... beats not all the same length") are true of the playback and standard theory. Grid per rung: rung 1 2/4 3/4 4/4; rung 2 adds 6/8 9/8
12/8; rung 3 adds 5/4 7/8; the Irregular row sub-label is "uneven groupings". Only the column placement fails (M1).

## 6. Rhythm tile names (placeholders, listed as asked)

| Tile | Rhythm on the tile (seen in `tiles_r3.png`) | Name | Matches Kodály usage? |
|---|---|---|---|
| q | crotchet | ta | yes |
| e2 | two beamed quavers | ti-ti | yes |
| h | minim | ta-a | yes |
| s4 | four beamed semiquavers | tika-tika | yes (also ti-ri-ti-ri / ti-ka-ti-ka) |
| qr | crotchet rest | sa | names a rest; conventions vary (silent, "sh", "rest", "zah") |
| dq | dotted crotchet + quaver | tam-ti | yes (also ta-i-ti) |
| es2 | quaver + two semiquavers | ti-tika | yes |
| s2e | two semiquavers + quaver | tika-ti | yes |
| syn | quaver, crotchet, quaver | syn-co-pa | yes (also ti-ta-ti) |

Each name matches the rhythm on its tile.

## 7. Tells

| Drill / rung | Feature | Edge over chance | Note |
|---|---|---|---|
| Cadences 1 | lowest+highest note (exact / 2-semitone / 3-semitone bands) | +9.8 / +6.5 / +7.7 | the known open one (~+5–7) |
| Cadences 2, 3 | lowest+highest exact; span exact | +10.3 / +11.7; +6.4 / +9.3 | +1 to +5 at 4-semitone bands (C2) |
| Cadences 1–3 | key, mode, chord count, second chord, first bass/soprano | ≤ +2.1 | none |
| Metre 2, 3 | shortest inter-onset (subdivision speed), simple vs compound | +32 / +30 | the known open one |
| Metre 1–3 | bpm, playing time (0.5 s and 1 s) | ≤ +3.2 | none |
| Chord quality 1–3 | register, lowest, highest, root | ≤ +1.2 | none |

(Rung 1 "first chord voicing relative to the key" at +47 is the cadence's own first chord, so it is content, not a tell.)

## 8. What I could not check

- Listening by ear: tells and accents are measured from data and an offline render, not by a listener.
- Blind excerpts: my leading-note check is a heuristic on note events (no voice separation); only the two clear cases are reported.
- The reconcile report's 76,506-sentence figure: I did not rerun its suite. My own 60,400 cadence sentences found the issues above.
- Unequal 5ths, doubling preferences beyond the leading note and 7th, and the 3rd doubling in rung 1 major chords were not checked.
- Whether the strict rules are meant to cover rung 2 and the bass drill (S1, S2) is a scope decision for Justin.
- Phone layouts, transport timing and Stage 4/5 gating beyond reading `EARSTAGE` (metre rung 3 = Stage 5, cadence rung 3 = Stage 6: correct).

## 9. Builder reports compared (read after the verdicts)

- **Agree**: Nearly logic and tallies (logic §1); interrupted-through-6/4 kept and judged as described, `CAD64_INT_NEARLY=false` (logic §2);
  metre grids and accents (logic §3); the subdivision-speed tell (logic: 81% vs 50%; mine +30–32) and the rung 1 register tell (logic:
  +4.7 to +6.9 at 6-semitone bands; mine +6.5 to +9.8 by resolution); the metre wording changes (fablefix "Wording changes").
- **Agree, now with evidence**: reconcile §1 lists the blind "leading note rises" sentence as unverified. I found two excerpts where it is
  false and four minor excerpts that say "V to I" (S5).
- **Disagree / differs from the brief**: reconcile §3 keeps "bass so" on the 6/4 chip inside the cadence bracket by design; the brief says
  the chip is labelled "cadential 6/4" (S4). Reconcile P's "6/4 bass held" accepts an octave drop (C1).
- **Not covered by any report**: the 5/4 cell under "Duple · 2 beats in a bar" (M1); rung 2 and bass-drill strict-rule faults (S1, S2; the
  logic report's strict checks cover rung 3 only); ii⁶–IV retrogressions against the bass drill's own rule (S3); "you heard six quavers"
  (S6); register tells at rungs 2–3 at semitone resolution (C2); the dead `earAnsTxt` (C4).
