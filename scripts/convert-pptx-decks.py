#!/usr/bin/env python3
"""Generate src/decks/*.deck.mdx from the 2024 theory PowerPoints.

These decks are GENERATED. Edit this converter and re-run it; do not hand-edit
a generated deck (the same rule comp1720 and comp4350 follow for their
Jekyll-sourced decks). See MATERIALS.md for what the source tree contains.

    python3 scripts/convert-pptx-decks.py [--materials ../comp3540-materials]

What it does with each slide:

  * drops the footer, slide-number and date placeholders, which are typed
    placeholders on the master (p:ph type="ftr"/"sldNum"/"dt") rather than
    content, so they can go structurally instead of by regex;
  * takes the slide heading from the first paragraph of the content
    placeholder and the bullets from the rest, using each paragraph's `lvl`
    for nesting;
  * turns the topic/citation placeholder (p:ph type="body" idx="13") into a
    citation line under the slide;
  * renders tables (p:graphicFrame) as Markdown tables;
  * extracts the raster images that are actually placed on the slide and big
    enough to be content rather than decoration, and emits them as Markdown
    images;
  * keeps the speaker notes in a ```comment fence, which astromotion does not
    render.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import pathlib
import re
import shutil
import sys
import zipfile
import xml.etree.ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
MC = "{http://schemas.openxmlformats.org/markup-compatibility/2006}"

EMU_PER_INCH = 914400
#: PowerPoint names a placed picture "Picture N" and a stock icon from its
#: icon library "Graphic N". The icons (374 of them across these decks) are
#: Microsoft clip art at exactly 1x1 inch, so a size threshold does not
#: separate them; the shape name does.
PICTURE_NAME_RE = re.compile(r"^Picture\b", re.I)
#: The poster frame of the narration video that used to be embedded on every
#: slide is a 960x540 webcam still of the lecturer. Those blips are no longer
#: referenced by any p:pic, and this converter only ever reads blips from a
#: p:pic, so they are never extracted -- but guard the size explicitly so a
#: future change cannot start publishing 294 photographs of a person.
POSTER_FRAME_PX = (960, 540)
#: Placeholder types that live on the master and carry no slide content.
CHROME_PH = {"ftr", "sldNum", "dt"}
#: The topic label / reading citation placeholder in this deck template.
SIDEBAR_PH_IDX = "13"

#: Slide text that is template chrome wherever it appears.
CHROME_RE = re.compile(
    r"^(ANU SCHOOL OF COMPUTING\b.*|\d{1,2}\s+[A-Z]{3,4}\s+\d{2}|\d{1,3})$"
)
#: A reading citation, e.g. "Fullerton p.102-103" or "Schell Ch. 2, 4".
CITATION_RE = re.compile(r"^(Fullerton|Schell)\b", re.I)
#: A full bibliographic reference typed into a heading or a sidebar, e.g.
#: "Rudolf Kremers. (2009) Level Design: Concept, Theory, and Practice" or
#: "Richard Rouse III (2005) Game Design: Theory & Practice, 2nd Ed. Ch. 23."
#: Those belong under the slide with the reading citations, never in the `##`.
REFERENCE_RE = re.compile(r"\(\d{4}\)|\b(?:Ch|Chs|pp?)\.\s*\d|\bEd\.")


def is_citation(text: str) -> bool:
    return bool(CITATION_RE.match(text) or REFERENCE_RE.search(text))

#: Fixes for source typos that would otherwise reach the site. Keep this
#: short: prefer fixing the converter to adding an entry here.
SOURCE_FIXUPS: dict[str, list[tuple[str, str]]] = {}

#: Pictures cleared for publication, keyed by the SHA-256 of the image file.
#: These decks teach from Fullerton and Schell and many of their figures are
#: scans or web grabs, which were fine behind Wattle under the educational
#: licence but are not fine on a public site. So a source picture is published
#: only if it appears here, and every entry says what to do with it:
#:
#:   kind "source"   publish the picture itself (it is cleared)
#:   kind "figure"   publish an original redrawing from src/decks/figures/,
#:                   made by scripts/make-deck-figures.py
#:   kind "snippet"  replace it with the MDX in scripts/deck-snippets/
#:   kind "drop"     leave it out, recording `note` in the deck source
#:
#: An unlisted picture is dropped with a generic note. Regenerate the review
#: material with --review to triage new pictures.
SNIPPETS = pathlib.Path(__file__).parent / "deck-snippets"
#: Replacement photography and screenshots, captured or re-sourced for this
#: site rather than lifted from the source slides. Unlike src/decks/figures/
#: these are not ours: every one carries its own credit.
DECKS = pathlib.Path(__file__).parent.parent / "src" / "decks"
MEDIA = DECKS / "media"

ALLOWED_IMAGES: dict[str, dict[str, str]] = json.loads(
    (pathlib.Path(__file__).parent / "deck-images.json").read_text()
) if (pathlib.Path(__file__).parent / "deck-images.json").exists() else {}

#: Images ADDED to slides that never carried a picture, keyed by deck slug.
#: deck-images.json can only ever replace a source picture, and the source
#: slides are mostly bullet lists, so this is the other half: photographs and
#: figures placed against a slide of the source deck.
#:
#: Each entry is anchored on `after_source_slide`, the slide number in the
#: PowerPoint, not the output slide number -- the source never changes, while
#: output numbers shift every time a figure is added ahead of them.
#:
#:   layout "bg cover"    a new full-bleed slide after the anchor (photographs)
#:   layout "bg contain"  a new slide fitting the whole image (screenshots)
#:   layout "figure"      a new slide holding it as a captioned .deck-figure,
#:                        the same treatment a redrawing from deck-images.json
#:                        gets (drawings, which want a caption, not a scrim)
#:   layout "inline"      into the anchor slide's .slide-media row
#:
#: `file` resolves under src/decks/, so `photos/x.jpg` and `figures/x.svg`.
EXTRA_IMAGES: dict[str, list[dict]] = json.loads(
    (pathlib.Path(__file__).parent / "deck-extras.json").read_text()
) if (pathlib.Path(__file__).parent / "deck-extras.json").exists() else {}

EXTRA_LAYOUTS = {"bg cover", "bg contain", "inline", "figure", "split"}

#: Per-slide formatting, one file per deck in scripts/deck-format/ so all
#: eighteen decks can be worked on independently. Keyed by the SOURCE slide
#: number for the same reason deck-extras.json is: output numbering shifts
#: whenever a slide ahead of it is split. scripts/deck-format.README.md is the
#: rulebook; this is the only place a slide's words may be rewritten, since
#: the decks themselves are generated.
FORMAT_DIR = pathlib.Path(__file__).parent / "deck-format"
#: Everything a slide entry may set. An unknown key is a typo, and a typo that
#: silently did nothing would look exactly like a rule that did not work.
FORMAT_KEYS = {
    "heading",       # replace the generated `##`
    "bullets",       # replace the body list; two spaces of indent per level
    "continuations", # headings for the 2nd, 3rd ... slide of a split list
    "split_after",   # break the list after these top-level bullet numbers
    "aside",         # "keep" (default) | "drop"
    "loose",         # "comment" (default) | "keep" | "drop"
    "table",         # "keep" (default) | "drop"
    "class",         # a slide class, e.g. "impact"
    "image_layout",  # "auto" (default) | "split" | "row"
    "split_image",   # {file, alt, credit}: a photograph for the right column
    "why",           # what the rewrite left out and why; kept as a comment
    "drop",          # true: emit no slide for this source slide at all
    "links",         # "keep" (default) or "drop" for the source's hyperlinks
}
LOOSE_MODES = {"comment", "keep", "drop"}


def load_deck_formats() -> dict[str, dict]:
    formats: dict[str, dict] = {}
    if not FORMAT_DIR.is_dir():
        return formats
    for path in sorted(FORMAT_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        slides = data.get("slides", {})
        if not isinstance(slides, dict):
            raise SystemExit(f"{path.name}: `slides` must be an object")
        for key, entry in slides.items():
            where = f"deck-format/{path.name}: slide {key}"
            if not re.fullmatch(r"\d+", str(key)):
                raise SystemExit(f"{where} is not a source slide number")
            unknown = set(entry) - FORMAT_KEYS
            if unknown:
                raise SystemExit(
                    f"{where} sets {', '.join(sorted(unknown))}; use one of "
                    + ", ".join(sorted(FORMAT_KEYS))
                )
            if entry.get("loose", "comment") not in LOOSE_MODES:
                raise SystemExit(f"{where} has an unknown `loose` mode")
            if entry.get("links", "keep") not in {"keep", "drop"}:
                raise SystemExit(f"{where} has an unknown `links` mode")
            if entry.get("image_layout", "auto") not in {"auto", "split", "row"}:
                raise SystemExit(f"{where} has an unknown `image_layout`")
            img = entry.get("split_image")
            if img is not None:
                if not img.get("file") or not img.get("alt"):
                    raise SystemExit(f"{where}: split_image needs a file and an alt")
                target = DECKS / img["file"].lstrip("./")
                if not target.exists():
                    raise SystemExit(
                        f"{where}: split_image points at {target}, which is missing"
                    )
        formats[path.stem] = data
    return formats


DECK_FORMATS = load_deck_formats()


# --------------------------------------------------------------------------
# fitting a slide to the canvas

#: A Reveal deck scales a fixed 1280x720 canvas, and the theme pads a slide by
#: 64px top and bottom, 80px each side: a content box of 1120x592. Body text
#: is 1.75rem (28px) at line-height 1.5, so a line costs 42px and a slide is
#: fourteen of them; the `##` takes 52px of that. A full-width line holds
#: about 74 characters, the content column of a 40% split about 42.
#:
#: Everything below is measured in those 42px lines. It is an estimate, and
#: deliberately a cheap one -- its whole job is to decide where to break a
#: list before anything is rendered. The instrument that decides whether a
#: slide really fits is `scripts/check-decks.sh`, which measures every slide
#: of every deck in a browser. See scripts/deck-format.README.md.
SLIDE_LINES = 14.0
HEADING_LINES = 1.25
#: Characters per line by bullet depth, full width and in a split slide's
#: 60% content column.
CHARS_PER_LINE = {0: 74, 1: 68, 2: 62}
SPLIT_CHARS_PER_LINE = {0: 42, 1: 38, 2: 34}
#: A .slide-media row caps an image at 30vh, plus its margins.
MEDIA_ROW_LINES = 5.6
#: li margin-block, as a fraction of a line.
BULLET_MARGIN_LINES = 0.2
#: A table row at 0.8em with the theme's cell padding, plus the block margins.
TABLE_ROW_LINES = 1.35
TABLE_CHROME_LINES = 1.0
#: A .slide-aside is 0.92em with a rule down its left and its own margins.
ASIDE_CHROME_LINES = 0.8


def text_lines(paras: list[tuple[int, str]], widths=CHARS_PER_LINE,
               scale: float = 1.0) -> float:
    """How many body lines a list of (level, text) paragraphs is likely to run."""
    total = 0.0
    for lvl, text in paras:
        width = widths.get(min(lvl, 2), widths[2])
        wrapped = max(1, -(-len(text) // max(8, int(width / scale))))
        total += wrapped * scale + BULLET_MARGIN_LINES
    return total


def bullet_groups(paras: list[tuple[int, str]]) -> list[list[tuple[int, str]]]:
    """Split a body list into top-level bullets with their children."""
    if not paras:
        return []
    top = min(lvl for lvl, _ in paras)
    groups: list[list[tuple[int, str]]] = []
    for para in paras:
        if para[0] <= top or not groups:
            groups.append([para])
        else:
            groups[-1].append(para)
    return groups


def chunk_groups(groups, budget: float, widths=CHARS_PER_LINE,
                 breaks: list[int] | None = None) -> list[list[tuple[int, str]]]:
    """Break a body list into slide-sized pieces, never inside a bullet.

    `breaks` (deck-format's `split_after`) is a list of top-level bullet
    numbers to break after; it wins over the budget, because where a list
    divides is a teaching decision and the budget only knows about pixels.
    """
    if not groups:
        return []
    if breaks:
        pieces, start = [], 0
        # 0 is a legitimate break: it puts the slide's table or figure on a
        # slide of its own and starts the list on the next one.
        for b in sorted({b for b in breaks if 0 <= b < len(groups)}):
            pieces.append([p for g in groups[start:b] for p in g])
            start = b
        pieces.append([p for g in groups[start:] for p in g])
        return pieces
    pieces, current, used = [], [], 0.0
    for group in groups:
        cost = text_lines(group, widths)
        if current and used + cost > budget:
            pieces.append(current)
            current, used = [], 0.0
        current += group
        used += cost
    if current:
        pieces.append(current)
    return pieces


def split_bg(src: str, alt: str, percent: int = 40) -> list[str]:
    """The image half of a two-column slide: content left, image right.

    astromotion turns a `bg right:N%` image into .split-layout, wrapping
    everything else on the slide into a .split-content column beside it. The
    image lands as a CSS background, so nothing on the slide carries its alt
    and the deck writes the description out for screen readers itself.
    """
    return [
        "",
        f"![bg right:{percent}%]({src})",
        "",
        f'<p class="deck-sr-only">{mdx_escape(alt)}</p>' if alt else "",
    ]


#: A heading the source typed as the list's first line. It is a heading when
#: it is short, unpunctuated, and the line under it is a sentence rather than
#: another label -- which is what separates "Components of a Level: Puzzles"
#: from an agenda of seven equally short items.
HEADING_CHARS = 58


def promote_heading(paras: list[tuple[int, str]]):
    """(heading, remaining paragraphs), or None if the first line is a bullet."""
    if len(paras) < 3:
        return None
    (lvl, first), (next_lvl, second) = paras[0], paras[1]
    if lvl != min(l for l, _ in paras):
        return None
    if len(first) > HEADING_CHARS or first.endswith((".", ",", ";", ":")):
        return None
    if next_lvl <= lvl and len(second) <= HEADING_CHARS:
        return None  # a list of labels, e.g. the agenda slide
    return first, paras[1:]


def format_paras(entries: list[str]) -> list[tuple[int, str]]:
    """deck-format's `bullets` as (level, text): two spaces of indent a level."""
    paras = []
    for line in entries:
        text = line.lstrip(" ")
        paras.append(((len(line) - len(text)) // 2, text))
    return paras


# --------------------------------------------------------------------------
# shapes


class Shape:
    """One placed shape, flattened out of the slide's group/choice nesting."""

    def __init__(self, el, kind, x, y, ph_type=None, ph_idx=None, name=""):
        self.el = el
        self.kind = kind  # "text" | "table" | "pic"
        self.x = x
        self.y = y
        self.ph_type = ph_type
        self.ph_idx = ph_idx
        self.name = name

    @property
    def is_chrome(self) -> bool:
        return self.ph_type in CHROME_PH

    @property
    def is_sidebar(self) -> bool:
        return self.ph_type == "body" and self.ph_idx == SIDEBAR_PH_IDX

    @property
    def is_main(self) -> bool:
        """The title or content placeholder that holds the slide's substance."""
        return self.ph_type == "title" or (self.ph_type is None and self.ph_idx == "1")


def _offset(el):
    """Absolute-ish position of a shape, for reading order."""
    xfrm = el.find(f"{P}spPr/{A}xfrm") or el.find(f"{P}grpSpPr/{A}xfrm") or el.find(f"{P}xfrm")
    if xfrm is None:
        for cand in el.iter(A + "xfrm"):
            xfrm = cand
            break
    if xfrm is None:
        return (0, 0)
    off = xfrm.find(A + "off")
    if off is None:
        return (0, 0)
    try:
        return (int(off.get("x", 0)), int(off.get("y", 0)))
    except (TypeError, ValueError):
        return (0, 0)


def collect_shapes(tree) -> list[Shape]:
    """Flatten a spTree into shapes, descending into groups and mc:Choice.

    PowerPoint wraps media and some effects in mc:AlternateContent; the
    Choice branch is the real content and the Fallback branch duplicates it,
    so only Choice is followed.
    """
    out: list[Shape] = []

    def walk(node):
        for el in node:
            tag = el.tag
            if tag == MC + "AlternateContent":
                choice = el.find(MC + "Choice")
                walk(choice if choice is not None else el.find(MC + "Fallback") or [])
            elif tag == P + "grpSp":
                walk(el)
            elif tag == P + "sp":
                ph = el.find(f"{P}nvSpPr/{P}nvPr/{P}ph")
                nv = el.find(f"{P}nvSpPr/{P}cNvPr")
                x, y = _offset(el)
                out.append(
                    Shape(
                        el,
                        "text",
                        x,
                        y,
                        ph.get("type") if ph is not None else None,
                        ph.get("idx") if ph is not None else None,
                        (nv.get("name") or "") if nv is not None else "",
                    )
                )
            elif tag == P + "graphicFrame":
                ph = el.find(f"{P}nvGraphicFramePr/{P}nvPr/{P}ph")
                x, y = _offset(el)
                out.append(
                    Shape(
                        el,
                        "table",
                        x,
                        y,
                        ph.get("type") if ph is not None else None,
                        ph.get("idx") if ph is not None else None,
                    )
                )
            elif tag == P + "pic":
                nv = el.find(f"{P}nvPicPr/{P}cNvPr")
                x, y = _offset(el)
                out.append(
                    Shape(
                        el,
                        "pic",
                        x,
                        y,
                        None,
                        None,
                        (nv.get("name") or "") if nv is not None else "",
                    )
                )

    walk(tree)
    return out


# --------------------------------------------------------------------------
# text


def para_text(par) -> str:
    return " ".join(para_lines(par))


def para_lines(par) -> list[str]:
    """A paragraph's text, split at the soft line breaks (<a:br/>).

    PowerPoint uses a break rather than a new paragraph for the second line of
    a heading, so without this a title comes out as "Theory:Play & Games".
    """
    lines, cur = [], []
    for el in par.iter():
        if el.tag == A + "t":
            cur.append(el.text or "")
        elif el.tag == A + "br":
            lines.append("".join(cur))
            cur = []
    lines.append("".join(cur))
    return [ln.replace("\xa0", " ").strip() for ln in lines if ln.strip()]


def para_level(par) -> int:
    ppr = par.find(A + "pPr")
    if ppr is None:
        return 0
    try:
        return int(ppr.get("lvl", 0))
    except (TypeError, ValueError):
        return 0


def shape_paragraphs(shape: Shape) -> list[tuple[int, str]]:
    """(indent level, text) for each non-empty paragraph, in document order."""
    out = []
    for par in shape.el.iter(A + "p"):
        lvl = para_level(par)
        for line in para_lines(par):
            if not CHROME_RE.match(line):
                out.append((lvl, line))
    return out


def mdx_escape(text: str) -> str:
    """Make a plain string safe inside MDX prose.

    MDX reads `{` as an expression and `<` as a tag, and there are no HTML
    comments; `&` is left alone because MDX accepts bare ampersands but not
    malformed entities, so any `&xyz;`-looking run is escaped too.
    """
    text = html.unescape(text)
    text = text.replace("\\", "\\\\")
    text = re.sub(r"&(?=[a-zA-Z#][a-zA-Z0-9]*;)", "&amp;", text)
    for ch in "{}<>":
        text = text.replace(ch, "\\" + ch)
    # Markdown emphasis/heading characters at the start of a bullet.
    text = re.sub(r"^([#>*_`|+-])", r"\\\1", text)
    return text


def bullets(paras: list[tuple[int, str]], sub_headings: bool = True) -> list[str]:
    """Render (level, text) pairs as a nested Markdown list.

    Body paragraphs in these decks sit at indent level 2 and deeper, so
    nesting is taken relative to the shallowest body level. A paragraph that
    drops back to level 0 in the middle of a body is a sub-heading in the
    source, not a bullet, so it becomes an h3.
    """
    if not paras:
        return []
    body_levels = [lvl for lvl, _ in paras if lvl > 0]
    if sub_headings and body_levels:
        base = min(body_levels)
    else:
        base = min(lvl for lvl, _ in paras)
    out: list[str] = []
    for lvl, text in paras:
        if lvl == 0 and base > 0 and sub_headings:
            out += ["", f"### {mdx_escape(text)}", ""]
        else:
            out.append("  " * max(0, lvl - base) + "- " + mdx_escape(text))
    return out


# --------------------------------------------------------------------------
# tables


def table_md(shape: Shape) -> list[str]:
    tbl = shape.el.find(f".//{A}tbl")
    if tbl is None:
        return []
    rows = []
    for tr in tbl.findall(A + "tr"):
        cells = []
        for tc in tr.findall(A + "tc"):
            parts = [para_text(p) for p in tc.iter(A + "p")]
            cell = " ".join(p for p in parts if p)
            cells.append(mdx_escape(cell).replace("|", "\\|"))
        if any(cells):
            rows.append(cells)
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]

    tbl_pr = tbl.find(A + "tblPr")
    has_header = tbl_pr is not None and tbl_pr.get("firstRow") == "1"
    if not has_header or not all(c.strip() for c in rows[0]):
        # No header row to use, and the build's axe check rejects a table whose
        # header cells are empty or invented. A list says the same thing.
        return ["- " + " — ".join(c for c in r if c.strip()) for r in rows]

    head, *body = rows
    out = ["| " + " | ".join(head) + " |", "| " + " | ".join(["---"] * width) + " |"]
    out += ["| " + " | ".join(r) + " |" for r in body]
    return out


# --------------------------------------------------------------------------
# images


def slide_rels(z: zipfile.ZipFile, n: int) -> dict[str, tuple[str, str]]:
    """rId -> (target, mode) for one slide."""
    try:
        raw = z.read(f"ppt/slides/_rels/slide{n}.xml.rels")
    except KeyError:
        return {}
    root = ET.fromstring(raw)
    out = {}
    for rel in root:
        out[rel.get("Id")] = (rel.get("Target", ""), rel.get("TargetMode", "Internal"))
    return out


def pic_target(shape: Shape, rels) -> tuple[str | None, int, int]:
    blip = shape.el.find(f".//{A}blip")
    rid = blip.get(R + "embed") if blip is not None else None
    ext = shape.el.find(f"{P}spPr/{A}xfrm/{A}ext")
    cx = int(ext.get("cx", 0)) if ext is not None else 0
    cy = int(ext.get("cy", 0)) if ext is not None else 0
    target = rels.get(rid, ("", ""))[0] if rid else ""
    return (target or None, cx, cy)


def external_links(shape_or_root, rels) -> list[str]:
    urls = []
    for el in shape_or_root.iter():
        rid = el.get(R + "id") or el.get(R + "embed")
        if not rid:
            continue
        target, mode = rels.get(rid, ("", ""))
        if mode == "External" and target.startswith("http"):
            urls.append(target)
    return urls


# --------------------------------------------------------------------------
# notes


def notes_text(z: zipfile.ZipFile, n: int) -> str:
    name = f"ppt/notesSlides/notesSlide{n}.xml"
    try:
        root = ET.fromstring(z.read(name))
    except KeyError:
        return ""
    lines = []
    for par in root.iter(A + "p"):
        text = para_text(par)
        if text and not CHROME_RE.match(text):
            lines.append(text)
    return "\n".join(lines).strip()


# --------------------------------------------------------------------------
# deck


def slugify(value: str) -> str:
    value = value.replace("&", " and ")
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return re.sub(r"-{2,}", "-", value)


def deck_slug(path: pathlib.Path) -> str:
    stem = path.stem
    stem = re.sub(r"^GameDev-Theory-", "", stem)
    m = re.match(r"Week(\d+)-(\d+)-(.*)$", stem)
    if m:
        week, part, rest = m.groups()
        return f"week{int(week):02d}-{part}-{slugify(rest)}"
    return slugify(stem)


#: Words left lowercase inside a title.
SMALL_WORDS = {"a", "an", "and", "as", "at", "for", "in", "of", "on", "or",
               "the", "to", "with"}


def title_case(text: str) -> str:
    """Title-case an ALL-CAPS slide title without mangling & or apostrophes."""
    words = text.split()
    out = []
    for i, w in enumerate(words):
        lower = w.lower()
        stripped = lower.strip(",:;")
        if i and stripped in SMALL_WORDS:
            out.append(lower)
        elif w.isupper() or w.istitle() or w.islower():
            out.append(lower[:1].upper() + lower[1:])
        else:
            out.append(w)
    return " ".join(out)


def title_from_slide(z, slide_names) -> str | None:
    """The deck's own name, from the "THEORY - WEEK n - NAME" line on slide 1.

    The filenames abbreviate ("Agile-Game-Dev", "Flow-Needs-Motivation") where
    the title slide spells the topic out, so prefer the slide.
    """
    if not slide_names:
        return None
    root = ET.fromstring(z.read(slide_names[0]))
    for par in root.iter(A + "p"):
        for line in para_lines(par):
            # Match on the WEEK n part, not the leading word: two decks
            # spell it "THOERY".
            m = re.match(r"^[A-Za-z]+\s*[–—-]\s*WEEK\s*\d+\s*[–—-]\s*(.+)$", line)
            if m:
                return title_case(m.group(1).strip())
    return None


def deck_title(path: pathlib.Path) -> str:
    stem = re.sub(r"^GameDev-Theory-Week\d+-\d+-", "", path.stem)
    stem = stem.replace("&", " and ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem[:1].upper() + stem[1:]


def deck_week(path: pathlib.Path) -> int | None:
    m = re.search(r"Week(\d+)-", path.stem)
    return int(m.group(1)) if m else None


def deck_extras(slug: str, decks_dir: pathlib.Path) -> dict[int, list[dict]]:
    """This deck's deck-extras.json entries, checked and grouped by anchor."""
    by_slide: dict[int, list[dict]] = {}
    for n, entry in enumerate(EXTRA_IMAGES.get(slug, []), 1):
        where = f"deck-extras.json: {slug}[{n}]"
        anchor = entry.get("after_source_slide")
        if not isinstance(anchor, int):
            raise SystemExit(f"{where} needs an integer after_source_slide")
        layout = entry.get("layout", "bg cover")
        if layout not in EXTRA_LAYOUTS:
            raise SystemExit(
                f"{where} has layout {layout!r}; use one of "
                + ", ".join(sorted(EXTRA_LAYOUTS))
            )
        # The build fails on a missing alt, and a background image reaches the
        # page as a CSS background with no element to carry one, so the deck
        # has to write the description out itself. Either way it is required.
        if not entry.get("alt"):
            raise SystemExit(f"{where} needs an alt")
        target = decks_dir / entry.get("file", "")
        if not entry.get("file") or not target.exists():
            raise SystemExit(f"{where} points at {target}, which is missing")
        by_slide.setdefault(anchor, []).append(entry)
    return by_slide


def extra_src(entry: dict) -> str:
    """An added image's path, relative to the deck beside it in src/decks."""
    return "./" + entry["file"].lstrip("./")


def figure_slide(entry: dict, heading: str) -> str:
    """A slide holding one figure and its credit, and nothing else.

    It keeps its parent slide's heading, unchanged: the two slides are one
    thought, the bullets and then the picture of what they describe.
    """
    fig: list[str] = []
    if heading:
        fig.append(f"## {mdx_escape(heading)}")
        fig.append("")
    fig.append('<figure class="deck-figure">')
    fig.append("")
    fig.append(f'![{mdx_escape(entry["alt"])}]({entry["src"]})')
    fig.append("")
    if entry.get("credit"):
        fig.append(f'<figcaption>{mdx_escape(entry["credit"])}</figcaption>')
        fig.append("")
    fig.append("</figure>")
    return "\n".join(fig).rstrip() + "\n"


def extra_slide(entry: dict) -> str:
    """A slide carrying one added image, full-bleed or fitted."""
    layout = entry.get("layout", "bg cover")
    lines = [
        # The theme's own full-bleed slide class: it lays the content out
        # bottom-left and paints a scrim between the photograph and the text,
        # as an image rather than a gradient so the PDF export keeps it.
        "{/* _class: hero */}",
        "",
        f'![{layout}]({extra_src(entry)})',
        "",
        # A background image is a CSS background, so nothing on the slide
        # describes it: say what it shows for anyone who cannot see it.
        f'<p class="deck-sr-only">{mdx_escape(entry["alt"])}</p>',
    ]
    caption = mdx_escape(entry.get("caption", ""))
    credit = mdx_escape(entry.get("credit", ""))
    if caption or credit:
        lines.append("")
        lines.append('<div class="photo-caption">')
        if caption:
            lines.append(caption)
        if credit:
            lines.append(f'<span class="photo-credit">{credit}</span>')
        lines.append("</div>")
    return "\n".join(lines).rstrip() + "\n"


def convert(path: pathlib.Path, decks_dir: pathlib.Path, verbose=False,
            review_dir: pathlib.Path | None = None,
            review_index: list | None = None) -> dict:
    slug = deck_slug(path)
    asset_dir = decks_dir / "assets" / slug
    if asset_dir.exists():
        shutil.rmtree(asset_dir)

    if review_index is None:
        review_index = []
    z = zipfile.ZipFile(path)
    names = z.namelist()
    slide_names = sorted(
        (n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
        key=lambda n: int(re.search(r"\d+", n.rsplit("/", 1)[1]).group()),
    )
    title = title_from_slide(z, slide_names) or deck_title(path)

    week_no = deck_week(path)
    extras = deck_extras(slug, decks_dir)
    slide_fmt = DECK_FORMATS.get(slug, {}).get("slides", {})
    used_formats: set[str] = set()
    # A photograph moved into a slide's right-hand column is no longer a
    # full-bleed slide of its own. Saying so here, rather than editing
    # deck-extras.json, keeps one deck's formatting inside one file.
    claimed = {
        f.get("split_image", {}).get("file", "").lstrip("./")
        for f in slide_fmt.values() if f.get("split_image")
    }
    used_anchors: set[int] = set()
    stats = {"slug": slug, "slides": 0, "images": 0, "figures": 0,
             "snippets": 0, "pending": 0, "tables": 0, "links": 0, "notes": 0,
             "omitted": 0, "extras": 0}
    out: list[str] = []
    hero: str | None = None
    subtitle = ""
    prev_heading = ""
    prev_aside: list[str] = []
    seen_notes: set[str] = set()
    seen_images: set[str] = set()
    seen_snippets: set[str] = set()
    omitted: list[tuple[int, str, str, str]] = []

    for i, sname in enumerate(slide_names, 1):
        root = ET.fromstring(z.read(sname))
        tree = root.find(f"{P}cSld/{P}spTree")
        rels = slide_rels(z, i)
        shapes = [s for s in collect_shapes(tree) if not s.is_chrome]

        main = [s for s in shapes if s.kind == "text" and s.is_main]
        sidebar = [s for s in shapes if s.kind == "text" and s.is_sidebar]
        loose = [s for s in shapes if s.kind == "text" and not s.is_main and not s.is_sidebar]
        tables = [s for s in shapes if s.kind == "table"]
        # Only real pictures: see PICTURE_NAME_RE above.
        pics = [s for s in shapes if s.kind == "pic" and PICTURE_NAME_RE.match(s.name)]

        # --- heading and body
        fmt = slide_fmt.get(str(i), {})
        used_formats.add(str(i))

        main_paras: list[tuple[int, str]] = []
        for s in sorted(main, key=lambda s: (s.y, s.x)):
            main_paras += shape_paragraphs(s)

        title_ph = any(s.ph_type == "title" for s in main)
        heading = ""
        heading_cites: list[str] = []
        if main_paras and title_ph:
            # A title placeholder holds the whole heading, split over soft
            # line breaks, sometimes with the week's readings appended -- and
            # in week05-2 with the two books the lecture is drawn from, which
            # is how every slide of that deck came to be headed by a
            # bibliography.
            lines = [t for _, t in main_paras]
            heading_cites = [t for t in lines if is_citation(t)]
            keep = [t for t in lines if not is_citation(t)]
            heading = " ".join(keep).strip()
            main_paras = []
        elif main_paras and main_paras[0][0] == 0:
            heading = main_paras[0][1]
            main_paras = main_paras[1:]

        # --- topic label and citation
        side_paras = []
        for s in sorted(sidebar, key=lambda s: (s.y, s.x)):
            side_paras += [t for _, t in shape_paragraphs(s)]
        # The sidebar holds a topic label, then reading citations, then (on
        # about a third of the slides) real explanatory bullets. Only the
        # label and citations are chrome; the rest is content.
        citations = [t for t in side_paras if is_citation(t)]
        rest = [t for t in side_paras if not is_citation(t)]
        topic = rest[0] if rest else ""
        aside = rest[1:]

        # Every deck closes with the same slide pointing at the 2024 Wattle
        # site. Replace it with a closing slide that will not go stale.
        if topic.strip().lower() == "the end":
            out.append(
                "\n".join(
                    [
                        "{/* _class: impact */}",
                        "",
                        "## Questions?",
                        "",
                        "See the [course website](/) for everything else: "
                        "workshops, assessments and resources.",
                    ]
                )
            )
            stats["slides"] += 1
            continue

        if i == 1:
            # Title slide: the deck template puts the whole title block in one
            # text box, so take the course/week line from it and drop the
            # author and email (which belong to the 2024 offering).
            week_line = f"Week {week_no} theory" if week_no else "Theory"
            out.append(
                "\n".join(
                    [
                        "{/* _class: title-slide */}",
                        "",
                        "<header>",
                        "",
                        f"# {mdx_escape(title)}",
                        "",
                        f"COMP3540/6540 Game Development — {mdx_escape(week_line)}",
                        "",
                        "Slides by Professor Penny Kyburz",
                        "",
                        "</header>",
                    ]
                )
            )
            stats["slides"] += 1
            continue

        # Schell's "lenses" get a slide of their own that repeats the previous
        # heading; name the slide after the lens instead.
        lens = None
        if main_paras:
            m = re.match(r"#?(\d+)\s+(The Lens of .+)$", main_paras[0][1])
            if m:
                lens = f"{m.group(2)} (lens {m.group(1)})"
                main_paras = main_paras[1:]

        # The source writes a new topic as the first line of the body about
        # forty times across the eighteen decks: the slide has no title
        # placeholder, so the heading it deserves is sitting in the list under
        # a bullet point while the slide itself is headed "... (cont.)".
        if not heading or heading.strip().lower() == topic.strip().lower():
            promoted = promote_heading(main_paras)
            if promoted:
                heading, main_paras = promoted

        # The template writes the deck's own topic into the heading of its
        # agenda slide ("Theory: Level Design"), which says nothing the page
        # title has not already said.
        if heading:
            bare = re.sub(r"^Theory:\s*", "", heading).strip()
            if bare.lower() in (title.lower(), topic.strip().lower()):
                heading = "Overview" if i == 2 else bare

        if not heading:
            # No heading anywhere on the slide (an agenda, a figure-only
            # slide, or a list continuing the slide before it). Never fall
            # back to "Slide N" -- it would be the page's visible title.
            if i == 2:
                heading = "Overview"
            elif prev_heading:
                heading = f"{prev_heading} (cont.)"
            else:
                heading = topic or title
        if fmt.get("heading"):
            heading = fmt["heading"]

        # --- the words, rewritten by deck-format.json if it says so
        if fmt.get("bullets") is not None:
            main_paras = format_paras(fmt["bullets"])

        # --- the blocks the slide carries besides its list
        aside_block: list[str] = []
        aside_lines = 0.0
        if aside and fmt.get("aside", "keep") != "drop":
            if aside == prev_aside:
                # The same definition box held on screen across a run of
                # slides. It belongs on the first of them; repeating it six
                # times (week09-2) reads as a rendering fault.
                pass
            else:
                aside_block += ["", '<aside class="slide-aside">', ""]
                aside_block += bullets([(0, t) for t in aside])
                aside_block += ["", "</aside>"]
                aside_lines = (text_lines([(0, t) for t in aside], scale=0.92)
                               + ASIDE_CHROME_LINES)
        prev_aside = aside

        table_block: list[str] = []
        table_lines = 0.0
        if fmt.get("table", "keep") != "drop":
            for s in sorted(tables, key=lambda s: (s.y, s.x)):
                md = table_md(s)
                if md:
                    stats["tables"] += 1
                    table_block += [""] + md
                    table_lines += (len(md) * TABLE_ROW_LINES
                                    + TABLE_CHROME_LINES)

        # Loose text boxes: labels off a diagram the copyright review dropped,
        # so on the rendered slide they are a second, unexplained list under
        # the first. Keep the words in the source as a comment (they are
        # Penny's) but do not show them, unless deck-format says otherwise.
        loose_paras: list[tuple[int, str]] = []
        for s in sorted(loose, key=lambda s: (s.y, s.x)):
            loose_paras += shape_paragraphs(s)
        # A reading citation is a citation wherever the source typed it, and
        # some of them sit in a loose text box that is otherwise dropped.
        for _, text in loose_paras:
            if is_citation(text) and text not in citations:
                citations.append(text)
        loose_paras = [(l, t) for l, t in loose_paras if not is_citation(t)]
        loose_block: list[str] = []
        loose_lines = 0.0
        loose_mode = fmt.get("loose", "comment")
        if loose_paras and loose_mode == "keep":
            loose_block = [""] + bullets([(0, t) for _, t in loose_paras])
            loose_lines = text_lines([(0, t) for _, t in loose_paras])
        elif loose_paras and loose_mode == "comment":
            loose_block = ["", "```comment", "Loose text boxes from the source "
                           "slide (labels off a diagram that was dropped):"]
            loose_block += [f"- {t}" for _, t in loose_paras]
            loose_block += ["```"]

        # --- images
        slide_images: list[tuple[str, str]] = []
        image_credits: list[str] = []
        slide_figures: list[dict] = []
        slide_snippets: list[tuple[str, str]] = []
        for s in sorted(pics, key=lambda s: (s.y, s.x)):
            target, cx, cy = pic_target(s, rels)
            if not target:
                continue
            src = target.replace("../", "ppt/")
            suffix = pathlib.Path(src).suffix.lower()
            if suffix in (".svg", ".emf", ".wmf"):
                continue  # icon duplicates of an adjacent png

            if src not in names:
                continue
            data = z.read(src)
            digest = hashlib.sha256(data).hexdigest()

            if review_dir is not None:
                rp = review_dir / f"{digest[:12]}{suffix}"
                if not rp.exists():
                    rp.write_bytes(data)
                review_index.append(
                    {
                        "sha256": digest,
                        "deck": slug,
                        "slide": i,
                        "heading": heading,
                        "citation": " / ".join(citations) or None,
                        "file": rp.name,
                    }
                )

            entry = ALLOWED_IMAGES.get(digest)
            if entry is None:
                omitted.append((i, heading, " / ".join(citations), ""))
                continue

            kind = entry.get("kind", "source")
            if kind == "drop":
                omitted.append((i, heading, " / ".join(citations),
                                entry.get("note", "")))
                continue
            if kind == "figure":
                # A redrawing, so it is published every time it is used: the
                # same model is taught on several slides across several decks.
                slide_figures.append({
                    "src": f"./figures/{entry['file']}",
                    "alt": entry.get("alt", ""),
                    "credit": entry.get("credit", ""),
                })
                stats["figures"] += 1
                continue
            if kind == "photo":
                # A screenshot re-sourced for this site. Until the capture is
                # made the slide keeps a note, so a brief can be committed and
                # filled in one entry at a time.
                if not (MEDIA / entry["file"]).exists():
                    omitted.append((i, heading, " / ".join(citations),
                                    f"screenshot pending re-capture: "
                                    f"{entry.get('credit', entry['file'])}"))
                    stats["pending"] += 1
                    continue
                slide_figures.append({
                    "src": f"./media/{entry['file']}",
                    "alt": entry.get("alt", ""),
                    "credit": entry.get("credit", ""),
                })
                stats["images"] += 1
                continue
            if kind == "snippet":
                if digest in seen_snippets:
                    continue  # a reference table held on screen across slides
                seen_snippets.add(digest)
                snippet = SNIPPETS / entry["file"]
                if not snippet.exists():
                    raise SystemExit(
                        f"deck-images.json points at {snippet}, which is missing"
                    )
                slide_snippets.append((snippet.read_text().rstrip(),
                                       entry.get("credit", "")))
                stats["snippets"] += 1
                continue

            if digest in seen_images:
                continue  # the same figure repeated on later slides
            seen_images.add(digest)

            asset_dir.mkdir(parents=True, exist_ok=True)
            dest = asset_dir / (entry.get("file") or f"{digest[:12]}{suffix}")
            dest.write_bytes(data)
            rel = f"./assets/{slug}/{dest.name}"
            # A figure is never the deck's hero: the card on /lectures/ wants
            # something representative of the topic, not a cited diagram.
            if hero is None and not entry.get("own_slide"):
                hero = f"/src/decks/assets/{slug}/{dest.name}"
            # The source has no alt text for these and the heading is not a
            # description of the image, so emit them as decorative (empty alt)
            # rather than inventing one.
            alt = mdx_escape(entry.get("alt", ""))
            credit = entry.get("credit", "")
            if entry.get("own_slide"):
                # A detailed diagram is unreadable at the 30vh an image gets
                # beside a bullet list, so give it a slide like a redrawing.
                slide_figures.append({"src": rel, "alt": alt, "credit": credit})
            else:
                slide_images.append((rel, alt))
                if credit:
                    image_credits.append(mdx_escape(credit))
            stats["images"] += 1

        for entry in extras.get(i, []):
            if entry.get("file", "").lstrip("./") in claimed:
                continue
            if entry.get("layout", "bg cover") not in ("inline", "split"):
                continue
            slide_images.append((extra_src(entry), mdx_escape(entry["alt"])))
            if entry.get("credit"):
                image_credits.append(mdx_escape(entry["credit"]))
            stats["extras"] += 1
            if entry.get("layout") == "split":
                fmt = {**fmt, "image_layout": "split"}

        if fmt.get("split_image") and not slide_images:
            img = fmt["split_image"]
            slide_images.append((extra_src(img), mdx_escape(img["alt"])))
            if img.get("credit"):
                image_credits.append(mdx_escape(img["credit"]))
            fmt = {**fmt, "image_layout": "split"}
            stats["extras"] += 1

        snippet_block: list[str] = []
        snippet_lines = 0.0
        for text, snippet_credit in slide_snippets:
            snippet_block += ["", text]
            snippet_lines += len(text.splitlines()) * TABLE_ROW_LINES
            if snippet_credit:
                image_credits.append(mdx_escape(snippet_credit))

        # --- the credit line: absolutely positioned, so it costs no height
        # and is repeated on every slide a long list is broken across.
        urls = [] if fmt.get("links") == "drop" else external_links(root, rels)
        stats["links"] += len(urls)
        # The sidebar's topic label is the deck's own subject ("Agile",
        # "Level Design", "Training"), printed on every slide of it. The page
        # title says that already, so the credit line carries the readings and
        # the picture credits only.
        credit = [mdx_escape(c) for c in citations + heading_cites]

        def credit_line(with_images: bool) -> list[str]:
            # The readings belong to the slide's subject, so they repeat on
            # every slide a list is broken across; a picture credit belongs to
            # the picture, and only one of those slides carries it.
            parts = credit + (image_credits if with_images else [])
            if not parts:
                return []
            return ["", f'<div class="image-credit">{" — ".join(parts)}</div>']

        # --- fit it to the canvas
        #
        # One image beside a list becomes a two-column slide (content left,
        # image right) whenever the list fits the narrower column: that is the
        # layout these lectures wanted all along, and it gives the picture
        # 100% of the slide height instead of the 30vh a .slide-media row
        # allows. Everything that does not fit is broken into a second slide
        # rather than shrunk -- a 0.64em bullet is not readable from the back
        # of a theatre, so type size is not a variable here.
        groups = bullet_groups(main_paras)
        layout_pref = fmt.get("image_layout", "auto")
        fixed_lines = (HEADING_LINES + aside_lines + table_lines
                       + snippet_lines + loose_lines)
        # A break that falls outside the list does nothing at all, which on
        # the page looks exactly like a rule that did not work -- the same
        # reason an unknown deck-format key stops the converter.
        breaks = fmt.get("split_after")
        if breaks and any(not 0 <= b < len(groups) for b in breaks):
            raise SystemExit(
                f"{slug} slide {i}: split_after {breaks} is out of range; "
                f"the list has {len(groups)} top-level bullets, so a break "
                f"may be 0-{len(groups) - 1}."
            )
        as_split = False
        if len(slide_images) == 1 and groups and layout_pref != "row":
            if layout_pref == "split" or (
                fixed_lines + text_lines(main_paras, SPLIT_CHARS_PER_LINE)
                <= SLIDE_LINES
            ):
                as_split = True
        media_lines = 0.0 if as_split or not slide_images else MEDIA_ROW_LINES
        budget = max(2.0, SLIDE_LINES - fixed_lines - media_lines)
        if as_split:
            # The photograph is on the first slide only, so only the first is
            # measured against the narrow column: a continuation slide has the
            # whole width and should be allowed to use it.
            pieces = chunk_groups(groups, budget, SPLIT_CHARS_PER_LINE,
                                  breaks)
            if len(pieces) > 1 and not breaks:
                rest = bullet_groups([p for piece in pieces[1:] for p in piece])
                pieces = [pieces[0]] + chunk_groups(rest, SLIDE_LINES - HEADING_LINES)
        else:
            pieces = chunk_groups(groups, budget, CHARS_PER_LINE, breaks)

        media_block: list[str] = []
        if as_split:
            media_block = split_bg(*slide_images[0])
        elif slide_images:
            # A row, so several images on one slide scale together instead of
            # stacking off the bottom of it.
            media_block = ["", '<div class="slide-media">', ""]
            media_block += [f"![{alt}]({src})" for src, alt in slide_images]
            media_block += ["", "</div>"]

        comment_block: list[str] = []
        if fmt.get("why"):
            # A rewrite that drops a sentence has to say so somewhere the next
            # convenor will find it, and the slide it happened on is that
            # place. ```comment is stripped from the built page.
            comment_block += ["", "```comment", f'cut: {fmt["why"]}', "```"]
        if omitted and omitted[-1][0] == i:
            notes_for_slide = [o for o in omitted if o[0] == i]
            comment_block += ["", "```comment"]
            for _, h, c, note in notes_for_slide:
                comment_block.append(note or (
                    "figure omitted pending copyright review"
                    + (f" (see {c})" if c else "")
                ))
            comment_block.append("```")

        # --- speaker notes, kept but not rendered
        notes = notes_text(z, i)
        if notes in seen_notes:
            notes = ""  # several decks repeat one stale note on every slide
        if notes:
            seen_notes.add(notes)
            stats["notes"] += 1
            comment_block += ["", "```comment", notes, "```"]

        # A PowerPoint build-up: four source slides revealing one bullet at a
        # time, which convert to four slides each carrying a fragment. The
        # last of them takes the whole list (`bullets`) and the ones before it
        # are dropped -- while still anchoring their own figures and added
        # images, which are placed against the source slide, not against what
        # became of it.
        continuations = fmt.get("continuations") or []
        for k, piece in enumerate([] if fmt.get("drop") else (pieces or [[]])):
            body: list[str] = []
            if k == 0 and fmt.get("class"):
                body += [f'{{/* _class: {fmt["class"]} */}}', ""]
            if k == 0:
                slide_heading = lens or heading
            elif k - 1 < len(continuations):
                slide_heading = continuations[k - 1]
            elif heading.endswith("(cont.)"):
                slide_heading = heading
            else:
                slide_heading = f"{heading} (cont.)"
            body.append(f"## {mdx_escape(slide_heading)}\n")
            body += bullets(piece, sub_headings=fmt.get("bullets") is None)
            if k == 0:
                body += aside_block + table_block + media_block + snippet_block
                body += loose_block
            body += credit_line(k == 0)
            if k == 0 and urls:
                # MDX parses <url> as JSX, so autolinks must be explicit
                # links; and a link on a slide is read out, not typed in, so
                # it is labelled with its host rather than printed in full.
                body += [""] + [
                    f"- [{re.sub(r'^www[.]', '', u.split('/')[2])}]({u})"
                    for u in dict.fromkeys(urls)
                ]
            if k == 0:
                body += comment_block
            out.append("\n".join(x for x in body if x is not None).rstrip() + "\n")
            stats["slides"] += 1

        if heading and not heading.endswith("(cont.)"):
            prev_heading = heading

        # A redrawn figure gets a slide of its own. Beside a bullet list the
        # theme caps an image at 30vh, which is too small for any label to be
        # read from the back of a theatre; on its own slide it gets 60vh.
        for entry in slide_figures:
            out.append(figure_slide(entry, heading or prev_heading))
            stats["slides"] += 1

        # Added images (deck-extras.json), anchored on this source slide.
        used_anchors.add(i)
        for entry in extras.get(i, []):
            if entry.get("file", "").lstrip("./") in claimed:
                continue
            layout = entry.get("layout", "bg cover")
            if layout in ("inline", "split"):
                continue
            if layout == "figure":
                out.append(figure_slide(
                    {"src": extra_src(entry), "alt": entry.get("alt", ""),
                     "credit": entry.get("credit", "")},
                    entry.get("heading") or heading or prev_heading))
            else:
                out.append(extra_slide(entry))
            stats["slides"] += 1
            stats["extras"] += 1

    # The title slide and the closing slide are emitted without reaching the
    # extras block, and a typo in an anchor would otherwise drop an image
    # silently, so say so instead.
    stray = sorted(set(slide_fmt) - used_formats, key=int)
    if stray:
        raise SystemExit(
            f"deck-format/{slug}.json: slide(s) {', '.join(stray)} are not "
            "content slides of this deck (the title and closing slides are "
            "generated, and the deck has "
            f"{len(slide_names)} source slides)"
        )
    unused = sorted(set(extras) - used_anchors)
    if unused:
        raise SystemExit(
            f"deck-extras.json: {slug} anchors source slide(s) "
            f"{', '.join(str(u) for u in unused)}, which carry no content"
        )

    # A deck with no publishable source picture has no hero for its card on
    # /lectures/; an added photograph is a better one than the site default.
    # A drawing is not: the cards want something representative of the topic,
    # and an SVG diagram on a card reads as a rendering fault.
    if hero is None:
        for entry in EXTRA_IMAGES.get(slug, []):
            f = entry.get("file", "").lstrip("./")
            if f.startswith("photos/") and entry.get("layout") != "inline":
                hero = f"/src/decks/{f}"
                break

    # A pending screenshot also leaves a note on the slide, but it is not a
    # picture we decided to drop -- do not count it twice.
    stats["omitted"] = len(omitted) - stats["pending"]
    week = week_no
    description = (
        f"Week {week} theory: {title.lower()}." if week else f"Theory: {title.lower()}."
    )
    fm = ["---", f'title: "{title}"', f'description: "{description}"']
    if hero:
        fm.append(f'image: "{hero}"')
    fm.append("---")
    fm.append("")
    fm.append(
        "{/* Generated by scripts/convert-pptx-decks.py from the 2024 theory "
        "PowerPoints. Do not hand-edit: change the converter and re-run it. */}"
    )
    fm.append("")

    text = "\n".join(fm) + "\n" + "\n\n---\n\n".join(out)
    for old, new in SOURCE_FIXUPS.get(slug, []):
        text = text.replace(old, new)

    dest = decks_dir / f"{slug}.deck.mdx"
    dest.write_text(text)
    if verbose:
        print(
            f"  {stats['slides']:3d} slides  {stats['images']:3d} images  "
            f"{stats['tables']:2d} tables  {stats['notes']:3d} notes  -> {dest.name}"
        )
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    here = pathlib.Path(__file__).resolve().parent.parent
    ap.add_argument("--materials", default=str(here.parent / "comp3540-materials"))
    ap.add_argument("--decks", default=str(here / "src" / "decks"))
    ap.add_argument("--only", help="convert only decks whose slug contains this")
    ap.add_argument(
        "--review",
        metavar="DIR",
        help="also write every source picture and a manifest here, for the "
        "copyright triage that fills scripts/deck-images.json",
    )
    args = ap.parse_args()

    theory = pathlib.Path(args.materials) / "2024" / "Theory"
    if not theory.is_dir():
        print(f"no theory directory at {theory}", file=sys.stderr)
        return 1
    decks = pathlib.Path(args.decks)
    decks.mkdir(parents=True, exist_ok=True)

    review_dir = None
    review_index: list = []
    if args.review:
        review_dir = pathlib.Path(args.review)
        review_dir.mkdir(parents=True, exist_ok=True)

    sources = sorted(theory.glob("*/*.pptx"), key=lambda p: (deck_week(p) or 99, p.stem))
    total = {"slides": 0, "images": 0, "figures": 0, "snippets": 0,
             "pending": 0, "tables": 0, "links": 0, "omitted": 0, "extras": 0}
    n = 0
    for src in sources:
        if args.only and args.only not in deck_slug(src):
            continue
        stats = convert(src, decks, verbose=True, review_dir=review_dir,
                        review_index=review_index)
        n += 1
        for k in total:
            total[k] += stats[k]

    if review_dir is not None:
        (review_dir / "manifest.json").write_text(json.dumps(review_index, indent=2))
        uniq = {r["sha256"] for r in review_index}
        print(f"\nreview: {len(uniq)} distinct pictures -> {review_dir}")

    unknown = sorted(set(EXTRA_IMAGES) - {deck_slug(p) for p in sources})
    if unknown:
        raise SystemExit(
            "deck-extras.json names deck(s) that do not exist: "
            + ", ".join(unknown)
        )

    print(
        f"\n{n} deck(s): {total['slides']} slides, {total['images']} images published, "
        f"{total['figures']} figures redrawn, {total['snippets']} tables from "
        f"figures, {total['pending']} screenshots pending, "
        f"{total['omitted']} pictures dropped, {total['extras']} images added, "
        f"{total['tables']} tables, {total['links']} external links"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
