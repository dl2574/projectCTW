# Session Details

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
