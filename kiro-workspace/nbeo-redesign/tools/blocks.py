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

def index_sheet(records, session, guide):
    body = ('<h2>Session %d &middot; case index</h2>'
            '<p class="lede" style="margin-top:8px">Sorted as sat. Dx diagnosis, '
            'Tx treatment, Sci basic science, Law law and ethics. A star marks an '
            'all-or-none item, which is a format, not a type. Use the item-type '
            'column to work one weakness across the whole session.</p>'
            '<div style="margin-top:10px">%s</div>'
            % (session, case_index(records, session)))
    return sheet(body, "S%d case index" % session,
                 "Session %d / Case index" % session,
                 "Case index &middot; {{PG}}")


def domain_index_sheets(records):
    """Every case grouped by domain, which is the order this guide prints in.

    Rows are costed individually and packed, because a domain heading and a
    two-line presentation are not the same height and the page clips.
    """
    by_domain = {}
    for rec in records:
        by_domain.setdefault(rec["domain"], []).append(rec)

    rows = []
    for domain in sorted(by_domain, key=str.lower):
        block = sorted(by_domain[domain], key=lambda r: r["id"])
        rows.append(('<tr><td class="dom" colspan="4">%s &middot; %d cases</td></tr>'
                     % (esc(domain), len(block)), 15.5))
        for rec in block:
            rows.append((
                '<tr><td>%s</td><td>%s</td><td class="t">%s</td>'
                '<td class="t">{{PGREF:%s}}</td></tr>'
                % (esc(rec["id"]), esc(rec["title"]),
                   esc(" ".join(short_tag(i) for i in rec["items"])),
                   esc(rec["id"])),
                _lines(rec["title"], 52) * 11.6 + 1.6))

    lede = ('<p class="lede" style="margin-top:8px">This manual prints in this '
            'order: by domain, then by case number, with each teaching key on '
            'the page after its case. Competing conditions land within a few '
            'pages of each other, which is where the discriminators stick.</p>')
    head = 62.0 + block_cost(lede, 100, 16.6, 8.0)
    thead = 20.0

    pages, current, used = [], [], head + thead
    for html, cost in rows:
        if current and used + cost > USABLE:
            pages.append(current)
            current, used = [], 60.0 + thead
        current.append(html)
        used += cost
    pages.append(current)

    out = []
    for n, chunk in enumerate(pages):
        title = ('<h2>Domain index</h2>' + lede if n == 0
                 else '<h2>Domain index, continued</h2>')
        out.append(sheet(
            title + '<div style="margin-top:10px"><table class="idx lined">'
            '<thead><tr><th>Case</th><th>Presentation</th><th>Items</th>'
            '<th>Page</th></tr></thead><tbody>%s</tbody></table></div>'
            % "".join(chunk),
            "Domain index %d" % (n + 1),
            "Part 8 / Domain index, %d of %d" % (n + 1, len(pages)),
            "Domain index &middot; {{PG}}"))
    return out


def score_sheets(records, session, guide=None):
    cases = records
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

def answer_key_sheets(cases, guide=None):
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
            'distribution audited on page {{PGREF:keyint}}, not chosen by whoever '
            'wrote the item. Guessing one letter throughout scores close to a '
            'fifth of the paper, which is what it should score. Multiple letters '
            'in a cell mean an all-or-none item: every one, or no mark.</p>'
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

def _plan(records):
    """Eighteen days across both sessions, generated from the real case ids so
    the plan cannot drift from the bank."""
    ids = {s: sorted(r["id"] for r in records if r["session"] == s)
           for s in (1, 2)}
    rows, day = [], 0

    def span(session, lo, hi):
        block = ids[session][lo:hi]
        return "%s to %s" % (block[0], block[-1]) if len(block) > 1 else block[0]

    for session in (1, 2):
        n = len(ids[session])
        step = 5
        for start_i in range(0, n, step):
            day += 1
            done = start_i
            recall = ("-" if done == 0 else
                      "%s, missed items" % span(session, max(0, done - 10), done))
            rows.append(("Day %d" % day,
                         span(session, start_i, min(start_i + step, n)),
                         "Cases cold, keys the same evening", recall))
        day += 1
        rows.append(("Day %d" % day, "Score Session %d" % session,
                     "By item type, not just the total",
                     "The two weakest columns, worked through"))
    rows += [
        ("Day %d" % (day + 1), "Repair",
         "Every item missed with high confidence",
         "Rewrite each as one if-then rule"),
        ("Day %d" % (day + 2), "Timed run",
         "Session 1 again, 175 items in 3.5 hours",
         "Compare to the first pass by column"),
        ("Day %d" % (day + 3), "Timed run",
         "Session 2 again, under the same conditions",
         "Score by item type"),
        ("Day %d" % (day + 4), "Consolidate",
         "Emergency gate and competing pairs, aloud",
         "Formulas drilled, then stop"),
    ]
    return rows


def schedule_sheets(records, guide=None):
    rows = "".join(
        '<tr><td class="d">%s</td><td>%s</td><td>%s</td><td class="w">%s</td></tr>'
        % (esc(a), esc(b), esc(c), esc(d)) for a, b, c, d in _plan(records))
    body = (
        '<h2>Eighteen days</h2>'
        '<p class="lede" style="margin-top:8px">Both sessions, eighteen days, '
        'generated from the case numbers in this book. Cases are answered cold, '
        'once. Everything after that is recall, not rereading. The right-hand '
        'column is the part people skip and the part that moves the score.</p>'
        '<table class="lined sched" style="margin-top:11px"><thead><tr><th>Day</th>'
        '<th>New</th><th>Work</th><th>Recall</th></tr></thead><tbody>%s</tbody>'
        '</table>'
        '<div class="note"><b>Read the two score sheets side by side</b>Compare '
        'them by item-type column, not by total. A total that rose while the '
        'treatment column fell is a warning, not progress, because treatment '
        'carries the largest share of the blueprint and decides TMOD '
        'separately.</div>'
        '<div class="callout"><b>If you have fewer than eighteen days</b>Keep the '
        'recall column and cut new cases, not the reverse. Ten cases reviewed to '
        'the point of recall beat thirty-five read once. With four days: the '
        'emergency gate, the competing pairs, and one timed half session.</div>'
        % rows)
    return [sheet(body, "Schedule", "Part 10 / Eighteen days",
                  "Schedule &middot; {{PG}}")]


# --------------------------------------------------------------------------
# audit page for the colophon
# --------------------------------------------------------------------------

def audit_text(cases):
    lines, problems = audit(cases)
    return "\n".join(lines), problems
