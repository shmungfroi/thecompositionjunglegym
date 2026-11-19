# Ear Lab 0.48 — design spec

Branch `048-fable`, designed against the live 0.47 build. This is a spec and mock-ups, not production code.
Covers EL-1, EL-2, EL-3, EL-5, EL-8, EL-9, EL-10/11, EL-13, R4, R5. Kept from 0.47: the melody stave beside the hand-sign ladder, and the student's notes appearing while answering.

**How to use this folder**

| File | What it is |
|---|---|
| `assets/earlab048.css` | The new component CSS. **Lift it into `index.html` as written**; every size, colour and breakpoint below is taken from it. Where this document and the CSS disagree, the CSS wins. |
| `build.py` | Generates the mock-ups. Its Python functions (`play`, `stage`, `tally`, `head`, `metre_grid`, `rhy`, `tile`, `cell_marks`, `beats_svg`, `foot`) are the reference markup and the reference notation geometry. |
| `*.html` | Static mock-ups (open from disk). `png/` holds screenshots at 1440 and 390, plus 1366×768 and 1024 for the three answered states. |
| `assets/app.css`, `assets/frame.json`, `fonts/` | Copies of the 0.47 styles, frame markup and webfonts so the mock-ups render offline. Not for production. |
| `assets/glyphs.json` | Bravura outlines taken from VexFlow 4.2.3 (already loaded by the app), converted to SVG paths. |

Mock-ups: `metre_idle`, `metre_playing`, `metre_answered`, `rhythm_answering`, `rhythm_countin`, `rhythm_rung1`, `rhythm_checked`, `cadence_r3_answered`, `cadence_r3_nearly`, `tally`, `phone_dock` (390 only; there is no dock above 760 px).

---

## 1. Tokens

Existing variables only: `--ink --panel --panel2 --line --gold --goldhi --ivory --muted --red --green --violet --lush --pink`. Three additions:

| Token | Value | Use |
|---|---|---|
| `--r-s` | 8 px | tiles, chord chips, small insets |
| `--r-m` | 12 px | option buttons, stage/result panel |
| `--r-pill` | 999 px | buttons, segmented controls, toggle, dock |
| `--inset` | `#0e0c08` | the stage/result panel ground (already used by `.vrv`, `.tile`) |

That is the whole radius scale inside the Ear Lab (the card itself keeps the app-wide 14 px). Remove the 10 px and 16 px radii currently on `.earopt`, `.earres`, `.earslot`, `.earstep` (use `--r-m`, `--r-m`, `--r-s`, `--r-s`).

Type: Outfit 300 for text at 11 / 12.5 / 14 / 15 / 16 px only. Poiret One for the drill title (28 px; 24 px on phones), the answer headline (28 / 24 px), the score numeral (52 / 44 px) and the tip numerals (22 px). EB Garamond 500 for Roman numerals in chord chips (20 px). Nothing under 11 px.

Function colours: `FN[fnOf(ch,key)]` as elsewhere (T `--green`, PD `--gold`, D `--red`); any chord with a note outside the key (V7/V, V7/vi) `--violet`.

Status colours always travel with an icon and a word (section 10).

## 2. Layout by width

`#earMain` gets class `el`. Structure: drill strip, then `.el-cols` holding the drill card and the "Listening for it" card.

| Viewport | Content width | Columns | Notes |
|---|---|---|---|
| 1440 | `#earMain` capped at **1180 px**, left-aligned with the room head | drill card `minmax(0,1fr)` (842 px) + tips card **320 px**, gap 18 px | Card inner width 796 px. Tips stay beside the drill, visible while answering. |
| 1366×768 | same 1180 cap (1250 available) | same two columns | Play toggle, question and answer grid are all above the fold for metre, quality, cadences. |
| 1024 (and anything < 1180) | cap **880 px** | one column; tips card below the drill card | Drill strip fits without scrolling at 880. |
| ≤ 760 (390) | full width, `main` padding 14 px; Ear Lab card padding **16 px** (inner 330 px at 390) | one column | Phone rules in section 5. |

Vertical rhythm inside the card: header → 16 px → question line → 14 px → stage/result panel → 18 px → label → 8 px → answer area → 18 px → foot (1 px rule, 12 px padding above).

## 3. Drill strip, Stage switch, rungs (EL-10/11, EL-13)

**Drill strip** `.el-drills` replaces `.chips.eartabs`. One row at every width, `overflow-x:auto`, hidden scrollbar, 1 px `--line` rule beneath. Each `.el-drill` is two lines: name 14 px ivory, Stage tag 11 px muted, written out ("Stage 4–5", en dash). Min height 48 px. Selected: name `--goldhi`, tag `--gold`, 2 px underline in the app's `--lush`→`--pink` gradient (the same mark as the active rail item). `role="tablist"` / `role="tab"` / `aria-selected`. On selecting a drill, scroll its tab into view (`scrollIntoView({inline:'nearest'})`).

**Stage switch.** The top-bar Stage 4 / 5 / 6 switch filters the Ear Lab. A drill or rung shows when its minimum stage ≤ the selected stage:

