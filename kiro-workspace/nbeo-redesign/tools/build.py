#!/usr/bin/env python3
"""Assemble a guide from its content and its partials.

  python3 tools/build.py               # both guides
  python3 tools/build.py part2         # one guide
  python3 tools/build.py --audit       # audit the answer keys, write nothing

Page numbers, the contents, the indexes, the printed answer key and the
key-integrity chart are all generated after layout, so they cannot drift away
from the content. What each guide contains is in tools/guides.py.
"""

import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

import blocks                                                   # noqa: E402
import render                                                   # noqa: E402
from guides import GUIDES, CONTENT_DIR, SESSIONS, RECORD        # noqa: E402
from schema import load_cases, validate, assign_keys, audit     # noqa: E402

CONTENT = os.path.join(ROOT, "content")
PARTIALS = os.path.join(CONTENT, "partials")
BUILT = "15 August 2026"

FRONT = re.compile(r"^\s*<!--(.*?)-->", re.S)


def read_partial(name):
    path = os.path.join(PARTIALS, name)
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    meta, body = {}, raw
    match = FRONT.match(raw)
    if match:
        for line in match.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = raw[match.end():]
    return render.sheet(body.strip(), meta.get("label", name),
                        meta.get("part", ""),
                        meta.get("foot", "{{PG}}"),
                        meta.get("class", ""),
                        meta.get("chrome", "yes") != "none")


def assemble(guide, records):
    """Return [(html, anchor)] in print order for one guide."""
    sheets = []
    for kind, arg, anchor in guide["spine"]:
        if kind == "p":
            made = [read_partial(arg)]
        elif kind == "r":
            session, mode = arg
            block = [r for r in records if r["session"] == session]
            sheets.extend(_records(block, mode, anchor))
            continue
        elif kind == "d":
            # By domain, then by id inside a domain, with each case immediately
            # followed by its own key. This is the learning order.
            block = sorted(records, key=lambda r: (r["domain"].lower(), r["id"]))
            out = []
            for rec in block:
                out.extend(_records([rec], "items", None))
                out.extend(_records([rec], "keys", None))
            sheets.extend(out)
            continue
        else:
            made = _generate(arg, guide, records)
        for i, html in enumerate(made):
            sheets.append((html, anchor if i == 0 else None))
    return [list(s) for s in sheets]


def _records(block, mode, anchor):
    """Sheets for a run of records, tagged so cross-references resolve."""
    out = []
    for rec in block:
        pages = (render.record_sheets(rec) if mode == "items"
                 else render.key_sheets(rec))
        tag = rec["id"] if mode == "items" else "key-" + rec["id"]
        for i, html in enumerate(pages):
            out.append([html, (anchor or tag) if i == 0 else None])
            anchor = None
    return out


def _generate(name, guide, records):
    if name == "pairs":
        return blocks.pair_sheets(records)
    if name == "answerkey":
        return blocks.answer_key_sheets(records, guide)
    if name == "schedule":
        return blocks.schedule_sheets(records, guide)
    if name == "domainindex":
        return blocks.domain_index_sheets(records)
    if name.startswith("index"):
        return [blocks.index_sheet(records, int(name[-1]), guide)]
    if name.startswith("score"):
        return blocks.score_sheets(records, int(name[-1]), guide)
    raise KeyError("no generator called %r" % name)


def paginate(sheets):
    pages = {}
    for n, (_, anchor) in enumerate(sheets, 1):
        if anchor:
            pages[anchor] = n
    return [html.replace("{{PG}}", str(n))
            for n, (html, _) in enumerate(sheets, 1)], pages


def toc_html(guide, pages):
    """One row per entry, part number inline. Part heading rows cost more
    vertical space on the cover than they earn."""
    return "".join(
        '<div><b>%s</b><span><i>P%s</i>%s</span></div>'
        % (pages.get(anchor, "-"), num, render.esc(title))
        for num, title, anchor in guide["toc"])


