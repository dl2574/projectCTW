---
title: Session Details
tags:
  - projectctw
  - sessions
description: Chronological log of development sessions, newest first
---

# Session Details

---

## Session: 2026-07-19

### What We Did
Wrote and verified the `account/email.html` conditional button logic tests carried over from 2026-07-10. Three test methods added to `EmailTemplateLogicTests` in `userProfile/tests/test_views.py`, covering the three reachable `(primary, verified)` states for an `EmailAddress` row. Full suite: 73 tests passing (was 70).

### Test Scenario Design (discussion, before any code)
- Worked through all 4 combinations of `(primary, verified)` for a row: `(True,True)` → no buttons, `(False,True)` → Make Primary + Delete, `(False,False)` → Resend Verification + Delete.
- `(True,False)` (primary but unverified) initially flagged as a possible 4th case, then ruled out after tracing the actual code paths: `account_email` can only be viewed by an authenticated session, login enforces `ACCOUNT_EMAIL_VERIFICATION = "mandatory"`, and no view action can revert an already-verified primary back to unverified. Concluded there's no real code path that renders the template in that state — decided not to test it. Correct call, not just a shortcut.
- Confirmed assertions should be response-content only (`assertContains`/`assertNotContains` on button `name` attributes) — not testing allauth's own POST handling, only the template's conditional rendering given a DB state.
- Decided against a single page with all 3 states rendered at once and scoped per-row assertions — the per-row wrapper `<div>` was removed in the 2026-07-09 grid alignment fix, so there's no DOM boundary to scope a check to. Three isolated single-state test methods instead.

### Bugs Found and Fixed While Writing
- `setUpTestData` was missing `@classmethod` — would have raised `TypeError` when Django calls `cls.setUpTestData()`.
- `assertNotContains(response, "action_verify")` — checked a string that doesn't exist anywhere in the template (`action_send` is the actual name attribute), so it was a no-op assertion that would pass regardless of correctness.
- Forgot `.save()` after mutating `self.email.primary`/`self.email.verified` in-memory — mutation never reached the DB, so the view would've queried stale state.

### Real Bug Uncovered: allauth Auto-Creates an EmailAddress on GET
`account_email`'s view (`allauth/account/views.py`) calls `sync_user_email_addresses(request.user)` on every GET, silently creating an `EmailAddress(primary=False, verified=False)` for `user.email` if no matching row exists. The test `User` was built via `create_user()`, bypassing allauth's signup flow, so it had no such row — the first GET request created a phantom row that leaked an unexpected `action_send` button into the response and broke an assertion.
Fix: `setUpTestData` now creates a `primary=True, verified=True` `EmailAddress` for the user's own email up front — this also matches reality, since mandatory verification means a real logged-in user's primary email is always verified by the time they can view the page.

### Second Bug: DB Constraint on Primary Email
Attempted to test "no buttons" by flipping the baseline row's `primary=False` and the test row's `primary=True, verified=True` in the same test. This recreated the exact multi-row contamination problem the row-isolation decision was meant to avoid — the baseline row, now `(primary=False, verified=True)`, correctly showed its own Make Primary/Delete buttons, which broke the assertions meant for the other row. Also touched allauth's DB-level `UniqueConstraint(fields=["user", "primary"], condition=Q(primary=True))` — only one primary row per user, enforced at the database. Fixed by deleting the extra test row for that one test instead, leaving only the already-correct baseline row on the page.

### Memory Updates
- Saved a testing-gotchas entry to project auto-memory: the allauth auto-create-on-GET behavior, the primary-email DB constraint, and the row-isolation pattern for future `email.html`-adjacent tests.
- Saved a feedback memory: don't ask the user to paste code — read files directly once they report a save.

### Next Session
- Input/form field styling refactor sitewide — global `input` selector in `input.css` broke some fields on `user_account.html`. Need a consistent approach across all forms.

---

## Session: 2026-07-10

### What We Did
Short session — fixed the button text wrapping regression carried over from 2026-07-09. Started prepping for the `account/email.html` conditional button logic tests but got sidetracked by an nvim configuration issue and tabled it. No test code written.

