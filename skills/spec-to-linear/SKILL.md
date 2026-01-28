---
name: spec-to-linear
description: Create a Linear issue from a spec file. Derives issue title and summary from the spec, embeds the full spec in the issue description (collapsible). Updates the spec file with the issue ID for traceability. Can also update existing issues when spec changes. Use when phrases include "linear" with "issue" or "ticket" (e.g., "create a linear issue", "linear ticket for this spec", "create a ticket in linear"). Typically used after creating a spec and before starting implementation. Requires Linear MCP to be configured.
---

# Spec to Linear

Create a Linear issue from a spec file with full traceability.

## Prerequisites

Linear MCP must be configured. Verify by checking that `mcp__linear__*` tools are available.

## Workflow

### 1. Get the Spec File

Ask the user which spec file to use if not already specified. Common locations:
- `SPEC.md` in project root
- `specs/<feature-name>.md`

### 2. Check for Existing Issue

Read the spec file and look for an existing Linear issue ID.

**Pattern**: `Linear: [A-Z]+-\d+` (e.g., `Linear: ENG-123`)

**Location**: Right after the `# Spec:` title line:
```markdown
# Spec: User Authentication

Linear: ENG-123

<summary paragraph>
```

**If found**: Offer to update the existing issue's description with the current spec content instead of creating a new issue. Use `mcp__linear__update_issue` to update.

### 3. Gather Issue Details

**Extract from spec:**
- **Title**: From the `# Spec: <title>` heading (without the "Spec: " prefix)
- **Summary**: One paragraph describing the problem and key outcomes (a few sentences max)

**Ask user for:**
- **Team** (required): Which Linear team?
- **Project** (optional): Associate with a project?
- **State** (optional): Defaults to Triage

#### Team Name Resolution

Users often use informal names. Always fetch teams with `mcp__linear__list_teams` first, then:

1. **Exact match**: "Engineering" → Engineering team
2. **Partial match**: "eng" or "engineering team" → Engineering team
3. **Semantic match**: "the team that maintains auth" → try to infer from context
4. **No match**: Show available teams and ask user to pick or be more specific

**Always confirm** before creating the issue:
> "I found the 'Unicorn' team. Is this the right one for this spec?"

If uncertain or multiple possibilities exist, list the available teams and ask the user to choose.

Use `mcp__linear__list_projects` and `mcp__linear__list_issue_statuses` for other options when needed.

### 4. Create the Issue

Use `mcp__linear__create_issue`:
- **title**: Extracted from spec
- **description**: Format as shown below
- **team**: User-specified
- **project**: User-specified (if any)
- **state**: "Triage" (default) or user-specified

**Description format:**
```markdown
<One paragraph summary: problem statement and key outcomes>

+++ Spec (powered by spec-to-linear skill)

<full spec content here>

+++

```

The `+++ ` prefix creates a collapsible section in Linear.
The last `+++ ` is required to close the section

### 5. Update the Spec File

Add the issue identifier right after the title line:

```markdown
# Spec: User Authentication

Linear: ENG-123

One sentence summary of what we're building...
```

If there's already content between the title and the summary, insert the Linear reference on a new line after the title.

### 6. Confirm Completion

Report:
- Issue identifier (e.g., `ENG-123`) and URL
- Spec file updated with issue reference
