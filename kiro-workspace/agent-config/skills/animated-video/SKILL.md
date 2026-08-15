---
name: animated-video
description: Build timeline-based motion design as an HTML page with scenes, easing, playback controls, and video export at a fixed aspect ratio. Use for animated videos, motion graphics, product walkthroughs, and any timed visual storytelling.
---

# Animated video

An animation rendered as an HTML page: a timeline, smooth transitions, playback controls, export-ready at a fixed aspect ratio (16:9 or 9:16).

## Engine

Build every standalone animation on the v2 animation starter (`design/starters/animations_v2.jsx` in this workspace) unless LO explicitly says not to. Never load the older `animations.jsx` alongside it; v2 contains the whole engine and the same globals, so loading both means last-wins. Read the starter after copying it; its usage block is the authoring contract.

It provides the timeline engine (`<Stage>`, `<Sprite start end>`, `useTime()`, `useSprite()`, an `Easing` library, `interpolate()` and `animate()` tweens, `TextSprite` / `ImageSprite` / `RectSprite` / `VideoSprite`) plus scene sequencing: `<SceneStage>` plays named scenes in authored order and keeps the exportable duration in sync.

## Scene contract

Always structure the piece as a scene sequence; a single-scene piece is a one-entry list.

- Declare the scene list as a JSON string literal in a plain inline `<script>` of the main document: `<script>window.OM_SCENES = '[{"name":"Opening","dur":3}]';</script>`, exact `JSON.stringify` formatting, no spaces. Not in a babel script, not in a sibling `.jsx`; only vanilla inline literals are addressable for write-back.
- Pass it through untouched as `<SceneStage scenes={window.OM_SCENES}>` and map scene names to components in the children object.
- Timing is user-editable. When a scene's length changes, the engine remaps the scene clock so the choreography plays faster or slower rather than getting cut off. That only works for motion driven by the scene clock, so inside a scene component always animate from `useScene()`'s `localTime` / `progress` - never your own clock, never `useTime` directly inside a scene.
- Scene entries can carry extra fields (`"text"`, palettes, any params); the component receives the whole entry, so user-facing knobs belong in that JSON.

Give every motion project a tweaks panel whose defaults include `"motionEditor": true` with a toggle bound to it; that key gates the host timeline editor's visibility and touches neither the animation nor the export. Declare the defaults literal in a plain inline `<script>` of the main document so the flip persists.

`<SceneStage>` already owns the exportable-video contract: the exportable attribute, the seek listener, the svg/foreignObject wrapper, and font inlining. Never add the exportable duration attribute yourself; a second one on a wrapper above the stage binds playback and export to the wrong root and both silently break.

Only for a page built without the starter, implement the contract by hand: exactly one root element carrying the exportable-duration attribute (never nested), which listens for the seek event and synchronously renders that exact timestamp with playback paused; nested `<video>` elements carry their play-start, play-end, and optional speed, loop within that window, and stay in sync from your clock.

## Craft

- Storytelling first. Before building anything, identify the arc, the tension, the characters, and the message. Run it past LO.
- Use the classic principles: anticipation, easing, follow-through, exaggeration.
- Scenes open with an establishing shot, then push in on the action. Show, do not tell; use titles or captions only when necessary. Most scenes live in a real context - a background, a computer, a phone. Elements should not float in the aether.
- Short pieces mostly use one shot per scene, or a few shots in one setting. Decide the shot: start wide and zoom, cut between two subjects in tension, follow a cursor or a line on a graph.
- Something is always moving unless you are deliberately holding a beat. A truly static frame reads as a bug. Images especially: slow zoom, pan, or build.
- Text and images need seconds to land before the next thing appears.
- Cursor or pointer movement gets a zoom and a damped viewport follow, like a screen recorder. Use refs to locate elements so the cursor points at the right thing.
- Build reusable components per visual element and per scene, then iterate on the timeline.

Update the video root's `data-screen-label` with the current timestamp each second so a comment on a moment maps to an exact time.

If a screenshot of the stage comes back black, that is a capture artifact of the svg/foreignObject wrapper. Trust the live preview.
