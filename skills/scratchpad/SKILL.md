---
name: scratchpad
description: Maintain a persistent, project-specific memory of mistakes, preferences, and lessons learned in `.claude/scratchpad.md`, then apply it every session. Use when asked to "remember this", "don't do this again", "learn from this", "save this preference", or when recurring project context should persist across sessions.
---

# scratchpad

Store and apply project-specific memory from `.claude/scratchpad.md`.

## What this skill does

- Loads persistent guidance at session start from `.claude/scratchpad.md`.
- Captures new lessons when the user asks to remember them.
- Applies past lessons before doing work.

## When to use

- Start of each session if `.claude/scratchpad.md` exists.
- User says:
  - "add to scratchpad"
  - "remember this"
  - "don't do this again"
  - "save this preference"
  - "learn from this"
- After any mistake worth preventing next time.

## Initial session behavior

At session start:

1. Check for `.claude/scratchpad.md`.
2. If it exists, read it.
3. Acknowledge loaded memory with a short summary:
   - "Loaded scratchpad memory: [key points]"
4. Explicitly state how it affects this session.

## Capturing new memory

When the user asks to save memory or corrects your behavior:

1. Decide whether it is worth persisting:
   - Repeated mistakes
   - User workflow preferences
   - Project conventions
   - Important context likely to matter later
2. Append to `.claude/scratchpad.md` with a clear heading and date.
3. Keep entries concise and actionable.
4. Confirm save:
   - "Saved to scratchpad: [what was saved]"

## Memory file format

Use this structure in `.claude/scratchpad.md`:

```markdown
# Scratchpad Memory

## [YYYY-MM-DD] Category
Context: What happened
Lesson: What to remember
Action: How to behave next time

## [YYYY-MM-DD] Category
Context: ...
Lesson: ...
Action: ...
```

## Memory categories

- **User Preferences**: Communication and workflow choices.
- **Project Conventions**: Code style and repo-specific patterns.
- **Past Mistakes**: Errors and corrective behavior.
- **Environment Notes**: Setup quirks and constraints.

## Applying memory

Before starting any substantial task:

1. Quickly scan relevant memory entries.
2. Call out relevant lessons before acting.
3. Use lessons to guide decisions.
4. If memory conflicts with current request, ask for clarification.

## Example behavior

**Session start:**

```text
I found and loaded .claude/scratchpad.md.
Key points:
- Prefer bun over npm
- Always run tests after changes
- Use concise commit messages

I'll follow these preferences in this session.
```

**When user says "remember this":**

```text
User: "Use descriptive variable names, avoid abbreviations"
Assistant: "Saved to scratchpad: coding style preference for descriptive variable names."
```

**When applying memory:**

```text
"Based on scratchpad memory, I'll run `bun test` after making these changes."
```

## Best practices

- Keep memory short and scannable.
- Record behavior, not long transcripts.
- Prefer concrete rules over vague advice.
- Periodically prune outdated entries.
- Never store secrets, tokens, or credentials.

## Relationship to ephemeral memory

scratchpad is for persistent, cross-session memory.
Use normal context for task-specific, temporary details.

## Trigger phrases

This skill should activate when seeing:

- "scratchpad"
- "remember this"
- "save this"
- "don't forget"
- "learn from this"
- "add to memory"
