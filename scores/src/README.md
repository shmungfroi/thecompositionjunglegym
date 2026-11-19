# Score sources (Analysis room)

The ten Humdrum encodings the Analysis scores are engraved from, unchanged, with each repository's licence in `licences/`.
`engrave.py` turns them into `scores/<key>.svg` (desktop, 880 px), `scores/<key>.t.svg` (tablet, 560 px) and `scores/<key>.p.svg` (phone, 280 px, fits a 360 px screen) with Verovio 6.4.1 (`pip install verovio==6.4.1`, then `python3 scores/src/engrave.py` from the repo root).

| Key | File | Repository | Revision (HEAD when fetched, 19 Nov 2026) | Licence |
|---|---|---|---|---|
| chorale (BWV 269) | `chor001.krn` | github.com/craigsapp/bach-370-chorales | a95574f9e93b4d72a96cd390a059df4f8471ddb6 | CC BY-NC-SA 4.0 |
| ohaupt (BWV 244/44) | `chor080.krn` | github.com/craigsapp/bach-370-chorales | a95574f9e93b4d72a96cd390a059df4f8471ddb6 | CC BY-NC-SA 4.0 |
| jesu (BWV 64/8) | `chor138.krn` | github.com/craigsapp/bach-370-chorales | a95574f9e93b4d72a96cd390a059df4f8471ddb6 | CC BY-NC-SA 4.0 |
| k545 (K. 545/i) | `sonata15-1.krn` | github.com/craigsapp/mozart-piano-sonatas | 0f1f49d914494f8461709b2a2642153bb240c6da | CC BY-NC-SA 4.0 |
| k331a (K. 331/i, theme) | `sonata11-1a.krn` | github.com/craigsapp/mozart-piano-sonatas | 0f1f49d914494f8461709b2a2642153bb240c6da | CC BY-NC-SA 4.0 |
| k331d (K. 331/i, Var. III) | `sonata11-1d.krn` | github.com/craigsapp/mozart-piano-sonatas | 0f1f49d914494f8461709b2a2642153bb240c6da | CC BY-NC-SA 4.0 |
| maple | `mapleleaf.krn` | github.com/craigsapp/joplin | ad0840eb97e89fac7e89a94325a3d7526b0dc200 | CC BY-NC-SA 4.0 |
| entertainer | `entertainer.krn` | github.com/craigsapp/joplin | ad0840eb97e89fac7e89a94325a3d7526b0dc200 | CC BY-NC-SA 4.0 |
| chopin7 (Op. 28/7) | `028-1-BH-007.krn` | github.com/pl-wnifc/humdrum-chopin-first-editions | 95dfb105c1669c72d10b04088566154f12d3dc1c | CC BY 4.0 |
| chopin20 (Op. 28/20) | `028-1-BH-020.krn` | github.com/pl-wnifc/humdrum-chopin-first-editions | 95dfb105c1669c72d10b04088566154f12d3dc1c | CC BY 4.0 |

Note: in the mozart-piano-sonatas repository K. 545 is `sonata15` (the repository numbers the sonatas its own way; `sonata16` there is the B-flat sonata K. Anh. 136).

## How each file was matched to the app

Verovio names notes and bars after their line in the Humdrum file (`note-L23F1`, `measure-L24`), and `scores/meta.json` addresses every overlay and every bar by those names. Each file above was rendered without filters and compared with the 0.46 app's SVG and `meta.json`:

- the bar ids are identical, in the same order, and the set of note ids is identical (all ten scores);
- every note's onset, pitch and length equals `meta.json`'s `events` (to 2 ms: `meta.json` rounds onsets down), so the first and last bars hold the same notes.

`engrave.py` repeats the bar, anchor and note check every time it runs and stops on any difference.

**Unisons (0.48 fix R17).** Where tenor and bass (or any two voices) sound the same note together, onset, pitch and length cannot tell the two notes apart, and the 0.47 engraving gave six tenor–bass unisons each other's ids (BWV 269 bar 2; O Haupt bars 1, 8, 9, 11; Jesu bar 4). `engrave.py` now takes the voice from the grand-staff note's staff and layer (upper staff: soprano, alto; lower staff: tenor, bass) and gives it the id of the same voice. `tests/score_ids_test.py` checks every chorale note's id against its staff and layer, and every cadence anchor's onset against the cadence's arrival.

**BWV 269 line numbers.** An earlier mock-up found this file's line numbers two lower than the app's ids. The repository history explains it: the app's ids (`measure-L24` for bar 1) match every revision of `chor001.krn` from 6b90020 (20 Nov 2023, "Dual source encoding test for IIIF bounding boxes") to the current HEAD. Revisions 8036aea, 2016968 and f91f6cc (also 20 Nov and 19 Nov 2023) give bar 1 as `measure-L23`, and afea806 and earlier (18 Nov 2023 back to 2022) as `measure-L22`: two lower. Those revisions lack the `!!xywh` IIIF bounding-box lines added in November 2023; the music is the same. So the app was built from a revision at or after 6b90020, and the mock-up used an older copy. The file here is the current HEAD, whose ids match.

## Engraving notes

- Chorales: closed score on a grand staff via `!!!filter: satb2gs` (appended to the data in memory, not to the file). The filter rewrites the file, so `engrave.py` gives every note and bar back its canonical id, matched by onset, pitch and length.
- Instrument tokens (`*I"…`, `*I'…`, `*Ipiano`, `*ICklav`…) are blanked in memory, so there are no voice labels and no first-system indent.
- Verovio's embedded stylesheet is removed (its id-scoped `stroke` rule overrode the app's CSS); the hidden placeholders it styled are removed too. The NIFC encoders' editorial notes (`!LO:TX:…:problem`) are not part of the score and are left out.
- Bar numbers, tempo and expression text are set in final pixels (11 px, 14 px, 14 px); their fonts and colours come from the app's CSS on `.vrv`.
- **Common time (0.47 fix IC-1).** K. 545, O Haupt, Jesu meine Freude and Op. 28/20 mark the metre `*M4/4` with `*met(c)`. Verovio 6.4.1 imports that as a `meterSig sym="common"` with `visible="false"` plus an empty `mensur`, so no time signature was drawn. `engrave.py` loads the Humdrum, takes Verovio's MEI, removes `visible="false"` from common-time meter signatures and drops the empty `mensur`, then reloads the MEI and engraves it. The source files are untouched; element ids pass through the MEI unchanged (the bar, anchor and note checks still pass), and the script stops if any engraving lacks a time signature.
- **Embedded Bravura text font.** Verovio sets some dynamics as SMuFL text (the *f* of "*f* stacc." in the Maple Leaf Rag) and embeds a Bravura `@font-face` for it. That `@font-face` block is kept when the rest of the stylesheet is removed (in the first 0.47 engraving it was removed too, so that *f* did not show).
- **System spacing (design review FA-5).** Verovio's minimum gap between systems is 4 staff-spaces beyond each system's notation, plus room for the overlay rows the app draws. That is tighter than the standard's 9 staff-spaces where the notes stay inside the staves, so that 3 systems fit a 768–800 px tall screen where the score allows it.
- **Last systems (FA-8).** If the last system would hold one bar, `spacingLinear` is stepped down by 0.01, at most 5 times. K. 331 Var. III (all three engravings) and O Haupt (desktop and phone) still end with a one-bar system after 5 steps.
