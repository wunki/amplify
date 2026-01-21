# Amplify

Skills and configuration for AI coding agents. Works with Claude Code, OpenCode, Codex, and Amp.

## What's Inside

### Skills

| Skill | What It Does |
|-------|--------------|
| **ask-questions-if-underspecified** | Requirement clarification. Ask focused questions before implementing. |
| **browse-site** | Browser automation using agent-browser CLI. Navigate, click, fill forms, screenshot, scrape. |
| **create-plan** | Generate concise implementation plans. Scope, action items, open questions, documentation links. |
| **create-spec** | Create or update SPEC.md from requirements, notes, or interview output. Structures information into consistent spec format. |
| **execute-plan** | Work through PLAN.md one task at a time. Questions before action, summaries after, learning persistence. |
| **frontend-design** | Build distinctive, production-grade interfaces that don't look like AI slop. Opinionated about typography, color, motion, and spatial composition. |
| **gh-file** | Fetch source code from GitHub URLs. Supports line ranges, directories, and full repo clones via `gh` CLI. |
| **guide** | Interactive teaching mode. Orchestrates clarification, planning, and guided execution. |
| **interview** | Deep requirements gathering through exhaustive questioning. Hands off to create-spec or create-plan when complete. |
| **roadmap** | Create a ROADMAP.md for open source projects. Vision, milestones, timeline (Now/Next/Later/Future). Follows open source conventions. |
| **session-reviewer** | Extract learnings from sessions. Persists personal preferences globally, project knowledge locally. |
| **skill-creator** | Meta-skill for building new skills. Structure, progressive disclosure, bundled resources. |
| **solveit** | Generate structured learning guides using the Pólya problem-solving method. Self-contained documents for building features. |
| **stop-slop** | Remove AI writing patterns from prose. Eliminate filler phrases, formulaic structures, and predictable AI tells. |
| **web-perf** | Performance auditing via Chrome DevTools MCP. Core Web Vitals, render-blocking resources, network waterfalls, accessibility gaps. |
| **write-test** | Write meaningful tests using coverage as a guide. Prioritizes real user workflows over implementation details. |

### Commands

| Command | What It Does |
|---------|--------------|
| **/commit** | Generate conventional commit messages from staged changes |
| **/smart-commit** | Analyze unstaged changes, group into atomic commits, generate messages for each |

### Agents

| Agent | What It Does |
|-------|--------------|
| **code-simplifier** | Simplifies and refines code for clarity and maintainability. Focuses on recently modified code. |
| **create-plan** | Create implementation plans through interviewing. Thinks deeply before planning. |
| **execute-plan** | Execute PLAN.md tasks one at a time with human oversight. |
| **plan-reviewer** | Deep analysis of PLAN.md before execution. Validates against codebase, checks task decomposition, identifies risks. |
| **tech-docs-writer** | Technical writer that transforms codebases into clear documentation. README files, API docs, architecture guides. |

### Scripts

| Script | What It Does |
|--------|--------------|
| **wiggum** | Autonomous coding loop (Ralph Wiggum technique). Iterates through a plan until complete. |

## Skill Workflows

### Guided Learning: guide → ask-questions → create-plan

The **guide** skill orchestrates a full learning workflow:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              guide skill                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Clarify  │───▶│   Plan   │───▶│  Teach   │───▶│ Archive  │          │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘          │
│       │               │               │               │                 │
│       ▼               ▼               ▼               ▼                 │
│  ask-questions   create-plan     Guide through   history/YYYY-MM-DD-   │
│  skill           workflow        each item       plan-<name>.md        │
│                  ─▶ PLAN.md      with hints                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

1. **Clarify** — Uses ask-questions to gather requirements one at a time (voice-friendly)
2. **Plan** — Creates PLAN.md with action items, scope, and documentation links
3. **Teach** — Guides you through each step with hints, not solutions
4. **Archive** — Moves completed plan to `history/YYYY-MM-DD-plan-<name>.md`

For standalone planning without teaching, use **create-plan** directly.

### Autonomous Execution: wiggum

