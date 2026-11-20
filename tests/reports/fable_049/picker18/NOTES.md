# 18-rung picker: A and B

Fable, 21 Nov 2026, for decision log L103 (18 rungs on every recognition and skill tool from 0.50; Justin: "a [Fable redesign] or sub menus?"). Previews only; nothing here is in `index.html`. Built from the live app by `build_picker18.py` in headless Chrome. No real phone was used.

**Look at `sheet_picker18.png` first.** Then `a_1366.png`, `b_1366.png`, `a_390.png`, `b_390.png` (the screen as the card opens) and `b_open_1366.png`, `b_open_390.png` (B with the Stage 6 list open). The four `.html` files are the static mocks; each carries one small script (`picker18_behaviour.js`) so the picker can be clicked and driven from the keyboard.

Both options show the same moment: melodic dictation with 18 rungs, Stage switch on 6 (all three Stages showing), on rung 14, rungs 7–10 and 12–14 reached, rung 15 suggested.

- **A · One row, all rungs.** The 0.49 banded pill row, with the Stage name moved out of the pill to a caption above it. The three groups share the card width, so the row is exactly as wide as the card at every laptop size. Same gold cell, dot and ring as 0.49; the ring is now drawn inside the cell with soft corners. On phones the 0.49 fold does not survive (six rungs beside two 60 px tabs would be 33 px each), so the three Stage tabs take a row of their own above one row of six rungs.
- **B · Stage menus.** Three Stage buttons in one row. The button of the Stage in use reads "Rung 14" and is outlined gold; every button carries six small marks for its rungs (small ring: not reached; disc: reached; bar: in use; larger ring: suggested). A button opens a list of its six rungs: numeral, one-line description, and the word "reached", "in use" or "suggested" beside the same dot and ring.

Files: `picker18.css` (both options, on top of `ladder049.css`), `picker18.js` (reference markup: `P18.a()`, `P18.b()`), `picker18_behaviour.js` (reference behaviour), `parts/metrics.json` (every number below).

## Measurements

| | A · One row, all rungs | B · Stage menus |
|---|---|---|
| Header height at 1440 / 1366 / 1024 | 145 / 145 / 145 | 130 / 130 / 130 |
| Header height at 390 | 242 | 202 |
| For scale: 0.49 header, 12 rungs (DESIGN_049 2.1) | 126 laptop, 188 phone | the same |
| Picker block, laptop | 796 × 55 (caption 19, row 34) | 796 × 40 |
| Picker block, 390 | 328 × 100 (tabs 44, gap 8, rungs 44 plus borders) | 328 × 60 |
| Rung cell, laptop | 43 × 34 at 1366 and 1440, 45 × 34 at 1024 | list row 378 × 44 |
| Open list | none | 392 × 312 laptop; 328 × 348 phone |
| Taps to reach any rung, laptop | 1 | 2 |
| Taps to reach any rung, phone | 1 in the open Stage, 2 in another | 2 |
| Smallest tap target at 390 | 53.5 × 44 (a rung); tabs 108 × 44 | 105 × 60 (a Stage button); list rows 314 × 50 |
| Controls under 44 px at 390 | none | none |
| Text under 11 px | none | none |
| Sideways scroll, page errors | none | none |
| Rung descriptions on screen | 1 (the chosen rung, in the rung line) | 1 closed, 6 open |
| What the open state covers | nothing | the rung line, the question line and the top of the play panel (list ends 514 px down the 768 px laptop screen, 613 px down the 844 px phone screen) |

**Fit of A.** 18 cells at a 38 px floor, six borders and two 10 px gaps need 710 px; the card gives 796 (1366, 1440) and 834 (1024). There is no width between 761 and 1440 px where it wraps.

