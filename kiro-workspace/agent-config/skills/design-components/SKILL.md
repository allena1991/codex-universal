---
name: design-components
description: Authoring contract for Design Components (.dc.html) - template syntax, holes, control flow, child and external imports, helmet, inline styling, the DCLogic logic class, and props metadata. Use whenever writing or editing a .dc.html file.
---

# Design Components

A Design Component is a single `Name.dc.html` file that opens directly in a browser and can be imported by other DCs. It paints from the first streamed character. Do not write `<script type="text/babel">` pages, `.jsx` entrypoints, or plain `.html` designs; the entrypoint IS the DC. The only exception is an experience that is entirely canvas/WebGL, or a map or 3D page, with no DOM layout to stream.

## The three authored pieces

The file wrapper (doctype, head, runtime include, `<x-dc>` tags) is assembled for you. You author:

1. **Template** - the markup between `<x-dc>` and `</x-dc>`. Never include the `<x-dc>` tags, document scaffolding, or a `<script>` block.
2. **Logic class** - `class Component extends DCLogic { ... }` source, no `<script>` tag. Empty string for template-only designs.
3. **Props metadata** - the `data-props` JSON on the `<script data-dc-script>` tag, never on `<x-dc>`.

In this workspace the assembler is `design/tools/dc_write.py` and the runtime is `design/support.js`. Never hand-write the runtime.

## Props metadata

```json
{
  "$preview": {"width": 420, "height": 560},
  "accent": {"editor": "color", "default": "#1f4e46", "tsType": "string"},
  "columns": {"editor": "int", "default": 3, "min": 1, "max": 6, "tsType": "number"},
  "onSelect": {"editor": null, "tsType": "(id: string) => void"}
}
```

- `$preview` sets the preferred preview size for sized fragments (cards, modals). Omit it for full pages.
- One entry per prop the component actually reads. Never invent props.
- `editor`: `text`, `color`, `int`, `float`, `range`, `boolean`, `enum`, or `null` for callbacks, ReactNode, and objects. `enum` needs `options`. Numbers and ranges take `min`, `max`, `step`, `unit`. `section` groups props under a heading. A color editor given a 3-4 item list of hex strings, or 2-5 hex palette arrays, renders curated swatches.
- `default` seeds the editor, not the runtime. Always fall back in `renderVals()` with `this.props.x ?? ...`.

Editable entries also surface as a Tweaks panel for standalone pages. Copy text and single colors are already directly editable, so do not spend tweaks on those. Reserve them for what in-place editing cannot do: functional behavior, alternative UI treatments, one flag that changes copy or color across many elements. Add two or three even when the DC is not meant for embedding.

## Template syntax

Holes are dotted lookups only: `{{ user.name }}`, `{{ $index }}`, literals like `{{ true }}`. Never expressions - `{{ a + b }}`, `{{ !x }}`, `{{ fn() }}` all fail silently. Compute in `renderVals()` and expose the result by name. An unresolved hole renders nothing and warns in the console.

Attributes: `x="literal"` is a string; `x="{{ path }}"` passes the raw value (number, function, ref); `x="a {{ p }} b"` interpolates a string. Event handlers and refs are whole-value attributes with JSX camelCase (`onClick="{{ handler }}"`). `class` and `for` map to `className` and `htmlFor`.

Control flow always carries its `hint-*` attributes; they are what renders while values are still undefined during streaming.

```html
<sc-for list="{{ items }}" as="item" hint-placeholder-count="3">
  <div style="padding:12px">{{ item.name }}</div>
</sc-for>
<sc-if value="{{ hasItems }}" hint-placeholder-val="{{ true }}">...</sc-if>
```

`$index` is in scope inside `sc-for`.

## Styling: inline only

No stylesheets, no CSS classes, no base styles, no design-token setup - decks and slides included, where you repeat the literals on every slide. Class-based CSS delays everything until both rules and markup have streamed; inline styles paint immediately.

`style="..."` compiles to a React style object. Pseudo-states use `style-hover`, `style-active`, `style-focus`, `style-before`, `style-after`.

The only legal `<helmet><style>` content is what cannot be inline: `@font-face`, `@keyframes`, body resets. Put `<helmet>...</helmet>` at the **top** of the template, holding those rules and any font `<link>`s. Its scripts and links mount when `</helmet>` closes; for post-render JS use `componentDidMount`. `<script>` tags are legal only inside `<helmet>` - a `<script src>` lower in the template does not run until the stream reaches it.

