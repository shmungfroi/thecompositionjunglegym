# Fable review — Ear Lab card, 0.48 integration build

Build reviewed: `/home/claude/wt-check-int` (38ea640), read-only. Spec: `wt-fable/design/earlab_048/` (the SPEC, CSS and mock-ups are not in the integration tree; only `built/png` is).
My screenshots (about 250), scripts and raw measurements: `/home/claude/checks/fable_el/` (`png/`, `shots.py`, `shots2.py`, `m3.py`–`m8.py`, `metrics.json`, `metrics2.json`, `NOTES.md`). Paths below are relative to `/home/claude/checks/fable_el/png/`.

## Verdict: APPROVE WITH CHANGES

The build is faithful. The component CSS was lifted line for line (a diff of the spec CSS against `index.html` shows only additions), and the stage, toggle and ring, result panel, metre grid, one-line rhythm stave, tiles, You wrote / It was, dock, tally, inline Reset and Undo all match the mock-ups at 1440, 1024 and 390. It reads as one crafted system.

Four things must change before it ships. Three of them are places where another system (the US-term glosser, the 0.47 melody desk, the Keys header) meets the new card; one is a wrong picture. Several of the Should items are faults in my own spec that the build reproduced exactly; they are marked "spec".

### What I measured and it passed
- No text under 11 px in any state (HTML and SVG, scaled), 3 widths, 7 drills.
- No sideways scroll in any view at 390, 1024 or 1440.
- Phone targets: every Ear Lab button and tab is at least 44 px except one (FR-11). Ladder rows 44 px (8 rows = 352 px at rung 3).
- Focus: every control reached by Tab shows 2 px solid `--goldhi`, with the offsets in the spec. Order is drill tabs, rungs, toggle, variants or segments, Show me, Skip, answer area, foot. Focus goes to Next after an answer, and to "Keep it" in the Reset confirm.
- Stop: Esc stops; Space stops with focus on the page and with focus on an answer button (it stops and does not answer); a sounding variant stops the same way. On phones the global Stop hides and the dock toggle takes over.
- Reduced motion: the ring keeps running (it is information); the dock slide, tally fade and loading spin are off. No other animation runs.
- Nearly: gold panel, wave mark, "≈ YOUR ANSWER", streak kept, score unchanged, foot reads "14 answered · 2 nearly · 2 shown · 1 skipped".
- Metre rung 3: eight cells, 2/4 and 12/8 present, Irregular row, no dead cell.
- Blind analysis loads and plays; no page errors at any width.

---

## Must

**FR-1. The answer headline carries the US gloss in the display face.**
`cad_r2_wrong_result_1440.png`, `cmp_mel_blind_1440.png` (middle panel).
The headline reads "Interrupted cadence (US: deceptive cadence)" and "Imperfect cadence (US: half cadence)" in Poiret One 28 px. The spec headline is the name only; the US term belongs in muted brackets at the first mention in the sentence. Cause: the app-wide term glosser rewrites `.el-answer` (`<abbr class="tm tmb">…</abbr><span class="tmus"> (US: …)</span>`). At 390 it pushes the headline to two or three lines.
Change: put `data-notm` on `.el-answer` (the glosser already skips it), so the gloss falls on the first mention in `.el-teach`. If the gloss must stay in the headline, then at least: `.el-answer .tmus{font-family:Outfit,sans-serif;font-size:14px;letter-spacing:0;color:var(--muted);white-space:nowrap}`.

**FR-2. Melody result: Next sits between the headline and the teaching sentence.**
`mel_result_built_1440.png`, `cmp_mel_blind_1440.png` (top); fix shown in `proposal_mel_result_1440.png`.
In `.melres .el-result` the button takes its own row straight after the headline, so the panel reads headline, Next, sentence, replays. It happens at 1440 and 1024.
Change: `.melres .el-result>.el-btn{order:9;margin-top:14px}` (it keeps `grid-column:1 / -1;justify-self:start`). On phones add `justify-self:stretch` so Next is full width like every other drill (`mel_answered_wrong_390.png` shows it at 76 px wide). Tested by injection at all three widths.

**FR-3. Keys interval gym: the tally crushes the mode buttons on phones.**
`keys_name_hi_card_390.png` (also `built/png/tally_keys_sing_390.png`).
With a two-digit score the tally takes the row and "Hear it · name it" / "Sing it back" collapse to 58 × 76 px pills with one word per line. With a one-digit score they are already two lines. At 1024 they wrap to two lines as well.
Change: `.kqhead{flex-wrap:wrap;row-gap:10px}` `.kqhead button{white-space:nowrap}` and, at ≤ 760 px, `.kqhead .el-tally{flex:1 1 100%;order:-1;justify-content:flex-end}` (tally on its own line above the mode buttons).

