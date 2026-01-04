.PHONY: all claude opencode codex amp

HAS_CLAUDE := $(shell command -v claude 2>/dev/null)
HAS_OPENCODE := $(shell command -v opencode 2>/dev/null)
HAS_CODEX := $(shell command -v codex 2>/dev/null)
HAS_AMP := $(shell command -v amp 2>/dev/null)

# Auto-discover from repo directories
SKILLS := $(wildcard skills/*)
COMMANDS := $(wildcard commands/*)
AGENTS := $(wildcard agents/*)

all:
ifdef HAS_CLAUDE
	@$(MAKE) claude
endif
ifdef HAS_OPENCODE
	@$(MAKE) opencode
endif
ifdef HAS_CODEX
	@$(MAKE) codex
endif
ifdef HAS_AMP
	@$(MAKE) amp
endif

claude:
	@echo "Installing for Claude Code..."
	mkdir -p ~/.claude/commands ~/.claude/skills ~/.claude/agents
	ln -sf $(CURDIR)/config/AGENTS.md ~/.claude/CLAUDE.md
	@for cmd in $(COMMANDS); do \
		rsync -a $(CURDIR)/$$cmd ~/.claude/commands/; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.claude/skills/$$(basename $$skill)/; \
	done
	@for agent in $(AGENTS); do \
		rsync -a $(CURDIR)/$$agent ~/.claude/agents/; \
	done

opencode:
	@echo "Installing for OpenCode..."
	mkdir -p ~/.config/opencode/command ~/.config/opencode/skills
	ln -sf $(CURDIR)/config/AGENTS.md ~/.config/opencode/AGENTS.md
	ln -sf $(CURDIR)/config/opencode/opencode.json ~/.config/opencode/opencode.json
	ln -sf $(CURDIR)/config/opencode/themes ~/.config/opencode/themes
	ln -sf $(CURDIR)/config/opencode/tool ~/.config/opencode/tool
	@for cmd in $(COMMANDS); do \
		rsync -a $(CURDIR)/$$cmd ~/.config/opencode/command/; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.config/opencode/skills/$$(basename $$skill)/; \
	done

codex:
	@echo "Installing for Codex..."
	mkdir -p ~/.codex/skills ~/.codex/commands
	ln -sf $(CURDIR)/config/codex/config.toml ~/.codex/config.toml
	@for cmd in $(COMMANDS); do \
		rsync -a $(CURDIR)/$$cmd ~/.codex/commands/; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.codex/skills/$$(basename $$skill)/; \
	done

amp:
	@echo "Installing for Amp..."
	mkdir -p ~/.config/amp/skills ~/.config/amp/commands
	ln -sf $(CURDIR)/config/amp/settings.json ~/.config/amp/settings.json
	@for cmd in $(COMMANDS); do \
		rsync -a $(CURDIR)/$$cmd ~/.config/amp/commands/; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.config/amp/skills/$$(basename $$skill)/; \
	done