### Button Wrapping Fix (complete)
- Added `white-space: nowrap;` to `.btn-sm` in `static/css/input.css`
- Tailwind rebuilt (`static/css/main.css` regenerated — diff is mostly unrelated unused-class pruning from the rebuild, not hand-edited)
- Confirmed manually: "Resend Verification" / "Make Primary" no longer wrap under the grid's auto-sized button column
- 70 tests still passing, no regressions

### Test Prep (incomplete, tabled)
- Added imports to `userProfile/tests/test_views.py` (`get_user_model`, `allauth.account.models.EmailAddress`) in anticipation of writing the `account/email.html` button-logic tests
- No test class/methods written — scenario planning (what states/combinations to assert, response content vs. DB state) still hasn't happened

### Next Session
- Write tests for `account/email.html` conditional button logic (`action_send`/`action_primary`/`action_remove` per `email.primary`/`email.verified` state) — ask what scenarios/assertions before writing any test code
- Then: input styling refactor sitewide

---

## Session: 2026-07-09

### What We Did
Fixed the `account/email.html` row alignment bug carried over from 2026-07-06. Discussed but deferred: conditional button logic tests for the same template.

### Row Alignment Fix (complete)
- **Root cause confirmed**: each email row was its own independent flex container. `<p>` had `flex-1` and grew to fill whatever space the row's `<form>` didn't use. On the primary email's row, the form renders zero buttons (collapses to 0px width), so `<p>` grows further right than on other rows, shifting the badge's position — each row computed its own column widths independently, so nothing stayed aligned across rows.
- **Rejected fixed-pixel widths** (`w-[200px]` on the form) as brittle — hardcoded values silently go stale when content changes (already bit us once with button text wrapping).
- **Fix applied**: moved the grid to the *list wrapper* rather than per-row, so column tracks are shared across all rows instead of recalculated per-row:
  - Wrapper (`md:col-span-2`) changed from `space-y-6` to `grid grid-cols-[1fr_auto_auto] items-center gap-x-12 gap-y-6`
  - Removed the per-row `<div class="flex items-center gap-12">` wrapper — each row's three elements (`<p>`, badge `<div>`, `<form>`) are now direct grid children, auto-flowing into rows
  - Dropped `flex-1` from `<p>` and `min-w-[90px]` from the badge div (grid handles sizing now); badge div kept `flex gap-2` for when both badges render together
- **Verified manually in browser** (dev server + local test user with a primary/verified row and a secondary/unverified row) — user confirmed rows are now aligned correctly.
- **Regression found during verification**: button text ("Resend Verification", "Make Primary") wraps onto two lines again. The `auto`-sized button column is now sized to the *narrowest* content that still fits across rows, which is tighter than before. Deferred — not fixed this session.

### Concepts Covered
- Flexbox default sizing (`flex: 0 1 auto`) — why an empty flex child collapses to 0 width instead of holding space
- Why per-row flex containers can't produce cross-row alignment — each is an independent layout context with no shared sizing information
- CSS Grid column tracks as the fix — defining `grid-template-columns` once on a shared parent means all rows size against the same tracks (widest content across *all* rows), instead of each row negotiating its own layout in isolation

### Next Session
- Fix button text wrapping regression (`whitespace-nowrap` on `.btn-sm`, or shorten "Resend Verification" / "Make Primary" labels)
- Write tests for `account/email.html` conditional button logic (`action_send`/`action_primary`/`action_remove` per `email.primary`/`email.verified` state) — user was asked what scenarios/assertions they'd want before any test code is written; not yet answered

---

## Session: 2026-07-08

### What We Did
Design discussion session — no code written. Fleshed out proposal redesign and docketed several future features.

### Proposal Field List (finalized for now)
- **Name** — unchanged
- **Objective** — 1-2 sentence mission statement
- **Problem** — what's wrong and why it matters
- **Resolution** — what will be done about it
- **Impact** — what the community gains (also serves sponsor audience)
- **Activity tags** — multi-select, filterable (Clean Up, Repair, Build, etc.) — design discussion needed before building
- **Virtual toggle** + **location text** — short term; GeoDjango later
- **Minimum volunteer count** — integer, user-provided estimate; drives upvote threshold

