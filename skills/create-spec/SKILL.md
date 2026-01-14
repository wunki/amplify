---
name: create-spec
description: Create or update a SPEC.md document from requirements, notes, or interview output. Structures information into a consistent spec format. Triggers on "create a spec", "write a spec", "turn this into a spec", "spec template", or when structuring requirements into a specification document.
---

# Create Spec

Structure requirements into a well-organized SPEC.md document. This skill focuses on the *structure and writing* of specs, not the requirements gathering (use the `interview` skill for that).

## When to Use

- After an interview session, to write the gathered requirements
- To convert existing notes/requirements into spec format
- To create a blank spec template for a new feature
- To update an existing spec with new information

## Workflow

### 1) Gather Input

Determine what you're working with:

- **Interview output**: Requirements gathered from `interview` skill
- **Existing notes**: User-provided requirements, PRD, or design doc
- **Existing SPEC.md**: Update/extend rather than replace
- **Nothing yet**: Create a template with placeholders

### 2) Structure the Spec

Use the template in `references/spec-template.md`. Key sections:

| Section | Purpose |
|---------|---------|
| **Summary** | One breath: what and why |
| **Background** | Context for newcomers |
| **Goals / Non-Goals** | Scope control |
| **Design** | Technical, UI/UX, Data, API |
| **Edge Cases** | What could go wrong |
| **Security & Privacy** | Risks and mitigations |
| **Testing Strategy** | How we verify it works |
| **Success Criteria** | Measurable "done" |
| **Open Questions** | Honest uncertainty |
| **Decisions Log** | Why we chose what we chose |

**Omit sections that don't apply**, but consider each before omitting.

### 3) Write with Precision

- **Be specific**: "Validates email format using RFC 5322" not "validates input"
- **Include the why**: Decisions without rationale are useless to future readers
- **Note uncertainties**: Open questions are better than false confidence
- **Use concrete examples**: Show, don't just tell

### 4) Output Location

- Default: `SPEC.md` in project root
- If user specifies a path, use that
- Multiple specs: `specs/<feature-name>.md`
- If file exists, ask before overwriting (unless updating)

## Spec Quality Checklist

Before finishing:

- [ ] Summary is one breath (if you can't summarize it, you don't understand it)
- [ ] Goals are measurable, not vague
- [ ] Non-goals explicitly prevent scope creep
- [ ] Design is implementable without guessing
- [ ] Edge cases cover failure modes
- [ ] Success criteria are testable
- [ ] Open questions are honest about unknowns

## Example Usage

**From interview output:**
```
Based on our interview, here's the spec:

# Spec: User Authentication

OAuth + email/password, JWT in HTTP-only cookies...
[structured content from interview]
```

**From existing notes:**
```
I'll structure your notes into a spec. Let me organize this:

# Spec: Payment Processing

[transforms unstructured notes into spec format]
```

**Blank template:**
```
Here's a spec template for the notification system:

# Spec: Notification System

## Summary
<describe what the notification system does and why>

## Background
<why are we building this now?>
...
```

## Anti-patterns

- **Don't pad**: Empty sections are worse than omitted sections
- **Don't be vague**: "Handle errors" is not a spec
- **Don't skip security**: Even internal tools need threat consideration
- **Don't invent requirements**: If you don't know, mark it as an open question
