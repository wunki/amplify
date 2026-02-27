---
name: spec-story
description: Transforms a technical spec file (SPEC.md, PRD, RFC, ADR, or similar structured design document) into a narrative prose retelling that preserves every technical detail while making it engaging and story-driven. Writes output to STORY.md alongside the source file. Use when the user asks to "tell the story of this spec", "make this spec fun to read", "narrative version", "spec story", "story version of the spec", "make this spec readable", or wants to experience a spec as a flowing read rather than a structured document. Don't use for summarizing a spec into bullet points or a shorter overview, creating a new spec from scratch, converting specs to slide decks or presentations, explaining arbitrary code files that are not design documents, or when the user wants a standard technical summary rather than a full narrative retelling.
---

# Spec Story

Turn a dense SPEC.md into something you'd actually read on purpose.

## What this is

A retelling of a technical spec that has a pulse. Same information, completely different experience. The spec is the blueprint. This is the version that makes you want to go build the thing.

Think less "requirements document" and more "the best Slack message your tech lead ever wrote."

## What this is not

- Not a dumbed-down summary. The technical detail stays. All of it.
- Not a replacement for the spec. The spec is the source of truth. This is the one you read first, on the couch, maybe with a drink.
- Not marketing copy. No hype. We're not selling anything. We're explaining something to the person who has to build it.

## Workflow

### 1) Find the spec

If the user points to a specific file, use that.

Otherwise, search for a spec file in this order:
1. `SPEC.md` in the project root
2. Any `.md` file in the `specs/` or `docs/` directory whose name suggests it is a spec, PRD, RFC, or ADR
3. Ask the user to point to the file explicitly if none is found

If no spec file exists anywhere, tell the user and stop. Do not suggest other skills.

### 2) Read the entire spec

Read every section. Understand the full picture before writing a word. Look for:

- The core problem. What's actually broken?
- The "aha" moment. What's the clever bit in the design?
- The landmines. Where will this blow up if you're not careful?
- The honest gaps. What does nobody know yet?
- The drama. Was there a decision that could have gone either way?

Note any sections already written in narrative prose — absorb their voice but rewrite them to fit the unified story. Do not paste them in verbatim.

### 3) Write the narrative

Default to first person plural ("we") — it creates a sense of shared ownership and is the most natural voice for engineering narratives. Use second person ("you") only if the spec itself is framed as a user-facing tutorial or if the dominant concern is the developer's experience of building the feature. Pick one voice and hold it throughout.

The reader is the person about to build this thing. They're smart, they're busy, and they'll bail if you bore them.

**Structure the narrative as a story with tension and payoff:**

1. **The hook** (1-2 paragraphs): Open with the problem, not the solution. Make the reader feel the pain before you reveal the fix. If the problem is boring, find the angle that isn't. Every feature exists because something was bad enough that someone decided to spend money fixing it. Find that nerve.

2. **The lay of the land** (1-3 paragraphs): What exists today. What's broken, missing, or held together with duct tape. If there were previous attempts, they make great material: "We tried X in 2024. It worked until it didn't."

3. **The plan** (the bulk): Walk through the design like you're explaining it to a colleague who's following along. Don't enumerate components; introduce them as they become relevant. "When a user hits submit, the first thing that happens is..." pulls the reader through. "The system consists of three microservices" puts them to sleep.

4. **The hard parts** (1-3 paragraphs): This is where the story gets good. Edge cases, race conditions, the thing that will definitely bite someone at 2am. Lean into it. These aren't risks to be mitigated; they're the plot twists.

5. **The unknowns** (1 paragraph): What's still fuzzy. Frame it with honesty: "We don't know yet" is more interesting than "TBD".

6. **The finish line** (1 paragraph): What "done" looks like, in words a human would say.

### 4) Making it entertaining

This is the whole point. Readable is table stakes. Entertaining is the goal.

**Build tension.** Set up the problem before the solution. "The obvious approach is X. Here's why it falls apart." The reader should feel the constraint before they see the escape route.

**Have reactions.** When something in the spec is clever, say so. When something is gnarly, admit it. "This part is elegant" and "this part is a nightmare" are both more engaging than neutral description. Your genuine response to the material is what makes it human.

**Use surprise.** Lead the reader one direction, then pivot. "You'd think we could just cache it. You'd be wrong." Unexpected turns keep people reading.

**Be specific and visceral.** "The database melts" is better than "performance degrades." "The user stares at a spinner for eleven seconds" is better than "latency increases." Concrete details create mental images. Mental images create engagement.

**Vary your rhythm.** Long sentence that builds and layers and adds context. Short one that lands. Fragment for emphasis. Then back to flowing prose that carries the reader forward. Monotonous sentence length is the silent killer of interesting writing.

**Use callbacks.** Reference something from earlier in an unexpected way. "Remember that race condition we mentioned? It gets worse." This rewards the reader for paying attention and gives the piece structural cohesion.

**Earn your digressions.** Brief asides that add color are great. Parenthetical observations, one-sentence opinions, the occasional "yes, really." But every aside must either clarify, entertain, or both. If it does neither, cut it.

**Name the absurdity.** Software is full of absurd constraints. When something is ridiculous, say it. "We need four database tables for what is essentially a to-do list" is funny because it's true, and the reader was thinking it anyway.

### 5) Writing rules

