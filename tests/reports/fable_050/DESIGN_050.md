# DESIGN_050: Levels (design spec for the build)

Fable, 22 Nov 2026. Base: `050-levels` (0.49 plus the level plumbing already in the branch: `LVN`, `LVMIG`, `lvlSet`, `cjg_level`, `Q[].l` and `Q[].s`).
Nothing in the app folder was edited. Everything here lives in `/home/claude/fable050/`.

| File | What it is |
|---|---|
| `assets/levels050.css` | **The CSS to build.** Append it to the end of the main `<style>` in `index.html`, as written. |
| `mock_level_control.html` (+ `_closed`, `_L4_nocur`) | Piece 1 |
| `mock_ordering.html` (+ `_L2_open`) | Piece 2 |
| `mock_rungs.html` | Piece 3 |
| `png/` | Renders. Names: `<mock>_<width>.png` at 1440, 1366, 1280 (level control and rungs), 1024, 390, and 820 where a tablet tier matters |
| `tools/build.py`, `tools/shots.py` | Rebuild the mocks and the renders. `shots.py` also reports sideways scroll, text under 11 px and phone tap targets under 44 px |
| `assets/app.css` | The app's own `<style>` block, copied unchanged, so the mocks use the real components |

The mocks use the app's real CSS and the real fonts (Outfit, Poiret One). The only new CSS is `levels050.css`. Blocks marked "mock scaffolding" in `build.py` are not part of the build.

**Mock content that is illustrative, not decided:** the "≈ NSW Stage" text for each level, the levels given to the Forms, the Level 6 and 7 chord types, and which Ear Lab rungs are written. Take the real values from the Levels Framework and the Retag docs.

---

## 0. One shared mark: the level numeral (`.lvm`)

A 20 px ring with the level number in it (11 px). It is the only level marker in the app. Three states, told apart by shape as well as colour:

| Class | Meaning | Look |
|---|---|---|
| `.lvm` | a level already met (below yours) | solid gold ring, gold numeral |
| `.lvm.now` | your level | filled gold disc, dark numeral |
| `.lvm.ahead` | above your level | dashed grey ring, grey numeral |

`.lvm.lg` is the 26 px size (level button and level list).
Markup: `<span class="lvm now" aria-hidden="true">5</span>`. It is always `aria-hidden`; the level is given to screen readers in the label of the thing it marks.

The gradient bar (green to pink) keeps its one meaning in the app: "you are here". It is used for "new at your level" and for "your level" on the phone rung tabs.

---

## 1. The level control

### 1.1 What it is
The seven buttons become **one button** in the top bar that shows the current level, and a **list of the seven levels** that opens beneath it. On phones the same list sits in the More sheet.

Reason: seven names do not fit in the bar, and a level is a setting a learner changes rarely. One button frees about 65 px, which is part of the search-field fix.

### 1.2 Top bar markup (replaces `<div class="lvl" id="lvl">…</div>`)

```html
<div class="lvc" id="lvl">
 <button class="lvbtn" id="lvBtn" aria-haspopup="true" aria-expanded="false" aria-controls="lvPop"
         aria-label="Your level: 5, Senior, about NSW Stage 6. Change level" title="Your level">
  <span class="lvm lg now" aria-hidden="true">5</span>
  <span class="lvbtn-t"><b>Senior</b><small>≈ NSW Stage 6</small></span>
  <svg class="car" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4"/></svg>
 </button>
 <div class="lvpop" id="lvPop" role="dialog" aria-label="Your level" hidden>
  <!-- the level list, 1.3 -->
 </div>
</div>
```

- Curriculum set to None: leave out the `<small>` (the name centres on its own) and drop "about NSW Stage 6" from the `aria-label`.
- Journal button markup changes so it can shrink to its icon:
  `<button class="jbtn" id="openJ" aria-label="Journal"><span class="ji" aria-hidden="true">✎</span><span class="jt">Journal</span></button>`

### 1.3 The level list (used in `#lvPop` and in the More sheet)