The **Ralph Wiggum technique** lets you run an AI agent in a loop until work is complete. Based on [Geoffrey Huntley's methodology](https://ghuntley.com/ralph/).

Wiggum supports two modes:

#### Plan Mode (default)

Uses a `PLAN.md` file with checkboxes. Exits when all `[ ]` become `[x]`.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Plan Mode Loop                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │  Plan    │───▶│  Pick    │───▶│ Complete │───▶│  Commit  │──┐       │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │       │
│       │               │               │               │        │       │
│       ▼               ▼               ▼               ▼        │       │
│  create-plan     ONE task        Verify via       git commit   │       │
│  ─▶ PLAN.md      from plan       tests/lint       (no push)   │       │
│                                                                 │       │
│                  ◀──────────────────────────────────────────────┘       │
│                       Loop until all tasks [x] complete                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Step 1: Create a plan**

```bash
amp "create a plan for adding user authentication"
# or
claude "create a plan for adding user authentication"
```

**Step 2: Run the loop**

```bash
wiggum PLAN.md                      # Interactive (confirm each task)
wiggum --auto PLAN.md               # Autonomous (let it run)
wiggum --auto --max 20 PLAN.md      # With iteration limit
```

#### Promise Mode

Uses a prompt string. Exits when Claude outputs `<promise>DONE</promise>`.

Best for well-defined, verifiable tasks without a plan file:

```bash
# Fix lint errors until clean
wiggum --prompt "Fix all ESLint errors. Run npm run lint to verify."

# Make tests pass
wiggum --auto --prompt "Make all tests in src/auth pass" --promise "TESTS_PASS"

# Refactor with verification
wiggum --prompt "Convert all class components to functional components"
```

**How it works:** Each iteration, Claude sees the current codebase state (including changes from previous iterations). The codebase carries the progress, even though each Claude instance is stateless.

#### Options

| Flag | Description |
|------|-------------|
| `-a, --auto` | Auto-continue without confirmation |
| `-m, --max N` | Maximum iterations (cost control) |
| `--prompt TEXT` | Task prompt (enables promise mode) |
| `--promise TEXT` | Completion signal (default: `DONE`) |

#### Key Behaviors

- **Stateless iterations** — Each run re-reads full context, preventing drift
- **Plan evolution** — Claude updates the plan when reality diverges (splits tasks, adds blockers)
- **Operational learning** — Discoveries are written to AGENTS.md for future iterations
- **Safe commits** — Commits after each task, never pushes (you review and push)

#### Philosophy

> "If Ralph falls off the slide, you don't just put him back — you put up a sign that says 'SLIDE DOWN, DON'T JUMP.'"

Each failure teaches what guardrails to add. Tune the plan, tune AGENTS.md, iterate.

### Manual Execution: execute-plan

For **human-in-the-loop** execution where you want oversight and learning:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Manual Execution Flow                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐                    │
│  │create-plan │───▶│execute-plan│───▶│execute-plan│───▶ ... ───▶ Done │
│  └────────────┘    └────────────┘    └────────────┘                    │
│        │                 │                 │                 │          │
│        ▼                 ▼                 ▼                 ▼          │
│    PLAN.md          Task 1 done       Task 2 done       Archive spec to│
│    created          + summary         + summary         specs/         │
│                                                                         │
│  Human triggers each step. Reviews. Commits when ready.                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Workflow:**

1. Create a plan: `"create a plan for adding OAuth support"`
2. Execute tasks one at a time: `"execute the plan"` or `"continue the plan"`
3. Agent asks clarifying questions before acting
4. After each task: marks `[x]` and adds inline summary
5. Commit when ready: `/smart-commit`
6. Repeat until done, then archive `SPEC.md` to `specs/YYYY-MM-DD-<title>.md` and remove `PLAN.md`

**Key behaviors:**

- **Questions first** — Unlike wiggum, asks before acting (human is present)
- **One task at a time** — Complete focus, then hand back control
- **Learning persistence** — Updates AGENTS.md with project conventions discovered
- **Documentation updates** — Checks `docs/` and updates if building user-facing features
- **Plan mutations** — Splits tasks, adds blockers, restructures as needed

**When to use which:**

| Scenario | Use |
|----------|-----|
| Well-defined tasks, want speed | `wiggum --auto` |
| Learning a new codebase | `execute-plan` |
| Complex decisions needed | `execute-plan` |
| Repetitive refactoring | `wiggum` |
| Building new features | `execute-plan` |

### Learning Loops: session-reviewer

Knowledge gets lost between sessions. The **session-reviewer** skill extracts learnings and persists them so future sessions start smarter.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Three Learning Loops                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   GLOBAL LOOP          PROJECT LOOP           PLAN LOOP                 │
│   (all projects)       (this project)         (this feature)            │
│                                                                         │
│   ┌─────────────┐      ┌─────────────┐       ┌─────────────┐            │
│   │ ~/.claude/  │      │  CLAUDE.md  │       │   PLAN.md   │            │
│   │  CLAUDE.md  │      │             │       │             │            │
│   └──────┬──────┘      └──────┬──────┘       └──────┬──────┘            │
│          │                    │                     │                   │
│          │ prefs              │ knowledge           │ context           │
│          ▼                    ▼                     ▼                   │
│        ┌─────────────────────────────────────────────────┐              │
│        │                    SESSION                      │              │
│        │                                                 │              │
│        │     Work → Friction → Discovery → Preferences   │              │
│        │                                                 │              │
│        └──────────────────────┬──────────────────────────┘              │
│                               │                                         │
│                               ▼                                         │
│                    ┌─────────────────────┐                              │
│                    │  /session-reviewer  │                              │
│                    │   (extract & route) │                              │
│                    └─────────┬───────────┘                              │
│                              │                                          │
│          ┌───────────────────┼───────────────────┐                      │
│          │                   │                   │                      │
│          ▼                   ▼                   ▼                      │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│   │  "Prefer    │     │ "Run make   │     │ "Task 3     │               │
│   │   early     │     │  test-unit" │     │  needs auth │               │
│   │   returns"  │     │             │     │  first"     │               │
│   └──────┬──────┘     └──────┬──────┘     └──────┬──────┘               │
│          │                   │                   │                      │
│          ▼                   ▼                   ▼                      │
│    All future          This project's       This plan's                 │
│    sessions            sessions             remaining tasks             │
│                                                                         │
│   ◀──────────────── loops continue ────────────────▶                    │
│                                                                         │
│   When plan completes, learnings graduate upward:                       │
│   plan discovery → project knowledge → global preference                │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Run at session end:** `/session-reviewer` or "review this session"

**Three nested loops:**

| Loop | Storage | Scope | Lifetime | What it captures |
|------|---------|-------|----------|------------------|
| **Global** | `~/.claude/CLAUDE.md` | All projects | Forever | Coding style, communication, workflow |
| **Project** | `CLAUDE.md` | This project | Life of project | Commands, gotchas, patterns |
| **Plan** | `PLAN.md` | This feature | Until archived | Task deps, blockers, discoveries |

**How to route learnings:**
- "I prefer X" or style correction → **Global** (applies everywhere)
- "This codebase does Y" → **Project** (specific to this repo)
- "Task 3 needs X first" → **Plan** (relevant to current work)

**Graduation:** When a plan completes, review its learnings. Discoveries useful beyond this feature should promote to project CLAUDE.md. Preferences that apply everywhere should promote to global config.

**Also outputs** (one-way, not loops):
- `docs/` — User-facing documentation when features complete

The skill presents recommendations and waits for approval before making changes.

## Installation

### Claude Code (Plugin Marketplace)

Add the marketplace and install specific skills:

```bash
# Add the marketplace (one time)
/plugin marketplace add wunki/amplify

# Install individual skills
/plugin install dev-browser@amplify
/plugin install frontend-design@amplify
/plugin install web-perf@amplify
```

Or install everything at once:

```bash
/plugin install wunki/amplify
```

### Local Installation (All Tools)

Clone and run `make` to install for all detected tools:

```bash
git clone https://github.com/wunki/amplify.git
cd amplify
make
```

This detects which tools you have installed (Claude Code, OpenCode, Codex, Amp) and copies skills, commands, and configuration to each.

To install for a specific tool only:

```bash
make claude    # Claude Code only
make opencode  # OpenCode only
make codex     # Codex only
make amp       # Amp only
```

### Codex

Use the skill installer:

```bash
$skill-installer wunki/amplify/dev-browser
$skill-installer wunki/amplify/frontend-design
```

### Amp

Amp reads skills from `.agents/skills/` in your workspace. Either:

1. Run `make amp` to install to `~/.config/amp/skills/`
2. Or copy skills directly to your project's `.agents/skills/` directory

## Skill Locations by Tool

| Tool | Skills Directory | Commands Directory |
|------|------------------|-------------------|
| Claude Code | `~/.claude/skills/` | `~/.claude/commands/` |
| OpenCode | `~/.config/opencode/skills/` | `~/.config/opencode/command/` |
| Codex | `~/.codex/skills/` | `~/.codex/commands/` |
| Amp | `~/.config/amp/skills/` | `~/.config/amp/commands/` |

## Configuration

The `config/` directory contains tool-specific settings:

```
config/
├── AGENTS.md           # Shared agent profile (symlinked to all tools)
├── amp/
│   └── settings.json
├── codex/
│   └── config.toml
└── opencode/
    ├── opencode.json
    └── themes/
```

`config/AGENTS.md` is the shared agent profile that gets symlinked to each tool's configuration directory. Edit it once, changes propagate everywhere.

## Adding Your Own

### New Skill

1. Create `skills/<name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What it does. Include trigger phrases for auto-activation.
   ---
   ```
2. Add `scripts/` for executable code, `references/` for on-demand docs
3. Run `make`

### New Command

1. Create `commands/<name>.md` with frontmatter:
   ```yaml
   ---
   description: What the command does
   ---
   ```
2. Add step-by-step instructions
3. Run `make`

## How It Works

**Config files** are symlinked (changes propagate immediately).

**Skills and commands** are rsynced (run `make` after changes).

The Makefile auto-discovers skills in `skills/` and commands in `commands/`, then distributes them to each tool's expected location.

## Cross-Tool Compatibility

All three major tools use the same `SKILL.md` format with YAML frontmatter. The only difference is directory location. This repo handles that by:

1. Storing skills once in `skills/`
2. Using `make` to copy to each tool's directory
3. Providing a Claude Code marketplace for plugin-based installation

| Feature | Claude Code | Codex | Amp |
|---------|-------------|-------|-----|
| Skill format | SKILL.md | SKILL.md | SKILL.md |
| Plugin system | Yes (marketplace) | Yes ($skill-installer) | No |
| Config file | CLAUDE.md | AGENTS.md | AGENTS.md |

## Presentation

There's a slide deck in `docs/presentation.md` that explains the philosophy behind this repo. Run it with [slides](https://github.com/maaslalani/slides):

```bash
brew install slides
slides docs/presentation.md
```

## License

MIT. Individual skills may have their own licenses (see LICENSE.txt in skill directories).
