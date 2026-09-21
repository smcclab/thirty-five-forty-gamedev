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

#: Fixes for source typos that would otherwise reach the site. Keep this
#: short: prefer fixing the converter to adding an entry here.
SOURCE_FIXUPS: dict[str, list[tuple[str, str]]] = {}

#: Pictures cleared for publication, keyed by the SHA-256 of the image file.
#: These decks teach from Fullerton and Schell and many of their figures are
#: scans or web grabs, which were fine behind Wattle under the educational
#: licence but are not fine on a public site. So nothing is published unless
#: it appears here with an alt text and a credit. Everything else is replaced
#: in the deck by a note recording what was left out.
#: Regenerate the review material with --review to triage new pictures.
ALLOWED_IMAGES: dict[str, dict[str, str]] = json.loads(
    (pathlib.Path(__file__).parent / "deck-images.json").read_text()
) if (pathlib.Path(__file__).parent / "deck-images.json").exists() else {}


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


def bullets(paras: list[tuple[int, str]]) -> list[str]:
    """Render (level, text) pairs as a nested Markdown list.

    Body paragraphs in these decks sit at indent level 2 and deeper, so
    nesting is taken relative to the shallowest body level. A paragraph that
    drops back to level 0 in the middle of a body is a sub-heading in the
    source, not a bullet, so it becomes an h3.
    """
    if not paras:
        return []
    body_levels = [lvl for lvl, _ in paras if lvl > 0]
    base = min(body_levels) if body_levels else min(lvl for lvl, _ in paras)
    out: list[str] = []
    for lvl, text in paras:
        if lvl == 0 and base > 0:
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


def deck_title(path: pathlib.Path) -> str:
    stem = re.sub(r"^GameDev-Theory-Week\d+-\d+-", "", path.stem)
    stem = stem.replace("&", " and ").replace("-", " ")
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem[:1].upper() + stem[1:]


def deck_week(path: pathlib.Path) -> int | None:
    m = re.search(r"Week(\d+)-", path.stem)
    return int(m.group(1)) if m else None


