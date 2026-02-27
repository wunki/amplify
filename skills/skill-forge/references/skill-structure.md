# Skill Structure Rules

Reference when writing or editing a skill body. Skip if only running validation or packaging.

## Voice

Use third-person imperative throughout. The agent reading this skill is the actor.

- Correct: "Extract the schema from the database."
- Wrong: "I will extract..." / "You should extract..." / "Claude will extract..."

## Step Numbering

For sequential workflows, number steps explicitly:

```markdown
1. Do X
2. Do Y — if condition A, skip to Step 4
3. Do Z
4. Do W
```

For decision trees within a step:

```markdown
1. Determine the mode:
   - Creating a new skill → follow Step 2
   - Updating an existing skill → skip to Step 4
```

## Progressive Disclosure Rules

- Keep SKILL.md under **500 lines**. Split content into reference files when approaching this limit.
- Reference files must be **one level deep** only: `references/foo.md`, not `references/db/v1/foo.md`.
- Reference files longer than 100 lines must have a **table of contents** at the top.
- Always use `Read references/X.md when [condition]` — not "See X" or "refer to X".
- Include a skip condition: `Read references/X.md when [condition]. Skip if [skip condition].`

## Bundled Resource Guidelines

| Directory | Purpose | When to include |
|-----------|---------|-----------------|
| `scripts/` | Executable code (Python, Bash) for deterministic or repetitive operations | When the same code would be rewritten from scratch each time |
| `references/` | Dense context loaded on demand: schemas, API docs, domain rules | When the content is too large for SKILL.md or only relevant for some tasks |
| `assets/` | Output templates, boilerplate, fonts, images — not loaded into context | When the skill produces files the user needs (templates, starter projects) |

## What NOT to Create

Do not create any of these files in a skill directory:

- `README.md`
- `CHANGELOG.md`
- `INSTALLATION_GUIDE.md`
- `QUICK_REFERENCE.md`
- Any other human-facing documentation

Skills are for agents, not humans. Extra files add noise and context bloat.

## Specific Terminology

- Use the exact term the domain uses. In skills about skills: "frontmatter", "SKILL.md", "bundled resources", "load instruction".
- Pick one term per concept and use it consistently. Never alternate between "description" and "summary" for the same field.
