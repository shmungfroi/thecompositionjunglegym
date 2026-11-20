# ISSFIX 049: checker-row chips and score numerals (regression of 0.48)

Branch 049-issfix, from origin/049 (cd69362). All checks below are labelled "self-check": run by the builder, not independently verified.

## Defects (Must, regression of approved work)
1. Checker rows (.iss): the "strict SATB" chip printed over the message text, and the terms glosser's "(US: half step)" wrapped one word per line and floated above the row.
2. Roman numerals under the Voices score were cut off at the bottom edge of the score frame.

## Cause (verified)
1. CSS `.iss span{display:inline-block;width:18px;...}` was meant for the one-character icon, but matched every span inside .iss: the `.c2src` tradition chip, the `.tmus` term-gloss span, and the `.c2src` tags in forms checkers (at old code: "classical" box 18 px, text 43 px).
2. drawSATB reserved `bottom=20+14/k` below the staff; the numeral row (baseline lo+15+4/k plus glyph descent) overshot the SVG by 4 to 5 px at every width, and `.sframe` clips (overflow-y:hidden).

## Fix
- The icon span now has its own class: all 13 icon spans in .iss rows carry `class="ic"`, and the rule is `.iss span.ic{...}`. Chips and glosses lay out normally. Icon look unchanged. Rows covered: Voices (satbCheck and the "can't be spelled" row), secondary-dominant and swap checkers, climb 4 and Gym guide-tone/ii-V notes, Keys mic-fail rows. Rows without an icon (forms/blues/ragtime checkers with `.c2src` tags) are fixed by the same rule change.
- drawSATB bottom reserve raised to `20+28/k` (14 px more room); numerals are fully inside the frame, no sideways scroll.

## Regression check (tests/layout_test.py)
New `ISSQ` check runs in every view of the existing sweep (1440/1366/1024/390) plus a dedicated view "voice/iss-rows" (Stage 6, B flat, Imaj7 viiø7 vi7 vi7 iii7 ii7 viiø7 vi7), which also fails if no checker rows render. It reports: text overlapping another text box in the same .iss row; a span in .iss narrower than its own text; a score numeral (text.rnl) outside its SVG frame.
- On old code (origin/049 index.html, new test): 276 views, 58 with findings (numerals outside the frame in Voices and climbs, "classical" chip squeezed 18 vs 43 px in forms rows). self-check
- On new code: 276 views, 0 findings. self-check

## Suites on the fixed code (self-check)
- layout_test: 276 views, 0 with findings, 0 page errors
- pageerrors_test: n_errors 0 (881 random clicks, 0 errors)
- terms_test: 153 views scanned, n_failures 0
- content_lint: passed
- unit_test: 959 checks, 0 failures

## Before/after PNGs (Voices, that progression)
tests/reports/issfix_049/png/before_{1920,1366,1024,390}.png and after_{1920,1366,1024,390}.png (headless Chrome, staff plus checker rows). Measured numeral bottom vs SVG bottom, before: 1920 vs 1915 (1920 px wide), 1944 vs 1939 (1366), 2486 vs 2481 (1024), 3454 vs 3450 (390, second system); after: all inside by 9 px. self-check
