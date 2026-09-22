# Deck formatting

The 18 lecture decks are generated from Penny Kyburz's 2024 PowerPoints, and
the converter carries over whatever a source slide held. Measured on
2026-09-22: 359 slides, **152 of them ran off** the 1280x720 canvas, the worst
by 282px. A slide that does not fit is not a slide, so this file sets the
budget every slide must meet and the one place a rewrite may live.

The converter now breaks a list that does not fit across two slides instead of
shrinking it, lays one photograph beside bullets as a two-column slide, keeps
citations out of headings and drops the debris (see "Debris" below). That took
the same material to 501 slides with 18 overflows, all of them a single
oversized bullet, table or aside that only a rewrite can fix. **That rewrite is
the job this file describes**, and it is per-deck: one agent, one deck, one
JSON file.

Nothing is ever done by hand in a `*.deck.mdx`. A rule goes in
`convert-pptx-decks.py`, a per-slide decision goes in
`scripts/deck-format/<slug>.json`, and the deck is regenerated.

## The numbers

Canvas 1280x720; the theme pads 64px top and bottom and 80px each side, so the
content box is 1120x592. Body text is 1.75rem (28px) at line-height 1.5, so a
line costs 42px and **a slide is fourteen lines**, of which the `##` takes
1.25. A full-width line holds about 74 characters (12 words); the content
column of a 40% split holds about 42 (6 words). Those five numbers are the
constants at the top of `convert-pptx-decks.py` ("fitting a slide to the
canvas"); change them there and nowhere else.

Every slide is budgeted in **lines**, and a bullet costs what it wraps to:

| Slide | Bullet ≤ 1 line | Bullet = 2 lines | Longer |
|---|---|---|---|
| Full width | ≤ 11 words | 12-22 words | not allowed |
| Split (40% image) | ≤ 6 words | 7-12 words | not allowed |

- **12 lines of body per slide**, counting every top-level bullet, sub-bullet
  and aside line. Lens slides (Schell's numbered questions, quoted, not
  rewritten) may run to the full fourteen because they carry nothing else.
- **At most 6 top-level bullets, at most 8 bullets in all**, one level of
  nesting. A third level becomes its own slide or is folded into its parent.
- **Over budget means split, never shrink.** The 0.74em and 0.64em steps in
  `theme.css` are gone; 0.86em stays as a tripwire only, because 24px on the
  canvas is the smallest type a lecture theatre can read, and a deck is not
  finished while any slide is on it.
- A slide has one heading, one list, and at most one of: an aside (≤ 4
  lines), a table, an inline media row, a split photograph. Never two.

## The writing lives in `scripts/deck-format/<slug>.json`

One file per deck, named after the deck (`week05-2-level-design.json`), so
eighteen decks can be worked on at once without two people editing one file.
The PowerPoint is the source of truth and never changes, so an entry is keyed
the way `deck-extras.json` is: by **source slide number**, the `## Slide N` of
the text dump (`python3 scripts/extract-ooxml.py ../comp3540-materials
/tmp/comp3540-text`). Output numbering shifts every time a slide ahead of it is
split, which is why it is never used as a key.

```json
{
  "slides": {
    "4": {
      "heading": "Level separation",
      "bullets": [
        "How play is cut into levels shapes the flow of the whole game",
        "  Players stop \"just after this level\"; saves and a sense of accomplishment sit at level ends",
        "A level is a chapter or an act: tension and release on a dramatic curve"
      ],
      "split_after": [2],
      "continuations": ["Level separation: pacing"],
      "why": "dropped the lead-in sentence; nothing else"
    },
    "9": {
      "heading": "Choosing an idea",
      "split_image": {
        "file": "photos/annotated-design.jpg",
        "alt": "A pencil design sheet annotated in pen, arrows between the parts.",
        "credit": "COMP3540 workshop, 2024"
      }
    }
  }
}
```

Every key, and nothing else is allowed (an unknown key stops the converter,
because a typo that silently did nothing would look exactly like a rule that
did not work):

| Key | What it does |
|---|---|
| `heading` | replaces the generated `##` |
| `bullets` | replaces the body list; two leading spaces per level of nesting |
| `split_after` | break the list after these top-level bullet numbers (1-based), instead of wherever the budget falls |
| `continuations` | the headings for the 2nd, 3rd … slide the list is broken across |
| `split_image` | `{file, alt, credit}`: a photograph under `src/decks/` for the right-hand column |
| `image_layout` | `auto` (default), `split` to force two columns, `row` to force the inline media row |
| `aside` | `keep` (default) or `drop` |
| `loose` | `comment` (default), `keep` or `drop` |
| `table` | `keep` (default) or `drop` |
| `class` | a slide class: `impact` for a one-line question, `activity` for a prompt |
| `links` | `keep` (default) or `drop` for the source slide's hyperlinks |
| `drop` | `true`: emit no slide at all for this source slide (a PowerPoint build-up whose last slide carries the whole list) |
| `why` | one line on what the rewrite left out; the converter writes it into the slide's `comment` fence |

- `bullets` carries no Markdown other than `**`, `*` and links, and adds no
  picture that is not already in `src/decks/`. Nesting is by indent alone: a
  list you write is rendered as a list, top level to top level. (Converted
  source bullets are not: PowerPoint writes a sub-heading as a level-0 line
  with the rest nested under it, so for those the converter still turns a
  level-0 line into an `###`.)
- `links` is `keep` (default) or `drop`: `drop` when the rewrite has already
  worked the slide's hyperlink into a bullet as a named link, so the
  converter does not also append it under the list.
- A slide with a `split_image` that is also a full-bleed slide of its own in
  `deck-extras.json` **loses the full-bleed slide**: the converter drops any
  extra whose file a `split_image` in the same deck claims. That is how a
  photograph is moved into a column without touching the shared file.
- Leave a slide out of the file entirely when the converter already gets it
  right. Most slides should not be in here.

**What may be cut.** Lead-ins and hedges ("Important to consider", "Keep in
mind that", "Designer needs to"), "e.g.," and "etc.", the restated subject of
the slide, a second and third example where one carries the point, a
sentence that repeats the previous bullet in other words, a bare URL (it
becomes a named link: `[Video: graphically stunning levels](https://…)`).
Parentheticals become a dash clause or their own sub-bullet. Full sentences
become fragments with the verb kept.

**What is never cut.** A named game, designer or author; a number, a page
reference, a chapter; every question on a lens slide, word for word; a
definition (the sentence with "is" or "means" in it); any example Penny
chose, because students recognise the game and that is the teaching. If it
does not fit, it goes on the next slide, not into the notes and not away.

**Honesty.** Each bullet compresses one or more consecutive source lines in
source order; no bullet says something the source did not, and no example is
swapped for a better one. Read the deck against its `## Slide N` text in
/tmp/comp3540-text before calling it finished, and record what went in `why`.

## Two columns

`![bg right:40%](./photos/x.jpg)` makes astromotion lay the slide out as a
60% content column and a 40% image panel. That is the layout the decks are
missing, and it is standardised as follows.

- **Right, 40%, always.** The heading stays top-left where every other
  slide puts it, the eye lands in the same place on every slide, and 40%
  leaves a column wide enough for 6-word lines. No `left:`, no `50%`: two
  variants would cost every agent a judgement and buy nothing.
- **Photography only.** The panel is `background-size: cover` over a
  512x720 portrait, so a picture is centre-cropped to a third of its width.
  Unsplash and workshop photographs (`photos/`) survive that; choose ones
  whose subject sits in the middle third. A game screenshot does not: the
  crop takes the HUD and the edges, which is what the slide is about. Our
  SVG figures have labels and stay on their own slide (decided; do not
  re-litigate).
- **When.** A split slide is a bullet slide that has a photograph to
  support it: a concept with a photographable example (a stadium for
  sports levels, sticky notes for brainstorming). It replaces a full-bleed
  `hero` where the photograph is illustrating bullets rather than making a
  point of its own. Keep `hero` for the picture that *is* the point and
  gets a teaching caption; keep `bg contain` on its own slide for
  screenshots; keep `figure` slides for drawings.
- **No caption; credit yes.** The bullets are the text. The converter emits
  the usual `.image-credit`, which lands bottom-right over the photograph;
  `theme.css` gives it a text shadow on split slides so it reads on any
  picture.
- **An inline row carries at most three pictures.** The row shares 30vh
  between them, so a fourth is a stamp. A slide whose bullets are set with
  `"bullets": []` keeps its pictures and gets them at 52vh, which is how a
  row of three is given a slide of its own; a longer row is a note in the
  report, not a fix, because splitting it means re-deciding pictures in the
  shared `deck-images.json`.

## Headings

- A heading is **2-6 words, 40 characters at most**, sentence case, no
  trailing punctuation except a question mark. Proper nouns and Schell's
  lens names keep their capitals ("The Lens of Time (lens 27)").
- **A citation is never a heading.** The `Theory: <topic> <readings>` title
  block is the deck's title plus its readings: the converter drops it as a
  heading, sends the readings to the credit line, and takes the first
  level-0 body paragraph as the heading (the `week05-2` bug). Extend
  `CITATION_RE` to match "Kremers – Ch. 2" and "Rouse – Ch. 7" so those
  asides go to the credit line too.
- **No `(cont.)`, ever.** A slide that continues a topic gets a heading of
  its own in colon form, `Level flow: strategy`, `Good level design:
  navigating`, taken from the sub-heading the source stranded as its first
  bullet. Where the source gives no sub-heading, `continuations` supplies
  one: the converter's fallback is `<heading> (cont.)`, and a deck is not
  finished while one of those is left. A figure slide takes its parent's
  heading unchanged, so the pair
  reads as one thought; that is the only allowed repeat.
- The credit line drops the topic label ("Level Design", "Training"), which
  repeats the deck title, and keeps citations in the short form `Fullerton
  pp. 241-244`, then image credits.

## Debris

- **Loose text boxes** (shapes that are neither the content placeholder nor
  the sidebar) are diagram labels whose diagram was dropped. The converter
  never emits them as bullets; it writes them into the `comment` fence as
  `loose: …`. If one is content, the rewrite includes it.
- **An aside repeated on consecutive slides** is emitted once, on its first
  slide, and suppressed while its text is unchanged. The eight-step level
  design process (five slides in `week05-2`) becomes its own ordered-list
  slide before the steps, and is dropped from each step. Reading pointers in
  asides are citations (above). An examples aside ("Tic-Tac-Toe: discrete 2D,
  3x3; how about chess, Monopoly, pool?") stays, within the 4-line cap.
- **A table beside bullets that say the same thing** keeps the table and
  loses the bullets (`"bullets": []`); the table is denser and reads to a
  screen reader. A table of more than about eight rows does not fit a slide
  at all: either `table: "drop"` and write the rows as bullets across two
  slides, or leave it and say so in the report. Six rows by three columns is
  comfortable.
- **The agenda slide** stays as it is (numbered list, ≤ 8 lines). A slide
  the source left empty of content becomes nothing, not "Overview".

## Rhythm

Full-bleed image slides are how the sibling courses breathe (comp1720: 321
of 344 deck images are whole slides). Splitting dense slides will take a
20-slide source to 28-35 output slides, which is right for a 50-minute
theory session; a deck over 40 is a sign the rewrite kept every sentence.

Per deck, after the title and closing slides:

- **No more than 60% bullet-only slides**, and never more than three in a
  row: the fourth is a split, a hero or a figure.
- **At least 25% picture-bearing slides** (hero, contain, figure and split
  all count), which is the road to the 0.6 images-per-slide target. This one
  is out of reach for a deck with no photography: a formatting pass can lay a
  picture out, and `split_image` can move one into a column, but a new
  full-bleed slide is a `deck-extras.json` entry and that file belongs to the
  image pass (`IMAGE-PLAN.md`). Report the number you reached and leave it;
  do not pad a deck with photographs that illustrate nothing.
- **2-4 split slides**, placed where the bullets have a photographable
  example, not spread evenly for its own sake.
- **One `impact` slide** in the middle third, carrying a question the source
  already asks ("What is a system?", "How about chess?"). The 2023 poll
  prompts will fill this later; until then take the question from the 2024
  slide itself.
- One lens slide per lens, unchanged. One table slide per table.

## Definition of done, per deck

An agent claims a deck finished only after all of these, in order:

1. `python3 scripts/convert-pptx-decks.py --only <slug>` exits 0 and the diff
   touches only `src/decks/<slug>.deck.mdx` and
   `scripts/deck-format/<slug>.json`. Nothing else: the converter, the
   stylesheet and the two shared JSON files belong to whoever is running the
   pass, and a change to one of them is a note in the report.
2. `grep -nE '^## .*(cont\.\)|^## Theory:|^## .{41,}' src/decks/<slug>.deck.mdx`
   prints nothing, and no slide has more than 8 lines beginning `- ` or
   `  - ` (the 0.86em tripwire never fires).
3. `PORT=<your port> scripts/check-decks.sh <slug> --json` reports **zero**
   violations at the default 4px tolerance: no `overflow`, no `clipped`, no
   `scrollbar`. That script starts its own dev server and frees the port
   first, which matters, because Astro's managed dev server outlives the
   command that started it and goes on serving the slides it parsed at
   start-up -- run the check without it and you measure the deck you had
   before you regenerated it.
4. `pnpm build` passes: axe (every `alt`), links, deck structure.
5. `python3 scripts/fetch-deck-photos.py audit` is clean if any photograph
   was added.
6. The rhythm counts hold (bullet-only ≤ 60%, pictures ≥ 25%, 2-4 splits,
   one impact); state them in the report.
7. Eyes, twice. Read the regenerated deck against its source text in
   `/tmp/comp3540-text/2024/Theory/…`, slide by slide: nothing cut that the
   "never cut" list protects, no claim the source did not make, every `why`
   true. Then read the deck source through once as a deck -- headings in
   order, no slide that is only a fragment, no two consecutive slides that
   say the same thing.

Record the deck in the table in `../IMAGE-PLAN.md` with its new slide and
image counts, and nothing else in that file.
