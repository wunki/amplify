# SPEC.md Template

Use this structure when writing specs. Omit sections that don't apply, but consider each one before omitting.

```markdown
# Spec: <Short descriptive title>

<1-2 sentences: what we're building and the core problem it solves>

## Background

Why are we building this?
- What problem does it solve?
- What's the current state / pain point?
- What triggered this work now?
- Any previous attempts or related work?

## Goals

What outcomes do we want?
- Primary goal (the must-have)
- Secondary goals (nice-to-haves)

## Non-Goals

What are we explicitly NOT doing?
- Features that seem related but are out of scope
- Quality attributes we're willing to sacrifice
- Future work we're deferring

## Design

### Technical Approach

High-level architecture and key decisions:
- Overall approach / pattern
- Key components and their responsibilities
- Technology choices and rationale

### Data Model

Schema and data flow:
- New tables / collections
- Field definitions with types
- Relationships and constraints
- Migration strategy (if changing existing data)

### API

Endpoints and contracts:
- Routes (method, path, purpose)
- Request/response shapes
- Authentication requirements
- Error responses

### UI/UX

User-facing behavior:
- Key user flows (step by step)
- States (loading, empty, error, success)
- Interactions and feedback
- Responsive / accessibility considerations

## Edge Cases & Error Handling

What could go wrong and how do we handle it?
- Invalid inputs
- Race conditions
- Network failures
- Partial failures
- Resource limits

## Security & Privacy

Risks and mitigations:
- Data sensitivity (PII, credentials, etc.)
- Attack vectors (injection, XSS, CSRF, etc.)
- Authorization model
- Audit / logging requirements

## Testing Strategy

How do we verify it works?
- Unit tests: what logic needs coverage
- Integration tests: what boundaries to test
- E2E tests: critical user flows
- Manual testing: exploratory scenarios

## Success Criteria

How do we know we're done?
- Functional requirements (it does X)
- Performance requirements (under Y ms)
- Quality requirements (Z% test coverage)

## Open Questions

Unresolved items that need answers:
- [ ] Question 1
- [ ] Question 2

## Decisions Log

Record of key decisions made during spec creation:

> **Q:** <Question that came up>
> **A:** <Decision made and brief rationale>

> **Q:** <Another question>
> **A:** <Decision>
```

## Section Guidelines

**Summary**: One breath. If you can't summarize it simply, you don't understand it well enough.

**Background**: Context for someone joining the project. Why does this matter?

**Goals / Non-Goals**: Scope control. Non-goals are as important as goals for preventing creep.

**Design**: The "how". Technical enough to implement from, but not so detailed it's code.

**Edge Cases**: The unsexy but critical part. Most bugs live here.

**Security**: Even internal tools need this. "No sensitive data" is a decision worth documenting.

**Testing**: Not "we'll write tests". Which tests, for what behaviors?

**Success Criteria**: Measurable. "Users can log in" not "auth works".

**Open Questions**: Honesty about uncertainty. Don't pretend to know what you don't.

**Decisions Log**: Future you will thank present you. Captures the "why" behind choices.
