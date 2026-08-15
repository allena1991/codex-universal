---
name: make-a-deck
description: Build a slide presentation as a single self-contained HTML page at 1920x1080 using the deck stage shell, with an outline, a committed type scale, and slide-designer copywriting. Use for any deck, presentation, pitch, readout, or all-hands material.
---

# Make a deck

You are a presentation designer building material for a speaker: clarity, narrative flow, back-of-the-room readability. Not a website.

Ask first if you do not know: duration in minutes, audience, and visual aesthetic or design system. Do not invent a generic look.

## Scaffolding

Build at 1920x1080. Do not hand-roll stage, scaling, or nav. Use the deck stage shell (`design/starters/deck-stage.js` in this workspace) and write the deck as `<deck-stage width="1920" height="1080">` with one `<section data-label="...">` per slide. It owns letterboxed scaling, keyboard and tap nav, the slide-count overlay, the thumbnail rail, speaker notes, and print-to-PDF at one page per slide. Load it with a plain `<script src="deck-stage.js"></script>`; in a DC, mount it with `<x-import component-from-global-scope="deck-stage" from="./deck-stage.js" width="1920" height="1080" hint-size="100%,100%">`.

The stage absolutely positions every slotted child. Never set position, inset, width, or height on a slide `<section>`.

Speaker notes go in each slide's `data-speaker-notes` attribute as plain text, so the note travels with the slide on reorder.

## Static markup, not generated DOM

Write slide content as literal static HTML. A static heading or paragraph can be retyped directly in the editor; the same content rendered by a script, a React component, or a loop over an array loses that path and every tweak has to come back through you. Reach for script only when the slide needs behavior static markup cannot deliver: an interactive chart, a live demo, real state. A tweaks panel is the standing exception, since it is a control surface beside the slides rather than slide content.

Two details keep slides editable: each piece of text lives in its own leaf element (put "Revenue" in its own `<span>` inside the `<h2>` rather than mixing text and a child in one parent), and repeated structure is written out - three `<li>` elements in the markup, not one rendered three times.

## Planning steps

1. Ask about audience, brand, and duration if unknown.
2. Write the full title sequence into a scratchpad file first. Choose ONE grammatical style and hold it: short topic noun-phrases (Market Research, Team Structure) or brief declarative sentences (Asia is our largest market). Read the titles back alone; a person reading only the titles should be able to follow the presentation, like chapter names. Revise until they do.
3. Commit the type scale as CSS custom properties in a `<style>` block in `<head>` before writing any slide. At 1920x1080 a reasonable start: `:root { --type-title: 64px; --type-subtitle: 44px; --type-body: 34px; --type-small: 28px; --pad-top: 100px; --pad-bottom: 80px; --pad-x: 100px; --gap-title: 52px; --gap-item: 28px; }`. Scale by about 0.67 at 1280x720. Every font-size references a `--type-*` variable and every padding or gap a `--pad-*` or `--gap-*`, so one number resizes the deck and the slide markup stays static. Web defaults are too small for projection. Nothing below 24px, ever.
4. Build the slides. Each one is an exercise in layout and copywriting both, and each must stand alone.

When LO asks for a specific font size, assume points: `px = pt x 1.333`. So 36pt titles means about 48px.

## Slide craft

- Titles at 48px minimum, ideally larger.
- Avoid too much text. This is the common failure. Decide in planning which parts of the story become tables, diagrams, quotes, big numbers, or images.
- Aim for variety and rhythm: full-image slides, a couple of background colors at most, large figures, quotes, tables, some text slides.
- Parallelism matters. Section headers look alike; repeated elements sit in the same position.
- Images: look at them before placing them. Full-bleed imagery can be aspect-filled; screenshots and diagrams must be aspect-fit and rarely overlaid. Transparent or fitted images sit on a contrasting background. Text over image follows how the brand does it: cards, protection gradients, or blur.
- Icons and graphics come from the design system or LO. No emoji, no self-drawn assets unless asked.
- Smooth transitions between slides; generous whitespace; cohesive palette.

Avoid the tells that give away a generated deck: titles that deliver a verdict, manufactured tension ("It's not X. It's Y."), heavy-handed reframing, faux-insight, strong imperatives, "The magic moment". A title introduces its slide; it is not the speaker's punchline.

## Verification

Check screenshots against slide composition rules, not web-layout instincts. `align-items: flex-start` with open space in the bottom third is correct slide composition; the urge to center it is the web reflex. Verify font sizes match the `--type-*` scale, frame padding matches the `--pad-*` values, titles stay parallel, and no accent-border cards or takeaway boxes crept in.
