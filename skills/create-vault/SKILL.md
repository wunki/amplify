---
name: create-vault
description: Create an Ampi-ready SQLite vault from a folder of documents (md/markdown/txt/docx/doc) or an existing SQLite source table, including keyword + semantic search contract objects and manifest metadata.
---

# Create Vault

## Purpose

Produce a SQLite vault that Ampi can query through:
- `search_vault_keyword`
- `search_vault_semantic`
- `search_vault_deep`
- `lookup_vault_records`

The output vault includes:
- canonical `chunks` and `docs` views,
- `chunks_fts` keyword index,
- optional sparse semantic tables,
- `search_schema` and `build_info`,
- `amplify_search_manifest` with entity-level capabilities.

## Default Workflow

Prefer the `documents` command for non-technical users.

1. Confirm the input folder with documents.
2. Pick domain-specific entity names.
3. Run one command (`documents`) to ingest + build + check.
4. If output says `ok: true`, the vault is Ampi-ready.

Use `easy` only when the source table already exists in SQLite.

## Data Flow

```text
documents folder
      |
      v
documents ingest -> source_table rows
      |
      v
build contract objects (chunks/docs + fts + semantic + manifest)
      |
      v
check contract (keyword + lookup + semantic smoke checks)
      |
      v
Ampi-ready SQLite vault
```

## Quick Intake Questions

Before running commands, ask the user:
1. What is this vault about (support tickets, product notes, legal docs, research, etc.)?
2. Which folder contains the files?
3. Which file types should be ingested (`md`, `txt`, `docx`, `doc`)?
4. What should the two entity names be?
5. Keep semantic/deep enabled (default) or keyword-only?

If the user does not know entity names, propose domain nouns immediately.

## Entity Naming Rules

Use domain terms, not technical storage words.

Good pairs:
- `tickets` + `customers`
- `call_notes` + `accounts`
- `product_feedback` + `products`
- `research_findings` + `studies`

Avoid generic pairs:
- `chunks` + `docs`

Defaults:
- chunk-level entity defaults to `--source-table`
- doc-level entity defaults to `<chunks-entity-name>_docs`

## Commands

Document-first one-command path:

```bash
python3 skills/create-vault/scripts/bootstrap_ampi_vault.py documents \
  --db /tmp/my-vault.sqlite \
  --input-dir /path/to/documents \
  --source-table source_rows \
  --overwrite-table \
  --chunks-entity-name tickets \
  --docs-entity-name customers
```

Existing SQLite one-command path:

```bash
python3 skills/create-vault/scripts/bootstrap_ampi_vault.py easy \
  --db /tmp/my-vault.sqlite \
  --source-table source_rows \
  --chunks-entity-name tickets \
  --docs-entity-name customers
```

Inspect existing table before build:

```bash
python3 skills/create-vault/scripts/bootstrap_ampi_vault.py inspect \
  --db /tmp/my-vault.sqlite \
  --source-table source_rows
```

Validate an existing vault:

```bash
python3 skills/create-vault/scripts/bootstrap_ampi_vault.py check \
  --db /tmp/my-vault.sqlite
```

Keyword-only mode (skip semantic + deep):

```bash
python3 skills/create-vault/scripts/bootstrap_ampi_vault.py documents \
  --db /tmp/my-vault.sqlite \
  --input-dir /path/to/documents \
  --no-semantic
```

## File Type Notes

- `.md`, `.markdown`, `.txt`: native parsing.
- `.docx`: native parsing from Office XML.
- `.doc`: best-effort parsing via `textutil` or `antiword`, otherwise skipped with a warning.

If many `.doc` files fail, convert them to `.docx` first.

## Versioning

- `contract_version` uses CalVer (default example: `2026.02.13.1`).
- `manifest_json.version` is numeric (`--manifest-version`, default `1`).

## Agent Behavior

- Always run validation (`check`) after build unless the user explicitly skips it.
- Report `warnings_count` from document ingest so users know what was skipped.
- Keep semantic enabled by default.
- Never invent retrieval SQL in user-facing responses, rely on Ampi search tools.
- Return the final DB path and contract summary (`entities`, `capabilities`, `counts`).