**Keyboard and ARIA, B** (run in the live page at 1366; the log is `parts/metrics.json` → `b_1366.keyboard`). Menu button pattern: each Stage button has `aria-haspopup="menu"`, `aria-expanded`, `aria-controls`, and a label such as "Stage 6, on rung 14, 2 of 6 reached, holds the suggested rung". The list is `role="menu"` labelled by its button; rows are `role="menuitemradio"` with `aria-checked`, `tabindex="-1"`, and a label such as "Rung 15, Stage 6: harmonic minor · adds si, suggested next".

| Key | Where | Result (all confirmed in the run) |
|---|---|---|
| Enter, Space, Down | button | opens; focus on the rung in use, or the first row |
| Up | button | opens; focus on the last row |
| Down, Up | list | next, previous row; wraps (13 → 18) |
| Home, End | list | first, last row |
| Left, Right | list | closes this list and opens the neighbouring Stage's, focus on its first row |
| a digit | list | next row whose number ends in it (8 → rung 18) |
| Enter, Space | list | chooses the rung, closes, focus back on the button, which now reads "Rung 8" |
| Esc | list | closes, focus back on the button |
| Tab, or a click outside | list | closes |

Not run: a real Tab press (the test sends the key event; the browser's own focus move was not exercised) and a screen reader.

**Keyboard and ARIA, A.** As 0.49: rung buttons with `aria-pressed` and a label that now carries the description ("Rung 14, Stage 6: eight bars of 3/4 with dotted rhythms, 8 of the last 10 reached"); phone tabs are buttons with `aria-expanded` and `aria-controls`. Left, Right, Home, End walk the rungs across Stages and open a closed Stage on a phone. Clicked through in the static mocks (choose rung 3, Right → rung 4).

## Build and test cost

**A.** Small. It is the 0.49 picker's markup with one wrapper for the phone tabs: about 25 lines of CSS over `ladder049.css`, and `rp()` loses its per-drill band tables because every tool is 6 + 6 + 6. No new behaviour beyond the tab row. Tests: the 0.49 picker tests with new numbers (`layout_test` at four sizes, the 44 px phone count now including three tabs, arrow keys).

**B.** Medium. A new component: about 45 lines of CSS and 30 of script. The script is where the cost is: focus in and out, Esc, outside click, closing when the Stage switch or the drill changes, and the list's place on screen (it must stay above the phone's play bar and tab bar, and right-align on the third button). Tests: a new keyboard and ARIA section (the table above as assertions), focus return, the list inside the viewport at four sizes, and all of that on each of the nine tools, since the list's length in pixels depends on each tool's descriptions.

**Either one.** `index.html` on branch 049 at 7ad0895 has no banded picker yet (no `.el-band` in the file), so both are built on top of the 0.49 picker work, not instead of it. Both need 18 one-line descriptions per tool (162 lines) from the ladder register; B shows all of them, A one at a time. Both put the long header on all nine tools: DESIGN_049 D3 (b) found that 29 px more header sends the metre drill below the 1366 × 768 fold (9 px to spare), and A adds 48 and B 33 to the 97 px three-rung header. Worked out from those figures, not re-measured on the other eight tools.

## Recommendation

**A.** A ladder is easier to climb when the whole of it is in view: every rung, every dot and the suggested ring are on screen all the time, any rung is one click, and it is the cheaper of the two to build and test. It costs 15 px more header than B on a laptop and 40 px more on a phone. Choose B if reading the six descriptions before choosing matters more than seeing the whole ladder; its list is the one thing A cannot give.

## Not checked

- No real phone, no screen reader, no student.
- Drawn on melodic dictation only. The Keys interval quiz and Sing it back have a different header (`.kqhead`); neither option is drawn there.
- The Stage switch on 4 or 5 (the "more" chip of 0.49) is not drawn for either option. In A the chip would take the place of the hidden groups; in B a hidden Stage's button would go dashed.
- The 18 descriptions are mine, to test line length; the longest is 38 characters and wraps to two lines in B's phone list. The card under the header is the 0.48 melody drill, there as a backdrop.
