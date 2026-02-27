## Table of Contents

- [inputs_for basics](#inputsfor-basics)
- [cast_embed vs cast_assoc](#castembed-vs-castassoc)
- [Dynamic add/remove with sort and drop params](#dynamic-addremove-with-sort-and-drop-params)
- [Key requirements](#key-requirements)
- [Nested field used_input?](#nested-field-usedinput)

---

## inputs_for basics

```heex
<.inputs_for :let={ef} field={@form[:emails]}>
  <.input field={ef[:address]} label="Email" />
</.inputs_for>
```

---

## cast_embed vs cast_assoc

`sort_param` and `drop_param` work with both `cast_embed/3` and `cast_assoc/3`. Choose based on where the data lives:

| Scenario | Use |
|---|---|
| Nested data stored in a JSONB column or no separate table | `cast_embed` with `embeds_many` |
| Nested data in its own DB table with a foreign key | `cast_assoc` with `has_many` |

Both require `on_replace: :delete` on the association or embed definition.

**cast_assoc example (has_many with a separate table):**

```elixir
# Schema
schema "lists" do
  field :title, :string
  has_many :emails, Email, on_replace: :delete
end

def changeset(list, attrs) do
  list
  |> cast(attrs, [:title])
  |> cast_assoc(:emails,
    with: &Email.changeset/2,
    sort_param: :emails_sort,
    drop_param: :emails_drop
  )
end
```

**cast_embed example (embeds_many in same table):**

```elixir
# Schema
embeds_many :emails, Email, on_replace: :delete do
  field :address, :string
end

def changeset(list, attrs) do
  list
  |> cast(attrs, [:title])
  |> cast_embed(:emails,
    with: &email_changeset/2,
    sort_param: :emails_sort,
    drop_param: :emails_drop
  )
end
```

**Minimum Ecto version:** `sort_param` and `drop_param` were added in **Ecto 3.10.0**. If the option is silently ignored or raises, check the Ecto version in `mix.exs`.

---

## Dynamic add/remove with sort and drop params

The template is the same for both `cast_assoc` and `cast_embed`:

```heex
<.inputs_for :let={ef} field={@form[:emails]}>
  <input type="hidden" name="list[emails_sort][]" value={ef.index} />
  <.input field={ef[:address]} label="Email" />
  <button
    type="button"
    name="list[emails_drop][]"
    value={ef.index}
    phx-click={JS.dispatch("change")}
  >
    Remove
  </button>
</.inputs_for>

<%!-- Required: empty drop input so all items can be removed --%>
<input type="hidden" name="list[emails_drop][]" />

<%!-- Add button --%>
<button
  type="button"
  name="list[emails_sort][]"
  value="new"
  phx-click={JS.dispatch("change")}
>
  Add email
</button>
```

---

## Key requirements

- Add/remove buttons must be `type="button"` to prevent form submission.
- `JS.dispatch("change")` triggers the form's `phx-change` event, which rebuilds the changeset with the new sort/drop values.
- The empty `<input type="hidden" name="list[emails_drop][]" />` **outside** `inputs_for` is required. Without it, removing the last item sends no drop param and the delete is silently ignored.
- Do not access `form[:field].value` in nested forms for display logic. The value may be a struct, changeset, or raw params depending on state. Compute derived values in the LiveView or changeset instead.

---

## Nested field used_input?

A nested field group (like a date with year/month/day sub-fields) is considered "used" if **any** of its sub-fields have been interacted with.

`used_input?/1` requires Phoenix LiveView 0.20+. On earlier versions, errors are shown unconditionally once the changeset action is set.

---

## Schemas without a primary key

`inputs_for` requires a stable key to track items across renders. For schemas with `@primary_key false`, Phoenix falls back to index-based tracking. This means reordering can cause state mismatches. Options:

1. Add an `id` field (even a client-generated UUID) to the embedded schema.
2. Accept index-based tracking and ensure reordering is always a full rebuild (not a partial update).
