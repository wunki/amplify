# Task Summary Examples

Good summaries are concise, informative, and useful for future context.

## Good Examples

```markdown
- [x] Add user registration endpoint
  > POST /api/users in `src/routes/users.ts`. Validates email uniqueness,
  > hashes password with bcrypt (12 rounds). Returns 201 with user object
  > (password excluded). Tests in `src/routes/__tests__/users.test.ts`.

- [x] Implement dark mode toggle
  > Added ThemeContext in `src/contexts/theme.tsx`. Toggle component in
  > `src/components/ThemeToggle.tsx`. Persists preference to localStorage.
  > CSS variables defined in `src/styles/themes.css`.

- [x] Fix memory leak in WebSocket handler
  > Issue: Event listeners weren't cleaned up on disconnect. Added cleanup
  > in `useEffect` return. Verified with Chrome DevTools memory profiling.

- [x] Migrate from Moment.js to date-fns
  > Replaced all 23 Moment usages. Bundle size reduced by 64KB (gzipped).
  > See `src/utils/dates.ts` for wrapper functions maintaining old API.

- [x] Add rate limiting to public endpoints
  > Using express-rate-limit. Config in `src/middleware/rateLimit.ts`.
  > 100 req/15min for unauthenticated, 1000 for authenticated.
  > NOTE: Uses memory store; needs Redis for multi-instance deployment.
```

## Bad Examples (and why)

```markdown
- [x] Add user registration endpoint
  > Done.
```
Too brief. No context for future reference.

```markdown
- [x] Add user registration endpoint
  > Created a new file called users.ts in the src/routes directory. In this
  > file, I added a POST endpoint that handles user registration. The endpoint
  > first checks if the email already exists in the database by querying the
  > users table. If it does, it returns a 409 conflict error. If not, it
  > proceeds to hash the password using bcrypt with a cost factor of 12...
```
Too verbose. This is implementation detail, not a summary.

```markdown
- [x] Add user registration endpoint
  > Fixed the bug and added some tests.
```
Vague. What bug? What tests? Where?

## Format Guidelines

- Start with what was done, not how
- Include file paths for key changes
- Note important decisions (e.g., "bcrypt 12 rounds", "localStorage not cookies")
- Flag follow-up work with NOTE:
- Keep to 1-3 lines unless complexity demands more
- Use backticks for paths and code references
