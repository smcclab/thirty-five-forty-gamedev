import { defineCourseCollections } from "astro-course-university/schemas";
import { courseCollections } from "./course-collections";

export const collections = {
  ...defineCourseCollections(courseCollections),
};
