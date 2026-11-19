# CJG 0.48 · Decisions 5 and 12 · design notes

Sheet: `sheet.html` (self-contained). Screenshots in `png/`. Rebuild with `python3 build.py`; colour figures from `colour.py`.

## Decision 5 · the solfa ladder on phones

**A correction first.** SPEC.md (5.5 and open question 5) says the ladder rows go to 44 px "up from 24" and the ladder to about 400 px "was 220". That is wrong. In the app, 24 px is the grid track and every note spans two tracks. Measured in the running 0.48 build at 390 px: rows are **47 px**, the ladder is 384 px at rung 3 (8 notes) and 432 px at rung 2 (9 notes). `tests/earlab_r2_test.py` already asserts rows of at least 47 px. So the question is not "raise it or exempt it"; it is "keep what ships or shrink it".

Shown at 390 px, melodic dictation rung 3, E minor, four notes written, in a 390 × 844 phone with Safari's bars up (664 px for the page). The stave and hand signs are captured from the live app.

| | Rows | Ladder (8 notes) | In view under the pinned stave | Cost |
|---|---|---|---|---|
| A · 44 px rows, one column | 44 × 328 px | 360 px | 6 of 8 notes; 79 px scroll for the rest | a short scroll on short viewports |
| B · 24 px rows, one column | 24 × 328 px | 200 px | everything | targets about half a fingertip; hand signs 21 px |
| C · two columns, staggered | 47 × 161 px | 216 px | everything | the single-column tone ladder is lost |

C: notes alternate left and right, each half a row above the next, so targets stay 47 px on a 24 px pitch. What it costs, plainly: the eye zigzags; a step crosses the gap; thirds stack in a column (m, d, l, on one side), which is a new picture every student has to learn; "home" and letter names have less room.

**Recommendation: A.** Keep the single column at full height. Nothing in the app needs to change (47 px rows already meet the 44 px rule); the spec needs correcting. The scroll is short, the stave stays pinned, and Check is in the dock. With the browser bars tucked away the eight-note ladder fits whole; the nine-note rung 2 ladder fits only from the home screen. B should not ship. C is the one to build if scrolling turns out to bother students in class, and because it changes how the tone ladder looks it should be Justin's call.

Not verified: the 664 px page height is the usual figure for a 390 × 844 iPhone in Safari with both bars showing; I have not measured it on a device.

## Decision 12 · a function colour for minor v and VII

Existing: T `#8fbf6a`, PD `#c9a24a`, D `#c8473b`, chromatic `#a493d8`. Rejected: blue-grey `#7fb3c8`.

Checks: WCAG contrast on the three dark grounds (`#0b0906`, `#0e0c08`, `#17140e`, worst quoted); colour-blindness simulated with Machado et al. 2009 at full severity; difference measured as CIEDE2000 (ΔE) to the nearest of the four existing colours. Above about 10 is easy to tell apart.

| Candidate | Hex | Contrast (worst ground) | Nearest neighbour ΔE: typical / deutan / protan / tritan | ΔE to ivory text | On ivory, use |
|---|---|---|---|---|---|
| 1 Madder rose | `#bd6b97` | 5.0 : 1 | 19 / 15 / 14 / 14 | 42 | `#9e4776` |
| 2 Verdigris | `#6fdccf` | 11.2 : 1 | 23 / 18 / 22 / 15 | 25 | `#1b7066` |
| 3 Shell | `#dfcdc3` | 11.9 : 1 | 22 / 16 / 19 / 16 | 10 | `#845c46` |
| (old blue-grey) | `#7fb3c8` | 8.0 : 1 | 20 / 7 / 11 / 9 | 28 | |

All three pass 4.5 : 1 and all three separate from the four better than the blue-grey did. None passes on ivory as is (nor do the existing four); the app has no light theme, ivory appears only as a selected-chip fill, and a deepened hex is given for that case.

**Recommendation: Madder rose `#bd6b97`.** It reads as the dominant's cooler relative, which matches the theory (same side of the key, no leading note), it belongs with the warm Garden palette, and it is not in the blue family Justin turned down. Verdigris scores slightly higher on separation but is the closest of the three to the rejected colour. Shell is distinct from the four but only ΔE 10 from plain ivory text (5 to 7 under colour-blindness), so it stops reading as a category.

One caution on rose: it is ΔE 9 from the decorative `--pink` accent (`#ee6fa5`). The accent is never used for meaning, so I think this is harmony, not a clash, but it is worth a look in the app.

**Name: "modal dominant"**, code `MD`, plain word "soft pull" (beside home, away, pull). It describes the chords without adopting one school's label. The help text can name the traditions: function theory calls v the minor dominant and VII its relative; many English-language harmony texts call VII the subtonic chord; in modal, folk and rock harmony both are ordinary closing chords. Second choice: "subtonic chords" (both chords contain the unraised 7th), though in common usage "subtonic" means VII alone. The engine tags by content (dominant-side root, no leading note), not by what the chord does in a given phrase; a passing v6 in a lament bass would get the same colour.

In the sheet's example row, ♭II6 replaces the second iv so that all five colours appear together.

## Found on the way, outside these two decisions

- Tonic green and predominant gold are only ΔE 5 apart under deuteranopia (6 under protanopia). The numerals differ by letter, so meaning survives, but the pair is weaker than any candidate here.
- Dominant red `#c8473b` is 3.9 : 1 on `#17140e` and 4.2 : 1 on `#0b0906`, under 4.5 for text at these sizes.
- `homes()` in index.html still gives minor v the dominant colour (its table maps degree 5 to D whatever the chord quality), while the part-writing engine already treats v as non-dominant. Whichever colour is chosen, both places need the new category.
