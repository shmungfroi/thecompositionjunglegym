# Ear Lab 0.49 — ladder UI, part 2 (Fable)

Branch `049-fable-ladderui`, designed against 049 at 7b0b947. Specs, CSS and mock-ups only; `index.html` is not edited. Sonnet implements, I verify afterwards.

This document carries Justin's decisions of 21 Nov (L101 to L104) into a build spec. It **replaces** `DESIGN_049.md` section 2.3 (the two-step entry) and fills the gaps that document left (the result at rungs 4 and up, compound time, the seven-cell palette). Sections 2.1 and 2.2 of `DESIGN_049.md` (picker, suggestion, last 10) stand, with one correction in section 7 below.

Everything was built from the live app in headless Chrome at 1366×768 and 390×844 and measured there. No real phone was used.

## What is in this folder

| File | What it is |
|---|---|
| `ladder_ui.css` | **Lift into `index.html` as written**, after `ladder049.css`. Its header says which rules of `ladder049.css` it replaces. Where this document and the CSS disagree, the CSS wins. |
| `ladder_ui.js` | Mock-only, but its functions write the **reference markup**: `palHTML` (palette), `ladHTML` (ladder with half rungs, the gauge, the ladder after a mutation), `deskLen` (entry desk), `deskRes` (reveal desk), `resultHTML`, `markKey`, `gapHTML`, `mutHTML`, `setting`, `tile`, `rhyBar`, `rhyDesk`. `score` and `cellMarks` are the drawing rules in code (beaming, the gold marker, the marks at the reveal, tuplets). Line 4 holds three Bravura outlines to add to `ELGLY`. |
| `scenes.js` | The eight scenes, with their placeholder melodies. |
| `build_ui.py` | Builds and measures every scene: `python3 tests/reports/fable_049/ladder_ui/build_ui.py [scene ...]`. |
| `mocks/*.html` | Static mock-ups (no scripts; open from disk) at 1366 and 390. |
| `png/` | `*_1366.png`, `*_390.png` (the screen), `*_card.png` (the whole card), `*_390_entry.png` (phone, scrolled so the score and palette are held), `*_390_result.png`. `png/metrics.json` holds every measurement. |

| Scene | Shows |
|---|---|
| `pal_r6_24` | Palette entry, rung 6, 2/4: seven notes written, the marker inside a beat |
| `pal_r6_68` | Palette entry, rung 6, 6/8 with a quaver upbeat |
| `res_r6` | The reveal at rung 6: one rhythm slip, one wrong note |
| `a2_r7` | Rung 7 feedback for the augmented 2nd, fa to si |
| `mut_r9` | Rung 9 under "Move do (mutation)", after the pivot |
| `rhy_r9` | Rhythm rung 9: 5/4, a septuplet on the stave, the tuplet tiles, the names setting |
| `pal7_r12` | The seven-cell palette (six lengths and the crotchet rest) |
| `lad_chr` | The chromatic ladders of rungs 7, 8 and 10 |

**Placeholder content.** Every melody, rhythm, rung description and feedback sentence in the mock-ups is mine, to test the layout. The real ones come from the ladder register's generators and from Content. The five strings Justin fixed are used exactly: "Keep home do", "Move do (mutation)", "Mutation here: so = do", "Mutation at the G: so became do, and F♯ is the new ti", "Mutation: renaming the notes so the new key's home becomes do."

---

## 1. Melody entry from rung 4: the duration palette

Mock-ups: `pal_r6_24`, `pal_r6_68`, `pal7_r12`, `mut_r9`.

Choose a length; it stays chosen. Each tap on the solfa ladder writes one note of that length at the gold marker. One screen, one pass.

### 1.1 Which lengths appear

The palette is **derived, never typed per item**: it is the set of note values in the rung's rhythm cells for the metre family of the question (simple or compound), shortest first, then the rests. A value no bar of this metre can hold is left out (the metre is on screen, so this tells nothing). The palette therefore never changes with the item's content.

