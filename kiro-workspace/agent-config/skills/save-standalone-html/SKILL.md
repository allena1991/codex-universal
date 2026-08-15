---
name: save-standalone-html
description: Export a design as a single self-contained HTML file that works offline, by lifting code-referenced assets into declared dependencies, adding a splash thumbnail, and running the inliner. Use when a design must travel with no external files.
---

# Save as standalone HTML

The bundler inlines resources referenced directly in HTML attributes: `img` src and srcset, `source`, video and audio src, video poster, track src, SVG `image href` and `use href`, `link href` (stylesheets, favicons), script src, CSS `url()` and `@import`, and inline style attributes. It cannot discover a resource that only exists as a string inside JavaScript: an image src set in React, a background URL in a styled component, a dynamically imported script.

## Step 1: copy the file and find code-referenced assets

Copy the design's HTML file and read it. Look through all the code - inline scripts, imported JSX, styled components - for resource URLs referenced as strings rather than HTML attributes: image URLs in JSX or inline style objects, URLs in CSS-in-JS, scripts that import other scripts which themselves reference resources, `fetch` calls that load assets, media sources set programmatically.

If the design calls the model API, it will not work offline. When that is core to the project, stop and tell LO.

## Step 2: declare each one

For each resource found, add to `<head>`:

```html
<meta name="ext-resource-dependency" content="./hero.png" data-resource-id="heroImg" />
```

`content` is the URL relative to the HTML file (or absolute); `data-resource-id` is a short unique id. Then change the code to read `window.__resources.heroImg` instead of the hardcoded URL - at runtime that holds a blob URL for the inlined data. Do this for external scripts' resource references too: those scripts get inlined, but their references must be lifted. Be thorough; one missed resource is a broken image in the final file.

## Step 3: add the thumbnail (required - the bundler rejects the file without it)

A lightweight SVG splash shown while the file unpacks, and the permanent no-JS fallback:

```html
<template id="__bundler_thumbnail" data-bg-color="#0a5e3e">
  <svg viewBox="0 0 1200 800" xmlns="http://www.w3.org/2000/svg">
    <!-- simplified icon, glyph, or one or two letters, about 30% padding -->
  </svg>
</template>
```

Set `data-bg-color` to the page background, use a `viewBox` so it aspect-fits, keep it simple, and use the design's real colors so the transition feels seamless. It displays tiny; a simple glyph on a vibrant background is enough.

## Step 4: bundle, verify, deliver

Save the modified copy, then run the inliner to the friendly output name.

Read the tool result first: unresolved assets are listed there, and that is the authoritative miss list. Fix those references and re-run before opening anything. Then open the bundled output yourself to confirm it works and check the console for runtime errors. That check is for you, not the delivery.

Delivery is mandatory and is the download card pointing at the inlined output. A preview is not delivery: LO cannot save the file from it. Do not ask whether he wants it downloaded; present it.
