# Notice: third-party sources and licences

The Composition Jungle Gym is for non-commercial educational use. Some of the score data is licensed CC BY-NC-SA 4.0, so the app as a whole is non-commercial.

© Justin Ossher.

## Scores (Analysis room)

Each score in `scores/` is an SVG engraved from a Humdrum encoding, with timing, cadence and form annotations in `scores/meta.json`.

**Bach chorales**
- 370 Bach chorales, Humdrum encodings by Craig Stuart Sapp. Copyright (C) 2009 Craig Stuart Sapp.
- https://github.com/craigsapp/bach-370-chorales
- Licence: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**Mozart piano sonatas**
- Mozart piano sonatas, Humdrum encodings by Craig Stuart Sapp, from the Alte Mozart-Ausgabe (1878). Copyright (C) 2004-2018 Craig Stuart Sapp.
- https://github.com/craigsapp/mozart-piano-sonatas
- Licence: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**Joplin rags**
- Scott Joplin edition, Humdrum encodings by Craig Stuart Sapp. Copyright (C) 2004-2021 Craig Stuart Sapp.
- https://github.com/craigsapp/joplin
- Licence: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)

**Chopin, Preludes Op. 28 Nos. 7 and 20**
- First Editions of Fryderyk Chopin's Music
- Copyright 2017-2021 The Fryderyk Chopin Institute (https://nifc.pl)
- https://chopinscores.org
- Chopin first editions in Humdrum, Breitkopf & Härtel first edition (Leipzig, 1839): https://github.com/pl-wnifc/humdrum-chopin-first-editions
- Licence: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

**Changes made.** The Composition Jungle Gym converted the encodings and engraved them to SVG with Verovio, and added timing, cadence and form annotations.

**ShareAlike.** The score images (`scores/*.svg`) and the analysis data in `scores/meta.json` are derived from these encodings and are shared under the licence of their source: CC BY-NC-SA 4.0 for the Bach, Mozart and Joplin scores (including their annotations), and CC BY 4.0 for the NIFC Chopin scores (including their annotations). Verovio (LGPL) is only the engraving tool; it does not set the licence of the output.

## Hand signs

- Curwen hand-sign drawings: © 2003 Kodály Music Education Institute of Australia (KMEIA), used with permission; permission confirmed by Justin Ossher (project decision log L43, 18 Nov 2026).

## Sound (`audio/`)

| Material | Creator and source | Licence |
|---|---|---|
| Piano samples (Steinway B) | Versilian Community Sample Library (VCSL), https://github.com/sgossner/VCSL | [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/) |
| Guitar (steel and nylon) and bass samples | FluidR3_GM soundfont by Frank Wen, rendered per note by midi-js-soundfonts (Benjamin Gleitzman), https://github.com/gleitz/midi-js-soundfonts | [CC BY 3.0 US](https://creativecommons.org/licenses/by/3.0/us/) |

**Changes made.** The samples were trimmed, re-encoded and levelled; details and the range shipped are in `audio/CREDITS.md`.

## Software and fonts

| Material | Source | Licence |
|---|---|---|
| VexFlow 4.2.3 (music notation) | Loaded from jsDelivr | MIT |
| Bravura music font (VexFlow's default, used by the app) | Steinberg Media Technologies, bundled in VexFlow | SIL Open Font Licence 1.1 |
| Leipzig music font (outlines embedded in the score SVGs) | Verovio | SIL Open Font Licence 1.1 |
| Outfit and Poiret One (fonts) | Google Fonts | SIL Open Font Licence 1.1 |
| Verovio (engraving tool) | https://www.verovio.org | LGPL |

The VexFlow 4.2.3 build also bundles the Petaluma, Gonville and Leland music fonts. The app does not select them; their individual licences were not checked here and are not relied on.

## Where credits appear

The credits are on screen in the app: open **Credits** in the footer.
