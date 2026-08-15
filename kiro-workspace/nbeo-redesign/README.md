# NBEO Part II PAM/TMOD Clinical Reasoning Manual

A rebuilt replacement for a 120-page study guide whose answer key was 82% option A.
179 letter pages, 70 cases, 350 items, built from data rather than typed.

`AUDIT.md` is the case for the rebuild: what was wrong with the original, measured.
`content/AUTHORING.md` is the contract every case is written against.

## Build

```
python3 tools/build.py                                  # content -> index.html
node tools/shoot.mjs                                    # fails if any page clips
node tools/to_pdf.mjs                                   # index.html -> PDF
python3 tools/check_pdf.py "NBEO PAM-TMOD Clinical Reasoning Manual.pdf"
```

All four must pass. `build.py` refuses to write if the answer key misses its
distribution target, `shoot.mjs` exits non-zero if a single page is clipped, and
`check_pdf.py` catches a substituted font, which looks correct on screen and
wrong on paper.

In this sandbox node is not on the default PATH:

```
NODE=$(ls -d /root/.nvm/versions/node/*/bin/node | tail -1)
"$NODE" tools/shoot.mjs
```

## Layout

```
content/
  AUTHORING.md      the authoring contract: schema, length caps, item rules
  pattern.json      one fully worked case, the quality bar
  base.css          the whole design system, one file
  cases/*.json      70 cases in eight batches
  partials/*.html   27 authored reference sheets, with front matter
tools/
  schema.py         validation and answer-letter generation
  render.py         case and teaching-key sheets, and the fit model
  blocks.py         everything derived from the cases: index, key, pairs, score
  build.py          assembly, pagination, cross-references
  check_batch.py    check one authored batch before it enters the build
  calibrate.mjs     measure real block heights, to fit the cost model to them
  shoot.mjs         measure every page in a real render, fail on any clip
  preview.mjs       PNG of named sheets, for review
  to_pdf.mjs        print through Chromium at letter size
  check_pdf.py      page count, page box, embedded fonts
  glyph_check.mjs   prove which characters force a fallback face
  key_audit.py      the previous edition's key, kept as the record of the defect
  stub.py           worst-case filler content, for calibrating the layout
```

## Two decisions worth knowing before editing

**Answer letters are generated, not authored.** Item writers mark the correct
option in place and never choose a letter. `schema.assign_keys` deals an even
multiset of A to E across each session, rejects any sequence with a run longer
than three, and rotates each item's options so the correct one lands on its
assigned letter. Rotation rather than shuffling keeps graded and paired options
adjacent. The audit printed on page 4 of the manual comes from the same run that
produced the pages, so it cannot drift.

**Pages are fixed boxes that clip.** Every sheet is `height: 11in;
overflow: hidden`, so content that does not fit is lost in print rather than
reflowed. Python cannot measure text, so `render.py` carries a cost model in
typographic points that was fitted to real measurements from `calibrate.mjs`,
with a 13pt reserve. `shoot.mjs` is what keeps the model honest: it measures
`scrollHeight - clientHeight` for all 179 pages. Re-run `calibrate.mjs` after any
change to `base.css`, because the constants in `render.py` depend on it.

## Current state

| | |
| --- | --- |
| Pages | 179, letter, 1.76 MB |
| Cases and items | 70 cases, 350 items, all 17 blueprint domains |
| Key, both sessions | A 19.6%, B 19.6%, C 20.7%, D 20.4%, E 19.6% |
| Longest run of one letter | 3 |
| Correct option strictly longest | 13%, against 20% by chance |
| Distractor rationale rows | 711 |
| Item types | Tx 44.3%, Dx 34.0%, Sci 16.6%, Law 5.1% |
| Clipped pages | none |

Independent educational resource. Every case, option and rationale is original.
Nothing here reproduces secure NBEO content. Drug figures are exam anchors, not
prescriptions.
