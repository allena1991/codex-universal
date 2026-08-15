#!/usr/bin/env python3
"""Generated sheets and blocks: things that must agree with the case data.

Anything derived from the cases is built here rather than typed by hand, so a
change to a case cannot leave a stale index, key, or score sheet behind. That
was the failure mode in the source guide, where the printed key and the
rationales disagreed with each other.
"""

from collections import Counter
from render import esc, sheet, block_cost, _lines, USABLE
from schema import TYPES, audit, is_multi

TYPE_SHORT = {"diagnosis": "Dx", "treatment": "Tx", "basic": "Sci",
              "legal": "Law"}


def short_tag(item):
    """Dx, Tx, Sci or Law, with a star when the item is all-or-none."""
    return TYPE_SHORT[item["type"]] + ("*" if is_multi(item) else "")


# --------------------------------------------------------------------------
# key integrity: the audit result, printed inside the book
# --------------------------------------------------------------------------

def key_integrity(cases):
    out = []
    for session in (1, 2):
        block = [c for c in cases if c["session"] == session]
        keys = [i["key"] for c in block for i in c["items"]]
        single = [k for k in keys if len(k) == 1]
        counts = Counter(single)
        if not single:
            continue
        run = best = 1
        for i in range(1, len(single)):
            run = run + 1 if single[i] == single[i - 1] else 1
            best = max(best, run)
        bars = []
        for letter in "ABCDE":
            share = 100.0 * counts.get(letter, 0) / len(single)
            bars.append(
                '<div class="kbar"><span class="kl">%s</span>'
                '<span class="kt"><span class="target" style="left:%.1f%%;width:%.1f%%"></span>'
                '<span class="kf" style="width:%.1f%%"></span></span>'
                '<span class="kv">%d &middot; %.1f%%</span></div>'
                % (letter, 18 / 0.30, 4 / 0.30, share / 0.30,
                   counts.get(letter, 0), share))
        axis = ('<div class="kaxis"><span></span><span class="kt">'
                '<span style="left:0">0</span><span style="left:33.3%">10%</span>'
                '<span style="left:60%">18</span><span style="left:73.3%">22</span>'
                '<span style="left:100%">30%</span></span><span></span></div>')
        out.append(
            '<h3>Session %d, %d single-answer items</h3>%s%s'
            '<p class="tiny" style="margin-top:4px">Share of single-answer items on '
            'which each letter is correct. Dashed band is the 18-22%% target. '
            'Longest run of one letter: %d. The best single-letter guess scores '
            '%d of %d, %.0f%%.</p>'
            % (session, len(single), "".join(bars), axis, best,
               max(counts.values()), len(single),
               100.0 * max(counts.values()) / len(single)))
    return "".join(out)


# --------------------------------------------------------------------------
# case index, with page references resolved later
# --------------------------------------------------------------------------

def case_index(cases, session):
    rows = []
    for case in [c for c in cases if c["session"] == session]:
        types = " ".join(short_tag(i) for i in case["items"])
        rows.append(
            '<tr><td>%s</td><td>%s</td><td>%s</td><td class="t">%s</td>'
            '<td class="t">{{PGREF:%s}}</td><td class="t">{{PGREF:key-%s}}</td></tr>'
            % (esc(case["id"]), esc(case["title"]), esc(case["domain"]),
               esc(types), esc(case["id"]), esc(case["id"])))
    return ('<table class="idx lined"><thead><tr><th>Case</th><th>Presentation</th>'
            '<th>Domain</th><th>Items</th><th>Case</th><th>Key</th></tr></thead>'
            '<tbody>%s</tbody></table>' % "".join(rows))


# --------------------------------------------------------------------------
# score by item type: the capture grid that doubles as the diagnosis of you
# --------------------------------------------------------------------------

