# Putting images back in the lecture decks

A working plan. **Delete this file when the decks reach the target.** Phases 1
and 2 are done and committed; in Phase 3 the mechanism for adding an image is
built and **no deck is at zero any more**. What is left is the thin decks ---
and, first, a formatting pass (see the end of this file).

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
| After the image pass | 359 | 89 | 0.25 |
| **Now** (after the formatting pass) | 521 | 136 | **0.26** |
| Target | ~520 | ~310 | 0.60 |

Done so far:

- **Phase 1** --- 16 conceptual figures redrawn as original SVGs, plus Penny's
  own GameFlow figure published with permission. See
  `scripts/deck-images.README.md`.
- **Phase 2** --- the 24 commercial game screenshots published under fair
  dealing, each credited. See "The game screenshots" in `MATERIALS.md`.
- **Phase 3, task 1** --- `scripts/deck-extras.json` adds an image to a slide
  that never had one. See "Adding an image" below.
- **Phase 3, the five decks that were at zero** --- 42 images added:
  week02-3-prototyping (10 workshop photographs), week01-1-play-and-games
  (10 Unsplash), week02-2-idea-generation (3 Unsplash, 3 workshop, 2
  figures), week09-2-conducting-playtesting (5 Unsplash, 2 workshop, 3
  figures) and week07-1-agile-game-dev (2 Unsplash, 2 figures, plus the
  twelve Agile principles as a table instead of the dropped poster).
  `scripts/fetch-deck-photos.py` finds and downloads the Unsplash ones.

Per-deck state after the formatting pass (2026-09-23). "Pictures" counts
slides that carry one, as a share of the slides between the title and the
closing slide; "run" is the longest stretch of consecutive bullet-only slides,
which the rulebook caps at three.

| Deck | Slides | Images | Pictures | Splits | Bullet-only | Longest run |
|---|---|---|---|---|---|---|
| week01-1-play-and-games | 23 | 10 | 10 (48%) | 4 | 11 (52%) | 3 |
| week01-2-formal-elements | 28 | 5 | 5 (**19%**) | 4 | 21 (81%) | 9 |
| week02-1-playcentric-design-process | 29 | 5 | 5 (**19%**) | 4 | 22 (81%) | 7 |
| week02-2-idea-generation | 24 | 8 | 8 (36%) | 4 | 14 (64%) | 4 |
| week02-3-prototyping | 31 | 10 | 10 (34%) | 4 | 19 (66%) | 5 |
| week03-1-engaging-the-player | 30 | 6 | 6 (**21%**) | 3 | 22 (79%) | 7 |
| week03-2-designing-to-engage | 31 | 4 | 4 (**14%**) | 3 | 25 (86%) | **13** |
| week03-3-flow-needs-motivation | 29 | 8 | 8 (30%) | 4 | 19 (70%) | 6 |
| week04-1-systems | 22 | 6 | 6 (30%) | 4 | 14 (70%) | 5 |
| week04-2-mechanics | 35 | 6 | 6 (**18%**) | 4 | 27 (82%) | **11** |
| week04-3-balance | 33 | 6 | 6 (**19%**) | 4 | 24 (77%) | 7 |
| week05-1-interface-design | 43 | 7 | 7 (**17%**) | 4 | 34 (83%) | 8 |
| week05-2-level-design | 36 | 23 | 14 (41%) | 3 | 20 (59%) | 3 |
| week07-1-agile-game-dev | 8 | 4 | 4 (67%) | 1 | 2 (33%) | 2 |
| week08-1-learning-and-training | 29 | 5 | 5 (**19%**) | 4 | 22 (81%) | **12** |
| week08-2-challenge-difficulty-pacing | 25 | 6 | 6 (26%) | 4 | 17 (74%) | 5 |
| week09-1-playtesting-process | 28 | 7 | 7 (27%) | 6 | 19 (73%) | 5 |
| week09-2-conducting-playtesting | 37 | 10 | 10 (29%) | 3 | 25 (71%) | 3 |

521 slides, 136 images, **0.26 images per slide**. Recheck with:

```sh
grep -c '!\[' src/decks/*.deck.mdx
```

