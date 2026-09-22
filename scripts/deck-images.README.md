# Deck figures and copyright

`deck-images.json` decides what happens to every picture in the 2024 theory
PowerPoints. It is keyed by the SHA-256 of the source image, and each entry
says which of four things to do with it:

| `kind` | What the converter does |
|---|---|
| `source` | Publishes the picture itself, with its `alt` and `credit`. Add `"own_slide": true` to give it a slide rather than squeezing it beside the bullets. |
| `figure` | Publishes an **original redrawing** from `src/decks/figures/`, made by `scripts/make-deck-figures.py`. |
| `snippet` | Replaces it with the Markdown in `scripts/deck-snippets/` — for source "figures" that are really tables. |
| `photo` | Publishes a **replacement** from `src/decks/media/` — a cleaner capture of the same thing. Until that file exists the slide carries a note, so an entry can be written before the image is made. |
| `drop` | Leaves it out, writing the entry's `note` into the deck source so a future convenor can see what was there and why. |

A picture that is not listed is dropped with a generic note. The reverse job
— adding an image to a slide that never had one — is `deck-extras.json`,
documented in `../IMAGE-PLAN.md`.

To see the pictures again:

```sh
python3 scripts/convert-pptx-decks.py --review /tmp/deck-images
```

That writes every source picture (named by content hash) plus `manifest.json`
recording which deck and slide each came from and the citation beside it.

## Why the redrawings exist

All 49 distinct pictures in the source decks were reviewed on 2026-09-21.
They are commercial game screenshots, scans of figures from the set texts —
several still carrying their figure numbers — and stock photography. They were
fine in a PowerPoint behind Wattle under the educational statutory licence.
That licence does not cover a public website, which is what this repo builds.

But the *models* those figures show are the course content, and copyright
protects a drawing, not the idea it depicts. So the conceptual figures are
redrawn from scratch: `scripts/make-deck-figures.py` writes 23 SVGs into
`src/decks/figures/`, transparent and in the deck palette. Seventeen replace a
source picture; the other six were drawn for slides that never had one and are
described in `deck-extras.json` instead (see `../IMAGE-PLAN.md`).

**Most of these models are third-party even inside the textbook.**
Csikszentmihalyi (1990), Massimini & Carli (1988), Maslow (1943), Bartle
(1996), Parlett's rules taxonomy and Cook's "Loops and Arcs" (Lostgarden,
2012) are published in the primary literature; Fullerton and Schell are
themselves redrawing them. So a credit names the primary source and gives the
set text as the reading pointer:

> Redrawn after Csikszentmihalyi (1990); see Schell ch. 11

Always the word *redrawn* or *after*, so nobody later mistakes one of these
for a scan and re-derives the wrong licence. One credit on the slides was
simply wrong and is fixed here: the loop and arc figures are Dan Cook's, not
Fullerton's.

Figures in `src/decks/figures/` are original ANU drawings, © ANU like the rest
of the site.

### Drawing a replacement

Write the figure's `teaches` sentence and its `terms` into `deck-images.json`
first (or into `deck-extras.json`, for a figure that replaces nothing), then **close the original and draw from that description**. Keep the
technical vocabulary — students have to match it to the reading — and change
everything that is only presentation: orientation, node shapes, layout,
palette, sublabel wording. Drop every decorative device (Bartle's card suits,
Schell's gamepad and cityscape clip art, Cook's icons, the Spock photograph):
that is the part which is someone's expression.

Three things are better off not being pictures at all. Fullerton's figs. 8.2
and 9.1 are matrices, so they are Markdown tables in `scripts/deck-snippets/`,
which is also more accessible. Her fig. 9.10 is a full page of her own
playtest questions — reproducing it is a substantial excerpt, so it is
dropped, and the slide now carries a figure of the form's *structure*
(`playtest-notes`) instead. The Agile poster is a third-party infographic, so
it stays dropped too, but the twelve principles are reproducible ideas: they
are now a paraphrased two-column table in
`deck-snippets/agile-principles.md`, linked to agilemanifesto.org.

## Checking the result

```sh
python3 scripts/make-deck-figures.py           # redraw all 23
python3 scripts/make-deck-figures.py --check   # lint them
python3 scripts/make-deck-figures.py --sheet /tmp/figs   # contact sheet
```

`--check` applies the rules a machine can apply: every colour is in the deck
palette and clears 4.5:1 on the deck background, no opaque background rect,
at most 14 text labels, the smallest label is at least 16 css px at the size
the figure actually renders, every `terms` entry appears in the drawing, and
the `alt` and `credit` are present and well formed. It runs clean today, and
`pnpm build` is the last gate — axe fails the build on a missing `alt`.

The rest needs eyes, roughly two minutes per figure:

1. **Fidelity.** Read the redrawing alone and write down the takeaway. It
   should match `teaches`, and nothing the slide's bullets refer to should be
   missing.
2. **Projector.** Open the built deck and shrink the window to 640 px wide,
   which is about what the back of a theatre looks like. Every label readable,
   no two labels touching, arrows unambiguous.
3. **Legal distance.** Nothing traced, no photo or icon carried over, and at
   least three of {layout, shapes, palette, label wording, data values}
   different from the original.

## The game screenshots

The 24 commercial screenshots are a separate question from the figures, and
they **are** published, credited to game, developer and year. The reasoning,
and the two things worth improving about them, are in MATERIALS.md.