**FR-4. The 5/4 cell picture shows the wrong metre.** (spec: my wording "grouped 3+2" was ambiguous)
`metre_r3_54_card_1440.png`.
Everywhere else in the grid a large dot is a beat and the small dots are its split. The 5/4 cell shows ●•• ●• : two beats, one split in three and one in two, which is 5/8. The beat lane directly above it, and the sound, are five beats each split in two with accents on 1 and 4. The cell and the lane contradict each other on the same screen.
Change: `ELGRP['5/4']` should draw five beat units of ●• with a wider gap after the third (6 px extra), i.e. ●• ●• ●•  ●• ●•. It fits: 12/8 already carries twelve dots in the same box. Two wording consequences for the theory check: the row sub-label "beats of unequal length" and the sentence "Count the quick notes: 3+2" are true of 7/8 but not of 5/4 as it is played here; for 5/4 it should be "Count the beats: 3+2".

---

## Should

**FR-5. Phone header: the title wraps and the header jumps after the first answer.** (spec)
`metre_answered_wrong_390.png`, `mel_answered_wrong_390.png`; measurements in NOTES.md; fix in `proposal_head_stacked_390_view.png`.
With no answers the title has 209 px and sits on one line. After the first answer the tally grows to 145–194 px and "Pulse and metre", "Rhythm dictation", "Bass and numerals" and "Melodic dictation" drop to two lines, so the whole card shifts 26 px. At two-digit scores every title but "Cadences" wraps. My mock-up only tried "6 of 9".
Change, at ≤ 760 px: `.el-head{gap:0 10px}` `.el-tally{flex-direction:column;align-items:flex-end;gap:7px;padding-top:0}` `.el-side{display:flex;gap:10px;padding-left:0;border-left:0}` `.el-side div{letter-spacing:1px;gap:5px;align-items:baseline}` `.el-title{text-wrap:balance}`. Tested: every title on one line up to 99 of 99, except "Bass and numerals" at two-digit streaks, which breaks evenly.

**FR-6. Dock: text shows through it, and it covers the feedback just given.** (first part spec)
`crop_dock_bleed_390.png`, `cad_r3_nearly_390_view.png`.
(a) The 98% ground lets the text behind ghost through the dock. Change `.el-dock.show{background:#16130d}`.
(b) Straight after an answer the dock appears over the teaching sentence, because the first replay is below the fold while the result panel is in full view. Show the dock after answering only when the whole `#earResult` has left the view (observe the panel, not its first replay).

**FR-7. Glossary underlines leak into labels, headers and the wrong word.**
`idle_metre_390_view.png` (three dotted "bar"s in the column headers), `rhy_r3_checked_390.png` ("IT WAS · BAR 1" underlined inside a caps label), `dock_rhy_playing_390_view.png` (tips note: "The bar under the notes" is glossed as bar/measure, but it means the sound strip; "quaver, crotchet, quaver" underlined three times), provenance line "bar (US: measure) 4" in `cmp_mel_blind_1440.png`.
Change: add `data-notm` to `.el-mh`, `.el-cmp .who`, `.el-rhy .tag`, `.el-lbl`, and the blind provenance line. In the rhythm note write "The strip under the notes". Keep one gloss per card: the question line already carries "bar (US: measure)".

**FR-8. US brackets are not muted in the sentences.**
`cad_r3_nearly_1440.png`: "(US: half)" and "(US: half step)" are ivory; the mock-up has them muted.
Change: `.el-teach .tmus,.el-ask .tmus,.el-tips .tmus{color:var(--muted)}`. The Nearly sentence now has two US brackets in one sentence; that wording is with Opus, and one bracket (the cadence) is enough.

**FR-9. The cadence key line.**
`cad_keyline_390_view.png`, `cad_r3_nearly_1440.png`.
- "Plagal is the same in both" does not earn its place. It breaks the "X = US Y" pattern, it forces the second line, and at rung 3 it is incomplete (Phrygian and Cadential 6/4 are also the same in both). Remove it.
- The line breaks inside a pair ("Interrupted = / US deceptive"). Wrap each pair in `<span style="white-space:nowrap">`.
- Justin asked for it on phones. On the two-column desktop layout the tips card beside the drill already gives the US names, so it is said twice. Hide it at ≥ 1180 px: `@media (min-width:1180px){.el-key2{display:none}}`.
- Margin: `.el-key2{margin:10px 0 0}`.

**FR-10. "show all rungs" is missing whenever the strip link is present.**
`strip4_390.png`, `strip4_1440.png`.
At Stage 4, Pulse and metre shows Rung 1–2 with nothing beside them; the only way to rung 3 is "3 more for Stage 5–6 · show all" at the far end of the strip, off-screen on a phone, and it does not mention rungs. The spec puts "show all rungs" beside the rung control whenever a rung is hidden. (At Stage 5 it does appear.)

