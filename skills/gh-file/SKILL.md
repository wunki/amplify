---
name: gh-file
description: Fetch source code from GitHub URLs. Paste a GitHub link to a file, directory, or repository and get the contents. Supports line ranges (#L10-L25), directories, and full repo clones. Triggers on GitHub URLs like "github.com/owner/repo/blob/..." or phrases like "fetch this GitHub file", "get the code from GitHub", "show me this file".
---

# GitHub File Fetcher

Fetch source code from GitHub URLs using the `gh` CLI for reliable, authenticated access.

## URL Patterns

Parse the GitHub URL to determine what to fetch:

| URL Pattern | Type | Action |
|-------------|------|--------|
| `github.com/owner/repo/blob/ref/path` | File | Fetch file contents |
| `github.com/owner/repo/blob/ref/path#L10` | File + line | Fetch file, show from line 10 |
| `github.com/owner/repo/blob/ref/path#L10-L25` | File + range | Fetch file, show lines 10-25 |
| `github.com/owner/repo/tree/ref/path` | Directory | List directory contents |
| `github.com/owner/repo/tree/ref` | Root | List repository root |
| `github.com/owner/repo` | Repository | Offer to clone or list root |

## Fetching Files

Use the GitHub API via `gh` to fetch file contents:

```bash
# Fetch file content (returns JSON with base64-encoded content)
# IMPORTANT: Quote the URL to prevent shell interpretation of ?
gh api 'repos/{owner}/{repo}/contents/{path}?ref={ref}'
```

To decode and display:

```bash
gh api 'repos/{owner}/{repo}/contents/{path}?ref={ref}' --jq '.content' | base64 -d
```

### Line Ranges

If the URL includes a line range like `#L10-L25`:

1. Fetch the full file
2. Extract and display only the specified lines
3. Show the line numbers for context

Example output format:
```
# src/utils/parser.ts (lines 10-25)

10: export function parseUrl(url: string): ParsedUrl {
11:   const match = url.match(GITHUB_PATTERN);
...
```

## Fetching Directories

For directory URLs, list the contents:

```bash
gh api 'repos/{owner}/{repo}/contents/{path}?ref={ref}' --jq '.[] | "\(.type)\t\(.name)"'
```

Display as a tree structure showing files and subdirectories. Offer to fetch specific files if the user wants to explore further.

## Cloning Repositories

For full repository access (exploring multiple files, understanding structure):

```bash
# Clone to a temporary directory
TEMP_DIR=$(mktemp -d)
gh repo clone {owner}/{repo} "$TEMP_DIR" -- --depth 1 --branch {ref}
echo "Cloned to: $TEMP_DIR"
```

Use shallow clone (`--depth 1`) by default for speed. After cloning:
- List the directory structure
- Read files as requested
- Remember the temp directory path for subsequent requests

## URL Parsing

Extract components from GitHub URLs:

```
https://github.com/anthropics/claude-code/blob/main/src/index.ts#L10-L25
         ^^^^^^^^^ ^^^^^^^^^^^ ^^^^ ^^^^ ^^^^^^^^^^^^^ ^^^^^^^^
         |         |           |    |    |             |
         |         |           |    |    path          line range
         |         |           |    ref (branch/tag/commit)
         |         |           "blob" = file, "tree" = directory
         |         repo
         owner
```

## Error Handling

- **404**: File/path doesn't exist. Check spelling and ref.
- **403**: Rate limited or private repo. Ensure `gh auth status` is valid.
- **Large files**: If content is null and download_url is present, file is too large for API. Use download_url directly.

## Workflow

1. **Parse the URL** - Extract owner, repo, ref, path, and line range
2. **Determine type** - File (blob) or directory (tree)
3. **Fetch via gh API** - Use authenticated API access
4. **Format output** - Show file contents with line numbers, or directory listing
5. **Offer next steps** - "Want me to fetch another file?" or "Should I clone the repo for deeper exploration?"

## Examples

**User pastes**: `https://github.com/anthropics/claude-code/blob/main/src/index.ts#L1-L50`

Response:
1. Parse: owner=anthropics, repo=claude-code, ref=main, path=src/index.ts, lines=1-50
2. Fetch: `gh api repos/anthropics/claude-code/contents/src/index.ts?ref=main`
3. Decode base64 content
4. Display lines 1-50 with line numbers

**User pastes**: `https://github.com/anthropics/claude-code/tree/main/src`

Response:
1. Parse: owner=anthropics, repo=claude-code, ref=main, path=src
2. Fetch: `gh api repos/anthropics/claude-code/contents/src?ref=main`
3. Display directory listing
4. Offer to fetch specific files
