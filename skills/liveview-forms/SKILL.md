---
name: liveview-forms
description: >
  Builds and debugs Phoenix LiveView forms: changeset-backed validation,
  per-field error feedback with used_input?, form recovery on reconnect,
  nested forms with inputs_for and sort/drop params, file uploads with
  allow_upload, component forms with phx-target, and HTTP bridging via
  phx-trigger-action. Use when the user is working with LiveView forms,
  phx-change, phx-submit, to_form, changeset validation, error display,
  form errors not showing, dynamic add/remove fields, multi-step forms,
  file uploads, or form reconnect recovery. Don't use for non-LiveView
  forms (plain HTML, React, dead views), general Ecto changeset questions
  unrelated to a form, or LiveView topics that don't involve form input
  handling (streams, navigation, presence, JS hooks).
---

# LiveView Forms

Build forms in LiveView that validate cleanly, recover from disconnects, and handle complex data shapes.

## Core Model

1. The server owns data and validation. The client owns focus and unsaved input values.
2. Forms are driven by `to_form/2`, not raw changesets in assigns.
3. Error visibility is two-layered: changeset action gates all errors, `used_input?/1` gates per-field.
4. Form inputs auto-recover after disconnect when the form has both `phx-change` and an `id`.

## Workflow

1. Create the form: build a changeset from the schema, pass it through `to_form/2`, assign the result. Do not set `action: :validate` on mount.
2. Validate on change: handle `phx-change` to rebuild the changeset with `action: :validate` and reassign the form. Use `_target` for conditional validation logic.
3. Submit: handle `phx-submit`. On success, redirect or update assigns. On failure, reassign from the error changeset.
4. Give the form a unique `id`. Required for DOM stability, recovery, and component targeting.

## Form Lifecycle

### Mount: create the form

```elixir
def mount(_params, _session, socket) do
  changeset = Accounts.change_user(%User{})
  {:ok, assign(socket, form: to_form(changeset))}
end
```

### Validate: rebuild on every change

```elixir
def handle_event("validate", %{"user" => params}, socket) do
  form =
    %User{}
    |> Accounts.change_user(params)
    |> to_form(action: :validate)

  {:noreply, assign(socket, form: form)}
end
```

Setting `action: :validate` enables error display. Without it, errors exist in the changeset but are suppressed in the template.

### Submit: persist or show errors

```elixir
def handle_event("save", %{"user" => params}, socket) do
  case Accounts.create_user(params) do
    {:ok, user} ->
      {:noreply,
       socket
       |> put_flash(:info, "User created")
       |> redirect(to: ~p"/users/#{user}")}

    {:error, %Ecto.Changeset{} = changeset} ->
      {:noreply, assign(socket, form: to_form(changeset))}
  end
end
```

### Template

```heex
<.form for={@form} id="user-form" phx-change="validate" phx-submit="save">
  <.input field={@form[:name]} label="Name" />
  <.input field={@form[:email]} label="Email" phx-debounce="blur" />
  <button type="submit" phx-disable-with="Saving...">Save</button>
</.form>
```

Every form needs a unique `id`. Without it, DOM patching may replace elements instead of updating them, causing focus loss and breaking recovery.

## Error Feedback Model

Error visibility has two independent layers. Both must pass for errors to appear.

### Layer 1: Changeset action

Errors are suppressed when the changeset action is `nil` or `:ignore`. Set `action: :validate` in `to_form` to enable them:

```elixir
# Errors suppressed (mount, no action set)
to_form(changeset)

# Errors enabled (validation)
to_form(changeset, action: :validate)
```

### Layer 2: `used_input?/1`

Even with `action: :validate`, errors only show for fields the user has interacted with (focused, typed, or submitted). The LiveView JS client tracks this automatically by sending `_unused_<field>` params for untouched fields.

```elixir
# In a custom input component
errors = if Phoenix.Component.used_input?(field), do: field.errors, else: []
```

The default `<.input>` component from Phoenix generators (1.7.18+) handles this internally. `used_input?/1` requires Phoenix LiveView 0.20+. On earlier versions, errors show unconditionally once the changeset action is set.

### Nested fields

A nested field group (like a date with year/month/day sub-fields) is considered "used" if **any** of its sub-fields have been interacted with.

### "Why aren't my errors showing?" checklist

1. Is `action: :validate` set in `to_form`? Check both validate and save handlers.
2. Has the user interacted with the field? `used_input?/1` filters unused fields.
3. Is the changeset actually producing errors? Inspect `changeset.errors` directly.
4. For custom inputs: are you checking `used_input?/1`? The default `<.input>` handles this, custom components may not.

