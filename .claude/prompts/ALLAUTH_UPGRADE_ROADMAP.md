---
title: Allauth Upgrade Roadmap
tags:
  - projectctw
  - roadmap
  - security
  - auth
description: Implementation roadmap for upgrading django-allauth from 0.63.2 to the latest 65.x
---

# django-allauth Upgrade — Implementation Roadmap

**Target**: `django-allauth` **0.63.2 → 65.19.3** (latest on PyPI, confirmed 2026-09-15). Go all the way to latest — do not stop partway at a 64.x checkpoint.
**Status**: Phases 1–5 complete — real environment on 65.19.3, `manage.py check` clean, 74/74 tests passing, full manual auth-flow walkthrough confirmed, CI now gates on `manage.py check --fail-level WARNING`. Phase 6 (deploy) not yet started.
**Owner**: David

---

## Why This Exists

Auth is the highest blast-radius surface in the app. The 2026-09-14 case-sensitive login bug was traced to a silently-ignored `ACCOUNT_*` setting name that doesn't exist in the installed `0.63.2` — Django/allauth don't error on unrecognized `ACCOUNT_*` settings, they're just dropped. That means other settings could be silently drifted the same way, undiscovered until they cause a bug. Deliberately deferred as its own multi-session effort rather than a rider on that fix. See project memory `project_allauth_upgrade` / `project_python_314_migration` for full history.

Sequencing note: this is being done **before** the Event Planning UI's HTMX auth-redirect middleware (`base/middleware.py`, currently just `pass`) — that's new auth-adjacent code, better built on a current auth library than a known-stale one.

---

## Settings Translation Map (researched 2026-09-15, verified against current docs.allauth.org)

| Current (`settings.py`) | 65.x status | Action needed |
|---|---|---|
| `ACCOUNT_AUTHENTICATION_METHOD = "email"` | Renamed | → `ACCOUNT_LOGIN_METHODS = {"email"}` |
| `ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*']` | Unchanged, same syntax | none |
| `ACCOUNT_USERNAME_REQUIRED = False` | Obsolete | Remove — implied by no `username` in `ACCOUNT_SIGNUP_FIELDS` |
| `ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE = False` | Obsolete | Remove — implied by no `'password2'` in `ACCOUNT_SIGNUP_FIELDS` |
| `ACCOUNT_EMAIL_REQUIRED = True` | Obsolete | Remove — implied by `'email*'` in `ACCOUNT_SIGNUP_FIELDS` |
| `ACCOUNT_UNIQUE_EMAIL = True` | Unchanged | none |
| `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` | Unchanged (default changed to `"optional"` but we set explicitly) | none |
| `ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True` | Unchanged | none |
| `ACCOUNT_LOGOUT_REDIRECT_URL = "home"` | Unchanged | none |
| `ACCOUNT_FORMS = {...}` | Unchanged | none |

**Advantage for this specific upgrade**: 65.x ships a system check (`account.W001`) validating `ACCOUNT_LOGIN_METHODS` against `ACCOUNT_SIGNUP_FIELDS` — `manage.py check` will surface misconfiguration directly instead of silently dropping it, the way `0.63.2` did.

**Not yet audited**: `SOCIALACCOUNT_*` settings — currently unused (`allauth.socialaccount` is commented out of `INSTALLED_APPS`), so likely N/A, confirm in Phase 1.

**Known unresolved gap from the research pass**: the 64.0.0 release notes only formally flag Python/Django version-support drops as "breaking" — the settings changes above aren't marked breaking despite functionally changing behavior. Full changelog from 0.63.2 through 65.19.3 was not read entry-by-entry (100+ releases); Phase 1's `manage.py check` pass plus the full auth-flow walkthrough in Phase 4 are the real safety net for anything this table missed, not the changelog review alone.

---

## Phase 1: Isolated Upgrade + Check Pass — ✅ COMPLETE (2026-09-15)
**Goal**: See the real blast radius before fixing anything.

- [x] Confirm `SOCIALACCOUNT_*` settings audit — grepped repo-wide, only hit is the commented-out `# "allauth.socialaccount"` app line. Nothing else references it. Confirmed N/A.
- [x] Bump `django-allauth` to `65.19.3` — done in an **isolated scratch venv** (`/private/tmp/.../scratchpad/allauth-check-venv`, Python 3.14.7), not the working `.venv`/`requirements.txt`. Working dev environment untouched.
- [x] Run `manage.py check` against real `settings.py` — captured verbatim below
- [x] Note any other `ACCOUNT_*`/allauth-adjacent settings this table didn't anticipate — **none**. All 4 warnings exactly match the translation map researched last session.

