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

A rebuilt replacement for a 120-page NBEO Part II PAM/TMOD study guide. 70 cases, 350 items, 711 distractor explanations, built from data rather than typed. See `nbeo-redesign/README.md` for the build.

**Two guides, both complete.** Each carries the whole reference apparatus, all 70 cases, all 350 items and all 140 teaching-key pages. Neither is an extract of the other. They differ in order, because learning and testing want opposite orders.

- `NBEO PAM-TMOD Part 1 - Study Manual (by domain).pdf` — 178 pages. Ordered by clinical domain, each case followed immediately by its own teaching key. Cornea sits with cornea, so competing conditions land within a few pages of each other.
- `NBEO PAM-TMOD Part 2 - Exam Simulator (as sat).pdf` — 181 pages. Ordered as sat, session by session, cases only, with every key at the back. A session can be answered cold and timed.
- `AUDIT.md` — the findings that justified a rebuild rather than a redesign. The original answer key was 82% option A across 333 single-answer items, 95% in Session 2, with one unbroken run of 140 consecutive A answers.
- `content/` — the whole book as editable source: 70 cases in eight JSON batches, 29 authored reference sheets, one CSS file, and `AUTHORING.md`, the contract every case is written against.
- `tools/` — validation, answer-letter generation, layout, and the checks that have to pass. `guides.py` declares what each of the two guides contains.
- `preview/` — representative pages from both guides as PNG.

**Answer letters are generated, not authored.** Item writers mark the correct option in place and never choose a letter. The generator deals an even multiset of A to E per session, rejects any run longer than three, and rotates each item's options so the correct one lands on its assigned letter. Across both sessions: A 19.3%, B 19.6%, C 21.1%, D 20.7%, E 19.3%, longest run 3, best single-letter guess 21%. Letters are assigned in one pass over both sessions, so the two guides always agree.

**Every page is a fixed box that clips.** `tools/shoot.mjs` measures every page of both guides in a real Chromium render and exits non-zero if one is over. `tools/calibrate.mjs` produced the point constants the Python cost model uses.

What the rebuild fixed, measured: correct option strictly the longest in 15% of items against 20% by chance, 711 distractor rationale rows explaining why each trap is tempting and what rules it out, every item tagged by blueprint type with score-by-tag sheets, item types inside every published band (Tx 44.3%, Dx 34.0%, Sci 16.6%, Law 5.1%), all 17 domains covered, self-certification replaced by a dated verification table, and no filler pages.

**Two defects that shipped once, and the checks added for them.** Ten Session 2 cases reached an exported PDF still carrying placeholder text from `tools/stub.py`, because an authoring batch returned empty and it was not noticed. `schema.validate` now rejects that text outright. The same file also introduced a paraphrased domain name, which split one domain into two groups in the index, so domains are now a closed list of seventeen and anything else fails the build with a suggested correction.

Still unconfirmed and labelled as such in both guides: per-domain item ranges and item-type percentage bands, transcribed from the prior edition. The official Content Matrix PDF resolves but was not machine-read. Format facts for both Part I ABS and Part II PAM/TMOD were checked against NBEO's published exam pages, including the requirement to use non-possessive eponyms, which the content now follows.