| Rung | Metres | Simple time | Compound time (6/8) |
|---|---|---|---|
| 4, 5 | 2/4, 4/4 | quaver, crotchet, minim | none |
| 6, 7, 8 | 2/4, 3/4, 4/4, 6/8 | quaver, crotchet, minim; in 3/4 also the dotted minim | quaver, crotchet, dotted crotchet, dotted minim |
| 9 | as rung 6, 8 bars | adds the dotted crotchet (tam-ti) | as rung 6 |
| 10 | as rung 6, 8 bars | as the register's cell table for rung 10 gives (it says "a rung 6 line", so the dotted crotchet goes again unless the engine keeps tam-ti) | as rung 6 |
| 11 | 3/4, 4/4 | melody part: as rung 10. Bass part: one length (minim in 4/4, dotted minim in 3/4), shown chosen | none |
| 12 | per excerpt | the curated set's values; the largest set that fits one row is the seven drawn in `pal7_r12`: semiquaver, quaver, crotchet, dotted crotchet, minim, dotted minim, crotchet rest | the same rule |

Rests appear only where the rung's cells have them: in the melody ladder that is rung 12 alone. The semibreve is not in any melody rung's cells; its glyph is in `lenGlyph` in case rung 12 needs it.

More than seven cells (possible at rung 12 only, for example with a dotted quaver and a quaver rest): the palette breaks into two rows (`.el-pal.two`). **Open point O3**: this needs the curated rung 12 list before it can be settled.

