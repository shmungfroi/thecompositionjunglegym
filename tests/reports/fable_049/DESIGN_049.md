# Composition Jungle Gym 0.49 — design spec (Fable)

Branch `049-fable-design`, designed against the build at 3a75172 (0.48 with the 0.49 register). Specs and mock-ups only; `index.html` is not edited. Sonnet implements, I verify afterwards.

Everything measured here was measured in headless Chrome at 1440×900, 1366×768, 1024×768 and 390×844, with the new CSS injected into the live app. No real phone was used.

## What is in this folder

| File | What it is |
|---|---|
| `c5.css` | Corrections C5. **Lift into `index.html` as written**, at the end of the main style block. |
| `fn049.css` | Corrections C6: tokens and the function-letter cue. Lift as written. |
| `ladder049.css` | The 0.49 ladder components. Lift as written. Where this document and a CSS file disagree, the CSS wins. |
| `mock.js` | Mock-only helpers. Its functions `rp`, `last10`, `head`, `desk`, `sug` write the **reference markup** for `ladder049.css`. |
| `cvd_sim.py` | Colour-blind simulation and contrast script (C6). `--check` exits 1 on a failed rule, so it can join `tests/run_all`. |
| `c5_verify.py`, `shots_now.py`, `build_mocks.py` | The scripts that produced every number and picture here. |
| `mocks/*.html` | Static mock-ups (no scripts; open from disk), at 1366 and 390. `picker_states` also at 1440 and 1024. |
| `png/` | Renders of the mock-ups: `*_1366.png` and `*_390.png` (the screen), `*_card.png` (the whole card), `*_390_entry.png` (phone, scrolled into the entry). `png/metrics.json` holds the measurements. |
| `c5/` | Before and after pictures for C5 (`sheet_keys_390.png`, `sheet_rest.png` are the quick view) and `metrics.json`. |
| `now/` | The 0.48 state the ladder design starts from. |
| `cvd_swatches.png`, `fn_cue.png` | C6: the colours now and proposed under each simulation; the letter cue on a bar grid. |

---

# Deliverable 1 — corrections

## C5. Carried Shoulds

All six are in `c5.css`. Before and after, same script (`c5_verify.py`), no page errors at any size.

### C5-1 Phone header grows at the first answer

The empty tally is 38 px high and the counted tally 62 px, so the header jumps when the first answer lands.

| | 1440 | 1366 | 1024 | 390 |
|---|---|---|---|---|
| Header, empty → counted, before | 97 → 97 | 97 → 97 | 97 → 97 | **104 → 122** |
| After | 97 → 97 | 97 → 97 | 97 → 97 | **122 → 122** |

Change: on phones the Ear Lab tally holds `min-height:62px`. Same on all four drills measured (metre, cadences, melody, bass). Cost: the phone header is 18 px taller before the first answer. No markup change.

### C5-2 Unticked checkbox

The unticked box was the browser's white square (18 px in the Ear Lab, 13 px in Keys), and in Keys the ticked box was browser blue.

Change: one rule for every checkbox in the app. 18 px, 5 px radius, transparent with a 1 px `--muted` border; ticked, a gold ground with an ink tick; gold border on hover; the usual 2 px `--goldhi` focus ring. On phones the label row is 44 px (`label.tick`, `label.ck`, and any `label.note` holding a checkbox).

| | 1440 | 1366 | 1024 | 390 |
|---|---|---|---|---|
| Box, before (Keys / Ear Lab) | 13 / 18, native | 13 / 18 | 13 / 18 | 13 / 18 |
| Box, after | 18, drawn | 18 | 18 | 18 |
| Label row, Keys "up / down / together", before → after | 19 → 18 | 19 → 18 | 19 → 18 | **19 → 44** |
| Label row, Ear Lab "show letter names" | 20 | 20 | 20 | 44 (as before) |

No markup change. It applies to every room, so the Gym's "start at home", the Forms repeat box and the rest change with it; I looked at Keys and the Ear Lab only.

### C5-3 Keys tally at 1024

At 1024 a two-digit score (40 of 48) wraps the tally under the mode buttons and it lands on the left.