## Debouncing and Throttling

Both are client-side rate limiters applied to any event binding.

| Attribute | Behavior | Default (when value omitted) |
|---|---|---|
| `phx-debounce="300"` | Delays event until 300ms of inactivity | 300ms (when attribute value is empty string) |
| `phx-debounce="blur"` | Delays event until field loses focus | n/a |
| `phx-throttle="1000"` | Emits immediately, then at most once per 1s | 300ms (when attribute value is empty string) |

### Timer reset behavior

When a `phx-submit` fires, or a `phx-change` fires for a **different** input, all pending debounce/throttle timers are flushed. This ensures stale debounced events do not arrive after a submit.

### Choosing a strategy

- **Text inputs with server validation**: `phx-debounce="blur"` or 500-1000ms. Avoids validation noise while typing.
- **Search/filter inputs**: `phx-debounce="300"` (the default). Fast enough to feel responsive.
- **Sliders, continuous controls**: `phx-throttle="100"` or similar. Emits immediately, then rate-limits.
- **Buttons**: `phx-throttle="1000"` to prevent accidental rapid clicks.

### Gotchas

- `phx-keydown` on unique keypresses always dispatches immediately regardless of throttle. Only key **repeats** are throttled.
- The default when omitting the value is 300ms, not 0.
- Debouncing on inputs using the `form="..."` attribute to associate with a remote form had bugs before v1.1.15.

## Form Recovery on Reconnect

When a LiveView socket disconnects and reconnects (network interruption, server deploy, crash), forms with both `phx-change` and an `id` automatically recover. The client re-sends the form's current input values as a `phx-change` event immediately after mount.

### Default behavior

No extra code needed. The `phx-change` handler (`"validate"`) runs with the recovered data:

```heex
<.form for={@form} id="user-form" phx-change="validate" phx-submit="save">
  ...
</.form>
```

### Custom recovery for multi-step forms

For wizards or forms with server-side step state that cannot be inferred from inputs alone, use a dedicated recovery event:

```heex
<form id="wizard" phx-change="validate_step" phx-auto-recover="recover_wizard">
  ...
</form>
```

```elixir
def handle_event("recover_wizard", params, socket) do
  # Rebuild wizard state from the recovered input values
  {:noreply, rebuild_wizard_state(socket, params)}
end
```

### Disabling recovery

When form state cannot be meaningfully restored (e.g., a completed payment form):

```heex
<form id="payment" phx-change="validate" phx-auto-recover="ignore">
```

### Gotchas

- **LiveReload interferes in dev.** LiveReload causes a full page reload (not a socket reconnect), which discards form state entirely. To test recovery, either comment out the `LiveReload` plug or set `code_reloader: false`.
- Forms with **only hidden inputs** did not recover before v0.19.2.
- Recovery inside **portals** works as of v1.1.12.
- Recovery respects **fieldset** elements as of v1.1.6.
- `push_patch` during recovery caused issues before v1.1.9.

## Nested Forms

Read `references/nested-forms.md` when the request involves `inputs_for`, dynamic add/remove fields, `sort_param`, `drop_param`, `cast_embed`, `cast_assoc`, or schemas without a primary key. Skip if the form has no nested associations or embeds.

### Quick reference: key requirements

- `on_replace: :delete` is **required** on `has_many` and `embeds_many` when using sort/drop params.
- Add/remove buttons must be `type="button"` to prevent form submission.
- `JS.dispatch("change")` triggers the form's `phx-change` event, which rebuilds the changeset.
- The empty `<input type="hidden" name="list[emails_drop][]" />` **outside** `inputs_for` is required. Without it, removing the last item sends no drop param and the delete is silently ignored.
- Do not access `form[:field].value` in nested forms for display logic. The value may be a struct, changeset, or raw params depending on state. Compute derived values in the LiveView or changeset instead.
- `sort_param` and `drop_param` require Ecto 3.10.0+.

## Uploads

### Setup

```elixir
def mount(_params, _session, socket) do
  {:ok,
   socket
   |> assign(form: to_form(MyApp.change_post(%Post{})))
   |> allow_upload(:photos,
     accept: ~w(.jpg .jpeg .png),
     max_entries: 3,
     max_file_size: 5_000_000
   )}
end
```

The form **must** have both `phx-change` and `phx-submit` bindings for uploads to work.

### Template

