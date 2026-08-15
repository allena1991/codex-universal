---
name: interactive-prototype
description: Build a working prototype with real state, hover and press states, form validation, animated transitions, and multi-step navigation so it feels like a real app rather than a static mockup. Use for clickable flows, onboarding, app prototypes, and demos.
---

# Interactive prototype

The bar is that it feels like a working app, not a mockup.

- Real state management. Component state and effects drive what is on screen; nothing is faked with a static screenshot of a later step.
- Every interactive element has hover, active, focus, and disabled treatment. Mobile hit targets never below 44px.
- Forms validate: inline errors on blur, disabled submit until valid, a visible success state.
- Transitions are animated and short - entering panels, sheet and modal presentation, list insertion and removal, tab changes.
- Multi-step flows navigate for real: back preserves entered data, progress is visible, and the end state is reachable.
- Empty, loading, and error states exist for anything that would fetch. Loading is a skeleton or a spinner in place, never a blank screen.
- Content is plausible and specific. Realistic names, amounts, dates, and copy; no lorem ipsum, no "Item 1".

Ask a lot of questions before starting a prototype of someone's product: the flows in scope, what happens at each decision point, what the data looks like, which platform and frame, and what should be out of scope. Behavior that is unclear from the reference is worth one question, not a guess.

Device chrome comes from the frame starters (`ios_frame`, `android_frame`, `macos_window`, `browser_window`) rather than a hand-drawn bezel.

Keep it one Design Component with screens as sections and a state machine in the logic class. Split only when a component genuinely repeats across screens with real props and state.
