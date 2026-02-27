.PHONY: all claude scripts agent-skills clean cleanup reset

HAS_CLAUDE := $(shell command -v claude 2>/dev/null)

# Auto-discover from repo directories
SKILLS := $(wildcard skills/*)
AGENTS := $(wildcard agents/*)
SCRIPTS := $(wildcard scripts/*)
LEGACY_SKILL_NAMES := scratchpad

# Shared skills destination for all agents except Claude Code
AGENTS_SKILLS_DIR := $(HOME)/.agents/skills

all:
ifdef HAS_CLAUDE
	@$(MAKE) claude
endif
	@$(MAKE) agent-skills
	@$(MAKE) scripts

claude:
	@echo "Installing for Claude Code..."
	mkdir -p ~/.claude/skills ~/.claude/agents
	ln -sf $(CURDIR)/config/AGENTS.md ~/.claude/CLAUDE.md
	@for legacy in $(LEGACY_SKILL_NAMES); do \
		rm -rf ~/.claude/skills/$$legacy; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ ~/.claude/skills/$$(basename $$skill)/; \
	done
	@for agent in $(AGENTS); do \
		sed -e 's/model: codex/model: claude-opus-4-5/g' \
		    -e '/^reasoningEffort:/d' \
		    $(CURDIR)/$$agent > ~/.claude/agents/$$(basename $$agent); \
	done

agent-skills:
	@echo "Installing skills to $(AGENTS_SKILLS_DIR)..."
	mkdir -p $(AGENTS_SKILLS_DIR)
	@for legacy in $(LEGACY_SKILL_NAMES); do \
		rm -rf $(AGENTS_SKILLS_DIR)/$$legacy; \
	done
	@for skill in $(SKILLS); do \
		rsync -a $(CURDIR)/$$skill/ $(AGENTS_SKILLS_DIR)/$$(basename $$skill)/; \
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
	rm -rf $(AGENTS_SKILLS_DIR)
ifdef HAS_CLAUDE
	rm -rf ~/.claude/skills ~/.claude/agents
endif
	@for script in $(SCRIPTS); do \
		rm -f ~/.local/bin/$$(basename $$script); \
	done
	@echo "Done. Run 'make' to reinstall."

cleanup:
	@bash "$(CURDIR)/scripts/cleanup"

reset:
	@echo "Reinstalling without deleting custom skills..."
	@$(MAKE) all
	@echo ""
	@echo "Review stale installed skills/agents and choose what to remove:"
	@if [ -t 0 ]; then \
		$(MAKE) cleanup; \
	else \
		bash "$(CURDIR)/scripts/cleanup" --dry-run; \
	fi
