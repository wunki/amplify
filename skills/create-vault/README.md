# Create Vault

A Claude Code skill that creates Ampi-ready SQLite vaults from a folder of documents (md, markdown, txt, docx, doc) or an existing SQLite source table. Includes keyword and semantic search contract objects and manifest metadata.

## When to use

When you need to create a searchable SQLite vault from a collection of documents for use with Ampi or similar systems.

## What it covers

- **Purpose**: What vaults are and why they exist
- **Data Flow**: How documents become searchable vault entries
- **Quick Intake Questions**: What to ask before building a vault
- **Entity Naming Rules**: Conventions for vault naming
- **Commands**: Step-by-step vault creation process
- **File Type Notes**: Handling different document formats
- **Versioning**: How vault versions are managed

## Files

- `SKILL.md` - Main skill definition
- `scripts/bootstrap_ampi_vault.py` - Python script for vault creation

## Usage

```
/create-vault
```