def score_sheets(cases, session):
    block = [c for c in cases if c["session"] == session]
    rows = []
    for case in block:
        cells = []
        for item in case["items"]:
            cells.append('<td class="w">%s</td>' % short_tag(item))
        cells += ['<td class="w"></td>'] * (6 - len(case["items"]))
        rows.append('<tr><td>%s</td>%s<td class="sum"></td><td class="sum"></td>'
                    '<td class="sum"></td><td class="sum"></td></tr>'
                    % (esc(case["id"]), "".join(cells)))
    table = (
        '<table class="ans"><thead><tr><th>Case</th>'
        '<th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th>'
        '<th>Dx</th><th>Tx</th><th>Sci</th><th>Law</th></tr></thead>'
        '<tbody>%s</tbody><tfoot><tr><td>Totals</td>'
        '<td colspan="6">Mark each item R or W. A star means all or none</td>'
        '<td colspan="4">Then total the right-hand columns by item type</td>'
        '</tr></tfoot></table>' % "".join(rows))
    body = (
        '<h2>Session %d &middot; score by item type</h2>'
        '<p class="lede" style="margin-top:8px">Each cell carries its item type. '
        'Mark it right or wrong, then total the five columns on the right.</p>'
        '<div style="margin-top:11px">%s</div>'
        '<div class="callout"><b>Reading your own totals</b>Under 60%% in any '
        'single column is a study plan, not a bad day. Diagnosis misses send you '
        'to the condition cards. Treatment misses send you to pharmacology and '
        'the emergency gate. Basic science misses are the cheapest to fix and the '
        'easiest to postpone.</div>' % (session, table))
    return [sheet(body, "S%d score sheet" % session,
                  "Session %d / Score by item type" % session,
                  "Score sheet &middot; {{PG}}")]


# --------------------------------------------------------------------------
# printed answer key
# --------------------------------------------------------------------------

def answer_key_sheets(cases):
    tables = []
    for session in (1, 2):
        block = [c for c in cases if c["session"] == session]
        rows = []
        for case in block:
            cells = "".join('<td>%s</td>' % esc(i["key"]) for i in case["items"])
            cells += '<td></td>' * (6 - len(case["items"]))
            rows.append('<tr><td>%s</td>%s</tr>' % (esc(case["id"]), cells))
        tables.append(
            '<h3>Session %d</h3><table class="idx lined"><thead><tr><th>Case</th>'
            '<th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th>'
            '</tr></thead><tbody>%s</tbody></table>' % (session, "".join(rows)))
    body = ('<h2>Answer key</h2>'
            '<p class="lede" style="margin-top:8px">Letters are generated to the '
            'distribution on the key-integrity page, not chosen by whoever wrote '
            'the item. Guessing one letter throughout scores close to a fifth of '
            'the paper, which is what it should score.</p>'
            '<div class="cols2" style="margin-top:11px">%s</div>'
            % "".join(tables))
    return [sheet(body, "Answer key", "Part 10 / Answer key",
                  "Answer key &middot; {{PG}}")]


# --------------------------------------------------------------------------
# competing pairs
# --------------------------------------------------------------------------

def _pair_html(case):
    pair = case["pair"]
    rows = []
    for row in pair["rows"]:
        rows.append('<div class="pr split"><span>%s</span><span>%s</span>'
                    '<span>%s</span></div>'
                    % (esc(row[0]), esc(row[1]), esc(row[2])))
    rows.append('<div class="pr decider"><span>Decider</span>'
                '<span style="grid-column:span 2">%s</span></div>'
                % esc(pair["decider"]))
    return ('<div class="pair"><div class="ph"><b>%s</b><i>vs</i><b>%s</b></div>'
            '%s</div>' % (esc(pair["this"]), esc(pair["vs"]), "".join(rows)))


def pair_cost(case):
    pair = case["pair"]
    cost = 8.0 + 17.7                                   # margin and header
    for row in pair["rows"]:
        cost += max(_lines(row[1], 52), _lines(row[2], 52),
                    _lines(row[0], 12)) * 11.2 + 6.6
    cost += _lines(pair["decider"], 105) * 11.2 + 6.6
    return cost