No time names sit on the palette (Justin's decision: pattern names appear at the reveal). Each cell is the note itself; its name in words ("dotted crotchet") is the `aria-label` and the tooltip.

### 1.2 Which lengths are live

A length is live when the bar so far, plus that length, is still **the start of a bar the rung could have written**. In code: for each rung and metre, list every legal bar as a string of lengths (the rung's cells under the register's fill rules RF, including a short first bar for an upbeat and the shortened last bar); a length is live if the student's bar so far with that length added is a prefix of one of them. One function, `earLenLive(rung, sig, barSoFar, len)`, tested for every rung and metre.

Worked cases (all follow from the rule):

| Where the marker is | Live | Dimmed, and what its label says |
|---|---|---|
| 2/4, rung 6, after one quaver | quaver | crotchet "cannot start inside a beat"; minim "does not fit this bar" |
| 6/8, rung 6, on beat 2 | quaver, crotchet, dotted crotchet | dotted minim "fills a whole bar: only from beat 1" |
| 6/8, after a crotchet inside a beat | quaver | the rest |
| 3/4, after a minim on beat 1 | quaver, crotchet | minim, dotted minim |
| 2/4, rung 9, on beat 2 | quaver, crotchet | dotted crotchet "starts on beat 1"; minim |
| an upbeat bar of one quaver | quaver | the rest |

A dimmed cell (`aria-disabled="true"`, glyph at 30%) stays focusable so its label can say why. Tapping it does nothing.

**The chosen length is always live.** If, after a note is written, the chosen length is no longer live at the marker, the choice moves to the longest live length shorter than it (or, if there is none, the shortest live length). The move is announced once through `earLiveSay` ("Length: crotchet. A minim does not fit here."). When a question is drawn the chosen length is the given first note's length, under the same rule.

This does narrow the choice at some points (after a lone quaver only a quaver is live). It is the same help the rhythm tiles give, where one tile writes both quavers.

### 1.3 On the stave

- **Given.** Clef, key signature, time signature, the bar outline (every bar drawn empty, an upbeat bar drawn short and the last bar short by the same length), and the first note with its length, in the "given" colour.
- **Spacing is in proportion to time**: a note sits at `bar start + tick / bar length`. Bars get width in proportion to their length (an upbeat bar no less than a fifth of a full bar). This keeps the empty part of a bar honest, and at the reveal it lines the two staves up beat for beat.
- **The gold marker** shows where the next note goes: a 2 px gold line through the stave with a small cap above it, at the next free tick. It is the rhythm drill's cursor, so the two drills share one sign. At a full bar it moves to the start of the next; when every bar is full it goes and Check lights.
- **Beaming is automatic**, redone at every entry. Simple time: quavers and semiquavers inside one crotchet beat join. 6/8: inside one dotted-crotchet beat. A note that is alone in its beat so far keeps its flag and gains its beam when its partner arrives. Nothing beams across a beat, a rest or a barline.
- **Solfa** under each note as now. Accidentals follow the key signature and the bar.
- **The label** above the stave is the position (`role="status"`): "Upbeat", "Bar 2 of 4 · beat 2", "Bar 3 of 4 · in beat 1" (the marker is inside a beat). It replaces "k of N notes": the note count is not given from rung 4 (rule MU1).
- Two bars to a system at both widths. A 4/4 bar with semiquavers takes a system to itself on phones (as `DESIGN_049.md` 2.3 said; not drawn).

### 1.4 Rests and the upbeat

- A rest cell is a **key, not a choice**: one tap writes that rest at the marker and the chosen length stays as it was. Rest cells come last, behind a double rule. They dim by the same rule as lengths.
- The upbeat is shown, not found (register D9). Bars are numbered from the first full bar; the first system's tag reads "upbeat · bar 1". The count-in is one full bar, then the upbeat on its own beat.

### 1.5 Undo, Redo, Clear, Check

- One step is one tap that wrote something: a note, a rest, or the mutation (section 4). Choosing a length is not a step.
- **Undo** takes the last step back and returns the marker; if the chosen length is not live there, the rule in 1.2 applies. **Redo** as now. **Clear** goes back to the given first note and is itself one step. **Check** lights when every bar is full.
- Entry is still append and undo: mending a slip in bar 1 from bar 3 means undoing back to it. That is the known cost of this option.
- Keyboard: the palette is a radio group (arrow keys move and choose). Digits 1 to 7 choose the nth cell where those keys are free; Backspace and Ctrl+Z undo.

### 1.6 Layout

**Desktop** (the present desk: 292 px left, the score right). Left column: a "Length" label, the palette (58 px high), then the ladder. Right column: the position label, the score, the edit row.

| At 1366 | Size |
|---|---|
| Palette | 292×58 |
| Cells, 3 / 4 / 7 in the palette | 97×56 / 73×56 / 40×56 (the rest cell 50) |
| Score, 4 bars | 442×203, two systems |
| Score, 8 bars | 442×419, four systems |
| Card, rung 6 entry | 842×1097 |

**Phones.** The score and the palette are **one block held under the top bar** (`.melhold`: `display:contents` on desktop, a sticky block on phones, so no script has to measure anything). Inside it, top to bottom:

1. the position label;
2. one row: the bar map (one 44 px button per system) and a **one-tap Undo** (44×44). Redo, Clear and Check stay at the foot of the desk, and Check in the play bar, as now. With a single system (the two-bar rungs 4 and 5) there is no bar map, and the label and Undo share one line;
3. the stave, one system, **drawn bare** (no inset frame: the held block is its frame). That gives the stave 328 px instead of 294 and takes 32 px off the block's height;
4. the palette, 50 px high.

| At 390 | Size |
|---|---|
| Held block, rungs 4 to 8 | 242 high (276 with the framed stave) |
| Held block, rung 9 under Move do (adds the mutation button) | 294 |
| Palette cells, 3 / 4 / 7 | 108×48 / 81×48 / 45 to 48×48 |
| Undo | 44×44 |
| Bar map buttons, 2 / 4 systems | 136×44 / 65×44 |
| Ladder rows | 328×44 |
| Ladder rows on screen under the held block (above the tab bar / clear of the play bar) | 9 / 8 of 11 at rung 6; 8 / 6 of 12 at rung 9 |
| Controls under 44 px, text under 11 px, sideways scroll, page errors | none in any scene |

The rung 6 ladder (low so to high do) is 11 rows, so two are below the fold at any moment; the block stays put while they scroll.

### 1.7 Markup and state

`deskLen()` and `palHTML()` write the markup. In short:

```html
<div class="meldesk bylen">
 <div class="melhold">
  <div class="melscore">            <!-- add class "one" when there is a single system -->
   <div class="lbl" role="status" data-notm>Bar 3 of 4 · in beat 1</div>
   <div class="el-sysrow"><div class="el-sysmap" role="group" aria-label="Bars">…</div>
     <button class="el-undo1" data-hist="ear:u" aria-label="Undo">…</button></div>
   <div class="melfr" id="earMel" role="img" aria-label="Written so far: …"></div>   <!-- class "bare" on phones -->
  </div>
  <div class="el-palwrap"><div class="el-lbl" data-notm>Length</div>
   <div class="el-pal" role="radiogroup" aria-label="Note length">
    <button class="el-len" role="radio" data-len="e" aria-checked="true" aria-disabled="false" aria-label="quaver" tabindex="0">…</button>
    <button class="el-len" role="radio" data-len="q" aria-checked="false" aria-disabled="true" aria-label="crotchet, cannot start inside a beat" tabindex="-1">…</button>
    <button class="el-len rest" data-rest="qr" aria-disabled="false" aria-label="crotchet rest">…</button>
   </div>
   <!-- rung 9 under Move do: the .el-mut button goes here -->
  </div>
 </div>
 <div class="melentry">…the ladder…</div>
 <div class="melacts">…Undo, Redo, Clear, Check, show letter names…</div>
</div>
```

State: `EAR.ans` becomes a list of `{len, sol}` (a rest has no `sol`; the mutation is `{mut:true}`); `EAR.len` is the chosen length (not saved, not in the history). The bar map's two small bars per button are gold when that bar is full.

---

## 2. The reveal at rungs 4 and up

Mock-ups: `res_r6`, `a2_r7` (desktop, phone card, phone `_result`).

**Order.** The verdict comes first, then the staves (rungs 1 to 3 keep stave, then verdict: their stave is one line). A four-bar comparison is 433 px high at 1366; with the verdict under it, the answer to "was I right?" would be off the screen. On phones the verdict panel is first as well, and the block stops being held (nothing is being entered).

**The headline reports the two halves apart** (`.el-answer.two`, written by `resultHTML`):

- Each half is an icon and words, so it never rests on colour: a tick with "Rhythm right", or a cross with "Rhythm 7 of 8 beats"; a tick with "Solfa right", or a cross with "Solfa 10 of 12 notes". The unit is small text.
- The verdict line above it is as now: Correct when both are right, otherwise Not this time (register D4 (a): all or nothing for the score). "x of y notes" goes to the journal line.
- **Rhythm** is counted in beats: a beat is right when what the student has in it (starts, holds, rests) is the same as the answer, as the rhythm drill counts.
- **Solfa** is counted in the answer's notes, **bar by bar and in order**: the nth note the student wrote in a bar against the nth note of that bar. A barline stops one slip from pushing every later note out of place. **Open point O4**: this is the engine's and the checker's to confirm.

**The staves.** Each system is a pair, aligned beat for beat (same bar widths, same spacing rule): "You wrote · bars 1–2" above "The melody · bars 1–2" (the second label in gold).

| Mark | Where | Meaning |
|---|---|---|
| Red note head, stem and syllable | "You wrote" | a wrong note. A beam stays ivory unless every note under it is wrong |
| A 2 px red rule under the beat, below the syllables | "You wrote" | that beat's rhythm is wrong |
| Time names, 11 px, muted, under the syllables | "The melody" | the rhythm pattern names (ti-ti, ta, tam-ti …), one per cell, from `RHYNAMES` and the names setting. This is the only place they appear in the melody drill |

The two error marks differ by shape and place as well as colour (a head against a rule), and the red head is far darker than the ivory ones, so it reads without colour. A key line under the staves (`.el-markkey`) says what each mark means.

The teaching sentence names the place and the fix, rhythm before solfa, each once: "Bar 2, beat 2 is two quavers, mi re: you wrote one crotchet. In bar 3 the third note is so, the top of do–mi–so: you wrote la." The first replay is the first bar with an error ("Hear bar 2: yours, then the answer").

**Nearly, at rung 10 only** (register D4): every sound and the rhythm are right, and at least one chromatic note has the other spelling (se for fi).

- Verdict "Nearly" (gold, the wave icon). Headline: tick "Rhythm right"; wave "Solfa right by sound" with small text "1 other spelling".
- On "You wrote" the note head stays ivory (the sound is right); its syllable is gold with a dotted gold underline. The key line gains "the other spelling".
- Sentence, for example: "Bar 5: you wrote se; going up it is fi. The same sound, the other name: a chromatic note on the way up is raised, on the way down lowered."
- Streak kept, not counted as right, and left out of the last-10 window (section 7). Not drawn; the mark is in `score()` (`near`).

**Phones.** One pair at a time, with the bar map. Its small bars now show the result per bar: a green bar for a bar that is right, a red outline for a bar with an error (shape as well as colour), and the button's label says which ("Bars 1 to 2, a rhythm slip in bar 2"). The view opens on the first pair with an error.

| | 1366 | 390 |
|---|---|---|
| Result panel, `res_r6` | 476×335 | 328×394 |
| Headline | 396×66, two lines | 256×57, two lines |
| Staves, 4 bars | 442×433 (two pairs) | 328×206 (one pair) |
| Card | 842×1215 | 362×1699 |

`aria-label` on the stave gives both in words ("You wrote: do re mi; so mi; … The melody: …").

---

## 3. The augmented 2nd, fa to si (rung 7)

Mock-ups: `a2_r7`, and the first column of `lad_chr`.

The step is shown in three places, with one idea: **count the semitones**.

1. **On the ladder, always, at rung 7** (it belongs to the rung, not to the item, so it tells nothing). A gauge runs down the right of the rows from fa up to si: one node per row it passes (fa, fi, so, si), so three gaps, with the end nodes filled. Beside it, in the so row, "3 semitones" over "fa to si". On a ladder with half rungs the eye already sees that fa to si passes two rungs where every other step passes one or none; the gauge says so in a number. Muted while writing.
2. **In the feedback**, when the melody takes that step (whether or not the student got it right): the gauge turns gold and its four rows stay at full strength in the locked ladder (`.earlad.a2on`); the result panel shows a small figure (`.el-gap`), two measures one above the other in semitone cells: "fa to so · 2 semitones · a tone" in grey, "fa to si · 3 semitones · an augmented 2nd" in gold. On phones, where the ladder is below the fold, the figure carries it.
3. **On the stave**, "The melody" row: a gold bracket over the two notes, labelled "augmented 2nd".

Sentence (mine, for Content): "From fa up to si is three semitones, an augmented 2nd. That is wider than a tone, so the step sounds almost like a leap: the sound of the harmonic minor." When the student wrote so for si it follows the register's line: "Bar 2: you wrote so; it was raised: si." The first replay: "Hear fa to si, then fa to so".

The gauge is drawn in CSS from classes on the rows (`a2`, `a2bot` on fa, `a2top` on si); nothing is measured in script. The figure carries `data-notm` so the terms glosser leaves it in one line.

| | 1366 | 390 |
|---|---|---|
| Ladder, rung 7 (9 notes, 3 half rungs) | 292×609 | 328×561 |
| The figure | 396×43 | 302×93 |

---

## 4. Rung 9: "Keep home do" and "Move do (mutation)"

Mock-up: `mut_r9`.

**The setting.** One more group at the right of the listening options row (`.el-vars .grp.set`): the label "Solfa" and a two-part switch, **Keep home do** (default) and **Move do (mutation)**. Shown at melody rung 9 only. Saved with the rest of `cjg_ear` as `EAR.do` (`'home'` / `'move'`). Changing it clears what is written for this question (the question and its plays stay), as one step that Undo brings back. On phones it takes a row of its own (136 and 164 × 44).

**Under Keep home do** nothing more is asked: the ladder carries the half rungs the modulation needs (fi, si, ri), the syllables stay in the home key, and there is no mutation button.

**Under Move do (mutation):**

- **The question** gains one sentence, "Where the key changes, mark the mutation.", and under it, the first time in a visit, the gloss (`.el-gloss`, 12.5 px): "**Mutation:** renaming the notes so the new key's home becomes do." The same sentence is the tooltip of the setting's second button, so it can always be found again.
- **The button** (`.el-mut`), full width under the palette, 44 px, dashed gold: **Mutation here: so = do**. It acts on the note just written: that note becomes the pivot. It is disabled until a note has been written. On phones it sits in the held block under the palette.
- **After it is pressed** (one step; Undo takes it back):
  - the button turns solid and reads "Mutation set: so = do", with the bar at its right ("bar 4");
  - **the stave** writes the pivot's double name under it, old name first, in gold: "s = d" (in general the note's name in each key: "r = s", "l = r");
  - **the ladder relabels**: the same pitches, top to bottom, named in the new key. Each row shows its new name, its hand sign for the new name, and at the right "was s", its old name. The home mark moves to the new do. A note that was chromatic and is now in the key becomes a full row ("t," with "was fi"); the half rungs are the new key's;
  - notes written from here on are named in the new key.
