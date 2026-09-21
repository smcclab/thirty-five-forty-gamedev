import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import universityTheme from "astro-theme-university";
import courseGraph from "astro-course-university";
import { courseCollections } from "./src/course-collections";

// SITE_URL and BASE_PATH come from .env locally, from .gitlab-ci.yml on ANU
// GitLab and from .github/workflows/pages.yml on GitHub Pages.
const site = process.env.SITE_URL ?? "https://comp.anu.edu.au";
const base = process.env.BASE_PATH ?? "/courses/comp3540/";

export default defineConfig({
  site,
  base,
  integrations: [
    universityTheme({
      defaultLayout: "src/layouts/PageLayout.astro",
      // ANU branding is switched off while the site is a development
      // preview off ANU servers. Re-enable this line and the `anuBranding`
      // spread in src/site-config.ts when it moves to comp.anu.edu.au.
      // brandCss: "astro-theme-anu/anu.css",
      // astromotion for src/decks/*.deck.mdx, served at /lectures/<slug>/ so
      // the decks sit inside the Lectures section of the site.
      decks: { theme: "./src/decks/theme.css", routePrefix: "/lectures" },
      llmsTxt: true,
    }),
    courseGraph({ collections: courseCollections }),
    sitemap(),
  ],
});
