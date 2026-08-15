#!/usr/bin/env python3
"""Sheet rendering for the manual: case sheets, teaching keys, generated blocks.

Every sheet is a fixed 11in box with overflow hidden, so anything that does not
fit is silently clipped in print. Python cannot measure text, so this module
carries a cost model in typographic points, calibrated against the real
Chromium render, and packs rationales into as many sheets as they need.
tools/shoot.mjs is the check that keeps the model honest.
"""

import math
import re
from schema import LETTERS, TYPES, is_multi

# Every number below is in typographic points and was measured in a real
# Chromium render by tools/calibrate.mjs, not estimated. Re-measure after any
# change to the CSS in content/base.css.
#
#   sheet 11in = 792pt, less 0.5in top and 0.34in bottom padding  -> 731.5
#   less the running head (24.1) and the footer (24.2)            -> 683.2
#   less a 13pt reserve, because measured pages ran a few points over  -> 670.0
USABLE = 670.0
# A teaching key opens with an h2 (25.5) and a 9px gap (6.8).
KEY_HEAD = 32.3

_ENTITY = re.compile(r"&(?![a-zA-Z]+;|#\d+;)")


def esc(text):
    """Escape for HTML while leaving authored entities such as &nbsp; alone."""
    text = _ENTITY.sub("&amp;", str(text))
    return text.replace("<", "&lt;").replace(">", "&gt;")


def _lines(text, per_line):
    return max(1, math.ceil(len(text) / float(per_line)))


# --------------------------------------------------------------------------
# cost model
# --------------------------------------------------------------------------

def item_cost(item):
    cost = 16.0                                         # margins and capture strip
    cost += _lines(item["q"], 95) * 13.4                # question, 10pt semibold
    cost += sum(_lines(o["t"], 112) * 12.2              # 9.5pt option rows
                for o in item["options"])
    return cost


def head_cost(case):
    """Case title block plus the stem panel."""
    return 46.3 + _lines(case["stem"], 112) * 14.3 + 9.0


def case_cost(case):
    return head_cost(case) + sum(item_cost(i) for i in case["items"])


def rat_cost(item):
    cost = 7.5                                          # margin, padding, rule
    label = "%s %s" % (item.get("key", "A"), item.get("short", ""))
    cost += _lines(label, 85) * 13.8                    # key badge and answer
    cost += _lines(item["why"], 112) * 11.6 + 3.0
    cost += 13.7                                        # table head
    for row in item["dis"]:
        span = max(_lines(row["tempting"], 44), _lines(row["ruled"], 44),
                   _lines(row["label"], 18))
        cost += span * 10.4 + 3.7
    return cost


def block_cost(html, per_line=100, line=13.0, base=12.0):
    """Rough cost for an authored HTML block, used to pack mixed sheets."""
    text = re.sub(r"<[^>]+>", " ", html)
    return base + _lines(re.sub(r"\s+", " ", text).strip(), per_line) * line


# --------------------------------------------------------------------------
# sheet chrome
# --------------------------------------------------------------------------

def sheet(body, label, part="", foot_right="", classes="", chrome=True):
    head = ""
    if chrome:
        head = ('<div class="rh"><span class="part">%s</span>'
                '<span class="pg">{{PG}}</span></div>' % esc(part))
        body = body + (
            '<div class="rf"><span>Clinical Reasoning Manual &middot; PAM/TMOD</span>'
            '<span>%s</span></div>' % (foot_right or esc(part)))
    cls = ("sheet " + classes).strip()
    return ('<section class="%s" data-screen-label="%s">\n%s\n%s\n</section>\n'
            % (cls, esc(label), head, body))


# --------------------------------------------------------------------------
# case sheets
# --------------------------------------------------------------------------

def _options_html(item):
    rows = []
    for pos, src in enumerate(item["order"]):
        rows.append('<li><span>%s</span><div>%s</div></li>'
                    % (LETTERS[pos], esc(item["options"][src]["t"])))
    return '<ol class="opts">%s</ol>' % "".join(rows)


