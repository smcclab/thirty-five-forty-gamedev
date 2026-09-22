#!/usr/bin/env python3
"""Find and download the Unsplash photographs used as deck backgrounds.

The decks need photographs for the slides that never had a picture (see
IMAGE-PLAN.md). comp1720 sources those from Unsplash and keeps attribution in
the filename --- `<photographer>-<photo id>-unsplash.jpg` --- and this script
does the same thing without a browser:

    python3 scripts/fetch-deck-photos.py search "children playing" -n 8
    python3 scripts/fetch-deck-photos.py get <photo-id>
    python3 scripts/fetch-deck-photos.py audit

`search` writes a numbered contact sheet to /tmp so the candidates can be
looked at before one is chosen; `get` downloads the full picture at 2000px
into src/decks/photos/, which is where a deck can reference it (only
src/decks/ is copied into dist/).

It reads unsplash.com's own search endpoint, which needs no API key. That is
not a supported API, so expect to fix this script rather than the decks if it
stops working --- the photographs themselves are committed, so nothing in the
build depends on it.

**Unsplash+ results are skipped.** They sit alongside the free ones in every
search, and the file you get back is watermarked: four of them reached the
decks on 2026-09-22 before this was caught. `search` leaves them out of the
listing and the contact sheet, and `get` refuses them outright.

Unsplash's licence allows this use and does not require attribution; we credit
anyway, in the filename and in the `credit` field of scripts/deck-extras.json,
as the other two courses do.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import subprocess
import sys
import urllib.parse
import urllib.request

HERE = pathlib.Path(__file__).parent
PHOTOS = HERE.parent / "src" / "decks" / "photos"
SEARCH = "https://unsplash.com/napi/search/photos"
PHOTO = "https://unsplash.com/napi/photos"
#: A browser user-agent gets a 307 redirect away from the JSON endpoint; a
#: plain tool string is served.
UA = "comp3540-deck-photos/1.0"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def fetch_json(url: str) -> dict:
    # Some descriptions carry raw control characters, which strict JSON
    # rejects; the endpoint is not going to be fixed for us.
    return json.loads(fetch(url).decode("utf-8", "replace"), strict=False)


def slugify(value: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", value.lower())).strip("-")


def photo_meta(hit: dict) -> dict:
    return {
        "id": hit["id"],
        # Unsplash+ pictures are a paid licence and are delivered with a
        # watermark. They are mixed in with the free ones in every search
        # result, so they have to be filtered out rather than eyeballed.
        "plus": bool(hit.get("plus") or hit.get("premium")),
        "photographer": hit["user"]["name"],
        "description": hit.get("description") or hit.get("alt_description") or "",
        "raw": hit["urls"]["raw"],
        "small": hit["urls"]["small"],
        "page": hit["links"]["html"],
    }


def search(query: str, n: int, sheet_dir: pathlib.Path) -> list[dict]:
    url = f"{SEARCH}?{urllib.parse.urlencode({'query': query, 'per_page': n})}"
    # The endpoint ignores per_page below its default page of 20.
    all_hits = [photo_meta(h) for h in fetch_json(url)["results"]]
    hits = [h for h in all_hits if not h["plus"]][:n]
    plus = sum(1 for h in all_hits if h["plus"])
    if plus:
        print(f"({plus} Unsplash+ result(s) left out: paid licence, "
              f"delivered watermarked)")
    sheet_dir.mkdir(parents=True, exist_ok=True)
    tiles = []
    for k, h in enumerate(hits, 1):
        tile = sheet_dir / f"{k:02d}-{h['id']}.jpg"
        tile.write_bytes(fetch(h["small"]))
        tiles.append(str(tile))
        print(f"{k:2d}  {h['id']:14s}  {h['photographer'][:22]:22s}  "
              f"{h['description'][:60]}")
    if tiles:
        sheet = sheet_dir / f"{slugify(query)}.png"
        subprocess.run(
            ["magick", "montage", "-label", "%f", *tiles, "-tile", "4x",
             "-geometry", "360x260+6+6", "-background", "#1f2429",
             "-fill", "#f2f2f2", "-pointsize", "16", str(sheet)],
            check=True,
        )
        print(f"\ncontact sheet: {sheet}")
    return hits


def get(photo_id: str, width: int) -> pathlib.Path:
    try:
        hit = photo_meta(fetch_json(f"{PHOTO}/{photo_id}"))
    except urllib.error.HTTPError as e:
        raise SystemExit(f"no Unsplash photo with id {photo_id} ({e.code})")
    if hit["plus"]:
        raise SystemExit(
            f"{photo_id} is an Unsplash+ photo: the file is watermarked and "
            "the licence is not the free one. Pick another."
        )
    dest = PHOTOS / f"{slugify(hit['photographer'])}-{photo_id}-unsplash.jpg"
    PHOTOS.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(fetch(f"{hit['raw']}&w={width}&q=80&fm=jpg"))
    print(f"{dest.relative_to(HERE.parent)}  ({dest.stat().st_size // 1024} KB)"
          f"  Photo by {hit['photographer']} on Unsplash  {hit['page']}")
    return dest


def audit() -> int:
    """Re-check every Unsplash photo in the deck tree against the licence it
    was downloaded under. Unsplash+ can be granted to a picture after the
    fact, and four watermarked ones reached the decks before `get` refused
    them, so this is the check to run before a commit that adds photography.
    """
    bad = 0
    for f in sorted(PHOTOS.glob("*-unsplash.jpg")):
        stem = f.name[: -len("-unsplash.jpg")]
        # An id may itself contain hyphens, and so may a photographer's name,
        # so try the shortest trailing id first and keep the one that resolves.
        parts = stem.split("-")
        hit = None
        for k in (1, 2, 3):
            if k >= len(parts):
                break
            try:
                hit = photo_meta(fetch_json(f"{PHOTO}/{'-'.join(parts[-k:])}"))
                break
            except urllib.error.HTTPError:
                continue
        if hit is None:
            print(f"  ?     {f.name}  (id not recognised; check by hand)")
            bad += 1
        elif hit["plus"]:
            print(f"  PLUS  {f.name}  by {hit['photographer']} -- replace it")
            bad += 1
        else:
            print(f"  ok    {f.name}  by {hit['photographer']}")
    print(f"\n{bad} problem(s)")
    return 1 if bad else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search", help="list candidates and build a contact sheet")
    s.add_argument("query")
    s.add_argument("-n", type=int, default=8)
    s.add_argument("--sheet-dir", type=pathlib.Path,
                   default=pathlib.Path("/tmp/comp3540-photos"))
    sub.add_parser("audit", help="re-check the committed photos' licences")
    g = sub.add_parser("get", help="download one photo into src/decks/photos/")
    g.add_argument("photo_id")
    g.add_argument("--width", type=int, default=2000,
                   help="these are backgrounds; 2000px is plenty")
    args = ap.parse_args()

    if args.cmd == "search":
        search(args.query, args.n, args.sheet_dir)
    elif args.cmd == "audit":
        return audit()
    else:
        get(args.photo_id, args.width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
