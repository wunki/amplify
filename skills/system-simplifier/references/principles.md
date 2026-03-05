# Design Principles for Simplification

These principles guide every recommendation. They are drawn from decades of systems thinking, not invented here.

## The Simplicity Test

Before every change, ask: "Am I making this simpler or just different?"

Simpler means fewer concepts to hold in your head at once. Fewer moving parts. Fewer places a change can propagate. If a refactor moves complexity from one place to another without reducing total complexity, skip it.

## Principle 1: Delete Before Abstracting

The best code is no code. Before writing anything new, ask:

- Can this be solved with existing primitives?
- Is this feature actually used?
- Would deleting this break anything?

If a module, function, field, or config key has no live callers, delete it. Do not comment it out. Do not mark it deprecated. Do not add a TODO. Delete it. Version control remembers.

Dead code is not free. It misleads readers, creates false dependencies in search results, and makes real changes harder to evaluate.

## Principle 2: Simple vs Easy

Simple means "not interleaved." Easy means "close at hand." They are not the same.

A helper function that's easy to call but hides three concerns behind one name is easy, not simple. Three explicit lines that each do one thing are simple, not easy. Prefer simple.

Concretely:

- **Complecting** = braiding together things that could change independently. A struct that holds both request config and response data complects input with output.
- **Decomplecting** = separating things so each can change without affecting the other. Separate structs for request and response, even if it means typing more.

Test: if changing requirement A forces you to also touch code for requirement B, A and B are complected.

## Principle 3: Data Over Abstractions

Prefer plain data (maps, lists, structs with well-known fields) over opaque abstractions (GenServers, behaviours, protocols) when the data shape is stable and the operations are few.

A struct with three fields is easier to reason about than a module with three functions that each return a different opaque type.

When in doubt, represent state as data and operations as functions that transform it. The pipeline operator exists for a reason.

## Principle 4: Deep Modules, Not Many Modules

A deep module has a simple interface and hides significant complexity behind it. A shallow module has an interface as complex as its implementation. Shallow modules add cognitive overhead without earning it.

Signs of a shallow module:
- The caller needs to understand the implementation to use it correctly
- The module has 1-2 public functions and 0-1 private functions
- The module is a "pass-through" that delegates to another module with the same arguments
- Deleting the module and inlining its code makes the caller simpler

When you find a shallow module: inline it into its caller. The two-line function body at the call site is cheaper than a separate file, an alias, and the mental overhead of "what does this module do?"

Exception: modules that implement a behaviour or protocol have a reason to exist even when shallow, because the interface contract justifies the separation.

## Principle 5: Flatten Nested State

Every level of nesting multiplies the paths a reader must trace. `ctx.control.constraints.max_results` is three lookups. `ctx.max_results` is one.

Flatten when:
- The nested structure is accessed by multiple callers (it's not encapsulated anyway)
- The nested struct has no independent lifecycle (it's always created and consumed with its parent)
- The nesting exists "for organization" rather than for a real boundary

Keep nesting when:
- The nested struct is created, passed, and consumed independently
- The nesting represents a real domain boundary (e.g., `order.payment` where payments have their own lifecycle)

## Principle 6: Fix Producers, Not Consumers

When a function handles 8 different input shapes with normalization, the problem is not the consumer. The problem is the 8 producers sending inconsistent data.

Fix the sources. Make them produce a single consistent shape. Then delete the normalization code.

This applies recursively: if a "normalizer" module exists, ask who calls it and why the callers can't produce the right shape in the first place.

## Principle 7: Define Errors Out of Existence

The best way to handle an error is to make it impossible. Design APIs so invalid states cannot be represented.

- Use `@enforce_keys` on structs so required fields cannot be nil
- Use pattern matching in function heads so invalid inputs fail at the call boundary
- Use types and guards instead of runtime validation where possible
- Make success the only path through the code, not one of several branches

When errors remain: keep failures explicit and structured in the interior, and decide user-facing degradation only at the boundary. The outermost caller should see a clean `{:ok, result}` or `{:error, reason}`. Do not silently swallow failures in inner layers, log and propagate with enough context for diagnosis.

## Principle 8: Optimize for the Reader

Code is read 10x more than it is written. Every name, every structure, every abstraction boundary is a decision about what the next reader will need to understand.

Test: Can a new team member open this module and understand what it does, what it reads, what it writes, and how it fails, within 60 seconds?

If not, the problem is not documentation. The problem is the code is doing too many things or hiding its contract behind indirection.

## Principle 9: One Change, One Place

When a requirement changes, it should require editing one place. If a change touches 5 files, the abstraction boundaries are wrong.

This is the practical test for whether modules are well-separated: count the files in a typical PR. If most PRs touch 2-3 files, the boundaries are good. If most touch 8-10, the boundaries are drawn in the wrong places.

## Principle 10: Mechanical Sympathy

Understand the runtime. In Elixir:

- Processes are cheap but not free. Don't wrap pure functions in GenServers.
- Pattern matching is the primary control flow. Use it instead of if/case chains.
- The pipe operator encodes data flow. If the pipe breaks, the abstraction is wrong.
- Supervision trees are the error handling strategy. Don't duplicate it with try/rescue.
- Immutability means you can't accidentally corrupt shared state. Trust it.
