# Project Memory

A Claude Code skill that maintains durable, project-specific memory in `MEMORY.md` at the repository root. Persists preferences, conventions, and lessons learned across sessions.

## When to use

At session start (to load context), when the user says "remember this", "save this", or "don't do this again", or before substantial work in a project.

## What it covers

- **Initial session behavior**: How memory is loaded at start
- **Capturing new memory**: When and how to save new entries
- **Memory file format**: Structure of MEMORY.md (user preferences, project conventions, past mistakes, environment notes)
- **Applying memory**: How saved context influences future sessions
- **Best practices**: What to save and what to skip

## Usage

```
/project-memory
```

Memory is stored in `MEMORY.md` at the project root and persists across Claude Code sessions.