### Deliberately Excluded from Proposal
- Supplies — too many unknowns, belongs in plan
- Budget — same reason; proposal is a community interest check not a project plan
- Duration — can't know without knowing volunteer count and skill level; belongs in plan

### Upvote Threshold Formula
`required_num_upvotes = max(10, ceil(min_volunteers * 1.5))` — calculated on save, not user-editable. Platform-wide. Floor of 10. Revisit post-launch with real data.

### Docketed
- GeoDjango setup as dedicated prerequisite task before any location-dependent features
- Print/PDF export (WeasyPrint) — build after each feature is stable, not during development
- Public roadmap page — after plan feature is complete
- Activity tags + skill tags — two distinct systems, design discussion needed before building

### Next Session
- Finish email row alignment bug (`account/email.html`)
- Then: write tests for conditional button logic
- Then: input styling refactor sitewide
- Proposal development begins after email/account verification work is wrapped up

---

## Session: 2026-07-06

### What We Did
Continued polishing `account/email.html`. Fixed button sizing, back button, and header. Ran into row alignment issue — not yet resolved.

### Completed
- Removed `<h1>Email Management</h1>` — redundant with user card header
- Replaced `btn-secondary` back button with plain muted text link: `← Account Settings`
- Added `.btn-sm` class to `input.css` (`padding: 0.375rem 0.625rem`, `font-size: 0.75rem`) — layered on top of `.btn-outline`/`.btn-danger` for smaller row buttons
- Fixed `.btn-primary` duplicate selector bug introduced by autocomplete (was overriding btn-primary instead of creating btn-sm)
- Added `mt-2` to Add Email submit button for spacing
- Logic fix: `action_primary` (Make Primary) now only shows when `email.verified and not email.primary` — you can't make an unverified address primary
- Added `w-[90px]` to badge container to reserve space when no badges present
- Added `flex-1` to email `<p>` to anchor badges and buttons to the right

### Remaining Alignment Issue (pick up here)
Row layout uses flex with three children: email text (`flex-1`), badge container (`w-[90px]`), form (buttons). When a row has no buttons the form is empty but still present — the badge gets pushed off-center. Tried `flex-shrink-0` on the form, no effect. 

**Root cause**: with `flex-1` on the email text and no fixed anchor on the form, the empty form doesn't hold its space consistently.

**Next approaches to try**:
- Give the form a fixed width (`w-[200px]` or similar) matching the widest button combination
- Or switch the row from flex to a 3-column CSS grid with fixed column definitions

---

## Session: 2026-07-05

### What We Did
Built `templates/account/email.html` — nearly complete, two polish items remaining for next session.

### Design Decision: Per-Row Layout (complete)
- Rejected allauth's radio + bottom buttons pattern in favor of per-row forms
- Rationale: users will have 1-2 emails max; per-row is clearer, removes radio selection step
- Each email row has its own `<form>` posting to `{% url 'account_email' %}` with a hidden `name="email"` input
- allauth routes by button `name` attribute: `action_primary`, `action_send`, `action_remove`

### email.html Structure (complete)
- Extends `base.html`, matches `user_account.html` fieldset/grid layout
- Loops `{% for email in emailaddresses %}` (not `emailaddress_radios` — simpler, same objects)
- Row layout: email text | badges | form buttons (flex, items-center, gap-12)
- Badges: `.badge.badge-primary` (Primary), `.badge.badge-warning` (Unverified) — both can appear simultaneously (allauth allows unverified primary)
- Conditional buttons per row:
  - `action_send` (Resend Verification): `{% if not email.verified %}`
  - `action_primary` (Make Primary): `{% if not email.primary %}`
  - `action_remove` (Delete): `{% if not email.primary %}` — user must set a new primary before deleting
- JS IIFE confirm dialog on Delete (copied pattern from allauth default, stripped i18n)
- `{% if can_add_email %}` section: Add Email form using `add_email_form` context variable
  - `add_email_form.email` rendered via `{{ add_email_form.email }}` (Django widget, styled via CSS selector)
  - Field errors via `add_email_form.email.errors.0`, non-field errors via `add_email_form.non_field_errors`
  - Submit button `name="action_add"`
