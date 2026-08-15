---
name: wireframe
description: Explore the design space fast with rough low-fidelity wireframes and storyboards - three to five distinctly different approaches per idea, sketchy and structural rather than polished. Use before committing to a direction.
---

# Wireframe

Interview first, then map the space before committing to a direction.

- Breadth over polish. Three to five distinctly different approaches per idea, not five variations on one.
- Simple shapes, placeholder text, minimal color, so attention stays on structure and flow.
- Sketchy vibe: handwritten but readable fonts, mostly black and white with one accent, low-fidelity and simple.
- Show flow, not chrome. Where does the user land, what do they do next, what happens on failure.
- Label each approach with what makes it different in one line, so LO can react to the idea rather than the drawing.

Lay the wireframes out as the vertical option stack: one `<section>` per turn, newest at the top, stable `{turn}{letter}` ids on each option wrapper, `<meta name="design_doc_mode" content="canvas">` in `<helmet>` for pan and zoom, and a `.dv-next` line of follow-ups. The `design-options` skill carries the full markup recipe; use it verbatim.

A wireframe that has drifted into a polished mockup has failed at its job. Keep it rough until LO picks a direction, then move to `hi-fi-design`.
