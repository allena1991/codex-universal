---
name: save-as-pdf
description: Reformat an HTML design into a paginated, paper-ready PDF through a print-based copy on the paged-document or deck stage shell. Use when real pages are wanted rather than a one-page capture at the design's native pixel size.
---

# Save as PDF

Never rasterize the page. No jsPDF, no html2canvas, no dom-to-image, no canvas-to-PDF, and never generate a PDF binary yourself: those produce blurry, non-selectable, oversized output. PDF export is print-based - a print-ready copy goes to the browser's own print engine, which renders crisp selectable text. The only supported way to make a copy print-ready is a component that owns its print geometry: the paged-document starter for documents, or a source already built on the deck stage or paged-document shell. Do not hand-author `@page` rules or print resets.

## Steps

1. **Read the current design file** on every PDF request, even if you read it earlier in the conversation. Content and tweak values may have changed since.
2. **Write the print copy fresh** from what you just read. An existing `-print` copy is a stale snapshot; reusing or partially updating it ships outdated values. The path is the source path with `-print` inserted before the extension, in the same directory with the same basename: `slides/deck.html` becomes `slides/deck-print.html`. Never name it after the deck title or project, and never move it to the project root - any change in directory depth breaks every relative URL (font `src`, `<img src>`, `<link href>`, CSS `url()`), and the print tab then shows missing images and fallback fonts.
   - **Source already on the deck stage or paged-document shell**: the copy is the source plus content-level print rules only. Both components own their print geometry, so never add an `@page` rule or reflow their layout. For decks, set the active-slide attribute on every direct-child slide so entrance styles keyed to it resolve on every page; each slide is already one page. For paged documents there is nothing structural to do.
   - **Otherwise**: rebuild the content as a paged document on the paged-document starter. Pour the content in as normal flowing HTML inside `<doc-page size="letter" margin="0.75in">` (`a4` when non-US), keeping the design's typography, colors, and imagery intact. The component owns the sheet, pagination, and print geometry: no `@page` rule, no print reset, no page-card divs, no fake page breaks. Use `break-before: page` only where a section genuinely starts a chapter; long tables get a `<thead>`.
   - **Fixed-canvas design** (poster, social graphic, infographic): also a paged-document rebuild, with one decision - print at true dimensions (`<doc-page width="18in" height="24in" margin="0">`, the page is the design) or scale onto standard paper (`<doc-page size="letter" content-width="960px" content-height="1440px">`, content lays out at authored size and the component scales it to fit). When the intent is not clear from the request, ask in plain terms before exporting. Never hand-scale with your own transforms.
   - Every copy gets the color-adjust rule so backgrounds match the preview: `* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }`. Do not strip backgrounds.
   - Freeze animations at their end state. Never `animation: none`, which reverts fade-ins to the hidden base. Instead: `* { animation-delay: -99s !important; animation-duration: .001s !important; animation-iteration-count: 1 !important; animation-fill-mode: both !important; animation-play-state: running !important; transition-duration: 0s !important; }`.
3. **Test the copy** by loading it and confirming no JS errors. No screenshot needed unless asked.
4. **Open the export dialog** on the print-ready file. The print-firing code is injected for you; never write your own auto-print or `window.print()` script. Unless the export started from LO's own Export click, the dialog waits on him: his Continue click is what opens the print view. Report the state the tool result describes, not the state you expect - if it says the dialog is waiting, the print view has not opened, and saying otherwise is wrong.

## Notes

- Keep visual fidelity: typography, colors, and imagery intact.
- Deck slides stay one per page; paged documents flow and paginate themselves.
- The `-print` file is plumbing for the print tab, not a deliverable. The export dialog is the only delivery step; never offer the print copy as a download, since its relative asset paths only resolve through the project file server.
- When you already know the output will be printed, author on the print-owning starter from the start. Then export needs only the mechanical print copy, never a rebuild.
