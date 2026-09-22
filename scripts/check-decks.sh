#!/bin/sh
# Run astromotion's overflow check over the lecture decks: every slide of
# every deck in headless Chrome, reporting what does not fit the 1280x720
# canvas. It is the instrument the formatting pass is measured with (see
# scripts/deck-format.README.md).
#
#   scripts/check-decks.sh                       # all eighteen decks
#   scripts/check-decks.sh week05-2 --json       # one deck, machine-readable
#   PORT=4410 scripts/check-decks.sh             # a port of your own
#
# Two things this wraps, both of which cost an afternoon to find out:
#
#  * the route prefix has to carry the site's base path (BASE_PATH is
#    /courses/comp3540/), or every deck comes back as HTTP 404;
#  * `astro dev` here is Astro's *managed* dev server: it keeps running after
#    the command that started it exits, and it goes on serving the MDX it
#    parsed at start-up. Re-running the check after regenerating the decks
#    then silently re-measures the old slides. So free the port first, which
#    is what the loop below does -- and only for a server of this project, as
#    the sibling course sites run their own on nearby ports.
set -e
PORT=${PORT:-4399}
root=$(cd "$(dirname "$0")/.." && pwd)
for pid in $(lsof -ti:"$PORT" 2>/dev/null || true); do
  case "$(ps -o command= -p "$pid" 2>/dev/null)" in
    *"$root"*) kill "$pid" 2>/dev/null || true ;;
  esac
done
# Start the server ourselves rather than letting the check do it: Astro's
# managed dev server takes a per-project lock, so with several decks being
# worked on at once the check could not start one at all. --ignore-lock and a
# port of our own give each run its own server, freshly parsed.
if ! curl -fs -o /dev/null "http://localhost:$PORT/courses/comp3540/"; then
  (cd "$root" && npx astro dev --port "$PORT" --ignore-lock >/dev/null 2>&1 &)
  i=0
  while [ "$i" -lt 60 ]; do
    curl -fs -o /dev/null "http://localhost:$PORT/courses/comp3540/" && break
    i=$((i + 1)); sleep 1
  done
fi
if [ -z "$ASTROMOTION_CHROME_PATH" ] && [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  ASTROMOTION_CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  export ASTROMOTION_CHROME_PATH
fi
exec npx astromotion-check --prefix=/courses/comp3540/lectures --port="$PORT" "$@"
