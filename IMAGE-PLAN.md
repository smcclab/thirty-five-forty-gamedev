# Putting images back in the lecture decks

A working plan. **Delete this file when the decks reach the target.** Phases 1
and 2 are done and committed; Phase 3 is the work remaining.

## Why

The decks are generated from Penny Kyburz's 2024 theory PowerPoints. Every
picture in those slides was originally dropped for copyright reasons, which
left 294 slides of bullet points and nothing to look at. The sibling courses
sit at **0.60 images per slide** (comp1720: 345/575; comp4350: 321/529), and
that number is the target here --- it is really a statement about slide
rhythm, not about decorating existing slides: in comp1720, 321 of 344 deck
images are full-bleed image-only slides and only 23 are inline.

## Where it stands

| | Slides | Images | Per slide |
|---|---|---|---|
| Before | 294 | 0 | 0.00 |
| **Now** | 317 | 47 | **0.15** |
| Target | ~317 | ~190 | 0.60 |

Done so far:

- **Phase 1** --- 16 conceptual figures redrawn as original SVGs, plus Penny's
  own GameFlow figure published with permission. See
  `scripts/deck-images.README.md`.
- **Phase 2** --- the 24 commercial game screenshots published under fair
  dealing, each credited. See "The game screenshots" in `MATERIALS.md`.

Per-deck state (`grep -c '!\[' src/decks/*.deck.mdx` to recheck):

| Deck | Slides | Images |
|---|---|---|
| week01-1-play-and-games | 12 | **0** |
| week01-2-formal-elements | 17 | 1 |
| week02-1-playcentric-design-process | 17 | 1 |
| week02-2-idea-generation | 11 | **0** |
| week02-3-prototyping | 15 | **0** |
| week03-1-engaging-the-player | 20 | 6 |
| week03-2-designing-to-engage | 18 | 1 |
| week03-3-flow-needs-motivation | 20 | 4 |
| week04-1-systems | 13 | 2 |
| week04-2-mechanics | 21 | 2 |
| week04-3-balance | 20 | 2 |
| week05-1-interface-design | 24 | 3 |
| week05-2-level-design | 21 | 20 |
| week07-1-agile-game-dev | 7 | **0** |
| week08-1-learning-and-training | 22 | 1 |
| week08-2-challenge-difficulty-pacing | 22 | 3 |
| week09-1-playtesting-process | 19 | 1 |
| week09-2-conducting-playtesting | 18 | **0** |

