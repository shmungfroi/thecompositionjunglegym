# R14 (Could): minor licensing, 0.48

Branch `048-r14lic`, based on 0.47 (ef97cdb).

## 1. Score SVG credits

All 30 files (`scores/<key>.svg`, `.t.svg`, `.p.svg` for the ten scores) now carry, straight after the opening `<svg>` tag:

- a `<desc data-credit="cjg">` with the title, the full source line from `scores/meta.json` (edition, encoder, repository, licence), the licence URL and a pointer to NOTICE.md / the Credits panel;
- a `<metadata data-credit="cjg">` block (RDF: `dc:title`, `dc:source`, `dc:rights`, `cc:license`).

No `<title>` was added (it would show a tooltip over the whole score). Verovio's own `<desc>` is kept.

| Keys | Source credited | Licence |
|---|---|---|
| chorale, ohaupt, jesu | Sapp, 370 Bach chorales | CC BY-NC-SA 4.0 |
| k545, k331a, k331d | Sapp, Mozart piano sonatas (Alte Mozart-Ausgabe 1878) | CC BY-NC-SA 4.0 |
| maple, entertainer | Sapp, Scott Joplin edition | CC BY-NC-SA 4.0 |
| chopin7, chopin20 | NIFC, Chopin first editions in Humdrum (Breitkopf & Haertel 1839) | CC BY 4.0 |

Drawing unchanged: with the credit elements removed, all 30 files are byte-identical to 0.47. Added size: 48,303 bytes in total (about 1.6 kB per file).

Generator: new `scores/src/credit.py` (`embed()` builds the credit from `meta.json`); `scores/src/engrave.py` calls it on every engraving. Re-running `python3 scores/src/engrave.py` (Verovio 6.4.1) reproduced all 30 committed files byte-for-byte, so re-engraving keeps the credit. `python3 scores/src/credit.py` re-applies it without re-engraving.

## 2. Chord-sheet source links

Six links on lyric-displaying chord-sheet sites (guitartabs.cc x4, ukutabs.com, guitartabsexplorer.com) were found in the chord-library song data. No lyrics were quoted anywhere.

| Song | Old link | Action | What the remaining source verifies |
|---|---|---|---|
| Crazy Little Thing Called Love (Queen), Dsus4 | guitartabs.cc ... crazy_little_thing_called_love_crd_ver_7 (intro D Dsus4 D) | Removed; already covered by the MusicRadar link in the same entry (musicradar.com/how-to/brian-may-queen-guitar-chords), which I fetched | The song opens with a D vamp alternating D and Dsus4 |
| Nothing Else Matters (Metallica), Cadd9 | guitartabs.cc ... nothing_else_matters_acoustic_tab (Cadd9 in verse) | Removed; Hooktheory link in the same entry already states the verse as Em, D, C(add9) | Verse chords (Hooktheory; not re-fetched, see below) |
| Weather with You (Crowded House), A7sus4 | guitartabs.cc ... weather_with_you_crd_ver_4 | Removed; Hooktheory link in the same entry already states D major, chorus V7sus4 to I (= A7sus4) | Chorus V7sus4 to I (Hooktheory; not re-fetched, see below) |
| Highway to Hell (AC/DC), A major | ukutabs.com/id/a/ac-dc/highway-to-hell/ ("intro chord list A D G D G D G D A", the old note admitted the page did not load) | Swapped for https://www.musicradar.com/how-to/classic-rock-guitar-riffs-led-zeppelin-acdc-eric-clapton-eagles-deep-purple; note reworded to what it verifies | The riff is played with A, D and G chords, the D being a D/F# (fetched) |
| Let It Happen (Tame Impala), G#sus4 | guitartabsexplorer.com/tame-impala/let-it-happen-chords (A F#m G#sus4) | Removed; Hooktheory link in the same entry kept and its note extended with the letter names, which follow from its numerals | In C# minor, VI iv vsus4 V in intro and verse = A, F#m, G#sus4, G# (Hooktheory page fetched: no lyrics shown) |

Not replaced (left in place):

- Somebody That I Used to Know (Gotye), Dm: `https://guitartabs.cc/tabs/g/gotye/somebody_that_i_used_to_know_crd_ver_5.html` ("capo 5, shapes Am G F, which sound Dm C Bb"). The capo and shape fact is not confirmed by any non-lyric page I could reach (Wikipedia and Hooktheory song pages other than the one above were blocked by the session allowlist; the pages I could fetch were chord sites or did not agree). Hooktheory in the same entry confirms the D minor i VII sound. Suggest removing the capo/shape claim and this link, or confirming from a source you can open.

Caveats: the Hooktheory song pages for Nothing Else Matters and Weather with You could not be fetched in this session (allowlist), so I relied on the existing, earlier-audited citations there rather than re-verifying them. `hooktheory.com` (64 links) shows chords and melody, not lyrics (checked on the Let It Happen page), so it was left alone.

## 3. Unused VexFlow fonts

The fonts are not bundled in the repo: `index.html` loaded VexFlow 4.2.3 from jsDelivr as `vexflow.js`, the full build, which carries Bravura, Petaluma, Gonville and Leland. The app never selects a font other than the default Bravura. Change: the script now loads `.../vexflow@4.2.3/build/cjs/vexflow-bravura.js` (the official Bravura-only build in the same package).

- Bytes saved per page load: 992,166 to 570,163 = 422,003 bytes (42.5%).
- Petaluma, Gonville and Leland glyph data is no longer shipped. (The Bravura-only build still has a few lines of text-font metadata for the name "PetalumaScript"; no font file is loaded unless a music font is selected.)
- Test harness: `tests/harness/cjg.py` now serves the build the page asks for (it served `vexflow.js` for any VexFlow URL before), so the suites test what ships.
- NOTICE.md and the Credits panel line now say the Bravura-only build is used; NOTICE.md also notes the embedded SVG credits. The `fonts/` folder (Bravura OFL, EB Garamond) is untouched.

Visual check: 80 app views (every VexFlow score view of the score_measure suite, at 1440 px and 390 px) were rendered with the full build and with the Bravura-only build and their `svg.vfx` markup compared. The markup is identical in 76 of 80 views, with no page errors. The other 4 are the random ear-training drills ("ear/rhy answer", "ear/mel answer" at both widths), which also differ between two runs of the same build, so they are random, not font, differences. Raw screenshots differ run to run (animation and random content) even for the same build, so the markup comparison was used. Not verified: the live jsDelivr URL (outbound CDN is blocked from this machine); the file exists in the published `vexflow@4.2.3` npm package, which jsDelivr serves, and the local copy of that file was used in tests.

## Suite results (run from the worktree)

- content_lint: pass (60 song entries, lyric-word check: no failures, credits check passes)
- analysis_engrave_test: pass (0 failures; includes the Bravura @font-face and common-time checks on all 30 SVGs)
- score_measure_test: pass (300 scores measured, 0 with findings, no page errors)
- pageerrors_test: pass (0 page errors; 881 seeded random climb-2 clicks, 0 errors)

## Not done / for decision

- Gotye link above (left, listed).
- No lyrics were quoted; no new songs were added.
