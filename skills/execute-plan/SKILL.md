---
name: execute-plan
description: Executes tasks from a PLAN.md file one at a time with human oversight, handling task splitting, clarifying questions, tests, and learning persistence. Use when the user says "execute the plan", "work on the plan", "next task", "pick up where I left off", "continue the plan", "resume the plan", or asks to make progress on a specific PLAN.md. Don't use for general task execution without a PLAN.md, creating a new plan (use create-plan instead), answering questions about what is in a plan without executing it, one-off commands or scripts with no plan file, or continuing an unrelated conversation.
---

# Execute Plan

Work through a PLAN.md **one task at a time**, with human oversight. Unlike automated loops, this skill encourages questions, explanations, and deliberate progress.

**Prerequisites**: If a project-level `AGENTS.md` exists at the repository root, read it before starting and follow its conventions throughout this workflow.

## Core Principles

1. **One task per invocation** - Complete one checkbox, then stop
2. **Questions before action** - Clarify ambiguities using `ask-questions-if-underspecified` patterns
3. **Tests are not optional** - Every behavior change needs tests; run them before marking complete
4. **Learn and persist** - Update PLAN.md with discoveries, AGENTS.md with project conventions
5. **Summarize work** - Every completed task gets an inline summary

## Workflow

### 1) Find the Current Task

Read `PLAN.md` at the repository root and locate the first unchecked `[ ]` item that is not prefixed with `BLOCKED:`.

**Tracking:** If a TodoWrite tool is available in the current environment, create TodoItems from the Task Checklist (at the end of this skill) so progress is visible to the user. Detect availability by checking whether the tool appears in the active tool list. Skip this step if the tool is not available.

**If no PLAN.md exists at the repository root:**

1. If the user specified a plan inline, write it to `PLAN.md` and proceed.
2. Otherwise, ask the user to create one (suggest `create-plan` skill). If a `SPEC.md` exists, offer to generate a plan from it.

**If the first unchecked task is `BLOCKED:`:** Report the blocker to the user, state what is needed to unblock it, and stop. Do not skip to a later task without explicit user instruction.

**If all remaining unchecked tasks are `BLOCKED:`:** Report each blocker with its unblock condition, then stop. Do not attempt to work around blockers.

### 2) Understand Before Acting

Before writing any code:

- **Verify the plan still fits** - If earlier tasks changed the codebase in ways that affect this task (e.g., a file was renamed, an API was replaced, a dependency was removed), note the conflict and propose adjustments before writing any code.
- Read relevant files mentioned in the task
- Check existing patterns in the codebase
- Identify what "done" looks like for this specific task

**If the task is too large:** Split it in PLAN.md before writing any code. Break it into atomic steps, then work only on the first one. A task is too large if it touches multiple unrelated areas or would take more than one focused session.

If anything is unclear, **ask questions first**. Use the `ask-questions-if-underspecified` patterns:

```text
Before I start on: "Add JWT authentication to /api/login"

1) Token storage?
   a) HTTP-only cookie (recommended for web)
   b) localStorage
   c) Let me decide based on existing auth patterns

2) Expiration?
   a) 15min access + 7d refresh (default)
   b) Different duration: <specify>

Reply with: 1a 2a (or describe)
```

Do not proceed until questions are answered or user says to use defaults.

### 3) Execute the Task

Complete the work. Stay focused on just this one task.
After each substantive change, simplify and clean up touched areas when appropriate.

**Testing is not optional.** Every task that changes behavior must include tests:

- **Unit tests**: Always. Cover the behavior you added or changed.
- **E2E tests**: If the task touches UI or user-facing workflows.

Use the `write-test` skill for guidance on what to test if it is available. Focus on user-facing behavior, not implementation details. If existing tests break, fix them as part of the task.

**Before marking complete, verify the code passes all checks.**

Check `package.json`, `Makefile`, `.github/workflows/`, or project docs to identify the actual commands. Common patterns:

1. **Format**: e.g., `bun run format`, `npm run format`, `mix format`
2. **Lint**: e.g., `bun run lint`, `npm run lint`, `mix credo`
3. **Test**: e.g., `bun run test:all`, `npm test`, `mix test`

All applicable checks must pass. If any fail, fix the issues before proceeding.

**If none of these files exist:** Ask the user how to run checks before proceeding. Do not invent commands.

