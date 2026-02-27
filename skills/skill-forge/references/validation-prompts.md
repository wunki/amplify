# Validation Prompts

Three ready-to-paste prompts for validating a skill before packaging.
Run each in a **fresh LLM chat** to avoid cross-contamination.

---

## Phase 1 — Discovery Validation

Tests whether the frontmatter description routes correctly.

> I am building an Agent Skill. Agents decide whether to load this skill based entirely on the YAML metadata below.
>
> ```yaml
> name: <skill-name>
> description: <paste full description here>
> ```
>
> Based strictly on this description:
> 1. Generate 3 realistic user prompts you are 100% confident should trigger this skill.
> 2. Generate 3 user prompts that sound similar but should NOT trigger this skill (false positives this description might cause).
> 3. Critique the description: Is it too broad? Too narrow? Missing negative triggers? Suggest an optimized rewrite if needed.

**What to fix if it fails:**
- False positives → add explicit negative triggers to the description
- False negatives → add the missing trigger language
- Too broad → narrow the verb phrases or domain scope

---

## Phase 2 — Logic Validation

Tests whether the step-by-step instructions are deterministic.

> Here is the full draft of my SKILL.md and its directory tree:
>
> ```
> <paste directory tree here>
> ```
>
> <paste full SKILL.md contents here>
>
> Act as an autonomous agent that has just triggered this skill. Simulate your execution step-by-step for this request: **"<paste a realistic trigger request>"**
>
> For each step, write your internal monologue:
> 1. What exactly are you doing?
> 2. Which specific file or script are you reading or running?
> 3. Flag any **Execution Blockers**: the exact line where you are forced to guess or hallucinate because the instructions are ambiguous.

**What to fix if it fails:**
- Execution Blockers → add explicit instructions, concrete examples, or move dense logic to a reference file
- Missing file references → add "Read `references/X.md` when..." instructions in SKILL.md

---

## Phase 3 — Edge Case Testing

Forces the LLM to find failure modes before users do.

> Switch roles. Act as a ruthless QA tester. Your goal is to break this skill.
>
> Ask me 3–5 highly specific, challenging questions about edge cases, failure states, or missing fallbacks in the SKILL.md. Focus on:
> - What happens if a script fails with an unexpected error?
> - What if the user's environment is missing a dependency?
> - Are there implicit assumptions about file structure, OS, or toolchain?
> - What configurations or variants does the skill not handle?
>
> Do not fix anything yet. Ask the numbered questions and wait for my answers.

After answering, continue:

> Based on my answers, update the SKILL.md to address these edge cases. Add an **Error Handling** section at the bottom if the skill involves scripts or external tools.

---

## Architecture Refinement (optional, post-Phase 3)

Enforces progressive disclosure — surfaces content that should move out of SKILL.md.

> Review the SKILL.md below and enforce the Progressive Disclosure design pattern:
>
> <paste SKILL.md>
>
> 1. Identify any dense rules, large templates, or detailed schemas currently in SKILL.md that belong in `references/` or `assets/` instead.
> 2. For each item found: tell me what new file to create and what exact instruction to replace it with in SKILL.md (e.g., "Read `references/schema.md` when the user asks about table structure").
> 3. Confirm that all reference files are one level deep only — flag any nested paths.
> 4. Confirm SKILL.md will be under 500 lines after the refactor.
