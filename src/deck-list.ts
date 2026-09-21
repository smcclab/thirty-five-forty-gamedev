export interface DeckListEntry {
  slug: string;
  date?: Date;
}

export function sortDecks<T extends DeckListEntry>(decks: T[]): T[] {
  return [...decks].toSorted((a, b) => {
    if (a.date && b.date) return a.date.getTime() - b.date.getTime();
    if (a.date) return -1;
    if (b.date) return 1;
    return a.slug.localeCompare(b.slug, undefined, { numeric: true });
  });
}
