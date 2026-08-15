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

Redesign of a 120-page NBEO Part II PAM/TMOD study guide.

- `AUDIT.md` — the findings. The headline: the original answer key was 82% option A across 333 single-answer items, 95% in Session 2, with one unbroken run of 140 consecutive A answers. Also distractor quality, missing distractor rationales, unverifiable self-certification, and layout defects.
- `tools/key_audit.py` — reproduces those numbers from the transcribed keys, and states the rebuild target.
- `index.html` — a print-ready 16-sheet specimen at 8.5 x 11in: cover with contents, verification status, method, blueprint chart, item types and pacing, a two-page keyed emergency gate, condition cards, pharmacology, formulas and drills, a rebuilt case with item-type tags, a two-page teaching key with per-distractor analysis, a cut-line recall deck, and sources with link status.
- `preview/sheet-01.png` … `sheet-16.png` — rendered pages.
- `tools/shoot.mjs` — renders each sheet and fails if any sheet clips its page. All 16 fit.

The specimen is a pattern, not the whole guide. Rolling it across 120 pages is mechanical once the key rebuild and distractor rewrite are agreed.
