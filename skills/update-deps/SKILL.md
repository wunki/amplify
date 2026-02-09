---
name: update-deps
description: Update Elixir dependencies in mix.exs safely, including patch/minor upgrades, major-version migrations, and verification. Use when asked to update deps, bump packages, or resolve outdated Mix/Hex dependencies.
---

# Update Elixir Dependencies

Use this workflow for Elixir projects that use Mix + Hex.

## Workflow

### 1. Baseline And Scope

1. Confirm a clean baseline with `git status --short`.
2. Identify outdated dependencies with `mix hex.outdated`.
3. Split findings into:
   - Patch/minor upgrades (usually non-breaking).
   - Major upgrades (potentially breaking).

### 2. Apply Patch/Minor Upgrades First

1. Update dependencies that do not require major version constraint changes.
2. Prefer targeted updates for easier debugging:
   - `mix deps.update <dep_name>`
3. If many safe updates exist and risk is low, `mix deps.update --all` is acceptable.
4. Run verification (Section 4) before touching major upgrades.

### 3. Handle Major Upgrades One Dependency At A Time

For each dependency with a major bump:

1. Update the version constraint in `mix.exs`.
2. Gather migration notes from primary sources, in this order:
   - `mix hex.info <dep_name>` to find package/repo links.
   - `https://hexdocs.pm/<dep_name>` (look for changelog, migration, or upgrade sections).
   - Repository `CHANGELOG*`, release notes, and upgrade guides.
3. Extract only changes relevant to the jump from current to target major version.
4. Implement required code/config updates.
5. Run verification (Section 4) before moving to the next major dependency.

If a major upgrade fails verification and cannot be resolved quickly:
1. Revert only that dependency change.
2. Continue with other upgrades.
3. Report the blocker with exact failing errors and required follow-up.

### 4. Verification

Run these commands after each update batch and after each major dependency:

```sh
mix compile --warnings-as-errors
mix format --check-formatted
mix test
```

If the project defines additional CI checks, run the same checks used in `.github/workflows`.

Failure handling:
- Compile warnings/errors: fix code or config issues introduced by the upgrade.
- Format check failures: run `mix format`.
- Test failures: fix behavior regressions before proceeding.

### 5. Completion

1. Run `mix hex.outdated` again and confirm the remaining items (if any) are intentional.
2. Summarize:
   - Dependencies updated and final versions.
   - Major migrations performed and code changes required.
   - Any intentionally deferred upgrades and why.