def substitute(doc, guide, records, pages, n_pages):
    n_items = sum(len(r["items"]) for r in records)
    alloc = Counter(i["type"] for r in records for i in r["items"])
    for kind, count in alloc.items():
        doc = doc.replace("{{ALLOC:%s}}" % kind,
                          "%d &middot; %.0f%%" % (count, 100.0 * count / n_items))
    per_session = [sum(len(r["items"]) for r in records if r["session"] == s)
                   for s in SESSIONS]
    doc = (doc.replace("{{ALLOC:multi}}", str(sum(
               1 for r in records for i in r["items"]
               if i.get("format") == "multi")))
              .replace("{{DOMAINS}}", str(len({r["domain"] for r in records})))
              .replace("{{DISROWS}}", str(sum(
                  len(i["dis"]) for r in records for i in r["items"])))
              .replace("{{TOC}}", toc_html(guide, pages))
              .replace("{{KEYBARS}}", blocks.key_integrity(records))
              .replace("{{NPAGES}}", str(n_pages))
              .replace("{{NRECORDS}}", str(len(records)))
              .replace("{{NITEMS}}", str(n_items))
              .replace("{{PERSESSION}}", str(per_session[0]))
              .replace("{{GUIDE}}", guide["shortname"])
              .replace("{{OTHERGUIDE}}", (
                  "Exam Simulator" if guide["order"] == "domain"
                  else "Study Manual"))
              .replace("{{ORDER}}", (
                  "by clinical domain, each case followed by its key"
                  if guide["order"] == "domain"
                  else "in exam order, with every key at the back"))
              .replace("{{DATE}}", BUILT))
    doc = re.sub(r"\{\{PGREF:([^}]+)\}\}",
                 lambda m: str(pages.get(m.group(1), "-")), doc)
    left = sorted(set(re.findall(r"\{\{[A-Z][^}]*\}\}", doc)))
    return doc, left


SHELL = ('<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
         '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
         '<title>%s</title>\n'
         '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:'
         'ital@0;1&family=Spectral:ital,wght@0,300;0,400;0,600;1,400'
         '&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">\n'
         '<style>\n%s</style>\n</head>\n<body>\n\n%s\n</body>\n</html>\n')


def build_guide(key, css, write=True):
    """Validate, key, lay out and write one guide. Returns (pages, problems)."""
    guide = GUIDES[key]
    records = load_cases(os.path.join(CONTENT, CONTENT_DIR))
    if not records:
        return 0, ["%s: no content in content/%s" % (key, CONTENT_DIR)]

    problems = validate(records, strict="--loose" not in sys.argv)
    assign_keys(records)
    lines, key_problems = audit(records)
    print("\n%s: %s" % (key, guide["title"]))
    print("\n".join(lines))
    problems += key_problems
    problems += render.fit_problems(records)

    if not write:
        return 0, problems

    sheets = assemble(guide, records)
    html_pages, pages = paginate(sheets)
    doc, unresolved = substitute("\n".join(html_pages), guide, records, pages,
                                 len(html_pages))
    if unresolved:
        problems.append("%s: unresolved tokens %s" % (key, unresolved[:8]))

    out = os.path.join(ROOT, guide["slug"] + ".html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(SHELL % (render.esc(guide["title"]), css, doc))
    print("  wrote %s.html: %d pages, %d cases, %d items"
          % (guide["slug"], len(html_pages), len(records),
             sum(len(r["items"]) for r in records)))
    _write_key_json(records, guide)
    return len(html_pages), problems


def _write_key_json(records, guide):
    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    key = {"built": BUILT, "guide": guide["title"], "sessions": {}}
    for session in SESSIONS:
        key["sessions"][str(session)] = [
            {"id": r["id"], "title": r["title"], "domain": r["domain"],
             "keys": [i["key"] for i in r["items"]],
             "types": [i["type"] for i in r["items"]]}
            for r in records if r["session"] == session]
    path = os.path.join(ROOT, "build", "key.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(key, fh, indent=1)


def main():
    wanted = [a for a in sys.argv[1:] if not a.startswith("--")] or ["part1", "part2"]
    unknown = [w for w in wanted if w not in GUIDES]
    if unknown:
        print("unknown guide %s, expected any of %s" % (unknown, sorted(GUIDES)))
        return 2

    with open(os.path.join(CONTENT, "base.css"), encoding="utf-8") as fh:
        css = fh.read()

    failed = False
    for key in wanted:
        pages, problems = build_guide(key, css, write="--audit" not in sys.argv)
        if problems:
            print("  %d problem(s) in %s:" % (len(problems), key))
            for p in problems[:40]:
                print("    -", p)
            if len(problems) > 40:
                print("    ... and %d more" % (len(problems) - 40))
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
