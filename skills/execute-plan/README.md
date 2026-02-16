# Execute Plan

A Claude Code skill that works through PLAN.md one task at a time with human oversight. Picks up where you left off and tracks progress.

## When to use

Trigger phrases: "execute", "execute plan", "continue", "next task", "work on the plan", "pick up where I left off", "resume", or any request to make progress on PLAN.md.

## What it covers

- **Core Principles**: One task at a time, human approval between steps
- **Workflow**: How tasks are picked up, executed, and marked complete
- **Plan Mutations**: How the plan adapts when requirements change mid-execution
- **Action Items**: How individual tasks are structured and tracked
- **Learning Persistence**: Capturing lessons learned during execution
- **Anti-patterns**: Common execution mistakes

## Files

- `SKILL.md` - Main skill definition
- `references/summary-examples.md` - Examples of task completion summaries

## Usage

```
/execute-plan
```

Requires a `PLAN.md` file, typically created by the `create-plan` skill.
