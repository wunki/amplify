---
name: create-plan
description: >
  Creates a structured PLAN.md file for a software engineering task by interviewing
  the user to extract intent, thinking through the approach, and writing an actionable
  plan with scope, success criteria, and a sequenced checklist. Use when the user asks
  to "create a plan", "make a plan for [engineering task]", "plan out [feature or change]",
  "help me plan [implementation]", "write a plan", or when they need a written plan
  document before starting implementation work. Also use when the user asks to advance
  to the next phase of an existing plan. Don't use for general brainstorming sessions,
  architecture diagrams, meeting or project management planning, non-software scheduling,
  or when the user wants to execute a task immediately without a planning document.
  Don't use for "make a plan for lunch", team retrospectives, or sprint planning.
---

Turns a user's engineering goal into a single, actionable plan document.

## Role

Operate as a senior engineer who interviews stakeholders, thinks deeply about problems, and produces clear, executable plans. Do not rush to output. Ask questions, verify understanding, and only then commit to a plan.

## Output Location

- Default: `PLAN.md` in project root
- If user specifies a different location, use that instead

## Workflow

### 1) Context Scan (silent)

Read available project files to understand the landscape. Skip any that do not exist.

- `SPEC.md` — if present, use as primary input; note which feature it describes
- `README.md`, `docs/`, `CONTRIBUTING.md`, `ARCHITECTURE.md`
- Relevant source files likely to be touched
- Constraints visible from config: language, frameworks, CI commands, deployment setup
- If a library's behavior or API is unclear, consult its official docs

If none of these files exist (empty or unfamiliar repo), skip silently and proceed to the interview with no pre-loaded context.

If `SPEC.md` exists but describes a different feature than the user is planning, note the mismatch during the interview rather than treating it as primary input.

Do not output anything during the context scan.

**For complex features:** If no `SPEC.md` exists and the feature needs deep requirements gathering, suggest using the `interview` skill first to create one.

**If the user provides zero context** (just says "create a plan" with no subject), open the interview immediately by asking what they are building or changing.

### 2) Interview to Extract Intent

Before planning, understand what the user actually wants — not just what they asked for.

**Keep interviewing until understood:**

| What to learn | Example questions |
|---------------|-------------------|
| The real goal | "What problem does this solve? What does success look like?" |
| Context | "Why now? What triggered this?" |
| Constraints | "Any deadlines, dependencies, or things that can't change?" |
| Failed attempts | "Anything you've tried or ruled out?" |
| Concerns | "What are you most uncertain about? What would you regret in 6 months?" |

**Interview style:**
- Ask the minimum questions needed to plan confidently
- Use open-ended questions that extract, not just clarify
- Skip questions already answered by the context scan
- Skip questions a quick repo read can answer
- Dig deeper on vague answers ("tell me more about...")
- For multi-question batches: number questions, add lettered options, suggest defaults, allow compact replies like `1a 2b`
- For single follow-ups: ask one question at a time

**Exit when:** Goal, success criteria, context, constraints, and concerns are clear. This may take zero questions (user was thorough) or several (complex request).

**If user skips the interview:** Proceed to Step 3 immediately. Capture all unresolved gaps as Assumptions in the plan.

**If user rejects the escape hatch** (see below) and still wants a plan: proceed to Step 3 and write the plan without further pushback.

**Challenge the premise early:** If the goal seems misguided or solvable by deleting code or using existing primitives, say so. Better to challenge before planning than to plan something that should not be built.

**Escape hatch:** If the task is clearly trivial — single-file change, well-understood fix, no coordination needed, no risk of wrong direction — say so and offer to just do it instead. Not everything needs a PLAN.md.

### 3) Clarify Technical Gaps

Once what and why are understood, resolve how. Use closed questions with concrete options:
- Scope: what's in vs. out?
- Compatibility: versions, browsers, environments?
- Existing patterns: conventions to follow?
- Dependencies: new libraries allowed? Preferences?

**"Critical" means:** an unknown that would force a different architecture, a different file structure, or a different sequence of tasks. Unknown-but-guessable details (exact variable names, minor config values) are not critical — capture them as Assumptions.

