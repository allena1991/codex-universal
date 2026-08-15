---
name: design-options
description: Present several design explorations as a vertical stack of turns with stable referenceable ids, newest turn on top, on a pannable canvas. Use whenever showing more than one option, variation, or direction side by side.
---

# Design options

Options are grouped by turn. Each turn is its own `<section>`, newest at the top, and every option carries a stable `{turn}{letter}` id that LO references back in chat and you cross-link between turns.

Always include `<meta name="design_doc_mode" content="canvas">` in `<helmet>`; the host provides pan and zoom, so options can be wider than the viewport. Never hand-roll your own pan and zoom.

## Markup

One `<style>` block in `<helmet>`, then one `<section class="dv-turn">` per turn as a direct child of the root, immediately after `</helmet>`, with no wrapper.

```html
<helmet data-dc-atomics><meta name="design_doc_mode" content="canvas"><style>body{margin:0;background:#f0eee9;font-family:system-ui,sans-serif}.dv-turn{padding:40px 44px 32px;border-bottom:1px solid rgba(0,0,0,.08);scroll-margin-top:16px}.dv-thd{display:flex;align-items:baseline;gap:10px;margin:0 0 20px}.dv-tid{font:600 10px ui-monospace,Menlo,monospace;padding:3px 7px;background:#1a1a1a;color:#fff;border-radius:4px;text-decoration:none}.dv-tname{font:600 13px/1.2 system-ui,sans-serif;color:#1a1a1a}.dv-opts{display:flex;flex-wrap:wrap;gap:28px;align-items:flex-start}.dv-opt{flex:none;display:flex;flex-direction:column;gap:9px;scroll-margin-top:16px}.dv-oid{font:600 10.5px ui-monospace,Menlo,monospace;padding:3px 7px;background:rgba(0,0,0,.08);color:#1a1a1a;border-radius:5px;text-decoration:none}.dv-olabel{display:flex;align-items:baseline;gap:8px;font:400 11px/1.3 system-ui,sans-serif;color:rgba(0,0,0,.55)}.dv-card{max-width:100%;background:#fff;border:1px solid rgba(0,0,0,.08);border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,.06);overflow:hidden}.dv-opt:target .dv-oid{background:#2a78d6;color:#fff}.dv-next{margin:22px 0 0;font:12px/1.5 system-ui,sans-serif;color:rgba(0,0,0,.5)}</style></helmet>
<section class="dv-turn" id="t2">
<div class="dv-thd"><a class="dv-tid" href="#t2">2</a><span class="dv-tname">Riffs on <a class="dv-oid" href="#1b">1b</a></span></div>
<div class="dv-opts">
<div class="dv-opt" id="2a"><div class="dv-olabel"><a class="dv-oid" href="#2a">2a</a>Tighter spacing</div><div class="dv-card" style="width:360px">...design...</div></div>
<div class="dv-opt" id="2b">...</div>
</div>
<p class="dv-next">Try next: "more like <a class="dv-oid" href="#2a">2a</a> but with the serif from <a class="dv-oid" href="#1c">1c</a>" - "make <a class="dv-oid" href="#2b">2b</a> full-bleed" - "new directions"</p>
</section>
<section class="dv-turn" id="t1">...turn 1, unchanged...</section>
```

## Rules

- Turn section ids are `t1`, `t2`, `t3`. Option ids are `1a`, `1b`, `2a`, and go on the option's outermost element (`.dv-opt`), never on the badge, so `#1b` scrolls the whole option into view.
- Ids are stable forever. Never reused, renumbered, or reordered.
- When LO asks for more, insert the new section above the existing ones and leave earlier turns untouched.
- Options within a turn sit side by side in a wrapping row. Size each card to its content; explicit widths are fine; never `height:100%`.
- Every id reference in the file is an `<a class="dv-oid" href="#1b">1b</a>` link, never a bare id. In chat, write the bare id.
- End each turn with a one-line `.dv-next` of two or three plain-English follow-ups LO could paste into chat.

Choosing between this and one full-size prototype with tweaks: a single responsive prototype suits prototype-shaped asks with few variants; the option stack suits design-shaped asks, many options, or small artifacts. Judge by how design-y the ask is, how many options there are, and how big each one is.
