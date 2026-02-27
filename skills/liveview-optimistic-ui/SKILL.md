---
name: liveview-optimistic-ui
description: >
  Implements optimistic UI patterns in Elixir Phoenix LiveView: instant client
  feedback before server confirmation, loading states, rollback/revert on failure,
  race condition guards, stream insert/delete animations, undo windows, and
  accessibility for async interactions. Use when the user needs LiveView interactions
  to feel immediate, wants to add loading indicators or spinners, needs to handle
  double-submit or double-click, wants to animate stream inserts or deletes, needs
  undo/rollback for destructive actions, is dealing with stale data or flicker under
  latency, or needs aria-live announcements for optimistic state changes.
  Don't use for general LiveView form validation or changeset errors (use
  liveview-forms instead), non-LiveView frontend frameworks (React, Vue, Svelte),
  or server-side performance optimization unrelated to perceived UI responsiveness.
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
   - Purely visual (open/close/toggle): JS-only commands, no round-trip.
   - Server mutation (save/delete/archive): `JS.push` plus optimistic visuals.
   - Rich browser behavior (media, drag/drop, third-party libs): `phx-hook` or colocated hooks.
   - Large collections: streams or keyed comprehensions.
2. Choose loading feedback level:
   - Button-only feedback: `phx-disable-with`.
   - Button + related UI: `JS.push(..., loading: "#other-element")`.
   - Whole page transition: `JS.push(..., page_loading: true)`.
   - Multiple scattered elements: compose `JS.add_class` calls in a pipe.
3. Compose optimistic JS:
   - Pipe commands: `JS.push(...) |> JS.add_class(...) |> JS.transition(...)`.
   - Use `display:` in `JS.show` and `JS.toggle` for layout stability on inline elements.
   - Use `JS.toggle_attribute/2` with a 3-value tuple for instant ARIA updates.
   - Use `to: {:closest, selector}` or `to: {:inner, selector}` to avoid brittle selectors.
4. Keep it patch-safe:
   - Prefer LiveView JS commands over ad-hoc DOM mutation.
   - Use `JS.ignore_attributes` for browser-owned attributes like `open` on `<details>`/`<dialog>`.
   - Ensure failures remove stale optimistic decorations deterministically.
5. Plan for failure — see **Error Recovery** section below for implementation:
   - On mutation rejection: choose server-driven revert (for server-rendered attrs) or `push_event` revert (for `JS.add_class` changes that survive patches).
   - On concurrent clicks: disable or serialize per resource key.
   - On async work: guard stale responses with request IDs or version checks. Use `cancel_async/3` to cancel a superseded `start_async` by name before starting a new one.
   - On socket disconnect: server patches resync DOM on reconnect. Re-derive any hook-managed state from the patched DOM in `mounted()`.
6. Make it accessible:
   - Use `aria-live="polite"` regions to announce state changes to screen readers.
   - Set `aria-busy` on containers during mutations.
   - Respect `prefers-reduced-motion` with a CSS guard.
7. Validate with latency:
   - In dev tools, run `liveSocket.enableLatencySim(ms)`.
   - Verify there is no rollback flicker, wrong-row updates, or duplicate submissions.
   - Write LiveViewTest assertions for server-side state changes. Note: LiveViewTest does not execute client-side JS commands (e.g., `JS.add_class`, loading classes). Test visual feedback with browser-level tests.

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

## Stream Optimistic Patterns

Streams are the default for any list of non-trivial size. Optimistic stream updates require coordination between client-side visuals and server-side stream operations.

### Optimistic stream insert with temp ID

Insert a temporary item immediately, swap it for the real one on confirmation, or remove it on failure.

```elixir
def handle_event("add_item", params, socket) do
  temp_id = "temp-#{System.unique_integer([:positive])}"
  temp_item = %{id: temp_id, title: params["title"], pending?: true}

  socket =
    socket
    |> stream_insert(:items, temp_item, at: 0)
    |> start_async({:create_item, temp_id}, fn ->
      {temp_id, MyApp.Items.create(params)}
    end)

  {:noreply, socket}
end

def handle_async({:create_item, _}, {:ok, {temp_id, {:ok, item}}}, socket) do
  socket =
    socket
    |> stream_delete(:items, %{id: temp_id})
    |> stream_insert(:items, item, at: 0)

  {:noreply, socket}
end

def handle_async({:create_item, _}, {:ok, {temp_id, {:error, _changeset}}}, socket) do
  socket =
    socket
    |> stream_delete(:items, %{id: temp_id})
    |> put_flash(:error, "Could not create item")

  {:noreply, socket}
end
```

Using a tuple name `{:create_item, temp_id}` allows concurrent inserts: each gets its own async, and the temp ID flows through the return value so the right placeholder is replaced.

Style the temp item as pending in the template:

```heex
<div
  :for={{dom_id, item} <- @streams.items}
  id={dom_id}
  class={if item[:pending?], do: "opacity-50 animate-pulse"}
>
  <%= item.title %>
</div>
```

### Optimistic stream delete with transition timing

When using a CSS transition, delay `stream_delete` so the animation completes before the element is removed from the DOM.

