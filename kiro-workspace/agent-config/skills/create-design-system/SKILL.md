---
name: create-design-system
description: Build a design system or UI kit project - tokens, fonts, assets, guidelines, reusable components, product UI kits, specimen cards, and a skill manifest - from a real codebase, Figma file, or brand materials. Use when asked to create a design system or UI kit.
---

# Create a design system

A design system is a folder containing typography and color foundations, brand voice and style guides, CSS, real visual assets, reusable components, and full-screen UI kits. It lets design agents work against a company's real product and brand.

## Fixed locations

Everything is discovered from file content and sibling relationships, not folder names. The one fixed location is `styles.css` at the project root (or `index.css`, `globals.css`, `global.css`, `main.css`, `theme.css`, `tokens.css` - first match wins). It is the global CSS entry point and must contain `@import` lines only. Everything it transitively imports ships to consumers; `@font-face` rules anywhere in that closure declare the webfonts.

A sensible default layout, unless the source has its own convention: `tokens/` (one file per concern, each imported from `styles.css`), `components/<group>/`, `ui_kits/<product>/`, `guidelines/`, `assets/`, and a root `readme.md`.

What gets indexed: a **component** is any `<Name>.jsx` or `.tsx` with PascalCase stem and a sibling `<Name>.d.ts` in the same directory; a **token** is any `--*` custom property under `:root` or a single-selector theme scope in a file reachable from `styles.css`; a **font** is any `@font-face` in that closure.

## Work order

1. Explore every provided asset - codebase, Figma, files, decks - and understand the company, the products, and the surfaces. Find product copy; examine core screens; find any existing design system definition.
2. Write root `readme.md` with that high-level understanding, and record the sources: full Figma links, repos, codebase paths. Do not assume the reader has access.
3. Set the project title from the brand or product name.
4. If decks were attached, extract key assets and text to disk.
5. Write the token CSS files: base values and semantic aliases both. Copy webfonts in and write the `@font-face` rules. Then write `styles.css` as import lines only, reaching every token and font file.
6. Add a CONTENT FUNDAMENTALS section to the readme: how copy is written, tone, casing, I versus you, emoji or not, the vibe, with specific examples.
7. Add a VISUAL FOUNDATIONS section answering all of it: colors, type, spacing, backgrounds (images, full-bleed, illustration, pattern, texture, gradient), animation easing and style, hover and press treatments, borders, shadow systems, protection gradients versus capsules, layout rules, transparency and blur, imagery color temperature and grain, corner radii, what a card looks like.
8. If font files are missing, substitute the nearest Google Fonts match, flag the substitution, and ask for the real files.
9. Build foundation specimen cards as small HTML files, about 700x150px each and 400px max height. Err toward more small cards: separate cards for primary versus neutral versus semantic colors, display versus body versus mono type, spacing tokens versus spacing in use. A typical set is 12 to 20 or more. No titles or framing - the card name renders outside the card. Each card links `styles.css` by relative path so it picks up the real tokens, and carries the card marker comment as its first line with group, viewport, subtitle, and name. Keep groups title-cased and consistent: Type, Colors, Spacing, Brand.
10. Copy logos, icons, and visual assets into `assets/`. If the sources contain no logo, do not create one: set the brand name in plain type where a mark would go and note the absence in the readme. Never draw, reconstruct, or approximate a real logo from memory, and never rebrand the system with an identity LO did not provide. Add an ICONOGRAPHY section: which icon system, built-in icon font, SVG or PNG, emoji or unicode usage. Copy the real icons programmatically; never hand-draw them.
11. Icons in order of preference: copy the codebase's own icon font, sprite, or SVGs; else link a CDN set if the source uses one; else substitute the closest CDN match at the same stroke weight and fill style and flag the substitution.
12. Author the reusable components. Each is one file with a named PascalCase export, self-contained, React only, styled through the CSS custom properties - no CSS-in-JS libraries, no npm packages; siblings may import each other by relative path. Add a sibling `.d.ts` with the props interface (that file is what gives a component its props contract and starting-point eligibility) and a `.prompt.md` with a one-sentence what-and-when, a small usage example, and notable variants. One card HTML per directory, marked as the Components group, linking `styles.css` and loading the generated bundle, mounting from the bundle namespace rather than script-tagging the source. Show key states and variants densely, not a single default render. Never write the generated bundle, manifest, adherence config, or a barrel index.
13. The source defines the component inventory. A mounted Figma file, a Figma link, or a component library in the codebase IS the list: build exactly those families. Do not add primitives a design system "usually" has; a component with no counterpart in the source is an invention consumers will trust and designers will not recognize. Genuinely needed additions go in the readme under "Intentional additions" with a one-line reason. Only when no source defines components should you author a standard set. Enumerate the full inventory first, put every family on the todo list, and build all of them. Never stop at a core subset; if you cannot finish, end by naming exactly which families remain and ask whether to continue.
14. For each product, build a UI kit in its own directory: README, `index.html`, and screen components. Three to five core screens per product with click-through interactivity, iterated visually once or twice against the source. UI kits are high-fidelity recreations of full interfaces, composing the primitives you authored rather than reimplementing them; the `index.html` looks like a typical view of the product and demonstrates an interactive version. Get the visuals exactly right from code or design context. Do not invent new designs; copy the existing one, and omit or leave deliberately blank with a disclaimer what you cannot see. Within a screen you may abbreviate repeated content, but never skip a component family.
15. If a slide template was provided, build sample slides as one HTML file per slide type in their own directory, marked with the Slides group at 1280x720, copying the provided decks' style and using the real assets. If no sample slides were given, do not create them.
16. Mark each UI kit's `index.html` with its product group and a viewport whose height caps the portion worth previewing.
17. Add an index section to the readme: a manifest of the root folder plus the list of components and UI kits.
18. Write `SKILL.md` at the root so the system works as a downloadable skill: front matter with `name: {brand}-design` and a description covering branded interfaces and assets for the brand; body pointing at the readme and the other files, saying to copy assets out and produce static HTML for visual artifacts or read the rules for production work, and to ask what LO wants to build if invoked bare.

Mark starting points separately from cards: a component opts in via a JSDoc marker on its props interface in the `.d.ts` (section, subtitle, viewport), and its thumbnail is that directory's card HTML; a screen opts in via a first-line HTML comment marker, and the screen itself is the thumbnail. Retitling or removing one is an edit to that marker.

## Guidance

- Run independently. Stop only on a crucial blocker.
- Copy icon assets in rather than approximating iconography with hand-rolled SVG or emoji.
- Never recreate UI from screenshots alone when code or design context exists. Screenshots are a lossy high-level guide.
- The attached kit is ground truth. Where it differs from the published conventions of a library it resembles, the kit wins. Copy exact numeric values - paddings, radii, sizes, line-heights - and never round them to a 4 or 8px grid or a framework default. If the kit says 5px, write 5px.
- Avoid bluish-purple gradients, emoji cards, and colored-left-border cards unless you actually see them in the source.
- Do not read SVGs for their own sake; copy them and reference them.
- If an attached codebase or Figma link is inaccessible, stop and ask LO to re-attach it. Never spend hours building a design system without access to everything he gave you. This applies mid-run: if reads start failing or rate-limiting partway through, stop and report exactly what you did and did not read. Never infer or invent component names, structures, or values for content you could not read.

Finish by naming caveats only, with a clear ask for what LO should check so you can iterate, and a reminder to set the file type to Design System in the Share menu so his org can view it.