**Do the five zero-image decks first** (Charles's call, 2026-09-22): a deck at
zero reads as unfinished in a way a thin deck does not.

## Task 1 (blocking): a way to *add* an image

`scripts/deck-images.json` is keyed by the SHA-256 of a picture in the source
PowerPoint, so it can only ever *replace* something that was already there.
Phase 3 is mostly about adding images to slides that never had one, and there
is no mechanism for that yet. Build it first.

Proposed shape --- `scripts/deck-extras.json`, read by
`scripts/convert-pptx-decks.py`:

```json
{
  "week02-3-prototyping": [
    { "after_source_slide": 5,
      "file": "photos/paper-grid-prototype.jpg",
      "alt": "A paper grid prototype with counters laid out on a desk.",
      "credit": "COMP3540 workshop, 2024",
      "layout": "bg cover",
      "caption": "Paper first: the cheapest way to find out a rule does not work." }
  ]
}
```

Notes on the design:

- **Anchor on the source slide number, not the output slide number.** The
  source PowerPoints never change, so `after_source_slide` is stable; output
  slide numbers shift every time a figure is added.
- `layout` is `bg cover` (full-bleed photo), `bg contain` (fits the whole
  image, for diagrams and screenshots) or `inline` (into the existing
  `.slide-media` row on that slide rather than a new slide). Default to
  `bg cover` for photographs: that is the comp1720/comp4350 idiom and the one
  that fixes "boring".
- A full-bleed slide still needs `alt`; astromotion's deck checker has a
  `bg-missing-image` rule and `pnpm build` fails on axe's `image-alt`.
- Emit a new slide after the anchor, the same way the `figure` kind already
  does --- see the `for entry in slide_figures:` block in `convert()`.
- Files resolve relative to `src/decks/` (so `photos/...` can point at a new
  `src/decks/photos/` directory, and `media/...` at the existing one).

## Tasks 2-6: the five empty decks

Read the deck before working on it; the headings below are the current ones.
The 2023 PowerPoints in `../comp3540-materials/2023/Lectures/` are the best
guide to **where Penny wanted pictures** --- she illustrated far more heavily
in 2023 (168 distinct pictures over 731 slides) than in the 2024 rework (64).
Use them as a brief, not as a source of files: the same copyright rules apply.

### week02-3-prototyping (15 slides, needs ~9) --- START HERE

The easiest win on the site. `src/assets/images/photos/` already holds **29
photographs of COMP3540 students prototyping** --- paper grids, counters,
clay, pipe cleaners, storyboards --- cropped, EXIF-stripped and with no
identifiable faces. They are currently used only as page heroes, one each. They
are exactly what this deck is about.

Directly relevant: `paper-grid-prototype`, `prototyping-materials`,
`hands-prototyping`, `sticks-and-counters`, `circles-and-sticks`,
`maze-prototype`, `striped-prototype`, `path-prototype`, `clay-creature`,
`pipecleaner-tangle`, `storyboard-sketches`, `terrain-cutouts`,
`block-layout`, `counters-and-book`.

Slides to illustrate: Physical Prototypes, Prototyping your game idea (x2),
2. Structure, 3. Formal details, 4. Refinement, Types of digital prototypes
(x2). Credit line: `COMP3540 workshop, 2024`.

`student-game-portal.jpg` is the one photo currently unused anywhere.
There are also ~11 more frames in `2024/WW4-Photos` not yet cropped --- same
rule, no identifiable faces, and **never** `IMG_9501`.

### week09-2-conducting-playtesting (18 slides, needs ~11)

Six consecutive slides all headed "Conducting a Playtesting Session", then
Methods, A Primer, Taking Notes, Usability Techniques, Data Gathering,
Control Situations, Lens of Playtesting.

Mostly process, so mostly authored diagrams: a session timeline (brief ->
play -> observe -> debrief), a seating/observation layout, a quantitative vs
qualitative split, a note-taking template. `playtesting-hands.jpg` and
`workshop-desk.jpg` fit the session slides. Unsplash for the observation and
note-taking slides.

### week01-1-play-and-games (12 slides, needs ~7)

What is play / types of play / what is a game / game experience. The most
photographic deck of the five: children and animals playing, board games,
playgrounds, sport --- all well served by Unsplash. 2023 Lecture 1 is the
richest source deck (76 slides, 60 pictures) and shows what Penny used,
including a "20 published games" spread.

Note this deck already links a YouTube video on the first content slide
(Promise of Play); a still is not needed.

### week02-2-idea-generation (11 slides, needs ~7)

Brainstorming, Alternative Methods, Brainstorming Tips, Editing and Refining,
Narrowing the list, Choosing an Idea, Turning ideas into a game.

Unsplash territory --- sticky notes, whiteboards, sketchbooks, group work ---
plus one or two authored diagrams (a diverge/converge double diamond for
narrowing the list; a simple funnel for editing and refining). The workshop
photos `annotated-design`, `design-diagram`, `mechanics-worksheet` and
`spec-worksheet` also fit.

### week07-1-agile-game-dev (7 slides, needs ~4)

The thinnest deck on the site. The Agile Manifesto poster was dropped as a
third-party infographic, but **the four value statements and the twelve
principles are freely reproducible from agilemanifesto.org with its notice** ---
set them as text, not an image.

Authored diagrams: the sprint/iteration cycle, a burndown chart, a release
train or milestone plan for "Agile Project Planning". `scripts/make-deck-figures.py`
already has the Graphviz and matplotlib helpers for both.

## Conventions

**Authored diagrams** go in `scripts/make-deck-figures.py` and land in
`src/decks/figures/`. Read the "Drawing a replacement" and "Checking the
result" sections of `scripts/deck-images.README.md` first. Run
`python3 scripts/make-deck-figures.py --check` --- it enforces palette,
4.5:1 contrast on the deck background, a 16 css px minimum label size at the
rendered size, and the alt/credit rules. Note that a figure drawn for a slide
that never had a picture has no source SHA, so its `alt`/`credit`/`terms`
metadata needs to live in `deck-extras.json` rather than `deck-images.json`;
teach `--check` to read both.

**Unsplash photographs** follow the comp1720 convention: the file is named
`<photographer-name>-<unsplash-id>-unsplash.jpg`, so attribution survives in
the filename (65 of comp1720's 345 deck images are Unsplash, all named this
way). Keep the `credit` field as `Photo by <name> on Unsplash`. Unsplash's
licence does not require attribution but crediting is right and matches the
other courses. Download at a sensible width --- these are backgrounds, 2000px
is plenty --- and put them in `src/decks/photos/`.

**Workshop photographs** are credited `COMP3540 workshop, 2024`.

**Alt text** states what the image shows and why it is there, not its
composition. Under ~150 characters. It is not optional: the build fails
without it.

**Never** hand-edit a deck. Change the converter or the JSON and re-run
`python3 scripts/convert-pptx-decks.py`.

## Checking

```sh
python3 scripts/convert-pptx-decks.py     # regenerate all 18 decks
python3 scripts/make-deck-figures.py      # redraw the SVGs
python3 scripts/make-deck-figures.py --check
pnpm build                                # the real gate: axe, links, deck structure
```

To re-measure:

```sh
python3 - <<'PY'
import re, pathlib
ts = ti = 0
for f in sorted(pathlib.Path("src/decks").glob("*.deck.mdx")):
    t = f.read_text().split("---", 2)[2]
    s = len([x for x in re.split(r'(?m)^---\s*$', t) if x.strip()])
    i = len(re.findall(r'!\[[^\]]*\]\(', t))
    print(f"{i/s:5.2f}  {i:3d}/{s:3d}  {f.name}")
    ts += s; ti += i
print(f"TOTAL {ti}/{ts} = {ti/ts:.2f} per slide")
PY
```

## Decisions already made --- do not re-litigate

- **Commercial game screenshots are published** under fair dealing, credited
  to game/developer/year. Where the file came from does not change the
  analysis, and substituting open-licensed games was considered and rejected:
  students recognising the game is the point.
- **Microsoft PowerPoint stock icons are omitted entirely** (374 of them).
  Not replaced with an open icon set; they were decorative filler at 1x1 inch.
- **Textbook figures are redrawn, never reproduced**, and credited to the
  primary source ("Redrawn after Csikszentmihalyi (1990); see Schell ch. 11").
- **Figures get their own slide**, because a figure beside a bullet list is
  capped at 30vh and its labels cannot be read from the back of a theatre.

## Loose ends worth picking up

- **A converter bug in `week05-2-level-design`.** Every slide is headed
  `"Theory: Level Design Rudolf Kremers. (2009) ... Richard Rouse III (2005)"`
  --- the sidebar label and the full citation have been promoted to `##`, and
  the real headings (*Level Separation*, *Components of a Level: Puzzles*) are
  stranded as the first body bullet. Fix in the converter.
- **The Poll Everywhere prompts.** The 2023 decks carry ~70 live-poll slides
  whose questions are real teaching content --- "What is a system?", "What
  engages you in a game?", "What makes a control scheme good or bad for you?"
  They are the interactive spine of the lectures and are missing from the 2024
  decks. Not images, but the other thing these decks lack.
- **Three pictures flagged in `deck-images.json`**: an unidentified
  ruined-city concept painting (ask Penny), a stock stadium photograph (any
  freely-licensed one), and a grid of ~20 arcade screens used to show
  viewpoints, better rebuilt than re-sourced. The Tomb Raider and FIFA
  editions are unconfirmed.
- **Watermarked screenshots.** Several published files carry a third-party
  site's watermark (IGN, eurogamer.gr, GameSpot). `kind: "photo"` exists to
  swap in a cleaner capture from `src/decks/media/` one entry at a time.