| 40 of 48 | 1440 | 1366 | 1024 | 390 |
|---|---|---|---|---|
| Tally left edge, before | 1179 (one row) | 1105 (one row) | **551, second row, left** | own row, right |
| After | 1179 | 1105 | **763, second row, right edge 975** | unchanged |

Change: `.kqhead .el-tally{margin-left:auto}`. The row is still two lines at 1024 with a two-digit score (85 px); it now reads as one right-hand column with the single-digit state.

### C5-4 Song-starter link colour

`.istart .sb a` had no rule: browser blue (`rgb(0,0,238)`), underlined, 20 px high.

Change: the same pill the song cards use elsewhere (1 px line, 14 px radius, ivory, no underline, gold on hover).

| | 1440 | 1366 | 1024 | 390 |
|---|---|---|---|---|
| Before | blue, underlined, 20 px | same | same | same |
| After | ivory pill, 26 px | 26 px | 26 px | **44 px** |

### C5-5 Keys interval controls on phones

At 390 the Intervals and Aural Gym pane had **49 controls under 44 px**. After: **none**.

| Control | Before | After |
|---|---|---|
| Start note, sharps and flats (`.rk button`) | 46×24 | 46×44 (the key is 91 px: two stacked) |
| Start note, naturals (`.rp`) | 46×50 | 46×91, letter at the foot (they read as piano keys) |
| Interval buttons (`.qp`) | 43 | 48 |
| Direction (`.ip`) | 32 | 44 |
| Mode buttons "Hear it · name it / Sing it back" | 28 | 44, two equal halves |
| Start, Hear it again, Next interval, voice buttons (`.mini`) | 28 | 44 |
| Answer chips (`.gans .chip`) | 30 | 44, at least 56 wide |
| Tick labels | 19 | 44 |
| Song-starter links | 20 | 44 |

The gym header (`.kqhead`) goes from 76 to 92 px. Desktop sizes are untouched (the rules sit inside `max-width:760px`). Picture: `c5/sheet_keys_390.png`.

### C5-6 Top-bar search collapsing at 1024

The title (355 px), crumb, Stage switch and Journal leave the search 57 px at 1024: a clipped "F".

| Search form / input | 1440 | 1366 | 1280 | 1181 | 1180 | 1024 | 901 | 761 | 390 |
|---|---|---|---|---|---|---|---|---|---|
| Before | 420 / 354 | 399 / 334 | 310 / 245 | 211 / 146 | 210 / 145 | **57 / 32** | 68 / 32 | **2 / 32** | 366 / 300 |
| After | 420 / 354 | 399 / 334 | 420 / 354 | 348 / 283 | 420 / 354 | **271 / 206** | 220 / 154 | **220 / 154** | 366 / 300 |

(1366 to 761 measured in the Analysis room, whose crumb is the longest.)

Changes:
1. 761–1280 px: the crumb is hidden (the rail and the room heading already say where you are).
2. 761–1180 px: title 18 px with 3 px tracking (355 → 295 px), bar gap 14 px, and the search has `flex:1 1 220px; min-width:220px`.
3. 761–900 px: the title drops "COMPOSITION" as it does on phones (133 px).
4. Markup: shorten the placeholder to `Type a chord: Bm7, E♭9…`. The present one is cut off at 1024 ("Type a chord: Bm7, F#din").

Nothing overflows the bar at any width from 761 to 1440.

### Seen on the way (new rows for the register, status Drafted; not fixed here)

- **N-1** Keys piano labels ("C3", "Middle C", "C5", "C6") are 10 px (`.piano .c`), under the 11 px floor. Should.
- **N-2** The song-card links in the other rooms (`.song .sb a`, `.c6h .sb a`) are the same 26 px pill on phones. Could: give them the 44 px phone rule from C5-4.
- **N-3** `--red` does two jobs: the dominant function and "wrong". C6 lifts it for both; see C6.

## C6. Colour-blind safety of the function colours

