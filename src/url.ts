/** Prefix a root-absolute path with the configured base (e.g. /courses/comp1720/). */
export function withBase(path: string): string {
  const base = import.meta.env.BASE_URL.replace(/\/$/, "");
  return `${base}/${path.replace(/^\//, "")}`;
}
