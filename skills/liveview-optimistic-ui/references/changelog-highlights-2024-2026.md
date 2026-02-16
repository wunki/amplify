# LiveView Changelog Highlights (2024-2026)

Scope: items most relevant to responsive and optimistic UI behavior, based on LiveView changelogs from approximately Feb 2024 through Feb 2026.
Reviewed on: 2026-02-16.

## Why this matters

Optimistic UI is sensitive to patch ordering, form lock behavior, stream diffs, and command semantics. Small client/runtime fixes can change perceived UX quality dramatically under latency.

## High-impact timeline

### 2024-02 to 2024-06 (`0.20.x` and `1.0.0-rc.*`)

- `0.20.6` to `0.20.16`: multiple stream and acknowledgement bug fixes, important for list-heavy optimistic UIs.
- `1.0.0-rc.6`: adds `blocking: false` for transition-capable JS commands, useful when transition blocking hurts responsiveness.
- `1.0.0-rc.7`:
  - adds `to: {:inner, ...}` and `to: {:closest, ...}` for JS commands,
  - exposes programmable JS command interface to hooks,
  - exports `createHook` for custom element interop.
- `1.0.0-rc.8`:
  - fixes submitter handling with `JS.push`,
  - fixes latency simulator race that could apply messages out of order,
  - includes focused input and rapid update stability fixes.

### 2024-12 (`1.0.0` / `1.0.1`)

- Removes `phx-page-loading` attribute in favor of `JS.push(..., page_loading: true)`.
- Moves input feedback toward `used_input?` and server-rendered feedback model.

### 2025-06 to 2025-07 (`1.1.0-rc.*` to `1.1.0`)

- `1.1.0-rc.0`: adds `JS.ignore_attributes/1`, crucial for browser-managed attrs (`open`, etc.) that would otherwise be overwritten by patches.
- `1.1.0-rc.0`: introduces colocated hooks/JS and typed public JS interfaces, making richer optimistic flows easier to compose safely.
- `1.1.0-rc.2` / `1.1.0`: change tracking in comprehensions by default and `:key` improvements, reducing payloads and improving perceived responsiveness for list updates.

### 2025-08 to 2025-11 (`1.1.5+`)

- `1.1.5`: adds `stream_async/4` for asynchronous stream insertion.
- `1.1.9`: adds richer metadata for `phx:page-loading-start` in error scenarios, useful for global loading instrumentation.
- `1.1.16`: fixes `phx-disable-with` whitespace restoration regression.
- `1.1.18`:
  - fixes boolean handling in `JS.ignore_attributes`,
  - adds `onDocumentPatch` DOM callback and event dispatch phase options (useful for custom transition integrations).

### 2026-01 to 2026-02 (`1.1.20+`)

- Portal-related event/form fixes and stream delete/reset correctness (`1.1.20`, `1.1.21`) matter if optimistic interactions happen inside teleported UI.

## Design implications for this skill

1. Prefer `JS.push` + local visual transition over waiting for round-trip.
2. Use scoped selectors (`:closest`, `:inner`) to reduce selector fragility.
3. For browser-controlled attrs, use `JS.ignore_attributes` instead of reapplying values in hooks.
4. Treat streams and keyed comprehensions as first-class tools for fast list UX.
5. Use the latency simulator regularly while iterating on optimistic patterns.
6. Re-test optimistic flows during LiveView upgrades because runtime ordering and lock behaviors evolve.

## Concurrency model reminder (José Valim)

Concurrent submission + revalidation over independent HTTP requests can expose stale data without causal ordering. LiveView's persistent channel model avoids this class of UI rollback issues when events are handled in channel order and server mutation logic remains deterministic.

## Source links

- LiveView changelog (current): https://hexdocs.pm/phoenix_live_view/changelog.html
- LiveView changelog (`v1.0` branch): https://github.com/phoenixframework/phoenix_live_view/blob/v1.0/CHANGELOG.md
- LiveView changelog (`v1.1.23` tag): https://github.com/phoenixframework/phoenix_live_view/blob/v1.1.23/CHANGELOG.md
- Syncing changes guide: https://hexdocs.pm/phoenix_live_view/syncing-changes.html
- `Phoenix.LiveView.JS` docs: https://hexdocs.pm/phoenix_live_view/Phoenix.LiveView.JS.html
- José Valim video: https://www.youtube.com/watch?v=fCdi7SEPrTs
- LiveView JS commands video: https://www.youtube.com/watch?v=BRUTYHBJ_Z4
- José Valim article: https://dashbit.co/blog/remix-concurrent-submissions-flawed
