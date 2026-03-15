---
name: mcp-builder
description: "Builds new MCP (Model Context Protocol) servers that expose external API tools to LLMs. Use when the user wants to create, scaffold, or implement an MCP server to integrate a third-party service or API, in Python (FastMCP) or Node/TypeScript (MCP TypeScript SDK). Also use when asked to add tools to an existing MCP server, write or run evaluations for an MCP server, or design the tool interface for a new MCP integration. Don't use for: connecting to or configuring an already-running MCP server, debugging MCP client connections, explaining the MCP protocol in general, or configuring Claude Desktop MCP settings."
license: Complete terms in LICENSE.txt
---

# MCP Server Development Guide

## Overview

This skill produces high-quality MCP (Model Context Protocol) servers that enable LLMs to interact with external services. An MCP server provides tools that allow LLMs to access external services and APIs. Quality is measured by how well those tools enable LLMs to accomplish real-world tasks.

---

# Process

## High-Level Workflow

Creating an MCP server involves four phases. Phases 1-3 apply when building or extending a server. Phase 4 applies when creating evaluations for an existing server.

### Phase 1: Deep Research and Planning

#### 1.1 Determine implementation language

Ask the user which language to use via `AskUserQuestion` (single-select) if not already specified:

- "Python (FastMCP)" — single-file or modular, decorator-based
- "Node/TypeScript (MCP SDK)" — project-based, build step required

All steps below branch by language where relevant.

#### 1.2 Understand Agent-Centric Design Principles

Design tools for AI agents, not human developers. Apply these principles:

**Build for Workflows, Not Just API Endpoints:**
- Consolidate related operations (e.g., `schedule_event` checks availability and creates the event in one call)
- Focus on tools that enable complete tasks, not individual API calls

**Optimize for Limited Context:**
- Return high-signal information, not exhaustive data dumps
- Offer `concise` vs `detailed` response format options
- Default to human-readable identifiers (names over IDs)

**Design Actionable Error Messages:**
- Suggest specific next steps: "Try using filter='active_only' to reduce results"
- Make errors educational, not just diagnostic

**Follow Natural Task Subdivisions:**
- Tool names reflect how humans think about tasks
- Group related tools with consistent `service_` prefixes

**Use Evaluation-Driven Development:**
- Create realistic evaluation scenarios early; iterate based on agent performance

#### 1.3 Study MCP Protocol Documentation

Fetch the latest MCP protocol specification using WebFetch: `https://modelcontextprotocol.io/llms-full.txt`

If the URL is unreachable, continue using `reference/mcp_best_practices.md` as the primary reference.

#### 1.4 Study Framework Documentation

Read `reference/mcp_best_practices.md` for universal MCP guidelines. Skip if already loaded this session.

For Python: also fetch `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md` and read `reference/python_mcp_server.md`. If the URL is unreachable, use the local guide only.

For Node/TypeScript: also fetch `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md` and read `reference/node_mcp_server.md`. If the URL is unreachable, use the local guide only.

#### 1.5 Study the Target API Documentation

Read through all available documentation for the API to integrate:
- Official API reference (endpoints, parameters, data models, schemas)
- Authentication and authorization requirements
- Rate limiting and pagination patterns
- Error responses and status codes

Use WebSearch and WebFetch as needed.

#### 1.6 Create an Implementation Plan

Write a plan covering:

**Tool Selection:** List the most valuable endpoints to implement. Prioritize tools that enable complete workflows. Identify which tools work together.

**Shared Utilities:** Common API request patterns, pagination helpers, filtering and formatting utilities, error handling strategy, authentication management.

**Input/Output Design:** Pydantic models (Python) or Zod schemas (TypeScript) for input validation. Consistent response formats (JSON and Markdown). Character limits and truncation (25,000 characters).

**Error Handling:** Graceful failure modes. Clear, actionable, LLM-friendly error messages. Rate limiting and timeout handling. Authentication/authorization error handling.

---

### Phase 2: Implementation

#### 2.1 Set Up Project Structure

For Python: create a single `.py` file, or organize into modules if complex. See `reference/python_mcp_server.md` for patterns.

For Node/TypeScript: create `package.json`, `tsconfig.json`, and source directory. See `reference/node_mcp_server.md` for project structure.

#### 2.2 Implement Core Infrastructure First

