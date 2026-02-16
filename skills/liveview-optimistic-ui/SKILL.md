---
name: liveview-optimistic-ui
description: Build responsive and optimistic UI in Elixir Phoenix LiveView using `Phoenix.LiveView.JS`, loading classes, `phx-disable-with`, hooks, and latency testing. Use when requests mention optimistic UI, instant feedback, responsive LiveView interactions, `JS.push`, loading states, flicker/race issues, or toggles/modals/deletes/forms that should feel immediate.
---

# LiveView Optimistic UI

Build LiveView interactions that feel instant while preserving server truth.

## Core Model

1. Keep data state on the server, visual feedback on the client.
2. Apply immediate client feedback first, then push the event.
3. Let server diffs confirm, refine, or revert optimistic visuals.
4. Assume overlap and latency are normal, not edge cases.

## Workflow

1. Classify the interaction:
   - Purely visual (open/close/toggle), use JS-only commands.
   - Server mutation (save/delete/archive), use `JS.push` plus optimistic visuals.
   - Rich browser behavior (media, drag/drop, third-party libs), use `phx-hook` or colocated hooks.
   - Large collections, use streams or keyed comprehensions.
2. Add immediate feedback:
   - Add loading classes (`phx-click-loading`, `phx-submit-loading`, etc.).
   - Add `phx-disable-with` for click/submit actions.
   - If pending state belongs outside the clicked element, use `JS.push(..., loading: "...")`.
3. Compose optimistic JS:
   - Pipe commands: `JS.push(...) |> JS.add_class(...) |> JS.transition(...)`.
   - Use `display:` in `JS.show` and `JS.toggle` for layout stability on inline elements.
   - Use `JS.toggle_attribute/2` with a 3-value tuple for instant ARIA updates.
   - Use `to: {:closest, selector}` or `to: {:inner, selector}` to avoid brittle selectors.
4. Keep it patch-safe:
   - Prefer LiveView JS commands over ad-hoc DOM mutation.
   - Use `JS.ignore_attributes` for browser-owned attributes like `open` on `<details>`/`<dialog>`.
   - Ensure failures remove stale optimistic decorations deterministically.
5. Validate with latency:
   - In dev tools, run `liveSocket.enableLatencySim(ms)`.
   - Verify there is no rollback flicker, wrong-row updates, or duplicate submissions.
6. Verify failure paths:
   - Mutation rejected, restore CTA state and show a deterministic error.
   - Concurrent clicks, disable or serialize per resource key.
   - Async work, guard stale responses with request IDs or version checks.

## Event Flow

```text
User intent (click/submit)
  -> JS commands execute immediately (visual feedback)
  -> event is pushed over the LiveView channel
  -> server handles mutation
  -> diff and acknowledgement arrive
  -> client keeps, refines, or reverts optimistic visuals
```

## Baseline Patterns

### 1) Optimistic row delete

```heex
<button
  phx-click={
    JS.push("delete", loading: "#row-#{item.id}")
    |> JS.add_class("opacity-50 pointer-events-none", to: "#row-#{item.id}")
  }
  phx-disable-with="Removing..."
>
  Remove
</button>
```

### 2) Instant toggle without round-trip

```heex
<button phx-click={JS.toggle(to: "#details-#{@id}", display: "inline")}>
  More info
</button>
```

### 3) Instant ARIA state transitions

```heex
<button
  id={"expander-#{@id}"}
  phx-click={JS.toggle_attribute({"aria-expanded", "true", "false"})}
  aria-expanded="false"
>
  Toggle
</button>
```

### 4) Page-level loading event for long actions

```heex
<button phx-click={JS.push("rebuild", page_loading: true)}>
  Rebuild
</button>
```

## Anti-Patterns

- Waiting for a server response before any feedback.
- Relying on independent HTTP response order for correctness.
- Manually mutating DOM where `JS.*` commands already provide patch-aware behavior.
- Re-rendering whole lists for single-item changes when streams/keys are available.

José Valim's analysis of concurrent submissions is the design warning here: without causal ordering, concurrent request/revalidation models can surface stale user-visible state. Prefer LiveView's persistent channel model and server-side ordering discipline for mutation flows.

## References

- Load `references/js-commands-cookbook.md` for command syntax and composition patterns.
- Load `references/changelog-highlights-2024-2026.md` for version-sensitive behavior and upgrade checks.
