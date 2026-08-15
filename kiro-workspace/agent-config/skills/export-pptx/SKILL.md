---
name: export-pptx
description: Export an HTML slide deck to PowerPoint, either as native editable text and shapes or as full-bleed screenshots, with the right navigation, scaling, and font strategy. Use when a deck must land in PowerPoint or Google Slides.
---

# Export as PPTX

Two modes. Editable emits native PowerPoint text, shapes, and images. Screenshots emit one full-bleed PNG per slide: pixel-perfect but not editable. One export call does everything - capture, font handling, generation, download.

## Steps

1. **Know the deck.** You probably wrote it; if not, read the HTML to find the slide selector, how navigation works, which fonts it uses, and whether there is a scaling wrapper.
2. **Show the deck to LO** so it is the file in his preview. The export reads what is showing.
3. **Call the export** with slide size in CSS px matching the deck, one entry per slide in order (each with its selector and the navigation expression), selectors to hide (nav arrows, progress bars, chrome), and a `resetTransformSelector` naming any `transform: scale()` wrapper - the exporter clears the transform and forces the element to the declared width and height.
4. **Read the validation flags** and decide whether each is expected for this deck.

Navigation expressions run inside the iframe as synchronous expressions; never `await`. If the deck's nav function is async, call it without awaiting and let the per-slide delay (default 600ms) cover the transition. Bump the delay for longer CSS transitions.

Speaker notes are read automatically from the deck's notes JSON block and attached by index; you do not pass them.

## Decks on the deck stage shell

- `resetTransformSelector` is `deck-stage`: the exporter sets its no-scale attribute, which the component observes by dropping its shadow-DOM scale. There is no other way to reach the scaled canvas.
- Navigation per slide is the stage's `goTo(n)`, zero-indexed, so slide one is `goTo(0)`.
- Slide selector is the stage's active-slide child selector.
- Hide selectors are unnecessary: the overlay and tap zones live in shadow DOM and are not captured.

## Validation flags

Warnings, not errors. Read each message and judge it against this deck.

- Duplicate adjacent or majority slides almost always means navigation did not fire. Check the function name, lengthen the delay, check zero- versus one-indexing.
- A slide-size mismatch means the selector is matching a wrapper, or a reset-transform selector is missing.
- Uniform non-empty notes usually means a placeholder. Fine if intentional.
- A notes count mismatch means notes attach by index and the tail will be wrong.
- No speaker notes is expected for a deck without notes.
- A fonts timeout means font URLs may be unreachable.
- A failed font swap means the target never loaded, so the deck was laid out with a fallback while the file names the swap font. Retry with a corrected family or fall back to web-safe, and tell LO plainly which fonts could not be applied and that text may wrap differently.
- Failed images usually means a 404 or CORS.
- A reset-selector miss means your selector matched nothing.

When talking to LO about flags, never relay the internal names. If everything is expected, do not mention validation at all - just confirm the download. If something is genuinely wrong, describe it plainly: "a couple of slides may have captured identically, let me fix navigation and retry."

## Font strategy

- Brand fonts as-is: pass no font options.
- Web-safe substitutes: swap each custom font to Arial, or Georgia for serifs, Courier New for monospace.
- Google Font substitutes: import the families and swap each custom font to one of them.

Substitution happens before capture so layout reflows correctly. Leave system fonts alone.

Google Slides: only when LO asked for it, enable the Google Slides option, which adds a send button to the export dialog; the upload happens only if he clicks it.

The page reloads after capture, so DOM mutations (hidden chrome, font swaps) revert on their own.
