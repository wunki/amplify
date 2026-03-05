---
name: system-simplifier
description: >-
  Analyze a codebase or module namespace for structural simplification opportunities.
  Finds dead code, shallow abstractions, misplaced concerns, unnecessary indirection,
  and complected state. Produces a classified report of findings with recommended actions.
  Use when asked to "simplify this system", "reduce complexity", "clean up architecture",
  "find dead code", "flatten this", "what can I delete", or when a namespace feels too large.
  Don't use for single-function refactors, formatting, or performance optimization.
  Don't use for planning or execution — hand off to create-plan and execute-plan.
---

# System Simplifier

Analyze a codebase namespace for structural simplification opportunities. Produce a classified report of findings with recommended actions. Hand off to `create-plan` for planning and `execute-plan` for execution.

## Core Principles

Read `references/principles.md` now. It contains the design principles that drive every recommendation.

## Workflow

### 1. Scope the Target

Determine what to analyze. Ask the user if unclear.

- A module namespace (`lib/my_app/billing/`)
- A pipeline or data flow (request -> process -> response)
- A specific struct or data shape that feels too large

### 2. Map the Territory

Before proposing changes, understand what exists.

**Module census:** List every module in the namespace with line counts.

```bash
find lib/path -name '*.ex' -exec wc -l {} + | sort -n
```

**Dependency graph:** For each module, grep for who imports, aliases, or calls it.

```bash
grep -r 'alias MyApp.Billing' lib/ --include='*.ex' -l
```

**Dead code scan:** Find modules, functions, or fields with no callers.

```bash
# Elixir-first: use compiler-aware references before text search
mix xref callers MyApp.Billing
mix xref graph --label compile

# Supplement with text search for dynamic callsites/tests
grep -r 'ModuleName.function_name' lib/ test/ --include='*.ex' --include='*.exs' -l
```

Then check for dynamic usage that static scans can miss:

- Behaviour and protocol implementations
- `apply/3`, `Module.concat/2`, and runtime dispatch
- External/public API entrypoints used by other apps

**Struct field audit:** For each struct, check which fields are actually read.

```bash
grep -r 'ctx\.field_name\|:field_name' lib/ --include='*.ex' -l
```

### 3. Classify What You Find

Categorize each finding using the complexity taxonomy:

| Category | Signal | Action |
|----------|--------|--------|
| **Dead code** | No callers in lib/ or test/ | Delete |
| **Write-only fields** | Set but never read | Delete |
| **Shallow module** | 1-2 functions, single caller | Inline into caller |
| **Pass-through function** | Wraps another call with no added value | Inline or delete |
| **Misplaced concern** | Function lives far from its only consumers | Move to natural owner |
| **Unnecessary indirection** | Intermediate data structure rebuilt from source | Derive on demand |
| **Nested state** | Sub-struct accessed through parent everywhere | Flatten into parent |
| **God module** | Mixed responsibilities and frequent unrelated edits (line count is a signal, not a verdict) | Split by responsibility seams |
| **Synthetic compatibility** | Adapter maps between old and new shapes | Delete old shape |
| **Dead configuration** | Config keys read but never affect behavior | Delete |

### 4. Report Findings

Present findings grouped by category. For each finding:

- **What:** the specific module, function, field, or pattern
- **Why it's complexity:** which principle it violates (reference `principles.md`)
- **Recommended action:** delete, inline, move, flatten, or extract
- **Risk:** low (dead code deletion), medium (moving concerns), high (data shape changes)
- **Evidence:** exact search/xref output or code references that support the claim
- **Confidence:** high (multiple strong signals), medium (partial signals), low (heuristic only)
- **Blast radius:** files/modules likely affected by change

Use this compact format:

```md
- Finding: <short title>
  What: <module/function/field>
  Why: <violated principle>
  Evidence: <xref/grep/code refs>
  Action: <delete|inline|move|flatten|extract>
  Risk: <low|medium|high>
  Confidence: <high|medium|low>
  Blast radius: <estimated files/modules>
```

Order the report by risk: low-risk findings first (easy wins), high-risk last.

**Recommended phase ordering** when the user is ready to plan:

1. Delete dead things (lowest risk)
2. Flatten and inline (remove indirection)
3. Move misplaced concerns
4. Simplify data shapes
5. Clean observability (dead metrics, events, codes)
6. Rename (highest blast radius, do last)

### 5. Hand Off

After presenting findings, suggest the user run `create-plan` to turn the report into an executable plan, and `execute-plan` to work through it.

## Red Flags

These patterns are complexity hotspots worth investigating:

- **A module exists "for future use"** — likely dead weight; verify usage, then delete.
- **A function that takes 5+ parameters** — often a boundary smell; check if data is complected.
- **An "options" map passed through 3+ layers** — likely leaking concerns across boundaries.
- **A "normalize" function that handles many input shapes** — usually producer inconsistency.
- **A struct with many fields** — often multiple concerns sharing one bag.
- **Comments explaining what the code does** — the code should say that; comments explain why.
- **A retry/fallback wrapper around a function that never fails** — validate failure modes, then remove.
- **An alias used once** — usually unnecessary; inline or move code closer.
- **A test helper that's more complex than the code it tests** — simplify helper and production code.

## What This Skill Does NOT Do

- Write plans (use `create-plan`)
- Execute changes (use `execute-plan`)
- Performance optimization (use profiling tools)
- Single-function refactoring (use `code-simplifier`)
- Adding features or capabilities
- Rewriting working code for style preferences