```heex
<.form for={@form} id="post-form" phx-change="validate" phx-submit="save">
  <.live_file_input upload={@uploads.photos} />

  <%!-- Preview entries --%>
  <div :for={entry <- @uploads.photos.entries}>
    <.live_img_preview entry={entry} />
    <progress value={entry.progress} max="100"><%= entry.progress %>%</progress>
    <button type="button" phx-click="cancel-upload" phx-value-ref={entry.ref}>
      Cancel
    </button>
  </div>

  <%!-- Show errors --%>
  <div :for={err <- upload_errors(@uploads.photos)} class="text-red-600">
    <%= humanize_upload_error(err) %>
  </div>

  <button type="submit" phx-disable-with="Uploading...">Save</button>
</.form>
```

### Processing uploads on submit

Files are uploaded **before** the `phx-submit` callback fires. Consume them in the submit handler:

```elixir
def handle_event("save", params, socket) do
  uploaded_files =
    consume_uploaded_entries(socket, :photos, fn %{path: path}, entry ->
      dest = Path.join(["priv", "static", "uploads", "#{entry.uuid}-#{entry.client_name}"])
      File.cp!(path, dest)
      {:ok, ~p"/uploads/#{Path.basename(dest)}"}
    end)

  # uploaded_files is a list of the {:ok, value} return values
  # Save post with file paths...
end
```

### Auto-upload (upload on selection, not submit)

```elixir
allow_upload(socket, :avatar,
  accept: :any,
  auto_upload: true,
  progress: &handle_progress/3
)

defp handle_progress(:avatar, entry, socket) do
  if entry.done? do
    url =
      consume_uploaded_entry(socket, entry, fn %{path: path} ->
        dest = Path.join(["priv", "static", "uploads", Path.basename(path)])
        File.cp!(path, dest)
        {:ok, ~p"/uploads/#{Path.basename(dest)}"}
      end)

    {:noreply, assign(socket, :avatar_url, url)}
  else
    {:noreply, socket}
  end
end
```

### Cancel an upload

```elixir
def handle_event("cancel-upload", %{"ref" => ref}, socket) do
  {:noreply, cancel_upload(socket, :photos, ref)}
end
```

### Error atoms

| Error | Meaning |
|---|---|
| `:too_large` | File exceeds `max_file_size` |
| `:not_accepted` | File type not in `accept` list |
| `:too_many_files` | Exceeds `max_entries` |
| `:external_client_failure` | External upload (S3, etc.) failed |

### Gotchas

- Cannot call `consume_uploaded_entries` while entries are still uploading. Raises `ArgumentError`.
- `max_file_size` is enforced server-side chunk by chunk. Client metadata is untrusted.
- Storing to `priv/static/uploads` triggers LiveReload in dev and does not work in multi-instance production. Use external storage for production.

## Component Forms

### Targeting events to a component

```heex
<.form for={@form} id={"card-#{@card.id}"} phx-submit="save" phx-target={@myself}>
  <.input field={@form[:title]} />
  <button type="submit">Save</button>
</.form>
```

`@myself` is only available in stateful `live_component` renders. It routes `phx-submit` and `phx-change` events to the component's `handle_event/3`.

### Source of truth rule

If a component's form modifies data **owned by the parent**, the component must notify the parent after saving. Never let component state diverge from parent state.

```elixir
# In the component
def handle_event("save", %{"card" => params}, socket) do
  socket.assigns.on_save.(params)
  {:noreply, socket}
end
```

```heex
<%!-- In the parent --%>
<.live_component
  module={CardFormComponent}
  id={"card-#{card.id}"}
  card={card}
  on_save={fn params -> send(self(), {:save_card, card.id, params}) end}
/>
```

### When to use a component vs. a function component

Use a `live_component` only when the form needs its own state or event handling (e.g., independent validation, local UI state). If the form just renders inputs and the parent handles all events, use a plain function component. Components add overhead for state tracking.

## HTTP Bridging with `phx-trigger-action`

For operations that require a traditional HTTP request (session mutation, OAuth redirect), validate in LiveView then trigger an HTTP form submission:

```heex
<.form
  for={@form}
  id="login-form"
  action={~p"/users/log_in"}
  phx-change="validate"
  phx-submit="save"
  phx-trigger-action={@trigger_submit}
>
  <.input field={@form[:email]} />
  <.input field={@form[:password]} type="password" />
  <button type="submit">Log in</button>
</.form>
```

