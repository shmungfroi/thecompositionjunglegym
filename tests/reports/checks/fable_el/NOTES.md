# Fable's working notes — Ear Lab 0.48 review

Scripts (all read the repo through tests/harness/cjg.py; nothing in the repo was edited):
- shots.py   seven drills idle / ready / playing / answered wrong / answered ok at 1440, 1024, 390; metre rungs 1 and 3; rhythm rungs 1-3 answering and checked; count-in; cadence rung 3 Nearly (both kinds), 6/4 correct, Phrygian wrong; Reset confirm and undo; Stage 4 strip; phone dock (ready / playing / answered) for four drills; key line; Keys tallies. Measurements in metrics.json.
- shots2.py  bass and melody through real clicks; 1366x768 fold; Tab order with a shot per control type; focus after answering; Esc / Space; variant sounding; reduced motion. Measurements in metrics2.json.
- m3.py-m8.py  phone header under four tallies; two header proposals; rung 3 metre cards (5/4, 7/8, 12/8); melody result fix; Keys cards with low / high / empty tallies; foot confirm; strip at Stage 4 and 5.
- cmp_*.png, crop_*.png are side-by-side or cropped comparisons; proposal_*.png are the build with my suggested CSS injected at run time.

Caveats
- Full-page captures at 390 show the tab bar and dock part-way down the image. That is how a full-page capture draws fixed elements; use the *_view.png files for the dock.
- bass_*/mel_* answered states in shots.py failed (my script built an invalid answer); the valid ones are from shots2.py.
- metre_r3_78_wrong128_*.png is mislabelled: the question drawn was 2/4. The 5/4, 7/8 and 12/8 answered cards are metre_r3_54/78/128_card_*.png.
- Headless Chrome only; no real phone, no iOS safe area.

Phone header, title lines (title box width / tally width, px), built:
  0 of 1: Pulse 2 lines (162/154), Rhythm 2, Chord 1, Bass 2, Melodic 2, Blind 1
  11 of 15, streak 3: Pulse 1 (171/145), Rhythm 1, Bass 2, Melodic 2
  40 of 48, streak 12: every title 2 lines (122/194) except Cadences
With the stacked tally (FR-5): all 1 line up to 40 of 48 except Bass and numerals (2, balanced).

Fold at 1366x768, bottom of the last answer control: metre r2 833, quality r3 754, cadences r3 801, rhythm r3 931.
Keys mode buttons at 390: 84x44 and 68x44 with "5 of 8"; 58x76 and 53x76 with "40 of 48".
Key line at 390: two lines, 37.5 px, breaks inside "Interrupted = US deceptive".
Dock: 366x64 at left 12, top 712 (bottom 68 above the tab bar); toggle 56; Check / Next 77x48; .tstop hidden.
