#!/usr/bin/env python3
"""Assemble the manual from case data and authored partials.

  python3 tools/build.py            # writes index.html and build/key.json
  python3 tools/build.py --audit    # audit only, no write

Page numbers, the table of contents, the case index, the printed answer key and
the key-integrity chart are all generated after layout, so they cannot drift
away from the content.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)

import blocks                                                   # noqa: E402
import render                                                   # noqa: E402
from schema import load_cases, validate, assign_keys, audit     # noqa: E402

CONTENT = os.path.join(ROOT, "content")
PARTIALS = os.path.join(CONTENT, "partials")
BUILT = "15 August 2026"

# Sheet order. Partials are authored HTML; generators come from blocks.py.
SPINE = [
    ("p", "10-cover.html", "cover"),
    ("p", "11-how-to-use.html", "how"),
    ("p", "12-verification.html", "verify"),
    ("p", "13-key-integrity.html", "keyint"),
    ("p", "20-exam-map.html", "map"),
    ("p", "21-item-types.html", "types"),
    ("p", "22-pacing.html", "pacing"),
    ("p", "30-emergency-1.html", "emerg"),
    ("p", "31-emergency-2.html", "emerg2"),
    ("p", "32-emergency-3.html", "emerg3"),
    ("p", "40-conditions-1.html", "cond"),
    ("p", "41-conditions-2.html", None),
    ("p", "42-conditions-3.html", None),
    ("p", "43-conditions-4.html", None),
    ("p", "50-pharm-1.html", "pharm"),
    ("p", "51-pharm-2.html", None),
    ("p", "52-pharm-3.html", None),
    ("p", "60-formulas.html", "optics"),
    ("p", "61-procedures.html", None),
    ("p", "62-law.html", "law"),
    ("g", "pairs", "pairs"),
    ("p", "80-divider-s1.html", "s1"),
    ("g", "index1", "idx1"),
    ("g", "score1", None),
    ("c", 1, None),
    ("p", "90-divider-s2.html", "s2"),
    ("g", "index2", "idx2"),
    ("g", "score2", None),
    ("c", 2, None),
    ("p", "95-back-divider.html", "back"),
    ("g", "answerkey", "key"),
    ("g", "schedule", "sched"),
    ("p", "96-recall-1.html", "recall"),
    ("p", "97-recall-2.html", None),
    ("p", "98-sources.html", "sources"),
    ("p", "99-colophon.html", "colo"),
]

TOC = [
    ("1", "How to use this manual", "how"),
    ("1", "What was verified, and what was not", "verify"),
    ("1", "Key integrity", "keyint"),
    ("2", "The exam, to scale", "map"),
    ("2", "Item types", "types"),
    ("2", "Pacing and the case algorithm", "pacing"),
    ("3", "Emergency gate", "emerg"),
    ("4", "Condition cards", "cond"),
    ("5", "Pharmacology", "pharm"),
    ("6", "Optics, formulas, drills", "optics"),
    ("6", "Law, ethics, public health", "law"),
    ("7", "Competing pairs", "pairs"),
    ("8", "Session 1 simulation", "s1"),
    ("8", "Session 1 case index", "idx1"),
    ("9", "Session 2 simulation", "s2"),
    ("9", "Session 2 case index", "idx2"),
    ("10", "Answer key", "key"),
    ("10", "Eighteen days", "sched"),
    ("10", "Rapid recall deck", "recall"),
    ("10", "Sources", "sources"),
]

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


def assemble(cases):
    """Return [(html, anchor)] in print order."""
    sheets = []
    for kind, arg, anchor in SPINE:
        if kind == "p":
            sheets.append([read_partial(arg), anchor])
        elif kind == "c":
            first = True
            for case in [c for c in cases if c["session"] == arg]:
                for i, html in enumerate(render.case_sheets(case)):
                    sheets.append([html, case["id"] if i == 0 else None])
                for i, html in enumerate(render.key_sheets(case)):
                    sheets.append([html, "key-" + case["id"] if i == 0 else None])
                first = False
        else:
            made = {
                "pairs": lambda: blocks.pair_sheets(cases),
                "index1": lambda: [_index_sheet(cases, 1)],
                "index2": lambda: [_index_sheet(cases, 2)],
                "score1": lambda: blocks.score_sheets(cases, 1),
                "score2": lambda: blocks.score_sheets(cases, 2),
                "answerkey": lambda: blocks.answer_key_sheets(cases),
                "schedule": lambda: blocks.schedule_sheets(),
            }[arg]()
            for i, html in enumerate(made):
                sheets.append([html, anchor if i == 0 else None])
    return sheets


def _index_sheet(cases, session):
    body = ('<h2>Session %d &middot; case index</h2>'
            '<p class="lede" style="margin-top:8px">Sorted as sat. Dx diagnosis, '
            'Tx treatment, Sci basic science, Law law and ethics, Sel select all '
            'that apply. Use the item-type column to work a single weakness across '
            'the whole session.</p><div style="margin-top:10px">%s</div>'
            % (session, blocks.case_index(cases, session)))
    return render.sheet(body, "S%d case index" % session,
                        "Session %d / Case index" % session,
                        "Case index &middot; {{PG}}")


def paginate(sheets):
    pages = {}
    for n, (_, anchor) in enumerate(sheets, 1):
        if anchor:
            pages[anchor] = n
    out = []
    for n, (html, _) in enumerate(sheets, 1):
        out.append(html.replace("{{PG}}", str(n)))
    return out, pages


def toc_html(pages):
    """One row per entry, with the part number inline. Part heading rows cost
    more vertical space on the cover than they earn."""
    rows = []
    for num, title, anchor in TOC:
        rows.append('<div><b>%s</b><span><i>P%s</i>%s</span></div>'
                    % (pages.get(anchor, "-"), num, render.esc(title)))
    return "".join(rows)


def main():
    cases = load_cases(os.path.join(CONTENT, "cases"))
    strict = "--loose" not in sys.argv
    problems = validate(cases, strict=strict)
    if problems:
        print("content problems (%d):" % len(problems))
        for p in problems[:60]:
            print("  -", p)
        if len(problems) > 60:
            print("  ... and %d more" % (len(problems) - 60))
        if strict:
            return 1

    assign_keys(cases)
    lines, key_problems = audit(cases)
    print("\n".join(lines))
    if key_problems:
        print("\nkey problems:")
        for p in key_problems:
            print("  -", p)

    if "--audit" in sys.argv:
        return 1 if key_problems else 0

    sheets = assemble(cases)
    html_pages, pages = paginate(sheets)
    doc = "\n".join(html_pages)

    n_items = sum(len(c["items"]) for c in cases)
    from collections import Counter
    alloc = Counter(i["type"] for c in cases for i in c["items"])
    for kind, count in alloc.items():
        doc = doc.replace("{{ALLOC:%s}}" % kind,
                          "%d &middot; %.0f%%" % (count, 100.0 * count / n_items))
    doc = doc.replace("{{ALLOC:multi}}", str(sum(
        1 for c in cases for i in c["items"] if i.get("format") == "multi")))
    doc = doc.replace("{{DOMAINS}}", str(len({c["domain"] for c in cases})))
    doc = doc.replace("{{DISROWS}}", str(sum(
        len(i["dis"]) for c in cases for i in c["items"])))

    doc = (doc.replace("{{TOC}}", toc_html(pages))
              .replace("{{KEYBARS}}", blocks.key_integrity(cases))
              .replace("{{NPAGES}}", str(len(html_pages)))
              .replace("{{NCASES}}", str(len(cases)))
              .replace("{{NITEMS}}", str(n_items))
              .replace("{{DATE}}", BUILT))
    doc = re.sub(r"\{\{PGREF:([^}]+)\}\}",
                 lambda m: str(pages.get(m.group(1), "-")), doc)

    left = re.findall(r"\{\{[A-Z][^}]*\}\}", doc)
    if left:
        print("unresolved tokens:", sorted(set(left))[:10])

    with open(os.path.join(CONTENT, "base.css"), encoding="utf-8") as fh:
        css = fh.read()
    shell = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>NBEO Part II PAM/TMOD - Clinical Reasoning Manual</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
        '&family=Spectral:ital,wght@0,300;0,400;0,600;1,400'
        '&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">\n'
        '<style>\n%s</style>\n</head>\n<body>\n\n%s\n</body>\n</html>\n' % (css, doc))

    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(shell)

    os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
    key = {"built": BUILT, "sessions": {}}
    for session in (1, 2):
        key["sessions"][str(session)] = [
            {"case": c["id"], "title": c["title"], "domain": c["domain"],
             "keys": [i["key"] for i in c["items"]],
             "types": [i["type"] for i in c["items"]]}
            for c in cases if c["session"] == session]
    with open(os.path.join(ROOT, "build", "key.json"), "w", encoding="utf-8") as fh:
        json.dump(key, fh, indent=1)

    print("\nwrote index.html: %d sheets, %d cases, %d items"
          % (len(html_pages), len(cases), n_items))
    return 1 if key_problems else 0


if __name__ == "__main__":
    sys.exit(main())