```html
<div class="lvhd"><span class="lbl" id="lvLbl">Your level</span><small>≈ NSW syllabus</small></div>
<div class="lvlist" role="radiogroup" aria-labelledby="lvLbl">
 <button class="lvopt upto" role="radio" aria-checked="false" tabindex="-1" data-l="1">
  <span class="lvm lg" aria-hidden="true">1</span><b><span class="sr">Level 1, </span>First steps</b><small>≈ Stage 4</small></button>
 …
 <button class="lvopt upto" role="radio" aria-checked="true" tabindex="0" data-l="5">
  <span class="lvm lg now" aria-hidden="true">5</span><b><span class="sr">Level 5, </span>Senior</b><small>≈ Stage 6</small></button>
 <button class="lvopt" role="radio" aria-checked="false" tabindex="-1" data-l="6">
  <span class="lvm lg ahead" aria-hidden="true">6</span><b><span class="sr">Level 6, </span>Advanced</b><small>≈ Stage 6</small></button>
 …
</div>
<p class="lvnote">What is new at your level comes first in every list. Nothing is hidden.</p>
<div class="lvcur"><label for="lvCur">Curriculum</label>
 <select id="lvCur"><option value="nsw">NSW (Stages 4–6)</option><option value="">None</option></select></div>
```

- `.upto` goes on levels 1 to the current level (it turns the ladder line between the discs gold).
- Disc: below current = plain, current = `.now`, above = `.ahead`.
- Curriculum None: omit the `<small>` in `.lvhd` and leave each row's `<small>` empty.
- In the More sheet use the ids `mslvLbl` and `mslvCur` (ids must be unique). `.sr` is a visually hidden class; if the app has none, add `.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}`.
- The curriculum setting lives **at the foot of the level list**, in both places. It is a `<select>` because more curricula are coming.

### 1.4 More sheet markup (replaces the `Stage` label and `#msLvl`)

```html
<div class="mslv" id="msLvl"> …the level list from 1.3… </div>
```
The sheet's `aria-label` becomes "More". The sheet's max height goes from 80vh to 88vh (in the CSS). On a 390 × 844 phone the whole sheet shows with 5 px of scroll; on shorter phones it scrolls.

### 1.5 Measurements

| Part | Value |
|---|---|
| `.lvbtn` | 38 px high (same as the search field), radius 22, 1 px `--line` border on `--panel`; gold border on hover and when open |
| Button text | name 14 px ivory; hint 11 px muted |
| `.lvpop` | 340 px wide, 11 px below the button, right edges aligned; `#14110b`, gold top border, radius 14 (same family as the More sheet) |
| `.lvopt` rows | 40 px desktop, 44 px phone; name 15 px; hint 11 px; current row = gold border + 14% gold tint (same as `.qp.on`) |

Top bar, measured in the mocks with **Stop showing** (the tightest case):

| Width | What shows | Search field | Before (0.49) |
|---|---|---|---|
| 1440 | full title, crumb, search, level with hint, Stop, Journal | 420 (its max) | 372 |
| 1366 | same | 356 | 298 |
| 1280 | crumb hidden (existing rule) | 409 | 346 |
| 1024 | title shortens to JUNGLE GYM | 399 | 220 (the sliver) |
| 820 | level button = disc and caret only; Journal = icon only | 368 | about 60 |
| 390 | row 1: JUNGLE GYM and the level button; row 2: search | 366 | 366 |

### 1.6 The search-field fix (in the CSS)
1. `.search{flex:1 1 260px;min-width:200px}`.
2. 761 to 1100 px: hide `.top .tw` (the word COMPOSITION), as phones already do.
3. 761 to 900 px: `.lvbtn-t` and `.jbtn .jt` hidden.

### 1.7 CSS to remove
`.lvl{…}`, `.lvl button{…}`, `.lvl button.on{…}`, `.lvl` in the 700 px and 760 px media rules, the `.mslvl` rules, and the old `.rail .lv` and `.rail .lv small` rules (replaced in `levels050.css`). Remove `.lvl button` from the transition list at line ~1125.