**If the project has no test infrastructure:** Note this explicitly in the task summary and skip the test step. Do not invent test commands.

### 4) Reflect and Persist Learnings

Before marking complete, ask yourself:

- What did I learn about how this project works?
- Would this knowledge help on future tasks?

Persist learnings now (before context is lost):

- **Plan-specific** (e.g., "this endpoint already exists", "the schema uses soft deletes"): Add a note in PLAN.md near the relevant task.
- **Project-wide** (e.g., "all API routes use kebab-case", "tests require `DATABASE_URL` set"): Update `AGENTS.md` at the repository root. If `AGENTS.md` does not exist, create it with a `## Project-Specific` section containing the new entry.
- **User-facing features**: If the project has a `docs/` directory, update relevant documentation.

### 5) Mark Complete with Summary

After completing the task, update PLAN.md with a completion summary.

Read `references/summary-examples.md` when writing a task summary. Skip if the format is already clear from earlier tasks in the session.

Summary guidelines:

- 1-3 lines, indented with `>`
- What was done (not how)
- Key files created/modified
- Important decisions made
- Gotchas for future reference

### 6) Report and Stop

After marking the task complete:

1. Show the user what was done
2. Mention any learnings persisted to AGENTS.md or docs
3. State what the next task is (but don't start it)

Let the user decide when to continue. They may want to review, test, or commit first.

## Plan Mutations

The plan is a living document. Update it when reality diverges:

**Splitting a task (during research, before any code):**

```markdown
## Action items

<!-- "Set up database schema" was too large, split into: -->

- [ ] Define user table with email/password fields
- [ ] Define session table for refresh tokens
- [ ] Run migration and verify
```

**Adding discovered work:**

```markdown
- [x] Add rate limiting to auth endpoints
  > Implemented using express-rate-limit. 5 attempts per 15min.
  > NOTE: Discovered Redis is not configured. Added task below.
  > ...
- [ ] Configure Redis for distributed rate limiting (added: discovered during rate limiting work)
```

**Blocking issues:**

```markdown
- [ ] BLOCKED: Deploy to staging - waiting on DevOps to provision new env
```

## Learning Persistence

### AGENTS.md Format

Format entries as actionable guidance under a `## Project-Specific` section:

```markdown
## Project-Specific

- **Auth**: All auth logic lives in `src/auth/`. Use `requireAuth` middleware, not manual token checks.
- **Testing**: Run `pnpm test:unit` for fast feedback, `pnpm test:e2e` before PR.
```

### Documentation Updates

If the project has a `docs/` directory and you built a user-facing feature:

- Check if relevant docs exist
- Update them to reflect new functionality
- Ask the user if unsure whether to document

## Plan Completion

When all tasks are checked:

1. Congratulate briefly (one line, no fluff)
2. Summarize what was built overall
3. Archive the spec if `SPEC.md` exists at the repository root:
   - Create `specs/` directory if it doesn't exist
   - Move `SPEC.md` to `specs/YYYY-MM-DD-<descriptive-title>.md` using today's date
   - Derive the title from the spec's stated goal
   - Skip this step entirely if `SPEC.md` does not exist
4. Remove `PLAN.md` (do not archive plans)
5. Mention any follow-up work that emerged during execution

```bash
# Example: Spec was about adding authentication, today is 2026-02-27
mkdir -p specs
mv SPEC.md specs/2026-02-27-add-user-authentication.md
rm PLAN.md
```

## Anti-patterns

- **Don't batch tasks** - One task, one invocation
- **Don't skip questions** - The human is present; use that
- **Don't forget summaries** - Future you will thank present you
- **Don't hoard learnings** - If it's reusable, persist it
- **Don't touch git** - User handles commits via `/smart-commit`

## Task Checklist (Quick Reference)

For every task, complete ALL steps:

- [ ] Read PLAN.md, find first unchecked task
- [ ] Research: read relevant code, check patterns
- [ ] Split task in PLAN.md if too large (before writing any code)
- [ ] Ask clarifying questions if anything unclear
- [ ] Implement the change
- [ ] Write tests (unit always, e2e if UI touched)
- [ ] Run format, lint, and tests (all must pass)
- [ ] Reflect: what did I learn? Persist to PLAN.md, AGENTS.md, or docs/
- [ ] Mark task complete with summary in PLAN.md
- [ ] Report to user, state next task, stop
