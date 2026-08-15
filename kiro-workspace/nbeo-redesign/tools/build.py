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
from collections import Counter
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
#
# The manual prints as two volumes, one per session. Each volume is complete:
# it carries the whole reference apparatus, then its own session. Within a
# volume the 35 cases come first and the 35 teaching keys follow, so a session
# can be sat cold without a key on the facing page. That was the one real flaw
# in the single-file edition: turn the page, see the answer.

REFERENCE = [
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
]

BACK = [
    ("p", "95-back-divider.html", "back"),
    ("g", "answerkey", "key"),
    ("g", "schedule", "sched"),
    ("p", "96-recall-1.html", "recall"),
    ("p", "97-recall-2.html", None),
    ("p", "98-sources.html", "sources"),
    ("p", "99-colophon.html", "colo"),
]


def spine(volume):
    return (REFERENCE
            + [("p", {1: "80-divider-s1.html", 2: "90-divider-s2.html"}[volume],
                "session"),
               ("g", "index", "idx"),
               ("g", "score", None),
               ("c", "cases", None),
               ("p", "85-keys-divider.html", "keys"),
               ("c", "keys", None)]
            + BACK)


SHARED_TOC = [
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
]


def toc_for(volume):
    return SHARED_TOC + [
        ("8", "Session %d, thirty-five cases" % volume, "session"),
        ("8", "Case index and score sheet", "idx"),
        ("9", "Teaching keys, case by case", "keys"),
        ("10", "Answer key, Session %d" % volume, "key"),
        ("10", "Eleven days", "sched"),
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


def assemble(cases, volume):
    """Return [(html, anchor)] in print order for one volume.

    `cases` is the whole bank, because the answer letters are generated across
    both sessions. Only this volume's session is rendered.
    """
    mine = [c for c in cases if c["session"] == volume]
    sheets = []
    for kind, arg, anchor in spine(volume):
        if kind == "p":
            sheets.append([read_partial(arg), anchor])
        elif kind == "c":
            for case in mine:
                made = (render.case_sheets(case) if arg == "cases"
                        else render.key_sheets(case))
                tag = case["id"] if arg == "cases" else "key-" + case["id"]
                for i, html in enumerate(made):
                    sheets.append([html, tag if i == 0 else None])
        else:
            made = {
                "pairs": lambda: blocks.pair_sheets(mine),
                "index": lambda: [_index_sheet(cases, volume)],
                "score": lambda: blocks.score_sheets(cases, volume),
                "answerkey": lambda: blocks.answer_key_sheets(cases, [volume]),
                "schedule": lambda: blocks.schedule_sheets(volume),
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


def toc_html(pages, volume):
    """One row per entry, with the part number inline. Part heading rows cost
    more vertical space on the cover than they earn."""
    rows = []
    for num, title, anchor in toc_for(volume):
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

    with open(os.path.join(CONTENT, "base.css"), encoding="utf-8") as fh:
        css = fh.read()

    counts = {}
    for volume in (1, 2):
        counts[volume] = write_volume(cases, volume, css)

    write_key_json(cases)
    print("")
    for volume in (1, 2):
        print("wrote %s: %d pages" % (html_name(volume), counts[volume]))
    print("%d cases, %d items, %d distractor rows across the two volumes"
          % (len(cases), sum(len(c["items"]) for c in cases),
             sum(len(i["dis"]) for c in cases for i in c["items"])))
    return 1 if key_problems else 0


VOLUME_WORDS = {1: "One", 2: "Two"}


def html_name(volume):
    return "volume-%d.html" % volume


def pdf_name(volume):
    return "NBEO PAM-TMOD Manual - Volume %d, Session %d.pdf" % (volume, volume)


def write_volume(cases, volume, css):
    """Render one volume to volume-N.html. Returns its page count."""
    sheets = assemble(cases, volume)
    html_pages, pages = paginate(sheets)
    doc = "\n".join(html_pages)

    n_items = sum(len(c["items"]) for c in cases)
    alloc = Counter(i["type"] for c in cases for i in c["items"])
    for kind, count in alloc.items():
        doc = doc.replace("{{ALLOC:%s}}" % kind,
                          "%d &middot; %.0f%%" % (count, 100.0 * count / n_items))
    mine = [c for c in cases if c["session"] == volume]
    doc = (doc.replace("{{ALLOC:multi}}", str(sum(
               1 for c in cases for i in c["items"]
               if i.get("format") == "multi")))
              .replace("{{DOMAINS}}", str(len({c["domain"] for c in cases})))
              .replace("{{DISROWS}}", str(sum(
                  len(i["dis"]) for c in cases for i in c["items"])))
              .replace("{{TOC}}", toc_html(pages, volume))
              .replace("{{KEYBARS}}", blocks.key_integrity(cases))
              .replace("{{VOLUME}}", str(volume))
              .replace("{{VOLWORD}}", VOLUME_WORDS[volume])
              .replace("{{OTHERVOL}}", VOLUME_WORDS[3 - volume])
              .replace("{{VOLCASES}}", str(len(mine)))
              .replace("{{VOLITEMS}}", str(sum(len(c["items"]) for c in mine)))
              .replace("{{NPAGES}}", str(len(html_pages)))
              .replace("{{NCASES}}", str(len(cases)))
              .replace("{{NITEMS}}", str(n_items))
              .replace("{{DATE}}", BUILT))
    doc = re.sub(r"\{\{PGREF:([^}]+)\}\}",
                 lambda m: str(pages.get(m.group(1), "-")), doc)

    left = re.findall(r"\{\{[A-Z][^}]*\}\}", doc)
    if left:
        print("volume %d unresolved tokens: %s"
              % (volume, sorted(set(left))[:10]))

    title = ("NBEO Part II PAM/TMOD - Clinical Reasoning Manual, "
             "Volume %d: Session %d" % (volume, volume))
    shell = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>%s</title>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1'
        '&family=Spectral:ital,wght@0,300;0,400;0,600;1,400'
        '&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">\n'
        '<style>\n%s</style>\n</head>\n<body>\n\n%s\n</body>\n</html>\n'
        % (render.esc(title), css, doc))

    with open(os.path.join(ROOT, html_name(volume)), "w", encoding="utf-8") as fh:
        fh.write(shell)
    return len(html_pages)


def write_key_json(cases):
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


if __name__ == "__main__":
    sys.exit(main())
