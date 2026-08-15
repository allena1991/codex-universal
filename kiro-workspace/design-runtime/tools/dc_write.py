#!/usr/bin/env python3
"""Assemble a Design Component file from its three authored pieces.

    python3 tools/dc_write.py --out "Roadmap.dc.html" \
        --template examples/roadmap.template.html \
        --logic examples/roadmap.logic.js \
        --props examples/roadmap.props.json

The template is the markup that belongs between <x-dc> and </x-dc>; the logic is
`class Component extends DCLogic { ... }` with no <script> tag; props is the
data-props JSON. Document scaffolding is added here so it never appears in an
authored piece.
"""

import argparse
import json
import os
import re
import sys

REACT = "https://unpkg.com/react@18.3.1/umd/react.production.min.js"
REACT_DOM = "https://unpkg.com/react-dom@18.3.1/umd/react-dom.production.min.js"

HELMET_RE = re.compile(r"<helmet\b.*?</helmet\s*>", re.S | re.I)
HOLE_RE = re.compile(r"\{\{([^{}]*)\}\}")
NOT_A_PATH_RE = re.compile(r"[+*/!()\[\]?]|\s")

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script src="{react}" crossorigin="anonymous"></script>
<script src="{react_dom}" crossorigin="anonymous"></script>
<script src="{runtime}" defer></script>
</head>
<body>
<div id="dc-root"></div>
<x-dc>
{template}
</x-dc>
<script data-dc-script type="text/dc-logic"{props}>
{logic}
</script>
</body>
</html>
"""


def read(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def check_template(src):
    errors = []
    warnings = []
    lowered = src.lower()
    for token in ("<!doctype", "<html", "<x-dc", "</x-dc"):
        if token in lowered:
            errors.append('template contains document scaffolding "%s"' % token)
    without_helmet = HELMET_RE.sub("", src)
    if "<script" in without_helmet.lower():
        errors.append("<script> in the template body - only <helmet> may hold scripts")
    if re.search(r"<link\b[^>]*stylesheet", without_helmet, re.I):
        errors.append("stylesheet <link> outside <helmet>")
    if re.search(r"<style\b", without_helmet, re.I):
        errors.append("<style> outside <helmet> - styling is inline only")
    for match in HOLE_RE.finditer(src):
        inner = match.group(1).strip()
        if not inner:
            warnings.append("empty hole {{ }} renders nothing")
            continue
        if inner[0] in "\"'" and inner[-1] == inner[0]:
            continue
        if NOT_A_PATH_RE.search(inner):
            warnings.append(
                'hole "{{ %s }}" is not a dotted path - compute it in renderVals() and expose it by name' % inner
            )
    if re.search(r"<(dc-import|x-import)\b(?![^>]*hint-size)", src, re.I):
        warnings.append("an import is missing hint-size")
    if re.search(r"<(dc-import|x-import)[^>]*/>", src, re.I):
        errors.append("self-closed import tag - write the explicit close tag")
    if re.search(r"<sc-for\b(?![^>]*hint-placeholder-count)", src, re.I):
        warnings.append("<sc-for> is missing hint-placeholder-count")
    if re.search(r"<sc-if\b(?![^>]*hint-placeholder-val)", src, re.I):
        warnings.append("<sc-if> is missing hint-placeholder-val")
    if re.search(r"<[A-Z]", src):
        errors.append("capitalized component tag - use <dc-import name=\"...\">")
    return errors, warnings


def check_logic(src):
    errors = []
    if not src.strip():
        return errors
    if "class Component" not in src:
        errors.append("logic must define `class Component extends DCLogic`")
    if "</script" in src.lower():
        errors.append("logic contains a closing script tag")
    if re.search(r"^\s*(import|export)\s", src, re.M):
        errors.append("logic uses import/export - plain classic JavaScript only")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Assemble a .dc.html Design Component")
    parser.add_argument("--out", required=True, help="destination .dc.html path")
    parser.add_argument("--template", required=True, help="template file, or - for stdin")
    parser.add_argument("--logic", default=None, help="logic class file")
    parser.add_argument("--props", default=None, help="data-props JSON file")
    parser.add_argument("--title", default=None, help="document title (default: filename stem)")
    parser.add_argument("--runtime", default="support.js", help="src for the runtime include")
    parser.add_argument("--force", action="store_true", help="write even when checks fail")
    args = parser.parse_args()

    if not args.out.endswith(".dc.html"):
        parser.error("--out must end in .dc.html")

    template = read(args.template).strip("\n")
    logic = read(args.logic).strip("\n") if args.logic else ""
    props_raw = read(args.props) if args.props else ""

    errors, warnings = check_template(template)
    errors += check_logic(logic)

    props_attr = ""
    if props_raw.strip():
        try:
            parsed = json.loads(props_raw)
        except json.JSONDecodeError as exc:
            errors.append("props is not valid JSON: %s" % exc)
        else:
            for key, meta in parsed.items():
                if key.startswith("$"):
                    continue
                if not isinstance(meta, dict) or "editor" not in meta:
                    errors.append('prop "%s" needs an editor field (or null)' % key)
                elif meta["editor"] == "enum" and "options" not in meta:
                    errors.append('enum prop "%s" needs options' % key)
            encoded = json.dumps(parsed, separators=(",", ":")).replace("'", "&#39;")
            props_attr = " data-props='%s'" % encoded

    for warning in warnings:
        print("warn: %s" % warning, file=sys.stderr)
    if errors:
        for error in errors:
            print("error: %s" % error, file=sys.stderr)
        if not args.force:
            return 1

    title = args.title or os.path.basename(args.out)[: -len(".dc.html")]
    page = PAGE.format(
        title=title,
        react=REACT,
        react_dom=REACT_DOM,
        runtime=args.runtime,
        template=template,
        props=props_attr,
        logic=logic or "class Component extends DCLogic {}",
    )

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as handle:
        handle.write(page)
    print("wrote %s (%d bytes)" % (args.out, len(page)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