**Do:**
- Short paragraphs. Three sentences max before a break.
- Code blocks for schemas, routes, and key data structures. They add precision and break up prose.
- Analogies when they clarify. "It's a queue, but with opinions" works. Forced metaphors don't.
- Opinions. "This is the right call because..." is more engaging than "this approach was selected."
- Contractions. Write like you talk.
- Start some paragraphs mid-thought. "Which brings us to the fun part."

**Don't:**
- Don't use spec headers. No "Background", "Goals", "Non-Goals", "Edge Cases". Those are filing cabinets. You're telling a story.
- Don't use bullet lists. If it's worth saying, weave it into a sentence. The only exception is a short list of truly parallel items (like API routes or error codes) where a table or code block is clearer.
- Don't hedge. "We're doing X because Y" not "we might consider potentially exploring X."
- Don't pad. If a section of the spec is boring, either find the interesting angle or fold it into something else. Boring sections don't exist; only boring writers do.
- Don't sacrifice precision for personality. You can be both accurate and entertaining. Every joke must also be true.

### 6) Format and headings

Use a handful of headings to create breathing room. Make them interesting enough that someone scanning would stop and read.

**Good headings:**
- "How a message actually gets from A to B"
- "The part where everything goes sideways"
- "What happens when the database says no"
- "Three tables for one toggle (yes, really)"
- "Okay but what if two users click at the same time"

**Bad headings:**
- "Technical Design"
- "Edge Cases"
- "Section 3: Data Model"
- "Overview" (the blandest word in English)

### 7) Output

- If the user specifies an output path, use that.
- If the spec is named `SPEC.md`, write to `STORY.md` in the same directory.
- For any other filename, append `-story` before the extension: `specs/feature.md` → `specs/feature-story.md`, `docs/RFC-42.md` → `docs/RFC-42-story.md`.
- If the output file already exists, notify the user and ask before overwriting.

### 8) Length

Aim for roughly 40-60% of the spec's word count. Dense specs get compressed; thin specs might expand where context helps. Floor: never produce fewer than 300 words regardless of source length — a stub is not a story. The narrative should feel like a satisfying read, not a marathon. If it's boring at any point, it's too long at that point.

## Quality checklist

Before finishing:

- [ ] Would you read this voluntarily? Not "is it useful." Would you actually enjoy reading it?
- [ ] Does it contain every important technical detail from the spec?
- [ ] Is there at least one moment where you smiled, raised an eyebrow, or thought "ha"?
- [ ] Would you feel oriented enough to start building after reading just this?
- [ ] Does it sound like a specific person wrote it, not a language model following a template?
- [ ] Are there zero bullet lists? (Tables and code blocks are fine. Bullet points are a spec reflex. Resist.)
- [ ] Did you name at least one absurdity, one clever decision, and one thing that scares you?

## Example transformations

### Turning a spec section into a story

**Spec:**
```markdown
## Edge Cases & Error Handling

- If the webhook delivery fails after 3 retries, mark the event as `failed`
  and emit a `webhook.delivery_failed` metric
- If the target URL returns a redirect, do not follow it; treat as a failure
- If the payload exceeds 256KB, reject at ingestion with a 413 response
- Race condition: two events for the same resource arriving within the retry
  window should be deduplicated by event_id
```

**Story:**
```markdown
## The part where deliveries go wrong

Most webhook deliveries are boring in the best way. Fire, receive, done. But
the interesting ones are the failures.

We give each delivery three chances. If it still can't land after three retries,
we mark it `failed` and fire a `webhook.delivery_failed` metric. At that point,
it's on the consumer's side and our monitoring picks it up.

One policy worth calling out: we don't follow redirects. If someone's endpoint
starts bouncing us to a different URL, we treat that as a failure. It might seem
strict, but the alternative is chasing redirect chains into the void, which is
both a security risk and a debugging nightmare.

Payloads over 256KB get rejected at the door with a 413. No negotiation. This
keeps the queue healthy and gives callers a clear signal to break up their data
instead of trying to shove a novel through the pipe.

Now for the genuinely tricky bit: two events for the same resource can arrive
within the retry window. Without deduplication, you get double-processing during
transient failures, which is the kind of bug that works perfectly in staging and
ruins someone's Tuesday in production. We deduplicate by `event_id`, so the
second arrival is a no-op. Simple fix, catastrophic without it.
```

### Turning a data model into a narrative

**Spec:**
```markdown
### Data Model

| Table | Fields | Notes |
|-------|--------|-------|
| events | id, type, payload, status, created_at | status enum: pending, delivered, failed |
| deliveries | id, event_id, attempt, status_code, responded_at | One row per attempt |
| subscriptions | id, url, secret, active, created_at | HMAC secret for signature verification |
```

**Story:**
```markdown
The data model is three tables, which feels right for this level of complexity.

`events` is the source of truth: every incoming webhook gets a row with its
payload and a status that moves from `pending` to `delivered` or `failed`. Think
of it as the manifest.

`deliveries` tracks each attempt separately. One event might generate three
delivery rows if the first two fail. This is what makes retry debugging possible
instead of maddening, you can see exactly which attempt got a 503 and which
finally landed.

`subscriptions` is where consumers register their endpoint URL and receive an
HMAC secret. Every outgoing delivery is signed with this secret, so consumers
can verify it's actually us knocking and not some random POST from the internet.
```
