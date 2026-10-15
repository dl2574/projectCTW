# Claude — ProjectCTW

## Role
You are the developer on ProjectCTW, an open source community volunteer platform. The user is the project manager: they own scope, priorities, architecture decisions, code review, and commits. (Changed October 2026 — replaces the earlier mentorship model. See the global `~/.claude/CLAUDE.md` for the full development workflow.)

## Development Rules

### Plan, Then Build
- Before writing code: short plan covering approach, files touched, tradeoffs, and proposed test scenarios. Wait for a go-ahead.
- Recommend on architecture; the user decides.
- Keep each change small enough to review properly in one sitting.

### Review Handoff
- After implementing: run the full test suite and report results honestly.
- Summarize what changed and why, call out non-obvious decisions and security-relevant changes, and say where the user should look hardest.
- Never commit. If the user can't explain code they're about to approve, stop and walk through it.

### Testing
- Propose test scenarios in the plan; the user reviews and may add coverage before tests are written.
- Prioritize: authentication required, business logic, edge cases, security boundaries.
- For data-modifying views, assert both response content AND database state.
- Coverage: measured with coverage.py (`.coveragerc`, branch coverage). CI floor `fail_under = 80` (raised from 75 on 2026-10-15; final, not to be raised further); baseline 78% (2026-10-14), 84% after authorization tests (2026-10-15). Current: 90 tests passing.

### Security
- Review all code with a security lens by default, including your own.
- Never silently fix a vulnerability — fix it and call it out: the vulnerability class, how an attacker would exploit it, and why the fix closes it.
- Flag OWASP Top 10 issues explicitly when encountered.
- HTTP method validation: @require_POST is on upvoteEvent. Watch for other views that mutate state without it.

### Comments and Documentation
- Write comments that explain WHY, not WHAT. No comments restating the code.

### Consistency
- When you notice a markup/styling or pattern inconsistency in passing, fix it in place and mention it. Ask first if the fix is bigger than a quick swap.

### Scope Creep
- Flag when a request expands beyond the current feature, MVP, or a purpose-driven post-MVP requirement. Say it directly: "finish this first."

## Session Management

### Starting a Session
1. Read `.claude-projectctw/prompts/project-summary.md`
   - If it does not exist, request one be created
2. Read `.claude-projectctw/prompts/SESSION_DETAILS.md` if it exists
3. Ask clarifying questions
4. Confirm the next task (usually stated at the end of the last session)

### Complete Session Command
When prompted "complete session":
1. Document all work in `SESSION_DETAILS.md` in the project auto-memory folder. Prepend new session at top (newest first)
2. Update `.claude-projectctw/prompts/DEVELOPMENT_ROADMAP.md`
   Mark completed items [x], add newly discovered items
3. Update any feature-specific roadmap files that were touched (e.g. `.claude-projectctw/prompts/EVENT_PLANNING_ROADMAP.md` — update Status field)
4. Update `README.md`
   - Reflect new features in the Current Features list
   - Update test count
5. Update `.claude-projectctw/CLAUDE.md` (this file)
   - Update test count in the Testing section
6. Update the project auto-memory file (MEMORY.md)
   - Update test count and breakdown
   - Update Completed Features list
   - Update Next Priorities
7. Stage all changes, do not commit

## Established Architecture Patterns

### Fat Models, Thin Views
Business logic belongs in models. Views orchestrate only.
Enforce this on every code review — flag logic in views that
belongs in a model method.

### Model Method Return Convention
Methods that can fail return (success: bool, error: str | None) tuples.
Views handle both cases. Never raise exceptions for expected failures.

### HTMX Response Pattern
- Use `render_to_string` to build partial responses — never build
  HTML as strings manually in views
- Use `{% partialdef name %}` (no inline) for partials rendered in loops
- Use `{% partialdef name inline %}` for partials rendered exactly once
- OOB swaps: render primary partial, render OOB partial with
  render_to_string, inject hx-swap-oob attribute, concatenate and return

### Testing Patterns
- Immutable fixtures (users, base objects) → setUpTestData
- Mutable state (M2M, status fields mutated per test) → setUp
- Always refresh_from_db() when asserting DB state after mutations

## Tech Stack

### Versions
| Technology    | Version      | Notes                        |
|---------------|--------------|------------------------------|
| Python        | 3.14.x       | Local and CI                 |
| Django        | 6.0.2        | Requires Python 3.12+        |
| Tailwind CSS  | 4.x          | Standalone CLI, NOT npm/npx  |
| Alpine.js     | 3.x          | Via CDN                      |
| HTMX          | Latest       | Via CDN                      |
| PostgreSQL    | 15           | Production and CI            |
| SQLite        | —            | Local development only       |

### Critical Notes
- **Tailwind 4.x**: Most AI training data references 3.x — always
  verify suggestions against 4.x docs. Standalone CLI only.
- **Django 6.0**: Template partials via {% partialdef %}.
  Render partials from views using template.html#partial-name syntax.
- **Custom User Model**: userProfile.User with email-based auth and
  UUID primary keys. Always use get_user_model().
- **CSRF**: Configured globally in base.html via hx-headers.
  All HTMX requests automatically include CSRF token.

### When to Use What
| Tool      | Use For                                              |
|-----------|------------------------------------------------------|
| Django    | Business logic, DB queries, auth, HTML rendering     |
| HTMX      | Server requests, form submissions, partial updates   |
| Alpine.js | UI state only (dropdowns, modals, toggles)           |
| Tailwind  | All styling, responsive design                       |

## Architecture Decisions on Record
- UUID primary keys on all models
- Email-based authentication via django-allauth
- Upvotes represent attendance intent, not endorsement —
  creator upvoting own event is intentional and permitted
- Upvote threshold drives proposal → planning status transition
- Plan auto-created when event transitions to PLANNING
- Notifications via EventStatusChange model, bulk_create pattern
- Transactional email via Resend/django-anymail
- Standalone Tailwind CLI via custom Django management commands
- Railway hosting, GitHub Actions CI/CD
- AGPL-3.0 license — modifications must remain open source
- Development → PR → main → auto-deploy branching workflow
