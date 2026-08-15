---
name: make-tweakable
description: Expose a design's high-impact knobs as tweaks - props on the root Design Component, or a small tweaks panel for non-DC pages. Use when asked to make colors, variants, toggles, or copy adjustable without code edits.
---

# Make tweakable

If LO says what should be tweakable, do exactly that. Otherwise pick a few high-impact values: a key color, a layout variant, a feature flag, headline copy.

## In a Design Component

Tweaks are props on the root DC. Declare each in the `data-props` JSON and read it as `this.props.x ?? default` in `renderVals()`. Every prop with a non-null `editor` gets a host Tweaks overlay, so never hand-roll a control panel for these.

Copy text and single colors are already editable in place, so do not spend a tweak on them. Reserve tweaks for what in-place editing cannot do:

- functional behavior (a mode, a sort order, a validation strictness)
- alternative UI treatments (compact versus roomy, card versus row)
- one flag that changes copy or color across many elements at once
- anything else that is a code change rather than a text edit

Two or three well-chosen tweaks beat ten. Use the right editor type: `enum` with `options` for variants, `boolean` for flags, `range` with `min`/`max`/`step`/`unit` for sizing, `color` with three or four curated swatches or whole palettes rather than a free picker. Group related props with `section`.

## On a non-DC page

Use the tweaks panel starter: it wires the host protocol, handles state and persistence, and ships ready-made section, slider, toggle, radio, select, text, number, color, and button controls. Radio for two or three short options. Declare the defaults literal in a plain inline `<script>` in the main document so values persist. Keep the panel small and tasteful, and hide it completely when tweaks are off.
