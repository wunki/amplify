---
name: session-reviewer
description: Extract learnings from the current session and recommend what to record for future work. Reviews the conversation for friction points, working commands, and discoveries worth preserving. Triggers on "review this session", "what did we learn", "session review", "capture learnings", or at the end of a work session.
---

# Session Reviewer

Mine the current conversation for knowledge worth preserving. You have full access to the chat history; use it.

## The Problem

Claude Code sessions are ephemeral. Every session, we discover things:
- "This command works, that one doesn't"
- "This API has a quirk where..."
- "The build fails unless you..."

Without capturing these, the next session starts from zero. Your job is to extract the gold before it's lost.

## Workflow

### 1) Gather Context

Read these files if they exist (in parallel):
- `PLAN.md` - Is there an active plan? Is it complete (all tasks checked)?
- `CLAUDE.md` (project root) - What's already documented? Don't duplicate.
- `~/.claude/CLAUDE.md` (global config) - User's personal preferences across all projects.
- `docs/` directory - What user-facing documentation exists?

### 2) Review the Session

Scan the conversation for **friction points**:

- What took multiple attempts to get right?
- What commands failed before we found working ones?
- What assumptions were wrong?
- What wasn't obvious from the code or docs?
- What would have been faster if we'd known it upfront?

Also scan for **discoveries**:

- Working commands and workflows (especially non-obvious ones)
- Codebase patterns that weren't documented
- Environment or tooling quirks
- Decisions made and their rationale

### 3) Apply Quality Filters

For each potential learning, ask:

| Filter | Question |
|--------|----------|
| **5-Minute Rule** | Would knowing this upfront have saved at least 5 minutes? |
| **Recurrence Test** | Will this come up again? (Skip one-time issues) |
| **Specificity Test** | Is it actionable? ("Be careful with X" is useless; specific guidance is useful) |
| **Duplication Test** | Is this already in CLAUDE.md or obvious from the code? |

If any answer is "no", skip it.

### 4) Categorize by Destination

| Destination | What Goes There | Examples |
|-------------|-----------------|----------|
| **~/.claude/CLAUDE.md** | Personal preferences that apply to all projects | Coding style, communication preferences, workflow habits |
| **CLAUDE.md** (project) | Project-specific knowledge for future Claude sessions | Commands, gotchas, patterns, conventions |
| **PLAN.md** | Context for remaining tasks in the current plan | Dependencies discovered, blockers, revised approaches |
| **docs/** | User-facing documentation (features, APIs, setup) | New endpoints, changed config, new features |
| **Nothing** | Generic knowledge, one-time issues, already documented | Standard debugging, temporary workarounds |

### 5) Present Recommendations

Use this format:

```markdown
## Session Review

### Summary
[1-2 sentences: what was accomplished this session]

### Friction Points
- [Thing that was harder than expected and why]
- [Another friction point]

### Recommendations

#### Add to ~/.claude/CLAUDE.md (global)

**Section:** [Coding Style | Communication | Workflow]

> [Exact text to add, ready to copy-paste]

**Why:** [User expressed this preference; applies to all projects]

---

#### Add to CLAUDE.md (project)

**Section:** Commands (or Gotchas, Patterns, etc.)

> [Exact text to add, ready to copy-paste]

**Why:** [What pain this prevents]

---

#### Update PLAN.md

**Add to task X / Notes section:**

> [Exact text to add]

**Why:** [How this helps remaining tasks]

---

#### Documentation Needed

**What:** [Brief description of what to document]
**Where:** [File path, e.g., docs/api.md]
**Action:** Run `/tech-docs-writer` with brief: "[specific guidance]"

---

### Considered but Skipped
- [Learning X] - Already in CLAUDE.md
- [Learning Y] - One-time issue, won't recur
```

### 6) Wait for Approval

Present recommendations. Do not make changes until the user approves. They may want to:
- Edit the wording
- Skip some recommendations
- Add context you missed

## What Makes Good Global Config (~/.claude/CLAUDE.md)

Personal preferences that apply everywhere:

**Coding Style**
```markdown
## Coding Style
- Prefer explicit returns over implicit
- No emojis in code or comments
- Use descriptive variable names, never abbreviate
```

**Communication**
```markdown
## Communication
- Be concise, skip pleasantries
- Don't ask "shall I proceed?" - just do it or state what you'll do
- When in doubt, ask clarifying questions
```

**Workflow**
```markdown
## Workflow
- Always run tests before committing
- Prefer small, atomic commits
- Don't push to main without asking
```

**Key distinction:** If the user says "I prefer X" or corrects your behavior in a way that would apply to any project, that's global. If it's about how this specific codebase works, that's project-level.

## What Makes Good Project CLAUDE.md Content

Structure learnings by category:

**Commands and Workflows**
```markdown
## Commands
- Run tests: `make test-unit` (fast) or `make test-all` (includes e2e)
- Build: `npm run build` (runs type-check first)
- Lint: `npm run lint -- --fix` (auto-fixes what it can)
```

**Gotchas** (things that will bite you)
```markdown
## Gotchas
- The auth middleware lowercases all header names
- `user.deleted` is a soft delete; always check `deleted_at` field
- Tests fail silently if Redis isn't running locally
- The `/api/users` endpoint returns 404 for soft-deleted users
```

**Patterns** (how this codebase does things)
```markdown
## Patterns
- All API responses use `{ data, error }` shape, never throw
- Feature flags live in `config/features.ts`, not env vars
- Database queries go through `src/db/queries/`, not inline SQL
```

## When to Recommend Documentation Updates

Only recommend docs work when ALL of these are true:
1. PLAN.md exists AND all tasks are checked complete
2. The completed work includes user-facing changes
3. Existing docs don't already cover it

**Recommend docs for:** New features, changed APIs, new configuration options, updated workflows.

**Don't recommend docs for:** Internal refactors, bug fixes, performance improvements, test additions.

When docs are needed, suggest running the `tech-docs-writer` skill with a specific brief.

## Examples

### Good Recommendation (Global Preference)

> **Add to ~/.claude/CLAUDE.md (Coding Style):**
>
> "Prefer early returns over nested if/else blocks."
>
> **Why:** User corrected nested conditional code twice this session, expressing preference for guard clauses.

### Good Recommendation (Project Knowledge)

> **Add to CLAUDE.md (Gotchas):**
>
> "The test database resets between test files but not between tests in the same file. Use `beforeEach` for isolation, or tests will pollute each other."
>
> **Why:** We spent 15 minutes debugging flaky tests before discovering test pollution from a previous test case.

### Bad Recommendation (too generic)

> **Add to CLAUDE.md:**
>
> "Always write tests for new features."
>
> **Why:** This is generic advice, not project-specific knowledge.

### Bad Recommendation (one-time issue)

> **Add to CLAUDE.md:**
>
> "If npm install fails with ENOENT, delete node_modules and retry."
>
> **Why:** This was a one-time corruption issue, not a recurring project problem.

### Bad Recommendation (already obvious)

> **Add to CLAUDE.md:**
>
> "Run `npm install` before running tests."
>
> **Why:** This is standard practice, not project-specific insight.

## If the Session Has No Learnings

Sometimes sessions are straightforward. If you review the conversation and find nothing worth recording:

> "Reviewed the session. No significant friction points or new discoveries. The work was straightforward and existing documentation covered what was needed."

Don't manufacture recommendations just to have output.
