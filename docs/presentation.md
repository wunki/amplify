---
theme: dark
author: Amplify
date: MMMM dd, YYYY
paging: "%d / %d"
---

# Building the Agent Harness
## The future of software development

---

# This Is Happening Now

Antirez (creator of Redis):

> "Writing code is no longer needed for the most part.
> For most projects, writing the code yourself is
> no longer sensible, if not to have fun."

He completed **weeks of work in hours**.

---

# Second Signal

Mike Arnaldi (creator of Effect):

> "While software development as we know it is dead,
> software engineering is alive and well."

He built a Bloomberg Terminal clone in **2 hours**.
**Zero lines of code written or reviewed.**

---

# The New Reality

> "Engineers are no longer writing software.
> They're designing higher-order systems.
> Systems that write code."

This talk is about building those systems.

---

# The Catch

Agents are incredibly capable.

But capability without structure is just fast chaos.

> "The outcome is defined by the process, not the model."

**The bottleneck isn't the model. It's the harness.**

---

# Aside: Three Clarifications

**This is not vibecoding.**
Vibecoding is "let it rip" with zero validation.
This is paying attention, thinking, validating, closing the loop.

**Tooling is not the point.**
I'm using OpenCode. Same principles apply in Claude Code, Cursor, etc.

**This isn't just about code.**
The harness model translates to how we build AI products too.

---

# What I Built Over Christmas

```
amplify/
  config/AGENTS.md     # Template → installed as CLAUDE.md
  skills/              # On-demand expertise  
  agents/              # Specialized workers
  commands/            # Workflow templates
```

A harness that shapes how I work with agents.

---

# The Problems I Hit

Building this, I kept hitting the same walls:

1. Agent built the wrong thing (vague requirements)
2. Agent built too much, too fast (lost oversight)
3. Agent couldn't verify its work (no feedback)
4. Long sessions degraded (context limits)

Sound familiar?

---

# The Ralph Loop

Named after Ralph Wiggum. "I'm helping!"

A pattern for autonomous agent work:

```
┌─────────────────────────────────────────┐
│                                         │
│   READ → PLAN → IMPLEMENT → VERIFY      │
│     ↑                          │        │
│     └──── COMMIT & UPDATE ─────┘        │
│                                         │
└─────────────────────────────────────────┘
```

One atomic task. Verify. Persist learnings. Repeat.

---

# Ralph Loop: External Memory

The agent reads/writes three files:

| File | Purpose |
|------|---------|
| `SPEC.md` | Requirements and acceptance criteria |
| `PLAN.md` | Tasks, progress, current context |
| `CLAUDE.md` | Long-term memory (patterns, lessons) |

**Memory lives outside the conversation.**

Context degrades? Read the files. Start fresh.

---

# Ralph Loop: The Workflow

```
1. INTERVIEW
   - Gather requirements
   - Write SPEC.md with acceptance criteria

2. PLAN
   - Break spec into atomic tasks
   - Write PLAN.md

3. EXECUTE (repeat for each task)
   - Read CLAUDE.md, PLAN.md, SPEC.md
   - Implement one task
   - Verify (run tests)
   - Commit, mark complete, persist learnings
```

---

# Why This Works

Each step solves one of these problems:

| Problem | Ralph Loop Solution |
|---------|---------------------|
| Vague requirements | Acceptance criteria in SPEC.md |
| Too fast, no oversight | One atomic task per iteration |
| No feedback loop | Verify step before commit |
| Context degradation | External memory files |

This is the shape of the harness.

---

# Problem 1: Vague Requirements

```
"Add authentication"
```

Agent produces 800 lines. Wrong auth method.
Wrong token storage. Wrong session handling.

It reasoned correctly from what you gave it.

**You gave it nothing.**

---

# The Fix: Structured Interviewing

Before any code, gather requirements:

```
1) Auth method?
   a) Email/password only
   b) OAuth (Google, GitHub)  
   c) Both (recommended)

2) Token storage?
   a) HTTP-only cookie (recommended)
   b) localStorage

Reply: 1c 2a (or describe)
```

Easy to answer. Hard to misunderstand.

---

# The Specification Pipeline

```
interview -> create-spec -> create-plan -> execute
    |            |              |            |
  gather      SPEC.md        PLAN.md      one task
  requirements (what)        (how)        at a time
```

Each stage produces a **file**.

Files survive. Conversations don't.
Archive completed specs to `specs/`.

---

# Aside: Why Files, Not Linear?

Why not keep specs and plans in the cloud?

**The cloud is dead for agents.**

Agents are fast at reading and writing local files.
They're slow and clumsy with APIs and web UIs.

Keep the source of truth where the agent lives.

---

# Problem 2: Too Fast, No Oversight

Agent produces 500 lines across 6 files.

You can't review that in real-time.
You can't verify it until it's done.
By then, it's already broken something.

---

# The Fix: One Task at a Time

The `execute-plan` skill enforces discipline:

1. Find first unchecked task in PLAN.md
2. Research before coding
3. Implement just that task
4. Run tests
5. Mark complete with summary
6. **Stop. Report. Wait.**

Human stays in the loop.

---

# Problem 3: No Feedback Loop

Agent finishes. Says "done."

Is it actually done? Does it work?
Did it break something else?

Without verification, you're just hoping.

---

# The Fix: Tests Are Not Optional

Every task that changes behavior needs tests.

```markdown
- [ ] Run format, lint, and tests (all must pass)
```

Before marking complete:
- `mix format`
- `mix credo`  
- `mix test`

**Trust is a passing test suite.**

---

# Problem 4: Context Degradation

Long sessions get weird.

Agent forgets constraints. Contradicts itself.
Hallucinates patterns from 2000 tokens ago.

