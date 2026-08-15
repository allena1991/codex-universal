#!/usr/bin/env python3
"""Content schema, validation, and answer-key generation for the manual.

Authors write cases as JSON with the correct option flagged in place. They do
not choose answer letters. This module assigns the letters, so the printed key
is generated to a distribution target instead of being audited after the fact:

  - every letter A-E carries 18-22% of the single-answer items in a session
  - no letter is correct on more than three consecutive single-answer items
  - all five letters are correct at least once in every session

It also enforces the option-writing rules that the original guide broke. The
worst one was length: the correct option was usually the longest and most
hedged, which teaches "pick the careful one" instead of clinical reasoning.
"""

import json
import os
import random
from collections import Counter

LETTERS = "ABCDEF"
# The blueprint scores four item types. "Select all that apply" is a response
# format, not a type, so it lives in item["format"] and an all-or-none item is
# still a treatment or a diagnosis item for scoring purposes.
TYPES = {
    "diagnosis": ("Diagnosis", ""),
    "treatment": ("Treatment", "tx"),
    "basic": ("Basic science", "bs"),
    "legal": ("Law and ethics", "lg"),
}


def is_multi(item):
    return item.get("format") == "multi"
BANNED = ("all of the above", "none of the above", "both a and b",
          "any of the above", "a and b", "options above")

# The seventeen blueprint domains, spelled once. An index groups on this string,
# so a paraphrase silently splits a domain in two. Validation rejects anything
# not on this list rather than trusting every author to spell it the same way.
DOMAINS = (
    "Cornea and refractive surgery",
    "Retina, choroid, vitreous",
    "Optic nerve and neuro-ophthalmic",
    "Lens, cataract, IOL, perioperative",
    "Glaucoma",
    "Contact lenses",
    "Accommodation, vergence, oculomotor",
    "Lids, lacrimal, adnexa, orbit",
    "Episclera, sclera, anterior uvea",
    "Emergencies and trauma",
    "Systemic health",
    "Ametropia",
    "Amblyopia and strabismus",
    "Ophthalmic optics and spectacles",
    "Low vision",
    "Perceptual function and colour vision",
    "Visual and human development",
)

# Calibrated against a real Chromium render: see tools/shoot.mjs output.
# Units are arbitrary "height points" per sheet of printable column.
SHEET_BUDGET = 1000


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def load_cases(dirpath):
    """Read every case JSON in dirpath. Each file holds a list of cases."""
    cases = []
    for name in sorted(os.listdir(dirpath)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(dirpath, name), encoding="utf-8") as fh:
            payload = json.load(fh)
        batch = payload if isinstance(payload, list) else payload.get("cases", [])
        for case in batch:
            case["_file"] = name
            cases.append(case)
    cases.sort(key=lambda c: (c.get("session", 0), c.get("n", 0)))
    return cases


# --------------------------------------------------------------------------
# validation
# --------------------------------------------------------------------------

def _bad_length_spread(options):
    lengths = [len(o["t"]) for o in options]
    return max(lengths) > 2.4 * min(lengths) and max(lengths) - min(lengths) > 28