```heex
<button phx-click={
  JS.push("delete_item", value: %{id: item.id})
  |> JS.transition(
    {"transition-opacity duration-300", "opacity-100", "opacity-0"},
    to: "#items-#{item.id}"
  )
}>
  Delete
</button>
```

```elixir
def handle_event("delete_item", %{"id" => id}, socket) do
  case MyApp.Items.delete(id) do
    {:ok, item} ->
      Process.send_after(self(), {:remove_from_stream, item}, 300)
      {:noreply, socket}

    {:error, _reason} ->
      {:noreply, put_flash(socket, :error, "Delete failed")}
  end
end

def handle_info({:remove_from_stream, item}, socket) do
  {:noreply, stream_delete(socket, :items, item)}
end
```

The 300ms delay matches the `duration-300` transition class. If the server responds faster than the animation, the item disappears mid-fade without this delay.

### Async stream loading with `stream_async` (v1.1.5+)

For paginated or lazily loaded lists, `stream_async/4` inserts items as they arrive without blocking the initial render. Skip this pattern if the project uses LiveView older than v1.1.5 — use `start_async` with manual `stream_insert` calls instead.

```elixir
def mount(_params, _session, socket) do
  {:ok,
   socket
   |> stream(:items, [])
   |> stream_async(:items, fn -> {:ok, MyApp.Items.list_all()} end)}
end
```

## Error Recovery

Optimistic visuals must revert cleanly when the server rejects a mutation.

### Server-driven revert (attributes rendered by the server)

Server patches restore attributes and content that the server controls. If the item stays in assigns or streams unchanged, the next patch naturally restores server-rendered DOM state (text, data attributes, conditionally rendered classes).

However, classes added client-side via `JS.add_class` are **not** reverted by server patches. They persist until explicitly removed. For server-driven revert to work, the optimistic visual must come from server-rendered state (e.g., a conditional class in HEEx), not from a client-side JS command.

```elixir
def handle_event("archive", %{"id" => id}, socket) do
  case MyApp.Items.archive(id) do
    {:ok, item} ->
      {:noreply, stream_delete(socket, :items, item)}

    {:error, _reason} ->
      # Server patch restores server-rendered attributes, but NOT JS.add_class changes
      {:noreply, put_flash(socket, :error, "Could not archive item")}
  end
end
```

### Explicit revert via `push_event` (JS.add_class and similar)

Classes added via `JS.add_class` survive server patches. Use `push_event` to tell a hook to clean them up on failure. See `references/js-commands-cookbook.md` for the hook-side implementation.

```elixir
{:error, _reason} ->
  {:noreply,
   socket
   |> push_event("revert-optimistic", %{id: id})
   |> put_flash(:error, "Archive failed")}
```

### Undo window for destructive actions

For deletes and archives, offer a brief undo window instead of executing immediately.

```elixir
def handle_event("delete", %{"id" => id}, socket) do
  ref = make_ref()
  Process.send_after(self(), {:confirm_delete, id, ref}, 5_000)

  {:noreply,
   socket
   |> assign(:pending_delete, {id, ref})
   |> put_flash(:info, "Item will be deleted. Undo?")}
end

def handle_event("undo_delete", _params, socket) do
  {:noreply, assign(socket, :pending_delete, nil)}
end

def handle_info({:confirm_delete, id, ref}, socket) do
  case socket.assigns.pending_delete do
    {^id, ^ref} ->
      MyApp.Items.delete!(id)

      {:noreply,
       socket
       |> stream_delete(:items, %{id: id})
       |> assign(:pending_delete, nil)}

    _ ->
      # Undo was clicked, or a different delete superseded this one
      {:noreply, socket}
  end
end
```

## Race Conditions

### Request ID tracking for async results

Discard stale responses when a newer request supersedes an older one. `start_async` does **not** auto-cancel a previous async of the same name. Cancel the named async before starting a new one:

```elixir
socket = socket |> cancel_async(:search, :superseded) |> start_async(:search, fn -> ... end)
```

For manual `Task`-based async (pre-LiveView 1.0 or third-party tasks), track a monotonic request ID in assigns and ignore results where `request_id != socket.assigns.search_request_id`.

### Optimistic locking for concurrent edits

Prevent silent overwrites when multiple users edit the same resource.

```elixir
def handle_event("update", params, socket) do
  item = socket.assigns.item

  case MyApp.Items.update(item, params, expected_version: item.lock_version) do
    {:ok, updated} ->
      {:noreply, assign(socket, :item, updated)}

    {:error, :stale} ->
      fresh = MyApp.Items.get!(item.id)

      {:noreply,
       socket
       |> assign(:item, fresh)
       |> put_flash(:error, "Updated by someone else. Your changes were not saved.")}
  end
end
```

### Serializing concurrent clicks

Use `phx-disable-with` to block double-submit on a button. For per-row serialization, use `loading: "#row-#{item.id}"` to lock the row element during the round-trip (see Baseline Pattern 1).

## Form Validation

For the full form lifecycle (changesets, `to_form`, error feedback model, debouncing, recovery, nested forms, uploads), see the `liveview-forms` skill. This section covers only the optimistic feedback patterns.