def pair_sheets(cases):
    have = [c for c in cases if c.get("pair")]
    if not have:
        return []
    blocks = [(_pair_html(c), pair_cost(c)) for c in have]
    lede = ('<p class="lede" style="margin-top:8px">Each pair is two conditions '
            'that trade places under time pressure. The decider row is the single '
            'finding that separates them, which is the finding the item will turn '
            'on.</p>')
    pages, current, used = [], [], 62.0 + block_cost(lede, 100, 16.6, 8.0)
    for html, cost in blocks:
        if current and used + cost > USABLE:
            pages.append(current)
            current, used = [], 58.0
        current.append(html)
        used += cost
    pages.append(current)

    out = []
    for p, chunk in enumerate(pages):
        title = ('<h2>Competing pairs</h2>' + lede if p == 0
                 else '<h2>Competing pairs, continued</h2>')
        out.append(sheet(title + '<div style="margin-top:10px">%s</div>'
                         % "".join(chunk),
                         "Competing pairs %d" % (p + 1),
                         "Part 7 / Competing pairs, %d of %d" % (p + 1, len(pages)),
                         "Competing pairs &middot; {{PG}}"))
    return out


# --------------------------------------------------------------------------
# spaced repetition schedule, keyed to real case numbers
# --------------------------------------------------------------------------

SCHEDULE = [
    ("Day 1", "S1-01 to S1-05", "Cases cold, keys same evening", "-"),
    ("Day 2", "S1-06 to S1-10", "Cases cold", "S1-01 to S1-05 recall cards"),
    ("Day 3", "S1-11 to S1-15", "Cases cold", "S1-01 to S1-10 missed items only"),
    ("Day 4", "S1-16 to S1-20", "Cases cold", "S1-06 to S1-15 recall cards"),
    ("Day 5", "S1-21 to S1-25", "Cases cold", "S1-01 to S1-10 second pass"),
    ("Day 6", "S1-26 to S1-30", "Cases cold", "S1-16 to S1-25 recall cards"),
    ("Day 7", "S1-31 to S1-35", "Cases cold", "Score all of Session 1 by item type"),
    ("Day 8", "Repair", "Weakest two item-type columns", "Condition cards, pharmacology"),
    ("Day 9", "S2-01 to S2-06", "Cases cold", "S1 missed items, third pass"),
    ("Day 10", "S2-07 to S2-12", "Cases cold", "S1-26 to S1-35 recall cards"),
    ("Day 11", "S2-13 to S2-18", "Cases cold", "Emergency gate, aloud"),
    ("Day 12", "S2-19 to S2-24", "Cases cold", "S2-01 to S2-12 missed items"),
    ("Day 13", "S2-25 to S2-30", "Cases cold", "Competing pairs, aloud"),
    ("Day 14", "S2-31 to S2-35", "Cases cold", "Score all of Session 2 by item type"),
    ("Day 15", "Timed run", "Session 1 in one 3.5 hour block", "Compare to first pass"),
    ("Day 16", "Repair", "Every item still missed twice", "Rewrite each as a rule"),
    ("Day 17", "Timed run", "Session 2 in one 3.5 hour block", "Score by item type"),
    ("Day 18", "Consolidate", "Emergency gate and competing pairs", "Formulas, drilled"),
]


def schedule_sheets():
    rows = "".join(
        '<tr><td class="d">%s</td><td>%s</td><td>%s</td><td class="w">%s</td></tr>'
        % (esc(a), esc(b), esc(c), esc(d)) for a, b, c, d in SCHEDULE)
    body = (
        '<h2>Eighteen days</h2>'
        '<p class="lede" style="margin-top:8px">Cases are answered cold, once. '
        'Everything after that is recall, not rereading. The right-hand column is '
        'the part people skip and the part that moves the score.</p>'
        '<table class="lined sched" style="margin-top:11px"><thead><tr><th>Day</th>'
        '<th>New</th><th>Work</th><th>Recall</th></tr></thead><tbody>%s</tbody>'
        '</table>'
        '<div class="note"><b>If you have fewer than eighteen days</b>Keep the '
        'recall column and cut new cases, not the reverse. Ten cases reviewed to '
        'the point of recall beat thirty-five read once. If you have four days, '
        'run the emergency gate, the competing pairs, and the score sheets for '
        'both sessions, and accept that the rest is coverage you will not '
        'get.</div>' % rows)
    return [sheet(body, "Schedule", "Part 10 / Eighteen days",
                  "Schedule &middot; {{PG}}")]


# --------------------------------------------------------------------------
# audit page for the colophon
# --------------------------------------------------------------------------

def audit_text(cases):
    lines, problems = audit(cases)
    return "\n".join(lines), problems
