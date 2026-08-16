#!/usr/bin/env python3
"""Assemble and render the NBEO study guides to print-ready PDF.

Each guide is a manifest of HTML fragments under content/<guide>/.
The builder injects heading ids, generates a leader-dotted table of
contents with real page numbers via target-counter(), wraps everything
in a paged-media shell, and renders with WeasyPrint.

Usage:
    python3 build.py            # build all guides
    python3 build.py part1      # build one guide
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
CSS = ROOT / "assets" / "print.css"

EDITION = "NBEO Board Review \u00b7 2026\u20132027 blueprint edition"

GUIDES = {
    "part1": {
        "out": "NBEO_Part_I_ABS_Study_Guide.pdf",
        "title": "NBEO Part I \u00b7 Applied Basic Science \u00b7 Study Guide",
        "short": "Part I ABS \u00b7 Applied Basic Science",
        "description": "Full-scope preparation for NBEO Part I Applied Basic Science: "
        "anatomy, physiology, biochemistry, optics, pharmacology, pathology, and "
        "systemic health, organised against the published content matrix.",
        "keywords": "NBEO, Part I, ABS, applied basic science, optometry boards, "
        "ocular anatomy, optics, pharmacology, board review",
    },
    "part2": {
        "out": "NBEO_Part_II_PAM_TMOD_Study_Guide.pdf",
        "title": "NBEO Part II \u00b7 Patient Assessment and Management / TMOD \u00b7 Study Guide",
        "short": "Part II PAM / TMOD",
        "description": "Full-scope preparation for NBEO Part II Patient Assessment "
        "and Management including the Treatment and Management of Ocular Disease "
        "section, organised against the published content outline.",
        "keywords": "NBEO, Part II, PAM, TMOD, patient assessment and management, "
        "treatment and management of ocular disease, optometry boards, board review",
    },
    "part3": {
        "out": "NBEO_Part_III_PEPS_Study_Guide.pdf",
        "title": "NBEO Part III \u00b7 Patient Encounters and Performance Skills \u00b7 Study Guide",
        "short": "Part III PEPS",
        "description": "Station-by-station and item-by-item preparation for NBEO "
        "Part III Patient Encounters and Performance Skills, built on the candidate "
        "guide, blueprint, and the official skills evaluation forms.",
        "keywords": "NBEO, Part III, PEPS, patient encounters, performance skills, "
        "biomicroscopy, gonioscopy, applanation tonometry, BIO, fundus lens, "
        "optometry boards, board review",
    },
}

SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="author" content="NBEO Board Review">
<meta name="description" content="{description}">
<meta name="keywords" content="{keywords}">
<meta name="generator" content="nbeo build.py + WeasyPrint">
<style>
{css}
body {{ string-set: guide-short "{short}", guide-edition "{edition}"; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""

H1 = re.compile(r'<h1(?P<attrs>[^>]*class="[^"]*\b(?:chapter)\b[^"]*"[^>]*)>(?P<inner>.*?)</h1>', re.S)
H1FM = re.compile(r'<(?P<tag>section|div)[^>]*class="[^"]*\bfm\b[^"]*"[^>]*>\s*<h1(?P<attrs>[^>]*)>(?P<inner>.*?)</h1>', re.S)
H2 = re.compile(r"<h2(?P<attrs>[^>]*)>(?P<inner>.*?)</h2>", re.S)
ID_ATTR = re.compile(r'\bid="([^"]+)"')
TAGS = re.compile(r"<[^>]+>")
NUMSPAN = re.compile(r'<span class="num">.*?</span>', re.S)


def slug(text: str) -> str:
    text = NUMSPAN.sub(" ", text)
    text = TAGS.sub(" ", text)
    text = text.replace("&amp;", "and").replace("&nbsp;", " ")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:64] or "sec"


def clean_label(inner: str) -> str:
    inner = NUMSPAN.sub("", inner)
    inner = TAGS.sub("", inner)
    inner = inner.replace("&amp;", "&").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", inner).strip()


def chapter_number(inner: str) -> str:
    m = re.search(r'<span class="num">(.*?)</span>', inner, re.S)
    if not m:
        return ""
    return re.sub(r"\s+", " ", TAGS.sub("", m.group(1))).strip()


def inject_ids(html: str) -> tuple[str, list[dict]]:
    """Give every chapter/front-matter h1 and h2 a stable id; return the outline."""
    used: set[str] = set()
    outline: list[dict] = []

    def unique(base: str) -> str:
        cand = base
        n = 2
        while cand in used:
            cand = f"{base}-{n}"
            n += 1
        used.add(cand)
        return cand

    events: list[tuple[int, int, str, str, str]] = []  # start, end, level, id, label

    for pat, level in ((H1, 1), (H1FM, 1), (H2, 2)):
        for m in pat.finditer(html):
            attrs = m.group("attrs") or ""
            inner = m.group("inner")
            existing = ID_ATTR.search(attrs)
            base = existing.group(1) if existing else slug(inner)
            notoc = "notoc" in attrs
            events.append((m.start(), m.end(), level, base, inner, notoc))

    events.sort(key=lambda e: e[0])

    # de-duplicate overlapping matches (fm h1 also matched by nothing else, safe)
    seen_spans: set[tuple[int, int]] = set()
    out: list[str] = []
    cursor = 0
    for start, end, level, base, inner, notoc in events:
        if (start, end) in seen_spans or start < cursor:
            continue
        seen_spans.add((start, end))
        chunk = html[start:end]
        hid = unique(base)
        if ID_ATTR.search(chunk.split(">", 1)[0]):
            chunk = ID_ATTR.sub(f'id="{hid}"', chunk, count=1)
        else:
            # insert id on the heading tag itself (first <h1/<h2 in chunk)
            chunk = re.sub(r"<(h[12])", rf'<\1 id="{hid}"', chunk, count=1)
        out.append(html[cursor:start])
        out.append(chunk)
        cursor = end
        if not notoc:
            outline.append(
                {
                    "level": level,
                    "id": hid,
                    "label": clean_label(inner),
                    "num": chapter_number(inner) if level == 1 else "",
                }
            )
    out.append(html[cursor:])
    return "".join(out), outline


RELAXABLE = ("box", "drill", "numbers", "checklist", "algo", "recap")
BLOCK_OPEN = re.compile(
    r'<(?P<tag>div|section|table)\b[^>]*\bclass="(?P<cls>[^"]*)"[^>]*>', re.I
)
# A page holds roughly this much markup. Blocks past the threshold, and any
# block wrapping a multi-row table, are allowed to break across pages.
TALL_CHARS = 2600
TALL_ROWS = 9


def _matching_close(html: str, tag: str, after: int) -> int:
    """Index just past the close tag that balances an opening tag at `after`."""
    token = re.compile(rf"</?{tag}\b", re.I)
    depth = 1
    pos = after
    while depth:
        m = token.search(html, pos)
        if not m:
            return len(html)
        depth += -1 if m.group(0).startswith("</") else 1
        pos = m.end()
    return html.index(">", pos - 1) + 1 if depth == 0 else len(html)


def relax_tall_blocks(html: str) -> tuple[str, int]:
    """Add `long` to callout blocks too tall to survive `break-inside: avoid`."""
    edits: list[tuple[int, int, str]] = []
    for m in BLOCK_OPEN.finditer(html):
        classes = m.group("cls").split()
        if "long" in classes or not any(c in RELAXABLE for c in classes):
            continue
        close = _matching_close(html, m.group("tag"), m.end())
        inner = html[m.end() : close]
        rows = inner.count("<tr")
        if len(inner) < TALL_CHARS and rows < TALL_ROWS:
            continue
        span = m.group(0)
        edits.append(
            (m.start(), m.end(), span.replace(f'class="{m.group("cls")}"',
                                              f'class="{m.group("cls")} long"', 1))
        )
    for start, end, replacement in reversed(edits):
        html = html[:start] + replacement + html[end:]
    return html, len(edits)


def render_toc(outline: list[dict]) -> str:
    rows: list[str] = ['<nav class="toc"><ol>']
    open_sub = False
    for node in outline:
        if node["level"] == 1:
            if open_sub:
                rows.append("</ol></li>")
                open_sub = False
            label = node["label"]
            rows.append(f'<li><a href="#{node["id"]}">{label}</a>')
            rows.append("<ol>")
            open_sub = True
        else:
            if not open_sub:
                rows.append("<li><ol>")
                open_sub = True
            rows.append(f'<li><a href="#{node["id"]}">{node["label"]}</a></li>')
    if open_sub:
        rows.append("</ol></li>")
    rows.append("</ol></nav>")
    return "\n".join(rows)


def manifest(guide: str) -> list[Path]:
    files = sorted((CONTENT / guide).glob("*.html"))
    if not files:
        raise SystemExit(f"no content fragments found for {guide}")
    return files


def build(guide: str) -> Path:
    meta = GUIDES[guide]
    parts = [p.read_text(encoding="utf-8") for p in manifest(guide)]
    body = "\n".join(parts)
    body, outline = inject_ids(body)
    body, relaxed = relax_tall_blocks(body)
    body = body.replace("<!--TOC-->", render_toc(outline))

    html = SHELL.format(
        title=meta["title"],
        short=meta["short"],
        description=meta["description"],
        keywords=meta["keywords"],
        edition=EDITION,
        css=CSS.read_text(encoding="utf-8"),
        body=body,
    )

    DIST.mkdir(parents=True, exist_ok=True)
    debug = DIST / f"{guide}.debug.html"
    debug.write_text(html, encoding="utf-8")

    from weasyprint import HTML

    target = DIST / meta["out"]
    doc = HTML(string=html, base_url=str(ROOT)).render()
    doc.write_pdf(target)
    chapters = sum(1 for n in outline if n["level"] == 1)
    print(
        f"{guide}: {len(parts)} fragments, {chapters} chapters, "
        f"{len(outline)} outline entries, {relaxed} tall blocks relaxed, "
        f"{len(doc.pages)} pages -> {target.name}"
    )
    return target


def main() -> None:
    wanted = sys.argv[1:] or list(GUIDES)
    for guide in wanted:
        if guide not in GUIDES:
            raise SystemExit(f"unknown guide: {guide}")
        build(guide)


if __name__ == "__main__":
    main()