**`manage.py check` output (65.19.3, isolated venv, real settings.py):**
```
System check identified some issues:

WARNINGS:
?: settings.ACCOUNT_AUTHENTICATION_METHOD is deprecated, use: settings.ACCOUNT_LOGIN_METHODS = {'email'}
?: settings.ACCOUNT_EMAIL_REQUIRED is deprecated, use: settings.ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*']
?: settings.ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE is deprecated, use: settings.ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*']
?: settings.ACCOUNT_USERNAME_REQUIRED is deprecated, use: settings.ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*']

System check identified 4 issues (0 silenced).
```
Result: the translation map from planning is validated — exactly these 4, no surprises. Phase 2 is now a known, bounded amount of work, not a guess.

## Phase 2: Settings Migration — ✅ COMPLETE (2026-09-15)
**Goal**: Resolve everything Phase 1 surfaced.

- [x] Apply the translation map above — user made the edit directly in `settings.py`: removed `ACCOUNT_AUTHENTICATION_METHOD`/`ACCOUNT_USERNAME_REQUIRED`/`ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE`/`ACCOUNT_EMAIL_REQUIRED`, uncommented `ACCOUNT_LOGIN_METHODS = {'email'}` (was already sitting there commented-out from the original 2026-09-14 bug investigation). `requirements.txt` and the real working `.venv` bumped to `django-allauth==65.19.3` (no longer isolated — this is the real environment now).
- [x] Re-run `manage.py check` clean — confirmed: `System check identified no issues (0 silenced)`
- [x] Diff `settings.py` against current docs one more time post-edit — the remaining allauth settings (`ACCOUNT_UNIQUE_EMAIL`, `ACCOUNT_FORMS`, `ACCOUNT_EMAIL_VERIFICATION`, `ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION`, `ACCOUNT_LOGOUT_REDIRECT_URL`) were already confirmed unchanged-in-name during Phase 1 planning research; some have new *defaults* in 65.x (e.g. `ACCOUNT_EMAIL_VERIFICATION` default flipped to `"optional"`) but this project sets all of them explicitly, so the default change has no effect.

## Phase 3: Automated Suite Pass — ✅ COMPLETE (2026-09-15)
**Goal**: Existing 74 tests still pass, or failures are understood and fixed.

- [x] Run full suite — 74/74 passing on the real 65.19.3 environment, no failures to triage
- [x] Special attention: any test reaching into allauth internals directly — grepped `userProfile/tests`/`events/tests` for `allauth.`/`filter_users_by_email`/`get_adapter`/etc. Only hit: `from allauth.account.models import EmailAddress` in `test_views.py` — a stable public model, not an internal function. Last week's `filter_users_by_email()` diagnostic calls were throwaway and never made it into the permanent suite, as recorded. No hidden internal-API dependency.

## Phase 4: Manual Auth-Flow Verification — ✅ COMPLETE (2026-09-15)
**Goal**: Every real user-facing flow confirmed working by hand, not just by test.

- [x] Signup (email + password)
- [x] Login — including the case-insensitive regression this whole upgrade traces back to, deliberately re-tested
- [x] Logout
- [x] Email verification (mandatory) — both the correct-link and expired-link paths confirmed
- [x] Password reset (all 5 pages, including `token_fail`)
- [x] Password change (logged in)
- [x] Email management — add / verify / set new primary / set original back to primary / delete — full round trip confirmed
- [x] Remember-me checkbox behavior
- [x] Custom login/signup forms (`CustomLoginForm`, `CustomSignupForm`, `CustomAddEmailForm`) — rendered/validated correctly throughout

## Phase 5: New Regression Coverage — ✅ COMPLETE (2026-09-15)
**Goal**: Lock in anything whose *behavior* (not just setting name) changed.

