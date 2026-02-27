---
name: create-vault
description: >
  Creates an Ampi-ready SQLite vault from a folder of documents (md, markdown,
  txt, docx, doc) or an existing SQLite source table. Builds keyword search
  (FTS5), optional sparse semantic search, a search_schema contract, and an
  amplify_search_manifest so Ampi tools (search_vault_keyword,
  search_vault_semantic, search_vault_deep, lookup_vault_records) work
  immediately. Use when the user wants to build a new Ampi vault, ingest
  documents into a searchable SQLite database, check whether an existing vault
  passes the Ampi search contract, or re-build a vault from updated documents.
  Don't use for general SQLite database creation, non-Ampi document stores,
  CSV imports, querying an existing vault, or adding documents to an
  already-built vault without re-ingesting.
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

## Resolving the Script Path

Before running any command, resolve the absolute path to the script. Use the
amplify repo root (ask the user if unknown, or locate it via `git rev-parse
--show-toplevel` from the working directory):

```
SCRIPT=/path/to/amplify/skills/create-vault/scripts/bootstrap_ampi_vault.py
```

All command examples below use `$SCRIPT` as a placeholder for this path.

## Commands

Document-first one-command path (preferred for new vaults from files):

```bash
python3 $SCRIPT documents \
  --db /path/to/my-vault.sqlite \
  --input-dir /path/to/documents \
  --source-table source_rows \
  --overwrite-table \
  --chunks-entity-name tickets \
  --docs-entity-name customers
```

`--overwrite-table` drops and recreates the source table before ingest. Include
it on every fresh build or rebuild. Omit only when intentionally appending to
an existing table.

Existing SQLite one-command path (source table must already exist):

```bash
python3 $SCRIPT easy \
  --db /path/to/my-vault.sqlite \
  --source-table source_rows \
  --chunks-entity-name tickets \
  --docs-entity-name customers
```

`easy` runs build then check. `build` runs build only (no check).

Inspect a source table before build. Run this when the table columns are
unfamiliar or when a previous build failed with a field-mapping error:

```bash
python3 $SCRIPT inspect \
  --db /path/to/my-vault.sqlite \
  --source-table source_rows
```

Output shows detected columns, inferred field mapping, and a suggested build
command. If required fields (`id_field`, `text_field`) cannot be inferred,
supply them explicitly with `--id-field` and `--text-field`.

Validate an existing vault:

```bash
python3 $SCRIPT check \
  --db /path/to/my-vault.sqlite
```

Keyword-only mode (skip sparse semantic index and semantic/deep capabilities):

```bash
python3 $SCRIPT documents \
  --db /path/to/my-vault.sqlite \
  --input-dir /path/to/documents \
  --source-table source_rows \
  --overwrite-table \
  --no-semantic
```

## File Type Notes

- `.md`, `.markdown`, `.txt`: native parsing.
- `.docx`: native parsing from Office XML.
- `.doc`: best-effort parsing via `textutil` (macOS) or `antiword` (Linux); skipped with a warning if neither is available.

If many `.doc` files are skipped, install `antiword` (Linux: `apt install antiword`, macOS: `brew install antiword`) or convert the files to `.docx` first.

After ingest, check `warnings_count` in the output. A high count relative to total files means many documents were skipped; investigate before treating the vault as complete.

## Versioning

- `contract_version` uses CalVer (default example: `2026.02.13.1`).
- `manifest_json.version` is numeric (`--manifest-version`, default `1`).

## Error Handling

**Build fails with "Unable to resolve required field"**
Auto-mapping could not find a column matching `id_field` or `text_field`. Run
`inspect` to see the detected columns, then re-run the build command with
explicit `--id-field` and `--text-field` flags.

**Build fails with "No rows available in chunks view"**
The input directory was empty, all files were skipped, or the source table has
no rows. Confirm the `--input-dir` path is correct and contains supported file
types. Check `warnings_count` to see if every file was rejected.

**check output shows `ok: false`**
Read the `errors` array in the output. Common causes: missing `chunks_fts`
table (FTS5 not compiled into SQLite), missing manifest table, or zero rows in
views. Re-run the build after addressing the specific error, or run with
`--no-semantic` if FTS5-related errors appear.

**FTS5 not available**
Some SQLite builds (notably older system SQLite on macOS) lack FTS5. Check with
`python3 -c "import sqlite3; sqlite3.connect(':memory:').execute('CREATE VIRTUAL TABLE t USING fts5(x)')"`.
If this raises `OperationalError`, install a newer SQLite or use `--no-semantic`
(which skips the sparse index but still requires FTS5 for keyword search — if
FTS5 is absent, the vault cannot be built and the user must upgrade SQLite).

**Rebuilding an existing vault**
Re-run the same `documents` or `easy` command with `--overwrite-table`. This
drops and recreates the source table and rebuilds all contract objects cleanly.

## Agent Behavior

- Always run validation (`check`) after build unless the user explicitly skips it.
- If `ok: false`, read the `errors` array and diagnose before reporting results.
- Report `warnings_count` from document ingest so users know what was skipped.
- Keep semantic enabled by default.
- Never invent retrieval SQL in user-facing responses; rely on Ampi search tools.
- Return the final DB path and contract summary (`entities`, `capabilities`, `counts`).