def validate(cases, strict=True):
    """Return a list of human-readable problems. Empty list means clean."""
    problems = []
    seen = set()

    for case in cases:
        cid = case.get("id", "?")
        where = "%s (%s)" % (cid, case.get("_file", "?"))

        for field in ("id", "session", "n", "domain", "title", "stem", "items"):
            if not case.get(field):
                problems.append("%s: missing %s" % (where, field))
        if cid in seen:
            problems.append("%s: duplicate case id" % where)
        seen.add(cid)

        if case.get("domain") and case["domain"] not in DOMAINS:
            near = [d for d in DOMAINS
                    if d.split(",")[0].split(" and ")[0].lower()
                    in case["domain"].lower()]
            problems.append("%s: domain %r is not one of the seventeen%s"
                            % (where, case["domain"],
                               ", did you mean %r" % near[0] if near else ""))

        if "Stub" in json.dumps(case):
            problems.append("%s: placeholder text from tools/stub.py is still "
                            "in this case" % where)

        items = case.get("items") or []
        if not 4 <= len(items) <= 6:
            problems.append("%s: %d items, expected 4-6" % (where, len(items)))
        if len(case.get("stem", "")) < 120:
            problems.append("%s: stem is too thin to reason from (%d chars)"
                            % (where, len(case.get("stem", ""))))

        for i, item in enumerate(items, 1):
            tag = "%s item %d" % (where, i)
            kind = item.get("type")
            if kind not in TYPES:
                problems.append("%s: type %r not in %s"
                                % (tag, kind, sorted(TYPES)))
            if not item.get("q"):
                problems.append("%s: missing q" % tag)
            if not item.get("why"):
                problems.append("%s: missing why" % tag)
            if not item.get("short"):
                problems.append("%s: missing short (the answer in a few words, "
                                "printed on the teaching key)" % tag)

            options = item.get("options") or []
            correct = [j for j, o in enumerate(options) if o.get("correct")]
            if item.get("format") not in (None, "multi"):
                problems.append("%s: format %r, expected \"multi\" or nothing"
                                % (tag, item.get("format")))
            if is_multi(item):
                if not 5 <= len(options) <= 6:
                    problems.append("%s: all-or-none item has %d options, "
                                    "expected 5-6" % (tag, len(options)))
                if not 2 <= len(correct) <= 3:
                    problems.append("%s: all-or-none item has %d correct, "
                                    "expected 2-3" % (tag, len(correct)))
            else:
                if len(options) != 5:
                    problems.append("%s: %d options, expected 5"
                                    % (tag, len(options)))
                if len(correct) != 1:
                    problems.append("%s: %d correct options, expected 1"
                                    % (tag, len(correct)))

            texts = [o.get("t", "").strip() for o in options]
            if len(set(texts)) != len(texts):
                problems.append("%s: duplicate option text" % tag)
            for t in texts:
                if not t:
                    problems.append("%s: empty option" % tag)
                low = t.lower()
                if any(b in low for b in BANNED):
                    problems.append("%s: throwaway option %r" % (tag, t[:40]))
            if options and _bad_length_spread(options):
                problems.append("%s: option lengths not matched (%s)"
                                % (tag, sorted(len(t) for t in texts)))

            rows = item.get("dis") or []
            if len(rows) < 2:
                problems.append("%s: %d distractor rows, expected at least 2"
                                % (tag, len(rows)))
            for row in rows:
                refs = row.get("refs")
                if not refs:
                    problems.append("%s: distractor row without refs" % tag)
                    continue
                for ref in refs:
                    if not 0 <= ref < len(options):
                        problems.append("%s: ref %r out of range" % (tag, ref))
                    elif not is_multi(item) and ref in correct:
                        problems.append("%s: ref %d points at the correct option"
                                        % (tag, ref))
                for field in ("label", "tempting", "ruled"):
                    if not row.get(field):
                        problems.append("%s: distractor row missing %s"
                                        % (tag, field))

    if strict:
        for session in (1, 2):
            block = [c for c in cases if c.get("session") == session]
            if not block:
                continue
            if len(block) != 35:
                problems.append("session %d: %d cases, expected 35"
                                % (session, len(block)))
            n_items = sum(len(c.get("items") or []) for c in block)
            if n_items != 175:
                problems.append("session %d: %d items, expected 175"
                                % (session, n_items))
            problems.extend(_length_bias(session, block))

    return problems


def _length_bias(session, block):
    """The correct option must not be reliably the longest one."""
    longest = total = 0
    for case in block:
        for item in case["items"]:
            if is_multi(item):
                continue
            others = [len(o["t"]) for o in item["options"] if not o.get("correct")]
            correct = next(len(o["t"]) for o in item["options"] if o.get("correct"))
            total += 1
            if correct > max(others):
                longest += 1
    if total and longest > 0.34 * total:
        return ["session %d: correct option is the longest in %d/%d items (%.0f%%),"
                " target is at or under 34%%" % (session, longest, total,
                                                 100.0 * longest / total)]
    return []


# --------------------------------------------------------------------------
# key generation
# --------------------------------------------------------------------------

def _target_sequence(n, rng, span=5, max_run=3):
    """A length-n sequence over the first `span` letters, evenly split and
    with no letter repeating more than max_run times in a row."""
    pool = []
    for i in range(n):
        pool.append(LETTERS[i % span])
    for attempt in range(400):
        rng.shuffle(pool)
        run, bad = 1, False
        for i in range(1, n):
            run = run + 1 if pool[i] == pool[i - 1] else 1
            if run > max_run:
                bad = True
                break
        if not bad:
            return list(pool)
    # Deterministic repair: walk the sequence and swap offenders forward.
    for i in range(max_run, n):
        window = pool[i - max_run:i + 1]
        if len(set(window)) == 1:
            for j in range(i + 1, n):
                if pool[j] != pool[i]:
                    pool[i], pool[j] = pool[j], pool[i]
                    break
    return pool