- One mutation per melody. It is offered on every rung 9 question under this setting, so its presence tells nothing; whether to use it is part of the answer.
- **Marking** is by sound (L102). Under Move do the headline gains a third part where a mutation is expected or was marked: tick "Mutation in place", or cross "Mutation missing" / "Mutation late" / "Mutation early", by the register's pivot window. **Open point O2**: a mutation marked in an item that moves to the relative key (do does not need to move), with every sound right.
- **Feedback line**, exactly: "Mutation at the G: so became do, and F♯ is the new ti." (the pivot's letter name, and the new leading note). For the minor to dominant minor kind the same pattern would read "Mutation at the E: mi became la, and D♯ is the new si." (mine, for Content). At the reveal both staves carry the double name where the mutation was put, and where it belongs.

| | 1366 | 390 |
|---|---|---|
| Setting group | 289×32, buttons 103 and 132 × 30 | 302×66, buttons 136 and 164 × 44 |
| Mutation button | 292×44 | 328×44 |
| Ladder after the pivot (11 notes, 1 half rung) | 292×641 | 328×561 |
| Score, 8 bars | 442×419 | 328×91, one system, four bar-map buttons 65×44 |

---

## 5. Rhythm: the names setting and the tuplet tiles

Mock-up: `rhy_r9`.

**The setting.** A group in the rhythm drill's listening options, after Pulse, Speed and Sound: the label "Names" and a two-part switch, **Kodály names** (default) and **Kodály with konnakol tuplets**. Shown from rhythm rung 7 (the first rung with a tuplet); below that the group is not drawn. `EAR.names` (`'k'` / `'kk'`), saved. It changes labels at once (tiles, and the names under the stave at any reveal, the melody drill's included) and never changes marking. At 1366 it wraps to a second line of the options row, right-aligned (339×32); on phones it is a row of its own (buttons 111 and 189 × 44).

