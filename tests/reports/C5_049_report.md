# 0.49 C5 report (carried Shoulds)

Implemented as specified in `tests/reports/fable_049/DESIGN_049.md` (C5) and `c5.css`: the CSS block is appended unchanged at the end of the main `<style>`; the one markup change is the search placeholder, now `Type a chord: Bm7, E♭9…`. No behaviour change. C6 and the ladder UI are not touched.

## Measurements (own run, `c5_verify.py` adapted to compare HEAD against the worktree; no page errors at any size)

| Check | 1440 | 1366x768 | 1024 | 390 |
|---|---|---|---|---|
| C5-1 header, empty to counted (all 4 drills), before | 97 to 97 | 97 to 97 | 97 to 97 | 104 to 122 |
| after | 97 to 97 | 97 to 97 | 97 to 97 | 122 to 122 |
| C5-2 Keys checkbox box, before / after | 13 native / 18 drawn | same | same | same |
| C5-2 Keys tick label row at 390 | | | | 44 (was 19) |
| C5-3 Keys tally left edge at 40 of 48, before / after | 1179 / 1179 | 1105 / 1105 | 551 / 763 | own row, unchanged |
| C5-4 song-starter link, before / after | blue underline 20 / ivory pill 26 | same | same | 20 / 44 |
| C5-5 Keys controls under 44 px at 390 | | | | 49 to 0 |
| C5-5 Keys gym header height at 390 | | | | 76 to 92 |
| C5-6 chord search input width, before / after | 354 / 354 | 334 / 334 | 32 / 206 | 300 / 300 |

All figures match Fable's tables. No horizontal overflow at any size.

## Tests

| Test | Result |
|---|---|
| layout_test | 272 views, 0 with findings, 0 page errors |
| pageerrors_test | 0 errors (881 random clicks, 0 errors) |
| transport_test | 0 fails, 0 page errors |
| content_lint | passed |

Note: the machine was busy with other agents; pageerrors_test and transport_test needed longer than 10 minutes each.
