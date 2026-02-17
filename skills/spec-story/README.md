# Spec Story

A Claude Code skill that transforms dense technical specs into narratives you'd actually read on purpose. Same information, completely different experience.

## When to use

When you have a SPEC.md and want a version that's fun to read before you start building. Trigger phrases: "make this readable", "tell the story", "narrative version", "explain this spec", "make this fun to read", "story version", "readable spec".

## What it does

Takes a structured spec (headers, bullet lists, tables) and rewrites it as a story with tension, personality, and opinions. Technical detail stays. Dry formatting goes. Edge cases become plot twists.

## How it entertains

- Builds tension (problem before solution, constraint before escape route)
- Has genuine reactions (calls out clever decisions and nightmares alike)
- Uses surprise ("You'd think we could just cache it. You'd be wrong.")
- Names the absurdity ("Four tables for what is essentially a to-do list")
- Varies rhythm (long setup, short payoff, fragment, flowing prose)
- Zero bullet lists (if it's worth saying, weave it into a sentence)

## Story structure

1. **The hook**: The problem, and why it hurts
2. **The lay of the land**: What exists today, what's broken
3. **The plan**: Design as narrative, not enumeration
4. **The hard parts**: Where it gets interesting (the plot twists)
5. **The unknowns**: Honest about what's fuzzy
6. **The finish line**: What done looks like

## Output

Writes a `STORY.md` alongside the source spec.

## Usage

```
/spec-story
```

Requires an existing SPEC.md. Pairs with the `create-spec` skill.
