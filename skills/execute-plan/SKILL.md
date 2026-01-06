---
name: execute-plan
description: Work through a PLAN.md one task at a time. Asks clarifying questions, marks tasks done with summaries, persists learnings to AGENTS.md, and archives completed plans. Triggers on "execute the plan", "continue the plan", "continue", "let's continue", "let's continue work", "continue work", "continue work on the plan", "work on next task", "pick up where I left off", or when a PLAN.md exists and user wants guided execution.
---

# Execute Plan

Work through a PLAN.md **one task at a time**, with human oversight. Unlike automated loops, this skill encourages questions, explanations, and deliberate progress.

**Prerequisites**: Read and follow `$HOME/.config/opencode/AGENTS.md` throughout this workflow.

## Must-Follow Guardrails

- Ask before adding dependencies
- No mocks, test behavior not implementation, run only tests you touched
- Low-risk decisions can be made and noted, high-risk decisions must be confirmed

## Core Principles

1. **One task per invocation** - Complete one checkbox, then stop
2. **Questions before action** - Clarify ambiguities using `ask-questions-if-underspecified` patterns
3. **Learn and persist** - Update PLAN.md with discoveries, AGENTS.md with project conventions
4. **Summarize work** - Every completed task gets an inline summary

## Workflow

### 1) Find the Current Task

Read `PLAN.md` and locate the first unchecked `[ ]` item. If no PLAN.md exists, ask the user to create one (suggest `create-plan` skill).

### 2) Understand Before Acting

Before writing any code:

- Read relevant files mentioned in the task
- Check existing patterns in the codebase
- Identify what "done" looks like for this specific task

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

If the task is **bigger than expected**:

- If it can be split into 2-3 subtasks, restructure PLAN.md inline
- If it's substantially larger, propose creating a new dedicated PLAN.md for it
- Ask the user which approach they prefer

If you **discover something new**:

- **Task-specific**: Add a note in PLAN.md near the relevant task
- **Project-wide convention**: Update AGENTS.md
- **User-facing feature**: Check if `docs/` exists and update relevant docs

### 4) Mark Complete with Summary

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

### 5) Report and Stop

After marking the task complete:

1. Show the user what was done
2. Mention any learnings persisted to AGENTS.md or docs
3. State what the next task is (but don't start it)

Let the user decide when to continue. They may want to review, test, or commit first.

## Plan Mutations

The plan is a living document. Update it when reality diverges:

**Splitting a task:**

```markdown
## Action items

- [x] Set up database schema
  > Created initial schema in `prisma/schema.prisma`
- [ ] Add user table with email/password fields
- [ ] Add session table for refresh tokens
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
   - Move PLAN.md to `plans/YYYY-MM-DD-<descriptive-title>.md`
   - Use today's date and derive title from the plan's goal

```bash
# Example: Plan was about adding authentication
mkdir -p plans
mv PLAN.md plans/2025-01-05-add-user-authentication.md
```

4. Mention any follow-up work that emerged during execution

## Anti-patterns

- **Don't batch tasks** - One task, one invocation
- **Don't skip questions** - The human is present; use that
- **Don't forget summaries** - Future you will thank present you
- **Don't hoard learnings** - If it's reusable, persist it
- **Don't touch git** - User handles commits via `/smart-commit`

## Trigger Phrases

- "execute the plan"
- "continue the plan"
- "continue"
- "let's continue"
- "let's continue work"
- "continue work"
- "continue work on the plan"
- "work on next task"
- "pick up where I left off"
- "let's work through PLAN.md"
