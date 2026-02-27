---
name: stop-slop
description: >
  Detects and removes AI writing patterns from prose to make text sound human.
  Use when the user asks to clean up, edit, review, or rewrite text that sounds
  like AI, contains AI tells, or reads as generic filler. Use when drafting new
  prose with explicit instructions to avoid AI patterns or sounding robotic.
  Don't use for grammar fixes, spell-checking, general tone rewrites, style
  changes unrelated to AI patterns, code review, SEO optimization, or
  translation. Don't use if the user wants the writing to sound more formal or
  professional without mentioning AI patterns specifically.
---

# Stop Slop

Eliminate predictable AI writing patterns from prose while preserving the author's voice and intent.

## When to Load References

Read `references/phrases.md` when identifying or removing filler phrases, business jargon, or emphasis crutches. Skip if the user's request is purely structural (rhythm, fragmentation).

Read `references/structures.md` when identifying or fixing binary contrasts, dramatic fragmentation, rhetorical setups, or rhythm problems. Skip if the user's request is purely about specific word choices.

Read `references/examples.md` when the user asks for examples, before/after rewrites, or when demonstrating a transformation would clarify a correction. Skip if the user has not asked for examples and the correction is self-evident.

## Core Rules

1. **Cut filler phrases.** Remove throat-clearing openers and emphasis crutches. Specific phrases are in `references/phrases.md`.

2. **Break formulaic structures.** Avoid binary contrasts, dramatic fragmentation, rhetorical setups. Patterns are in `references/structures.md`.

3. **Vary rhythm.** Mix sentence lengths. Two items beat three. End paragraphs differently.

4. **State facts directly.** Skip softening, justification, hand-holding.

5. **Cut quotables.** If it sounds like a pull-quote, rewrite it.

6. **Preserve voice.** Remove patterns without flattening the author's distinctive choices. A phrase is deliberate (not slop) when it appears consistently in multiple places, uses unusual word choice unique to the author, or is structurally necessary (e.g., a technical instruction like "Navigate to Settings"). Flag it rather than silently removing it.

7. **Skip technical content.** Do not apply prose rules to code blocks, filenames, CLI commands, UI labels, or technical terms embedded in prose (e.g., "Navigate to the Settings page" in a tutorial is a UI instruction, not business jargon).

## Quick Checks

Before delivering prose:

- Three consecutive sentences match length? Break one.
- Paragraph ends with punchy one-liner? Vary it.
- Em-dash before a reveal? Remove it.
- Explaining a metaphor? Trust it to land.

## Scoring

Rate 1-10 on each dimension:

| Dimension | Question |
|-----------|----------|
| Directness | Statements or announcements? |
| Rhythm | Varied or metronomic? |
| Trust | Respects reader intelligence? |
| Authenticity | Sounds human? |
| Density | Anything cuttable? |

Below 35/50: revise. Perform one revision pass, then re-score. Stop after the second pass regardless of score — additional passes risk changing the author's meaning. If the score is still below 35 after two passes, note the remaining issues and ask the user whether to continue.

If the text is under 50 words, skip scoring and apply the Core Rules and Quick Checks only.

## Workflow

1. Determine the task:
   - **Editing existing prose** ("clean up", "rewrite", "fix"): apply Core Rules, run Quick Checks, score, revise if below 35.
   - **Writing new prose** ("write", "draft"): apply Core Rules as constraints during drafting; score the draft before delivering.
   - **Review/audit only** ("review", "check", "flag", "what's wrong"): list flagged patterns with location references, score, and stop — do not rewrite.
   - **Ambiguous request** ("take a look", "what do you think"): ask whether the user wants a rewrite or an audit before proceeding.

2. If the text is ambiguous in intent (e.g., a stylistic fragment that could be deliberate), flag it with a one-line note rather than silently removing it.

3. Deliver the output. If patterns were intentionally left, list them at the end with a one-sentence reason for each.
