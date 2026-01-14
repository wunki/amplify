---
name: interview
description: Deep, exhaustive requirements gathering for features. Reads existing SPEC.md, interviews about technical implementation, UI/UX, edge cases, tradeoffs, concerns. Continues until complete, then hands off to create-spec or create-plan. Triggers on "interview me", "fill out the spec", "spec this out", "deep dive on requirements", "help me think through this".
---

# Interview

Exhaustive requirements elicitation through deep questioning. This skill focuses on *gathering* requirements thoroughly. For writing specs, it uses the `create-spec` skill.

## When to Use

- User explicitly asks to be interviewed
- Starting a complex feature that needs thorough thinking
- Existing SPEC.md has gaps that need filling
- Any task requiring deep requirements extraction before action

## Workflow

### 1) Read Existing Context

Before asking anything:

1. Check if `SPEC.md` exists in project root
2. If yes, read it to understand what's already documented
3. Check for related docs (`README.md`, `docs/`, existing code)
4. Note what's already answered vs. what's missing

Do not ask questions you can answer from existing context.

### 2) Interview Deeply

Cover these areas, but **only ask non-obvious questions** - things you can't discover from reading the codebase:

| Area | What to explore |
|------|-----------------|
| **Purpose** | What problem? Why now? What triggered this? What does success look like? |
| **Technical** | Architecture choices, data model, APIs, integrations, performance requirements |
| **UI/UX** | User flows, states, feedback, accessibility, responsive behavior |
| **Edge cases** | What could go wrong? Invalid inputs, race conditions, failure modes |
| **Tradeoffs** | What are we optimizing for? What are we willing to sacrifice? |
| **Security/Privacy** | Data sensitivity, auth requirements, audit needs |
| **Testing** | How do we verify it works? What's critical to test? |
| **Rollout** | Feature flags? Migration? Backwards compatibility? |

**Question style**: Follow the patterns in the `ask-questions-if-underspecified` skill:
- Numbered questions with lettered options when possible
- Suggest reasonable defaults (mark clearly)
- Include "Not sure - use default" option
- Allow compact responses like `1a 2b 3c`
- Keep questions scannable, not paragraphs

**Pacing**: 
- Start with 3-5 questions covering the biggest unknowns
- After answers, ask follow-up questions that dig deeper
- Continue until you have enough for the task at hand

**Challenge the premise**: If something seems like the wrong approach, say so early. Better to redirect now than proceed with something that shouldn't be built.

### 3) Hand Off to Output

When interviewing is complete:

- **For specs**: Use the `create-spec` skill to write SPEC.md
- **For plans**: Hand off to `create-plan` agent
- **For other tasks**: Summarize findings and proceed with the task

The interview skill gathers; other skills/agents structure and write.

### 4) Confirm Understanding

Before handing off:
1. Summarize what you learned
2. Ask if anything is missing or wrong
3. Iterate if needed

## Anti-patterns

- **Don't ask obvious questions**: If you can read it from the code, don't ask
- **Don't ask everything at once**: Start broad, then dive deep based on answers
- **Don't skip areas**: Even if user seems impatient, cover security/edge cases
- **Don't interview forever**: Know when you have enough for the task

## Example Interview Flow

```text
I've read the existing SPEC.md and codebase. A few questions before I fill in the gaps:

1) User authentication - which approach?
   a) Email/password only (simplest)
   b) OAuth providers (Google, GitHub)
   c) Both (recommended for flexibility)
   d) Not sure - recommend what fits

2) Session handling?
   a) JWT in HTTP-only cookie (recommended for web)
   b) JWT in localStorage
   c) Server-side sessions with Redis
   d) Not sure - use recommended

3) What happens on auth failure?
   a) Redirect to login page
   b) Show inline error, stay on page
   c) Depends on context - describe: ___

Reply with: 1c 2a 3a (or describe)
```

After receiving answers, dig deeper:

```text
Got it: OAuth + email/password, JWT cookies, redirect on failure.

Follow-up on OAuth:

4) Which providers are must-have vs nice-to-have?
   a) Google only (most users have it)
   b) Google + GitHub (good for dev tools)
   c) Let users choose from: ___

5) Account linking - if user signs up with email, then tries Google with same email?
   a) Link accounts automatically
   b) Prompt user to link or keep separate
   c) Reject - must use original method
```

Continue until requirements are complete, then use `create-spec` to write the spec.
