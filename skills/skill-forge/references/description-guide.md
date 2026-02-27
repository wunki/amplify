# Writing Trigger-Optimized Descriptions

The `description` frontmatter field is the **only signal** the agent sees before deciding to load a skill. A weak description means the skill is invisible or fires on wrong requests.

Max 1,024 characters. No angle brackets (`<` or `>`).

---

## Formula

```
[Third-person capability statement]. Use when [specific trigger conditions].
Don't use for [negative triggers — what sounds similar but isn't this skill].
```

---

## Components

### Capability Statement
Describe what the skill does in the third person, using domain-specific verbs and nouns.

- Bad: "React skills."
- Good: "Creates and updates React components using Tailwind CSS, including state management, hooks, and prop interfaces."

### Trigger Conditions
List concrete trigger phrases, file types, or user intents that should load this skill. Be specific — generic conditions create false positives.

- Bad: "Use when working with documents."
- Good: "Use when the user needs to create, edit, or extract content from `.docx` files, work with tracked changes, or add comments to Word documents."

### Negative Triggers
Explicitly name what should NOT trigger this skill. This is the most commonly missing element.

- Bad: (no negative triggers)
- Good: "Don't use for Vue, Svelte, or vanilla CSS projects. Don't use for `.pdf` or `.odt` files."

---

## Examples

### Too vague (bad)
```yaml
description: Helps with Angular projects.
```
Will fire on any Angular question. No negative triggers.

### Overly specific (bad)
```yaml
description: Migrates Angular CLI webpack config to Vite when the user says "migrate to vite".
```
Too narrow — misses paraphrase variants.

### Well-calibrated (good)
```yaml
description: Migrates Angular CLI projects from Webpack to Vite and esbuild. Use when
  the user wants to update builder configurations, replace webpack plugins with rollup
  equivalents, or speed up Angular compilation. Don't use for React-to-Vite migrations,
  plain Webpack projects, or Angular version upgrades that don't involve the build system.
```

---

## Checklist Before Finalizing

- [ ] Capability is stated in third-person with domain-specific terms
- [ ] Trigger conditions include at least 2–3 concrete scenarios
- [ ] Negative triggers explicitly exclude the most likely false-positive domains
- [ ] Under 1,024 characters
- [ ] No angle brackets
- [ ] Name matches the directory name exactly, `[a-z0-9-]+`, max 64 chars

Run Phase 1 (Discovery Validation) to empirically verify before packaging.