### Optimistic search with loading feedback

`phx-change-loading` is applied automatically to the input and its parent form during the round-trip. To show loading feedback on a results container **outside** the form, use `loading:` in `JS.push`:

```heex
<form phx-change={JS.push("search", loading: "#results")} phx-submit="search">
  <input
    type="search"
    name="q"
    value={@query}
    phx-debounce="300"
    placeholder="Search..."
  />
</form>

<div id="results" class="phx-submit-loading:opacity-50">
  ...
</div>
```

## Accessibility

### Screen reader announcements

Use an `aria-live` region in the layout (so it persists across patches). Update `@status_message` from the server after mutations.

```heex
<div role="status" aria-live="polite" class="sr-only" id="live-status">
  <%= @status_message %>
</div>
```

Mark containers as busy during async operations: `<section aria-busy={@saving?}>`. Update `@saving?` before and after the mutation.

### Respect reduced motion

One CSS rule prevents all transition-based optimistic animations from causing issues for motion-sensitive users. The optimistic state classes still apply, only the visual transition is suppressed.

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Testing Optimistic Flows

### LiveViewTest basics

LiveViewTest processes events synchronously through the server, so you can assert the post-mutation state directly.

```elixir
test "delete removes the item", %{conn: conn} do
  item = insert(:item)
  {:ok, view, _html} = live(conn, ~p"/items")

  assert has_element?(view, "#items-#{item.id}")

  view |> element("#delete-#{item.id}") |> render_click()

  refute has_element?(view, "#items-#{item.id}")
end
```

### Testing failure recovery

```elixir
test "shows error and keeps item when delete fails", %{conn: conn} do
  item = insert(:item, locked: true)
  {:ok, view, _html} = live(conn, ~p"/items")

  view |> element("#delete-#{item.id}") |> render_click()

  assert has_element?(view, "#items-#{item.id}")
  assert render(view) =~ "Could not delete"
end
```

### Testing async flows

For `start_async` and `stream_async` patterns, use `render_async/1` to await all pending async tasks before asserting:

```elixir
test "optimistic insert shows pending item then resolves", %{conn: conn} do
  {:ok, view, _html} = live(conn, ~p"/items")

  view
  |> form("#new-item-form", item: %{title: "New thing"})
  |> render_submit()

  # Wait for start_async to complete, then render
  html = render_async(view)
  assert html =~ "New thing"
end
```

### Latency simulation in development

Not a substitute for tests, but catches visual regressions tests cannot. In the browser console: `liveSocket.enableLatencySim(1000)`. Check for flicker, stale state, and double submissions. Disable with `liveSocket.disableLatencySim()`.

## Colocated Hooks (v1.1+)

Prefer colocated hooks over global hook registrations. They keep hook logic close to the LiveView that uses them and avoid global namespace pollution. See [`Phoenix.LiveView.ColocatedHook`](https://hexdocs.pm/phoenix_live_view/Phoenix.LiveView.ColocatedHook.html) and [`Phoenix.LiveView.ColocatedJS`](https://hexdocs.pm/phoenix_live_view/Phoenix.LiveView.ColocatedJS.html). Hook-side implementation for `push_event` revert patterns is in `references/js-commands-cookbook.md`.

## Anti-Patterns

**Feedback timing:**
- Waiting for a server response before any visual feedback.
- Transitions that finish after the server responds, causing a flash of reverted state. Match `Process.send_after` delay to transition duration.

**DOM management:**
- Manually mutating DOM where `JS.*` commands already provide patch-aware behavior.
- Using `phx-update="ignore"` on a container and expecting server patches to revert optimistic classes inside it. `ignore` blocks all server patches to that subtree.
- Using `phx-hook` for things `JS.*` commands handle natively. Hooks are an escalation, not a default.

**Streams and lists:**
- Re-rendering whole lists for single-item changes when streams/keys are available.
- Stream items with unstable IDs (timestamps, list indexes). Use database IDs or deterministic unique keys.

**Forms:**
- Modifying form input values with JS commands during `phx-change`. The wrong values may serialize. Use `value:` in `JS.push` instead.

**State management:**
- Relying on independent HTTP response order for correctness.
- Forgetting that socket disconnect and reconnect resets hook state. Re-derive optimistic state from the server-patched DOM in `mounted()`.

**Accessibility:**
- Optimistic transitions without a `prefers-reduced-motion` CSS guard.
- No `aria-live` region for announcing mutation outcomes to screen readers.

See José Valim's [analysis of concurrent submissions](https://dashbit.co/blog/remix-concurrent-submissions-flawed): without causal ordering, concurrent request/revalidation models can surface stale user-visible state. Prefer LiveView's persistent channel model and server-side ordering discipline for mutation flows.

## References

- Read `references/js-commands-cookbook.md` when composing JS command chains, choosing selector strategies, or looking up loading feedback options. Skip if the question is purely about server-side Elixir patterns.
- Read `references/changelog-highlights-2024-2026.md` when checking version-specific behavior, planning a LiveView upgrade, or debugging a regression that appeared after a version bump. Skip if the LiveView version is not in question.
