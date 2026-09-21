// The graph collections, declared once: src/content.config.ts builds the
// Astro collections from this object and astro.config.ts hands the same
// object to courseGraph(), so keys, directories and schemas never drift.
import { z } from "astro/zod";
import type { CourseCollectionsSpec } from "astro-course-university";

// Fields course pages carry beyond the shared node schema.
const page = {
  heroImage: z.string().nullish(),
  heroImageAlt: z.string().nullish(),
  /** Listing order within the collection. */
  order: z.number().int().nullish(),
  toc: z.boolean().default(true),
  /** The year's GitLab template repository for student work. */
  templateRepo: z.url().nullish(),
};

export const courseCollections = {
  workshops: { schema: (node) => node.extend(page) },
  assessments: { schema: (node) => node.extend(page) },
  resources: { schema: (node) => node.extend(page) },
} satisfies CourseCollectionsSpec;
