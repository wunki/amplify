---
name: elixir-docs
description: >-
  Writes production-quality @moduledoc, @doc, and @typedoc annotations for Elixir modules.
  Scales doc shape to module complexity: one-line docs for simple wrappers, multi-section
  guides with examples for core concepts. Applies ExDoc conventions including cross-references,
  admonitions, doctests, tables, options lists, and return contracts.
  Use when asked to "document modules", "add moduledocs", "write elixir docs", "doc standard",
  "add @doc", "improve documentation", or when Elixir modules have thin, missing, or
  inconsistent documentation.
  Don't use for README files, user-facing guides, ExDoc configuration, hex.pm publishing,
  mix docs generation, non-Elixir projects, or LiveBook notebooks.
---

# Elixir Module Documentation

Write `@moduledoc`, `@doc`, and `@typedoc` annotations for Elixir modules. Doc shape follows module shape: scale documentation length and structure to match the module's complexity and public surface area. Delegate to the `tech-docs-writer` agent for the actual writing.

## When to Use

- Documenting one or more Elixir modules
- Bringing consistent doc quality across a namespace
- Modules have thin or missing `@moduledoc`

## Workflow

### 1. Identify Targets

Determine which modules need documentation.

- Named modules → use those directly.
- "All modules in X" → scan the directory. For umbrella apps, check `apps/*/lib/` instead of `lib/`:

```bash
find lib/path/to/namespace -name '*.ex' | sort
```

Audit current doc quality. Check for missing `@moduledoc`, misuse of `@moduledoc false`, or thin/outdated docs:

```bash
# Find modules with no @moduledoc at all
while IFS= read -r -d '' f; do
  grep -q '@moduledoc' "$f" || echo "NO MODULEDOC: $f"
done < <(find lib/path -name '*.ex' -print0)

# Find modules with @moduledoc false that might deserve docs
grep -rl '@moduledoc false' lib/path/to/namespace/
```

Categorize each module before writing. Respect the project's existing conventions for what gets documented. If the project already uses `@moduledoc false` consistently, follow that boundary. Otherwise, use these defaults:

- **Public API** — modules developers intentionally navigate to. Full docs.
- **Internal plumbing** — query modules, helpers, framework callbacks, `*HTML` view modules. Use `@moduledoc false`.
- **Web layer** — apply the same complexity-scaling rule. Plugs with non-trivial logic, controllers with multi-step flows or significant API surface get brief docs. Boilerplate controllers, view modules, and single-action delegates stay undocumented.
- **Already well-documented** — skip unless a refresh is requested.

### 2. Read the Codebase

Before writing any docs, understand the project:

- Find well-documented modules by scanning for long `@moduledoc` blocks. Learn the project's voice and conventions from these.
- Map the module hierarchy and call graph for the target namespace.
- Note which modules emit telemetry, define behaviours, or have complex failure modes.
- Check for existing guides in `docs/` that should be cross-referenced.

Documentation that contradicts the codebase is worse than no documentation.

### 3. Group for Parallelism

Group modules by domain proximity (3-7 modules per agent). Modules that reference each other belong in the same group so the agent can read context.

Good groupings:
- Pipeline stages that share a Context struct
- A parent behaviour and its implementations
- A core module and its supporting types/exceptions
- Plugins that follow the same pattern

### 4. Launch Doc Writers

Read `references/doc-standard.md` now. Skip if the standard is already loaded in context. If the file is missing or empty, use the ExDoc conventions and quality bar sections below as the fallback standard.

For each group, launch a `tech-docs-writer` agent using the Agent tool (subagent_type: `tech-docs-writer`, run_in_background: true). Paste the full documentation standard into every agent prompt — the standard is designed to fit in a single prompt alongside the module source.

If the Agent tool is not available or background execution is not supported, process groups sequentially in the current session using the same prompt template and quality bar.

Agent prompt template:

