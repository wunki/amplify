---
name: skill-creator
description: Low-level scaffolding toolkit for agent skills — init_skill.py creates a new skill directory from template, package_skill.py validates and packages a skill folder into a distributable .skill file, and quick_validate.py checks frontmatter. Use when the user asks to run, fix, or understand these scripts directly, or when skill-forge delegates to these scripts during scaffolding or packaging. Don't use for end-to-end skill authoring, writing SKILL.md content, or skill design guidance — use skill-forge for that. Don't use for README writing, AGENTS.md configuration, or general agent documentation.
license: Complete terms in LICENSE.txt
---

# Skill Creator

Low-level scaffolding toolkit for skill authoring. Provides three scripts: `init_skill.py` (create a new skill from template), `package_skill.py` (validate and package into a `.skill` file), and `quick_validate.py` (frontmatter checks). For end-to-end skill authoring workflow, use `skill-forge` instead.

---

## Scripts

### init_skill.py — Create a new skill from template

**Prerequisites:** Python 3 (`python3 --version`) and PyYAML (`pip install pyyaml`).

Run from the repository root:

```bash
python3 skills/skill-creator/scripts/init_skill.py <skill-name> --path skills/
```

The script:
- Creates `skills/<skill-name>/` directory
- Generates `SKILL.md` with frontmatter template and TODO placeholders
- Creates `scripts/`, `references/`, and `assets/` subdirectories with example placeholder files

**After init:** Delete all unneeded placeholder files. The script creates examples in all three directories — most skills won't need all of them.

**Skill name rules:** `[a-z0-9-]+`, max 64 characters, must match the directory name exactly. (The script's help text says "Max 40 characters" — this is stale; the validator enforces 64.)

---

### package_skill.py — Validate and package a skill

**Must be run from inside the `scripts/` directory** because `package_skill.py` imports `quick_validate` without a path:

```bash
cd skills/skill-creator/scripts && python3 package_skill.py ../../<skill-name>
```

Or with an explicit output directory:

```bash
cd skills/skill-creator/scripts && python3 package_skill.py ../../<skill-name> ../../../dist
```

The script validates the skill first (frontmatter format, required fields, naming conventions, description length, no angle brackets). If validation passes, it creates `<skill-name>.skill` — a ZIP archive with a `.skill` extension — containing all files from the skill directory.

If `ModuleNotFoundError: No module named 'quick_validate'` appears, the CWD is wrong. Run from `skills/skill-creator/scripts/` as shown above.

---

### quick_validate.py — Frontmatter checks only

```bash
python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>
```

Checks: SKILL.md exists, valid YAML frontmatter, `name` and `description` present, name is `[a-z0-9-]+` and max 64 chars, description has no angle brackets and is under 1024 chars, no unexpected frontmatter keys.

**Allowed frontmatter keys:** `name`, `description`, `license`, `allowed-tools`, `metadata`. Any other key fails validation.

---

## Skill Structure Reference

Read `references/workflows.md` when writing sequential or conditional workflow steps in a skill body.

Read `references/output-patterns.md` when the skill needs to produce consistent output formats or example-driven guidance.

---

## Core Concepts

### Anatomy of a skill

```
skill-name/
├── SKILL.md           (required)
│   ├── YAML frontmatter (name + description — the only routing signal)
│   └── Markdown body   (loaded only after the skill triggers)
└── Bundled resources  (optional)
    ├── scripts/        executable code for deterministic/repetitive operations
    ├── references/     dense context loaded on demand
    └── assets/         output templates, boilerplate, fonts, images (not loaded into context)
```

### Progressive disclosure

Skills use three loading levels:
1. `name` + `description` — always in context (~100 words)
2. SKILL.md body — loaded when the skill triggers (keep under 500 lines)
3. Bundled resources — loaded only when Claude determines they're needed

Keep SKILL.md body under 500 lines. Move dense reference material, large examples, and schemas to `references/`. Always use `Read references/X.md when [condition]. Skip if [skip condition].` — not "See X" or "refer to X".

### What not to include in a skill

Do not create: `README.md`, `CHANGELOG.md`, `INSTALLATION_GUIDE.md`, `QUICK_REFERENCE.md`, or any other human-facing documentation. Skills are for agents; extra files add noise and inflate context.

### Description formula

```
[Capability statement in third person]. Use when [2-3 concrete trigger conditions].
Don't use for [negative triggers — most likely false-positive domains].
```

Max 1,024 characters. No angle brackets. Read `references/description-guide.md` (in `skill-forge`) for detailed formula, examples, and checklist.

---

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'quick_validate'` | `package_skill.py` run from wrong CWD | Run from `skills/skill-creator/scripts/` |
| `Unexpected key(s) in SKILL.md frontmatter` | Extra YAML fields (e.g., `license` without validator support) | Remove the key or check allowed keys list above |
| `Description is too long` | Over 1,024 characters | Shorten; move detail to trigger conditions |
| `Name should be hyphen-case` | Uppercase or underscore in skill name | Rename to `[a-z0-9-]+` |
| `Skill directory already exists` | `init_skill.py` run on an existing skill | Skip init; edit SKILL.md directly |
| Validation passes but skill doesn't trigger | Description too narrow or missing paraphrase variants | Broaden trigger conditions; run Phase 1 validation via skill-forge |
