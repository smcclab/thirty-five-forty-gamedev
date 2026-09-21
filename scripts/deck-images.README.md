# Deck figures and copyright

`deck-images.json` is the allow-list of pictures from the 2024 theory
PowerPoints that may be published on the site. It maps the SHA-256 of an image
file to `{"file": "name.png", "alt": "...", "credit": "..."}`.

**It is deliberately empty.** All 49 distinct pictures in the source decks were
reviewed on 2026-09-21 and none were cleared:

- commercial game screenshots (FIFA, Burnout, GTA, Tomb Raider, Dead Space,
  Left 4 Dead, Warcraft III, Pac-Man, Space Invaders, Bastion, Pillars of
  Eternity, Half-Life 2, StarCraft maps);
- scanned figures from the set texts — several still carry their figure
  numbers, e.g. Fullerton 8.2 "Types of playtesters appropriate for each stage
  of prototyping", Schell's interface model, the GameFlow (2005) model, the
  Bartle taxonomy, Csikszentmihalyi's flow channel, Maslow's hierarchy, interest
  curves, the iterative design cycle and the production funnel;
- stock and product photography (a petrol gauge, a thermometer, a stadium, a
  Connect 4 set, a portrait of Louis Sullivan).

These were fine in a PowerPoint behind Wattle under the educational statutory
licence. That licence does not cover a public website, which is what this repo
builds.

The converter therefore publishes none of them. Instead it writes a
```comment fence into the deck at the point each figure was used, naming the
citation it sat next to, so a future convenor can see what was there and
either re-source it, redraw it, or link to it.

To review the pictures again:

```sh
python3 scripts/convert-pptx-decks.py --review /tmp/deck-images
```

That writes every source picture (named by content hash) plus `manifest.json`
recording which deck and slide each came from and the citation beside it. To
publish one, add its hash to `deck-images.json` with real alt text and a
credit line, and re-run the converter.
