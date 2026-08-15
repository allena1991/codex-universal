# Kiro workspace

Three pieces of work that were built in the sandbox and are parked here so they survive it. None of it touches the codex-universal image build.

## agent-config/

The design-agent specification, implemented as Kiro configuration.

- `steering/design-agent.md` — operating guide, `inclusion: auto`, activates on design requests. Voice, deliverable rules, Design Component contract, options presentation, content standards, economy.
- `skills/<name>/SKILL.md` — 21 skills: `design-components`, `make-a-deck`, `make-a-doc`, `flier`, `html-email`, `animated-video`, `interactive-prototype`, `three-d-object`, `web-research`, `maps-and-geography`, `design-options`, `wireframe`, `hi-fi-design`, `frontend-design`, `make-tweakable`, `claude-api-prototypes`, `save-as-pdf`, `save-standalone-html`, `export-pptx`, `handoff-to-claude-code`, `create-design-system`.

To install, copy `steering/` and `skills/` into `.kiro/` at whichever scope you want. A matching `designer` agent definition could not be written in the sandbox: `fs_write` to `.kiro/agents/*` is denied by a session permission rule.

## design-runtime/

A working runtime for the `.dc.html` Design Component format, plus its assembler and tests. See `design-runtime/README.md`.

- `support.js` — compiles the markup inside `<x-dc>` to React elements: dotted holes, `sc-for`, `sc-if`, inline styles with pseudo-state compilation, `<helmet>` hoisting, `dc-import`, `x-import`, `data-props` defaults, `DCLogic`.
- `tools/dc_write.py` — assembles a `.dc.html` from template, logic class, and props, and rejects the documented anti-patterns.
- `tools/verify_runtime.mjs`, `tools/verify_imports.mjs` — 17 and 8 checks, all passing. Run under node, not bun.

Not implemented, deliberately: streaming paint, the host Tweaks overlay, the direct-edit override channel. Those are host concerns. The starter components (deck stage, doc page, image slot, tweaks panel, animation engine, device frames, 3D stage) are not built yet.

## nbeo-redesign/

A rebuilt replacement for a 120-page NBEO Part II PAM/TMOD study guide. 179 letter pages, 70 cases, 350 items, built from data rather than typed. See `nbeo-redesign/README.md` for the build commands and the two decisions that shape the whole thing.

- `AUDIT.md` — the findings that justified a rebuild rather than a redesign. The headline: the original answer key was 82% option A across 333 single-answer items, 95% in Session 2, with one unbroken run of 140 consecutive A answers. Then distractor quality, missing per-distractor rationales, unverifiable self-certification, and the layout defects.
- `content/` — the whole book as editable source: 70 cases in eight JSON batches, 27 authored reference sheets, one CSS file, and `AUTHORING.md`, the contract every case is written against.
- `tools/` — validation, answer-letter generation, layout, and four checks that all have to pass.
- `NBEO PAM-TMOD Clinical Reasoning Manual.pdf` — the printed manual. 179 pages, 8.5 x 11in, 1.76 MB, real text with embedded subsets.
- `preview/` — 18 representative pages as PNG.

**Answer letters are generated, not authored.** Item writers mark the correct option in place and never choose a letter. The generator deals an even multiset of A to E per session, rejects any run longer than three, and rotates each item's options so the correct one lands on its assigned letter. Result across both sessions: A 19.6%, B 19.6%, C 20.7%, D 20.4%, E 19.6%, longest run 3, and the best single-letter guess scores 21%. The audit printed on page 4 of the manual comes from the same build that produced the pages.

**Every page is a fixed box that clips.** `tools/shoot.mjs` measures all 179 in a real Chromium render and exits non-zero if one is over. `tools/calibrate.mjs` produced the point constants the Python cost model uses, so the model is fitted to measurements rather than guessed.

What the rebuild fixed, measured: correct option is strictly the longest in 13% of items against 20% by chance, 711 distractor rationale rows explaining why each trap is tempting and what rules it out, every item tagged by blueprint type with score-by-tag sheets for both sessions, item types landing inside every published band (Tx 44.3%, Dx 34.0%, Sci 16.6%, Law 5.1%), all 17 domains covered, self-certification replaced by a dated verification table with three states, and no filler pages.

Still unconfirmed and labelled as such in the manual: per-domain item ranges and item-type percentage bands, transcribed from the prior edition. The official Content Matrix PDF resolves but was not machine-read.
