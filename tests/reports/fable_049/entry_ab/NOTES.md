# Entry A/B: melody with rhythm (melody rungs 4 and up)

Fable, 0.49. Previews for Justin's choice; nothing here is in `index.html`. Built from the live app by `build_entry_ab.py` in headless Chrome at 1366×768 and 390×844. No real phone was used.

**Look at `sheet_ab.png` first.** Then `a_1366.png`, `b_1366.png` (the whole card) and `a_390.png`, `b_390.png` (the phone screen while entering). `a_390_card.png` and `b_390_card.png` show the whole phone card. The `.html` files are the static mocks.

Both options show the same placeholder melody (rung 6, four bars of 2/4, twelve notes, first note given) with seven notes written.

- **a · Rhythm first, then solfa.** Step 1: rhythm tiles. Step 2: the solfa ladder gives each slash note its pitch. Free movement back. This is DESIGN_049 §2.3 unchanged; the mock shows step 2, and the sheet insets step 1.
- **b · Choose a length, then tap the note.** A length palette (`entry_b.css`) takes the step switch's place: a "Length" label cell and one cell per length, name under the note, the chosen one washed gold with a bar at its foot. Each ladder tap writes one note. A gold line on the stave marks where the next note goes. A length that does not fit the rest of the bar is dimmed. On phones the palette sticks under the score, so it never scrolls away.

**Lettering.** These letters follow this brief. `LADDER_REGISTER_049.md` D3 uses them the other way round (its (a) is the palette, its (b) is two passes), and its line 338 says "duration palette + ladder" while D3 itself recommends two passes. One of the two needs correcting once Justin chooses.

## Measurements

| | a | b |
|---|---|---|
| Card height at 1366 | 967 | 979 |
| Desk height at 1366 | 536 | 552 |
| Control above the ladder at 1366 | step switch 292×54 | palette 292×70, lengths 70×68 |
| Score at 1366 | 442×198, two systems | the same |
| Desk height at 390 | 814 | 810 |
| Score block at 390 (sticky) | 218 | 215, plus the palette: 280 held in all |
| Step switch / palette at 390 | 328×54, halves 163×52 | 328×54, lengths 81×52 |
| Step 1 tiles at 390 | ta 56×76, ti-ti 56×76, ta-a 112×76 | none |
| Ladder rows at 390 | 328×44, nine rows | the same |
| Ladder rows fully above the tab bar | 9 of 9, 0 px spare | 9 of 9, 4 px spare |
| Ladder rows clear of the play bar (64 px) | 7 of 9 | 7 of 9 |
| Controls under 44 px at 390 | none | none |
| Text under 11 px | none | none |
| Sideways scroll, page errors | none | none |
| Taps for this melody | 19 (8 tiles, 11 ladder) | 14 (11 ladder, 3 changes of length) |

Worked out, not drawn: with seven lengths at the top rungs (semiquaver, quaver, crotchet, dotted crotchet, minim, dotted minim, crotchet rest) the phone palette drops its label cell and each length is about 46×52. The tap count for b assumes the palette opens on the given note's length.

## What each costs

**a.** Build: the step switch, slash notes and solfa slots on the score, the rule for keeping solfa when the rhythm changes. Both entries (tiles, ladder) exist and are reused as they are. Test: two entry states, the move between them, and the keep-solfa rule. Marking rhythm and solfa separately falls out of the data.

**b.** Build: the palette; a rule for which lengths are legal at each point (fits the bar, and stays inside the rung's rhythm vocabulary, for example no crotchet after a single quaver unless syncopa is in the rung); automatic beaming as notes arrive, including 6/8 groups; rests and the anacrusis as palette entries; the sticky palette on phones (it needs the score block's height). Test: one entry state, but the legality rule must be checked for every rung's vocabulary and metre, and beaming for every cell. Two things do not come free: the rhythm-drill tiles and their names are not reused (the palette is note values, so ti-ti, tika-tika, tam-ti and syn-co-pa never appear as patterns), and entry is still append and undo, so a rhythm slip in bar 1 found in bar 3 means undoing every note after it, pitches included.

## Recommendation

**a, rhythm first, then solfa.** It costs five more taps on this melody, but it reuses both entries the students already know, keeps the rhythm patterns and their names, lets a rhythm slip be mended without losing the pitches, and marks the two halves separately with no extra work. b is quicker for a fluent student and is one screen rather than two, so it is the better choice only if speed matters more here than the rhythm-then-pitch order.

## Not checked

- No real phone; no student has tried either.
- b's legality rule and beaming are described, not built; the palette is drawn with three lengths only.
- Compound time, rests and the anacrusis are not drawn in either option.
