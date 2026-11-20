# C content builder report, 0.49 (C1, C2, C10, C11)

Branch `049-c-content`, worktree `/home/claude/wt/c-content`. Not pushed.

## C1: content lint
`tests/content_lint.py` and the new `tests/fixtures/us_probes.json` (35 positive and 29 negative US-term probes, 7 short-bracket positives and 5 negatives; 64 cases checked plus the short-form cases, run on every lint).
- Now caught: "8th/16th/32nd note", "two sixteenths", "quarter&nbsp;note" and U+00A0, "measure one" to "twelve", "measures 4-8", "the first/last measure of the song/piece/...", "a measure of rest/silence", "(US:half)", "(US: Half)", "(US: deceptive.)".
- No longer false positives: "In the US this is called a half cadence", "whole note-for-note copy", "an authentic Baroque sound / performance", "a deceptive appearance", "it measures 4 cm" (a unit after the number). "authentic" and "deceptive" count only in a cadence sense.
- Also added to the lint: a syllabus tag check (C10) and a song-rule check (C11: one entry per slot per chord type, approved slot order, at least one post-2015 song).

## C2: Ear Lab rhythm card
The card's own prompt now carries the first mention of bar: "one bar (US: measure)" (rungs 1 and 2) and "two bars (US: measures)" (rung 3, which is two bars). Before this the first mention sat only in the "Listening for it" box beside the card. Later mentions stay as hovers. `tests/terms_test.py` checks the prompt on rungs 1 to 3 (first mention in the prompt, none bracketed again).

## C10: syllabus tags
Outcome wording was read from the NESA outcomes pages on 20 Nov 2026 (curriculum.nsw.edu.au, Music 1, Music 2, Music Extension 11-12 (2025)) and is stored in the lint as the reference; the lint fails if a code is missing, unused, or its wording differs.

Added to SYLO and attached (a code only where the content matches the wording):
| Code | NESA wording | Attached to | Why it matches |
|---|---|---|---|
| MU2-11C-02 | "composes music with stylistic understanding of Compositional language and expressive intent" | every room that already carried MU2-12C-02 (Climbs 2, 8, 10, 11, 12, 13; Forms rhythm changes, sonata) | the Year 11 and Year 12 wording is identical |
| MU2-11L-01 | "analyses the ways Music context and Music language shape meaning in musical pieces" | Analysis | score layers (function, cadence, form) plus period and style notes |
| MU2-12L-01 | "evaluates the ways Music context and Music language shape meaning and expressive intent in musical pieces" | Analysis | was defined and unused |
| MU2-12C-01 | "evaluates and notates compositions using Music language" | Climb 2 (modal polyphony) and Climb 13 (imitation and fugue) | both have a checker that evaluates the student's notated line |
| MU1-11L-01, MU1-12L-01 | "describes / analyses the ways Music context and Music language shape music" | Analysis | same content as the Music 2 L-01 codes |
| MU1-11L-02 | "uses aural skills to identify and describe features of music" | Ear Lab | |
| MU1-12L-02 | "uses aural skills to analyse features of music" | Ear Lab | blind analysis |
| MU1-11C-01 | "uses Compositional language to create musical ideas" | Gym, Oracle, Climbs 4 and 5, Phrase form | composing tools |
| MUE-12L-01 | "analyses musical intent and effect based on score study, recordings, composer and performer commentary" | Analysis | engraved score study |

Elements: Melody (key Y) and Harmony (key H) added. Harmony added to the chord and progression rooms (Chords, Voices, Gym, Oracle, Climbs 1, 3 to 12, blues and jazz forms, sonata forms, Analysis, Ear Lab); Melody added to Keys, Climb 2, Climb 13, Phrase, Theme and variations, Ear Lab. Pitch is kept where it applied. Caveat: the NESA Stage 4 page text is flattened and some labels show "Loading", so Melody and Harmony as top-level elements is inferred from the page order (also the 0.48 cross-check's reading). Teacher check needed (register N5).

The tag-bar notes were updated: they no longer say Music 1 codes are "not listed here yet".
Not added (content does not genuinely match): MU1-11C-02 / 12C codes, MUE-12C, MU5-PER, MUE-12M/P.

## C11: songs after 2015
Search ran against Hooktheory, Wikipedia (and mirrors), Skoove, Flowkey, Guitar World, Ethan Hein, roadiemusic, The Conversation, Medium. Many pages are only fetchable once a search has returned the URL.

**Changed (1):**
- Minor triad, Australian pick: "Somebody That I Used to Know", Gotye (2011, one Hooktheory source) replaced by **"Dance Monkey", Tones and I (2019)**. Two sources for the chord claim plus one for the facts, so stronger than the entry it replaces.
  1. https://www.hooktheory.com/theorytab/view/tones-and-i/dance-monkey : F♯ minor in every section; verse v–i–VI–VII, chorus i–VI–VII–v.
  2. https://skoove.com/blog/dance-monkey : "played in the key of F# minor", progression F♯m–D–A–E.
  3. https://en.wikipedia.org/wiki/Dance_Monkey : released 10 May 2019; Tones and I is an Australian singer; lyrics about the pressure of busking (described in the note, no lyric quoted).
  The two chord sources agree on the key, on F♯m, D and E. They differ on a fourth chord (C♯m or A), so the card names only F♯m, D and E. Content note: no ⚠ tag (clean); recording listed as the original 2019 single; no clean-version advice.

**Checked and not added (could not meet two independent non-lyric sources, or unsuitable):**
- Shape of You (2017): Wikipedia mirror gives C♯m–F♯m–A–B; roadiemusic gives Am, Dm, F, G; The Conversation and Medium name no chords. Sources disagree (register N3). Hello (2015) kept.
- Waving Through a Window (Dear Evan Hansen, 2016): Hooktheory A major I6–IV–V / vi–IV–I–V; the UMB page says only "primarily in A major"; Wikipedia gives a key only for a cover. One chord source.
- Leave the Door Open (2021): Hooktheory lists seventh and eleventh chords across key changes; Wikipedia gives C major and key changes only; no second chord source.
- Blinding Lights (2019): Hooktheory only (F Dorian; ii7 appears only at phrase ends).
- Shallow (2018): Wikipedia names no key or chords.
- Augmented, maj9, madd9 and m9 lists (Ethan Hein, Guitar World, Flowkey, roadiemusic): no post-2015 example named.
- Let It Happen (Tame Impala, 2015) stays on its single Hooktheory source.

Result: 1 entry changed, 0 added. Post-2015 songs in the data: 1 (Dance Monkey 2019). Thin coverage is recorded as register row N2, with other findings N1 and N3 to N5.

## Tests (run one at a time on branch tip)
- content_lint: passed (64 US cases, 56 song entries, 21 syllabus codes over 32 rooms, 0 failures)
- unit_test: 859 checks, 0 failures
- terms_test (TERMS_FAST=1, after C2): 0 failures
- pageerrors_test: 153 views, 4,195 clicks, 881 random clicks, 0 errors
- layout_test: 272 views, 0 findings, 0 page errors