Script: `cvd_sim.py` (Machado, Oliveira and Fernandes 2009; full protanopia, deuteranopia, tritanopia, and severity 0.6 as a second view; differences in CIEDE2000; contrast by WCAG). Run `python3 tests/reports/fable_049/cvd_sim.py` for the present colours, `--proposed` for the proposal, `--search` for the search, `--check` to fail a test run.

### What fails now

**Contrast** (text needs 4.5:1; the stripe on the gold-washed "now" bar needs 3:1):

| Function | Hex | Page `#0b0906` | Inset / bar `#0e0c08` | Card `#12100b` | Wheel `#14110c` | Dock `#16130d` | Panel 2 `#17140e` | Tile `#1b170f` | "Now" bar |
|---|---|---|---|---|---|---|---|---|---|
| T tonic | `#8fbf6a` | 9.31 | 9.14 | 8.90 | 8.81 | 8.67 | 8.60 | 8.36 | 6.63 |
| PD pre-dominant | `#c9a24a` | 8.29 | 8.14 | 7.92 | 7.85 | 7.72 | 7.66 | 7.44 | 5.90 |
| **D dominant** | `#c8473b` | **4.19** | **4.11** | **4.00** | **3.96** | **3.90** | **3.87** | **3.76** | **2.98** |
| MD modal dominant | `#bd6b97` | 5.41 | 5.32 | 5.17 | 5.12 | 5.04 | 5.00 | 4.86 | 3.85 |
| C chromatic | `#a493d8` | 7.33 | 7.20 | 7.01 | 6.94 | 6.83 | 6.78 | 6.58 | 5.22 |

Dominant red fails as text on **every** ground, not only one (the 3.9 in the handover is the dock), and its stripe just misses 3:1 on the "now" bar. The ivory variant `#9e4776` on ivory is 4.50:1, exactly on the line.

**Pairs** (ΔE00; under 11 two small swatches cannot be told apart, 11 to 20 is weak):

| Pair | Normal | Protan | Deutan | Tritan |
|---|---|---|---|---|
| **T / PD** | 23.4 | **6.0** | **5.3** | 39.5 |
| T / D | 58.4 | 30.4 | 16.6 | 54.1 |
| T / C | 46.8 | 46.4 | 43.1 | 20.0 |
| PD / D | 36.2 | 26.3 | 15.6 | 22.8 |
| PD / MD | 46.5 | 40.6 | 32.4 | 13.6 |
| D / MD | 23.9 | 32.0 | 28.4 | 13.9 |
| MD / C | 19.3 | 14.0 | 15.4 | 26.1 |

- **Tonic and pre-dominant collapse** for red-green colour blindness (5.3 and 6.0): green and gold become the same olive-yellow. This is the one true collapse, and it is the most used pair in the app.
- Rose against violet (the pair the handover asked about) is weak for everyone, 19.3 with normal vision and 14 to 15 under protan and deutan, but it does not collapse.
- Rose against red is weak under tritan only (13.9).
- At severity 0.6 the picture is the same: T / PD 8.3 and 7.7.

### Proposal

Gold is the Garden's gold and violet is fine, so both stay. Three colours move, each inside its own Garden hue:

