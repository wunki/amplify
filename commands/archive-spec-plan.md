---
description: Archive root SPEC.md and/or PLAN.md into .specs/ and .plans/
---

Archive the root `SPEC.md` and/or `PLAN.md` into `.specs/` and `.plans/` using a shared, derived filename. This command moves the files (no copies), never creates directories, and works if only one of the files exists.

## Step 1: Verify required files and directories

```bash
test -f SPEC.md || test -f PLAN.md
test -f SPEC.md && test -d .specs
test -f PLAN.md && test -d .plans
```

If any check fails, stop and tell the user exactly what is missing. Do not create directories.

## Step 2: Derive archive name from title

If `SPEC.md` exists, read the first H1 with the `# Spec:` prefix. Otherwise, read the first H1 with the `# Plan:` prefix in `PLAN.md`. If missing, ask the user for a name.

Slug rules:

- Strip `# Spec:` prefix
- Trim whitespace
- Lowercase
- Replace spaces with `-`
- Remove non-alphanumeric characters (keep `-`)
- Collapse duplicate `-` and trim leading/trailing `-`
- Append `.md`

If the user provides a name, apply the same slug rules.

## Step 3: Compute target paths

- Spec target (if `SPEC.md` exists): `.specs/<slug>.md`
- Plan target (if `PLAN.md` exists): `.plans/<slug>.md`

## Step 4: Guard against overwrites

If any target path already exists, stop and ask whether to overwrite or choose a new name. Do not overwrite without explicit confirmation.

## Step 5: Move files

```bash
test -f SPEC.md && mv SPEC.md ".specs/<slug>.md"
test -f PLAN.md && mv PLAN.md ".plans/<slug>.md"
```

Confirm the final paths to the user.

## Step 6: Provide a brief description

Add a 1-2 sentence description of what the archived spec and/or plan cover.

- Prefer to summarize from the available spec summary or plan intro if they are clear and concrete.
- If the description is not obvious, ask the user for a short description and include it in the response.
- Keep it brief, plain language, and focused on the problem and approach.
