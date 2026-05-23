---
title: Session Details
tags:
  - projectctw
  - sessions
description: Chronological log of development sessions, newest first
---

# Session Details

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
> 1. Add `collectstatic` to Railway build process — it's not running automatically, causing 500 errors when new static files are added. Find where Railway build is configured (Procfile, Dockerfile, railway.toml, or nixpacks.toml) and add it.
> 2. Write tests for profile picture upload (form validation, view behavior, AccountProfileView)
> 3. Style allauth email verification pages (unstyled defaults)
> 4. HTMX auth redirect middleware — `base/middleware.py`
> 5. Build Event Date section UI
> 6. Login page brute force protection (rate limiting / captcha) — docketed

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
