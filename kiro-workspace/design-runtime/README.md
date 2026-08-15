# Design workspace

The executable half of the design-agent setup: a runtime that makes `.dc.html` Design Components real, plus the assembler and tests. The behavioural half lives in Kiro config: the `design-agent` steering guide and the skills under `.kiro/skills/`.

## Files

| Path | What it is |
| --- | --- |
| `support.js` | The runtime. Compiles the markup inside `<x-dc>` to React elements and mounts it. Never hand-edit a design against this file. |
| `tools/dc_write.py` | Assembles a `.dc.html` from the three authored pieces and rejects the documented anti-patterns. |
| `tools/verify_runtime.mjs` | Smoke test: holes, `sc-for`, `sc-if`, inline styles, pseudo-states, helmet hoisting, events, `setState`. |
| `tools/verify_imports.mjs` | Covers `dc-import` and `x-import` with a real child DC and a real web component. |
| `examples/` | The authored pieces behind `Roadmap.dc.html`, `Chip.dc.html`, and `Imports.dc.html`. |

## Authoring

Write three pieces and assemble them; never write the document wrapper by hand.

```bash
python3 tools/dc_write.py --out "Roadmap.dc.html" \
  --template examples/roadmap.template.html \
  --logic examples/roadmap.logic.js \
  --props examples/roadmap.props.json
```

The template is what belongs between `<x-dc>` and `</x-dc>`. The logic is `class Component extends DCLogic { ... }` with no `<script>` tag. The props file is the `data-props` JSON. `--out` must end in `.dc.html`, and the generated file loads `support.js` from its own directory, so keep them side by side.

The assembler fails the build on document scaffolding in the template, a `<script>` or `<style>` outside `<helmet>`, a stylesheet link, a self-closed import tag, a capitalized component tag, malformed props, and logic that uses `import`/`export` or omits `class Component`. It warns on holes that are not dotted paths and on missing `hint-*` attributes. `--force` writes anyway.

## What the runtime supports

- `{{ dotted.path }}` holes in text and attributes, with literals (`true`, numbers, quoted strings) and interpolation (`a {{ p }} b`). A whole-value hole passes the raw value, so handlers and refs work.
- `<sc-for list="{{ items }}" as="item" hint-placeholder-count="3">` with `$index` in scope, falling back to placeholder rows while the list is undefined.
- `<sc-if value="{{ flag }}" hint-placeholder-val="{{ true }}">`.
- Inline `style` compiled to a React style object, plus `style-hover`, `style-active`, `style-focus`, `style-before`, `style-after` compiled to generated classes and injected rules.
- `<helmet>` contents hoisted into `<head>`, de-duped by URL, with scripts re-created so they execute.
- `<dc-import name="Chip" ...>` fetching and mounting a sibling DC, and `<x-import component="X" from="./x.jsx">` / `component-from-global-scope="my-tag"` mounting a module export, a window global, or a custom element. Both show their `hint-size` placeholder until ready.
- `data-props` defaults seeded as initial props; `class` and `for` mapped to `className` and `htmlFor`; lowercased attribute names mapped back to React's camelCase (`onclick` to `onClick`, `viewbox` to `viewBox`).

Deliberately not implemented here: character-by-character streaming paint, the host Tweaks overlay, and the direct-edit override channel. Those belong to the host, not the runtime.

## Tests

Run with node, not bun: bun's `vm` lacks the context mode jsdom 30 needs.

```bash
NODE=$(ls -d /root/.nvm/versions/node/*/bin/node | tail -1)
"$NODE" tools/verify_runtime.mjs Roadmap.dc.html
"$NODE" tools/verify_imports.mjs
```

Dependencies (`jsdom`, `react@18`, `react-dom@18`) are already installed in `node_modules`. The tests rewrite the CDN React tags to those local copies and, for the import test, shim `window.fetch` onto the filesystem, since jsdom provides no fetch.
