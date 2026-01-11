.PHONY: all claude opencode codex amp scripts clean

HAS_CLAUDE := $(shell command -v claude 2>/dev/null)
HAS_OPENCODE := $(shell command -v opencode 2>/dev/null)
HAS_CODEX := $(shell command -v codex 2>/dev/null)
HAS_AMP := $(shell command -v amp 2>/dev/null)

# Auto-discover from repo directories
SKILLS := $(wildcard skills/*)
COMMANDS := $(wildcard commands/*)
AGENTS := $(wildcard agents/*)
SCRIPTS := $(wildcard scripts/*)

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
	@$(MAKE) scripts

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
		sed -e 's/model: codex/model: claude-opus-4-5/g' \
		    -e '/^reasoningEffort:/d' \
		    $(CURDIR)/$$agent > ~/.claude/agents/$$(basename $$agent); \
	done

opencode:
	@echo "Installing for OpenCode..."
	mkdir -p ~/.config/opencode/command ~/.config/opencode/skill ~/.config/opencode/agent
	ln -sf $(CURDIR)/config/AGENTS.md ~/.config/opencode/AGENTS.md
	ln -sf $(CURDIR)/config/opencode/opencode.json ~/.config/opencode/opencode.json
	ln -sfn $(CURDIR)/config/opencode/themes ~/.config/opencode/themes
	ln -sf $(CURDIR)/config/opencode/tool ~/.config/opencode/tool
	@for cmd in $(COMMANDS); do \
		rsync -a $(CURDIR)/$$cmd ~/.config/opencode/command/; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.config/opencode/skill/$$(basename $$skill)/; \
	done
	@for agent in $(AGENTS); do \
		sed -e 's/model: sonnet/model: anthropic\/claude-sonnet-4-5/g' \
		    -e 's/model: opus/model: anthropic\/claude-opus-4-5/g' \
		    -e 's/model: haiku/model: anthropic\/claude-haiku-3-5/g' \
		    -e 's/model: codex/model: openai\/gpt-5.2-codex/g' \
		    $(CURDIR)/$$agent > ~/.config/opencode/agent/$$(basename $$agent); \
	done

codex:
	@echo "Installing for Codex..."
	mkdir -p ~/.codex/skills ~/.codex/commands
	ln -sf $(CURDIR)/config/AGENTS.md ~/.codex/AGENTS.md
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
	ln -sf $(CURDIR)/config/AGENTS.md ~/.config/amp/AGENTS.md
	ln -sf $(CURDIR)/config/amp/settings.json ~/.config/amp/settings.json
	@for cmd in $(COMMANDS); do \
		rsync -a $(CURDIR)/$$cmd ~/.config/amp/commands/; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.config/amp/skills/$$(basename $$skill)/; \
	done

scripts:
	@echo "Installing scripts to ~/.local/bin..."
	mkdir -p ~/.local/bin
	@for script in $(SCRIPTS); do \
		ln -sf $(CURDIR)/$$script ~/.local/bin/$$(basename $$script); \
	done
	@echo "Ensure ~/.local/bin is in your PATH"

clean:
	@echo "Removing installed skills and commands..."
ifdef HAS_CLAUDE
	rm -rf ~/.claude/skills ~/.claude/commands ~/.claude/agents
endif
ifdef HAS_OPENCODE
	rm -rf ~/.config/opencode/skill ~/.config/opencode/command ~/.config/opencode/agent
endif
ifdef HAS_CODEX
	rm -rf ~/.codex/skills ~/.codex/commands
endif
ifdef HAS_AMP
	rm -rf ~/.config/amp/skills ~/.config/amp/commands
endif
	@for script in $(SCRIPTS); do \
		rm -f ~/.local/bin/$$(basename $$script); \
	done
	@echo "Done. Run 'make' to reinstall."
