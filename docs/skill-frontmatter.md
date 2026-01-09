# Skill Frontmatter

How to write SKILL.md frontmatter that Claude actually loads.

Source: [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)

## How Claude Chooses Skills

Claude reads your request and decides which skills to load. At startup, Claude sees only the `name` and `description` of each skill. The full SKILL.md body loads only after Claude picks that skill.

This means: **the description is everything**.

## Writing Descriptions

Max 1024 characters.

Answer two questions:

1. **What does this skill do?** List specific actions.
2. **When should Claude use it?** Include words users would say.

### Good Example

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

Why it works:
- Lists specific actions (extract, fill, merge)
- Includes trigger words (PDF, forms, document extraction)
- Says when to use it

### Bad Example

```yaml
description: Helps with documents
```

Why it fails:
- Too vague
- No specific actions
- No trigger words

## The Pattern

```
<What it does: specific actions>. <When to use: trigger phrases>.
```

Examples:

```yaml
# execute-plan skill
description: Work through PLAN.md one task at a time. Use when continuing, resuming, or working on an existing plan. Triggers on "continue the plan", "next task", "pick up where I left off", or any request to make progress on PLAN.md.

# create-plan skill
description: Create a plan for a coding task. Interviews to extract intent, thinks deeply before planning, writes a plan file. Triggers on "create a plan", "make a plan for", "plan out", or when user needs a structured approach.

# code-review skill
description: Review code for quality, security, and maintainability. Use when reviewing PRs, checking code changes, or when user says "review", "check my code", or "look at these changes".
```

## How Trigger Matching Works

Claude uses semantic similarity, not exact string matching. But specific phrases help:

- Include verbs users would say: "continue", "create", "review", "fix"
- Include nouns for the domain: "plan", "code", "PR", "test"
- Put common phrases in quotes: "next task", "pick up where I left off"

## Description vs Body

| Description | Body |
|-------------|------|
| What the skill does (brief) | Detailed instructions |
| When to trigger | Step-by-step workflows |
| Key trigger phrases | Examples and templates |
| | Reference docs |

The body loads after triggering. Put trigger words in the description, not the body.

## Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Lowercase letters, numbers, hyphens (max 64 chars). Match the directory name. |
| `description` | Yes | What it does and when to use it (max 1024 chars). Claude uses this to decide when to load the skill. |
| `allowed-tools` | No | Tools Claude can use without asking when this skill is active. |
| `model` | No | Model to use (e.g., `claude-sonnet-4-20250514`). Defaults to the conversation's model. |

## Troubleshooting

If your skill isn't triggering:

1. Check the description includes words the user said
2. Make the description more specific
3. Add a "Use when..." clause
4. Run `claude --debug` to see loading errors

## References

- [Claude Code Skills Documentation](https://code.claude.com/docs/en/skills)
- [Skills Best Practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices)
- [Skills Overview](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview)