**The five zero-image decks came first** (Charles's call, 2026-09-22): a deck
at zero reads as unfinished in a way a thin deck does not. All five are done.

**What the formatting pass changed about this plan.** Splitting the dense
slides took the decks from 359 to 521, so the same 136 images now cover half
again as many slides: every deck gained pictures in absolute terms and most
lost ground as a proportion. Eight decks are under the 25% picture floor and
every deck but three breaks the three-in-a-row rule --- `week03-2` runs
thirteen bullet-only slides together, `week08-1` twelve, `week04-2` eleven.
Those runs, not the ratio, are the thing to fix, and they are all in
`deck-extras.json`: **each of the eighteen decks now has a list of places a
full-bleed photograph would land**, written into the per-deck reports of the
pass. The bolded cells are where to start.

## Adding an image (task 1 --- done)

`scripts/deck-images.json` is keyed by the SHA-256 of a picture in the source
PowerPoint, so it can only ever *replace* something that was already there.
`scripts/deck-extras.json` is the other half: it *adds* an image to a slide,
and `scripts/convert-pptx-decks.py` reads both.

```json
{
  "week02-3-prototyping": [
    { "after_source_slide": 6,
      "file": "photos/paper-grid-prototype.jpg",
      "layout": "bg cover",
      "alt": "Coloured buttons and foam triangles on a grid drawn in pencil.",
      "caption": "A grid, some buttons, a legend down the side: enough to play a turn and find out whether the rule works.",
      "credit": "COMP3540 workshop, 2024" }
  ]
}
```

- **The anchor is the source slide number**, not the output slide number: the
  PowerPoints never change, while output numbers shift every time a figure is
  added ahead of them. Print the source numbering with the snippet under
  "Checking". An anchor on a slide that carries no content (the title slide,
  the closing slide) is an error rather than a silently dropped image, and so
  is a deck name that does not exist, a missing file, a missing `alt` or an
  unknown `layout`.
- `layout` is `bg cover` (a new full-bleed slide, the default), `bg contain`
  (a new slide fitting the whole image, for diagrams and screenshots) or
  `inline` (into the anchor slide's existing `.slide-media` row). Default to
  `bg cover` for photographs: that is the comp1720/comp4350 idiom and the one
  that fixes "boring".
- A `bg` slide uses the **theme's own `hero` class**, which lays the caption
  out bottom-left and paints a scrim between photograph and text (as an image
  rather than a gradient, so the PDF export keeps it). `caption` is the
  teaching line; `credit` sits under it.
- A background image is a CSS background, so no element carries its `alt`.
  The converter writes the `alt` into a visually hidden paragraph instead
  (`.deck-sr-only` in `src/decks/theme.css`), which is why `alt` is required
  whatever the layout.
- `file` resolves under `src/decks/`, so `photos/...` (photography, new) and
  `figures/...` (redrawings) both work. It has to live there: only
  `src/decks/` is copied into `dist/`, so a deck cannot reference
  `src/assets/`.
- A deck with no publishable source picture takes its card hero on
  `/lectures/` from its first added image.

## What went into the five decks

Recorded so the reasoning survives; the entries themselves are in
`scripts/deck-extras.json`.

### week02-3-prototyping (25 slides, 10 images)

Ten workshop photographs, one full-bleed slide each, anchored on source slides
3 and 6-14: the materials, the paper grid, the core-mechanic sticks and
counters, one per stage of Fullerton's build (foundation, structure, formal
details, refinement) and three on the move to digital.

### week01-1-play-and-games (22 slides, 10 images)

All Unsplash, and the most straightforwardly photographic deck on the site:
children running for "what is play", a dog with an oversized stick for playful
animals, then **one photograph per Caillois type** on the types-of-play slide
--- runners (agon), falling dice (alea), carnival masks (mimicry), a spinning
carousel (ilinx) --- a board game seen from above for play-with-structure, two
chess knights for the formal definition, players reaching over a board for the
magic circle, and a laid dinner table before the guests arrive for Fullerton's
party-host analogy, which is the best single image in the set.

### week02-2-idea-generation (19 slides, 8 images)

Three Unsplash (a wall of sticky notes, a desk of sketches and a connected
diagram, someone pinning sketches to a wall), two new figures
(`idea-filters`, `narrowing-the-list`) for editing and narrowing, and three
workshop photographs for choosing an idea and turning it into one
(`annotated-design`, `spec-worksheet`, `design-diagram`).

### week09-2-conducting-playtesting (28 slides, 10 images)

Mostly process, so mostly figures: `playtest-observation` (who sits where),
`playtest-session` (the test script as a timeline) and `playtest-notes` (the
three parts of Fullerton's form, which is the figure that was dropped as too
substantial an excerpt --- this is its structure, not her questions).
Photographs for the rest: a recorded play session, a post-play conversation,
friends on a couch for group testing, a clipboard for note-taking, an
analytics dashboard for the quantitative slide, and two workshop shots.

### week07-1-agile-game-dev (11 slides, 4 images)

Two figures (`sprint-cycle`, `burndown`), a backlog wall and a standup. The
Agile Manifesto poster stays dropped, but the **twelve principles are now a
two-column table** (`scripts/deck-snippets/agile-principles.md`, paraphrased
and linked to agilemanifesto.org) on the slide where the poster was --- that
closes the loose end the deck comment recorded.

## What is left

- **The thin decks**, bolded in the table above. `week08-1-learning-and-training`
  (one image over 22 slides) is the worst; `week01-2-formal-elements`,
  `week02-1-playcentric-design-process`, `week03-2-designing-to-engage` and
  `week09-1-playtesting-process` are next.
- **Unused workshop photographs**: `circles-and-sticks`, `counters-and-book`,
  `pipecleaner-tangle`, `mechanics-worksheet`, `interface-sketch`,
  `stick-maze-level`, `grid-figure`, `teal-board-figure`,
  `student-game-portal`. There are also ~11 more frames in
  `2024/WW4-Photos` not yet cropped --- same rule, no identifiable faces, and
  **never** `IMG_9501`.
- **The 2023 PowerPoints** in `../comp3540-materials/2023/Lectures/` remain the
  best guide to where Penny wanted pictures: she illustrated far more heavily
  in 2023 (168 distinct pictures over 731 slides) than in the 2024 rework
  (64). Use them as a brief, not as a source of files --- the same copyright
  rules apply.
- **The Poll Everywhere prompts.** The 2023 decks carry ~70 live-poll slides
  whose questions are real teaching content. Not images, but the other thing
  these decks lack.

## Conventions

**Authored diagrams** go in `scripts/make-deck-figures.py` and land in
`src/decks/figures/`. Read the "Drawing a replacement" and "Checking the
result" sections of `scripts/deck-images.README.md` first. Run
`python3 scripts/make-deck-figures.py --check` --- it enforces palette,
4.5:1 contrast on the deck background, a 16 css px minimum label size at the
rendered size, and the alt/credit rules. A figure drawn for a slide that never
had a picture has no source SHA, so its `alt`/`credit`/`terms` live in
`deck-extras.json` with `"layout": "figure"`; `--check` reads both files.
A diagram of our own is still credited, with the pages it was drawn from:
`Drawn for COMP3540 from Fullerton pp. 431-440`. `--check` insists on the
word *from* or *after* so nothing here is ever mistaken for a scan.

**Unsplash photographs** follow the comp1720 convention: the file is named
`<photographer-name>-<unsplash-id>-unsplash.jpg`, so attribution survives in
the filename (65 of comp1720's 345 deck images are Unsplash, all named this
way). Keep the `credit` field as `Photo by <name> on Unsplash`. Unsplash's
licence does not require attribution but crediting is right and matches the
other courses.

`scripts/fetch-deck-photos.py` does the fetching, with no API key:

```sh
python3 scripts/fetch-deck-photos.py search "children playing outdoors" -n 12
python3 scripts/fetch-deck-photos.py get DldEn-9g78k
```

`search` writes a numbered contact sheet to /tmp --- **look at it**, because
the first hit is rarely the right one --- and `get` downloads at 2000px into
`src/decks/photos/` under the naming convention.

**Unsplash+ is the trap.** Those results sit alongside the free ones in every
search, the licence is a paid one, and the file you are served is
**watermarked**. Four of them (Andy Quezada, Kateryna Hliznitsova, Andrej
Lišakov, Devin Nelson) got into the decks on 2026-09-22 before this was
noticed; they were swapped for free equivalents the same day. The `plus` flag
in the API is the reliable signal, and the script now acts on it: `search`
leaves those results out entirely and `get` refuses them. Run

```sh
python3 scripts/fetch-deck-photos.py audit
```

before any commit that adds photography --- it re-checks every committed
Unsplash file against its current licence, since the flag can be granted
after the fact. It was clean on 2026-09-22 (20 photographs).

The other thing to watch is composition: pick images that work at full bleed
behind a caption, so dark, or with a quiet bottom-left corner.

**Workshop photographs** are credited `COMP3540 workshop, 2024`.

**Alt text** states what the image shows and why it is there, not its
composition. Under ~150 characters. It is not optional: the build fails
without it.

**Never** hand-edit a deck. Change the converter or the JSON and re-run
`python3 scripts/convert-pptx-decks.py`.

## Checking

To print the source slide numbering that an anchor refers to:

```sh
python3 - <<'SLIDES'
import importlib.util, pathlib, re, zipfile
import xml.etree.ElementTree as ET
spec = importlib.util.spec_from_file_location("conv", "scripts/convert-pptx-decks.py")
c = importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
SLUG = "week02-3-prototyping"
src = [p for p in pathlib.Path("../comp3540-materials/2024/Theory").glob("*/*.pptx")
       if c.deck_slug(p) == SLUG][0]
z = zipfile.ZipFile(src)
names = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
               key=lambda n: int(re.search(r"\d+", n.rsplit("/", 1)[1]).group()))
for i, n in enumerate(names, 1):
    tree = ET.fromstring(z.read(n)).find(f"{c.P}cSld/{c.P}spTree")
    main = [s for s in c.collect_shapes(tree) if s.kind == "text" and s.is_main]
    paras = [p for s in sorted(main, key=lambda s: (s.y, s.x)) for p in c.shape_paragraphs(s)]
    print(f"{i:3d}  {paras[0][1][:70] if paras else '(no text)'}")
SLIDES
```

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

- **One photograph is in the repo and in no deck.** James Sestric's campfire
  (`photos/james-sestric-BWRkppsh46U-unsplash.jpg`) was added for the story
  machine in week03-1 and freed again when that slide became the deck's impact
  slide (media only ever lands on the first piece of a split list). It is kept
  because it is the right picture for `Games as story generators`, which wants
  a full-bleed hero and therefore a `deck-extras.json` entry. Check for others
  with:

  ```sh
  for f in src/decks/photos/*; do b=$(basename "$f"); \
    grep -rq "$b" src/decks/*.deck.mdx scripts/deck-extras.json \
      scripts/deck-format/ || echo "unused: $b"; done
  ```

- **The same photograph is in five decks.** The formatting pass gave 38 slides
  a photograph in the right-hand column, drawing on the pictures already in
  `src/decks/photos/`, and it drew on some of them hard: Stacie Ong's climber
  is in week03-1, week03-3, week04-3, week08-1 and week08-2; the workshop
  playtesting hands are in four decks; six more photographs are in three each.
  Twenty pictures in all are used by more than one deck. A student taking the
  course sees the climber five times. The fix is more photography, not fewer
  splits --- one new picture per over-used slot --- and it is an image-pass
  job, not a formatting one. Recheck with:

  ```sh
  grep -oh './photos/[^)]*' src/decks/*.deck.mdx | sort | uniq -c | sort -rn
  ```

- **A figure is emitted once per source picture, not once per deck.** The
  converter deduplicates a repeated source picture by SHA-256 (`seen_images`),
  but the `kind: "figure"` branch returns before that check, so a redrawing
  placed on a PowerPoint build-up appears on every slide of the build-up:
  `dramatic-arc.svg` three times in week03-1, `interest-curve.svg` twice.
  Fixed in the converter to deduplicate within a deck; a figure taught in
  several decks still appears in each. Which slide of a build-up should carry
  the figure is a separate question, and `deck-images.json` (keyed by hash)
  has no way to say: the dramatic arc wants to be after source 6 and the
  interest curve after source 8, and today they land wherever the picture
  first appeared.

- **No screenshot anchoring.** week04-3's Total War screenshot lands in the
  media row of the first output slide, while the bullet it illustrates
  ("'Mopping up' in strategy games --- Total War") is on the continuation. A
  screenshot belongs on its own `bg contain` slide; there is no key that says
  which piece of a split list it follows.

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

## Next: a formatting pass (Charles, 2026-09-22)

**The deck formatting is bad**, and now that every deck has images it is the
next job --- before any more images go in. The converter takes whatever the
source slide contains, so a generated slide can carry a twenty-item bullet
list, a heading that is really a citation, an `aside` of loose text boxes and
a table, all at once. Every slide has to make sense rendered, at projector
size. Known offenders:

- **`week05-2-level-design`**: every slide is headed
  `"Theory: Level Design Rudolf Kremers. (2009) ... Richard Rouse III (2005)"`
  --- the sidebar label and the full citation have been promoted to `##`, and
  the real headings (*Level Separation*, *Components of a Level: Puzzles*) are
  stranded as the first body bullet. A converter bug.
- **Twenty-bullet slides** (`week04-2-mechanics`, `week08-1-learning-and-training`,
  `week09-2` primer slides). `theme.css` steps the font down to 0.64em, which
  is a workaround, not a fix: these want splitting into two slides.
- **Loose text boxes** appended as a second unexplained bullet list after the
  main one (see the end of `week02-3-prototyping`, "Kinesthetics - feel /
  Game Mechanics / Aesthetics"). They are diagram labels from the source
  slide, with the diagram gone.
- **Repeated `(cont.)` headings**, and asides that repeat the same test-script
  list on six consecutive slides in `week09-2`.
- **The dense new slides**: the Agile Manifesto slide now carries the four
  values *and* a six-row table; the twelve principles probably want their own
  slide.
