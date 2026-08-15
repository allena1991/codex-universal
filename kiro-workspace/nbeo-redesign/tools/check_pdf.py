#!/usr/bin/env python3
"""Check a printed PDF: page count, page box in inches, and embedded fonts.

  python3 tools/check_pdf.py FILE [expected page count]

The page count defaults to the current length of the manual. Run it after every
export: a silently substituted font and a page box that is not letter both look
correct on screen and wrong on paper.
"""
import re
import sys
import zlib

path = sys.argv[1]
raw = open(path, "rb").read()

pages = len(re.findall(rb"/Type\s*/Page[^s]", raw))
boxes = set()
for m in re.finditer(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)", raw):
    w = float(m.group(3)) - float(m.group(1))
    h = float(m.group(4)) - float(m.group(2))
    boxes.add((round(w / 72, 2), round(h / 72, 2)))

fonts = sorted({m.group(1).decode("latin-1") for m in re.finditer(rb"/BaseFont\s*/([A-Za-z0-9+\-,_]+)", raw)})
names = sorted({f.split("+", 1)[-1] for f in fonts})

print("file      %s" % path)
print("bytes     %d (%.2f MB)" % (len(raw), len(raw) / 1048576))
print("pages     %d" % pages)
print("page box  %s inches" % ", ".join("%s x %s" % b for b in sorted(boxes)))
print("fonts     %s" % ", ".join(names))
print("embedded  %d font objects, %d subset-tagged"
      % (len(fonts), sum(1 for f in fonts if "+" in f)))

# Chromium substitutes a fallback face for fonts or glyphs it cannot embed.
# A missing body face shows up here even when the screen render looked correct,
# so the only tolerated fallback is the one documented below.
#
# Tolerated: NotoSans carries U+0394, the Greek delta used for prism dioptres.
# Spectral has no Greek coverage, and document.fonts.check reports it as covered,
# so this was proved by exporting copies with the character removed one at a
# time (tools/glyph_check.mjs). Removing the delta drops both Noto weights;
# removing U+00B5 drops nothing, so Spectral does cover the micron sign.
# Two weights appear because prism values are quoted inside question stems and
# short answers, which are set semibold.
ALLOWED_FALLBACK = {"NotoSans-Regular", "NotoSans-SemiBold"}
fallback = {n for n in names if n.startswith("Noto")}
expected = {"Spectral", "InstrumentSerif", "IBMPlexMono"}
missing = sorted(e for e in expected if not any(n.startswith(e) for n in names))

problems = []
# Pass the expected page count to assert it. Without one the count is reported
# but not checked, because the two volumes are different lengths.
if len(sys.argv) > 2 and pages != int(sys.argv[2]):
    problems.append("expected %s pages, found %d" % (sys.argv[2], pages))
if boxes != {(8.5, 11.0)}:
    problems.append("page box is not letter: %s" % boxes)
if fallback - ALLOWED_FALLBACK:
    problems.append("unexpected fallback font: %s" % ", ".join(sorted(fallback - ALLOWED_FALLBACK)))
if missing:
    problems.append("expected family not embedded: %s" % ", ".join(missing))
if fallback & ALLOWED_FALLBACK:
    print("note      %s embedded for the prism-dioptre delta only, proved by "
          "tools/glyph_check.mjs" % ", ".join(sorted(fallback & ALLOWED_FALLBACK)))

print("status    %s" % ("OK" if not problems else "; ".join(problems)))
sys.exit(0 if not problems else 1)
