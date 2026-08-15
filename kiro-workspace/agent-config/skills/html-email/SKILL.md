---
name: html-email
description: Design a send-ready HTML email as one self-contained file that survives Gmail, Outlook, and Apple Mail - table layout, fully inlined styles, bulletproof buttons, no JavaScript. Use for newsletters, announcements, transactional and marketing email.
---

# HTML email

One self-contained `.html` file. Email rendering is not browser rendering: Gmail, Outlook, and Apple Mail each strip or mangle different things. Where these rules conflict with normal web instincts, the rules win.

## Layout and styling

- Structure with nested `<table role="presentation" cellpadding="0" cellspacing="0" border="0">`. No flexbox, no grid, no floats, no positioning. One centered wrapper table, max-width 600px, single-column flow. Stacked rows beat side-by-side columns.
- Inline every style on the element it styles. A `<style>` block in `<head>` may carry only what cannot inline (media queries, dark-mode tweaks); several clients drop it entirely, so the email must read correctly from inline styles alone.
- No JavaScript anywhere. No external stylesheets. No web fonts: use email-safe stacks (Arial, Helvetica, Georgia, Verdana, Tahoma, Courier New) with generic fallbacks.
- Build the visual design from colored table cells, borders, spacer cells, and type, not images. There is nowhere to host project images from here, so a referenced project file will not exist for recipients. If imagery is essential, leave a clearly marked placeholder cell with alt text and tell LO to swap in a hosted https URL before sending.
- Buttons are bulletproof: a padded `<td>` with `bgcolor` and inline border-radius, the `<a>` filling it with `display:block` and inline color. Never an image, never a styled `<button>`.

## Client quirks

- Outlook runs the Word engine: give every table and cell explicit widths, set line-height with `mso-line-height-rule:exactly`, and wrap Outlook-only fixes in `<!--[if mso]> ... <![endif]-->`.
- Gmail clips messages past roughly 100KB of HTML. Stay well under.
- Add `<meta name="color-scheme" content="light dark">` and pick colors that survive dark-mode inversion: avoid pure #000 and #fff backgrounds, and test text on mid-tone fills.

## Deliverability and accessibility

- First element in `<body>`: a hidden preheader span of about 85 characters that previews next to the subject line.
- `alt` text on any image, `lang` on `<html>`, real `<a href>` links with no dead `#` anchors, and a footer with a plausible unsubscribe line and postal address for anything marketing-shaped.

Show the design at 600px, and say in your reply that the file is send-ready HTML LO can drop into an email tool.
