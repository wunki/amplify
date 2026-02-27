---
name: frontend-slides
description: >
  Creates zero-dependency, animation-rich HTML slide presentations as single self-contained
  files. Use when the user wants to build a presentation from scratch, convert a .ppt or
  .pptx file to a web-based deck, or enhance an existing HTML presentation.
  Don't use for Reveal.js, Marp, Slidev, Google Slides, Keynote, or PowerPoint authoring.
  Don't use for non-presentation HTML pages, landing pages, or dashboards.
---

# Frontend Slides Skill

Create zero-dependency HTML presentations that run entirely in the browser. All CSS and JS
are inlined — no npm, no build step, no external runtime.

## Core Philosophy

1. **Zero Dependencies** — Single HTML file, inline CSS/JS.
2. **Show, Don't Tell** — Generate visual style previews; let the user react instead of
   asking abstract questions like "minimalist or bold?".
3. **Distinctive Design** — No generic AI aesthetics. Every deck should feel custom-crafted.
4. **Production Quality** — Well-commented, accessible, performant code.

Read `references/html-architecture.md` when generating any presentation HTML.
Read `references/style-presets.md` when selecting or describing visual styles or when
asked about fonts, colors, or animation approaches. Skip if the user provides a complete
custom design spec with no style questions.

---

## Phase 0: Detect Mode

Determine what the user wants before proceeding:

- **Mode A — New Presentation:** User wants slides from scratch → Phase 1
- **Mode B — PPT Conversion:** User has a `.ppt` or `.pptx` to convert → Phase 4
- **Mode C — Enhancement:** User has an existing HTML presentation → read the file,
  understand its structure, then jump directly to Phase 3 to apply changes

---

## Phase 1: Content Discovery (New Presentations)

Ask via AskUserQuestion (the built-in interactive question tool):

**Question 1 — Purpose** (single-select)
- "Pitch deck" — selling an idea, product, or company
- "Teaching/Tutorial" — explaining concepts or how-to guides
- "Conference talk" — tech talk, keynote, event
- "Internal presentation" — team updates, strategy

**Question 2 — Length** (single-select)
- "Short (5–10)" — quick pitch, lightning talk
- "Medium (10–20)" — standard presentation
- "Long (20+)" — deep dive

**Question 3 — Content readiness** (single-select)
- "I have all content ready" — just design it
- "I have rough notes" — help organize into slides
- "I have a topic only" — help create the full outline

If content is ready or rough, ask the user to share it now.

---

## Phase 2: Style Discovery

**This is the "show, don't tell" phase.** Do not ask abstract style questions.

### Step 2.1 — Mood Selection

Ask via AskUserQuestion (multi-select, up to 2):

- "Impressed/Confident" — professional, trustworthy
- "Excited/Energized" — innovative, bold, futuristic
- "Calm/Focused" — clear, minimal, thoughtful
- "Inspired/Moved" — emotional, storytelling, cinematic

### Step 2.2 — Generate Style Previews

Based on mood, pick 3 presets from `references/style-presets.md` and generate
mini HTML preview files — one title slide each, self-contained, 50–100 lines.

Place them in `.claude-design/slide-previews/`:
```
.claude-design/slide-previews/
├── style-a.html
├── style-b.html
└── style-c.html
```

Create the `.claude-design/slide-previews/` directory if it does not exist.
Each preview must show typography, color palette, and an entrance animation.

Present to the user:
```
I've created 3 style previews for you to compare:

**Style A: [Name]** — [1 sentence]
**Style B: [Name]** — [1 sentence]
**Style C: [Name]** — [1 sentence]

Open each to see them in action:
- .claude-design/slide-previews/style-a.html
- .claude-design/slide-previews/style-b.html
- .claude-design/slide-previews/style-c.html

Which resonates? What do you like or want changed?
```

### Step 2.3 — Style Confirmation

Ask via AskUserQuestion (single-select):

- "Style A: [Name]"
- "Style B: [Name]"
- "Style C: [Name]"
- "Mix elements" — combine aspects

If "Mix elements", ask for specifics before proceeding.

---

## Phase 3: Generate Presentation

Generate the full presentation using the content from Phase 1 and the style from Phase 2
(or the chosen enhancement changes for Mode C).

Read `references/html-architecture.md` now for the full HTML template, JS class,
accessibility requirements, and performance rules.