- [x] Identify any behavior change surfaced in Phases 1–4 that isn't already covered by an existing test — **none**. The settings-only translation held up perfectly across all 74 tests and the full manual walkthrough. No new test needed.
- [x] Process improvement instead: added a `System Check (fail on warnings, not just errors)` step to `ci.yml` (`python manage.py check --fail-level WARNING`, between `Migrate Database` and `Run Tests`) — CI previously ran `migrate`+`test` only, no `check` step existed at all. Verified locally: exit code 0.
  - **Known limitation, recorded honestly**: default `manage.py check` only fails on `ERROR`+, not `WARNING` — `--fail-level WARNING` was required to actually catch deprecation-class issues like the 4 this upgrade just fixed.
  - **This gate would NOT have caught the original 2026-09-14 bug** — that was a typo'd *future* setting name while still pinned to `0.63.2`, and neither old nor new allauth validates *unknown* `ACCOUNT_*` names, only ones it used to recognize and has since deprecated. This gate protects the *next* upgrade from leaving stale settings behind, not against writing a setting name too early.

## Phase 6: Deploy
**Goal**: Ship it safely, given this touches every user's session.

- [ ] Push to `main`, watch GitHub Actions CI
- [ ] Watch Railway logs post-deploy for auth-related errors
- [ ] Update `MEMORY.md` / `project_allauth_upgrade.md` — close out as complete

---

## Session Log

### 2026-09-15 (planning)
Planning session. Researched settings translation map (above) via docs.allauth.org and allauth.org release notes. Confirmed latest version is `65.19.3` (checked live via `pip index versions django-allauth`) — target is latest, not a 64.x stopping point. No code touched yet.

### 2026-09-15 (Phase 1)
Ran Phase 1 same day. Built an isolated scratch venv (Python 3.14.7, not the working `.venv`) with `requirements.txt` + `django-allauth==65.19.3`, ran `manage.py check` against the real `settings.py`. Result: 4 warnings, exactly matching the pre-researched translation map — `ACCOUNT_AUTHENTICATION_METHOD`, `ACCOUNT_EMAIL_REQUIRED`, `ACCOUNT_SIGNUP_PASSWORD_ENTER_TWICE`, `ACCOUNT_USERNAME_REQUIRED` all flagged deprecated, nothing else. `SOCIALACCOUNT_*` confirmed still N/A via repo-wide grep. Working `.venv`/`requirements.txt` untouched — real package bump happens in Phase 2. Scratch venv is disposable (lives in session scratchpad, not part of the repo).

Also created a dedicated `allauth-upgrade` branch off `development` before Phase 2 started (user's suggestion — multi-session, higher-risk change, keeps `development` stable/mergeable in the meantime).

### 2026-09-15 (Phase 2)
Same day. Bumped `requirements.txt` + real `.venv` to `django-allauth==65.19.3` for real. User made the settings.py edit themselves after a guided walkthrough of `ACCOUNT_SIGNUP_FIELDS` semantics (the `*` suffix = shown+required, no suffix = shown+optional, absent = not shown — one list now replaces what used to be 3 separate booleans). Verified independently: `manage.py check` clean, 0 issues. Environment is for-real on 65.19.3 now, not just the scratch venv.

### 2026-09-15 (Phase 3)
Same day. Full suite run: 74/74 passing on the real 65.19.3 environment, no failures. Grepped test files for direct allauth-internals usage per the plan's flagged risk — only hit is `EmailAddress` model import (stable public API), no internal function calls survived from last week's throwaway diagnostics. Three phases closed in one session.

### 2026-09-15 (Phase 4)
Same day — four phases in one session total. Full manual walkthrough by the user in the browser: signup, login (including a deliberate case-insensitive re-test — the exact regression that started this whole upgrade), logout, email verification (correct + expired link), password reset (all 5 pages incl. `token_fail`), password change, remember-me, and the full email-management round trip (add → verify → set new primary → revert primary → delete). Everything confirmed working, no issues found. Zero behavior changes surfaced across the entire manual pass — the settings-only translation from Phase 2 held up completely.

### 2026-09-15 (Phase 5)
Same day — five phases in one session. No behavior changes surfaced anywhere in Phases 1–4, so no new regression test was needed. Instead added a real CI process improvement: `ci.yml` had no `manage.py check` step at all before this (only `migrate`+`test`) — added one using `--fail-level WARNING` (not the default `ERROR`) since deprecation-class warnings like this upgrade's 4 don't fail the bare command otherwise. Explicitly scoped what this does and doesn't protect against: catches *future* upgrades leaving stale settings behind, would NOT have caught the original 2026-09-14 bug (a typo'd future setting name on an old pinned version — unknown setting names aren't validated by either version, only deprecated-known ones are).