- Back button: plain `<a href="{% url 'account_profile' user.username %}">` with `btn-secondary`

### input.css Refactor (complete)
- Added global `input` selector to `static/css/input.css` — styles all inputs sitewide without Tailwind classes
- Converted widget `attrs` classes from `userProfile/forms.py` `CustomUserChangeForm.__init__` to CSS
- Added `.btn-danger` class: red-500 base, red-600 hover, matches btn-primary/secondary pattern
- Removed redundant `sm:` media query (values already set globally)
- Note: `userProfile/forms.py` still has the Tailwind classes on widget attrs — those should be removed in a follow-up cleanup once input.css is confirmed working everywhere

### Remaining Polish (pick up next session)
1. **Button text wrapping** — "Resend Verification" and "Make Primary" wrap onto two lines, making buttons oversized. Fix: shorten button text (e.g., "Resend" / "Make Primary" → shorter) or add `whitespace-nowrap` to buttons
2. **Add Email form spacing** — "Add" button is touching the input field. Add `mt-4` or similar margin-top to the button

### Concepts Covered
- allauth `EmailView.get_context_data` — `emailaddresses` vs `emailaddress_radios` (same objects, radios just add wrapper dict)
- allauth POST routing: single endpoint, button `name` attribute tells the view which action to take
- `type="submit"` buttons with `name` — clicked button's name is included in POST data
- `e.preventDefault()` — cancels default browser behavior (form submit); if omitted, form submits normally
- IIFE pattern (Immediately Invoked Function Expression) — scope isolation pre-ES6
- `emailaddresses|length > 1` — Django template `{% if %}` syntax for length comparison
- `add_email_form` vs `form` context variable — allauth passes both, `add_email_form` is the explicit name
- Per-element vs. global CSS selectors for form inputs — global `input {}` cleaner than per-widget attrs

---

## Session: 2026-07-02

### What We Did
Started building `account/email.html`. Removed email management from `CustomUserChangeForm` and `user_account.html` in favor of allauth's built-in email management page. Wired HTMX seamless navigation to the allauth email page from account settings. Did NOT yet create `account/email.html` — ran out of time.

### Email Field Removed from Account Settings (complete)
- Removed `"email"` from `CustomUserChangeForm.fields` in `userProfile/forms.py`
  - Rationale: allauth manages email addresses (verified state, primary address, multiple addresses) better than a plain editable field; data integrity and security
  - Admin panel unaffected — uses `UserAdmin`'s own form, not `CustomUserChangeForm`
- In `user_account.html`, replaced email `<div>` with "Manage Emails" HTMX button:
  ```html
  <button hx-get="{% url 'account_email' %}"
          hx-target="#main-container"
          hx-select="#main-container"
          hx-push-url="true">Manage Emails</button>
  ```
  - `hx-select="#main-container"` extracts only the content div from the full page response — navbar stays put, only content swaps
  - `hx-push-url="true"` updates the URL so back-button works
  - POST actions inside the email page are regular form POSTs (allauth handles them), redirect normally — that's acceptable

### Test Impact
- `test_profile_picture_correct_size` in `test_forms.py` passes `email` in form data — harmless, Django ignores unknown fields

### account/email.html — NOT YET BUILT
Context for next session:
- Template lives at `templates/account/email.html` (does not exist yet)
- Must extend `base.html`, NOT allauth's base — use plain HTML, not `{% element %}` tags
- Match layout from `user_account.html`: `mx-auto max-w-7xl` container, fieldset/grid pattern, same button classes
- Allauth context variables:
  - `emailaddress_radios` — list of dicts: `{emailaddress, checked, id}`
  - `emailaddress.email`, `emailaddress.verified`, `emailaddress.primary`
  - `can_add_email` — bool, controls whether Add Email section renders
  - `form` — the add-email form (single email field)