def assign_keys(cases, seed=20260815):
    """Give every item an `order` (authored indices in print order) and a
    `key` (the printed answer letters). Single-answer letters follow the
    balanced target; items flagged fixed_order keep their authored order."""
    for session in (1, 2):
        block = [c for c in cases if c.get("session") == session]
        rng = random.Random(seed + session)

        movable = []
        for case in block:
            for item in case["items"]:
                if is_multi(item):
                    continue
                if item.get("fixed_order"):
                    continue
                movable.append(item)

        targets = _target_sequence(len(movable), rng)
        for item, letter in zip(movable, targets):
            options = item["options"]
            at = next(j for j, o in enumerate(options) if o.get("correct"))
            want = LETTERS.index(letter)
            # Rotate rather than swap: authored order survives cyclically, so
            # graded or paired options stay next to each other.
            shift = (at - want) % len(options)
            item["order"] = [(j + shift) % len(options) for j in range(len(options))]

        for case in block:
            for i, item in enumerate(case["items"]):
                options = item["options"]
                if "order" not in item:
                    if is_multi(item) and not item.get("fixed_order"):
                        # Spread correct sets off ABC without a distribution target.
                        shift = (case["n"] + i) % len(options)
                        item["order"] = [(j + shift) % len(options)
                                         for j in range(len(options))]
                    else:
                        item["order"] = list(range(len(options)))
                item["key"] = ", ".join(
                    LETTERS[pos] for pos, src in enumerate(item["order"])
                    if options[src].get("correct"))
                item["letter_of"] = {src: LETTERS[pos]
                                     for pos, src in enumerate(item["order"])}
    return cases


def key_table(cases):
    """Printed key as {session: [(case_id, [letters...])]}."""
    out = {1: [], 2: []}
    for case in cases:
        out[case["session"]].append(
            (case["id"], [item["key"] for item in case["items"]]))
    return out


def audit(cases):
    """Distribution report plus pass/fail against the rebuild target."""
    lines, problems = [], []
    grand = Counter()
    grand_n = 0

    for session in (1, 2):
        block = [c for c in cases if c.get("session") == session]
        if not block:
            continue
        keys = [item["key"] for c in block for item in c["items"]]
        single = [k for k in keys if len(k) == 1]
        multi = [k for k in keys if len(k) > 1]
        counts = Counter(single)
        grand.update(counts)
        grand_n += len(single)

        lines.append("")
        lines.append("Session %d" % session)
        lines.append("  %d items: %d single-answer, %d multiple-response"
                     % (len(keys), len(single), len(multi)))
        for letter in "ABCDE":
            n = counts.get(letter, 0)
            share = 100.0 * n / len(single) if single else 0
            lines.append("  %s %4d  %5.1f%%  %s"
                         % (letter, n, share, "#" * int(round(share / 2))))
            if not 18.0 <= share <= 22.0:
                problems.append("session %d letter %s at %.1f%%, target 18-22%%"
                                % (session, letter, share))
            if n == 0:
                problems.append("session %d never uses %s" % (session, letter))

        run = best = 1
        for i in range(1, len(single)):
            run = run + 1 if single[i] == single[i - 1] else 1
            best = max(best, run)
        lines.append("  longest run of one letter: %d" % best)
        if best > 3:
            problems.append("session %d has a run of %d, limit is 3" % (session, best))

        longest = 0
        for case in block:
            for item in case["items"]:
                if is_multi(item):
                    continue
                others = [len(o["t"]) for o in item["options"]
                          if not o.get("correct")]
                correct = next(len(o["t"]) for o in item["options"]
                               if o.get("correct"))
                if correct > max(others):
                    longest += 1
        share = 100.0 * longest / len(single) if single else 0
        lines.append("  correct option is strictly the longest: %d items "
                     "(%.0f%%), chance is 20%%" % (longest, share))
        if share > 34:
            problems.append("session %d: correct option longest in %.0f%% of items"
                            % (session, share))

        blind = max(counts.values()) if counts else 0
        lines.append("  best single-letter guess scores %d/%d (%.0f%%)"
                     % (blind, len(single), 100.0 * blind / len(single)))

    if grand_n:
        lines.append("")
        lines.append("Both sessions (%d single-answer items)" % grand_n)
        for letter in "ABCDE":
            lines.append("  %s %4d  %5.1f%%" % (letter, grand.get(letter, 0),
                                                100.0 * grand.get(letter, 0) / grand_n))
    return lines, problems