A `<style id="__om-edit-overrides">` block holds direct-edit `!important` overrides. When restyling an element it targets, edit or remove that rule; an inline change alone will not win.

Animations are not driven from the template. Build animated elements as `React.createElement(...)` in `renderVals()` and expose them by name so animation state survives re-renders.

## Child DCs and external components

Use sparingly. One DC by default; a 400-line `<x-dc>` body is normal and `<sc-for>` handles repetition. Split only when LO asked for reusable components, or an element repeats four or more times across screens AND has real props or state.

```html
<dc-import name="Card" item="{{ it }}" hint-size="100%,120px"></dc-import>
<x-import component="Chart" from="./Chart.jsx" data="{{ rows }}" hint-size="100%,320px"></x-import>
```

- `name` is the sibling file's basename. Never a capitalized tag like `<Card />`.
- Other attributes become props (kebab to camel). Always set `hint-size` (placeholder and min-size while streaming). `style` position and size props apply to the mount.
- Props are readable in the child's template by name with no logic class; the child's `renderVals()` keys override props.
- `x-import` mounts a component from a sibling file (`module.exports = {Chart}` or `window.Chart`). For a script with no exports that registers itself globally, use `component-from-global-scope` and pass the tag name for a `customElements.define` web component, or the global name (dotted paths allowed) for a `window.Foo` React component. Never assign a custom-element class to `window`.
- `from` must be a literal URL; the fetch starts at parse time, so a hole there never loads. The name attributes do accept holes and re-resolve per render. `from` is optional when the global is already loaded.
- Template children pass through as `props.children`. `dc-props="{{ obj }}"` spreads extra props. Importing the same file N times evaluates it once.
- Always write the explicit close tag. Never self-close `<x-import>` or `<dc-import>`.
- Only for pre-existing or copied components. Never write new UI as `.jsx`; it does not stream.

Design-system components: load the bundle in each DC's `<helmet>` (de-duped by URL), then mount with `<x-import component-from-global-scope="Namespace.Component" hint-size="...">children</x-import>`. No logic class needed.

## Logic class

```js
class Component extends DCLogic {
  state = { n: 0 };
  renderVals() {
    return { n: this.state.n, inc: () => this.setState(s => ({ n: s.n + 1 })) };
  }
}
```

Plain classic JavaScript. No TypeScript, no import/export. `DCLogic` and `React` are injected. The class must be named `Component`. You get `this.props`, `this.state`, `setState`, `forceUpdate`, and the React class lifecycle minus `render()`. `renderVals()` returns the template's inputs: flat values, arrays, handlers, refs.

Anything you would write as a JSX expression - ternary, `.map`, comparison - belongs here, exposed by name. `React.createElement(...)` in a return value is a last resort for a narrow piece the template genuinely cannot express, such as an animated element whose state must survive re-render. Never for UI layout: anything rendered that way is opaque to the editor, so "I cannot edit X" usually means X is a `createElement` subtree.

Shared business logic (formatters, default data, validators) may live in a plain `.js` ES module referenced via `<x-import>` or dynamic `import()`. No npm imports, no cycles, and never a design-tokens file.

## Anti-patterns

- Document scaffolding inside an authored piece (`<!DOCTYPE>`, `<html>`, `<x-dc>`, `<script>` in the template or a replacement string) - nests two documents.
- Class-based stylesheets, or a `<script src>` in the template body.
- JS in holes.
- Static styles or static text via holes: `style="{{ cardStyle }}"` or fixed copy from `renderVals()` cannot resolve mid-stream, so the design cannot paint until the call completes. A style hole is legitimate only for a live runtime value that cannot exist at parse time (a live percentage, user-typed text) - never for theme or prop-driven tokens.
- UI layout via `React.createElement` exposed through a hole.
- Capitalized component tags.
- Premature componentization; missing `hint-size`; writing `.dc.html` content with a plain file write instead of the assembler.

## Labels and anchors

- Put `[data-screen-label]` on slide- and screen-level elements so review comments can be traced to the right screen. "Slide 5" means the fifth slide (label `05`), never index 4.
- `data-comment-anchor="..."` pins a review comment to its element. Keep it on the semantic equivalent through edits and restructures; drop it only when deleting the element. Never invent values or duplicate one onto another element.
