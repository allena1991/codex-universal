---
name: three-d-object
description: Model a 3D object with three.js in the viewer stage so it can be inspected from every angle and downloaded as OBJ+MTL or GLB. Use for product models, hardware mockups, and any downloadable 3D asset.
---

# 3D object

## Page shape

Build the page as plain HTML with ordinary `<script>` tags, even when every other design in the project is a Design Component. DC confines scripts to `<helmet>`, whose mount timing races the stage.

Use the 3D stage starter (`design/starters/three_d_stage.js`): it is the whole viewer - renderer, studio lighting, ground shadow, orbit controls, an auto-framed camera, and a toolbar that downloads the shown object as OBJ+MTL or GLB. Follow its usage block's page skeleton exactly. You write only the model-building module script.

Load three.js only through the pinned, hash-verified import map in `<head>`, before any module script, with exactly these entries: `three`, `three/addons/controls/OrbitControls.js`, `three/addons/exporters/OBJExporter.js`, `three/addons/exporters/GLTFExporter.js` at version 0.184.0 with their integrity hashes. The map is deliberately a closed set: do not change versions, URLs, or hashes, do not add another copy of three.js, and do not import other addons. Anything else fails to resolve rather than loading unverified.

## Modeling

Build a `THREE.Group` composed of named parts.

- Compose primitives (Box, Cylinder, Sphere, Torus, Lathe, Extrude with Shape) before reaching for raw BufferGeometry. Real objects decompose into far more primitives than you would guess.
- Name every mesh and every material ("hull", "walnut", "brass"). Those names become the `o` and `usemtl` entries in the OBJ and the node names in the GLB, which is what makes the download usable in Blender.
- `MeshStandardMaterial` with a small curated palette of three to five materials shared across parts. Set roughness and metalness deliberately. Textures do not survive the OBJ export, so prefer geometry and material color over texture detail.
- Model in real-world meters, y-up, centered on the origin, base resting at the lowest y. Offset deliberately coplanar faces by about 0.001 so nothing z-fights.
- Curved surfaces need enough segments to read as smooth at full screen (32 or more radial segments on feature surfaces), but do not tessellate what no one will see.

Await the stage's ready promise, then hand it the group.

## Iterating and export

The stage keeps its last frame readable, so ordinary screenshots capture the live canvas. After editing a module file, reload the page before screenshotting; the iframe caches already-loaded modules. Look at the object from the default framing and refine silhouette, proportion, and material separation - the silhouette carries the object.

The toolbar exports OBJ+MTL (universal geometry plus per-material colors) and GLB (keeps hierarchy and PBR materials; imports cleanly into Blender, Maya, Cinema 4D, Unity, Unreal). If LO asks for FBX, USDZ, or STEP, say plainly that those two are what the stage exports.
