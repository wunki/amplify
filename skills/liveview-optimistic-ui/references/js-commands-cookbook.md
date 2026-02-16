# LiveView JS Commands Cookbook

Reviewed against Phoenix LiveView `v1.1.23`.

## `JS.push` options that matter for optimistic UX

`JS.push(event, opts)` supports:

- `target:` route event to a component or selector.
- `loading:` apply loading classes and locking to another element.
- `page_loading:` emit `phx:page-loading-start/stop` for this interaction.
- `value:` merge payload values over `phx-value-*` attributes.

Useful rule: for form events, payload precedence is:
`JS.push value > phx-value-* > input value`

## Selector targeting (`to:`)

Every command supports selector targeting:

- String selector, example: `to: "#row-12"`
- Scoped selector, example: `to: {:closest, "tr"}`
- Scoped selector, example: `to: {:inner, ".menu"}`

Use scopes first when possible, they are usually less fragile than global IDs.

## Command patterns

### Pending-state mutation

```heex
phx-click={
  JS.push("archive", loading: "#row-#{@id}")
  |> JS.add_class("opacity-50 pointer-events-none", to: "#row-#{@id}")
}
```

### Mark related UI as loading (not just clicked element)

```heex
phx-click={
  JS.push("delete", loading: "#cart-total")
  |> JS.add_class("line-through opacity-60", to: "#cart-total")
}
```

### Optimistic transition

```heex
phx-click={
  JS.push("delete")
  |> JS.transition({"transition-opacity", "opacity-100", "opacity-0"}, to: "#row-#{@id}")
}
```

### Layout-stable toggle for inline content

```heex
phx-click={JS.toggle(to: "#details-#{@id}", display: "inline")}
```

### Accessible state updates

```heex
phx-click={JS.toggle_attribute({"aria-expanded", "true", "false"})}
```

### Browser-owned attributes

```heex
<details phx-mounted={JS.ignore_attributes(["open"])}>
  ...
</details>
```

## Transition options

Commands with transitions (`show/hide/toggle/add_class/remove_class/toggle_class/transition`) accept:

- `transition:` class tuple or class string
- `time:` transition duration in milliseconds
- `blocking:` set `false` to avoid blocking DOM updates during transition when needed

## Loading feedback without custom JS

LiveView adds loading classes automatically:

- `phx-click` -> `phx-click-loading`
- `phx-submit` -> `phx-submit-loading`
- `phx-change` -> `phx-change-loading`

And related event variants (`focus`, `blur`, `window-keydown`, `window-keyup`).

Add `phx-disable-with` to buttons for immediate text/disabled feedback.

## Composing multiple loading indicators

When one action affects several UI regions, pipe multiple class additions:

```heex
phx-click={
  JS.push("checkout", loading: "#cart-summary")
  |> JS.add_class("opacity-50", to: "#cart-items")
  |> JS.add_class("animate-pulse", to: "#order-total")
}
```

`loading:` applies loading classes and locking to a single target; these loading classes are removed automatically when the server acknowledges the event. `JS.add_class` calls are **not** auto-removed on acknowledgement. They persist until explicitly removed via `JS.remove_class`, a hook, or a full re-render that replaces the element.

## Server-to-client revert with `push_event`

When `JS.add_class` adds optimistic classes that survive server patches, use `push_event` from the server to tell a hook to clean up:

```elixir
# Server
push_event(socket, "revert-optimistic", %{id: id})
```

```javascript
// Hook
this.handleEvent("revert-optimistic", ({ id }) => {
  const el = document.getElementById(`item-${id}`)
  if (el) el.classList.remove("opacity-50", "pointer-events-none")
})
```

This is the escape hatch for error recovery when server diffs alone cannot undo client-side JS changes.

## Hook escalation path

Escalate to `phx-hook` when:

- You need third-party JS interop.
- You need imperative control that `JS.*` cannot express.
- You need custom event orchestration around browser APIs.
- You need to listen for `push_event` calls from the server (e.g., revert patterns).

For modern LiveView versions (v1.1+), prefer colocated hooks over global registrations. Colocated hooks and typed hook interfaces reduce glue code and keep hook logic close to the LiveView that uses it.
