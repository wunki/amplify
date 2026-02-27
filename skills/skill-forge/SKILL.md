---
name: skill-forge
description: Create, update, or validate agent skills — SKILL.md authoring, frontmatter writing, bundled resource planning, and three-phase discoverability validation. Use when the user says "create a skill", "make a new skill", "write a skill for", "forge a skill", "update this SKILL.md", or asks for help with skill frontmatter, skill structure, or skill validation probes. Don't use for README writing, AGENTS.md configuration, general agent documentation, or anything that isn't a SKILL.md file or its bundled resources.
---

# Skill Forge

Creates and validates agent skills end-to-end: scaffolding, editing, validation, and packaging.

## Workflow

1. Understand the skill with concrete examples
2. Plan reusable contents (scripts, references, assets)
3. Initialize or locate the skill directory
4. Edit the skill — write SKILL.md and populate resources
5. Validate — run the three-phase validation protocol
6. Package the skill
7. Iterate based on real usage

---

## Step 1: Understand with Concrete Examples

Ask until the usage patterns are unambiguous. Stop when these three questions have clear answers:

1. What specific user requests should trigger this skill? (Get at least 2–3 concrete examples.)
2. What should NOT trigger this skill? (Needed for negative triggers in the description.)
3. Are there multiple modes or variants (e.g., frameworks, file types, domains)?

Avoid asking more than two questions per turn. Move to Step 2 once all three questions are answered — do not wait for perfect information.

---

## Step 2: Plan Reusable Contents

For each concrete example from Step 1, decide:

- `scripts/` — Code rewritten identically every time → extract to a script
- `references/` — Dense context loaded only when needed → move to reference files
- `assets/` — Output templates, boilerplate, fonts, images → assets

---

## Step 3: Initialize or Locate the Skill

**Creating a new skill:** Run the scaffolding script. Prerequisites: Python 3 (`python3 --version`) and PyYAML (`pip install pyyaml`) must be available. If `python3` is not found, try `python`.

```bash
python3 skills/skill-creator/scripts/init_skill.py <skill-name> --path skills/
```

The max skill name length is 64 characters. (Ignore the "Max 40 characters" note in `init_skill.py`'s help text — it is stale.)

**Updating an existing skill:** Skip `init_skill.py`. Go directly to Step 4. After editing, run Phase 2 and Phase 3 validation, then re-package — `package_skill.py` overwrites the existing `.skill` file.

---

## Step 4: Edit the Skill

Read `references/description-guide.md` when writing or revising the frontmatter description. Skip if the description already exists and is not being changed.

Read `references/skill-structure.md` when writing or editing the skill body. Skip if only running validation or packaging.

### Frontmatter

Write `name` and `description` fields only. No other fields.

- `name`: must exactly match the directory name, `[a-z0-9-]+`, max 64 chars
- `description`: see `references/description-guide.md` for the formula, examples, and checklist

### Body

Follow the voice, structure, and progressive disclosure rules in `references/skill-structure.md`.

---

## Step 5: Validate — Three-Phase Protocol

Read `references/validation-prompts.md` now — it contains the exact paste-ready prompts for all three phases plus the optional Architecture Refinement prompt.

Run each phase in order in a **fresh LLM chat** (a new conversation with no prior context — use a sub-agent call or a new session):

- **Phase 1 — Discovery Validation**: Tests frontmatter routing. Paste the YAML frontmatter and run the discovery probe.
- **Phase 2 — Logic Validation**: Tests step determinism. Feed the full SKILL.md and directory tree, simulate execution for a realistic request, find Execution Blockers.
- **Phase 3 — Edge Case Testing**: Forces the LLM to surface failure modes. Answer the questions, then update SKILL.md or reference files to cover the gaps.

**If Phase 3 requires adding an Error Handling section:** check the current SKILL.md line count first. If adding it would exceed 500 lines, run the Architecture Refinement prompt to offload dense content to `references/` before adding the section.

**If Phase 1 and Phase 2 feedback conflict** (e.g., Phase 1 says broaden the description, Phase 2 says narrow the scope): fix Phase 2 Execution Blockers first — they are hard failures. Then re-run Phase 1 to verify the description still routes correctly.

After Phase 3, optionally run the Architecture Refinement prompt (in `references/validation-prompts.md`) to enforce progressive disclosure.

---

## Step 6: Package

```bash
python3 skills/skill-creator/scripts/package_skill.py skills/<skill-name>
```

The script validates frontmatter and structure, then produces a distributable `.skill` file. Fix any reported errors and re-run.

If the command exits with `ModuleNotFoundError: No module named 'quick_validate'`, the script must be run from inside its own directory:

```bash
cd skills/skill-creator/scripts && python3 package_skill.py ../../<skill-name>
```

---

## Step 7: Iterate

After real usage:

1. Note where the agent struggled or produced low-quality output.
2. Decide whether the fix belongs in SKILL.md, a reference file, or a script.
3. Re-run Phase 2 and Phase 3 validation after non-trivial edits.
