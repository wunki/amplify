---
name: frontend-design
description: >
  Designs and builds distinctive, production-grade frontend interfaces with high
  aesthetic intentionality. Use when the user asks to create, design, or build a
  web UI from scratch, substantially redesign an existing one for visual
  improvement, or apply a specific design direction — including landing pages,
  dashboards, React/Vue/Svelte components, HTML/CSS layouts, single-page apps,
  or interactive artifacts. Also use when the user explicitly asks to make a UI
  visually striking, beautify it, give it a mood or theme, or produce a polished
  visual result. Don't use for: adding UI functionality without changing
  appearance, bug fixes to existing CSS or JS, accessibility audits, frontend
  performance profiling, framework migrations, writing tests for UI components,
  backend work that incidentally touches a frontend file, or purely structural
  refactors that have no visual outcome.
license: Complete terms in LICENSE.txt
---

Implement real working frontend code with exceptional aesthetic intentionality.
The goal is distinctive, production-grade output that avoids generic AI aesthetics.

## Execution Steps

1. **Determine the task type:**
   - Building new UI from scratch → follow Steps 2–5.
   - Redesigning or beautifying existing UI → read the existing code first, note
     the constraints, then follow Steps 2–5.
   - Refining a previous output in this session → apply targeted changes and
     skip to Step 5. Do not re-execute the full design thinking phase.

2. **Understand context before touching code:**
   - Purpose: what problem does this interface solve, and who uses it?
   - Brand constraints: has the user provided colors, fonts, a design system,
     brand guidelines, a reference image, or a Figma/screenshot link? If yes,
     treat those as hard constraints and respect them exactly. Do not override
     explicit brand constraints with a "bold" aesthetic direction. If no brand
     input is provided, invent a cohesive palette and typography pairing that
     fits the purpose — do not ask for missing constraints, just make a clear
     design decision and state it.
   - Existing design system: if the project already uses a component library
     (Material UI, shadcn/ui, Ant Design, etc.), work within its token system
     for colors and spacing. Apply distinctive aesthetic choices through
     typography, layout composition, and custom CSS layered on top — do not
     fight the component library's fundamentals.
   - Technical constraints: framework, target environment (browser, mobile,
     artifact), performance requirements, accessibility needs.
   - Responsive scope: default to mobile-first responsive layouts unless the
     user specifies desktop-only. Use CSS media queries or responsive utilities
     appropriate to the framework.
   - Differentiation: what is the one thing someone will remember about this UI?

3. **Commit to a clear aesthetic direction.** Name it explicitly in a short
   comment before the first file's code block (e.g., `/* Direction: editorial
   brutalism */`; use `{/* */}` for JSX, `<!-- -->` for HTML, or a plain prose
   line for other formats). Bold maximalism and refined minimalism both work —
   the key is intentionality, not intensity. Do not start coding without a
   direction.

4. **Implement working code** using the framework or format the user specifies.
   If no framework is specified, default to self-contained HTML/CSS/JS.
   - For React with animations: use inline CSS animations or CSS keyframes by
     default. Use the Motion library only if it is already present in the
     project's dependencies; do not import it speculatively.
   - For single-component output: deliver one complete, self-contained file.
   - For multi-file output (full page, route, or app section): deliver each
     file in its own clearly labeled code block with the intended file path as
     the block header (e.g., `// src/components/Hero.tsx`). List all output
     files at the top before the first code block so the user knows what to
     expect.

5. **Review before delivering:**
   - Does the output reflect the named aesthetic direction consistently?
   - Are there any generic font or color choices that snuck in? (See the
     Anti-patterns section below.)
   - Is every animation purposeful, not decorative noise?
   - Is the layout responsive (or is desktop-only intentional and noted)?
   - Then deliver the output. For refinements triggered by Step 1's third
     branch, deliver only the changed portions with brief context on what
     changed and why.

## Aesthetics Reference

**Typography**: Pair a distinctive display font with a refined body font. Avoid
overused families: Inter, Roboto, Arial, system-ui, Space Grotesk, Outfit, Plus
Jakarta Sans. Use Google Fonts or system alternatives that match the aesthetic
direction.

**Color**: Commit to a cohesive palette. Use CSS variables for consistency.
Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
Avoid: purple gradients on white backgrounds, generic blue-on-white SaaS palette.

**Motion**: Prioritize CSS-only animations for HTML. Focus on high-impact moments
— one well-orchestrated page load with staggered reveals creates more delight than
scattered micro-interactions. Use scroll-triggered animations and hover states that
surprise.

**Spatial Composition**: Unexpected layouts, asymmetry, overlap, diagonal flow,
grid-breaking elements. Choose generous negative space OR controlled density.

**Backgrounds and Depth**: Create atmosphere rather than defaulting to solid
colors. Options: gradient meshes, noise textures, geometric patterns, layered
transparencies, dramatic shadows, grain overlays, decorative borders.

**Anti-patterns — never use:**
- Font families: Inter, Roboto, Arial, system-ui, Space Grotesk, Outfit, Plus Jakarta Sans
- Color schemes: purple/violet gradients on white, generic blue SaaS palette
- Layouts: centered hero + three-column features + CTA footer (default SaaS template)
- Effects: generic glassmorphism cards on every surface, flat-color buttons

No two designs should look the same. Vary light/dark themes, font pairings, and
spatial composition across generations.

## Accessibility Baseline

Even for visually ambitious designs, maintain:
- Minimum 4.5:1 contrast ratio for body text, 3:1 for large text.
- Focus-visible states on all interactive elements.
- Semantic HTML structure (use `<nav>`, `<main>`, `<section>`, `<h1>`–`<h6>`
  correctly).
- Do not rely on color alone to convey meaning.

If the user has explicitly deprioritized accessibility, proceed but note the
tradeoffs in a comment.
