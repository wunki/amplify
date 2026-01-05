---
name: roadmap
description: Create a ROADMAP.md document for open source projects. Analyzes the codebase, defines vision and milestones, organizes work into short/medium/long term goals. Follows open source conventions. Triggers on "create a roadmap", "generate roadmap", "write a ROADMAP.md", "project roadmap", or when a user needs to communicate project direction to contributors.
---

# Roadmap

Create a **ROADMAP.md** document—a public-facing plan that communicates project vision, current status, and future direction.

## Process

### 1) Discover

Analyze the project before asking questions:
- Read README, docs, code structure
- Check issue tracker, existing TODOs, CHANGELOG
- Identify what's built vs what's incomplete

### 2) Clarify

After discovery, ask focused questions to fill gaps. Keep it to 3-5 questions max.

```text
1) Vision: Where is this project heading?
   a) [Inferred from README: "..."]
   b) Different vision: <describe>

2) Audience: Who is this roadmap for?
   a) Just me (personal tracking)
   b) Contributors (open source)
   c) Both

3) Timeframe: How far out to plan?
   a) 3 months
   b) 6 months
   c) 1 year
   d) No specific timeline

4) Priorities: What's most important right now?
   a) [List 2-3 inferred priorities from codebase]
   b) Different priorities: <describe>

Reply with: 1a 2b 3b 4a (or describe)
```

Skip questions where the answer is obvious from discovery.

### 3) Draft

Generate ROADMAP.md using the template below. Present to user before writing to disk.

### 4) Finalize

Incorporate feedback, then write `ROADMAP.md` to project root.

## Template

```markdown
# Roadmap

> Brief one-liner about the project's mission.

## Current Status

What's working today.

## Vision

Where this project is heading. The "why" that gets people excited.

## How to Contribute

Point to areas where help is welcome. Link to CONTRIBUTING.md if it exists.

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

- Write for the intended audience (personal vs contributors)
- Be specific about what help is needed
- Keep milestones concrete and achievable
- Use checkboxes for trackable items, plain text for vision items
- Link to issues/discussions where relevant