```
Write documentation for these Elixir modules following the documentation
standard below. Read each module fully before writing. For context, also
read [list related modules the agent should understand].

Modules to document:

1. `path/to/module_a.ex` — one-line role description
2. `path/to/module_b.ex` — one-line role description

IMPORTANT:
- Do NOT change any code logic — only add or update documentation.
- Scale doc length to module complexity. Do not force structure on simple modules.
- Every public function needs at least one example.
- Use the `* :name` — description format for options.
- Use ExDoc cross-references, not plain backticks, for module/function refs.

[PASTE FULL DOC STANDARD FROM references/doc-standard.md]
```

### 5. Verify

After all agents complete:

1. Compile: `mix compile --warnings-as-errors`. If this fails due to pre-existing warnings unrelated to documentation changes, fall back to `mix compile` without `--warnings-as-errors` and note the pre-existing warnings separately.
2. Run targeted tests for touched areas (including doctests): `mix test test/my_app/billing/`. For umbrella apps, run from the appropriate app directory.
3. Run full `mix test` only when requested or when scope is unclear.
4. Spot-check documentation quality:

```bash
# Find documented modules missing examples (checks ## Example headers and iex> doctests)
while IFS= read -r -d '' f; do
  has_moduledoc=$(grep -c '@moduledoc' "$f")
  has_doc_false=$(grep -c '@moduledoc false' "$f")
  has_example=$(grep -cE '(## Example|iex>)' "$f")
  if [ "$has_moduledoc" -gt 0 ] && [ "$has_doc_false" -eq 0 ] && [ "$has_example" -eq 0 ]; then
    echo "NO EXAMPLES: $f"
  fi
done < <(find lib/path -name '*.ex' -print0)
```

5. Verify cross-references use `Module.function/arity` syntax, not plain backtick text.
6. Verify doc length matches module complexity. One-line modules get one-line docs. Core concepts get comprehensive guides.

If modules still have quality gaps after one round of fixes, flag them to the user rather than retrying indefinitely.

## ExDoc Conventions

Elixir documentation lives in BEAM files and is consumed three ways:

1. **hexdocs.pm** — rendered HTML with search, cross-linking, and styling
2. **IEx shell** — `h Module` or `h Module.function` prints plain text
3. **Editor tooltips** — LSP shows `@doc` on hover

Write docs that work well in all three. Read `references/doc-standard.md` for the full set of ExDoc features. Skip if already loaded.

Summary of key features:

- **Summary line** — first paragraph stands alone in module listings and search
- **Cross-references** — `Pipeline.run/2`, `t:Context.t/0`, `c:GenServer.init/1` auto-link in hexdocs
- **Admonitions** — `> #### Warning {: .warning}` for callouts, gotchas, and audience scoping
- **Tables** — for structured reference data like telemetry events, options, error codes
- **Doctests** — `iex>` examples in `@doc` run as ExUnit tests; use for pure functions only
- **Metadata** — `@moduledoc since:`, `@doc since:`, `@doc deprecated:` rendered by ExDoc

## Quality Bar

**Audience:** An engineer who joined the team this week. Knows Elixir but not this codebase.

A first-time engineer opens any documented module and answers these in under 60 seconds:

- What does this module do?
- How do I use it?
- What inputs does it need and what outputs does it guarantee?
- How can it fail?
- Can I call this function safely right now?

**Friction log test:** Open 2-3 documented modules cold. Answer "Can I call this function safely?" using only the docs. If source code is needed, send the module back for a rewrite.

**Docs rot:** Docs must be updated in the same change that modifies behavior. Stale docs actively mislead.

## Anti-patterns

- Narrating implementation ("This function iterates over...") — state the contract instead.
- Filler openings ("This module is responsible for...", "A module that provides...") — lead with the verb.
- Documenting private functions — skip unless the logic is genuinely dangerous.
- Adding `@doc` to trivial getters, delegations, or single-line wrappers.
- Adding doctests for functions with side effects or complex setup.
- Referencing modules with plain backticks when ExDoc cross-reference syntax works.
- Forcing multi-section structure on simple modules — a one-line wrapper does not need Usage, Options, and Examples.
- Writing docs that require reading source code to understand — if docs cannot stand alone, they are incomplete.
