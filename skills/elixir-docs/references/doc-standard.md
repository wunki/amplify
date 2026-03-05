# Elixir Documentation Standard

Paste this entire section into every tech-docs-writer agent prompt.

---

## Module docs (`@moduledoc`)

The first paragraph is the **summary line**. ExDoc uses it in module listings, hex.pm search results, and `h Module` in IEx. Write one sentence that stands alone.

After the summary, answer 6 questions using bold headers or `##` sections. Keep each section 1-4 lines.

1. **Role in flow** — where this module fits in the system (e.g., which pipeline stage, what calls it, what it calls).
2. **Owns what** — the data or behavior it is responsible for. Name the struct, field, or side effect.
3. **Reads / Writes** — exact fields, keys, or inputs read and outputs written. Use a table or bullet list. Be specific: `ctx.metadata[:agent_result]`, not "metadata".
4. **Failure behavior** — how failures/degradation are represented (`{:error, reason}`, fallback value, skip). What does the caller see? Name the error shapes and boundary behavior explicitly.
5. **Observability** — telemetry events emitted, reason codes produced, turn events appended. If none, say "None — pure function" or "None — delegates to X".
6. **Non-goals** — what this module explicitly does not do. Name the module that handles it instead.

## Public function docs (`@doc`)

The first sentence is the summary. ExDoc shows it in the function listing sidebar.

After the summary, include:

- Input contract (required fields, expected shape).
- Return contract (`{:ok, ctx}` / `{:error, reason}` / `map()` etc).
- Side effects (telemetry emission, event appending, I/O).
- Failure/degradation semantics.

For pure functions with clear contracts, add a **doctest**:

```elixir
@doc """
Normalize an optional text value.

Returns the trimmed string, or `nil` for blank/non-string input.

## Examples

    iex> normalize_optional_text("  hello  ")
    "hello"

    iex> normalize_optional_text("")
    nil

    iex> normalize_optional_text(42)
    nil
"""
```

Doctests are compiled and run as tests by ExUnit. Only add them for pure functions where the example is genuinely useful. Do not add doctests for functions with side effects or complex setup.

## Type docs (`@typedoc`)

- Field meanings and invariants.
- Valid values for enum-like fields (atoms, string constants).
- Which fields are optional vs required.
- What "nil" means for optional fields (not yet populated vs intentionally absent).

## ExDoc features to use

**Cross-references:** Link to modules and functions using ExDoc auto-linking syntax. ExDoc converts these to clickable links in hexdocs and preserves them as readable text in `h` shell output.

- `Foo.Bar` — links to module
- `Foo.Bar.baz/2` — links to function
- `c:GenServer.init/1` — links to callback
- `t:String.t/0` — links to type

Use these instead of backtick-only references. Write `see `Pipeline.run/2`` not `see the run function in Pipeline`.

**Admonitions:** Use for warnings or important notes that must stand out:

```markdown
> #### Warning {: .warning}
>
> This function is called from test stubs. Changing its signature
> is a breaking change for test infrastructure.

> #### Note {: .info}
>
> This struct is immutable once produced. All fields are set at
> construction time.
```

Use sparingly. One per doc block at most.

**Metadata:** Use `@doc since:` for functions added after v1.0, and `@doc deprecated:` for functions being phased out:

```elixir
@doc since: "1.4.0"
@doc deprecated: "Use Gate.run/1 instead"
```

## Audience

Write for **an engineer who joined the team this week**. They know Elixir but not this codebase. Every term, acronym, or module reference that isn't in the Elixir standard library needs either a cross-reference link or a one-line explanation on first use.

The Curse of Knowledge is real: once you understand a system, you forget what was confusing. Fight it by asking "would I understand this sentence if I had never seen this module before?"

## Reference vs Explanation

`@moduledoc` and `@doc` are **reference documentation**. They answer "what does this do?" and "how do I call it?" concisely and completely.

They are NOT the place for:

- **Explanations** of why the system is designed this way (put those in `docs/` guides)
- **Tutorials** walking through a use case step by step
- **How-to guides** for common tasks

If you find yourself writing more than 4 lines of narrative context in a `@moduledoc`, extract it to a guide in `docs/` and cross-reference it: `See the [Answer Pipeline guide](docs/how-ampi-answers.md) for architectural context.`

## Style rules

- **Summary first.** The first sentence must work standalone in a module listing, IEx `h` output, and hex.pm search.
- **Third-person imperative.** "Runs the pipeline" not "This module runs the pipeline".
- **Lead with the verb.** Not "This module is responsible for..." or "A module that...".
- **Prefer "why + contract" over implementation narration.** Say what it guarantees, not how it does it.
- **Document only public APIs.** Do not add `@doc` to private functions. Use `@doc false` for public functions that are internal implementation details.
- **Keep docs current.** Wrong docs are worse than no docs. Update docs in the same change that modifies behavior. Stale docs actively mislead, which is worse than no docs at all.
- **Plain text friendly.** Docs are read in IEx with `h/1` as much as in hexdocs. Don't rely on HTML rendering for comprehension.

## Definition of done

A first-time engineer opens any documented module and answers these in under 60 seconds, whether reading hexdocs or running `h Module` in IEx:

- What does this module do?
- What inputs does it need?
- What outputs does it guarantee?
- How can it fail or degrade?
- What telemetry/reason codes should I expect?

### Friction log test

After writing docs, do a cold read. Open the module as if you have never seen it. Try to answer: "Can I call this function safely right now?" If you need to read the source code to answer that, the docs are incomplete.
