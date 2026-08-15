---
name: flier
description: Design a print-ready single-page flier or handout at exactly one fixed sheet, read at a distance in under three seconds. Use for fliers, posters-as-handouts, event notices, and tear-off sheets.
---

# Flier

One self-contained HTML file, exactly one fixed-size page.

## Sheet setup

Build inside `<doc-page size="letter" margin="0">` from `design/starters/doc-page.js` (`size="a4"` when metric). The component owns the page box, the desk background that disappears at print, and all print geometry. Write no `@page` rule and no body background.

- The flier is a single block of exactly 8.5in x 11in, or 210mm x 297mm for A4: the whole sheet, since `margin="0"` means content fills the page box.
- The print dialog must show exactly one page. Watch trailing margins and stray whitespace.
- `margin="0"` makes the sheet full-bleed, so the flier owns its own inset: keep a visual margin of at least 0.375in as the content block's padding, and keep everything inside it.
- Physical units only - in, pt, mm. No viewport units.

## Composition

A flier is read in passing, at a distance, in under three seconds.

- One dominant element, usually a headline under six words, sized to read across a room. Think 60pt and up. Everything else clearly subordinate.
- The five Ws grouped tight and scannable: what, when, where, cost, and one way to act (a QR-sized URL, a phone number, a tear-off). Not scattered through prose.
- Strong flat color blocks and vector shapes over photos and gradients. High contrast. Body text near-black on light stock.
- Generous whitespace beats more words. Cut copy until the hierarchy is unmissable.
- Optional tear-off fringe along the bottom edge when phone-number slips are wanted: a row of narrow cells with dashed left borders and rotated contact text.

Check the print preview: nothing clipped, nothing spilling to a second sheet, and the design still works in grayscale.
