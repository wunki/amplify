# Skill Frontmatter Best Practices

How to write effective SKILL.md frontmatter so Claude loads your skill at the right time.

Source: [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

## How Skills Are Triggered

Skills are **model-invoked**: Claude decides which skills to use based on your request. At startup, Claude loads only the `name` and `description` of each skill. The full SKILL.md body is only loaded after Claude decides to use the skill.

This means: **the description field is everything for triggering.**

## The Description Field

Max 1024 characters.

A good description answers two questions:

1. **What does this skill do?** List specific capabilities.
2. **When should Claude use it?** Include trigger terms users would naturally say.

### Good Example

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

Why it works:
- Lists specific actions (extract, fill, merge)
- Lists trigger terms (PDF, forms, document extraction)
- Says when to use it explicitly

### Bad Example

```yaml
description: Helps with documents
```

Why it fails:
- Too vague
- No specific capabilities listed
- No trigger terms

## Pattern for Descriptions

```
<What it does: specific actions/capabilities>. <When to use: trigger phrases and contexts>.
```

Examples:

```yaml
# execute-plan skill
description: Work through PLAN.md one task at a time. Use when continuing, resuming, or working on an existing plan. Handles "continue the plan", "next task", "pick up where I left off", "let's continue working", or any request to make progress on PLAN.md.

# create-plan skill
description: Create a plan for a coding task. Interviews to extract intent, thinks deeply before planning, writes a plan file. Triggers on "create a plan", "make a plan for", "plan out", "help me plan", or when user needs structured approach to a task.

# code-review skill
description: Review code for quality, security, and maintainability. Use when reviewing PRs, checking code changes, or when user mentions "review", "check my code", or "look at these changes".
```

## Trigger Matching

Claude uses **semantic similarity**, not exact string matching. But including specific phrases helps:

- Include verbs users would say: "continue", "create", "review", "fix"
- Include nouns for the domain: "plan", "code", "PR", "test"
- Include common phrasings in quotes: "next task", "pick up where I left off"

## What Goes in the Body vs Description

| Put in description | Put in body |
|-------------------|-------------|
| What the skill does (brief) | Detailed instructions |
| When to trigger it | Step-by-step workflows |
| Key trigger phrases | Examples and templates |
| | Reference documentation |

The body is only loaded after triggering, so don't put trigger-relevant info there.

## Available Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase letters, numbers, hyphens (max 64 chars). Should match directory name. |
| `description` | Yes | What it does and when to use it (max 1024 chars). **This is what Claude uses to decide when to apply the skill.** |
| `allowed-tools` | No | Tools Claude can use without permission when skill is active. |
| `model` | No | Model to use (e.g., `claude-sonnet-4-20250514`). Defaults to conversation's model. |

## Debugging

If a skill isn't triggering:

1. Check the description includes terms the user actually said
2. Make the description more specific, not less
3. Add explicit "Use when..." clause
4. Run `claude --debug` to see skill loading errors

## References

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