**FR-11. The strip's "show all" link is 18 px high on phones.**
Only sub-44 target in the Ear Lab. Change at ≤ 760 px: `.el-all{min-height:44px;display:inline-flex;align-items:center;border-bottom:0;text-decoration:underline dotted var(--muted);text-underline-offset:4px}`.

**FR-12. Rhythm on phones: the empty second bar has no beat placeholders.**
`cmp_rhy_answering_390.png` (mock-up left, build right).
At 1440 the unwritten beats of bar 2 show dashed outlines on the sound strip; in the one-bar-per-line phone layout bar 2 is a bare line with its ruler floating above. Draw the dashed outlines in the narrow layout too.

**FR-13. Rhythm listening options: "SPEED" is stranded at the end of the first line on phones.** (spec; my mock-up does the same)
`cmp_rhy_answering_390.png`.
Wrap each caption with its control: `<span class="grp">` with `.el-vars .grp{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}`, so the row breaks between groups, never between a caption and its buttons.

**FR-14. Bass headline: Poiret One numerals read as strokes.** (spec)
`cmp_qual_bass_1440.png` (middle).
"I – vi – V – I" in Poiret One shows the I as a bare vertical line and repeats the chord row beneath it. Set the numerals in the chip face: `.el-answer .rn{font-family:"EB Garamond",Georgia,serif;font-weight:500;font-size:26px;letter-spacing:0}`.

**FR-15. Focus ring on the selected rung is nearly invisible.**
`cmp_focus_1440.png` (top). `--goldhi` inside a `--gold` fill is about 1.5:1.
Change: `.el-rungs button.on:focus-visible{outline-color:var(--ink)}`.

**FR-16. At 1366 × 768 the metre grid is not above the fold.**
`fold_metre_1366_view.png`. The spec promises toggle, question and grid above the fold for metre, quality and cadences. Quality passes (bottom at 754). Metre rung 2 ends at 833 and cadences rung 3 at 801: the Compound row is cut. The room header takes 330 px, 30 of them the new syllabus row.
Change: on the Ear Lab, when the viewport is under 820 px high and wider than 1179 px, hide the three-line room introduction (it repeats what the strip shows) or cut the room head's bottom margin; either recovers about 60 px.

**FR-17. Tips at 1024 run the full card width.**
`cad_r3_nearly_1024.png`. Lines of about 130 characters. Change: `.el-tips li,.el-tips+p{max-width:68ch}`.

**FR-18. Rhythm feedback sentence has a lower-case start and a tangled bracket.**
`cmp_rhy_checked_1440.png` (lower): "Bar 2 is exactly right. bar 1, beat 1: you wrote two quavers (US: eighth notes; two even sounds)." Should read "In bar 1, beat 1, you wrote two quavers (two even sounds)." as in the upper panel. Pass to Opus with the other text.

**FR-19. "show letter names" is a raw browser checkbox.**
`mel_answered_wrong_390.png`. White 13 px box, 20 px row. Change: `#earMain input[type=checkbox]{accent-color:var(--gold);width:18px;height:18px}` and give its label `min-height:44px;display:inline-flex;align-items:center;gap:10px` on phones.

---

## Could

**FR-20. Orphan options.** `cmp_qual_bass_1440.png`. Four quality options in three columns leave "Augmented" alone on a row; five numerals in four columns leave "vi" alone. On desktop use `.c4` for four options and five columns for five numerals.

**FR-21. "Reset score" is live when there is nothing to reset.** `idle_metre_390_view.png`. Disable it (the 40% state) until there is a count.

**FR-22. A score of 0 reads as an empty ring.** `metre_answered_wrong_1440.png`. Poiret One's zero is a perfect circle at 52 px. It only shows after a first miss. If it bothers Justin, draw the zero in `--muted` like the empty-state dash.

**FR-23. Seen on the way, outside the Ear Lab card** (not part of this verdict): Keys "Song starters" links are default browser blue with underlines (`keys_name_1440_view.png`); Keys interval buttons are 28–30 px high on phones and its checkboxes are raw; the top-bar search collapses to a clipped "F" at 1024 (`cad_r3_nearly_1024.png`); the page footer still says "preview 0.47".

---

## The three open items you named
- Interrupted-after-6/4 and Nearly wording: not reviewed as text. Visual consequence: with two US brackets the Nearly sentence runs to three lines at 1440 and five at 390, and on phones the dock covers part of it (FR-6b, FR-8).
- Rhythm names at rungs 2–3: the tiles hold them cleanly at 76 px at every width; the longest placeholder ("tika-tika", "syn-co-pa") fits its tile. Disabled tiles drop the name to 32% with the notation, as intended.
- Phone ladder: 44 px rows as built, one variable (`--lad-row`). Nothing new to add to the decision sheet.