- Three POST actions, all submit same form, distinguished by button `name`:
  - `action_primary` — Make Primary
  - `action_send` — Re-send Verification
  - `action_remove` — Remove (needs JS confirm dialog)
- POST target: `{% url 'account_email' %}` (resolves to `/accounts/email/`)
- Include "← Back to Account Settings" link at the top
- JS confirm dialog on Remove (copy from allauth default or rewrite inline)

---

## Session: 2026-06-28

### What We Did
Styled allauth email verification templates. Diagnosed quoted-printable encoding in console email output. Added auto-login on email confirmation. Reviewed `account/email.html` for next session.

### Email Confirm & Verification Sent Templates (complete)
- `templates/account/email_confirm.html` — extended `base.html`, styled with Tailwind, shows email address and confirm button, handles expired/invalid key branch with link back to email management
- `templates/account/verification_sent.html` — extended `base.html`, styled with Tailwind
- `ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True` added to settings — user is auto-logged in after clicking confirmation link (safe: they just proved email ownership)

### Quoted-Printable Encoding (debug)
- Console email backend renders emails in quoted-printable format — long lines wrap with `=` at line end
- "confirm-emai=l" in console output was NOT a typo — `=` is a soft line-break marker; joining lines gives the correct URL
- No code change needed

### account/email.html — Reviewed, Not Yet Styled
- Lists all email addresses as radio buttons with Verified/Unverified/Primary badges
- Three form actions on selected radio: Make Primary, Re-send Verification, Remove
- Add Email section (conditional on `can_add_email`)
- JS confirm dialog on Remove button
- All three actions POST to `accounts/email/` — allauth routes by button `name` attribute
- More complex than the other two templates; style next session

---

## Session: 2026-05-24

### What We Did
Wired `collectstatic` into Railway pre-deploy command. Deleted stale Procfile. Completed profile picture form validation tests. Practiced commit message writing.

### collectstatic in Railway (complete)
- Pre-deploy command updated to: `python manage.py collectstatic --noinput && python manage.py migrate`
- Root cause of previous 500: `CompressedManifestStaticFilesStorage` raises `ValueError` if `{% static %}` references a file not in its manifest
- Procfile deleted — was stale, Railway uses dashboard config, GitHub Actions uses `.github/` workflows

### Profile Picture Form Tests (complete)
- `userProfile/tests/test_forms.py` — `UserChangeFormTests` class added (3 tests, 70 total passing)
- `SimpleUploadedFile` is in `django.core.files.uploadedfile` (not `django.test`)
- `make_image_file(self, size=None)` helper: `PIL.Image.new` → `BytesIO` → `img.save(buffer, "JPEG")` → `buffer.getvalue()` + optional null-byte padding → `SimpleUploadedFile`
- Padding valid JPEG bytes with `b"\x00" * N` works — Pillow stops at end-of-image marker, ignores trailing bytes
- `ModelForm.is_valid()` calls `validate_unique()` which hits the DB — `SimpleTestCase` forbids this; must use `TestCase`
- `MAX_PROFILE_PICTURE_SIZE = 2 * 1024 * 1024` extracted to class-level constant on `CustomUserChangeForm`
- Files must be passed as second argument to `ModelForm(data, files)` — not in `data`

### Commit Message Practice
- Imperative mood, present tense: "Add" not "Added"
- Subject line under 72 chars, blank line, then body
- Body explains WHY not WHAT
- Use heredoc for multiline `git commit -m` — cover heredoc in detail next session

---

## Session: 2026-05-23

### What We Did
Completed Cloudinary integration for production image storage. Reviewed and confirmed file size validation. Fixed default profile picture to use static fallback instead of model default.

### File Size Validation Review (complete)
- Reviewed `clean_profile_picture()` in `userProfile/forms.py` — logic was correct
- Found and fixed typo: `1025 * 1024` → `1024 * 1024` in error message f-string
  - Validation limit itself was correct; only the displayed MB value was wrong
- Covered: byte → MB math (powers of 2), why 1024 not 1000, appropriate limit (2MB) for profile pictures