def _item_html(item, number):
    label, css = TYPES[item["type"]]
    if is_multi(item):
        n = sum(1 for o in item["options"] if o.get("correct"))
        label, css = "%s &middot; select %d" % (label, n), (css + " mr").strip()
    tag = '<span class="tag%s">%s</span>' % ((" " + css) if css else "", label)
    return (
        '<div class="item">'
        '<div class="q"><span class="n">%d</span><span class="qt">%s</span>%s</div>'
        '%s'
        '<div class="capture">ANSWER ______ &nbsp;&nbsp; CONFIDENCE&nbsp; L &middot; M &middot; H</div>'
        '</div>' % (number, esc(item["q"]), tag, _options_html(item))
    )


def case_sheets(case):
    """The presented case: stem plus items. Splits if it cannot fit one sheet."""
    head = (
        '<div class="case-head">'
        '<div class="cid">Case %s &middot; %s &middot; %d items</div>'
        '<h3>%s</h3></div>'
        '<p class="stem">%s</p>'
        % (esc(case["id"]), esc(case["domain"].lower()), len(case["items"]),
           esc(case["title"]), esc(case["stem"]))
    )
    pages, current, used = [], [], head_cost(case)
    for i, item in enumerate(case["items"], 1):
        cost = item_cost(item)
        if current and used + cost > USABLE:
            pages.append(current)
            current, used = [], 46.3
        current.append(_item_html(item, i))
        used += cost
    pages.append(current)

    out = []
    for p, chunk in enumerate(pages):
        part = "Session %d / Case %d of 35" % (case["session"], case["n"])
        body = (head if p == 0 else
                '<div class="case-head"><div class="cid">Case %s, continued</div>'
                '<h3>%s</h3></div>' % (esc(case["id"]), esc(case["title"])))
        used = (head_cost(case) if p == 0 else 46.3) + sum(
            item_cost(case["items"][i]) for i in range(len(case["items"]))
            if _in_chunk(chunk, i))
        chunk = list(chunk) + [_tail(case, USABLE - used)]
        out.append(sheet(body + "".join(chunk),
                         "%s case%s" % (case["id"], "" if p == 0 else " cont"),
                         part, "Case %s &middot; {{PG}}" % esc(case["id"])))
    return out


# --------------------------------------------------------------------------
# teaching keys
# --------------------------------------------------------------------------

def _rat_html(item, number):
    rows = []
    for row in item["dis"]:
        letters = ", ".join(item["letter_of"][r] for r in sorted(
            row["refs"], key=lambda r: item["letter_of"][r]))
        rows.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                    % (esc(letters), esc(row["label"]),
                       esc(row["tempting"]), esc(row["ruled"])))
    return (
        '<div class="rat compact">'
        '<div class="rh2"><span class="key">%d &middot; %s</span>'
        '<span class="rt">%s</span></div>'
        '<p class="why">%s</p>'
        '<table class="dis"><thead><tr><th>Opt</th><th>Distractor</th>'
        '<th>Tempting because</th><th>Ruled out by</th></tr></thead>'
        '<tbody>%s</tbody></table></div>'
        % (number, esc(item["key"]), esc(item.get("short", "")),
           esc(item["why"]), "".join(rows))
    )


def _in_chunk(chunk, index):
    """True when item `index` was packed onto this sheet."""
    return any(('<span class="n">%d</span>' % (index + 1)) in html for html in chunk)


TIMING = 24.0
NOTE_LINE = 17.7


