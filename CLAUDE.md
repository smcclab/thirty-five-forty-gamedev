# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Source for the COMP3540/COMP6540 *Game Development* course website (ANU School
of Computing), built with Astro on the astro-theme-university /
astro-theme-anu / astro-course-university / astromotion stack — the same stack
as the comp1720 and comp4350 sites, which are the worked examples to copy from
when something here is missing.

The site is built out from the 2024 offering: 18 generated lecture decks, 11
workshop pages, 5 assessment pages with their rubrics, 5 resource pages, and
policies. The source material lives outside this repo in
`../comp3540-materials/` and is **not** committed here.
**`MATERIALS.md` surveys that tree, records what was converted and how, and
sets out the rules about images — read it before doing any content work.**
In short: 2024 is the source of truth; the material was written by Professor
Penny Kyburz and reuse should be confirmed with her; the deck converter must
never extract images from the slide relationship list (they are webcam stills
of the lecturer); no slide figure is published unless it is allow-listed in
`scripts/deck-images.json`, which is empty; and the peer-assessment
spreadsheets, the tutor brief and student names must not be published.

**This is a running course**, so there is deliberately no archive notice.
Year-specific values are placeholders marked `TODO` and must be filled in for
each offering: the `course` object in `src/site-config.ts` (semester, year,
convenor, Ed forum, the year-specific Programs and Courses links), the due
dates and weightings in `src/pages/assessments/index.mdx` and
`src/content/assessments/`, and the engine/version in
`src/content/resources/tools.md`.

## Commands

```sh
mise install        # node 24 + pnpm from mise.toml
pnpm install        # --frozen-lockfile in CI
pnpm dev            # http://localhost:4321/courses/comp3540/
pnpm build          # static site in dist/; fails on a11y, broken-link, base-path or deck-structure violations
pnpm typecheck      # astro check
```

`SITE_URL` and `BASE_PATH` come from `.env` locally (copy `.env.example`) and
from `.gitlab-ci.yml` in CI; `astro.config.ts` falls back to the production
values when they are unset.

## Where this repo lives

`origin` is <https://gitlab.anu.edu.au/u4110680/comp3540> for now. The
`.gitlab-ci.yml` is the CECS GitLab Pages pipeline the other two courses use
(`BASE_PATH=/$CI_PROJECT_PATH/`, tags `Pages`, deploys `master` only); it will
only actually run once the project moves to
`gitlab.cecs.anu.edu.au:courses/comp3540`. Until then CI on gitlab.anu.edu.au
will not pick up a `Pages`-tagged runner — run `pnpm build` locally as the
check.

## Dependencies

Every theme package in `package.json` is pinned to an exact release tag and
fetched over anonymous HTTPS from ANU GitLab. Upgrade by editing the tag and
running `pnpm install`; never float to a branch.

- `astro-theme-anu` --- ANU branding, from Ben Swift's repo on gitlab.anu.edu.au.
- `astro-theme-university`, `astro-course-university`, `astromotion` --- the
  theme, course model and deck packages, from read-only mirrors of the
  ANUcybernetics GitHub repos under `u4110680` on gitlab.anu.edu.au. To pick
  up a new upstream release, refresh the mirror first, then bump the pin:

  ```sh
  git clone --mirror https://github.com/ANUcybernetics/astromotion.git
  git -C astromotion.git push --mirror git@gitlab.anu.edu.au:u4110680/astromotion.git
  ```

`patches/astromotion@0.30.1.patch` (applied through `patchedDependencies` in
`pnpm-workspace.yaml`) fixes deck background URLs for a checkout that lives
under a directory named `src`, such as `~/src/...`. Drop it once upstream
resolves asset paths against the project root. The same patch is carried by
the comp1720 and comp4350 repos.

## Layout

