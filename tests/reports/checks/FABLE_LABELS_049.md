# Fable design check: song card labels (L106), 0.49

Reviewed: commit 438849d on 049-songs (built by Sonnet). Reviewer did not build it.
Looked at: the four PNGs in tests/reports/songs_049/png/, the index.html diff, the chip CSS (`.song .lw`, `.song .lw.th`), `warnTags()`, and the genre-line CSS (`.song .gt`).

## Verdict: CHANGES (made in this commit). With them, SIGN OFF.

## What was wrong with 438849d

1. **It reads as a content warning.** The label was rendered as `<span class="lw th">`, which is the ⚠ Themes chip exactly: same amber text (#d9b46a), same amber outline (#a9853a), same pill, same caps. Only the ⚠ glyph was missing. On these cards the amber outlined pill has one meaning: "content note, prepare students". A teacher scanning the list would take "FILM MUSICAL" and "MAJOR CHORDS IN A MINOR-KEY SONG" for cautions about the song. It also weakens the real warnings, because the pill stops being a reliable signal. The class name itself (`lw`, the language-warning chip) says the component was built for warnings.
2. **The pill broke across lines at both widths.** The song column is only 374 px wide at 1366, so the long label wrapped there too, not just at 390. An inline pill that wraps is drawn as two open fragments (first line with no right edge, second with no left edge). That looks like a rendering fault, not a design.
3. **Hierarchy.** A whole sentence in letter-spaced capitals inside an outline was the loudest thing in the genre line, louder than the slot name it qualifies and competing with the song title below.
4. **Consistency.** The other non-warning qualifiers on these cards are plain text: "· Australian/NZ" in the genre line, "Artist · year", and the single-source wording ("as transcribed on Hooktheory") in the body. No informational item on a song card was a pill before this. The `title` tooltip repeated the visible text and added nothing.

What was fine: 11 px floor held, no sideways scroll, no page errors, contrast adequate, lint rule (1 to 40 characters) sensible and kept.

## The change

Markup, in `renderSongs()`: the label moves next to the slot it qualifies, before the star and any warning chips, joined by the same middot the card already uses.

    ${esc(x.slot)}${aus}${x.label?`&nbsp;· <span class="nb">${esc(x.label)}</span>`:''}${x.prime?...}${warnTags(x)}

(the non-breaking space is a literal U+00A0 in the source, so a line can never start with the dot)

CSS, one new rule after `.song .gt .st`:

    .song .gt .nb{color:var(--ivory);font-weight:400;letter-spacing:.4px;text-transform:none}

No border, no pill, no amber, no tooltip. Sentence case in ivory against the gold caps of the slot, so it reads as a quiet note on the slot: "MUSICAL THEATRE · Film musical", "AUSTRALIAN PICK · Major chords in a minor-key song". Nothing in `.lw` or `.lw.th` changed; warning chips are untouched and are now again the only pills in the genre line.

`render_cards.py` now measures `.gt .nb` and also reports whether any warning-styled element is present on the card (`warnStyled`).

## Checks after the change

| | 1366 | 390 |
|---|---|---|
| Dance Monkey label font | 11 px | 11 px |
| Bruno label font | 11 px | 11 px |
| Smallest font in genre line | 11 px | 11 px |
| Warning-styled element on card | none | none |
| Sideways scroll | none (doc 1366 = window) | none (doc 390 = window) |
| Genre line | one line | one line |
| Page errors | none | none |

- Wrap: both labels now sit on one line at both widths (the 390 card is 316 px wide; the long label fits with a few px to spare). If a future label is longer it wraps as ordinary text, which is acceptable; nothing can break the way the pill did.
- Contrast: ivory #ece2c8 on the panel #12100b is about 14:1; the gold slot text is unchanged.
- Crafted look: reads like a typeset credit line, the same grammar as "Tones and I · 2019" beneath it. No decoration added.
- tests/content_lint.py: passed. tests/layout_test.py: 272 views, 0 findings, 0 page errors.
- unit_test and pageerrors_test not re-run (one template string and one CSS rule changed; the render script loaded both cards with no page errors).

## Left open (not blocking)

- With a 2 px letter-spaced slot, the gap either side of the middot is slightly uneven (about 2 px wider on the left). Visible only when looked for; I left it rather than add markup for it.
- The "Card labels (L106)" paragraph in tests/reports/C18_C20_049_report.md still describes the chip. This file supersedes it; a pointer line has been added there.
- A card that has a label, the star and two warning chips at once does not exist yet. When one does, render it at 390 before shipping.
- Justin asked for a "visible label". This is visible but deliberately quiet. If he wants it stronger, the right move is weight 600 on `.nb`, not a return to the pill.