The context window is finite. Use it wisely.

---

# The Fix: External Memory

Keep the source of truth in files:

- `SPEC.md` for requirements
- `PLAN.md` for tasks and current state
- `CLAUDE.md` for learnings and constraints

When context drifts, reread and reset.

---

# The Primitives

Let me show you what I built.

---

# Primitive 1: CLAUDE.md

The agent's **mindset and constraints**.

Always loaded. Shapes every response.

```
$HOME/.claude/CLAUDE.md    # Your global prefs
./CLAUDE.md                # Project-specific
```

(`make` installs the template as CLAUDE.md)

---

# CLAUDE.md: Core Mindset

```markdown
## Core Mindset

- **Understand before acting**. Think deeply.
- **The best code is no code**. Simplest solution.
- **Fix root causes, not symptoms**.
- **Optimize for the reader**.
- **Leave the codebase better**.
```

This is the "don't be stupid" section.

---

# CLAUDE.md: Clarification

```markdown
## Clarification & Scope

- **Interview me when unclear**. Ask questions
  until it is crystal clear.
- **Stay focused**. Do the task you were asked.
- **Know when to proceed**. Low-risk? Go.
  High-risk? Ask first.
```

Permission to ask questions. Boundaries on scope.

---

# CLAUDE.md: Testing

```markdown
## Testing Philosophy

- **No mocks**. Unit tests or e2e, nothing between.
- **Test behavior, not implementation**.
- **Run only what you touch**.
```

Opinionated. But opinions create consistency.

---

# The Three Memory Scopes

Knowledge needs to persist at different levels.

| Scope | File | Lifetime |
|-------|------|----------|
| **Global** | `$HOME/.claude/CLAUDE.md` | Forever |
| **Project** | `./CLAUDE.md` | Project life |
| **Plan** | `./PLAN.md` | Until done |

When a plan completes, learnings graduate upward.

---

# Primitive 2: Skills

On-demand expertise. Loaded by trigger phrases.

```
skills/
  interview/                    # Deep requirements
  create-spec/                  # Write SPEC.md
  create-plan/                  # Write PLAN.md
  execute-plan/                 # Work through plan
  write-test/                   # Coverage-guided testing
  session-reviewer/             # Extract learnings
  ask-questions-if-underspecified/
```

Agent sees the description, decides to load.

---

# Skill Anatomy

```
skills/interview/SKILL.md
```

```yaml
name: interview
description: Deep requirements gathering.
  Triggers on "interview me", "spec this out",
  "help me think through this".
```

The description is everything. It's all the agent sees
when deciding whether to load a skill.

---

# Writing a Skill

```
skills/<name>/
  SKILL.md              # Frontmatter + instructions
  scripts/              # Executable code (optional)
  references/           # Docs loaded on-demand (optional)
```

Key rules:
- **Trigger phrases in description** - only way the agent finds it
- **Keep SKILL.md lean** - detailed docs go in `references/`

Okay, let's open up a skill and walk through it.

---

# Skill: execute-plan

The workhorse. Enforces the discipline.

```markdown
- [ ] Read PLAN.md, find first unchecked task
- [ ] Research: read relevant code
- [ ] Split task if too large
- [ ] Ask clarifying questions
- [ ] Implement the change
- [ ] Write tests
- [ ] Run format, lint, tests
- [ ] Persist learnings
- [ ] Mark complete with summary
- [ ] Report to user, stop
```

---

# Primitive 3: Agents (Subagents)

Specialized workers with their own config.

```
agents/
  create-plan.md      # Uses high reasoning
  execute-plan.md     # Uses opus for execution
  code-simplifier.md  # Cleanup specialist
  plan-reviewer.md    # Validates before execution
  tech-docs-writer.md # Documentation
```

Different models for different jobs.

---

# Agent Configuration

```yaml
name: create-plan
description: Create a plan for a coding task...
model: codex
reasoningEffort: high
```

Body: `Load and follow the create-plan skill.`

Agents delegate to skills for instructions.

---

# Model Selection Matters

Different models for different jobs:

| Task | Model | Why |
|------|-------|-----|
| Planning | OpenAI | Better at structured reasoning |
| Execution | Opus | Stronger at code generation |
| Quick edits | Sonnet | Fast, cheap, good enough |

Match the model to the cognitive task.

---

# Primitive 4: Commands

Workflow templates. Invoked with `/command`.

```
commands/
  smart-commit.md   # Group changes into atomic commits
  commit.md         # Simple commit helper
```

Repeatable workflows you don't want to explain.

---

# Session Reviewer

At end of session, extract what matters:

1. **Friction points** - what was harder than expected?
2. **Discoveries** - commands, patterns, gotchas
3. **Decisions** - why I chose X over Y

Persist to the right loop. Don't lose it.

---

# What Changed For Me

Before: React to whatever the agent does.

After: Lead. Specify. Verify. Learn.

The agent is the same.
**The harness makes the difference.**

---

# Build Together

Imagine what we can do if we build the harness together.

Continuously improving skills for everybody.

---

# Skills We Could Build

Ideas to get us started:

- **PR Description Writer** - consistent, high-quality PR summaries
- **Product Agent** - knows mission/vision, aligns features as we build
- **Brand Agent** - enforces voice and tone across the product
- **Onboarding Guide** - helps new engineers ramp up on the codebase
- **Migration Planner** - structured approach to large refactors

What's slowing you down? That's your first skill.

---

# Next Steps

Work together on our own agentic harness.

- I'll send a PR upgrading our agentic harness for Workera
- Shared skills live in workera_webapps
- When you hit friction, add or adapt a skill

```bash
# Run this presentation
brew install slides
slides docs/presentation.md

# Explore the repo
ls skills/
cat config/AGENTS.md
```
