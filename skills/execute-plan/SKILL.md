---
name: execute-plan
description: Work through PLAN.md one task at a time with human oversight. Use when continuing, resuming, or making progress on an existing plan. Triggers on "continue", "continue the plan", "let's continue working", "next task", "work on the plan", "pick up where I left off", or any request to execute tasks from PLAN.md.
---

# Execute Plan

Work through a PLAN.md **one task at a time**, with human oversight. Unlike automated loops, this skill encourages questions, explanations, and deliberate progress.

**Prerequisites**: Read and follow `$HOME/.config/opencode/AGENTS.md` throughout this workflow.

## Core Principles

1. **One task per invocation** - Complete one checkbox, then stop
2. **Questions before action** - Clarify ambiguities using `ask-questions-if-underspecified` patterns
3. **Tests are not optional** - Every behavior change needs tests; run them before marking complete
4. **Learn and persist** - Update PLAN.md with discoveries, AGENTS.md with project conventions
5. **Summarize work** - Every completed task gets an inline summary

## Workflow

### 1) Find the Current Task

Read `PLAN.md` and locate the first unchecked `[ ]` item.

**Tracking:** Create TodoItems from the Task Checklist (at the end of this skill) so progress is visible to the user.

**If no PLAN.md exists:**

- If the user specified a plan from `plans/` directory, check that no `PLAN.md` exists in the project root (do not overwrite an active plan). If clear, move the specified plan to `PLAN.md` in the project root and proceed.
- Otherwise, ask the user to create one (suggest `create-plan` skill) or specify which plan from `plans/` to activate.

### 2) Understand Before Acting

Before writing any code:

- **Verify the plan still fits** - If time has passed or earlier tasks changed assumptions, check that this task still makes sense. If not, propose adjustments before proceeding.
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

Use the `write-test` skill for guidance on what to test. Focus on user-facing behavior, not implementation details. If existing tests break, fix them as part of the task.

**Before marking complete, verify the code passes all checks:**

1. **Format**: Run the formatter (e.g., `bun run format`)
2. **Lint**: Run the linter (e.g., `bun run lint`)
3. **Test**: Run the tests (e.g., `bun run test:all`)

All three must pass. If any fail, fix the issues before proceeding.

### 4) Reflect and Persist Learnings

Before marking complete, ask yourself:

- What did I learn about how this project works?
- Would this knowledge help on future tasks?

Persist learnings now (before context is lost):

- **Plan-specific** (e.g., "this endpoint already exists", "the schema uses soft deletes"): Add a note in PLAN.md near the relevant task
- **Project-wide** (e.g., "all API routes use kebab-case", "tests require `DATABASE_URL` set"): Update AGENTS.md so future plans benefit
- **User-facing features**: If the project has a `docs/` directory, update relevant documentation

### 5) Mark Complete with Summary

After completing the task, update PLAN.md:

```markdown
- [x] Add JWT authentication to /api/login
  > Implemented in `src/auth/jwt.ts`. Uses HTTP-only cookies with 15min
  > access tokens. Refresh endpoint at `/api/refresh`. Added middleware
  > in `src/middleware/auth.ts`.
```

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

### AGENTS.md Updates

Add to AGENTS.md when you discover **how this project works**:

- Build/test commands that aren't documented
- Naming conventions
- Architectural patterns
- Common gotchas

Format as actionable guidance:

```markdown
## Project-Specific

- **Auth**: All auth logic lives in `src/auth/`. Use `requireAuth` middleware, not manual token checks.
- **Testing**: Run `pnpm test:unit` for fast feedback, `pnpm test:e2e` before PR.
```

### Documentation Updates

If the project has a `docs/` directory and you build user-facing features:

- Check if relevant docs exist
- Update them to reflect new functionality
- Ask the user if unsure whether to document

## Plan Completion

When all tasks are checked:

1. Congratulate briefly (one line, no fluff)
2. Summarize what was built overall
3. Archive the plan:
   - Create `plans/` directory if it doesn't exist
   - Move PLAN.md to `plans/YYYY-MM-DD-<descriptive-title>.done.md`
   - Use today's date, derive title from the plan's goal, suffix with `.done`
   - The `.done` suffix makes completion status visible in directory listings

```bash
# Example: Plan was about adding authentication
mkdir -p plans
mv PLAN.md plans/2025-01-05-add-user-authentication.done.md
```

4. Mention any follow-up work that emerged during execution

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
