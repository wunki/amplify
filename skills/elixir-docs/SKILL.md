---
name: elixir-docs
description: >-
  Document Elixir modules to a strict 6-question standard using the tech-docs-writer agent.
  Writes @moduledoc, @doc, and @typedoc annotations answering Role in flow, Owns what,
  Reads/Writes, Failure behavior, Observability, and Non-goals. Uses ExDoc conventions
  (cross-references, admonitions, doctests, summary lines). Parallelizes across modules.
  Use when asked to "document modules", "add moduledocs", "write elixir docs", "doc standard",
  or when Elixir modules need consistent, engineer-facing documentation.
  Don't use for README files, user guides, API docs, or non-Elixir projects.
---

# Elixir Module Documentation

Write `@moduledoc`, `@doc`, and `@typedoc` annotations for Elixir modules following a strict 6-question standard and ExDoc conventions. Delegate to the `tech-docs-writer` agent for the actual writing.

## When to Use

- User asks to document one or more Elixir modules
- User wants consistent doc quality across a namespace
- Modules have thin or missing `@moduledoc`

## Workflow

### 1. Identify Targets

Determine which modules need documentation.

- If the user names specific modules, use those.
- If the user says "all modules in X", scan the directory:

```bash
find lib/path/to/namespace -name '*.ex' | sort
```

Audit current doc quality to find gaps:

```bash
while IFS= read -r -d '' f; do
  missing=0
  grep -q 'Role in flow' "$f" || missing=1
  grep -q 'Owns what' "$f" || missing=1
  grep -q 'Reads / Writes' "$f" || missing=1
  grep -q 'Failure behavior' "$f" || missing=1
  grep -q 'Observability' "$f" || missing=1
  grep -q 'Non-goals' "$f" || missing=1
  [ "$missing" -eq 1 ] && echo "NEEDS DOCS: $f"
done < <(find lib/path -name '*.ex' -print0)
```

If you already have a known target list, validate only those files to avoid noise from unrelated modules.

```bash
# one file path per line
while IFS= read -r f; do
  missing=0
  grep -q 'Role in flow' "$f" || missing=1
  grep -q 'Owns what' "$f" || missing=1
  grep -q 'Reads / Writes' "$f" || missing=1
  grep -q 'Failure behavior' "$f" || missing=1
  grep -q 'Observability' "$f" || missing=1
  grep -q 'Non-goals' "$f" || missing=1
  [ "$missing" -eq 1 ] && echo "NEEDS DOCS: $f"
done < targets.txt
```

### 2. Group for Parallelism

Group modules by domain proximity (3-7 modules per agent). Modules that reference each other belong in the same group so the agent can read context.

Good groupings:
- Pipeline stages that share a Context struct
- A parent module and its sub-modules
- Tools that follow the same behaviour

### 3. Launch Doc Writers

For each group, launch a `tech-docs-writer` agent in the background when sub-agents are available. Include the full documentation standard in every prompt.

If sub-agents/background execution are not available, process groups sequentially in the current session using the same prompt template and quality bar.

Read `references/doc-standard.md` now. Paste the full standard into each agent prompt.

Template for agent prompts:

```
Write documentation for these modules to match the project's documentation standard:

1. `path/to/module_a.ex` — one-line role description
2. `path/to/module_b.ex` — one-line role description

[PASTE FULL DOC STANDARD FROM references/doc-standard.md]

Read each module fully. For context, also read [related modules].
Do NOT change any code logic — only documentation.
```

### 4. Verify

After all agents complete:

1. Compile: `mix compile --warnings-as-errors`
2. Run targeted tests for touched areas first (including doctests for changed modules where applicable), for example: `mix test test/my_app/billing/`
3. Run full `mix test` only when requested, or when changes are broad enough that targeted scope is unclear.
4. Spot-check strict structure (all 6 required sections):

```bash
while IFS= read -r -d '' f; do
  missing=""
  grep -q 'Role in flow' "$f" || missing="$missing Role in flow;"
  grep -q 'Owns what' "$f" || missing="$missing Owns what;"
  grep -q 'Reads / Writes' "$f" || missing="$missing Reads / Writes;"
  grep -q 'Failure behavior' "$f" || missing="$missing Failure behavior;"
  grep -q 'Observability' "$f" || missing="$missing Observability;"
  grep -q 'Non-goals' "$f" || missing="$missing Non-goals;"
  [ -n "$missing" ] && echo "MISSING: $f ->$missing"
done < <(find lib/path -name '*.ex' -print0)
```

If checking only target files:

```bash
# one file path per line
while IFS= read -r f; do
  missing=""
  grep -q 'Role in flow' "$f" || missing="$missing Role in flow;"
  grep -q 'Owns what' "$f" || missing="$missing Owns what;"
  grep -q 'Reads / Writes' "$f" || missing="$missing Reads / Writes;"
  grep -q 'Failure behavior' "$f" || missing="$missing Failure behavior;"
  grep -q 'Observability' "$f" || missing="$missing Observability;"
  grep -q 'Non-goals' "$f" || missing="$missing Non-goals;"
  [ -n "$missing" ] && echo "MISSING: $f ->$missing"
done < targets.txt
```

5. Spot-check ExDoc features: verify cross-references use `Module.function/arity` syntax, not plain backtick text.

If any module is missing sections, resume the relevant agent or launch a new one.

## ExDoc Conventions

Elixir documentation lives in BEAM files and is consumed three ways:

1. **hexdocs.pm** — rendered HTML with search, cross-linking, and styling
2. **IEx shell** — `h Module` or `h Module.function` prints plain text
3. **Editor tooltips** — LSP shows `@doc` on hover

Write docs that work well in all three. The doc standard in `references/doc-standard.md` covers the specific ExDoc features to use:

- **Summary line** — first paragraph stands alone in module listings and search
- **Cross-references** — `Pipeline.run/2`, `t:Context.t/0`, `c:GenServer.init/1` auto-link in hexdocs
- **Admonitions** — `> #### Warning {: .warning}` for callouts (use sparingly)
- **Doctests** — `iex>` examples in `@doc` run as ExUnit tests; use for pure functions only
- **Metadata** — `@doc since:`, `@doc deprecated:` rendered by ExDoc

## Quality Bar

**Audience:** An engineer who joined the team this week. They know Elixir but not this codebase.

A first-time engineer opens any documented module and answers these in under 60 seconds, whether reading hexdocs, running `h Module` in IEx, or hovering in their editor:

- What does this module do?
- What inputs does it need?
- What outputs does it guarantee?
- How can it fail or degrade?
- What telemetry or reason codes should I expect?

**Friction log test:** After all agents complete, open 2-3 documented modules cold. Try to answer "Can I call this function safely?" using only the docs. If you need to read source code, send the module back for a rewrite.

**Docs rot:** Remind agents that docs must be updated in the same change that modifies behavior. Stale docs actively mislead.

## Anti-patterns

- Do not narrate implementation ("This function iterates over..."). State the contract.
- Do not document private functions unless the logic is non-obvious.
- Do not add `@doc` to trivial accessors or delegations.
- Do not use filler phrases ("This module is responsible for..."). Lead with the verb.
- Do not add doctests for functions with side effects or complex setup requirements.
- Do not reference modules with plain backticks when ExDoc cross-reference syntax works.
- Do not write explanatory narrative in `@moduledoc`. It is reference docs, not a guide. Extract explanations to `docs/`.
