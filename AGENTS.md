# Amplify

Configuration repository for AI coding agents. Manages skills, commands, and settings across Claude Code, OpenCode, Codex, and Amp.

## Structure

```
commands/         Markdown workflow templates (YAML frontmatter + steps)
skills/           Modular capability packages (SKILL.md + scripts/references)
config/           Tool-specific configs and the shared AGENTS.md template
Makefile          Symlinks configs, rsyncs skills/commands to tool directories
```

## Key Files

- `config/AGENTS.md` - Shared agent profile symlinked to all tools. This is the template, not project-specific.
- `Makefile` - Run `make` to install to all detected tools, or `make <tool>` for one.

## Working Here

**Config files** are symlinked (changes propagate immediately).
**Skills and commands** are rsynced (run `make` after changes).

### Adding a Skill

1. Create `skills/<name>/SKILL.md` with frontmatter:
   ```yaml
   ---
   name: skill-name
   description: What it does. Include trigger phrases.
   ---
   ```
2. Add `scripts/` for executable code, `references/` for docs loaded on-demand.
3. Run `make`.

### Adding a Command

1. Create `commands/<name>.md` with frontmatter:
   ```yaml
   ---
   description: What the command does
   ---
   ```
2. Add step-by-step instructions.
3. Run `make`.

### Adding a Tool

1. Add detection: `HAS_<TOOL> := $(shell command -v <tool> 2>/dev/null)`
2. Add target to `all` block.
3. Create target with mkdir, symlinks, and rsync commands.
4. Add tool config to `config/<tool>/`.

## Conventions

- Skill descriptions must include trigger phrases (it's all Claude sees to decide whether to load).
- Keep SKILL.md lean (<500 lines); put detailed docs in `references/`.
- Use kebab-case for directories and files.
- Imperative mood in instructions ("Add...", "Fix...", "Verify...").
