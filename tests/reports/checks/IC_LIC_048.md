# IC_LIC_048: independent check, licensing and song sources (CJG 0.48, merged 048-int @ cf24fb3)

Checker: independent (did not build this work). Verdicts formed from the spec and the output before reading `tests/reports/LIC_048_report.md`.
Read-only copy: /home/claude/wt-check-int. Diffs from /home/claude/thecompositionjunglegym (`v0.48..048-int`).

## Verdict table

| # | Item | Verdict |
|---|---|---|
| 1 | Gotye: "capo 5, shapes Am G F" claim and guitartabs.cc link removed, song kept, no leftover | PASS (Should: the one remaining source is not labelled, unlike items 2b and 2c) |
| 2a | Nothing Else Matters, add9: second source | PASS with NOTE (second source confirms Cadd9 in the song, not the placement; placement still single-sourced and not labelled on screen) |
| 2b | Weather With You: no second source, claim narrowed honestly | PASS for the visible "where" text; FAIL for the source note (not visible, see 5) |
| 2c | Let It Happen: no second source, claim narrowed honestly | Same as 2b |
| 3 | FluidR3 described as "CC BY 3.0 US" everywhere it is named | PASS |
| 4a | Sapp/NIFC copyright lines and "changes made" in all score SVG credits | PASS (30 of 30 SVGs) |
| 4b | SVG drawings otherwise unchanged vs v0.48 (only credit metadata differs) | PASS |
| 5 | Source notes shown on screen; source links work | FAIL (pre-existing render bug, now load-bearing for 0.48's honesty notes) |
| 6 | No lyric pages / lyric-showing chord sheets among song sources | PASS for known domains; NOTE: 3 chord-lesson URLs could not be fetched |
| 7 | Content warnings describe, never quote; no clean/radio/instrumental suggestions; no censoring | PASS (unchanged in 0.48) |
| 8 | Credits panel / NOTICE.md / audio/CREDITS.md / README / scores/src consistent; non-commercial stated; KMEIA permission; OFL fonts | PASS |
| 9 | Two sources or one authoritative source for every song claim | NOTE / Should: 17 of 56 SONGS entries rest on one Hooktheory page, only 2 of them labelled |
| 10 | Other licensing-relevant changes in v0.48..048-int | PASS (none beyond the above; .gitignore and tests only) |

## Findings

### Must

**M1. Source notes are folded into the link URL: the 0.48 honesty notes are not visible, and the links are probably broken.**
- index.html:2387 (SONGS cards) and index.html:2755 (SCSONGS cards) render each source as
  `<a href="${esc(u)}">${esc(u.replace(/^https?:\/\/(www\.)?/,'').slice(0,60))}</a>`.
  The source strings are "URL (note)", so the whole string, note included, goes into `href`, and the visible text is the first 60 characters.
- Effect on the 0.48 changes (visible text computed from the data):
  - Weather With You: shows `hooktheory.com/theorytab/view/crowded-house/weather-with-you`. The note "a single community transcription, no second non-lyric source found yet" is never shown.
  - Let It Happen: shows `hooktheory.com/theorytab/view/tame-impala/let-it-happen (C♯ ` and the single-transcription note is cut off.
  - Nothing Else Matters add9: shows `guitargpsmethod.com/cadd-9-chord/ (lists this song among son`; "does not say where in the song" is cut off.
- The href: `new URL('https://www.hooktheory.com/theorytab/view/crowded-house/weather-with-you (D major: …)')` resolves to `…/weather-with-you%20(D%20major:%20chorus%20V7sus4%20%E2%86%92%20I;…` (checked with Node's URL parser, the same WHATWG parser browsers use). That is a different path from the real page, so the link very likely 404s. I could not fetch the mangled URL (allowlist) to confirm the 404.
- Scope: 73 of 118 SONGS sources and 54 of 54 SCSONGS sources carry a note. The render code is the same in v0.48 (pre-existing), but in 0.48 the "gaps shown honestly" requirement for Weather With You and Let It Happen depends on these notes, so I rate it Must.
- Fix: split each string at the first space: href = the URL part; link text = shortened URL; then the note in plain text after the link (escaped), e.g. `<a href="URL">hooktheory.com/…</a> (note)`. Apply this in both renderers. Add a content_lint check that every rendered `href` matches `^https?://\S+$`.

### Should

**S1. Gotye is now single-sourced but not labelled like Weather With You and Let It Happen.**
- index.html:2353 SONGS["m"], "Somebody That I Used to Know": the only source is `https://hooktheory.com/theorytab/view/gotye/somebody-that-i-used-to-know (D minor: i VII in intro and verse)`. Its `where` reads "Intro and verse loop: D minor alternating with C", with no "(as transcribed on Hooktheory)" and no single-source note. 0.48 removed the second source, so this entry dropped from two sources to one. The builder's report (section 4) says so but did not apply the label.
- Fix: give it the same treatment as items 2b and 2c ("… (as transcribed on Hooktheory)" plus the source note), or find a second non-lyric source. secretsofsongwriting.com/?p=5418 ("Why It Works") and a Rebel Music Teacher post on the song's Aeolian sample turned up in search but could not be read (bot wall and redirect loop), so neither is confirmed.

**S2. Nothing Else Matters add9: the placement claim still rests on one source and is not labelled on screen.**
- The `where` text reads "Verse: the third chord of the Em–D–C loop". The new second source, https://guitargpsmethod.com/cadd-9-chord/, does list "Metallica - Nothing Else Matters" under "Songs With The Cadd9 Guitar Chord" (fetched: no lyrics, no song chart). It does not give the placement. The limit is disclosed only in the source note, which M1 truncates.
- Fix: add "(as transcribed on Hooktheory)" to `where`, or narrow it to "Verse, as transcribed on Hooktheory; Cadd9 in the song confirmed by a second source".

**S3. The house rule "two sources or one authoritative source" is applied unevenly.**
- 17 of 56 SONGS entries have one source, all Hooktheory: Wild Thing, Hello (m, add9), Nothing Else Matters (m), Somebody That I Used to Know, Defying Gravity, Wait For It, Wonderwall (sus4, m7, 7sus4), Let It Happen, Don't You Worry 'bout a Thing, Isn't She Lovely (m7, 9), You Are the Sunshine of My Life (add9, 7sus4), Weather With You.
- 0.48 now calls Hooktheory "a single community transcription" (not authoritative) for two of them. By that standard the other 15 are below the rule too, and they are unlabelled. This is pre-existing, but 0.48's wording makes the inconsistency visible.
- Fix (a decision for Justin, as the builder also says): either record in the decision log that a Hooktheory TheoryTab counts as one acceptable source for a live claim with a visible "as transcribed on Hooktheory" label (then label all 17 consistently), or move the unlabelled ones to SONGGAPS until a second source is found.

### Could

**C1. Footer still reads "preview 0.47"** (index.html:1145) on the 0.48 build. This is not a licensing issue, but it sits on the same line as the Credits link. It is OPEN in the builder's report too.

**C2. The Credits panel and NOTICE do not mention Leipzig.** That is correct: engrave.py:135 sets `'font': 'Bravura'`, and the only "Leipzig" strings in scores/*.svg are "(Leipzig, 1839)" in the Chopin edition credit. The spec lists Leipzig under SIL OFL, so if a future engraving switches to Verovio's default font, a Leipzig credit must be added. No action now.

## Evidence for the PASS items

- **Gotye (1).** The SONGS diff v0.48→048-int removes only `https://guitartabs.cc/tabs/g/gotye/somebody_that_i_used_to_know_crd_ver_5.html (capo 5, shapes Am G F, which sound Dm C B♭)`. A grep of index.html, NOTICE.md, README.md and audio/CREDITS.md for `guitartabs`, `capo 5`, `Am G F` and `Am, G, F` finds nothing. The song is still at SONGS["m"]. Hooktheory search result confirms the page exists (https://hooktheory.com/theorytab/view/gotye/somebody-that-i-used-to-know); a direct fetch was blocked.
- **SONGS diff (2).** Only 4 entries changed (Weather With You, NEM add9, Gotye, Let It Happen). There are 56 entries before and after; none were added or removed.
- **Weather With You.** Fetched https://www.hooktheory.com/theorytab/view/crowded-house/weather-with-you: D major, chorus progression shown as V7sus4 → I, no lyrics. This matches the note. Search for a second source returned only chord-sheet sites (guitartabs.cc, guitartabsexplorer, ultimate-guitar, cifraclub), which show lyrics and are rightly not used.
- **Let It Happen.** Fetched https://www.hooktheory.com/theorytab/view/tame-impala/let-it-happen: C♯ minor; intro VI–iv–vsus4–V; verse VI–iv–vsus4–V–VI; no lyrics. The data's "intro and every verse" matches. The page writes "vsus4", not "G♯sus4"; the G♯ spelling is derived from the key, which is correct.
- **FluidR3 (3).** "CC BY 3.0 US" appears in all four places it is named: index.html:1154 (Credits panel, link text and href creativecommons.org/licenses/by/3.0/us/), index.html:1338 (code comment), NOTICE.md:48, audio/CREDITS.md:8–10. README names no licence for it (it points to NOTICE.md). The MP3s' ID3 tags carry no licence text. tests/content_lint.py checks for "CC BY 3.0" (a substring), which still matches.
- **SVG credits (4a).** All 30 scores/*.svg carry, in `<desc data-credit="cjg">` and in RDF `dc:rights` plus a new `cc:attributionName`:
  - Bach: "Copyright (C) 2009 Craig Stuart Sapp."
  - Mozart: "Copyright (C) 2004-2018 Craig Stuart Sapp."
  - Joplin: "Copyright (C) 2004-2021 Craig Stuart Sapp."
  - Chopin: "Copyright 2017-2021 The Fryderyk Chopin Institute (https://nifc.pl)."

  Each also has "Changes made: engraved to SVG with Verovio (instrument names blanked, restyled) and annotated by the Composition Jungle Gym.", the licence name and URL, and a pointer to NOTICE.md and the Credits panel. These copyright lines match the repository LICENSE files kept in scores/src/licences/ word for word, and NOTICE.md and the Credits panel. The generator is scores/src/credit.py (new COPYRIGHT table; it exits if a source has no notice).
- **Drawings unchanged (4b).** For each of the 32 files in `git diff --name-only v0.48 048-int -- scores/`, I removed every `<desc>…</desc>` and `<metadata>…</metadata>` element from the old and new versions and compared them. All 30 SVGs are byte-identical after that. The other 2 changed files are scores/src/credit.py (credit text) and scores/src/engrave.py (one docstring line, no code). scores/meta.json and the .krn sources are unchanged.
- **Lyric domains (6).** I extracted every URL in index.html and grouped them by domain. None of genius, azlyrics, musixmatch, lyrics.*, ultimate-guitar, guitartabs.cc, songsterr, chordify, e-chords, cifraclub or ukutabs appears. The nearest are chord-lesson blogs: jonmaclennan.com (9), justinguitar.com (2), fachords.com, learnjazzstandards, jazzguitar.be, and one musictheorymaterials.utk.edu "chords-only" Girl from Ipanema PDF. I could not fetch justinguitar, jonmaclennan or the utk PDF (allowlist), so I could not confirm that they show no lyrics. guitargpsmethod.com (new in 0.48) was fetched: no lyrics.
- **Content warnings (7).** WARN (index.html:2359–2372) and SCSONGS `content.note` describe themes, for example "The title and chorus use a mild word with religious imagery". None quotes lyric words, and none suggests a clean, radio or instrumental version. `cleanSuit` strips any such advice. All tracks are presented as originals. None of this changed in 0.48.
- **Credits panel and repo (8).** The panel (index.html:1146–1157) has the Sapp and NIFC copyright lines with licence links, a "Changes made" paragraph with the ShareAlike statement, the KMEIA hand signs "used with permission", VCSL CC0 1.0, FluidR3 CC BY 3.0 US, OFL fonts (Bravura with fonts/bravura/OFL.txt, EB Garamond with fonts/eb-garamond/OFL.txt, Outfit, Poiret One), Verovio (LGPL) and VexFlow (MIT), and a non-commercial statement with a link to NOTICE.md. NOTICE.md matches, and adds the KMEIA permission record (decision log L43). README.md:30–34 points to NOTICE.md and the Credits panel and states the non-commercial basis.
- **Other changes (10).** The only files changed outside scores/ and tests/ are .gitignore (node_modules pattern) and index.html. In the index.html diff, the only licensing-relevant lines are the two FluidR3 lines and the four SONGS entries. The rest is terminology, counterpoint messages and key-signature logic.

## Could not check
- Direct fetches were refused by the allowlist for these Hooktheory pages: Gotye, Nothing Else Matters, and the mangled-href URL (so the 404 in M1 is inferred, not observed). Also refused: justinguitar.com, jonmaclennan.com, musictheorymaterials.utk.edu, and github.com/gleitz/midi-js-soundfonts (so I could not confirm upstream's own FluidR3 licence wording).
- curl to hooktheory.com was refused by the egress proxy.
- secretsofsongwriting.com returned a bot-verification page, and rebelmusicteacher.squarespace.com looped on a redirect.
- I did not open the app in a browser. The visible link text in M1 is computed from the render code and the data.
- I did not check the KMEIA permission itself; I relied on decision log L43 as cited in NOTICE.md.

## Comparison with the builder's report (tests/reports/LIC_048_report.md, read after the verdicts)
- **Agree:** Gotye removal (section 4), FluidR3 wording (2), SVG copyright lines touching only the credit elements (3), the NEM second source being partial, and Weather With You and Let It Happen being unconfirmed (1). The builder also says Hooktheory-only entries are "below standard" and leaves that to Justin; I agree (S3).
- **Disagree / missed:** the builder says "the source note says so" and "the source note flags single transcription". The notes exist in the data but are not visible on screen and corrupt the links (M1). The builder did not notice this.
- **Missed:** Gotye is now in the same single-source state as items 2b and 2c but was not given the "as transcribed on Hooktheory" label (S1).
- **Partly missed:** the builder lists only 3 single-source entries; there are 17 (S3).
- **Still open in both reports:** footer "preview 0.47"; justinguitar pages not checked for lyrics.