| Drill | Tag | Rung 1 | Rung 2 | Rung 3 |
|---|---|---|---|---|
| Pulse and metre | Stage 4–5 | 4 | 4 | 5 |
| Rhythm dictation | Stage 4–5 | 4 | 4 | 5 |
| Chord quality | Stage 4–6 | 4 | 5 | 6 |
| Cadences | Stage 5–6 | 5 | 5 | 6 |
| Bass and numerals | Stage 5–6 | 5 | 5 | 6 |
| Melodic dictation | Stage 4–6 | 4 | 5 | 6 |
| Blind analysis | Stage 5–6 | 5 | 5 | 6 |

Hidden drills sit behind one text button at the end of the strip, `.el-all`: "3 more for Stage 5–6 · show all" (12.5 px muted, dotted underline). Hidden rungs sit behind "show all rungs" beside the rung control. Both set one flag, `EAR.all=true` (saved in `cjg_ear`), which shows everything; changing the Stage switch clears it. If the saved drill or rung is hidden under the current stage, show it anyway (never strand a student) and treat `EAR.all` as on.

**Rungs.** `.el-rungs`: a segmented pill like the top-bar `.lvl`. Buttons "Rung 1", "Rung 2", "Rung 3", 34 px high (44 px on phones, equal thirds of the card width), selected = gold fill, ink text, weight 600. `aria-pressed`.
Vocabulary rule: "rung" means the drill level and nothing else. The hand-sign rows are "notes" on "the solfa ladder" in all copy, tooltips and aria labels. Replace every student-facing "level" in the Ear Lab (EARHOW, tips, log lines, journal lines) with "rung".

## 4. Card header and tally (R5)

`.el-head` is a two-column grid. Left: Stage tag (`.el-tag`, 11 px gold caps), drill title (`.el-title`, Poiret One 28 px), rung control 12 px below. Right: the tally, spanning the header height.

**Tally** `.el-tally` (see `tally.html`):
- Score numeral: Poiret One **52 px** (44 px phones), `--goldhi`, line-height .86. Beside it, baseline-aligned, "of 15" in 14 px muted.
- 16 px to the right, behind a 1 px `--line` rule: two rows, "STREAK 3" and "BEST 6". Label 11 px caps muted, letter-spacing 1.5 px; value 14 px ivory, tabular numerals, right-aligned.
- Before any answer: numeral is an en dash in `--muted`, text "no answers yet", no streak/best block.
- `role="status"`, `aria-label="Score 11 of 15, streak 3, best 6"`.
- When the score goes up, the numeral cross-fades (opacity 0→1 over 180 ms); no bounce, no confetti. Skip the fade under `prefers-reduced-motion`.

The old `.earstat` line goes. **Foot** `.el-foot`: left, 12.5 px muted, "**15** answered · **2** shown · **1** skipped" (numbers ivory); right, "Reset score" and "Save to journal" (`.el-btn.sm`, 30 px; 44 px on phones, sharing the row equally).

**Reset, inline:** pressing "Reset score" swaps that button for `Reset the Cadences score? [Reset] [Keep it]` in the same place (no dialog; focus moves to "Keep it"; Esc = Keep it). After Reset the tally shows the empty state and the foot shows `Score reset. [Undo]`. Undo restores the previous counts exactly and stays available until the next answer, a drill/rung change, or leaving the room.

**Same tally elsewhere.** Keys room, interval gym: both modes ("Hear it · name it", "Sing it back") put the same `.el-tally` at the top right of their panel and drop the inline "Score: x / n" and "Sung in tune: x / n" text. Both gain `streak` and `best` (new fields on `KS.gym`, kept per mode, saved with the rest of the Keys state). No Reset is added there.

**Scoring model.** `EAR.st[drill] = {n, ok, streak, best, shown, skipped}`; missing fields read as 0 (old saves keep working).

| Event | n | ok | streak | Other | Log line ends |
|---|---|---|---|---|---|
| Correct | +1 | +1 | +1 (best updated) | | `correct` |
| Wrong | +1 | | 0 | | `missed` |
| Nearly (section 9.5) | +1 | | kept | | `nearly` |
| Show me | | | kept | shown +1 | `shown` |
| Skip (Next/Skip pressed, or drill/rung changed, with a question open and unanswered **after it has been played**) | | | kept | skipped +1 | `skipped` |

## 5. The sound stage (EL-1, EL-2)

One panel, `.el-stage`, directly under the question line: `--inset` ground, 1 px `--line`, radius 12, padding 12×14. Grid: toggle | state text | actions; a second row for variants.

### 5.1 The toggle `.el-play`

A circle, **48 px** (56 px on phones; 40 px inside a replay on desktop). One element, three states:

| State | Ground | Icon | Ring | Label beside it (15 px ivory / 12.5 px line below) |
|---|---|---|---|---|
| Ready | `--gold` (hover `--goldhi`) | play triangle, `--ink`, 38% of the diameter | hidden | "Play" / "Press play to hear the first one" before the first question; then "Play again" / "Ready · played once" ("twice", "3 times" …) |
| Playing | `#1b170f` | stop square, `--goldhi`, 30% | track 3 px `rgba(201,162,74,.28)`; arc 3 px `--goldhi`, round caps, sweeping clockwise from 12 o'clock over the **real duration** | "Stop" / "Playing · 0:04 of 0:11" in `--goldhi`, tabular numerals. Rhythm count-in: "Count-in · 3". |
| Loading (blind analysis, first use) | as Playing | stop square | quarter arc rotating, 1.1 s | "Loading the scores…" |

