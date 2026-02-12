---
name: code-simplifier
description: Simplify and refine existing code for clarity, consistency, and maintainability while preserving behavior. Use when asked to "simplify code", "clean this up", "refactor for readability", "reduce complexity", or to polish recently modified code without changing functionality.
---

# Code Simplifier

Refine code so it is easier to read, reason about, and maintain, while preserving behavior.

## Guardrails

1. Preserve functionality. Do not change outputs, side effects, interfaces, or user-visible behavior.
2. Stay in scope. Prioritize recently modified files unless the user asks for broader cleanup.
3. Follow project conventions from local instructions (for example `AGENTS.md`, lint rules, and existing patterns).
4. Prefer explicit, maintainable code over clever compression.

## Workflow

1. Identify target files and confirm the intended scope.
2. Find complexity hotspots:
   - Deep nesting or confusing control flow
   - Duplicate or redundant logic
   - Overly broad functions or components
   - Dead code, unused parameters, or unnecessary abstractions
3. Simplify safely:
   - Break large units into focused helpers when it improves readability
   - Replace nested ternaries with clearer branching
   - Use descriptive names for values, functions, and booleans
   - Remove comments that only restate obvious code
4. Verify behavior is unchanged by running relevant tests or checks for touched areas.
5. Summarize only meaningful simplifications and any assumptions made.

## Quality Bar

- The resulting code should be easier for a new contributor to modify correctly.
- If a simplification would increase ambiguity or risk, do not apply it.
- Favor root-cause cleanup over cosmetic edits.
