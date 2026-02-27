---
name: browse-site
description: >
  Navigates and interacts with websites using the agent-browser CLI, including
  clicking elements, filling forms, taking screenshots, extracting page content,
  and automating multi-step browser workflows. Use when the user asks to open a
  URL, click something on a page, fill out a web form, take a page screenshot,
  scrape or extract data from a website, or automate a browser task. Don't use
  for Playwright, Puppeteer, or Selenium scripts; don't use for browser extension
  development; don't use for questions about browser APIs, JavaScript, or frontend
  code that don't require live browser interaction.
---

# Browse Site Skill

Browse and interact with websites using the `agent-browser` CLI.

## Installation Check

Before first use, verify `agent-browser` is available:

```bash
agent-browser --version
```

If the command is not found, install it:

```bash
npm install -g agent-browser
agent-browser install  # Download Chromium
```

If installation fails, stop and report the error to the user. Do not proceed.

## Workflow

1. **Navigate** — open the target URL:
   ```bash
   agent-browser open <url>
   ```
   If the command exits with a non-zero code or outputs an error, report it and stop.

2. **Snapshot** — get interactive elements with stable refs:
   ```bash
   agent-browser snapshot -i -c --json
   ```
   The JSON output contains an `elements` array. Each element has a `ref` field (e.g., `"@e2"`) and a `role`/`name` describing it. Use these refs for all subsequent interactions.

3. **Interact** — act on elements using refs from the latest snapshot:
   ```bash
   agent-browser click @e2
   agent-browser fill @e5 "search term"
   agent-browser type @e7 "typed text"
   ```

4. **Re-snapshot** — after any interaction that changes the page, take a new snapshot before acting again. Refs from a previous snapshot are stale after page changes.

5. **Repeat** until the task is complete, then close the browser:
   ```bash
   agent-browser close
   ```

## Common Commands

| Action | Command |
|--------|---------|
| Navigate | `agent-browser open <url>` |
| Get elements | `agent-browser snapshot -i -c --json` |
| Click | `agent-browser click @e<n>` |
| Type text | `agent-browser type @e<n> "text"` |
| Fill field | `agent-browser fill @e<n> "text"` |
| Screenshot | `agent-browser screenshot <path>` |
| Get element text | `agent-browser get text @e<n>` |
| Get page title | `agent-browser get title` |
| Get current URL | `agent-browser get url` |
| Wait (milliseconds) | `agent-browser wait 2000` |
| Wait (element) | `agent-browser wait "#submit-button"` |
| Close browser | `agent-browser close` |

Always provide a path for screenshots (e.g., `agent-browser screenshot /tmp/page.png`). The command may fail silently without one.

## Sessions

Use `--session <name>` to persist browser state (cookies, local storage) across commands:

```bash
agent-browser open https://example.com --session mysite
agent-browser snapshot -i -c --json --session mysite
agent-browser click @e3 --session mysite
agent-browser close --session mysite
```

Use sessions for login flows so authenticated state is preserved between steps.

## Snapshot Options

| Option | Description |
|--------|-------------|
| `-i, --interactive` | Only interactive elements (buttons, links, inputs) |
| `-c, --compact` | Remove empty structural elements |
| `-d, --depth <n>` | Limit tree depth |
| `-s, --selector <sel>` | Scope to CSS selector |
| `--json` | Machine-readable output with refs |

Combine options: `agent-browser snapshot -i -c -d 5 --json`

## Error Handling

| Situation | Action |
|-----------|--------|
| `agent-browser` not found | Install it (see Installation Check), then retry. |
| `open` fails (bad URL, network error) | Report the error and URL to the user. Stop. |
| Snapshot returns empty elements | The page may require a wait; run `agent-browser wait 2000` then re-snapshot. |
| Login blocked by captcha or MFA | Stop and ask the user to complete the manual step, then continue. |
| Ref not found (stale ref) | Re-snapshot the page; refs change after DOM updates. |
| Screenshot path missing | Always supply an explicit output path to avoid silent failures. |

## Tips

- Use `--headed` on any command to watch the browser visually during debugging: `agent-browser open <url> --headed`
- Use `--session` for any workflow that requires login
- Prefer `-i -c` on snapshots to keep output small and refs easy to read
