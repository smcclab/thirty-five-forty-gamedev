import { defineSiteConfig } from "astro-theme-university/types";
// ANU branding (logos, legal links, partner logos, Acknowledgement of
// Country) is switched off while this is a development preview off ANU
// servers. To bring it back, restore this import, spread `...anuBranding`
// into `siteConfig` below and re-enable `brandCss` in astro.config.ts.
// import { anuBranding } from "astro-theme-anu";

// Course facts that pages, layouts and content refer to. These are the
// year-specific values (see CLAUDE.md): refresh them each offering. The
// `TODO` placeholders are deliberate — fill them in once the offering, the
// convenor and the Ed forum for that year are confirmed.
export const course = {
  code: "COMP3540/6540",
  title: "Game Development",
  /** TODO: e.g. "Semester 2, 2027" — also update `year` below. */
  semester: "TODO: semester and year",
  /** TODO: the catalogue year, used to build the Programs and Courses links. */
  year: "TODO",
  school: "ANU School of Computing",
  /** TODO: confirm the convenor for the next offering. The 2023 and 2024
   *  offerings were convened by Professor Penny Kyburz, who wrote all the
   *  source material in ../comp3540-materials (see MATERIALS.md). */
  convenor: "TODO: convenor",
  contactEmail: "TODO: convenor email",
  /** TODO: the Ed Discussion URL for the offering. */
  forumUrl: "TODO: Ed Discussion URL",
  // Undated catalogue links; swap in the year-specific ones once `year` is set.
  programsAndCourses: "https://programsandcourses.anu.edu.au/course/COMP3540",
  programsAndCoursesMasters: "https://programsandcourses.anu.edu.au/course/COMP6540",
};

/** Banner image for pages that do not set their own heroImage.
 *  TODO: replace with a photo of the class or a current student game. */
export const DEFAULT_HERO = "/src/assets/images/photos/student-game-platformer.jpg";

export const siteConfig = defineSiteConfig({
  // ...anuBranding,
  name: "COMP3540",
  // No `licence`: the content is not openly licensed. The copyright notice
  // and the course-design credit are the footer `meta` lines below.
  meta: [
    "&copy; The Australian National University. All rights reserved.",
    "The 2023 and 2024 offerings of this course were designed and taught by Professor Penny Kyburz, whose materials this site is built from.",
  ],
  links: [
    { text: "Lectures", href: "/lectures/" },
    { text: "Workshops", href: "/workshops/" },
    { text: "Assessments", href: "/assessments/" },
    { text: "Resources", href: "/resources/" },
    { text: "Policies", href: "/policies/" },
  ],
});