```elixir
def mount(_params, _session, socket) do
  {:ok, assign(socket, form: to_form(%{}, as: :user), trigger_submit: false)}
end

def handle_event("validate", %{"user" => params}, socket) do
  form = to_form(params, as: :user, action: :validate)
  {:noreply, assign(socket, form: form)}
end

def handle_event("save", %{"user" => params}, socket) do
  case validate_credentials(params) do
    :ok ->
      {:noreply, assign(socket, trigger_submit: true)}

    {:error, message} ->
      # Reset trigger_submit to false so a subsequent retry does not immediately re-submit
      {:noreply, socket |> assign(trigger_submit: false) |> put_flash(:error, message)}
  end
end
```

When `phx-trigger-action` becomes `true`, LiveView disconnects and submits the form via HTTP POST to the `action` URL. Always reset `trigger_submit` back to `false` in failure paths — leaving it `true` causes the form to re-submit immediately on the next render.

## Input Edge Cases

### Number inputs

LiveView does not receive change events for invalid number input values. Browsers do not fire `input` events for them. Once the value becomes valid, events fire normally.

Workaround for full control: use a text input with numeric constraints:

```heex
<input type="text" inputmode="numeric" pattern="[0-9]*" name="amount" />
```

### Password inputs

Values are **never** reused from the server for security. You must explicitly set the value:

```heex
<.input field={@form[:password]} type="password" value={@form[:password].value} />
```

### Focused input protection

LiveView will **never** overwrite the value of a focused input, even if the server sends different data. This prevents the user from losing what they're typing during validation round-trips.

### Form reset

A `type="reset"` button clears all inputs client-side and triggers `phx-change` with `_target` containing the reset button's name:

```elixir
def handle_event("validate", %{"_target" => ["reset"]} = params, socket) do
  # Handle form reset: rebuild changeset from default values
  {:noreply, assign(socket, form: to_form(Accounts.change_user(%User{})))}
end
```

### The `_target` param

Every `phx-change` event includes a `"_target"` key indicating which input triggered the change:

```elixir
# User typed in the username field
%{"_target" => ["user", "username"], "user" => %{"username" => "Name"}}
```

Use this for conditional validation (e.g., only run expensive uniqueness checks when the relevant field changes).

## Anti-Patterns

**Lifecycle:**
- Storing raw changesets in assigns instead of calling `to_form/2`. Changesets are single-use; `to_form` normalizes them for the template.
- Using `:let={f}` with `<.form>` in LiveView. This bypasses change tracking optimizations.
- Omitting `id` on forms. Causes DOM patching issues and breaks recovery.

**Validation:**
- Setting `action: :validate` on mount. Shows errors before the user has done anything.
- Forgetting to set `action: :validate` during validation. Errors exist but are invisible.
- Building custom inputs that ignore `used_input?/1`. Shows errors for untouched fields.

**Recovery:**
- Assuming `phx-change` alone enables recovery. The form also needs an `id`.
- Testing recovery with LiveReload enabled. LiveReload does a full page reload, not a socket reconnect.

**Nested forms:**
- Omitting `on_replace: :delete` on `has_many`/`embeds_many`. Sort/drop params silently fail.
- Forgetting the empty drop hidden input outside `inputs_for`. Removing the last item is ignored.
- Using `type="submit"` on add/remove buttons. Triggers form submission instead of `phx-change`.
- See `references/nested-forms.md` for the full list of nested-form pitfalls.

**phx-trigger-action:**
- Not resetting `trigger_submit` to `false` in error branches. Causes the form to re-submit on the next render.

**Uploads:**
- Calling `consume_uploaded_entries` before uploads complete. Raises `ArgumentError`.
- Storing uploads in `priv/static`. Triggers LiveReload in dev, does not scale in production.

**Components:**
- Letting component form state diverge from parent data. Always notify the parent for data it owns.
- Using `live_component` when a function component suffices. Adds unnecessary state tracking overhead.

## References

- For loading states, submit feedback, and optimistic form interactions, see the `liveview-optimistic-ui` skill.
- [Phoenix.LiveView form bindings guide](https://hexdocs.pm/phoenix_live_view/form-bindings.html)
- [Phoenix.LiveView uploads guide](https://hexdocs.pm/phoenix_live_view/uploads.html)
- [Phoenix.Component.used_input?/1](https://hexdocs.pm/phoenix_live_view/Phoenix.Component.html#used_input?/1)
- [Ecto.Changeset.cast_embed/3](https://hexdocs.pm/ecto/Ecto.Changeset.html#cast_embed/3) for sort/drop params