| Function | Now | Proposed | What moved | Worst text contrast | On the "now" bar |
|---|---|---|---|---|---|
| T tonic | `#8fbf6a` | **`#9dc995`** | lighter, a little cooler (towards the Garden's lush green) | 9.54 | 7.57 |
| PD pre-dominant | `#c9a24a` | unchanged | | 7.44 | 5.90 |
| D dominant | `#c8473b` | **`#d15e5d`** | lighter, a touch cooler (garnet) | **4.65** | 3.69 |
| MD modal dominant | `#bd6b97` | **`#b1729d`** | a little less pink, so the lifted red does not run into it | 4.90 | 3.89 |
| C chromatic | `#a493d8` | unchanged | | 6.58 | 5.22 |
| MD on ivory | `#9e4776` | **`#8b4978`** | follows the new rose | 4.90 on ivory | |

Pairs after:

| Pair | Normal | Protan | Deutan | Tritan |
|---|---|---|---|---|
| T / PD | 25.0 | **13.0** | **12.8** | 40.0 |
| T / D | 53.2 | 25.4 | 15.3 | 51.6 |
| PD / D | 35.4 | 22.3 | 12.9 | 17.1 |
| PD / MD | 46.0 | 41.3 | 35.2 | 12.6 |
| D / MD | 19.9 | 25.8 | 27.0 | 12.7 |
| MD / C | 16.4 | 12.6 | 13.0 | 23.6 |

Every rule in the script passes. What it does and does not buy:

- Every function colour is at least 4.5:1 as text on every ground, and at least 3:1 on the "now" bar.
- The worst pair goes from 5.3 to 12.6. Nothing collapses any more.
- **It does not make colour sufficient.** I searched about 6.6 million combinations near these hues: 12.6 is the ceiling. Five colours that must all be light enough to read on a near-black ground cannot be pulled further apart for a dichromat. Several pairs stay weak, and rose against violet gets slightly weaker for normal vision (19.3 → 16.4) as the price of fixing the red.

So the colours are the smaller half of the fix. The cue below is the half that works for everyone.

Because `--red` and `--green` are also "wrong" and "correct", those lift too. That helps: the red verdict text was failing 4.5:1 as well. Status never relies on colour (icon and word, 0.48 spec).

### The non-colour cue: the function letter

One cue everywhere, the letters the app already teaches: **T, PD, D, MD, C**. Picture: `fn_cue.png` (a bar grid in normal vision and the three simulations; the grid stays readable when the stripes do not).

| Where colour alone carries the function now | Change |
|---|---|
| Bar grids in the climbs (`.bar`, 3 px top stripe), about ten call sites | add `data-fn="…"` beside `style="--c:…"`; the letter sits bottom right, 11 px, weight 600, in the function colour |
| Analysis numeral strip (`.clrn span`) | same attribute; letter top right |
| Circle-of-fifths wheel nodes (stroke colour) | a small letter outside the node, upper right: `<text class="f">` |
| Ear Lab chord chips (`.el-ch`; the function is in the tooltip only) | the small line starts with the letter: "**D** bass s" |
| Analysis score numerals (fill colour) | no letter on the score (clutter); the Functions row beneath already lists the letters in order, and gets the legend line |
| Ear Lab numeral buttons (`.el-opt.num`) | nothing: they already carry the function word |
| Cadence coverage numerals (`.cov em`) | nothing: I, IV and V differ as text |

A legend line (`.fnkey`: "T tonic · PD pre-dominant · D dominant · MD modal dominant · C colour") goes once under any bar grid or numeral strip. The Ear Lab's `ELFN` should gain MD when C9 lands, so the Ear Lab and Analysis agree.

Regression test: add `cvd_sim.py --proposed --check` to `tests/run_all` once the tokens are in (then drop `--proposed`: the script reads the tokens from `index.html`).

---

# Deliverable 2 — the 0.49 ladder UI

Melody grows from 3 rungs to 12 (Stage 4: 1–4, Stage 5: 5–8, Stage 6: 9–12); rhythm from 3 to 10 (Stage 4: 1–3, Stage 5: 4–7, Stage 6: 8–10). The other five drills keep three rungs.

**Vocabulary.** "Rung" is the drill level and nothing else. The hand-sign rows stay "notes" on "the solfa ladder". New words in this design: "Stage band" does not appear in the UI (the bands are labelled "Stage 4"); the two parts of melody entry are "Rhythm" and "Solfa".

**Placeholder content.** The melodies, the rung descriptions ("four bars of 2/4, crotchets and quavers") and the count-in wording in the mock-ups are mine, to test the layout. The real ones come from the ladder register.

## 2.1 The rung picker

Mock-ups: `picker_states` (every state, four widths), and the head of every other mock-up.

**One pill per Stage.** Each band is a segmented pill in the style of the present rung control: a label cell ("STAGE 4", 11 px caps, on `--panel2`) and then the rung numerals. The word "Rung" is not repeated twelve times; it is said once, in the line beneath.

- Numerals 14 px, each button 40×34 (the present control is 34 high). Selected: gold fill, ink numeral, weight 600, as now. The label of the band you are in turns gold.
- **A rung you have reached 8 of the last 10 on** carries a 4 px dot under its numeral. It is a mark of where you have been, never a lock.
- **The suggested rung** carries a 1.5 px `--goldhi` ring. Still, not pulsing.
- The whole row is 746 px wide for melody (three 242 px bands and two 10 px gaps) and 666 for rhythm. The card is 796 px inside at 1440 and 1366 and 834 at 1024, so it is one row at every desktop width, with nothing changing between them.

**The rung line** sits under the picker, 12.5 px: "**Rung 6 of 12** · Stage 5 · four bars of 2/4, crotchets and quavers, do to la". With twelve rungs a number alone says too little; this line says what the rung is. It carries `data-notm` so the terms glosser leaves it alone (C2's first-mention rule is met by the question line).

**Last 10**, at the right end of the rung line: ten marks, 8 px. A filled gold disc is a right answer, a ring is an answered question that was not right, a short dash is not answered yet. Shape carries it, not colour. It makes the "8 of the last 10" rule visible before the suggestion ever appears, so the suggestion is never a surprise. `role="img"`, `aria-label="Last 9 answers on this rung: 7 right"`.

**Stage filter.** Bands above the Stage switch are not drawn. In their place is one dashed chip, "**8 more** · Stage 5–6", which sets `EAR.all` exactly as "show all rungs" does now. It replaces that link on these two drills, which also settles carried item S-5 (the link took a 54 px row of its own on phones). A rung in use always shows, with its band, even above the Stage (never strand a student). If the suggested rung is behind the chip, the chip takes the ring.

**Header layout** (`.el-head.long`): tag and title on the left, tally on the right, then the picker and the rung line across the full width.

| Header height | 1440 | 1366 | 1024 | 390 |
|---|---|---|---|---|
| 0.48, three rungs | 97 | 97 | 97 | 104 → 122 (122 after C5-1) |
| 0.49, long ladder | 126 | 126 | 126 | 188 (171 when the rung line fits two lines) |

The 29 px on desktop falls on melody and rhythm only, which already scroll at 1366×768; the fold rule (FR-16) covers metre, quality and cadences, which do not change.

**Phones.** Twelve 44 px buttons do not fit in 328 px. One band is open at a time; the others fold to a two-line tab ("Stage 4" over "1–4", 60×46). Tapping a tab opens that band in place. The band you are on is open when the card draws.

| At 390 | Size |
|---|---|
| Row | 328×46, one line, same height as the present control |
| Rung buttons, melody Stage 6 (4 open, 2 tabs) | 49×44 |
| Rung buttons, rhythm Stage 6 (3 open, 2 tabs) | 64×44 |
| Rung buttons, rhythm Stage 4 (3 open, chip) | 82×44 |
| Tab | 60×46 |
| "more" chip | 72×46, two lines |

No control in any phone mock-up is under 44 px in either direction. Any rung in your own band is one tap; any other rung is two.

**Behaviour.** Tabs are buttons with `aria-expanded`; rung buttons keep `data-earlv` and `aria-pressed`, with `aria-label="Rung 6, Stage 5"` (plus ", 8 of the last 10 reached" or ", suggested next"). Arrow keys move along the rungs across bands. Changing the Stage switch clears `EAR.all`, as now.

## 2.2 The suggestion

Mock-up: `suggest_rhy` (rhythm rung 3 answered right; rung 4 is the first Stage 5 rung, so it also shows the cross-Stage wording).

**When.** After an answer, if at least 8 of the last 10 answered questions on this rung were right (so it can first appear on the eighth answer), and there is a rung above. Shown and skipped questions do not enter the ten. Nearly counts as not right.

**Where.** Inside the result panel, as its last row, under a 1 px rule: a small ladder mark, then "**8 of your last 10 right.** Ready for rung 4?" (15 px) with one line beneath saying what the next rung adds (12.5 px, muted), then two buttons: **Try rung 4** (gold outline) and **Stay on rung 3** (plain). **Next →** stays where it is and stays the filled gold button: carrying on is always the main action. No dialog, no confetti, no sound. The panel announces it once (`role="status"`).

| | 1366 | 390 |
|---|---|---|
| Suggestion row | 762×55, one line | 302×133: text, then the two buttons side by side, 44 px each |

**In the picker** at the same moment: the rung gets its dot, the next rung (or its tab, or the chip) gets the ring.

**After it.** "Try rung 4" changes rung and starts a question there. "Stay" or "Next" closes the row. The ring stays on the next rung as a quiet standing invitation; the row itself does not come back until the count has dropped under 8 and climbed back. The dot, once earned, stays.

**Data.** `EAR.hist[drill][rung]`: the last ten results on that rung (1 right, 0 not), and `EAR.reached[drill]`: the rungs whose dot is earned. Saved with the rest of `cjg_ear`. The tally stays per drill, as now.

## 2.3 Melody entry with rhythm (melody rungs 4 and up)

Mock-ups: `mel_r6_rhythm` (step 1), `mel_r6_solfa` (step 2), `mel_r11_8bars` (eight bars).

**Two steps, in the order dictation is taught: rhythm first, then solfa under it.**

- A two-part switch (`.el-steps`): "**1 Rhythm** · 5 of 8 beats" and "**2 Solfa** · 7 of 12 notes". 52 px high at every width. Step 2 opens when the rhythm is full; the student can go back to step 1 at any time.
- **Step 1** is the rhythm drill's own entry, reused: the same named tiles ("ta", "ti-ti"), the same rule that a tile is disabled when it does not fit the bar, the same Undo, Redo and Clear.
- **Step 2** is the solfa ladder and hand signs exactly as they are now. Each tap fills the next note.
- **One score shows both.** A note with a rhythm but no pitch yet is a muted slash head on the middle line, with an empty slot beneath for its solfa. When its solfa is given it becomes a real note at its pitch, with the syllable beneath. The gold caret marks the next beat in step 1; the gold slot marks the next note in step 2. The given first note is drawn in the "given" colour as now.
- **Check** lights when the rhythm is full and every note has its solfa.
- Going back and changing the rhythm keeps the solfa already written, note for note from the start; any beyond the new number of notes is dropped (and Undo brings it back).

**Desktop.** The present desk is kept: 292 px on the left, the score on the right. The left column holds the step switch and then the tiles or the solfa ladder. The score is 442 px wide and breaks two bars to a system.

| Score at 1366 | Systems | Height |
|---|---|---|
| 2 bars | 1 | about 95 (not drawn) |
| 4 bars | 2 | 198 |
| 8 bars | 4 | 406 (the 9-note ladder beside it is 468) |

**Phones.** Top to bottom: the score, the step switch, the tiles or the ladder, the edit buttons.

- The score shows **one system at a time** (two bars; 294×91). Above it a bar map, one 44 px button per system ("1–2", "3–4", "5–6", "7–8"), with two small bars under each: grey when that bar's rhythm is written, gold when its solfa is written too. The view follows the entry; tapping a button looks back at another system. Entry is still append and undo, as now, so there is no cursor to move.
- The score block is **sticky under the top bar** while the entry is on screen (218 px with the bar map). The student sees the notes appear while tapping ladder rows far below it.
- With the score stuck, 462 px remain above the tab bar: the step switch and **all nine ladder rows (44 px each) are on screen at once** on a 390×844 phone. When the app's dock is showing it covers the last two rows; they scroll clear, as they do now.
- Two bars to a system holds for 2/4, 3/4 and 6/8. **A 4/4 bar with semiquavers needs a system to itself on a phone** (16 notes in 110 px is too tight to read); the bar map then has one button per bar, and above six buttons it scrolls sideways. This is the one thing the ladder register can make harder: eight bars of 4/4 with semiquavers would be eight single-bar views.

**Result.** Not mocked. Two labelled systems, "You wrote" and "The melody", as now. A wrong pitch is red in head and syllable; a wrong beat gets a 2 px red rule under the beat, so pitch and rhythm errors differ by shape as well. The headline reports the two parts separately ("Rhythm right · solfa 10 of 12").

## Decisions for Justin

Only the points where there is a real choice. My recommendation is first in each.

**D1. Function colours (C6).**
(a) Recommended: move green, red and rose as proposed, and add the function letter. Contrast passes everywhere, nothing collapses, and the letter works where colour cannot.
(b) Lift the red only (`#d15e5d`, the contrast failure) and add the letter; tonic and pre-dominant still collapse as colours, and the letter alone separates them.
Either way the letter goes in: no set of five colours on this ground is enough by itself.

**D2. `--red` and `--green` as "wrong" and "correct".**
(a) Recommended: let them lift with the function colours (one red, one green in the app; the red verdict text then passes 4.5:1).
(b) Split them into separate status tokens and leave status as it is.

**D3. Which drills get the banded picker.**
(a) Recommended: melody and rhythm only in 0.49. The five three-rung drills keep the present control, and nothing moves at the 1366×768 fold.
(b) All seven drills now, for one look across the room. Costs 29 px of header on each; metre at rung 2 has 9 px to spare at 1366×768 and would go below the fold.

**D4. The picker on phones.**
(a) Recommended: one band open, the others as tabs. One 46 px row; two taps to reach a rung in another band.
(b) All bands stacked, one row each. Every rung one tap away, but 140 px of header at Stage 6.

**D5. A suggestion that crosses a Stage** (rung 4 → 5 with the Stage switch on 4).
(a) Recommended: suggest it and say so ("Rung 5 starts Stage 5"). Progress is free choice and a student who has earned it should be offered it.
(b) Stop suggesting at the top rung of the chosen Stage; the chip is still there for anyone who wants more.

**D6. Order of melody entry at rungs 4 and up.**
(a) Recommended: rhythm first, then solfa, with free movement back. It is the order the method teaches, and it reuses both existing entries unchanged.
(b) Either order: solfa may be tapped first as a row of stemless notes and the rhythm added after. More freedom, more states to build and test, and the note count must be shown before the rhythm is known.

**D7. What counts as right at rungs 4 and up** (it feeds the 8 of 10).
(a) Recommended: right means rhythm and solfa both right; the headline reports the two separately so a student sees which half to work on.
(b) Add "Nearly" when one half is entirely right and the other has a single slip (streak kept, not counted as right).
This one is the engine's and the theory checker's to confirm; I raise it because the layout shows it.

## For the implementer

- Order: C5 and C6 first (three CSS files and the markup notes above), then the ladder.
- Reference markup: `mock.js` → `rp()` (picker), `last10()`, `head()` (the long header), `desk()` (steps, entry, score, bar map), `sug()`.
- The score in the mock-ups is drawn with VexFlow through `ENG`, like `earMelStave`: one stave per bar, clef and key at the start of each system, time signature at the first, slash heads (`duration + 's'`) for notes without a pitch. `mock.js` → `score()` is a sketch of it, not the engine.
- Tests to add: `layout_test` at the four sizes for the long header and the desk; `earlab_ui_test` section A for the new views (11 px floor, no sideways scroll, 44 px on phones, which should now count `.el-bandtab`, `.el-bandmore`, `.el-steps button`, `.el-sysmap button`); a unit test for the last-ten window and the suggestion rule.

## Not checked

- No real phone and no real colour-blind reader: the simulations are a model.
- The result state at rungs 4 and up is specified, not drawn.
- Compound time and 4/4 with semiquavers on phones are reasoned from the measured bar width (110 px), not drawn.
- C5-2 changes checkboxes in every room; I looked at Keys and the Ear Lab.

## Justin's answers, 21 Nov 2026 05:53 (decision log L101)
D1 (a) · D2 (a) · D3 (a) · D4 (a) · D5 (a) · D6: image previews of (a) and (b) requested (`entry_ab/`) · D7 (a). Note: the "8 of the last 10" window leaves Nearly out (ladder register D10 (a)), not "Nearly counts as not right" as in 2.2.

L103 (06:13): D6 = **option b, the duration palette** (`entry_ab/`), superseding 2.3's two-step entry. 18-rung picker for 0.50: mock a redesign and a sub-menu version.

L105 (06:27): 18-rung picker for 0.50 = **option A, one row, all rungs** (picker18/, branch 049-fable-picker18 @ 1e31ac9).