- One press starts. On a fresh card the press creates the first question and plays it.
- It returns to Ready by itself when the sound ends. Pressing it while playing stops.
- The ring is an SVG circle `r=22.5` in a 48 box, `pathLength="100"`, `stroke-dasharray:100`, animated `stroke-dashoffset 100→0` with `animation: elRing var(--dur) linear forwards`. To restart: remove `.playing`, force a reflow, set `--dur`, add `.playing`. The time text updates on a 250 ms interval.
- `aria-pressed`, `aria-label` "Play"/"Stop"; the state text is `aria-live="polite"` but only announces "Playing" and "Ready" (not every second).
- The Ear Lab's own "■ Stop" button is removed.

### 5.2 Variants (secondary, same state)

Row two of the stage, above a 1 px rule: caption "OR JUST" (11 px caps muted) then `.el-var` pills, 30 px (44 px phones), 12.5 px:
- Cadences: "Without the key chord"
- Bass: "Without the key chord", "Bass only"
- Melody: "Without the key chord", "First note"

They share the toggle's state: while a variant sounds, the main toggle shows Stop with the ring for that variant's duration, and the sounding pill takes a gold border, `--goldhi` text and a small square. Pressing the sounding pill, or the toggle, stops. Pressing another pill switches straight to it. Only one thing ever sounds.

Rhythm uses the same row for its listening options (section 7.5).

### 5.3 Actions

Right of the state text: `Show me` and `Skip →` (`.el-btn`, 34 px; on phones a full-width row of two 44 px buttons). Neither appears before the first question. After an answer the stage is replaced by the result panel (section 9), whose gold `Next →` sits in the same top-right corner.

### 5.4 What stops the sound

Answering (option press or Check), Next/Skip, Show me, changing rung, changing drill, leaving the room, Esc, and the toggle itself. After answering, the stage is gone and the replays in the result panel take over; each replay is the same `.el-play` component with the same shared state.

### 5.5 Phones (≤ 760 px)

