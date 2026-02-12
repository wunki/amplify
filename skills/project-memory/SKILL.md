---
name: project-memory
description: Maintain durable, project-specific memory in `MEMORY.md` at the repository root. Load it at session start and before major work, then append concise lessons when users ask to remember preferences, conventions, and mistakes.
---

# Project Memory

Store and apply project-specific memory from `MEMORY.md` in the repository root.

## What this skill does

- Loads persistent project memory from `MEMORY.md`.
- Captures new lessons when the user asks to remember something.
- Applies past lessons before substantial work.

## When to use

- At session start, if `MEMORY.md` exists.
- Before major implementation work.
- When the user says things like:
  - "remember this"
  - "save this to memory"
  - "add to memory"
  - "don't do this again"
  - "project-memory"
  - "scratchpad" (legacy phrasing)
- After any mistake worth preventing next time.

## Initial session behavior

At session start:

1. Check for `MEMORY.md` at the project root.
2. If it exists, read it.
3. Acknowledge loaded memory with a short summary:
   - "Loaded project memory: [key points]"
4. Explicitly state how it affects this session.

## Capturing new memory

When the user asks to save memory or corrects your behavior:

1. Decide if the information should persist:
   - Repeated mistakes
   - User workflow preferences
   - Project conventions
   - Important context likely to matter later
2. If `MEMORY.md` does not exist, create it with the format below.
3. Append a concise entry under the relevant category.
4. Confirm save:
   - "Saved to project memory: [what was saved]"

## Memory file format

Use this structure in `MEMORY.md`:

```markdown
# Project Memory

## User Preferences
### [YYYY-MM-DD] Short title
Context: What happened
Memory: What to remember
Action: How to behave next time

## Project Conventions
### [YYYY-MM-DD] Short title
Context: ...
Memory: ...
Action: ...

## Past Mistakes
### [YYYY-MM-DD] Short title
Context: ...
Memory: ...
Action: ...

## Environment Notes
### [YYYY-MM-DD] Short title
Context: ...
Memory: ...
Action: ...
```

## Applying memory

Before starting substantial work:

1. Scan relevant entries in `MEMORY.md`.
2. Call out relevant lessons before acting.
3. Use lessons to guide decisions.
4. If memory conflicts with the current request, ask for clarification.

## Best practices

- Keep memory concise and scannable.
- Record durable behavior, not long transcripts.
- Prefer concrete rules over vague advice.
- Prune outdated entries occasionally.
- Never store secrets, tokens, credentials, or personal data.

## Relationship to normal context

`MEMORY.md` is for persistent, cross-session project memory.
Use normal conversation context for temporary task details.
