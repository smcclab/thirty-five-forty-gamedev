# COMP3540/COMP6540 Game Development

Source for the COMP3540/COMP6540 course website at the ANU School of
Computing. It is being developed as preparation for a possible future
offering, and is published as a preview at
<https://smcclab.github.io/thirty-five-forty-gamedev/>; if the course runs it
will move to <https://comp.anu.edu.au/courses/comp3540/>.

The 2023 and 2024 offerings were designed and taught by Professor Penny
Kyburz, whose materials this site is built from. &copy; The Australian
National University. All rights reserved.

Built with [Astro](https://astro.build) on the
[astro-theme-university](https://anucybernetics.github.io/astro-theme-university/)
theme, the astro-course-university content model and astromotion slide
decks — the same stack as the comp1720 and comp4350 course sites. The
[astro-theme-anu](https://gitlab.anu.edu.au/u2548636/astro-theme-anu) brand
package is installed but switched off until the site is served from ANU. See
`CLAUDE.md` for the layout and conventions.

```sh
mise install        # node + pnpm from mise.toml (or install them yourself)
pnpm install
pnpm dev            # http://localhost:4321/courses/comp3540/
pnpm build          # static site in dist/, after accessibility, link and graph checks
pnpm typecheck
```

The site is a scaffold: most pages are placeholders pending conversion of the
2023--2024 course materials (PowerPoint and Word) held outside this repo.

If you're a student, you're probably looking for a different repository: follow
the links on the course website.