def _tail(case, room):
    """Pacing strip and note rules, sized to whatever column is left over."""
    if room < TIMING + NOTE_LINE:
        return ""
    minutes = len(case["items"]) + 1
    out = ('<div class="timing"><b>Target %d min</b><span>Started ______</span>'
           '<span>Finished ______</span><span>Flagged ______</span></div>'
           % minutes)
    lines = int((room - TIMING - 6.0) // NOTE_LINE)
    if lines > 0:
        out += '<div class="notelines">%s</div>' % ("<i></i>" * min(lines, 7))
    return out


def key_sheets(case):
    """Teaching key: why the answer is the answer, and why each trap works."""
    blocks = [(_rat_html(item, i), rat_cost(item))
              for i, item in enumerate(case["items"], 1)]

    tail = ""
    if case.get("rules"):
        tail += ('<div class="callout"><b>If-then rules from this case</b>%s</div>'
                 % esc(case["rules"]))
    tail_cost = block_cost(tail, 104, 13.4, 20.0) if tail else 0.0

    pages, current, used = [], [], KEY_HEAD
    for html, cost in blocks:
        if current and used + cost + tail_cost > USABLE:
            pages.append(current)
            current, used = [], KEY_HEAD
        current.append(html)
        used += cost
    pages.append(current)

    out = []
    for p, chunk in enumerate(pages):
        last = p == len(pages) - 1
        title = ('<h2>Case %s &middot; why</h2>' % esc(case["id"]) if p == 0 else
                 '<h2>Case %s &middot; why, continued</h2>' % esc(case["id"]))
        body = title + '<div style="margin-top:9px">%s%s</div>' % (
            "".join(chunk), tail if last else "")
        out.append(sheet(body,
                         "%s key%s" % (case["id"], "" if p == 0 else " cont"),
                         "Session %d / Teaching key, Case %d"
                         % (case["session"], case["n"]),
                         "Key %s &middot; {{PG}}" % esc(case["id"])))
    return out


# --------------------------------------------------------------------------
# fit contract
# --------------------------------------------------------------------------

# Each case is one presented sheet and one teaching key. Content that does not
# respect these caps pushes a case to three sheets, which is how a 170-page
# manual becomes a 240-page one. The caps are the contract; shoot.mjs is proof.
CAPS = {"stem": 440, "q": 145, "option": 112, "why": 205, "short": 70,
        "tempting": 88, "ruled": 88, "label": 30, "rules": 200}


def fit_problems(cases):
    problems = []
    for case in cases:
        cid = case["id"]
        if len(case["stem"]) > CAPS["stem"]:
            problems.append("%s: stem %d chars, cap %d"
                            % (cid, len(case["stem"]), CAPS["stem"]))
        if len(case.get("rules", "")) > CAPS["rules"]:
            problems.append("%s: rules %d chars, cap %d"
                            % (cid, len(case["rules"]), CAPS["rules"]))
        for i, item in enumerate(case["items"], 1):
            tag = "%s item %d" % (cid, i)
            for field in ("q", "why", "short"):
                if len(item.get(field, "")) > CAPS[field]:
                    problems.append("%s: %s %d chars, cap %d"
                                    % (tag, field, len(item[field]), CAPS[field]))
            for o in item.get("options", []):
                if len(o.get("t", "")) > CAPS["option"]:
                    problems.append("%s: option %d chars, cap %d: %s"
                                    % (tag, len(o["t"]), CAPS["option"], o["t"][:44]))
            rows = item.get("dis", [])
            if len(rows) > 3:
                problems.append("%s: %d distractor rows, cap 3" % (tag, len(rows)))
            for row in rows:
                for field in ("tempting", "ruled", "label"):
                    if len(row.get(field, "")) > CAPS[field]:
                        problems.append("%s: %s %d chars, cap %d"
                                        % (tag, field, len(row[field]), CAPS[field]))

        presented = len(case_sheets(case))
        keyed = len(key_sheets(case))
        if presented > 1:
            problems.append("%s: presented case needs %d sheets, trim the stem "
                            "or the options" % (cid, presented))
        if keyed > 1:
            problems.append("%s: teaching key needs %d sheets, trim the whys and "
                            "distractor rows (cost %.0f of %.0f)"
                            % (cid, keyed, KEY_HEAD
                               + sum(rat_cost(i) for i in case["items"]), USABLE))
    return problems
