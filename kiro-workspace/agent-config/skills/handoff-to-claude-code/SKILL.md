---
name: handoff-to-claude-code
description: Package a design as a developer handoff bundle - a self-sufficient README with layout, tokens, interactions, and state, plus the design files - so an engineer can implement it in a real codebase. Use when design work moves to implementation.
---

# Handoff to Claude Code

Create a handoff folder in the project named for the feature: `design_handoff_onboarding_flow`, `design_handoff_settings_redesign`.

## README.md

- **Overview**: what the design is for and what it accomplishes.
- **About the design files**: state clearly that the bundled files are design references created in HTML - prototypes showing intended look and behavior, not production code to copy. The task is to recreate them in the target codebase's existing environment (React, Vue, SwiftUI, native) using its established patterns and libraries, or, if no environment exists yet, to choose the appropriate framework and implement there.
- **Fidelity**: say which this is. High-fidelity means pixel-perfect mockups with final colors, type, spacing, and interactions, to be recreated pixel-perfectly using the codebase's own libraries. Low-fidelity means wireframes showing structure and flow, to be styled with the codebase's existing design system.
- **Screens**: for each one - name, purpose, layout in detail (grid structure, flex directions, widths, heights, margins, padding), and each component with position and size, exact colors, typography (family, size, weight, line-height, letter-spacing), radius, shadows, borders, hover/active/focus states, and the exact copy used.
- **Interactions and behavior**: click handlers and navigation, animations and transitions with duration and easing and the properties animated, hover states, loading states, error states, validation rules, responsive behavior.
- **State management**: which state variables are needed, the transitions and their triggers, any data fetching.
- **Design tokens**: colors with hex values, spacing scale, type scale, radii, shadows.
- **Assets**: every image, icon, and font used, and where it came from.
- **Files**: the design files in the bundle, so the developer can reference them.

Be extremely precise about measurements, colors, and typography; the developer relies on this. If the design uses an existing brand system, say to use that system in their codebase rather than the copied values.

## Bundle

Copy the design files into the handoff folder, then present the folder as a download so it arrives as a zip.

The README must be self-sufficient: a developer who was not in the conversation should be able to implement from it alone. After creating it, ask whether LO wants screenshots of the designs included; do not include them by default.
