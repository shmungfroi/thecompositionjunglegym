# LIC_048: licensing and song-source follow-ups (branch 048-lic, from v0.48 @ 075e6c1)

All checks below are the builder's self-checks; an independent checker should review them.

## 1. Second non-lyric sources (IC_R14_R18 rec. 3)

| Song / claim | Result | Change |
|---|---|---|
| Nothing Else Matters, Cadd9 | Partly confirmed | Added https://guitargpsmethod.com/cadd-9-chord/ : lists the song among songs that use the Cadd9 chord (no lyrics). It does not say where in the song, so the "verse, third chord" placement still rests on Hooktheory alone; the source note says so. |
| Weather With You, A7sus4 (V7sus4 to I) | NOT confirmed by a second non-lyric source | Claim narrowed: the "where" text now says "as transcribed on Hooktheory" and the source note reads "a single community transcription, no second non-lyric source found yet". |
| Let It Happen, G#sus4 | NOT confirmed by a second non-lyric source | Same narrowing ("as transcribed on Hooktheory", source note flags single transcription). |

Pages fetched and found NOT usable (no chord info, or they display lyrics): en.wikipedia.org Weather_with_You and Let_It_Happen (no chords or key); davesmusicdatabase (history only); neilfinn.com weather-with-you (lyrics, no chords); americansongwriter Crowded House list; songfacts Let It Happen (no chords); licklibrary NEM lesson (no chord names); musicradar metallica-chords lesson (no NEM, Emadd9 only); richterguitar, pickuptheguitar, yousician (show lyrics, and list plain C, not Cadd9); yourguitarworkshop (login-gated). Chord-sheet sites that display lyrics were not used.
Note: these two entries still carry one source (Hooktheory, a community transcription, not an authoritative source). By the house rule they are below standard; decision for Justin: keep with the honest label, or move both to SONGGAPS until a second source turns up.

## 2. FluidR3 wording: "CC BY 3.0 US"
- index.html Credits panel link text ("CC BY 3.0" to "CC BY 3.0 US") and the code comment at the audio loader.
- NOTICE.md and audio/CREDITS.md already said CC BY 3.0 US; README does not name FluidR3 (it points to NOTICE.md). No other meta files mention it. content_lint terms ("CC BY 3.0") still match.

## 3. Copyright lines in the score SVG credits
- scores/src/credit.py: new COPYRIGHT table (Sapp 2009 for Bach, 2004-2018 Mozart, 2004-2021 Joplin; NIFC "Copyright 2017-2021 The Fryderyk Chopin Institute (https://nifc.pl)") and a "Changes made" sentence (engraved with Verovio, instrument names blanked, restyled, annotated by CJG). Both go into the `<desc>` and the RDF (`dc:rights`, `cc:attributionName`). Wording matches NOTICE.md.
- Re-ran `python3 scores/src/credit.py`: all 30 SVGs updated. Only the two credit elements change (credit.py's embed replaces the earlier block and touches nothing else). engrave.py already calls credit.embed, so re-engraving keeps it.
- Also tidied the engrave.py docstring (rec. 5).

## 4. Gotye (answer 13)
Removed the guitartabs.cc source and the "capo 5, shapes Am G F, sound Dm C B-flat" claim; song kept with the Hooktheory source (D minor, i VII). Grepped index.html, tests, NOTICE, README: no remaining reference. (Other "capo" strings are other songs, unrelated.) The entry now has one source (Hooktheory), like the two above; its sounding-chord claim (Dm alternating with C) is unchanged.

## 5. Other items in IC_R14_R18.md
- Footer "preview 0.47": not changed (release bump, someone else's area). OPEN.
- justinguitar.com Three Little Birds and Johnny B. Goode pages (rec. 4): could not be fetched (allowlist). OPEN, needs a manual look for lyrics.
- Gap cards appended after songs rather than in slot order: cosmetic, pre-existing. OPEN.

## Tests (self-run in /home/claude/wt-lic)
- content_lint: passed (56 entries, no failures).
- unit_test: 637 checks, 0 failures.
- pageerrors_test: passed (0 errors; 881 seeded random clicks, 0 errors). No browser crash, no retry needed.