### Cloudinary Integration (complete)
- Installed `cloudinary` and `django-cloudinary-storage`, added both to `requirements.txt`
- Added `cloudinary` and `cloudinary_storage` to `INSTALLED_APPS` in `settings.py`
- Updated `STORAGES['default']` backend to `cloudinary_storage.storage.MediaCloudinaryStorage`
- Added `CLOUDINARY_URL` to `.env`, GitHub Secrets (Actions), and Railway env vars
- `django-cloudinary-storage` reads `CLOUDINARY_URL` from environment automatically — no explicit `CLOUDINARY_STORAGE` dict needed
- Fixed two bugs introduced during implementation: mismatched quotes in backend string, incorrect `CLOUDINARY_STORAGE = env.str(...)` line
- Tested locally: uploaded photo appears in Cloudinary dashboard and serves via Cloudinary URL

### Default Profile Picture — Static Fallback (complete)
- Problem: model `default=` pointed to a media path, which Cloudinary doesn't have
- Fix: removed `default=` from `ImageField`, moved default image to `static/images/`, updated templates to use `{% if user.profile_picture %}` with `{% static %}` fallback
- Updated 3 template locations: navbar.html (desktop button, mobile section), user_account.html header
- Created and applied migration `0007_alter_user_profile_picture.py`
- **Why static not media**: static assets never change, no API calls, survives Cloudinary outages, version controlled in repo

### Concepts Covered
- `commit=False` is a form-layer concept (prevents DB write from `form.save()`); at the model layer, use `super().save()` to trigger the write after manipulation
- Django storage backend abstraction — swapping backends leaves models/views unchanged
- Why Railway's ephemeral filesystem makes local storage unusable for uploads
- Static files vs. media files — default images belong in static, not media

### Flagged for Later (Docket)
- Login page brute force protection: rate limiting and/or hCaptcha on signin page
- Profile picture preview on upload (Alpine.js + FileReader API, client-side)
- Image compression (Cloudinary can handle transforms on delivery — may not need server-side)

> [!todo] Next Steps (pick up here)
> 1. Style allauth email verification pages (unstyled defaults)
> 2. HTMX auth redirect middleware — `base/middleware.py`
> 3. Build Event Date section UI
> 4. Login page brute force protection (rate limiting / captcha) — docketed
> 5. Site logging and alerting (Sentry + Railway log drains) — docketed
> 6. Cover heredoc — what it is, when to use it, git commit formatting

---

## Session: 2026-05-21

### What We Did
Completed profile picture upload feature. Added alt text to profile images sitewide. Reviewed code quality and identified outstanding gaps.

### Profile Picture Upload (complete)
- `profile_picture` ImageField already on User model from previous session (migration applied)
- Added `profile_picture` to `CustomUserChangeForm` fields in `userProfile/forms.py`
- Added `FileInput` widget override (replaces default `ClearableFileInput`)
  - **Why**: `ClearableFileInput` shows file path to user (UX/privacy concern) and "clear" behavior would set field to empty without a way to reset to default
  - **Trade-off accepted**: users can only replace the picture, not clear it back to default
- Added `enctype="multipart/form-data"` to form tag in `user_account.html` — required for binary file data in POST
- Added profile picture display to account settings page header (`{% partialdef user_card inline %}`)
- Updated mobile navbar profile image from hardcoded Unsplash URL to `{{ user.profile_picture.url }}`
- Added meaningful alt text to all profile picture `<img>` tags: `{{ user.username }}'s profile picture`

### Concepts Covered
- `enctype="multipart/form-data"` vs `application/x-www-form-urlencoded` — file uploads require multipart encoding
- Form vs model as the right layer for user input validation — both are server-side, but form errors surface to the user via `form.errors`

> [!warning] Tabled / Deferred
> - **File size validation** on `profile_picture` in `CustomUserChangeForm` — should be a custom `clean_profile_picture()` method; tabled for later
> - **Tests for profile picture feature** — added to roadmap