**Tiles in families.** From the rung where there are more than nine tiles, the tiles are grouped under small captions by how long they are: "One beat", "Two beats" (and "Longer" where the rung has three- or four-beat cells), "Tuplets". The metre decides which tiles show (the six compound tiles replace the simple ones in 6/8 and 12/8).

**Tuplet tiles** (`.el-tile.tup`):

| Tile | Name, Kodály names | Name, with konnakol tuplets | Size |
|---|---|---|---|
| Triplet | tri-o-la | ta-ki-ta | 56×88 |
| Quintuplet | ta-da-ki-na-dom | ta-da-ki-na-dom | 112×88 |
| Septuplet 3 + 4 | ta-ki-ta / ta-ka-di-mi | the same | 96×88 |
| Septuplet 4 + 3 | ta-ka-di-mi / ta-ki-ta | the same | 96×88 |

- The 5- and 7-tuplet tiles carry their konnakol names **in both settings** (D12 (b)).
- A septuplet's name is set on two lines, **one line per group**, so the name shows the grouping the notes show.
- Drawn as semiquavers under one beam with the figure (3, 5, 7) in italic above. A septuplet's second beam breaks between its groups. **Open point O5**: the register also asks for a dashed sub-group mark; at 12 px a note I have left it at the beam break, which is the standard sign.
- At most one quintuplet or septuplet in a bar (register): once a bar has one, those three tiles dim.

