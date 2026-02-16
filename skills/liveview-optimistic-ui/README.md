# LiveView Optimistic UI

A Claude Code skill for building LiveView interactions that feel instant while preserving server truth. Covers JS commands, streams, error recovery, race conditions, and accessibility.

## When to use

When working with optimistic UI, instant feedback, `JS.push`, loading states, flicker/race issues, double submit, "feels slow", undo/rollback, stale data, stream animations, `used_input?`, or `aria-live` accessibility in LiveView.

## What it covers

- **Core Model**: Client feedback first, server truth always
- **Workflow**: Classify interactions, choose loading feedback, compose JS, plan for failure
- **Baseline Patterns**: Optimistic delete, instant toggle, ARIA transitions, page-level loading, multi-element loading
- **Stream Optimistic Patterns**: Temp ID insert/swap, transition-timed delete, `stream_async`
- **Error Recovery**: Server-driven revert, explicit revert via `push_event`, undo windows
- **Race Conditions**: Request ID tracking, optimistic locking, concurrent click serialization
- **Accessibility**: `aria-live` announcements, `aria-busy`, `prefers-reduced-motion`
- **Testing**: LiveViewTest patterns, `render_async`, latency simulation
- **Colocated Hooks**: v1.1+ patterns with `Phoenix.LiveView.ColocatedHook`
- **Anti-Patterns**: Categorized pitfalls for feedback timing, DOM, streams, forms, state, accessibility

All patterns verified against LiveView v1.1.23 source.

## Files

- `SKILL.md` - Main skill definition
- `references/js-commands-cookbook.md` - JS command syntax and composition patterns
- `references/changelog-highlights-2024-2026.md` - Version-sensitive behavior and upgrade notes

## Related skills

- `liveview-forms` - For form lifecycle, validation, recovery, nested forms, uploads

## Usage

```
/liveview-optimistic-ui
```
