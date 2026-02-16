# LiveView Forms

A Claude Code skill for building correct, resilient forms in Phoenix LiveView. Covers the full form lifecycle from validation to reconnect recovery.

## When to use

When working with LiveView forms: `phx-change`, `phx-submit`, validation, changesets, `to_form`, reconnect recovery, nested forms, uploads, `phx-debounce`, `used_input?`, `inputs_for`, `phx-trigger-action`, or component forms with `phx-target`.

## What it covers

- **Form Lifecycle**: Mount, validate, submit pattern with `to_form/2`
- **Error Feedback Model**: Two-layer system (changeset action + `used_input?/1`) with a "why aren't errors showing?" checklist
- **Debouncing and Throttling**: `phx-debounce`, `phx-throttle`, defaults, timer reset behavior
- **Form Recovery on Reconnect**: `phx-auto-recover`, custom recovery for wizards, disabling recovery
- **Nested Forms**: `inputs_for`, dynamic add/remove with `sort_param`/`drop_param`
- **Uploads**: `allow_upload`, `consume_uploaded_entries`, auto-upload with progress
- **Component Forms**: `phx-target`, `@myself`, source of truth rules
- **HTTP Bridging**: `phx-trigger-action` for session mutations
- **Input Edge Cases**: Number inputs, password reuse, focused input protection, form reset
- **Anti-Patterns**: 12 categorized pitfalls

All patterns verified against LiveView v1.1.23 source.

## Related skills

- `liveview-optimistic-ui` - For loading states, submit feedback, and optimistic interactions

## Usage

```
/liveview-forms
```