### 1.8 Behaviour
1. Click `#lvBtn` (over 760 px): toggle `#lvPop`, set `aria-expanded`, move focus to the checked row.
2. Click `#lvBtn` (760 px and under): open the More sheet, scroll `#msLvl` into view, focus the checked row.
3. Click a row: `lvlSet(n)`, re-render the room, update the button (disc, name, hint, `aria-label`) and both lists. On desktop close the popover and return focus to `#lvBtn`. On the phone leave the sheet open.
4. Keys in the list (radio group): Up/Left and Down/Right move and select, wrapping; Home and End; only the checked row has `tabindex="0"`. Arrow keys do not close the popover. Enter, Space or Esc close it and return focus to `#lvBtn`. A click outside closes it.
5. Curriculum: store in `localStorage` as `cjg_curric` (`'nsw'` or `''`, default `'nsw'`). On change, refresh every hint: the button, both lists, the Ear Lab rung line.
6. Hint text comes from one table, for example `const CURR={nsw:{name:'NSW',opt:'NSW (Stages 4–6)',lv:['', 'Stage 4', …]}}`. Button: `≈ NSW Stage 6`. List rows: `≈ Stage 6`. Nothing else in the app shows a curriculum hint except the Ear Lab rung line.
7. **Remove the forced level jumps** at the four places that now set `S.level=6` when a chord or scale is above the level (around lines 2667, 3099, 3671, 3674). Nothing is hidden any more, so the level never changes on its own.

### 1.9 Area names
- Rail: `<div class="lv">Library</div>`, `<div class="lv">Voicing</div>`, `<div class="lv">Compose</div>` (Poiret One 13 px gold; the old 8 px caption is gone).
- Crumbs: `Library · <b>Bm7</b>`, `Compose · <b>Forms</b>` and so on.
- Kickers: drop "Level n ·" (`Compose · hear it before you write it`). The Chord Library kicker is 10.5 px today; make it 11 px.

---

## 2. The ordering rule

### 2.1 Three bands, always in this order

| Band | Holds | Default | Class |
|---|---|---|---|
| **New at Level n** | items whose level is the learner's level, in step order | always open, cannot fold | `.lvband.new` |
| **Earlier levels** | levels 1 to n−1, ascending by level then step | open, can fold | `details.lvband.met` |
| **Ahead of you** | levels n+1 to 7, ascending | folded, one tap opens | `details.lvband.ahead` |

- Level 1 has no Earlier band. Level 7 has no Ahead band.
- If the list has nothing new at this level, the New band still shows, with one line: `<p class="lvnone">No new chord types at Level 6. Everything you have met is below.</p>`
- Sort key everywhere: `l` then `s` then the table's own order.
- This replaces every `x.l<=S.level` filter on a list. It also replaces the family groups in pickers (Power & triads, and so on); family stays as the small name on each row.

### 2.2 Single-column lists (chord types, scales, intervals, cadences, climb examples, voicing types)

One rail runs down the left of the list: the gradient bar beside what is new, then a hairline carrying one level mark at the first row of each level, then a dashed line beside what is ahead. The mark is on the rail, once per level, not on every row.

```html
<div class="lvlst" id="qualList" role="listbox" aria-label="Chord type">
 <section class="lvband new" aria-label="New at Level 5, Senior">
  <h3 class="lvbh"><span class="lvm now" aria-hidden="true">5</span>New at Level 5<span class="n">4</span></h3>
  <button class="lvrow" role="option" aria-selected="false" data-pq="dim7"><b>Bdim7</b><span>dim 7th</span></button>
  <button class="lvrow on" role="option" aria-selected="true" data-pq="9"><b>B9</b><span>dominant 9th</span></button>
  …
 </section>
 <details class="lvband met" open>
  <summary class="lvbh"><svg class="car" viewBox="0 0 10 6" aria-hidden="true"><path d="M1 1l4 4 4-4"/></svg>Earlier levels · 1 to 4<span class="n">16</span></summary>
  <div class="lvgrp" role="group" aria-label="Level 1, First steps">
   <span class="lvm" title="Level 1 · First steps" aria-hidden="true">1</span>
   <button class="lvrow" role="option" aria-selected="false" data-pq=""><b>B</b><span>major</span></button>
   …
  </div>
  <div class="lvgrp" role="group" aria-label="Level 2, Foundation"> … </div>
 </details>
 <details class="lvband ahead">
  <summary class="lvbh"><svg class="car" …/>Ahead of you · 6 to 7<span class="n">6</span></summary>
  <div class="lvgrp" role="group" aria-label="Level 6, Advanced">
   <span class="lvm ahead" title="Level 6 · Advanced" aria-hidden="true">6</span> …rows…
  </div>
 </details>
</div>
```

| Part | Value |
|---|---|
| Rail gutter | 30 px; line at x = 9 px; the New bar is 3 px wide |
| `.lvrow` | 32 px min height (46 px on phones); symbol 15 px / 600 in an 84 px column; name 12.5 px muted; `.on` = gold border + 14% tint |
| `.lvbh` | 11 px caps, 2 px tracking; gold for New, muted for the others; count at the right; 30 px high (44 px on phones) |
| Between bands | 8 px and a hairline |
| Between levels | 6 px |

