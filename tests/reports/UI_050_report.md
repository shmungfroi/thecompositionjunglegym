# UI 0.50 Batch 0 (V3 to V7) build report

Sonnet build agent, clone `/home/claude/sonnetA`, branch `050-ui` (from `050-levels` at 339c696). Nothing pushed. All checks below are **self-checks** by the build agent; none is an independent review.

## What was built

| Item | Commit | Built |
|---|---|---|
| V3 ordering | "0.50 V3" | `levels050.css` appended unchanged at the end of the main `<style>`, then a short block of build additions (`.sr`, chord panel layout, sheet, voicing layout). Helpers `lvSort`, `lvSplit`, `lvBands` (single-column bands), `lvCards` (card galleries), `lvReveal`, fold state in `cjg_fold_<id>` (toggle listener; a band opened only because it holds the selected item is not saved). Sort key l, stp, table order. Lists converted: chord types, scales, intervals, voicing types, cadences (climb 3), the example pickers of climbs 1, 4 to 12, climb 2 cantus and species chips, Forms, Climbs, Analysis scores. Family groups dropped. Chord Library: side panel (312 px) at 1100 px and up with the same `.lvlst`; below 1100 px one 48 px button opening a sheet (More-sheet component), picking a row closes it. Level filters removed from the lists; quiz and exercise pools are still drawn by level (see deviations). |
| V4 level control | "0.50 V4" | `#lvBtn` + `#lvPop` (radiogroup, 52 px rows, one description line each, exactly the approved wording), same list in `#msLvl` (ids `mslvLbl`, `mslvCur`), Up/Left/Down/Right/Home/End select and wrap, only the checked row has tabindex 0, Esc and outside click close, Enter/Space close, focus returns to the button; at 760 px and under the button opens the More sheet. Journal button split into icon and text. Old `.lvl`, `.mslvl`, old `.rail .lv` rules and the transition/hover references removed. Forced level jumps removed (chord search, Library hand-off, Gym `kgo`, `kmode`); `lvlSet` no longer re-renders, `lvlChange` does. The old global `[data-l]` click branch is gone (it also caught `.el-cad[data-l="the cadence"]` and would have set the level to NaN). |
| V5 area names | "0.50 V5" | Rail: Library, Voicing, Compose (Poiret One 13 px from levels050.css). Crumbs and kickers use the area name; "Level n ·" dropped; Chord Library kicker 11 px. |
| V6 Stage wording | "0.50 V6/V7" | 69 user-visible Stage strings replaced. Climb kickers and gallery cards use level ranges from the climb's own examples (`clInfo`, approved climb floors), Forms carry `l` and `stp`, climb notes and Ear Lab copy say Level n. Remaining "Stage": CURR table and the three hints, the static level-button markup, the NESA syllabus sentence `SYLS6`, and three Ear Lab "Show all" chip strings (other agent's removal, see below). |
| V7 curriculum | "0.50 V6/V7" | `CURR` exactly as specified, `curHint(l, short)` (returns "≈ NSW Stage 5" or ""), `cjg_curric` (default `nsw`, "" = None) from the select at the foot of both lists, `curSet` refreshes button and both lists, dispatches `cjg-curric` and re-renders the Ear Lab if it is the open room (the other agent's rung line can call `curHint` at render or listen to the event). |
| Tests | "0.50 tests" and this commit | `tests/ordering_test.py`, extra content_lint checks, `pageerrors_test.py` now drives the real level button and list, `tests/ui_shots_050.py`. |

Outcome codes (MU4-, MU5-, MU2- and the rest, pattern `M[UV][0-9]-...`): **109 occurrences, 12 distinct before (339c696) and 109 / 12 after**; sorted occurrence counts per code identical (`diff` empty).

## Checks run (self-checks, one browser at a time)

| Check | Result |
|---|---|
| `tests/content_lint.py` | pass; new checks `stage_wording` (0 failures, 3 known Ear Lab chip strings counted not failed) and `area_labels` (0). Seeding a kicker with "Level 3 · Stage 5" makes both fail (tried). |
| `tests/unit_test.py` | 1164 checks, 0 failures |
| `tests/ordering_test.py` (new) | 147 list checks (21 lists x 7 levels), 0 failures, 0 page errors, none skipped; plus search-above-level (level unchanged, Ahead band open, row selected, not saved), fold memory, default fold state |
| `tests/pageerrors_test.py` | 357 views, 10083 clicks, 0 errors; P2-5 sequences clean |
| `tests/layout_test.py` | 332 views, 18 findings, all `DIV.el-band` clipped at 390 px in the Ear Lab (the V9 band picker). The same 332 views / 18 findings occur on 339c696 (rerun in a worktree), so none are new. No findings outside the Ear Lab. |
| `tests/terms_test.py` (full) | 153 views, 2350 clicks, 0 failures |
| `tests/ui_shots_050.py` | top bar and level list at 1440, 1366x768, 1280x800, 1024, 820, 390 in `tests/reports/ui_050/` (also Chord Library and Forms pages); no sideways scroll at any size, no top-bar child overflowing, list inside the window, every row 52 px, no description clipped |

Search field width in the top bar (Stop hidden): 420 px at every size from 1024 up to 1440 and 366 at 390.

Not run: `spelling_test`, `chordshape_test`, the Ear Lab suites (not asked; the Ear Lab suites belong with the other agent's picker), `cvd_sim.py` for the three level-mark states (the existing script checks function colours, not the marks; the marks differ by fill, solid ring and dashed ring as specified).

## Deviations and decisions (please check)

1. **Retag docs were not available** in the clone, so every level used is an existing `.l` / `.stp` tag from the data. Items with no tag, and where I had to choose:
   - Forms: `l` taken from the existing `FB[...].l` (blues12 2, jazzblues 4, minblues 4, rag 5, rondo 3, sonata 5, rhythm 6, sonrondo 6); **phrase 2, tv 3, fugue 6 are my choice** (no tag exists). The mock's illustrative levels differ (rhythm 5, rag 4).
   - **Analysis scores have no level tags anywhere. The levels in `ANLV` (chorale 3, ohaupt 3, jesu 4, k331a 4, maple 4, entertainer 4, k331d 5, k545 5, chopin7 5, chopin20 6) are PROVISIONAL placeholders** so the gallery works. Replace the pairs with the Retag 07 values.
   - Climb card levels come from each climb's example tables with the existing page floors (1,4,1,1,1,3,4,3,4,6,2,5,4); climb 13 is 4 to 6 by hand.
2. **Chord Library layout**: side panel from 1100 px, button + sheet from 1099 px down (the spec says phone only; the tablet tier was unspecified and a 300 px list in the horizontal bar did not fit). Between 1100 and 1279 px the seed cards stack to one column to make room.
3. **Climb example pickers keep their `.cad` cards** (name, chord string, one-line feel) inside the bands, with the rail and level marks, instead of `.lvrow` rows: rows only carry two short fields and would have dropped the chord strings. Same for the climb 2 chips. Scales use `.lvrow` with alias or group as the small name; intervals and voicings use rows.
4. **Level popover 376 px wide** (spec 340) and the description wraps if it must: the longest approved line did not fit a 340 px row on one line at 11 px. Rows are 52 px at every size (the spec allowed 52).
5. **Level-gated content inside climb pages is untouched** (for example climb 8's chromatic hear cards `S.level>=6`, climb 2 `L<5` position rules, the neighbour chips in Climb further that fall back to triads below Level 3). Quiz and exercise pools stay filtered by level (`cadsFor`, `gymSet`, `C6Q`, `QVS`, `QMS`...). These are not lists a learner picks from, so I did not call them "hidden", but the spec's "nothing is hidden" could be read wider.
6. `lvlChange` does not reset `EAR.all` (the spec removes it; the other agent's picker owns it). Until that lands the "n more" chip logic is unchanged.
7. `SYLS6` ("Stage 6 (2025): the Music 2 Year 11 content ...") is NESA's own syllabus sentence and V7 says syllabus content must not change, so it stays; the lint allows it. The Ear Lab "Show Stage n only" / "outside Stage n" chip strings stay until section 3 deletes `EAR.all`; the lint counts them (3).
8. "Seed Bank" still appears in the page title and in two button labels ("Change chord in the Seed Bank"); only the area label (rail, crumb, kicker) was changed.
9. Scales and intervals pickers are a 430 px column in the left of the picker card (own scroll, 54 vh max) with empty space on the right: no layout was specified for them.
10. Search or link landing: the selected row is scrolled into view only inside its own scroll area (`lvReveal`); lists that sit in the page flow (climb examples) are not scrolled, so the page does not jump.
11. Band header ranges ("Earlier levels · 1 to 4") are taken from the levels actually present in the band, not from n-1.

## Ambiguities in the spec

- Section 2 lists "climb examples" as single-column lists but the mocks show only the chord list; see deviation 3.
- Section 1.8 item 5 says to refresh "the Ear Lab rung line": done by re-render plus the `cjg-curric` event; the other agent needs to call `curHint` where it builds the line.
- "Phone chord-type picker ... sheet" says nothing about 761 to 1099 px.
- The two hint formats (button "≈ NSW Stage 6", list "≈ Stage 6") come from one `curHint(l, short)`.

## Handoff notes for the merge with the other agent

- Both agents append the identical `levels050.css` block; my build-additions block follows it (`.sr` is defined there, so the other agent's copy of `.sr`, if any, will be a harmless duplicate).
- Overlap risk: the global click handler and `lvlSet` region (I removed `[data-l]` and `EAR.all` there), `LVN` neighbourhood, and the end-of-file phone IIFE.
- The old Ear Lab 'Level n' labels in `.el-band` still produce the 18 layout findings at 390 px; section 3 removes them.