- `src/content/{workshops,assessments,resources}/` --- content collections,
  declared once in `src/course-collections.ts` (read by both
  `src/content.config.ts` and `courseGraph()` in `astro.config.ts`). A file's
  name is its URL slug. Front matter: `title`, `description` (the lead
  paragraph, the card blurb and the llms.txt entry), `heroImage` (a
  `/src/assets/images/...` path) + `heroImageAlt`, `order` (listing order),
  `toc` (false to suppress the "On this page" list), `templateRepo`, and
  `unlisted: true` for a page that builds but is left out of listings. A page
  is `.mdx` only when it needs a component; in `.mdx` there are no HTML
  comments and bare `{` must be escaped `\{`. Callouts are `:::info` /
  `:::warning` / `:::tip` / `:::error` directives.
- `src/decks/*.deck.mdx` --- the 18 lecture decks (astromotion), served at
  `/lectures/<slug>/` via the theme's `decks.routePrefix`. They are
  **generated** from the 2024 theory PowerPoints by
  `scripts/convert-pptx-decks.py`; edit the converter and re-run it rather
  than hand-editing a deck, exactly as comp1720 and comp4350 do with their
  Jekyll sources. `MATERIALS.md` documents what the converter models and why.
  Slide classes are set with an MDX comment (`{/* _class: impact */}`) and
  styled in `src/decks/theme.css`, layered over the theme's `deck.css`; the
  stylesheet also has to cope with dense converted slides, so it steps the
  font size down as a slide's bullet count grows and lays several images out
  in a row. Background images would be `![bg contain|cover](./assets/<path>)`
  from `src/decks/assets/`.
- `src/pages/` --- `index.mdx` (home, with `CourseJsonLd`), `policies.mdx`,
  `404.mdx`, and the collection index pages (`lectures/index.mdx`,
  `workshops/index.mdx`, `assessments/index.mdx`, `resources/index.mdx`) which
  carry their own prose and embed `<CollectionCards collection="…" />` or
  `<DeckCards />`. MDX pages get `src/layouts/PageLayout.astro` via the theme's
  `defaultLayout`; front matter `toc: true` adds an "On this page" list
  (`tocDepth` to include h3). Detail routes (`[slug].astro`) define their own
  `getStaticPaths` so unlisted entries still build.
  Pages without their own hero get `DEFAULT_HERO` from `src/site-config.ts`.
- `src/layouts/` --- `PageLayout` (MDX pages), `SiteLayout` (listings),
  `EntryLayout` (collection entries).
- `src/components/` --- `CollectionCards` (sorted by `order`), `DeckCards`,
  `Toc`, `CourseJsonLd`. YouTube embeds use the theme's `YouTubeEmbed`.
  `src/images.ts` resolves front-matter image paths to `ImageMetadata`.
- `public/images/` --- images referenced from content by root-absolute path;
  the theme prefixes the base for Markdown images and links but not for raw
  `<img>` tags: use Markdown syntax or `withBase()` from `src/url.ts`.
- `src/llms.md` --- hand-written preamble for the generated `/llms.txt`.

## Checks the build runs

`pnpm build` fails on any axe accessibility violation (iframes need `title`,
tables need non-empty header cells, heading levels must not skip: card grids
on an h1 page with h2 prose headings need `headingLevel="h2"`), any broken
internal link, any root-absolute link that escapes the base, any `related:`
ref that does not resolve, and any deck whose structure the astromotion
checker rejects. Fix the content rather than disabling the check. Link
fragments are not verified.

## Source materials

See `MATERIALS.md` for the full survey, the 2024 course and assessment
structure, what was converted and the image rules. Two scripts:

```sh
python3 scripts/extract-ooxml.py ../comp3540-materials /tmp/comp3540-text  # text of every pptx/docx
python3 scripts/convert-pptx-decks.py                                      # regenerate src/decks
python3 scripts/convert-pptx-decks.py --review /tmp/deck-images            # triage slide figures
```

Site photography is in `src/assets/images/photos/`: workshop prototype photos
from `2024/WW4-Photos` (cropped, EXIF stripped, no identifiable faces — the
one wide shot that did show faces, `IMG_9501`, is deliberately not used) and
four frames from the student game showreel `2024/ANU-Games.mp4`.
