# SRCFIX 0.48: song source links (IC_LIC_048 M1, S1)

## Change (index.html)
- New `srcItem(u)` / `srcList(a)` after `esc`. A source string is split at its first URL token: the `href` is only that bare URL; everything else (the "(note)" after it, or for scale songs a "note URL" / "Label: URL (note)" form) is shown as muted plain text (`.srcnote`, 12 px, wraps, `overflow-wrap:anywhere`) after the link. Link text is the existing truncated domain+path form. A source with no URL is shown as plain text, never a link. Each source is its own block line (`.srcit`).
- Used in both renderers: chord songs (`renderSongs`) and scale songs (`renderKsSongs`). Interval song starters (`renderIvSongs`) and Ear Lab render no source links, so nothing else needed changing.
- Scale-song sources mostly begin with a label ("Hooktheory TheoryTab: https://..."), so they were never links before; they now are, with the note shown.
- S1: Gotye "Somebody That I Used to Know": `where` now ends "(as transcribed on Hooktheory)", source note now "a single community transcription, no second non-lyric source found yet", same wording as Weather With You and Let It Happen.

## Tests added
- content_lint 3b `source_links`: runs the page's own `srcItem` under node on all 172 source strings (SONGS and SCSONGS); fails if any href is not `https?://\S+`, is not the first URL token, a note longer than 30 chars is not shown, or a URL-less source becomes a link.
- unit_test SRCFIX: renders a real chord card and a scale card; hrefs contain no whitespace, Weather With You card text contains its "a single community transcription" note, scale card has `.srcnote` elements. (640 checks, was 637.)

## Results
content_lint passed (source_links: 172 rendered, 0 failures); unit_test 640 checks, 0 failures; pageerrors_test 0 errors; layout_test 162 views, 0 findings. Screenshots: /tmp/srcfix_390.png (no horizontal overflow, scrollWidth 390) and /tmp/srcfix_1440.png, Weather With You card.

## Open (not changed)
- Scale-song source https://thefretboard.co.uk/discussion/comment/1590883/favicon.ico (Flying in a Blue Dream) is a bad URL (favicon, not the thread). Data fix for Justin/builder.
- IC_LIC S2 (NEM add9 label) and S3 (17 single-Hooktheory entries labelling policy) are not in this task.
