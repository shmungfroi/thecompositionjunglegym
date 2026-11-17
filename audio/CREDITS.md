# Sound credits

The Composition Jungle Gym plays these recorded samples. Every file was checked for pitch (all within 9 cents of their note, piano within 27 cents at the very top, which is normal stretch tuning) and levelled so the instruments sit at the same loudness.

| Folder | Instrument | Source | Licence |
|---|---|---|---|
| `piano/` | Steinway B grand piano, no sustain pedal, close microphones, middle velocity, every second semitone C2–A♯7 (G♯7 dropped: 76 cents flat) | Versilian Community Sample Library (VCSL), https://github.com/sgossner/VCSL | CC0 1.0 (public domain dedication) |
| `guitar-steel/` | Steel-string acoustic guitar, E2–E6, every semitone | FluidR3_GM soundfont by Frank Wen, rendered per note by midi-js-soundfonts (Benjamin Gleitzman), https://github.com/gleitz/midi-js-soundfonts | Creative Commons Attribution 3.0 |
| `guitar-nylon/` | Nylon-string guitar, E2–C7, every semitone (also used for the ukulele) | as above | Creative Commons Attribution 3.0 |
| `bass/` | Electric bass, finger style, E1–G4, every semitone | as above | Creative Commons Attribution 3.0 |

Processing: piano trimmed to 4.6 s with a 1 s fade and encoded at 128 kbps; guitar and bass re-encoded at 64 kbps; every file levelled with ffmpeg. Files are named by MIDI note number (60 = middle C).

If the samples can't load (the page opened from a file, or offline), the app falls back to its built-in synthesiser.
