---
name: create-spec
description: Creates or updates a SPEC.md specification document by structuring
  requirements, notes, or interview output into a consistent format with sections
  for goals, design, edge cases, security, testing, and success criteria. Use when
  the user asks to write a spec, create a specification, turn notes or requirements
  into a spec, document a feature design, or structure technical requirements. Don't
  use for requirements gathering or discovery interviews (use the interview skill
  instead), for Architecture Decision Records or RFCs, for general documentation or
  README files, or for implementing code based on a spec.
---

# Create Spec

Structure requirements into a well-organized SPEC.md document. This skill covers the *writing* of specs, not requirements gathering (use the `interview` skill for that).

## Workflow

### 1) Determine Input

Identify what the user has provided:

- **Interview output or structured notes** — proceed to Step 2
- **Unstructured text, PRD, or rough ideas** — proceed to Step 2, noting gaps as Open Questions
- **Existing SPEC.md to update** — read the file first, then extend or revise the relevant sections rather than replacing the whole document; proceed to Step 2
- **Both new input and an existing SPEC.md** — read the existing file; merge new information in, surfacing any contradictions in the Open Questions section; proceed to Step 2
- **No input yet** — ask: "What feature or system is this spec for? Share any notes, requirements, or context you have." Wait for the user's response, then restart from Step 1.

### 2) Read the Template

Read `references/spec-template.md` for the canonical section list and per-section guidance.

### 3) Structure the Spec

Apply the template sections. Omit sections that genuinely don't apply, but consider each one before omitting.

Write with precision:
- Specific over vague: "Validates email format using RFC 5322" not "validates input"
- Include the why: decisions without rationale are useless to future readers
- Note uncertainties as Open Questions rather than inventing answers
- Use concrete examples to illustrate behavior

If input contradicts itself (e.g., interview output conflicts with an existing SPEC.md), surface the conflict explicitly in the Open Questions section rather than silently picking one.

When updating an existing spec: revise in-place where the intent is clearly to replace, append to existing lists where the intent is additive, and add a Decisions Log entry for any significant structural change.

### 4) Write to File

Determine the output path:
- Default: `SPEC.md` in the project root
- User-specified path: use it exactly
- Multiple specs for a project: `specs/[feature-name].md`

If a file already exists at the target path and the user did not explicitly ask to update or extend it, confirm with the user before overwriting.

## Spec Quality Checklist

Before finishing:

- [ ] Summary fits in one or two sentences
- [ ] Goals are measurable, not vague
- [ ] Non-goals explicitly prevent scope creep
- [ ] Design is implementable without guessing
- [ ] Edge cases cover failure modes
- [ ] Success criteria are testable
- [ ] Open questions are honest about unknowns

## Anti-patterns

- **Don't pad**: Empty sections are worse than omitted sections
- **Don't be vague**: "Handle errors" is not a spec
- **Don't skip security**: Even internal tools need threat consideration
- **Don't invent requirements**: If you don't know, mark it as an open question
