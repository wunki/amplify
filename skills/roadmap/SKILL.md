---
name: roadmap
description: Creates or updates a ROADMAP.md file for a software project by analyzing
  the codebase and defining vision, milestones, and a timeline. Use when the user
  asks to create, generate, write, update, or revise a project roadmap, or wants to
  communicate project direction and priorities to contributors or stakeholders. Don't
  use for updating a single section of an existing roadmap in isolation without touching
  the rest, creating sprint plans or Jira boards, writing a product requirements document,
  or generating architecture or design docs.
---

# Roadmap

Create or update a **ROADMAP.md** document — a plan that communicates project vision, current status, and future direction.

## Process

### 1) Discover

Analyze the project before asking questions:
- Read README.md, docs/, CHANGELOG.md, and any existing ROADMAP.md
- Scan the code structure for what is built vs incomplete (open TODOs, stub files, empty directories)
- Check for an issue tracker link in README or package metadata; if found, note open issues as candidate roadmap items
- If no README or code exists yet, skip to Clarify immediately with no pre-filled answers

### 2) Check for existing ROADMAP.md

- If `ROADMAP.md` already exists: read it, then ask the user whether to **update in place** or **replace entirely**. Default to updating in place unless told otherwise.
- If it does not exist: proceed to Clarify.

### 3) Clarify

After discovery, ask only the questions that cannot be confidently inferred. Keep it to 3-5 questions max. Pre-fill answers from discovery and let the user confirm or override. If discovery yielded nothing, present all questions without pre-fills.

```
1) Vision: Where is this project heading?
   a) [Insert inferred vision from README, or "unclear — please describe"]
   b) Something different — describe it

2) Audience: Who is this roadmap for?
   a) Personal tracking only
   b) Open source contributors
   c) Both

3) Timeframe: How far out to plan?
   a) 3 months
   b) 6 months
   c) 1 year
   d) No specific timeline

4) Priorities: What matters most right now?
   a) [Insert 2-3 inferred priorities from codebase, or "unclear — please describe"]
   b) Different priorities — describe them

Reply with letter codes (e.g. 1a 2b 3b 4a) or describe inline.
```

Skip any question where the answer is obvious from discovery. If the user's replies are terse or ambiguous, make reasonable inferences and state them clearly in the draft.

### 4) Draft

Generate ROADMAP.md using the template in the Template section below, adjusted for audience:
- Personal tracking (audience 2a): omit the "How to Contribute" section
- Open source or both (audience 2b or 2c): include all sections

If updating in place (existing ROADMAP.md, user chose to update):
- Preserve the existing structure and completed items
- Update the Timeline sections to reflect current state: move finished items to Completed, add new items from the user's priorities
- Do not wipe custom sections the user has added outside the template structure

Present the full draft inline. Do not write to disk yet. Ask: "Does this look right? I'll write it to disk once you confirm."

### 5) Finalize

After explicit user confirmation (any affirmative reply counts), write `ROADMAP.md` to the repository root.

- If the repository root is ambiguous (monorepo, multiple package directories, or no git context detected): ask the user to specify the target path before writing.
- A monorepo is likely if the directory contains multiple subdirectories each with their own package.json, go.mod, Cargo.toml, or similar manifest files.
- If replacing entirely: overwrite the file.
- If updating in place: apply the merged draft produced in Step 4; do not discard sections that were present in the original but absent from the template.

## Template

```markdown
# Roadmap

> Brief one-liner about the project's mission.

## Current Status

What is working today.

## Vision

Where this project is heading and why it matters.

## How to Contribute

Areas where help is welcome. Link to CONTRIBUTING.md if it exists.

## Timeline

### Now (Active Development)
- [ ] Task 1
- [ ] Task 2

### Next (Short Term)
- [ ] Task 3
- [ ] Task 4

### Later (Medium Term)
- [ ] Task 5
- [ ] Task 6

### Future (Long Term)
- Task 7
- Task 8

## Out of Scope

What this project intentionally does not do.

## Completed

- [x] Milestone 1
- [x] Milestone 2
```

## Guidelines

- Write for the intended audience — contributors need context; personal notes can be terse
- Be specific about what help is wanted; vague asks attract no one
- Keep milestones concrete and achievable; avoid "improve performance" without a measurable target
- Use checkboxes for trackable tasks, plain text for long-horizon vision items
- Link to issues or discussions where the detail lives