**On the stave.** A beat that holds a quintuplet is drawn 1.3 times as wide, a septuplet 1.75 times (never less than 12 px a note); the beat numbers and the sound strip follow, so nothing else in the bar moves out of proportion. An irregular bar shows its grouping as a dashed line where each later group starts (5/4 as 3 + 2: before beat 4), and the count-in sentence says it ("Five clicks count you in, grouped 3 + 2").

| | 1366 | 390 |
|---|---|---|
| A plain 5/4 bar (no time signature) | 324×90 | 254×90 |
| The first bar (time signature) with a septuplet in it | 393×90 | 322×90 (328 available) |
| Bars to a line | two | one |
| One-beat and two-beat tiles | 56×76, 112×76 | the same |

`tile()`, `cellMarks()` and `rhyBar()` in `ladder_ui.js` are the reference. They work in beats, not in sixteenths of a 4/4 bar, which is what the register's rule U (420 ticks to a crotchet) needs.

---

## 6. Chromatic ladder rows (melody rungs 7 to 10)

Mock-up: `lad_chr` (rungs 7, 8 and 10 side by side; rung 10 on a phone).

**Names only. No new hand-sign drawing is made or asked for** (the hand-sign art is on hold). The seven notes of the scale keep their rows and their present drawings.

- A chromatic note is a **half rung**: a shorter, darker row (36 px against 52; `--inset` against `--panel`) set between the two notes it lies between. So the ladder becomes a true ladder of semitones: where two rows touch (mi–fa, ti–do) there is nothing between.
- **Lowered notes on the left half, raised notes on the right half** (Justin's chart): ra, me, se, le, te left; di, ri, fi, si, li right. At rung 7 only the right halves are there (si, fi); at rung 8 te is on the left and fi on the right; at rung 10 every half rung has both.
- Each half rung says what it is: the syllable, then "raised so" or "lowered ti" in 11 px. With "show letter names" on, the letter follows the syllable as in the full rows.
- The si row of the 0.48 minor rung (the so hand with a sharp beside it) is not carried forward. The tips card line "si uses the so sign, raised" should go with it (for Content).
- Markup: `ladHTML()`. A ladder with half rungs has class `chr` and is a plain column (the 26 px grid tracks of the present ladder are not used).

| | 1366 | 390 |
|---|---|---|
| Note row / half rung (in the 292 px desk column) | 292×52 / 145×36 | 328×44 / 163×44 |
| Rung 7 ladder (9 + 3 rows) | 609 high | 561 |
| Rung 8 ladder (11 + 3 rows) | 719 high | not drawn |
| Rung 10 ladder (11 + 7 rows) | 875 high | 843 |

The rung 10 ladder is long: 18 rows. On a phone about nine are on screen under the held block at a time (438 px of room, 47 px a row).

---

## 7. Picker, suggestion and last 10

As specified in `DESIGN_049.md` 2.1 and 2.2 and `ladder049.css`, with Justin's answers:

- **D3 (a)**: the banded picker on melody and rhythm only; the five three-rung drills keep the present control.
- **D4 (a)**: on phones one band is open and the others fold to tabs.
- **D5 (a)**: a suggestion may cross a Stage, and says so ("Rung 5 starts Stage 5").
- **Correction to 2.2: the "8 of the last 10" window leaves Nearly out**, with Shown and Skipped (register D10 (a)). Only answers marked right or not right enter the ten. A Nearly draws no mark in the last-10 row and moves no dot.
- One name for the data: the register's `EAR.rd[drill][rung]` (the last ten, 1 or 0), in place of `EAR.hist` in my 2.2; `EAR.reached[drill]` as there.
- The rhythm drill's Stage tag becomes "Stage 4–6" (register section 1); the mock-up shows it.

---

## For the implementer

1. Lift `ladder_ui.css` after `ladder049.css`; delete from `ladder049.css` the rules its header names.
2. Add the three outlines on line 4 of `ladder_ui.js` to `ELGLY` (`flag16thUp`, `rest8th`, `noteheadWhole`).
3. Colours on the stave come from the tokens (`--red` is `#d15e5d` after C6): `earMelMount`'s `RED` reads the token.
4. On phones the melody stave is mounted with class `bare` on `.melfr` (the engine's `ENG.avail` already allows for it).
5. Tests to add:
   - `earlab_ui_test` A at 1366 and 390 for each new view: 11 px floor, 44 px targets on phones (count `.el-len`, `.el-undo1`, `.el-mut`, `.earhalf .earstep`, `.el-tile.tup`, `.grp.set .el-seg button`), no sideways scroll;
   - a unit test for `earLenLive` over every rung and metre, and for the rule that moves the chosen length;
   - beaming: every cell of every rung, entered note by note, ends beamed as the cell is written;
   - the result counts: beats for rhythm, notes bar by bar for solfa;
   - names: every tile has a name under both settings; the 5- and 7-tuplet names are the same in both.

## Open points

Recommendation first in each.

- **O1. Names on the palette.** None, as decided. If Justin wants the single-value names under the notes (ti, ta, tam, ta-a), it is one line in `palHTML`; the semiquaver has no approved name of its own.
- **O2. A mutation marked where do does not need to move** (relative-key items), every sound right. Recommend: right, with a sentence that says do could have stayed. The register's to decide.
- **O3. Rung 12's palette** needs the curated list. Recommend keeping every excerpt inside the seven drawn here.
- **O4. How solfa is counted when the rhythm is wrong** (bar by bar, in order). The engine's and the checker's to confirm.
- **O5. The septuplet's sub-group mark**: beam break only.
- **O6. Verdict first at rungs 4 and up**, stave first at rungs 1 to 3. Recommend keeping the difference; the alternative is verdict first everywhere.

## Not checked

- No real phone, and no student has used any of it.
- The live rule (`earLenLive`), the beaming and the mutation are specified and drawn, not built: the mock-ups show states I set by hand.
- Not drawn: the Nearly result at rung 10; the reveal at rung 9; the two-row palette (more than seven cells); the two-part rungs (melody 11, rhythm 10); 7/8 and 12/8; a 4/4 bar with semiquavers on a phone; rests in a melody.
- The phone stave in 6/8 is tight (a quaver is about 19 px); it reads in the render, and a real phone should confirm it.
- Contrast was not re-run for this part: it uses the C6 tokens and existing text colours only.
