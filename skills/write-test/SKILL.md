---
name: write-test
description: Guides coverage-driven test writing for existing codebases: discovers untested user-facing behavior via coverage reports, writes one meaningful test per iteration, and marks low-value code with ignore annotations. Use when asked to "write tests", "add test coverage", "increase coverage", "test this feature", or when a coverage report shows gaps in a working codebase. Don't use for setting up a test framework from scratch, writing e2e or integration test suites, explaining testing theory, or reviewing existing tests without writing new ones.
---

# Write Test

Write tests that catch regressions users would notice. Use coverage as a discovery tool, not a target.

## What Makes a Great Test

A great test covers behavior users depend on — a feature that, if broken, would frustrate or block users. It validates real workflows, not implementation details. It catches regressions before users do.

**Do NOT write tests just to increase coverage.** Use coverage as a guide to find untested user-facing behavior.

If uncovered code is not worth testing (boilerplate, unreachable error branches, internal plumbing), add the appropriate ignore annotation instead of writing a low-value test.

## Process

1. **Locate the test runner** — check `package.json` scripts and CI config (`.github/workflows/`) to find the project's actual test command. If no test infrastructure exists at all, stop and tell the user: this skill requires an existing test runner.
2. **Run coverage** using the command from Step 1. See the Coverage Commands table below for common runner flags.
3. **Find the test file location pattern** — scan existing test files to determine naming convention (`.test.ts`, `.spec.ts`, `_test.go`, `test_*.py`) and placement (`__tests__/`, colocated, or dedicated `test/` directory).
4. **Read the uncovered lines** and identify the most important user-facing feature that lacks tests.
   - Prioritize: error handling users will hit, CLI commands, git operations, file parsing, public API methods
   - Deprioritize: internal utilities, edge cases users won't encounter, boilerplate
5. **Write ONE meaningful test** that validates the feature works correctly for users. Follow the file location pattern from Step 3. If creating a new test file, match the naming convention of existing test files exactly.
6. **Run coverage again** — coverage should increase as a side effect of testing real behavior. If it does not increase after a valid test, verify the test file is included in the runner's glob pattern.
7. **Repeat from Step 4** until the coverage target is reached or all user-facing behavior is tested. If coverage is stuck and no meaningful behavior remains untested, stop and mark remaining uncovered lines with ignore annotations.

## Guidelines

- **One test per iteration.** Focus beats breadth.
- **Test behavior, not implementation.** Refactoring internals should not break tests.
- **Name tests as user stories.** `"returns error when file not found"` not `"test getFile function"`.
- **Skip mocks when possible.** Real dependencies catch real bugs.

## Coverage Commands

Check `package.json` scripts or CI config first. If no script exists, use the runner's native flag:

| Runner | Coverage command |
|--------|-----------------|
| vitest | `npx vitest --coverage` |
| jest | `npx jest --coverage` |
| c8/node | `npx c8 node --test` |
| bun | `bun test --coverage` |
| go | `go test -cover ./...` |
| pytest | `pytest --cov` |
| cargo | `cargo tarpaulin` |

If the runner is not in this table, look for a `--coverage` or `--cov` flag in the runner's docs, or check the CI workflow for the exact invocation.

## Ignore Annotations

Use the annotation that matches the project's coverage tool — not all projects use V8:

| Tool | Annotation |
|------|------------|
| V8 / vitest (v8) | `/* v8 ignore next */` or `/* v8 ignore start */ … /* v8 ignore stop */` |
| Istanbul / jest | `/* istanbul ignore next */` or `/* istanbul ignore if */` |
| pytest-cov | `# pragma: no cover` |
| Go | No standard annotation; exclude files via `go test -coverprofile` flags or build tags |

## When to Stop

- All user-facing behavior has tests.
- Remaining uncovered code is internal plumbing (mark with the appropriate ignore annotation).
- Coverage target reached, if one was specified.
- Diminishing returns: remaining tests would only cover unlikely error paths with no user impact.