- Toggle 56 px. Every Ear Lab target ≥ 44 px: drill tabs 48, rung buttons 44, variant pills and segmented buttons 44, `.el-btn` 44, option buttons ≥ 60, metre cells 100, rhythm tiles 64, Undo/Redo/Clear/Check 44, and the solfa ladder rows **44 px** (up from 24; the stave stays sticky above the ladder as in 0.47).
- **Docked toggle** `.el-dock`: when the stage (or, after answering, the result's first replay) is scrolled out of view and a question is open, a bar appears fixed above the tab bar: left/right 12 px, `bottom: calc(68px + env(safe-area-inset-bottom))`, height 64 px, pill radius, ground `rgba(22,19,13,.98)`, 1 px `rgba(201,162,74,.5)`, shadow `0 10px 28px rgba(0,0,0,.6)`, z-index 8. Contents: the 56 px toggle (same state, same ring), the drill name (15 px) over the state line (12.5 px), and one context button on the right (48 px high): `Check` in the builder drills while answering (disabled until full), `Next →` after answering, nothing otherwise. It slides up 8 px and fades in over 160 ms. While it shows, `body.ear-docked` adds 68 px to `main`'s bottom padding so nothing is trapped beneath it.
- Use an `IntersectionObserver` on the stage/first replay with `rootMargin: -<top bar> 0 -61px 0`.
- **Global Stop:** while the Ear Lab is sounding set `body.ear-sounding`; under 760 px `.tstop` is hidden (the toggle or the dock is the stop). On desktop the top-bar Stop stays.

## 6. Pulse and metre (EL-3)

Question line: "How many beats in a bar? Does each beat split in two or in three?"

**Before answering, progress is time only.** The ring and "Playing · 0:04 of 0:11". No beat flashes, no bar count, nothing that moves with the pulse.

**Answer grid** `.el-mgrid` (see `metre_*.html`): columns Duple / Triple / Quadruple with sub-labels "2 beats in a bar" etc.; rows Simple "each beat splits in two" and Compound "each beat splits in three". Column 1 (row labels) 150 px, three equal cell columns, gap 10 px. Each cell (`.el-opt.el-mcell`, min height 76 px) shows the time signature in Bravura numerals (26×44 px box) and a beat picture: one 4.6 px-radius dot per beat followed by 2.3 px dots for the rest of its split, gold. `aria-label="Compound duple, 6 8"`.
- Rung 1: the Simple row only (2/4, 3/4, 4/4); the row label stays.
- Rung 2: both rows.
- Rung 3: both rows plus a third row "Irregular · beats of unequal length" with 5/4 (picture grouped 3+2) and 7/8 (2+2+3). This needs `earMetreOpts(3)` widened to all eight (adds 2/4 and 12/8) so no cell in the grid is a dead answer.
- Phones: three equal columns, gap 8 px; each row label becomes a full-width line above its row; cells 100 px high with the signature above the picture.
- Before the first question the grid is visible at 55% opacity and disabled, so the student can see what will be asked.

**After answering:** the primary replay is "Hear it again with the beats shown". It plays the same four bars and lights `.el-beats`: per bar a thin barline, a dot per beat (strong 5.5 px, medium 4.2, weak 3.4 radius, gold), small muted dots for the splits, beat numbers beneath (11 px). The sounding beat gets a `--goldhi` fill and a 9.5 px halo ring. On phones four bars sit on one row up to 6 slots a bar, otherwise two bars a row. The lane is visible (unlit) as soon as the result appears. Secondary replay when wrong: "Hear 3/4 at the same speed" (the student's choice, same bpm, so the two can be compared).

## 7. Rhythm dictation (EL-5)

Question line: "Four clicks count you in, then the rhythm plays on one note. Write what you hear." (rung 1: "…then the rhythm is clapped.")

### 7.1 The one-line stave

Drawn as inline SVG by a new `earRhySVG(cells, opts)`; reference implementation `rhy()` and `cell_marks()` in `build.py`. It replaces the five-line VexFlow stave in `earRhyDraw`. Glyphs are Bravura outlines via `Vex.Flow.Glyph` (or the paths in `assets/glyphs.json`) at VexFlow point 33: notehead 10.1 × 8.6 px.

Geometry, in px, `u` = width of one semiquaver:

| Item | Value |
|---|---|
| SVG height | 88 |
| Beat ruler baseline | y 13 (numerals 1–4 over each beat, 11 px, muted) |
| Stem top / beam top | y 26; primary beam 4 px thick; secondary beam at y 32.5, 4 px |
| Stave line and notehead centre | y 60; line 1 px `#c9b98f` at 55% |
| Sound strip | y 76–82 |
| Left margin | 34 (time signature 4/4, stacked, centred on the line) |
| A note at semiquaver position `p` in a bar starting at `bx` | notehead left edge `bx + p·u + 6`; stem on the head's right edge, 1.3 px |
| Barline between bars | 16 px gap, thin line y 43–77 |
| Final barline | thin 1 px + thick 3.5 px, 2.5 px apart, y 43–77, always drawn at the end of the last bar |
| `u` | **18** on desktop (bar 288 px; two bars 638 px total). Phones: one bar per line, `u = 17`, and the SVG scales down with `max-width:100%` (never scrolls). |

Notation: crotchet, quaver pairs beamed, four semiquavers beamed with a double beam, mixed groups with a partial second beam, minim open head, dotted crotchet with dot at head-right + 3 px and 4.3 px above the line, lone quavers flagged, crotchet rest centred on the line. Ink `--ivory`.

**Rung 1 is stick notation:** no stave line and no noteheads on crotchets and quavers (a 1.6 px stem from y 26 to y 64.5; quaver pairs joined by the beam); the minim keeps its open head. Time signature, ruler, sound strip and final barline as normal. See `rhythm_rung1.html`.

### 7.2 Count-in

The beat ruler doubles as the visible count-in. During the four clicks the numerals over bar 1 light one by one: 12.5 px, weight 600, `--goldhi`, and the current one sits in an 18 px circle (`rgba(240,212,138,.16)` fill, 1 px `--goldhi`). The state line reads "Count-in · 3". When the rhythm starts they return to the quiet ruler. See `rhythm_countin.html`.

### 7.3 Sound strip

Under every written note, a solid bar from its start for its sounding length: x `start + 2.5`, width `d·u − 5`, height 6, radius 3, ivory at 80% (gold in the "It was" row). A rest is a dashed gap: a 1.5 px muted line, dash 2/5, round caps. While answering, beats not yet written show as empty dashed outlines on the strip, and a gold caret (1.5 px line with a small triangle above the stem tops) marks where the next tile will land.

### 7.4 Entry tiles

`.el-tiles`, label "ADD THE NEXT BEAT". Each `.el-tile` draws its cell in the same notation (stick notation at rung 1) on a faint line, **width = duration × 14 px** (one beat 56 px, two beats 112 px), height 64 px, radius 8, gap 8 px, wrapping. Nine tiles fit one row on desktop and three rows at 390. A tile that cannot go next (would cross the bar, or a two-beat tile off beats 1 or 3) is disabled at 32% opacity. `aria-label` and `title` carry the name ("dotted crotchet, quaver"). At rung 1 only, each tile carries its time name beneath (ta, ti-ti, ta-a; 11 px muted; tile height 76 px).
Below: Undo, Redo, Clear (`.el-btn.sm`), then Check (`.el-btn.gold`) at the right, disabled until the bar(s) are full.
Label above the stave: "YOUR RHYTHM · 5 OF 8 BEATS".

### 7.5 Listening options

In the stage's second row: "PULSE" `[On | Off]` and "SPEED" `[Steady · 72 | Normal · 100]` as `.el-seg` segmented pairs (`aria-pressed`; selected = `rgba(201,162,74,.16)` ground, `--goldhi` text), then a plain note "Sound: clap" (rung 1) or "Sound: tone" (rung 2 up; not a choice). Defaults: Pulse On, Speed Steady at rung 1 and Normal otherwise; both saved in `cjg_ear`. Changing either stops the sound and applies from the next play.

### 7.6 After Check

`rhythm_checked.html`. Inside the result panel, full width: two rows on one beat grid, "YOU WROTE" above "IT WAS" (labels 11 px caps; the second in gold), same `u`, same left margin, so every beat lines up vertically. In the "You wrote" row each ruler numeral carries a small tick (green) or cross (red); a wrong beat also gets a full-height `rgba(200,71,59,.13)` band, radius 6. The "It was" row has no ruler and a gold sound strip. On phones: bar 1 pair, then bar 2 pair, each bar on its own line.
A beat is wrong when its pattern of starts, holds and rests differs from the answer's for that beat.

## 8. Other answer areas (EL-13)

**Option buttons** `.el-opt` (chord quality, cadences, blind analysis): a fixed grid, never a wrapping row. 3 columns on desktop, 2 on phones, gap 10 / 8 px, min height 56 / 60 px, radius 12, 15 px label, left-aligned. Quality rung 1 (two options) uses `.c2`. Buttons keep their position after answering.

**Cadences rung 3 (R4):** six buttons in this order: Perfect, Plagal, Imperfect, Interrupted, Phrygian, Cadential 6/4 (the figures stacked, `.fig`). Rungs 1–2: the first four. Button labels are the Australian terms only. `title` on the three that differ: "US: authentic", "US: half", "US: deceptive". US terms appear in feedback in muted brackets at the first mention, e.g. "an imperfect cadence (US: half)". `CADL` becomes the Australian names only, with a separate `CADUS` map.

**Bass and numerals:** four slots in a row (56 × 56 px, radius 8, EB Garamond 20 px numerals in function colours; the first is the given I; the current slot has a gold border). Below, the numeral options as a fixed grid of the same chips: 4 columns desktop, 4 on phones (≥ 68 × 48 px), each numeral in its function colour with its function beneath in 11 px muted ("tonic", "pre-dominant", "dominant", "outside the key"). After Check each slot shows a tick or cross and, where wrong, the right numeral beneath.

**Melody:** as built in 0.47. Changes: ladder rows 44 px on phones; the result strip uses the result panel of section 9 in the `melres` area (beside the ladder, under the stave); copy says "notes", never "rungs".

**Instructions.** One sentence above the stage (`.el-ask`, 16 px, max 60 characters wide); everything else moves to "Listening for it".

| Drill | Question line |
|---|---|
| Pulse and metre | How many beats in a bar? Does each beat split in two or in three? |
| Rhythm dictation | Four clicks count you in, then the rhythm plays on one note. Write what you hear. |
| Chord quality | One chord: together, then note by note, then together. What kind of chord is it? |
| Cadences | The key chord plays first, then a short phrase. How does the phrase end? |
| Bass and numerals | The key chord plays first. Chord 1 is always I. Name chords 2 to 4. |
| Melodic dictation | The key chord plays first and the first note is given. Write the rest in solfa. |
| Blind analysis | A phrase from a real score, with the score hidden. Name the cadence at the end. |

**"Listening for it"** becomes a numbered list, `.el-tips` (Poiret One numerals in gold, lead phrase in `--goldhi`, 14 px), with one muted 12.5 px note beneath. Copy for metre, rhythm and cadences is in `build.py` (`METRE_TIPS`, `RHY_TIPS`, `CAD_TIPS`). The other four take the existing `EARHOW` + `earTips` text, cut into three or four steps in the same pattern (lead phrase, one sentence). Keep the KMEIA credit and the blind-analysis provenance sentence as the muted note.

## 9. Feedback that teaches (EL-8)

### 9.1 The result panel

`.el-result` takes the stage's place the moment an answer is given (same box, same position, so nothing jumps and the result sits above the answer area). Parts:
1. Mark: a 32 px ring with a tick, cross, wave or eye (16 px icon).
2. Verdict, 11 px caps: "CORRECT" (`--green`), "NOT THIS TIME" (`--red`), "NEARLY" (`--gold`), "SHOWN" (`--gold`).
3. **Headline = the answer**, Poiret One 28 px ivory, with a small muted qualifier where useful ("Compound duple 6/8"; "Minor · on E♭, first inversion").
4. One teaching sentence or two short ones, 15 px, max 58 characters wide: first what the student heard correctly, then what to listen for, relating their choice to the answer.
5. Supporting picture where there is one (chord row, beat lane, You wrote / It was).
6. Replays: the first is an `.el-play` toggle with its label in `--goldhi` and is the one that demonstrates the sentence; others are `.el-btn` pills.
7. `Next →` (`.el-btn.gold`) top right; on phones full width at the foot of the panel. Focus moves to it after answering, so Enter carries on.

Panel border and a faint top wash take the verdict colour (green 50%, red 55%, gold 55% alpha). `role="status"`.

The option buttons stay where they are: the answer gets a green border, a faint green ground and a "✓ ANSWER" badge; a wrong choice gets red and "✕ YOUR ANSWER"; a right choice shows "✓ YOUR ANSWER"; a "nearly" choice gets gold and "≈ YOUR ANSWER"; the rest drop to 60% opacity.

**Chord row** (cadences, bass, blind): `.el-chords`, one `.el-ch` chip per chord, numeral in its function colour, an 11 px note beneath ("tonic", or "bass fa"), the cadence chords joined by a gold rule labelled "THE CADENCE", then "in D minor".

Voice for all templates: plain, second person, Australian terms, no exclamation marks, no "Great job". Minor keys use la-based solfa (home note la; the Phrygian bass is fa to mi).

### 9.2 Pulse and metre

Headline: `{Simple|Compound} {duple|triple|quadruple}` + small `{n/d}`. Let B = beats, S = split (two/three).

| Case | Sentence |
|---|---|
| Correct | "{B} beats in a bar, each one splitting in {S}." |
| 3/4 ↔ 6/8 | "You heard six quavers in every bar, and that is right. In {given} they fall in {twos, making three beats / threes, making two beats}. Here they fall in {…}, so there are {only two / three} beats in a bar." |
| 2/4 ↔ 4/4 | "You heard the beats split in two, and that is right. Here the heaviest click comes back every {B} beats{4/4: , with a lighter one on beat 3}." |
| Split right, count wrong | "You heard each beat split in {S}, and that is right. Now count from one heavy click to the next: {B} beats, not {given B}." |
| Count right, split wrong | "You counted {B} beats in a bar, and that is right. Now listen inside one beat: it splits in {S}, not {given S}, so this is {simple/compound}." |
| Both wrong | "Start with the heavy click: it comes back every {B} beats. Then listen inside one beat: it splits in {S}." |
| Irregular (answer) | "The beats are not all the same length. Count the quick notes: {3+2 / 2+2+3}." |
| Shown | the "Both wrong" sentence |

Replays: **"Hear it again with the beats shown"**; when wrong, "Hear {given} at the same speed".

### 9.3 Rhythm dictation

Headline: correct "Every beat right"; otherwise "{m} of {N} beats match". Words for each cell: crotchet "one sound"; 2 quavers "two even sounds"; 4 semiquavers "four even sounds"; minim "one sound held for two beats"; crotchet rest "a beat of silence"; dotted crotchet, quaver "long-short across two beats"; quaver, 2 semiquavers "long-short-short"; 2 semiquavers, quaver "short-short-long"; quaver, crotchet, quaver "short-long-short across two beats".

| Case | Sentence |
|---|---|
| Correct | "Every beat right{, including the dotted rhythm / the syncopation / the rest}. Tap it once more as you listen." |
| One or more beats wrong | "{Bar x is exactly right. / m of N beats match.} In {bar y,} beat k, you wrote {given cell} ({given words}). Listen for {answer words} there: {answer cell}." Only the first wrong beat is described; the picture shows the rest. |
| Shown | "Follow the notes as it plays, then tap it back." |

Replays: **"Hear {bar y,} beat k: yours, then the answer"** (the student's beat, a beat of silence, the right beat, at Steady speed, with the pulse); "Hear it all, following the notes" (a gold caret travels the "It was" row).

### 9.4 Chord quality

Headline: `{quality}` + small "on {root}, {inversion}".

| Given ↔ answer | Sentence (the brace picks the answer's side) |
|---|---|
| Correct | "{Major 3rd / Minor 3rd}, {perfect / diminished / augmented} 5th{, and a … 7th}." |
| Major ↔ minor | "Both have a perfect 5th, so either way the chord sounds settled. The difference is the 3rd: here it is {major, the brighter one / minor, the darker one}." |
| Minor ↔ diminished | "You heard the minor 3rd, and that is right. Now the 5th: {it is squeezed down a semitone, which makes the chord tense / it is perfect, so the chord is settled}." |
| Major ↔ augmented | "You heard the major 3rd, and that is right. Now the 5th: {it is stretched up a semitone, so the chord hangs unresolved / it is perfect, so the chord is settled}." |
| Major 7th ↔ dominant 7th | "You heard a major triad underneath, and that is right. The 7th on top is {a semitone under the octave: major 7th / a tone under the octave, and it wants to move on: dominant 7th}." |
| Dominant 7th ↔ minor 7th | "You heard the 7th a tone under the octave, and that is right. Underneath, the 3rd is {major / minor}." |
| Minor 7th ↔ half-diminished | "Minor 3rd and minor 7th: right. The 5th is {perfect / diminished, which darkens it}." |
| Half-diminished ↔ diminished 7th | "You heard the diminished triad, and that is right. The 7th is {a minor 7th / a diminished 7th: every note a minor 3rd from the next}." |
| Any other pair | "Take it from the bottom: the 3rd is {…}, the 5th is {…}{, the 7th is {…}}." |

Replays: **"Hear the {3rd / 5th / 7th}, then the chord"** (root plus the interval that decides it, then the full chord in root position, then as asked); "Hear {given}, then {answer}, on {root}".

### 9.5 Cadences (rungs 1–3) and blind analysis

Headline: `{name} cadence`, or "Cadential 6/4" (figures stacked). Below the sentence, the chord row. US term in muted brackets after the first mention of perfect, imperfect or interrupted.

Correct:

| Answer | Sentence |
|---|---|
| Perfect | "V to I: the leading note rises to the home note and the bass lands there. A full stop." |
| Plagal | "IV to I. No leading note; the home note is held through both chords. The Amen." |
| Imperfect | "It stops on V and waits there. A comma, not a full stop." |
| Interrupted | "V sets up the close, then the bass steps up to vi instead of falling home." |
| Phrygian | "iv⁶ to V in a minor key: the bass falls a semitone, fa to mi, and the phrase stops on V." |
| Cadential 6/4 | "The bass reaches the dominant early and holds it: I⁶₄, then V, then home. A perfect cadence with a delay built in." |

Wrong (given → answer):

| Given → answer | Sentence |
|---|---|
| Plagal → perfect | "You heard it come home to I, and that is right. Listen to the chord before: it is V, with the leading note pulling up to the home note. A plagal cadence has IV there." |
| Perfect → plagal | "You heard it come home to I, and that is right. Listen to the chord before: it is IV. There is no leading note, and the home note is held through both chords." |
| Perfect → interrupted | "You heard V set up a close, and that is right. But the bass steps up to vi instead of falling home, so the close never arrives." |
| Interrupted → perfect | "You heard V set up a close, and that is right. This time it arrives: the bass falls to the home note." |
| Perfect → imperfect | "You heard V, and that is right. But V is the last chord. The phrase stops there and I never comes." |
| Imperfect → perfect | "You heard V, and that is right. But it is not the last chord: it goes on to I and closes." |
| Imperfect ↔ interrupted | "You heard that it does not close on I, and that is right. {V is not the last chord: it moves on, up a step to vi. / The last chord is V itself; nothing follows it.}" |
| Plagal → imperfect | "You heard IV near the end, and that is right. But the last chord is V, not I, so the phrase is left open." |
| Imperfect → plagal | "You heard IV near the end, and that is right. It moves to I, not V: the phrase comes home." |
| Plagal → Phrygian | "You heard the subdominant, and it is there: iv is the chord before the end. But the phrase does not come home to i. It stops on V, with the bass stepping down a semitone, fa to mi. That falling semitone is the Phrygian cadence, a kind of imperfect cadence (US: half)." |
| Perfect or interrupted → Phrygian | "The phrase does not close: it stops on V. In the bass, fa falls a semitone to mi. That is the Phrygian cadence, a kind of imperfect cadence (US: half)." |
| Anything but perfect → cadential 6/4 | "Follow the bass: it reaches the dominant and holds it for two chords, I⁶₄ then V, before falling home to I." |
| Phrygian or cadential 6/4 → one of the four | Use the row for the plain cadence the student's choice belongs to (Phrygian as imperfect, cadential 6/4 as perfect), then add: "There is no {semitone fall in the bass / held dominant bass} here." |
| Any other pair | "Start with the last chord: here it is {I / V / vi}. Then the chord before it: {V / IV}." |

**Nearly** (rung 3 only; gold, streak kept, not added to the score):

| Given → answer | Sentence |
|---|---|
| Imperfect → Phrygian | "You heard it stop on V, and that is right: this is an imperfect cadence (US: half). It is the special kind. In a minor key the bass steps down a semitone, fa to mi (iv⁶ to V), and that is called a Phrygian cadence." |
| Perfect → cadential 6/4 | "You heard V to I close the phrase, and that is right. Listen just before V: the bass is already on the dominant, with the tonic chord sitting on top of it (I⁶₄). That delay is the cadential 6/4." |
| Phrygian → imperfect | "You heard it stop on V, and that is right. But the bass does not fall a semitone into V here, so it is a plain imperfect cadence (US: half)." |
| Cadential 6/4 → perfect | "You heard V to I, and that is right. Here V arrives directly: there is no I⁶₄ held over the dominant bass before it." |

Replays: **"Hear the last two chords, slowly"** (three for a cadential 6/4: "Hear the last three chords, slowly"); "Bass only"; "The whole phrase".

Blind analysis uses the same sentences and adds, under the chord labels, "From {title}, bar {n}" and an `.el-btn` "Open this score in Analysis". Its replays are "Hear the ending again" (the last two chords' worth of the excerpt) and "The whole phrase".

### 9.6 Bass and numerals

Headline: the four numerals in function colours, "I – IV – V – I", small "in G major". Bass solfa under each chip.

| Case | Sentence |
|---|---|
| Correct | "All three right. The bass spells it out: {do – fa – so – do}." |
| Wrong, same function (ii ↔ IV; vi ↔ I) | "Chord k: you wrote {given}; it is {answer}. Both do the same job here ({pre-dominant: they lead to V / tonic: a place of rest}), so you heard its role. The bass tells them apart: it is on {re}, not {fa}." |
| Wrong, different function | "Chord k: you wrote {given}; it is {answer}. Sing the bass: it {rises / falls} to {so}, the root of {answer}." |
| Answer is a secondary dominant | "Chord k has a note from outside the key, {fi}, leaning into the next chord. It is {V7/V}, the dominant of {V}." |
| Two or three wrong | Describe the first as above and add "Chord {m} is marked below." |

Replays: **"Bass only, with the solfa shown"** (each chip lights as its note sounds); "Hear chords {k−1} and {k}".

### 9.7 Melodic dictation

Headline: the answer in solfa, spaced ("d r m s m"). The stave shows both lines as in 0.47.

| Case | Sentence |
|---|---|
| Correct | "Every note right. Sing it once more with the hand signs." |
| Shape right (every rise, fall and repeat matches), pitch wrong | "You heard the shape: every rise and fall is right. Between notes {k−1} and {k} the melody {skips from m to s / steps from m to f}; you wrote {a step, m to f / a skip, m to s}." |
| Shape wrong | "Notes 1 to {k−1} are right. From note {k−1} the melody {goes up / goes down / stays on the same note}; you wrote it {…}." |
| Shown | "Sing it back with the hand signs, then try the next one." |

Replays: **"Hear notes {k−1} to {k+1}: yours, then the answer"**; "Hear it all with the hand signs" (the 0.47 follow highlight).

## 10. Accessibility (EL-9)

- No state is colour-only. Correct = green + tick + "Answer"/"Correct"; wrong = red + cross + "Your answer"/"Not this time"; nearly = gold + wave + "Nearly"; shown = gold + eye + "Shown". Rhythm beats carry a tick or cross beside each beat number as well as the red band. The sounding variant has a square as well as a gold border. Function-coloured numerals always carry the function name beneath or in `title`.
- Focus: every control shows `2px solid var(--goldhi)`; offset 2 px for buttons, tiles and options, 3 px for the round toggle, −2 px (inside) for strip tabs and segmented buttons so the pill's clipping never hides it. Listed at the foot of `earlab048.css`.
- Keyboard order: drill tabs → rungs → toggle → variants → Show me → Skip → answer area → foot. After answering, focus goes to `Next →`. Reset confirmation takes focus; Esc cancels it.
- `aria-pressed` on the toggle, rungs and segmented buttons; `role="status"` on the tally and result; SVG notation has `role="img"` and a spoken label ("You wrote: 2 quavers, crotchet, …").
- Text contrast: muted `#9c927c` on the panel is 6.3:1; it is not used below 11 px. Disabled controls are exempt but stay ≥ 32% opacity so the notation on a disabled tile is still readable.
- Motion: the ring is information and keeps running under `prefers-reduced-motion`; the loading spin, the tally fade and the dock slide are switched off.

## 11. Engine hooks needed

1. **Playback state with duration.** `earPlay(what)` must work out `dur`, the time from start to the end of the last scheduled sound, and set `EAR.play={on:true, what, t0, dur}`; a single timer (in `PLAY.timers`) at `dur + 0.15 s` calls `earPlayEnd()`. This replaces the fixed 20 s timeout. `earPlayEnd()` clears the state and calls `earPlaySync()`, which updates every `.el-play`, the state line, the sounding variant, the dock and `body.ear-sounding` **without re-rendering the card** (a re-render would restart the ring and drop focus). `earPlay` also counts plays per question for "played twice".
2. **Stop notification.** `stopAll()` must call `earPlayEnd()` when `PLAY.src==='ear'`, so Esc, the global Stop and room changes return the toggle to Ready.
3. **Phase marker for the rhythm count-in**: `EAR.play.countin = {t0, beat}` so the ruler and the state line can show "Count-in · n".
4. **Rhythm tempo, pulse and timbre**: beat length 60/72 s or 60/100 s; pulse clicks optional; rung 1 uses a clap (a short filtered noise burst), rung 2 up the existing tone.
5. **New replays**: metre with a beat callback (and a fixed metre at the question's bpm for "Hear 3/4 at the same speed"); rhythm one-beat A/B; quality interval-then-chord and given-then-answer on the same root; cadence last two/three chords at 1.6 s spacing and bass only; bass with a per-chord callback; melody fragment A/B.
6. **Per-beat rhythm comparison**: `earRhyBeats(cells)` returning one key per beat (starts, holds, rests), for the ticks and for the feedback sentence. Overall right/wrong stays as now (`rhyOnsets`).
7. **Cadence rung 3 answers**: `q.a` becomes `phrygian` or `cad64` when `cadSub` says so. The two "interrupted after a cadential 6/4" models (`I IV I:2 V vi`, `i VI i:2 V VI`) need a decision, because both "interrupted" and "cadential 6/4" would be defensible answers; this spec assumes they leave the rung 3 pool. Phrygian only exists in minor and cadential 6/4 has no four-chord model, so the generator must be checked so that mode and length still do not give the answer away. This is theory content and should go through the independent check.
8. **Metre rung 3 pool** widened to all eight metres.
9. **Scoring**: the fields and rules in section 4; Reset keeps one undo copy in memory.
10. **Stage filter**: read the top-bar stage, the table in section 3, and `EAR.all`.
11. **Dock**: one `IntersectionObserver`, torn down on leaving the room.
12. **Tests to update**: `earlab_test.py`, `earlab_r2_test.py`, `layout_test.py` and `transport_test.py` select `.earopt`, `[data-earstop]`, "Level n" and `.earstat`. Keep the `data-ear*` attributes on the new elements (`data-earplay`, `data-earans`, `data-earlv`, `data-eardr`, `data-earnew`, `data-earshow`, `data-earcell`, `data-earchk`) so the handlers and most selectors survive.

## 12. Open questions for Justin

1. **"Nearly" at cadences rung 3.** Choosing Imperfect for a Phrygian cadence (or Perfect for a cadential 6/4) is true but not precise. I have made it a third result, "Nearly": gold, streak kept, not added to the score (`cadence_r3_nearly`). Alternatives: count it right, or count it wrong. Your call.
2. **Cadential 6/4 as an answer.** It is a decoration, not a cadence type, and two rung 3 phrases end interrupted after a 6/4. I have assumed those two leave the pool so there is always exactly one right button. Confirm, or keep them and accept "Interrupted" as the answer.
3. **Stage per rung** (table in section 3) is my reading; rung 3 of Pulse and metre (5/4, 7/8) is tagged Stage 5, so the drill's tag becomes "Stage 4–5". Rung 3 metre also gains 2/4 and 12/8 so the grid has no dead cells.
4. **Time names on tiles** (ta, ti-ti, ta-a) are shown at rung 1 only. Say if you want your preferred names at rungs 2–3 as well (tika-tika, tam-ti, syn-co-pa …), and which set.
5. **Solfa ladder on phones at 44 px rows** makes the rung 2–3 ladder about 400 px tall (it was 220). The stave stays pinned above it. The alternative is to exempt the ladder from the 44 px rule.
