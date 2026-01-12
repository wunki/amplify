---
name: browse-site
description: Browser automation using agent-browser CLI. Use when users ask to navigate websites, fill forms, take screenshots, extract web data, test web apps, or automate browser workflows. Trigger phrases include "go to [url]", "click on", "fill out the form", "take a screenshot", "scrape", "automate", "test the website", "log into", "browse to", "open website", "visit", or any browser interaction request.
---

# Browse Site Skill

Browse and interact with websites using the `agent-browser` CLI.

## Installation

If `agent-browser` is not installed:

```bash
npm install -g agent-browser
agent-browser install  # Download Chromium
```

## Quick Start

```bash
agent-browser open https://example.com
agent-browser snapshot -i              # Get interactive elements with refs
agent-browser click @e2                # Click element by ref
agent-browser screenshot tmp/page.png  # Capture screenshot
```

## Workflow

1. **Navigate**: `agent-browser open <url>`
2. **Snapshot**: `agent-browser snapshot -i --json` returns accessibility tree with refs
3. **Interact**: Use refs to click, fill, type (e.g., `agent-browser click @e2`)
4. **Re-snapshot**: Get new snapshot after page changes
5. **Repeat**: Continue until task complete

Always use refs from the most recent snapshot. Refs are deterministic and point to exact elements.

## Common Commands

| Action | Command |
|--------|---------|
| Navigate | `agent-browser open <url>` |
| Get elements | `agent-browser snapshot -i` |
| Click | `agent-browser click @e<n>` |
| Type text | `agent-browser type @e<n> "text"` |
| Fill field | `agent-browser fill @e<n> "text"` |
| Screenshot | `agent-browser screenshot [path]` |
| Get text | `agent-browser get text @e<n>` |
| Get page title | `agent-browser get title` |
| Get current URL | `agent-browser get url` |
| Wait | `agent-browser wait <selector or ms>` |

## Sessions

Use `--session <name>` to maintain state across commands:

```bash
agent-browser open https://example.com --session mysite
agent-browser click @e3 --session mysite
```

## Snapshot Options

| Option | Description |
|--------|-------------|
| `-i, --interactive` | Only interactive elements (buttons, links, inputs) |
| `-c, --compact` | Remove empty structural elements |
| `-d, --depth <n>` | Limit tree depth |
| `-s, --selector <sel>` | Scope to CSS selector |
| `--json` | Machine-readable output |

Combine options: `agent-browser snapshot -i -c -d 5 --json`

## Tips

- Always use `--json` for parsing snapshot output programmatically
- Use `-i` (interactive only) to reduce output size
- Use `--headed` to watch the browser visually
- Refs like `@e2` come from the snapshot output and are deterministic
- Close the browser when done: `agent-browser close`