> [!todo] Next Steps (pick up here)
> 1. Set up Cloudinary for production image storage (Railway filesystem is ephemeral — uploaded images lost on redeploy)
> 2. Add file size validation to `CustomUserChangeForm.clean_profile_picture()`
> 3. Write tests for profile picture upload (form validation, view behavior, file saved correctly)
> 4. Style allauth email verification pages (unstyled defaults)
> 5. HTMX auth redirect middleware — `base/middleware.py`
> 6. Build Event Date section UI

---

## Session: 2026-05-12 – 2026-05-18

### What We Did
Security incident response + beginning of profile picture work.

### Security Incident (complete)
- Bot attack created 1885 accounts, hit Resend free tier limit
- Fix 1: `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` + `ACCOUNT_EMAIL_REQUIRED = True` — deployed
- Fix 2: hCaptcha on signup via `django-hcaptcha` (installs as `hcaptcha` module) — deployed
- Deleted all unverified accounts via Django shell
- DMARC record confirmed in Namecheap (`v=DMARC1; p=quarantine`), SPF/DKIM verified in Resend
- Email junk folder issue: likely reputation damage from bot attack — recovers passively over time
- GitHub Actions CI: added `HCAPTCHA_SITEKEY` and `HCAPTCHA_SECRET` to workflow env and GitHub secrets

### macOS SSL Issue (local only, resolved)
`SSL: CERTIFICATE_VERIFY_FAILED` when hcaptcha tried to verify token locally. Fixed with:
```
/Applications/Python\ 3.12/Install\ Certificates.command
```
**Flagged for deeper review**: macOS Python cert store vs system cert store.

### Profile Picture Work (in progress)
- Current state: navbar hardcodes an Unsplash URL on line 34 of `templates/partials/navbar.html`
- Plan: add `ImageField` to User model, set default, update template to use `request.user.profile_picture.url`
- `MEDIA_ROOT` was incorrectly pointing to `static/images` — corrected to `BASE_DIR / 'media'`
- Field to add to User model (not done yet — waiting on default image):
  ```python
  profile_picture = models.ImageField(
      upload_to='profile_pictures/',
      default='profile_pictures/default.jpg',
      blank=True,
  )
  ```
- Default image: being created in Inkscape at 256x256px, export as PNG
- Place finished file at `media/profile_pictures/default.jpg`

