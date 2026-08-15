#!/usr/bin/env python3
"""What each guide is made of: sheet order, contents, titles, filenames.

Two complete guides over one verified content set. Both carry everything: the
whole reference apparatus, all 70 cases, all 350 items and all 140 teaching-key
pages. Neither is an extract of the other. They differ in the order the content
is presented, because learning and testing want opposite orders:

  part1  Study Manual.    Ordered by clinical domain, each case followed
                          immediately by its own teaching key. Competing
                          conditions sit next to each other, which is how the
                          discriminators stick.
  part2  Exam Simulator.  Ordered as sat, session by session, cases only, with
                          every key at the back behind a divider. A session can
                          be answered cold and timed.

A spine entry is (kind, argument, anchor):
  "p"  a partial in content/partials
  "g"  a generator in blocks.py
  "r"  records as sat: (session, "items" | "keys")
  "d"  records by domain, each item sheet followed by its key sheet
"""

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

TAIL_TOC = [
    ("10", "Answer key, both sessions", "key"),
    ("10", "Eighteen days", "sched"),
    ("10", "Rapid recall deck", "recall"),
    ("10", "Sources", "sources"),
]


PART1 = {
    "slug": "part-1-study-manual",
    "title": "NBEO Part II PAM/TMOD - Study Manual, by domain",
    "shortname": "Study Manual",
    "pdf": "NBEO PAM-TMOD Part 1 - Study Manual (by domain).pdf",
    "order": "domain",
    "spine": (REFERENCE
              + [("p", "70-study-divider.html", "study"),
                 ("g", "domainindex", "didx"),
                 ("d", "all", None)]
              + BACK),
    "toc": SHARED_TOC + [
        ("8", "All seventy cases, by domain", "study"),
        ("8", "Domain index", "didx"),
    ] + TAIL_TOC,
}

PART2 = {
    "slug": "part-2-exam-simulator",
    "title": "NBEO Part II PAM/TMOD - Exam Simulator, as sat",
    "shortname": "Exam Simulator",
    "pdf": "NBEO PAM-TMOD Part 2 - Exam Simulator (as sat).pdf",
    "order": "session",
    "spine": (REFERENCE
              + [("p", "80-divider-s1.html", "s1"),
                 ("g", "index1", "idx1"),
                 ("g", "score1", None),
                 ("r", (1, "items"), None),
                 ("p", "90-divider-s2.html", "s2"),
                 ("g", "index2", "idx2"),
                 ("g", "score2", None),
                 ("r", (2, "items"), None),
                 ("p", "85-keys-divider.html", "keys"),
                 ("r", (1, "keys"), "keys1"),
                 ("r", (2, "keys"), "keys2")]
              + BACK),
    "toc": SHARED_TOC + [
        ("8", "Session 1, thirty-five cases", "s1"),
        ("8", "Session 1 case index", "idx1"),
        ("9", "Session 2, thirty-five cases", "s2"),
        ("9", "Session 2 case index", "idx2"),
        ("9", "Teaching keys, all seventy", "keys"),
    ] + TAIL_TOC,
}

GUIDES = {"part1": PART1, "part2": PART2}

# Both guides read the same content and both contain all of it.
CONTENT_DIR = "cases"
SESSIONS = (1, 2)
RECORD = "case"
