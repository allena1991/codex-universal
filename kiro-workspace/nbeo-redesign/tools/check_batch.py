#!/usr/bin/env python3
"""Check one authored batch file before it goes into the build.

  python3 tools/check_batch.py content/cases/s1-b.json

Reports schema problems, length-cap breaches, and any case that would spill
onto a third sheet. Exit code 0 means the batch is ready. This does not check
the answer-letter distribution: letters are generated across a whole session by
tools/build.py, so a single batch cannot be audited for them.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from schema import validate, assign_keys, TYPES          # noqa: E402
from render import fit_problems, CAPS, case_cost, rat_cost, KEY_HEAD, USABLE  # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    problems = []
    cases = []
    for path in sys.argv[1:]:
        with open(path, encoding="utf-8") as fh:
            batch = json.load(fh)
        if not isinstance(batch, list):
            problems.append("%s: top level must be a list of cases" % path)
            batch = batch.get("cases", [])
        for case in batch:
            case["_file"] = os.path.basename(path)
            cases.append(case)

    problems += validate(cases, strict=False)
    assign_keys(cases)
    problems += fit_problems(cases)

    print("cases: %d, items: %d"
          % (len(cases), sum(len(c.get("items") or []) for c in cases)))
    counts = {}
    for case in cases:
        for item in case.get("items") or []:
            counts[item.get("type")] = counts.get(item.get("type"), 0) + 1
    print("item types: %s" % ", ".join("%s %d" % (k, counts[k])
                                       for k in sorted(counts)))

    for case in cases:
        key = KEY_HEAD + sum(rat_cost(i) for i in case["items"])
        print("  %-7s case %5.0f/%.0f   key %5.0f/%.0f   %s"
              % (case.get("id", "?"), case_cost(case), USABLE, key, USABLE,
                 case.get("title", "")[:42]))

    if problems:
        print("\n%d problem(s):" % len(problems))
        for p in problems:
            print("  -", p)
        print("\ncaps: %s" % CAPS)
        print("item types allowed: %s" % sorted(TYPES))
        return 1
    print("\nclean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
