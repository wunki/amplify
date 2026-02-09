.PHONY: all claude opencode codex amp scripts clean reset

HAS_CLAUDE := $(shell command -v claude 2>/dev/null)
HAS_OPENCODE := $(shell command -v opencode 2>/dev/null)
HAS_CODEX := $(shell command -v codex 2>/dev/null)
HAS_AMP := $(shell command -v amp 2>/dev/null)

# Auto-discover from repo directories
SKILLS := $(wildcard skills/*)
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
	mkdir -p ~/.claude/skills ~/.claude/agents
	ln -sf $(CURDIR)/config/AGENTS.md ~/.claude/CLAUDE.md
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
	mkdir -p ~/.claude/skills ~/.config/opencode/agent
	ln -sf $(CURDIR)/config/AGENTS.md ~/.config/opencode/AGENTS.md
	ln -sf $(CURDIR)/config/opencode/opencode.json ~/.config/opencode/opencode.json
	ln -sfn $(CURDIR)/config/opencode/themes ~/.config/opencode/themes
	ln -sf $(CURDIR)/config/opencode/tool ~/.config/opencode/tool
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.claude/skills/$$(basename $$skill)/; \
	done
	@for agent in $(AGENTS); do \
		sed -e 's/model: sonnet/model: openai\/gpt-5.2-codex/g' \
		    -e 's/model: opus/model: openai\/gpt-5.2-codex/g' \
		    -e 's/model: haiku/model: openai\/gpt-5.2-codex/g' \
		    -e 's/model: codex/model: openai\/gpt-5.2-codex/g' \
		    $(CURDIR)/$$agent > ~/.config/opencode/agent/$$(basename $$agent); \
	done

codex:
	@echo "Installing for Codex..."
	mkdir -p ~/.codex/skills
	ln -sf $(CURDIR)/config/AGENTS.md ~/.codex/AGENTS.md
	ln -sf $(CURDIR)/config/codex/config.toml ~/.codex/config.toml
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.codex/skills/$$(basename $$skill)/; \
	done

amp:
	@echo "Installing for Amp..."
	mkdir -p ~/.config/amp/skills
	ln -sf $(CURDIR)/config/AGENTS.md ~/.config/amp/AGENTS.md
	ln -sf $(CURDIR)/config/amp/settings.json ~/.config/amp/settings.json
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
	@echo "Removing installed skills and agents..."
ifdef HAS_CLAUDE
	rm -rf ~/.claude/skills ~/.claude/agents
endif
ifdef HAS_OPENCODE
	rm -rf ~/.config/opencode/skills ~/.config/opencode/skill ~/.config/opencode/agent
endif
ifdef HAS_CODEX
	rm -rf ~/.codex/skills
endif
ifdef HAS_AMP
	rm -rf ~/.config/amp/skills
endif
	@for script in $(SCRIPTS); do \
		rm -f ~/.local/bin/$$(basename $$script); \
	done
	@echo "Done. Run 'make' to reinstall."

reset:
	@$(MAKE) clean
	@$(MAKE) all