Create shared utilities before implementing tools:
- API request helper functions
- Error handling utilities
- Response formatting functions (JSON and Markdown)
- Pagination helpers
- Authentication/token management

#### 2.3 Implement Tools Systematically

For each tool in the plan:

**Define Input Schema:**
- Use Pydantic (Python) or Zod (TypeScript) for validation
- Include constraints (min/max length, regex patterns, value ranges)
- Write clear, descriptive field descriptions with examples

**Write Comprehensive Docstrings/Descriptions:**
- One-line summary of what the tool does
- Detailed explanation of purpose and functionality
- Explicit parameter types with examples
- Complete return type schema
- Usage examples (when to use, when not to use)
- Error handling documentation

**Implement Tool Logic:**
- Use shared utilities — no duplicated code between tools
- Follow async/await patterns for all I/O
- Support JSON and Markdown response formats
- Respect pagination parameters
- Check character limits and truncate gracefully

**Add Tool Annotations:**
- `readOnlyHint`: true for read-only operations
- `destructiveHint`: false for non-destructive operations
- `idempotentHint`: true if repeated calls have the same effect
- `openWorldHint`: true if interacting with external systems

#### 2.4 Apply Language-Specific Best Practices

Read `reference/python_mcp_server.md` when implementing in Python. Skip if already loaded.

Confirm the implementation follows:
- MCP Python SDK with `@mcp.tool` registration
- Pydantic v2 models with `model_config`
- Type hints throughout
- Async/await for all I/O
- Module-level constants (`CHARACTER_LIMIT`, `API_BASE_URL`)

Read `reference/node_mcp_server.md` when implementing in Node/TypeScript. Skip if already loaded.

Confirm the implementation follows:
- `server.registerTool` for tool registration
- Zod schemas with `.strict()`
- TypeScript strict mode enabled
- No `any` types
- Explicit `Promise<T>` return types
- Build step configured (`npm run build`)

---

### Phase 3: Review and Refine

#### 3.1 Code Quality Review

Review the code for:
- **DRY**: No duplicated code between tools
- **Composability**: Shared logic extracted into functions
- **Consistency**: Similar operations return similar formats
- **Error Handling**: All external calls have error handling
- **Type Safety**: Full type coverage
- **Documentation**: Every tool has comprehensive docstrings

#### 3.2 Test and Build

MCP servers are long-running processes. Running them directly in the main process will hang indefinitely. Use safe testing approaches:

- Verify Python syntax: `python -m py_compile your_server.py`
- For TypeScript: run `npm run build` and verify `dist/index.js` is created
- To manually test: run the server in tmux, then connect with the evaluation harness
- Or run the evaluation harness directly — it manages the server process for stdio transport

Avoid running `python server.py` or `node dist/index.js` directly without a timeout or separate shell.

#### 3.3 Apply Quality Checklist

For Python: see "Quality Checklist" in `reference/python_mcp_server.md`.

For Node/TypeScript: see "Quality Checklist" in `reference/node_mcp_server.md`.

---

### Phase 4: Create Evaluations

Apply this phase after implementing a server, or when the user asks to write evaluations for an existing MCP server. Skip Phases 1-3 if the server already exists.

Read `reference/evaluation.md` for complete evaluation guidelines. The summary below covers the key requirements.

#### 4.1 Evaluation Purpose

Evaluations test whether LLMs can effectively use the MCP server to answer realistic, complex questions using only the tools provided.

#### 4.2 Create 10 Evaluation Questions

Follow the process in `reference/evaluation.md`:

1. Inspect available tools and understand their capabilities
2. Use READ-ONLY operations to explore available data
3. Generate 10 complex, realistic questions
4. Solve each question using the MCP server to verify answers before writing them

#### 4.3 Evaluation Requirements

Each question must be:
- **Independent**: Does not depend on other questions
- **Read-only**: Only non-destructive operations required
- **Complex**: Requires multiple tool calls and deep exploration
- **Realistic**: Based on real use cases humans would care about
- **Verifiable**: Single, clear answer verified by string comparison
- **Stable**: Answer does not change over time

#### 4.4 Output Format

Create an XML file:

```xml
<evaluation>
  <qa_pair>
    <question>Find discussions about AI model launches with animal codenames. One model needed a specific safety designation that uses the format ASL-X. What number X was being determined for the model named after a spotted wild cat?</question>
    <answer>3</answer>
  </qa_pair>
</evaluation>
```
