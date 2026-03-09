# Elixir Documentation Standard

Paste this entire section into every tech-docs-writer agent prompt.

## Contents

- [Core Principle: Doc Shape Follows Module Shape](#core-principle-doc-shape-follows-module-shape)
- [Module docs (`@moduledoc`)](#module-docs-moduledoc)
  - [Summary line](#summary-line)
  - [Structure after the summary](#structure-after-the-summary)
  - [Scaling doc length](#scaling-doc-length)
  - [Modules that should use `@moduledoc false`](#modules-that-should-use-moduledoc-false)
  - [`@moduledoc since:`](#moduledoc-since)
- [Public function docs (`@doc`)](#public-function-docs-doc)
  - [Summary line](#summary-line-1)
  - [Body structure](#body-structure)
  - [Options format](#options-format)
  - [Return values](#return-values)
  - [Examples](#examples)
  - [Callback docs](#callback-docs)
  - [`@doc false`](#doc-false)
  - [`@doc since:` and `@doc deprecated:`](#doc-since-and-doc-deprecated)
- [Type docs (`@typedoc`)](#type-docs-typedoc)
- [ExDoc features](#exdoc-features)
  - [Cross-references](#cross-references)
  - [Admonitions](#admonitions)
  - [Metadata](#metadata)
  - [Tables](#tables)
- [Audience](#audience)
- [Style rules](#style-rules)
- [Anti-patterns](#anti-patterns)
- [Definition of done](#definition-of-done)

---

## Core Principle: Doc Shape Follows Module Shape

Documentation length and structure scale with the module's complexity and public surface area. A one-line exception wrapper gets a one-line `@moduledoc`. A core concept like a Worker behaviour gets a multi-section guide. There is no fixed template.

Before writing, run through this **pre-flight checklist** mentally. You don't need to answer every question in the docs, but you need to *know* the answers so you can decide what the reader actually needs:

1. What does this module do? (always answer this one in the docs)
2. Where does it fit in the system? What calls it, what does it call?
3. What data or behavior does it own?
4. What are the inputs and outputs? Be specific about shapes.
5. How can it fail? What does the caller see?
6. Does it emit telemetry, append events, or produce observable side effects?
7. What does this module explicitly NOT do?

Surface these answers naturally through your chosen structure. Do not use the checklist questions as section headers.

## Module docs (`@moduledoc`)

### Summary line

The first paragraph is the **summary line**. ExDoc uses it in module listings, hex.pm search results, and `h Module` in IEx. Write one sentence that stands alone.

Good summary lines from Oban:

- "Defines a behavior and macro to guide the creation of worker modules."
- "Periodically delete `completed`, `cancelled`, and `discarded` jobs based on their age."
- "Wraps unhandled exits and throws that occur during job execution."
- "The `Notifier` coordinates listening for and publishing notifications for events in predefined channels."
- "Local process storage for Oban instances."

Bad summary lines:

- "This module is responsible for handling job processing." (filler + vague)
- "A module that provides worker functionality." (starts with "A module that")
- "Worker module." (too terse, not a sentence)

### Structure after the summary

Use `##` sections named after what the reader is trying to do, not architectural labels. Common section patterns from well-documented Elixir libraries:

- `## Usage` — how to use the module, with a minimal working example
- `## Options` — configuration options as a bullet list
- `## Examples` — real-world usage patterns, progressing from simple to complex
- `## Instrumenting with Telemetry` — events emitted by this module
- `## Customizing [Behavior]` — how to override defaults

Start simple and build complexity. Show the minimum viable usage first, then layer in options, advanced patterns, and edge cases. This progressive disclosure lets readers stop reading when they have enough.

### Scaling doc length

**One-line modules** (exceptions, simple structs, delegates):

```elixir
@moduledoc """
Wraps unhandled exits and throws that occur during job execution.
"""
```

**Small utility modules** (2-5 public functions, clear purpose):

```elixir
@moduledoc """
Local process storage for Oban instances.
"""
```

**Core concept modules** (behaviours, main entry points, complex configuration):

Multi-section guide with usage examples, options, advanced patterns, and telemetry. The `@moduledoc` for these modules can be 50-200+ lines. This is correct. The module IS the concept, and the docs should teach it completely.

**When to extract to `docs/` guides:**

Extract narrative to a separate guide only when:
- The explanation spans multiple modules (e.g., an architecture overview)
- The content is a step-by-step tutorial that doesn't belong in reference docs
- The `@moduledoc` is growing past ~200 lines and covers multiple distinct topics

When extracting, cross-reference the guide: `See the [Pipeline Architecture guide](pipeline_architecture.md) for how these stages connect.`

For single-module concepts, keep the guide in `@moduledoc`. This is where developers look first.

### Modules that should use `@moduledoc false`

- Internal implementation modules not meant for external callers
- Query modules, helper modules, and other internal support code
- Any module whose public functions exist only to satisfy OTP or framework callbacks
- Boilerplate Phoenix modules: `*HTML` view modules, `Endpoint`, `Router`, trivial session controllers

Only document modules that someone would intentionally navigate to for guidance.

### Web layer modules

Not all web modules are plumbing. Apply the same complexity-scaling rule: if the module has non-obvious behavior, it deserves a brief `@moduledoc`. If it's self-explanatory from its name and action signatures, leave it undocumented.

**Document** (brief one-liner to short paragraph):
- Plugs with non-trivial logic (auth, rate limiting, signature verification, transport protocols)
- Controllers that implement multi-step flows (OAuth, CLI login, webhook processing)
- Controllers that serve as the primary API surface (CRUD endpoints for domain resources)
- OAuth/discovery metadata endpoints

**Leave undocumented:**
- `*HTML` view modules, `Endpoint`, `Router`
- Trivial controllers (single `new`/`delete` action, no business logic)
- Manifest controllers that delegate entirely to a context module

### `@moduledoc since:`

Use `@moduledoc since: "x.y.z"` for modules added after the initial release:

```elixir
@moduledoc since: "2.2.0"
```

## Public function docs (`@doc`)

### Summary line

The first sentence is the summary. ExDoc shows it in the function listing sidebar. Lead with the verb.

Good: "Register the current process to receive messages from one or more channels."
Bad: "This function is used to register processes for channel messages."

### Body structure

After the summary, include what the reader needs to call the function safely:

- **Input contract** — required fields, expected shape, valid values
- **Return contract** — what comes back on success and failure
- **Side effects** — telemetry, I/O, database writes, message sends
- **Failure semantics** — when it raises vs returns error tuples

Not every function needs all four. A simple getter might only need the summary. A complex pipeline entry point needs all of them.

### Options format

Document options as a `## Options` section with `* :name` bullet format. This is the Elixir ecosystem standard (used by Phoenix, Ecto, Oban):

```elixir
@doc """
Defines an oban dashboard route.

It requires a path where to mount the dashboard at and allows options
to customize routing.

## Options

* `:as` — override the route name; otherwise defaults to `:oban_dashboard`

* `:resolver` — an `Oban.Web.Resolver` implementation used to customize
  the dashboard's functionality.

* `:socket_path` — a phoenix socket path for live communication,
  defaults to `"/live"`.
"""
```

### Return values

Document return values as a bullet list with the shape and its meaning:

```elixir
@doc """
The value returned from `c:perform/1` can control whether the job
is a success or a failure:

* `:ok` or `{:ok, value}` — the job is successful and marked as
  `completed`. The `value` from success tuples is ignored.

* `{:cancel, reason}` — cancel executing the job and stop retrying
  it. An error is recorded using the provided `reason`.

* `{:error, error}` — the job failed, record the error. If
  `max_attempts` has not been reached, the job is marked as
  `retryable`.

* `{:snooze, period}` — mark the job as `snoozed` and schedule it
  to run again after the specified period.
"""
```

### Examples

Every public function should have at least one example. Use `## Examples` (plural) or `## Example` (singular) as the section header.

**Fenced code blocks** for complex examples with context:

```elixir
@doc """
...

## Examples

Mount an `oban` dashboard at the path "/oban":

    defmodule MyAppWeb.Router do
      use Phoenix.Router

      import Oban.Web.Router

      scope "/", MyAppWeb do
        pipe_through [:browser]

        oban_dashboard "/oban"
      end
    end
"""
```

**Doctests** for pure functions with simple inputs and outputs:

```elixir
@doc """
Parse a crontab expression into a cron struct.

## Examples

    iex> Oban.Plugins.Cron.parse("@hourly")
    {:ok, #Oban.Cron.Expression<...>}

    iex> Oban.Plugins.Cron.parse("60 * * * *")
    {:error, %ArgumentError{message: "expression field 60 is out of range 0..59"}}
"""
```

Do not add doctests for functions with side effects, database access, or complex setup. Use fenced code blocks for those.

### Callback docs

Keep callback docs short. One sentence stating the contract, optionally followed by an example:

```elixir
@doc """
Check whether the current peer instance leads the cluster.
"""
@callback leader?(GenServer.server()) :: boolean()
```

For callbacks with meaningful behavior to explain, add more:

```elixir
@doc """
Determine the appropriate access level for a user.

During normal operation users can modify running queues and interact
with jobs through the dashboard. Through this callback you can tailor
precisely which actions the current user can do.

## Examples

To set the dashboard read only:

    def resolve_access(_user), do: :read_only

Forbid any user that isn't an admin:

    def resolve_access(user) do
      if user.admin?, do: :all, else: {:forbidden, "/"}
    end
"""
@callback resolve_access(user()) :: access()
```

### `@doc false`

Use `@doc false` for:
- Internal public functions (e.g., `child_spec/1`, `__options__/2`)
- Default callback implementations
- Functions that are public only because of OTP/framework requirements

### `@doc since:` and `@doc deprecated:`

```elixir
@doc since: "1.4.0"
@doc deprecated: "Use Gate.run/1 instead"
@doc deprecated: "Handled automatically by engine dispatch."
```

## Type docs (`@typedoc`)

- Field meanings and invariants
- Valid values for enum-like fields (atoms, string constants)
- Which fields are optional vs required
- What `nil` means for optional fields (not yet populated vs intentionally absent)

## ExDoc features

### Cross-references

Link to modules and functions using ExDoc auto-linking syntax. ExDoc converts these to clickable links on hexdocs and preserves them as readable text in IEx.

- `Foo.Bar` — links to module
- `Foo.Bar.baz/2` — links to function
- `c:GenServer.init/1` — links to callback
- `t:String.t/0` — links to type

Write `see Pipeline.run/2` not `see the run function in Pipeline`.

Cross-reference guides too: `See the [Periodic Jobs guide](periodic_jobs.html) for syntax and details.`

### Admonitions

Use for warnings, gotchas, audience scoping, and important notes:

```markdown
> #### Warning {: .warning}
>
> This function is called from test stubs. Changing its signature
> is a breaking change for test infrastructure.

> #### Meant for Extending Oban {: .warning}
>
> These functions should only be used when working with a repo inside
> engines, plugins, or other extensions for Oban.

> #### Options at Compile-Time {: .warning}
>
> Like all `use` macros, options are defined at compile time. Avoid
> using `Application.get_env/2` to define worker options.
```

Use admonitions wherever they add value. No hard limit on count per doc block. But if you're adding more than two, consider whether the information flows better as regular prose.

### Metadata

Use `@moduledoc since:` and `@doc since:` for features added after the initial release. Use `@doc deprecated:` for functions being phased out.

### Tables

Use tables for structured reference data, especially telemetry events:

```markdown
| event        | measures       | metadata                              |
| ------------ | -------------- | ------------------------------------- |
| `:start`     | `:system_time` | `:conf`, `:job`                       |
| `:stop`      | `:duration`    | `:conf`, `:job`, `:state`, `:result`  |
| `:exception` | `:duration`    | `:conf`, `:job`, `:kind`, `:reason`   |
```

Tables beat prose for anything with a repeating structure: options with types and defaults, error codes with meanings, event fields with descriptions.

## Audience

Write for **an engineer who joined the team this week**. They know Elixir but not this codebase. Every term, acronym, or module reference that isn't in the Elixir standard library needs either a cross-reference link or a one-line explanation on first use.

The Curse of Knowledge is real: once you understand a system, you forget what was confusing. Fight it by asking "would I understand this sentence if I had never seen this module before?"

## Style rules

- **Summary first.** The first sentence must work standalone in a module listing, IEx `h` output, and hex.pm search.
- **Lead with the verb.** "Runs the pipeline" not "This module runs the pipeline" or "A module that runs the pipeline" or "This module is responsible for running the pipeline."
- **Contract over narration.** Say what it guarantees, not how it works internally. "Returns `{:ok, job}` on success" not "Iterates over the queue and picks the next available job."
- **Progressive disclosure.** Simple usage first, options second, advanced patterns third, edge cases last.
- **Document only public APIs.** Do not add `@doc` to private functions. Use `@doc false` for public functions that are internal implementation details.
- **Keep docs current.** Wrong docs are worse than no docs. Update docs in the same change that modifies behavior.
- **Plain text friendly.** Docs are read in IEx with `h/1` as much as in hexdocs. Don't rely on HTML rendering for comprehension. Tables and lists must be readable without rendering.

## Anti-patterns

- **Narrating implementation.** "This function iterates over the list and..." State the contract instead.
- **Filler openings.** "This module is responsible for...", "A module that provides...", "This function is used to..."
- **Documenting private functions.** Don't, unless the logic is genuinely dangerous or non-obvious.
- **Trivial docs.** Don't add `@doc` to simple getters, delegations, or single-line wrappers. The typespec says enough.
- **Plain backtick references.** Write `Pipeline.run/2` not `` `Pipeline.run` `` when ExDoc cross-reference syntax works.
- **Doctests with side effects.** Don't add doctests for functions that need database setup, process spawning, or external services.
- **Forced structure on simple modules.** A one-line exception wrapper does not need Usage, Options, and Examples sections.
- **Stale docs.** If you change behavior, change the docs in the same commit. Stale docs actively mislead.

## Definition of done

A first-time engineer opens any documented module and answers these in under 60 seconds, whether reading hexdocs, running `h Module` in IEx, or hovering in their editor:

- What does this module do?
- How do I use it? (at least one example)
- What inputs does it need and what outputs does it guarantee?
- How can it fail?
- Can I call this function safely right now?

### Friction log test

After writing docs, do a cold read. Open the module as if you have never seen it. Try to answer: "Can I call this function safely right now?" If you need to read source code to answer that, the docs are incomplete.
