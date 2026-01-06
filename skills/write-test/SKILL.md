---
name: write-test
description: Write meaningful tests using coverage as a guide to find untested user-facing behavior. Use when asked to "write tests", "add test coverage", "increase coverage", "test this feature", or when coverage reports show gaps. Focuses on one test per iteration, prioritizing real user workflows over implementation details.
---

# Write Test

Write tests that catch regressions users would notice. Use coverage as a discovery tool, not a target.

## What Makes a Great Test

A great test covers behavior users depend on. It tests a feature that, if broken, would frustrate or block users. It validates real workflows, not implementation details. It catches regressions before users do.

**Do NOT write tests just to increase coverage.** Use coverage as a guide to find UNTESTED USER-FACING BEHAVIOR.

If uncovered code is not worth testing (boilerplate, unreachable error branches, internal plumbing), add `/* v8 ignore next */` or `/* v8 ignore start */` comments instead of writing low-value tests.

## Process

1. **Run coverage** to see which files have low coverage
2. **Read the uncovered lines** and identify the most important USER-FACING FEATURE that lacks tests
   - Prioritize: error handling users will hit, CLI commands, git operations, file parsing
   - Deprioritize: internal utilities, edge cases users won't encounter, boilerplate
3. **Write ONE meaningful test** that validates the feature works correctly for users
4. **Run coverage again** - coverage should increase as a side effect of testing real behavior
5. **Repeat** until coverage target is reached or all user-facing behavior is tested

## Guidelines

- **One test per iteration.** Focus beats breadth.
- **Test behavior, not implementation.** If you refactor internals, tests should still pass.
- **Name tests as user stories.** `"returns error when file not found"` not `"test getFile function"`.
- **Skip mocks when possible.** Real dependencies catch real bugs.

## Coverage Commands

Adapt to the project's test runner:

| Runner | Command |
|--------|---------|
| vitest | `npx vitest --coverage` |
| jest | `npx jest --coverage` |
| c8/node | `npx c8 node --test` |
| go | `go test -cover ./...` |
| pytest | `pytest --cov` |

Check `package.json` scripts or CI config for the project's preferred command.

## When to Stop

- All user-facing behavior has tests
- Remaining uncovered code is internal plumbing (mark with ignore comments)
- Coverage target reached (if specified)
- Diminishing returns: tests would only cover unlikely error paths