Existing `data-pq` click handling carries over (rows keep `data-pq`).

**Chord Library.** The mock puts the list in a 312 px side panel (Root, Chord type, Inversion) as the stand-in for layout B. Only `.lvlst` and its children are specified here; the panel around it is mock scaffolding. At 1366 × 768 the panel shows the whole New band and the first six earlier rows without scrolling.

**Phone.** A list this long cannot sit above the chord. The chord type becomes one 48 px button showing the current type and its level mark; it opens a sheet (the More sheet component: `.msheet` / `.msb` / `.msh`, title "Chord type") holding the same `.lvlst`. Picking a row closes the sheet. See decision 4.

### 2.3 Card galleries (Forms, Climbs, Analysis scores)

Same three bands, as headed groups. New items keep today's full card. Everything else becomes a **compact card** (title, family, level mark, arrow): this is where the clutter goes.

```html
<div class="lvlst cards" id="formsList">
 <section class="lvband new">
  <h3 class="lvch"><span class="disp">New at your level</span><small>Level 5 · Senior · 2 forms</small></h3>
  <div class="climbs"> …today's .climb cards, unchanged; the .st line is the family only ("Classical")… </div>
 </section>
 <details class="lvband met" open>
  <summary class="lvch"><span class="disp">Earlier levels</span><small>Levels 2 to 4 · 7 forms · in order</small><svg class="car" …/></summary>
  <div class="climbs cmp">
   <button class="climb cmp" data-fopen="rag" aria-label="Rag, Level 4, open">
    <span class="lvm" title="Level 4 · Intermediate" aria-hidden="true">4</span>
    <span class="tx"><b>Rag</b><small>Rag</small></span><span class="arr" aria-hidden="true">→</span></button>
   …
  </div>
 </details>
 <details class="lvband ahead">
  <summary class="lvch"><span class="disp">Ahead of you</span><small>Level 6 · 2 forms</small><svg class="car" …/></summary>
  <div class="climbs cmp"> …compact cards with <span class="lvm ahead">6</span>… </div>
 </details>
</div>
```

- A form that is not built yet: `<div class="climb cmp dim">` with no arrow and `· coming in climb 13` after the family.
- `.lvch` is the Climbs group header (`.clgh`) again: Poiret One 30 px for New, 24 px for the other two. The New header's underline is the green, gold, pink hairline from the top bar.
- Compact cards: grid `repeat(auto-fill,minmax(250px,1fr))`, 10 px gap, 62 px min height, title Poiret One 19 px. One column on phones.
- Bands are 26 px apart (22 px on phones).
- The old "Stages 4–6" text on cards is removed.

