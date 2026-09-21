import type { ImageMetadata } from "astro";

// Every image under src/ that content may point at by path. Front matter
// (`heroImage: /src/assets/images/...`, a deck's `image: ./assets/...`) is a
// plain string, so resolve it to ImageMetadata here for Card and Hero.
const siteImages = import.meta.glob<{ default: ImageMetadata }>(
  "/src/assets/images/**/*.{avif,png,jpg,jpeg,webp,gif,svg}",
  { eager: true },
);
const deckImages = import.meta.glob<{ default: ImageMetadata }>(
  "/src/decks/assets/**/*.{avif,png,jpg,jpeg,webp,gif}",
  { eager: true },
);

export function siteImage(path: string | null | undefined): ImageMetadata | undefined {
  if (!path) return undefined;
  return siteImages[path]?.default;
}

/** A deck front-matter `image` is relative to src/decks (e.g. ./assets/week-1/x.jpg). */
export function deckImage(path: string | null | undefined): ImageMetadata | undefined {
  if (!path) return undefined;
  const key = path.startsWith("/src/decks/") ? path : "/src/decks/" + path.replace(/^\.\//, "");
  return deckImages[key]?.default;
}
