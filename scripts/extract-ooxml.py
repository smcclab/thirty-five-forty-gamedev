"""Pull the text out of .pptx / .docx without unpacking their media.

pptx -> one markdown file per deck: "## Slide N" + the text of each shape, then
the speaker notes. docx -> one markdown file: paragraphs, with Heading styles
turned into markdown headings and tables rendered as pipe tables.
"""
import re, sys, zipfile, pathlib
import xml.etree.ElementTree as ET

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def slide_text(xml: bytes) -> list[str]:
    root = ET.fromstring(xml)
    out = []
    for para in root.iter(A + "p"):
        line = "".join(t.text or "" for t in para.iter(A + "t"))
        line = line.strip()
        if line:
            out.append(line)
    return out


def pptx_to_md(path: pathlib.Path) -> str:
    parts = [f"# {path.name}\n"]
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        slides = sorted(
            (n for n in names if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)),
            key=lambda n: int(re.search(r"(\d+)", n.rsplit("/", 1)[1]).group(1)),
        )
        media = [n for n in names if n.startswith("ppt/media/")]
        vids = [n for n in media if n.lower().endswith((".mp4", ".mov", ".m4v", ".wmv", ".avi"))]
        auds = [n for n in media if n.lower().endswith((".m4a", ".mp3", ".wav", ".wma"))]
        imgs = [n for n in media if n.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".emf", ".wmf"))]
        parts.append(
            f"_{len(slides)} slides; media: {len(imgs)} images, {len(vids)} video, {len(auds)} audio_\n"
        )
        for i, s in enumerate(slides, 1):
            lines = slide_text(z.read(s))
            parts.append(f"\n## Slide {i}\n")
            parts.extend(l + "\n" for l in lines)
            notes = f"ppt/notesSlides/notesSlide{i}.xml"
            if notes in names:
                nl = [l for l in slide_text(z.read(notes)) if l != str(i)]
                if nl:
                    parts.append("\n> **Notes:** " + " ".join(nl) + "\n")
    return "".join(parts)


def docx_to_md(path: pathlib.Path) -> str:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(W + "body")
    out = [f"# {path.name}\n"]

    def para_md(p) -> str:
        text = "".join(t.text or "" for t in p.iter(W + "t")).strip()
        if not text:
            return ""
        style = p.find(f"{W}pPr/{W}pStyle")
        val = style.get(W + "val") if style is not None else ""
        m = re.fullmatch(r"Heading(\d)", val or "")
        if m:
            return "#" * (int(m.group(1)) + 1) + " " + text
        numpr = p.find(f"{W}pPr/{W}numPr")
        if numpr is not None:
            return "- " + text
        return text

    for el in body:
        if el.tag == W + "p":
            md = para_md(el)
            if md:
                out.append(md + "\n")
        elif el.tag == W + "tbl":
            rows = []
            for tr in el.findall(W + "tr"):
                cells = [
                    " ".join(
                        x for x in (para_md(p) for p in tc.iter(W + "p")) if x
                    ).replace("|", "\\|")
                    for tc in tr.findall(W + "tc")
                ]
                rows.append(cells)
            if rows:
                width = max(len(r) for r in rows)
                out.append("\n")
                for i, r in enumerate(rows):
                    r = r + [""] * (width - len(r))
                    out.append("| " + " | ".join(r) + " |\n")
                    if i == 0:
                        out.append("| " + " | ".join(["---"] * width) + " |\n")
                out.append("\n")
    return "".join(out)


src = pathlib.Path(sys.argv[1])
dst = pathlib.Path(sys.argv[2])
for f in sorted(src.rglob("*")):
    if f.suffix.lower() not in (".pptx", ".docx") or f.name.startswith("~$"):
        continue
    rel = f.relative_to(src).with_suffix(".md")
    out = dst / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        md = pptx_to_md(f) if f.suffix.lower() == ".pptx" else docx_to_md(f)
        out.write_text(md)
        print(f"{len(md):8d}  {rel}")
    except Exception as e:
        print(f"   FAIL  {rel}: {e}")
