---
name: make-a-doc
description: Build a page-style document that is printable out of the box - resume, memo, report, letter, guide, paper - using the paged-document shell, or a fixed-size sheet for posters and infographics. Use for any document, write-up, or printable page-shaped deliverable.
---

# Make a doc

Decide which of two shapes the request is; they export completely differently.

## Flowing pages

Text that pours onto standard sheets and breaks wherever needed: reports, memos, letters, papers, guides. Write the whole document as normal flowing HTML inside `<doc-page size="letter" margin="0.75in">` (`size="a4"` when metric), from `design/starters/doc-page.js`. The component owns the sheet, the desk background that disappears at print, and all print geometry. Do not write your own `@page` rule, body background, page-card divs, fake `break-after: page` sheets, or `break-inside: avoid` on items inside a multi-column grid (a grid breaks only between rows, so a kept row that does not fit leaves a blank band).

Print rules:

- Multi-column text uses CSS columns (`column-count` plus `column-gap`, `column-span: all` on a spanning heading, `hyphens: auto` in narrow columns with `lang` on the html element). Side-by-side flex or grid columns do not flow across pages.
- `break-before: page` only where a section genuinely starts a new chapter.
- Add your own kept-together blocks (callouts, stat tiles, cards) to a `break-inside: avoid` rule and keep each shorter than a page. The component already keeps headings with their content, keeps figures, code, and table rows whole, and suppresses orphans and widows.
- Long tables get a `<thead>` so the header repeats on every page.
- No `position: fixed` or `sticky` and no viewport units in content. Fixed elements stamp every printed page; running headers and footers go in the component's `slot="header"` / `slot="footer"`.

Leave the running header and footer out by default; the body's own h1 already names the document. Add one only when asked or when the document type demands it (a long formal report, a brief needing a classification mark). Then: small muted type, no rule, title left, short context line right, footer different from the header, and never a "Page" label - page counters do not render there.

Do not add printed page numbers by default. CSS can only render them through `@page` margin boxes, which need a nonzero `@page` margin, which reopens the slot the browser's own date and URL header prints into. Only when explicitly asked, switch that document to `@page { size: letter; margin: 0.6in; @bottom-right { content: counter(page) " of " counter(pages); font: 10px sans-serif; color: #999; } }`, move the content padding to 0, and tell LO to untick "Headers and footers" in the print dialog.

## Fixed sheet

A design that must fill exactly one page at fixed dimensions: poster, infographic, social graphic, certificate. No starter component. Build it at its true pixel size with an explicit px `width` (and `height` if fixed) on the top-level element; export sizes the PDF page to it. Write no `@page` rule.

## Structure and type

The first element in the body is the document's own h1, never a masthead or eyebrow line. If pasted content starts with a header-shaped line, use it as the h1 rather than rendering a separate masthead.

Body type 14-16px with line-height 1.55-1.7. Clear heading hierarchy, restrained palette. Headings take `text-wrap: balance`, body and list items `text-wrap: pretty`. Tables get a header row and hairline borders. Figures and code blocks each carry a short caption. Links resolve to body ink at print. Mark on-screen-only chrome (download buttons, toolbars) so it is hidden in print.