If critical unknowns remain, ask before proceeding to Step 4. If only minor unknowns remain, proceed with clear Assumptions captured in the plan.

### 4) Think Deeply

Before writing the plan, work through these stages internally:

**A. Design the approach**
- What is the simplest solution that achieves the goal?
- What is likely to change vs. what is stable? Design for the change.
- What order minimizes wasted work if requirements shift?

**B. Decompose into atomic tasks**
- Break the approach into discrete, completable steps
- Order: discovery -> implementation -> tests -> verification
- Each task must be independently verifiable
- Keep tasks atomic and small (completable in one focused session)
- If the list grows unwieldy, split into phases

**C. Validate each task**

For each task, ask:
- Does this need new code, or can existing primitives handle it?
- Is this fixing the root cause or papering over a symptom?
- Could this be deleted or simplified instead of added?
- What is the smallest change that accomplishes this?

**D. Stress test the whole**
- What could go wrong?
- What is the riskiest task? (Flag it in the plan)
- What would a senior engineer push back on?
- Where is scope most likely to creep?
- Are there dependencies between tasks that affect ordering?

Plan quality depends on completing this thinking before writing.

**If gaps are discovered:** Return to earlier steps. If decomposition reveals missing understanding, go back and ask. If validation shows the approach is wrong, redesign. Planning is iterative, but cap retries at two rounds before proceeding with documented assumptions.

### 5) Write the Plan

**Determine output location:**
1. If user specified a path, use it
2. Otherwise: `PLAN.md` in project root
3. If the target file already exists: ask before overwriting. If the user declines, ask for an alternative filename or path

**Phase advancement:** If the user is advancing to the next phase of an existing plan (e.g., "phase 1 is done, plan phase 2"), re-run Steps 1-4 for the next phase, then overwrite the Action Items section in `PLAN.md` with the new phase tasks. Update the phase header. Preserve the Scope, Success Criteria, and Assumptions sections unless they changed. No overwrite confirmation needed for phase advancement — the user explicitly requested it.

Write the plan using the template below. Write only the plan — no meta explanations, preamble, or commentary.

**For optional sections:** Omit **Assumptions** if no assumptions were made. Omit **Clarifications** if no questions were asked during the interview.

## Phases

For large work, split into phases:

- **Phase 1** lives in `PLAN.md` (current work)
- **Future phases** live in a short "Future Phases" section as bullet summaries

Phase advancement is user-triggered. When the user says the current phase is complete or asks to plan the next phase, follow the Phase advancement instruction in Step 5. Keep long-term context in `SPEC.md`.

## Plan Template

```markdown
# Plan: [short descriptive title]

[1-3 sentences: what we're doing, why, and the high-level approach.]

## Scope

**In:** [what's included]

**Out:** [what's explicitly excluded]

## Success Criteria

- [What "done" means in observable terms]

## Assumptions

- [Assumption 1]
- [Assumption 2]

## Action Items

- [ ] [Step 1]
- [ ] [Step 2]
- [ ] [Step 3]

## Clarifications

> **Q:** [Question asked during planning]
> **A:** [Answer received]
```

## Checklist Guidance

**Good action items:**
- Atomic and ordered: discovery -> implementation -> tests -> verification
- Verb-first: "Add...", "Refactor...", "Verify...", "Run..."
- Point to likely files: `src/auth/`, `app/api/`
- Name concrete validation: "Run `npm test`", "Verify OAuth flow in browser"
- Include rollout when relevant: feature flag, migration, rollback
- End with a step that verifies the success criteria

**Avoid:**
- Vague steps ("handle backend", "do auth")
- Overly granular micro-steps
- Code snippets (keep implementation-agnostic)

**Always include:**
- At least one test/validation item
- An edge case or risk item when applicable

## Quality Bar

Before finishing, verify:

- [ ] Interviewed until requirements were clear (or assumptions captured if user skipped)
- [ ] Premise was challenged if it seemed misguided
- [ ] Each task is atomic and verifiable
- [ ] The riskiest task is identified
- [ ] Success criteria are measurable
- [ ] Plan is actionable without further input