### 2.4 Behaviour
1. Fold state is remembered per list: `localStorage` key `cjg_fold_<listId>`, value like `{"met":1,"ahead":0}` (1 = open). Defaults: met open, ahead folded. Listen for the `toggle` event on each `<details>`.
2. The selected item is never hidden: if it sits in a folded band, open that band on render (do not save that as the user's choice).
3. Chord search, links from other rooms and the Oracle may land on an item above the level: open the Ahead band and scroll the row into view (`scrollIntoView({block:'nearest'})`). The level does not change.
4. On render of a picker, scroll the selected row into view inside its scroll area.
5. `<details>` and `<summary>` give keyboard and screen-reader behaviour for free; the global focus ring already covers `summary`.
6. Changing level re-sorts at once. No animation.

---

## 3. The Ear Lab 21-rung picker

### 3.1 Rule
Every drill has 21 rung slots. **Rung number = 3 × (level − 1) + step**, so Level 4 is always rungs 10, 11, 12 in every drill. A slot with nothing written yet says "not yet". All seven levels always show; the "n more" chip (`.el-bandmore`) and `EAR.all` go.

### 3.2 Laptop (over 900 px): one row
Seven groups of three, joined by a short rail line, each with a caption above (number and level name). Your level's caption is gold with the filled disc, and its group has a gold border.

```html
<div class="el-rp7" role="group" aria-label="Rung">
 <div class="el-lg" role="group" aria-label="Level 3, Developing">
  <button class="el-ltab" data-band="3" aria-expanded="false" aria-label="Level 3, Developing, rungs 7 to 9"><b>3</b></button>
  <span class="el-lgcap" data-notm><i>3</i> Developing</span>
  <div class="el-lgr">
   <button data-earlv="7" aria-pressed="false" aria-label="Rung 7, Level 3, 8 of the last 10 reached" class="done">7</button>
   <button data-earlv="8" aria-pressed="false" aria-label="Rung 8, Level 3" class="">8</button>
   <span class="el-ny" style="--n:1" role="img" aria-label="Rung 9, not yet written">not yet</span>
  </div>
  <p class="el-lcap" data-notm><b>Level 3 · Developing</b></p>
 </div>
 <div class="el-lg you open" role="group" aria-label="Level 4, Intermediate">
  <button class="el-ltab you has sug" data-band="4" aria-expanded="true" aria-label="Level 4, Intermediate, your level, rungs 10 to 12, suggested next"><b>4</b></button>
  <span class="el-lgcap" data-notm><span class="lvm now" aria-hidden="true">4</span> Intermediate</span>
  <div class="el-lgr">
   <button data-earlv="10" aria-pressed="true" aria-label="Rung 10, Level 4" class="on">10</button>
   <button data-earlv="11" aria-pressed="false" aria-label="Rung 11, Level 4, suggested next" class="sug">11</button>
   <span class="el-ny" style="--n:1" role="img" aria-label="Rung 12, not yet written">not yet</span>
  </div>
  <p class="el-lcap" data-notm><b>Level 4 · Intermediate</b> · <em>your level</em></p>
 </div>
 <div class="el-lg none" role="group" aria-label="Level 7, Extension">
  <button class="el-ltab none" data-band="7" aria-expanded="false" aria-label="Level 7, Extension, not yet written"><b>7</b></button>
  <span class="el-lgcap" data-notm><i>7</i> Extension</span>
  <div class="el-lgr"><span class="el-ny" style="--n:3" role="img" aria-label="Rungs 19 to 21, not yet written">not yet</span></div>
  <p class="el-lcap" data-notm><b>Level 7 · Extension</b></p>
 </div>
</div>
```

Classes on `.el-lg`: `you` (the learner's level), `none` (no rung written in this level), `open` (phones: the tab showing).
Classes on `.el-ltab`: `you`, `none`, `has` (holds the rung in use), `sug` (holds the suggested rung).
Rung buttons keep today's `on`, `done`, `sug` and `data-earlv`.

**"Not yet".** A run of unwritten rungs inside a level is **one** `.el-ny` cell with `--n` set to the number of rungs it stands for (1, 2 or 3). It is not a button. It has a faint hatch and a dashed divider. A level with nothing written has a dashed outline. In a single 34 px cell the words wrap to two lines.

| Part | Value |
|---|---|
| Group | flexible width, 8 px apart; pill 34 px high |
| Fit | 21 rungs in one row from 901 px up. Rung cells (measured): 35 px wide at 1440 and 1366, 34 px at 1280, 37 px at 1024, 32 px at 901; 32 px high inside the 34 px pill |
| Caption | 11 px, 20 px high, 6 px above the pill |
| Rail | 1 px × 8 px line between pills |

### 3.3 Phone and tablet (900 px and under): seven level tabs over three rungs
Row 1: seven tabs, 1 to 7 (44 px high, 44 px wide at 390). Row 2: the three rungs of the open level, 50 px high. Row 3: the open level's name. The same markup; the CSS changes the layout (`.el-lg{display:contents}`).

| Tab state | Look |
|---|---|
| open | gold outline, joined to the rung row beneath |
| holds the rung in use (`.has`) | numeral in a filled gold disc |
| your level (`.you`) | short green-to-pink bar under the numeral |
| suggested rung inside (`.sug`) | gold ring (as now) |
| nothing written (`.none`) | dashed outline, grey numeral |

An unwritten rung is a wide cell reading "not yet" on one line.
At 360 px the tabs are 40 px wide (44 px high). See decision 7.

### 3.4 The rung line (existing `.el-rungline`, new wording)
`<b>Rung 10 of 21</b> · Level 4, Intermediate (≈ NSW Stage 5) · eight bars of 2/4, 3/4, 4/4 or 6/8 · adds leaps of a 6th` then Last 10, unchanged.
Curriculum None: leave out the bracket. Wrap the bracket in `white-space:nowrap`.

### 3.5 Behaviour
1. Click a rung: as now.
2. Click a tab (900 px and under): open that level (`.open` on its `.el-lg`, `aria-expanded` on the tabs). It does not change the rung in use. `EAR.band` holds the open level.
3. On entering a drill, the open tab is the level of the rung in use.
4. First visit to a drill: start on the first written rung at the learner's level; if there is none, the nearest written rung below; if none below, the lowest written rung.
5. The suggestion (8 of the last 10) points to the **next written rung**, skipping "not yet" slots.
6. Changing the learner's level only moves the `you` mark. It does not change the rung in use.
7. Every drill uses this picker, including drills with three rungs written. Remove `.el-rungs` (the "Rung 1 / 2 / 3" pill), `.el-band*`, `.el-bandtab`, `.el-bandmore`, `.el-all`.
8. Saved progress is keyed by rung number today. The move from old rung numbers to the 21 slots needs a one-time map per drill, from the Ear Lab Retag doc.
9. Focus: rung buttons and tabs keep the inset 2 px ring. No motion is added.

### 3.6 Two small labels around the picker (suggested)
- Drill tab sub-label: `12 rungs` (the number written) in place of "Stage 4–6".
- Card tag above the title: `Rungs 1 to 16 · 12 written` in place of "Stage 4–6".

---

## 4. Checks run on the mocks

- No sideways scroll at 1440, 1366, 1280, 1024, 820 or 390.
- No new text under 11 px.
- New phone controls are 44 px or more (the level button is 32 px tall with a 44 px tap area).
- Focus rings: the global `button:focus-visible` and `summary:focus-visible` rules apply to every new control; rows and rung cells use an inset ring so nothing clips.
- `prefers-reduced-motion`: the only motion added is 0.15 s colour and caret transitions, switched off in the last rule of `levels050.css`.
- Not checked: colour-blind simulation of the three level-mark states (they differ by fill, solid ring and dashed ring, so they should hold). Worth one run of `cvd_sim.py` at build.

Found in the app while measuring, not part of this job: tab-bar labels are 10.5 px; in the More sheet the close button is 36 × 28 px and Journal is 36 px high; the phone search field is 38 px high.

---

## 5. Decisions for Justin

1. **Earlier levels: open or folded?** Recommend **open** (as mocked). You use major and minor constantly, so they should not be behind a tap. Only "Ahead of you" starts folded. Either band can be folded by hand and the app remembers.
2. **Compact cards for earlier levels in galleries.** Recommend **yes**. At Level 5 the Forms page shows 2 full cards and 7 small ones in place of 11 full cards. The cost: the one-line description is gone from the small cards until you open the form.
3. **Pickers lose their family groups** (Power & triads, Sixths & sevenths, Added & extended). Recommend **yes**: the rule orders by level and step, and two groupings at once is the clutter you wanted gone. The family stays in each row's small name.
4. **Phone chord types open in a sheet.** Recommend **yes**. Tied to the Chord Library layout B decision; if the phone layout there is already settled differently, the same list can sit in that layout.
5. **The level list has no descriptions.** Recommend **adding one short line per level** ("First steps: beat, do–re–mi, major and minor chords") once the Levels Framework wording is agreed. The row has room at 52 px high. Without it a new student has only the name to choose by.
6. **Rung numbers 1 to 21, fixed to levels** (Level 4 is always rungs 10 to 12). Recommend **yes**. The alternative is naming rungs "4.1, 4.2, 4.3"; clearer about level, but it breaks "Rung n" in the feedback text, the journal and saved scores.
7. **Small phones (360 px wide).** The seven rung tabs are 40 px wide there. Recommend **accept**: they are 44 px high and 3 px apart. The alternative is a scrolling tab row, which hides Level 7.
8. **"≈ NSW" text for each level.** The mock uses 1–2 ≈ Stage 4, 3–4 ≈ Stage 5, 5–6 ≈ Stage 6, 7 ≈ Stage 6 Extension. That is my placeholder. Confirm the real wording from the Levels Framework (the branch maps old Stage 4, 5, 6 to Levels 2, 4, 5).
9. **Curriculum hint shows in three places only** (the level button, the level list, the Ear Lab rung line). Recommend **yes**: on every card and row it would bring the NSW feel back.
10. **Drill labels count written rungs** ("12 rungs", "Rungs 1 to 16 · 12 written"). Recommend **yes**; it is honest about how much of each ladder exists.