### Next Steps (pick up here)
1. Finish default.jpg in Inkscape, place at `media/profile_pictures/default.jpg`
2. Add `profile_picture` ImageField to User model in `userProfile/models.py`
3. Run `makemigrations` + `migrate`
4. Update navbar template line 34 to use `request.user.profile_picture.url`
5. Test locally, then deploy
6. After profile picture: set up Cloudinary for user upload storage (production uploads can't go to local filesystem on Railway)

### Topics Flagged for Deeper Review
- hCaptcha integration — went fast. Revisit CustomSignupForm inheritance, allauth form customization, hCaptchaField internals.
- macOS SSL cert issue — why Python needs Install Certificates.command.
- Email deliverability — SPF, DKIM, DMARC: what they are and how they work.

---

## Session: 2026-05-10

### What We Did
Security incident response — bot account spam on signup endpoint. Implemented two mitigations.

### Problem
1885 accounts created by bots, hitting Resend free tier limit. Out-of-office replies confirmed real email addresses being spammed. No advertising had been done.

### Fix 1: Email Verification (deployed)
- Added `ACCOUNT_EMAIL_VERIFICATION = "mandatory"` and `ACCOUNT_EMAIL_REQUIRED = True` to settings.
- Blocks unverified accounts from logging in. Does not stop emails from being sent on signup.
- Deployed and verified working.

### Fix 2: hCaptcha on Signup (deployed)
- Package: `django-hcaptcha` — installs as module `hcaptcha` (not `django_hcaptcha`)
- Added `hcaptcha` to `INSTALLED_APPS`
- Added `HCAPTCHA_SITEKEY` and `HCAPTCHA_SECRET` to settings via `environs` env vars
- Added `hCaptchaField` to `CustomSignupForm` in `userProfile/forms.py`
- Rendered via `{{ form.captcha }}` in `templates/account/signup.html`
- No template tags needed — widget renders through the form field directly
- Keys added to `.env` locally and Railway environment variables

### macOS SSL Certificate Issue (local only)
When hcaptcha tried to verify the token, got `SSL: CERTIFICATE_VERIFY_FAILED`. Fix:
```
/Applications/Python\ 3.12/Install\ Certificates.command
```
macOS Python does not use the system certificate store — this installs the required certs.
**Flagged for deeper discussion**: Why does macOS Python need this? What is the system cert store vs Python's bundled certs? What does this command actually do?

### Still TODO
- Email deliverability: verification emails going to Gmail junk folder.
  Likely missing SPF/DKIM/DMARC DNS records for sending domain.
  **Flagged for deeper discussion**: What are SPF, DKIM, DMARC? How do you configure them? How do they affect deliverability?
- hCaptcha deep review: went fast due to time pressure. Revisit `CustomSignupForm` inheritance pattern, how allauth form customization works, and what `hCaptchaField` does under the hood.
- Style the allauth email verification pages (unstyled default templates).
- HTMX auth redirect middleware (`base/middleware.py`) — still pending from 2026-05-10.

---

## Session: 2026-05-10

### What We Did
Verified setup tasks from last session were already complete (open_date_proposals field + migration, @login_required on planView). Discussed a UX bug and the correct architectural fix.

### HTMX + login_required Bug
**Problem:** When a logged-out user clicks the HTMX-powered "View Plan" button, `@login_required` issues a 302 redirect before the view runs. HTMX follows the redirect and renders the login page HTML inside the swap target — partial login form injected into the page body.

**Wrong fix:** Handling it per-button in templates (fragile, doesn't scale).

**Correct fix:** Custom middleware in `base/middleware.py`.
- Intercept every response that is a 302 redirect
- If the request has `HX-Request` header (it's an HTMX request)
- Return a 200 response with `HX-Redirect` header pointing to the same redirect URL
- HTMX sees `HX-Redirect` and does a full client-side navigation instead of a partial swap
- Register the middleware in `MIDDLEWARE` in `settings.py`

**Not implemented yet** — left for a future session.

### Next Steps (pick up here)
1. Write `base/middleware.py` — HTMX-aware redirect middleware (see above).
2. Register it in `settings.py` MIDDLEWARE list.
3. Begin building the Event Date section UI — date voting widget and "Manage Dates" creator popup.
4. Build the propose-date view with server-side permission check.

---

## Session: 2026-05-05

### What We Did
Orientation and design discussion for the event plan page. No code written.

### Plan Page Current State
- View: `events/views.py:89` — `planView` handles both HTMX and full-page GET. Missing `@login_required`.
- Template: `events/templates/events/event_plan.html` — skeleton only, two sections with comments but no rendered content.
- Two sections roughed out: "Event Date" and "Required Items".

### Design Decisions Made

**Plan page access:**
- Requires login — `@login_required` needs to be added to `planView` (not done yet).

**Plan page layout:**
- Single page for both creator and regular users.
- Creator-specific controls surface contextually (not a separate page).

**Event Date section — conditional rendering:**
- No date locked → show date voting widget for all users + "Manage Dates" button visible to creator only (opens a popup showing vote tallies and allows creator to lock a date).
- Date locked → show confirmed date + attendance commitment UI.

**Attendance commitment:**
- Depends on a date being locked — not shown until creator locks a date.

**Required Items section:**
- Independent of date — users can commit to supplies anytime.

**Date proposal permissions:**
- `open_date_proposals = models.BooleanField(default=False)` to be added to `Plan`.
- `False` (default) = creator-only proposals. `True` = any participant can propose.
- Default is `False` (restrictive) — easier to open up later than walk back after users have submitted dates.
- Server must enforce this independently of UI — view/model method validates the requesting user is permitted to propose before accepting a submission.

### Next Steps (pick up here)
1. Add `open_date_proposals = models.BooleanField(default=False)` to `Plan` model in `events/models.py`.
2. Run `python manage.py makemigrations` and `migrate`.
3. Add `@login_required(login_url="account_login")` to `planView`.
4. Begin building the Event Date section UI — date voting widget and "Manage Dates" creator popup.
5. Build the propose-date view with server-side permission check.