### File Output

Single presentation:
```
presentation.html
assets/           (images, if any)
```

Multiple presentations in one project:
```
[presentation-name].html
[presentation-name]-assets/
```

---

## Phase 4: PPT Conversion

### Step 4.1 — Check Dependency

Before extracting, verify `python-pptx` is available:

```bash
python3 -c "import pptx; print('ok')" 2>/dev/null || echo "missing"
```

If missing, run:
```bash
pip install python-pptx
```

If pip fails (permission error, no network), inform the user and stop:
```
python-pptx is required to read .pptx files. Install it with:
    pip install python-pptx
or activate a virtual environment that has it installed.
```

### Step 4.2 — Extract Content

Run the bundled extraction script:

```bash
python3 skills/frontend-slides/scripts/extract_pptx.py <input.pptx> <output_dir>
```

The script outputs a JSON summary (slide count, image count, unsupported shape count) and
writes `<output_dir>/slides.json` plus `<output_dir>/assets/`.

If the script exits non-zero, show the stderr message and stop.

**Unsupported shapes:** Charts, grouped shapes, and embedded video are logged in
`slides.json` under `"unsupported"` per slide. After extraction, check each slide's
`unsupported` array. If any are found, tell the user:
```
Note: [N] shape(s) could not be extracted automatically (e.g. charts, grouped shapes).
Slides affected: [list]. I'll add placeholder sections for these — let me know
what content to put there.
```

### Step 4.3 — Confirm Content

Read `<output_dir>/slides.json` and present a summary:
```
Extracted from [filename]:
  Slides: [count]
  Images: [count] (saved to assets/)
  Unsupported shapes: [count] (noted above if any)

Slide list:
  1. [title] — [content preview]
  2. [title] — [content preview]
  ...

Does this look right? Proceed with style selection?
```

### Step 4.4 — Style and Generate

Proceed to Phase 2 (Style Discovery) with the extracted content in mind, then Phase 3.
Preserve: all text, all images (referenced from assets/), slide order, speaker notes
(as HTML comments at the end of each `<section>`).

---

## Phase 5: Delivery

1. Delete `.claude-design/slide-previews/` if it exists.
2. Open the presentation: `open [filename].html`
3. Provide this summary (fill in the bracketed fields):

```
Your presentation is ready!

File:   [filename].html
Style:  [Style Name]
Slides: [count]

Navigation:
- Arrow keys or Space to advance; scroll/swipe also works
- Click the dots on the right to jump to a slide

To customize:
- Colors: edit :root CSS variables at the top
- Fonts: swap the Fontshare/Google Fonts link
- Animations: adjust .reveal class timings

Want any adjustments?
```

---

## Mood → Style Preset Mapping

Use this to pick 3 presets for Step 2.2. Full specs in `references/style-presets.md`.

| Mood               | Preset options                                      |
|--------------------|-----------------------------------------------------|
| Impressed/Confident | Midnight Executive, Paper & Ink, Swiss Modern      |
| Excited/Energized  | Neon Cyber, Gradient Wave, Terminal Green           |
| Calm/Focused       | Paper & Ink, Swiss Modern, Soft Pastel              |
| Inspired/Moved     | Deep Space, Warm Editorial, Neon Cyber              |

---

## Troubleshooting

**Fonts not loading:** Check Fontshare/Google Fonts URL; ensure font names in CSS match.

**Animations not triggering:** Verify IntersectionObserver is running and `.visible` is
being added to slides.

**Scroll snap not working:** `scroll-snap-type: y mandatory` must be on `html`; each slide
needs `scroll-snap-align: start`.

**Mobile layout broken:** Disable heavy effects at `max-width: 768px`; test touch events.

**Performance issues:** Use `will-change` sparingly; prefer `transform`/`opacity`
animations; throttle `scroll`/`mousemove` handlers.

**python-pptx missing:** See Phase 4, Step 4.1.

**PPTX charts or tables not extracted:** Charts are unsupported by python-pptx's shape
extractor. Tables are extracted as row arrays. Add manual content for chart slides.

---

## Related Skills

- **learn** — Generate FORZARA.md documentation for the presentation
- **frontend-design** — For interactive pages beyond slide decks
- **design-and-refine:design-lab** — For iterating on component designs
