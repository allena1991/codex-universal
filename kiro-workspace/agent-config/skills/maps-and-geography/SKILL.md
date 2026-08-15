---
name: maps-and-geography
description: Render accurate maps from real geographic data - d3-geo with pinned TopoJSON for static and exported graphics, Leaflet with OpenStreetMap tiles for pannable street-level maps. Use for any map, or whenever geography would make a good graphic.
---

# Maps and geography

Maps are a data problem, not a drawing problem. Never freehand country outlines, coastlines, or street layouts; hand-drawn geography is reliably wrong and people notice. Load real geometry and render it.

## Page shape

Build every map page as plain HTML with ordinary `<script>` tags, never a Design Component, even when every other design in the project is one. DC confines scripts to `<helmet>`, whose mount timing races the map container.

## Static and exported maps: d3-geo

For decks, docs, graphics, and animations - anything static or exported - render TopoJSON with d3-geo:

- Fetch `https://cdn.jsdelivr.net/npm/world-atlas@2.0.2/countries-110m.json` (Natural Earth, public domain). The URL is version-pinned; use it exactly.
- Convert with `topojson.feature(topology, topology.objects.countries)`.
- Draw with `d3.geoPath()` under a projection chosen for the job: `d3.geoNaturalEarth1` for the whole world, `d3.geoMercator().fitSize(...)` to zoom a region.

Load the libraries only through the pinned, hash-verified tags in `<head>`: `d3@7.9.0/dist/d3.min.js` and `topojson-client@3.1.0/dist/topojson-client.min.js`, each with its integrity attribute and `crossorigin="anonymous"`. They fail closed if tampered with, so do not change versions, URLs, or hashes, and add nothing else from a CDN. d3-geo ships inside the d3 bundle.

Inline SVG from d3 exports cleanly to PNG and PDF; live tiles do not. Exported deliverables always get d3 geometry, never an embedded tile map.

## Street-level interactive maps: Leaflet

For prototypes and sites where the map is panned and zoomed, use Leaflet with OpenStreetMap tiles, loaded only through the pinned, hash-verified `leaflet@1.9.4` stylesheet and script. The stylesheet is required; without it the tiles render scrambled.

Create the map with `L.map(...)` and `L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '(c) OpenStreetMap contributors' })`. That attribution string is OpenStreetMap's license requirement. Never omit it.