def convert(path: pathlib.Path, decks_dir: pathlib.Path, verbose=False,
            review_dir: pathlib.Path | None = None,
            review_index: list | None = None) -> dict:
    slug = deck_slug(path)
    title = deck_title(path)
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

    week_no = deck_week(path)
    stats = {"slug": slug, "slides": 0, "images": 0, "tables": 0, "links": 0,
             "notes": 0, "omitted": 0}
    out: list[str] = []
    hero: str | None = None
    subtitle = ""
    prev_heading = ""
    seen_notes: set[str] = set()
    seen_images: set[str] = set()
    omitted: list[tuple[int, str, str]] = []

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
        main_paras: list[tuple[int, str]] = []
        for s in sorted(main, key=lambda s: (s.y, s.x)):
            main_paras += shape_paragraphs(s)

        title_ph = any(s.ph_type == "title" for s in main)
        heading = ""
        heading_cites: list[str] = []
        if main_paras and title_ph:
            # A title placeholder holds the whole heading, split over soft
            # line breaks, sometimes with the week's readings appended.
            lines = [t for _, t in main_paras]
            heading_cites = [t for t in lines if CITATION_RE.match(t)]
            keep = [t for t in lines if not CITATION_RE.match(t)]
            heading = " ".join(keep).replace(": ", ": ").strip()
            main_paras = []
        elif main_paras and main_paras[0][0] == 0:
            heading = main_paras[0][1]
            main_paras = main_paras[1:]
        elif main_paras:
            # No level-0 first paragraph: this slide continues the previous
            # one. Do not promote a bullet to the heading.
            heading = f"{prev_heading} (cont.)" if prev_heading else (topic or title)

        # --- topic label and citation
        side_paras = []
        for s in sorted(sidebar, key=lambda s: (s.y, s.x)):
            side_paras += [t for _, t in shape_paragraphs(s)]
        # The sidebar holds a topic label, then reading citations, then (on
        # about a third of the slides) real explanatory bullets. Only the
        # label and citations are chrome; the rest is content.
        citations = [t for t in side_paras if CITATION_RE.match(t)]
        rest = [t for t in side_paras if not CITATION_RE.match(t)]
        topic = rest[0] if rest else ""
        aside = rest[1:]

        body: list[str] = []

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

        if lens:
            body.append(f"## {mdx_escape(lens)}\n")
        else:
            body.append(f"## {mdx_escape(heading)}\n")

        body += bullets(main_paras)

        if aside:
            body.append("")
            body.append('<aside class="slide-aside">')
            body.append("")
            body += bullets([(0, t) for t in aside])
            body.append("")
            body.append("</aside>")

        for s in sorted(tables, key=lambda s: (s.y, s.x)):
            md = table_md(s)
            if md:
                stats["tables"] += 1
                body.append("")
                body += md

        loose_paras: list[tuple[int, str]] = []
        for s in sorted(loose, key=lambda s: (s.y, s.x)):
            loose_paras += shape_paragraphs(s)
        if loose_paras:
            body.append("")
            body += bullets([(0, t) for _, t in loose_paras])

        # --- images
        slide_images: list[str] = []
        image_credits: list[str] = []
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
                omitted.append((i, heading, " / ".join(citations)))
                continue
            if digest in seen_images:
                continue  # the same figure repeated on later slides
            seen_images.add(digest)

            asset_dir.mkdir(parents=True, exist_ok=True)
            dest = asset_dir / (entry.get("file") or f"{digest[:12]}{suffix}")
            dest.write_bytes(data)
            rel = f"./assets/{slug}/{dest.name}"
            if hero is None:
                hero = f"/src/decks/assets/{slug}/{dest.name}"
            # The source has no alt text for these and the heading is not a
            # description of the image, so emit them as decorative (empty alt)
            # rather than inventing one.
            alt = mdx_escape(entry.get("alt", ""))
            credit = entry.get("credit", "")
            slide_images.append(f"![{alt}]({rel})")
            if credit:
                image_credits.append(mdx_escape(credit))
            stats["images"] += 1

        if slide_images:
            # A row, so several images on one slide scale together instead of
            # stacking off the bottom of it.
            body.append("")
            body.append('<div class="slide-media">')
            body.append("")
            body += slide_images
            body.append("")
            body.append("</div>")

        # --- citation and links
        urls = external_links(root, rels)
        stats["links"] += len(urls)
        credit = []
        if topic:
            credit.append(mdx_escape(topic))
        credit += [mdx_escape(c) for c in citations + heading_cites]
        credit += image_credits
        if credit:
            body.append("")
            body.append(f'<div class="image-credit">{" — ".join(credit)}</div>')
        if urls:
            body.append("")
            # MDX parses <url> as JSX, so autolinks must be explicit links.
            body += [f"- [{u}]({u})" for u in dict.fromkeys(urls)]

        if omitted and omitted[-1][0] == i:
            notes_for_slide = [o for o in omitted if o[0] == i]
            body.append("")
            body.append("```comment")
            for _, h, c in notes_for_slide:
                body.append(
                    f"figure omitted pending copyright review"
                    + (f" (see {c})" if c else "")
                )
            body.append("```")

        # --- speaker notes, kept but not rendered
        notes = notes_text(z, i)
        if notes in seen_notes:
            notes = ""  # several decks repeat one stale note on every slide
        if notes:
            seen_notes.add(notes)
            stats["notes"] += 1
            body.append("")
            body.append("```comment")
            body.append(notes)
            body.append("```")

        if heading and not heading.endswith("(cont.)"):
            prev_heading = heading
        out.append("\n".join(body).rstrip() + "\n")
        stats["slides"] += 1

    stats["omitted"] = len(omitted)
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
    total = {"slides": 0, "images": 0, "tables": 0, "links": 0, "omitted": 0}
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

    print(
        f"\n{n} deck(s): {total['slides']} slides, {total['images']} images published, "
        f"{total['omitted']} figures omitted pending review, "
        f"{total['tables']} tables, {total['links']} external links"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
