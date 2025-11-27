# Session Details - 2025-11-26 (Evening)

## Session Summary
This session focused on transitioning to a mentorship model for development, planning the Event Planning Features implementation, and establishing the Fat Models, Thin Views design pattern for the project.

---

## Work Completed

### 1. Development Approach Change
**New Methodology**: David will write code, Claude will mentor and review

**Role Transition**:
- ✅ Claude shifts from writing code to mentoring/guiding
- ✅ David implements features to learn by doing
- ✅ Claude provides roadmaps, checklists, and guiding questions
- ✅ Claude reviews code like senior developer reviewing junior's work
- ✅ Focus on helping David understand *why* certain approaches work better

### 2. IDE Transition Noted
**Environment Change**:
- David switched from VS Code to Neovim (LazyVim config)
- Still learning Neovim - may ask for IDE-specific help
- Claude ready to assist with Neovim/LazyVim questions

### 3. Repository Made Public
**Milestone**: ProjectCTW repository is now public on GitHub
- All open source documentation from previous session is live
- Project ready for community discovery and contributions
- Next steps: Share on civic tech communities, Django forums, etc.

### 4. Event Planning Features - Comprehensive Planning
**Files Created**:
- `.claude/prompts/EVENT_PLANNING_ROADMAP.md` - Detailed 10-phase implementation guide
- `.claude/prompts/FAT_MODELS_GUIDE.md` - Design pattern guide with specific examples

**EVENT_PLANNING_ROADMAP.md Contents**:
- **Overview**: Complete planning workflow (PROPOSAL → PLANNING → SCHEDULED)
- **Database Models**:
  - ✅ Existing: Event, Plan, ProposedDate, Comment
  - 🔨 New to create: SupplyItem, SupplyCommitment, AttendanceCommitment
  - 🔄 Potential modifications: Event (selected_date field), Plan (min/max volunteers)
- **10 Implementation Phases**:
  1. Database Setup (create models, migrations, test in shell)
  2. Auto-Create Plan on Status Change (PROPOSAL → PLANNING transition)
  3. Planning Interface - Date Voting (propose, vote, confirm winning date)
  4. Planning Interface - Supply List (add items, commit to bringing supplies)
  5. Planning Interface - Attendance Commitments (Yes/Maybe/No status)
  6. Status Transition (PLANNING → SCHEDULED when date confirmed)
  7. Permissions & Access Control (who can participate in planning)
  8. Event Detail Page Integration (conditional UI based on status)
  9. Notifications (notify upvoters when status changes)
  10. Testing Strategy (model tests, view tests, integration tests)
- **Design Questions**: Key decisions David needs to make about business rules
- **Success Criteria**: Clear checklist of what "done" looks like
- **Potential Pitfalls**: Common issues to watch out for

**FAT_MODELS_GUIDE.md Contents**:
- **Design Pattern**: Fat Models, Thin Views methodology explained
- **Philosophy**: Business logic in models, views for orchestration only
- **Anti-Pattern vs Good Pattern**: Side-by-side comparison with code examples
- **Complete Model Method Examples**:
  - Event: permission checks, state transitions, calculations, notifications
  - ProposedDate: voting logic, validation, creation with business rules
  - SupplyItem: fulfillment tracking, quantity calculations
  - SupplyCommitment: automatic quantity updates on save/delete
  - AttendanceCommitment: status management
- **Thin View Examples**: All views simplified to ~10-15 lines
- **Custom Manager Example**: Efficient query patterns
- **Code Review Checklist**: What Claude will check during reviews
- **Decision Guide**: "Should this go in model or view?"

### 5. Design Pattern Agreement
**Fat Models, Thin Views Commitment**:
- ✅ Business logic belongs in models
- ✅ Views should orchestrate, not implement logic
- ✅ Model methods return `(success: bool, error: str or None)` tuples
- ✅ All business logic should be testable without HTTP
- ✅ Claude will enforce this pattern during code reviews

**Benefits**:
- Easier testing (test business logic without HTTP)
- Reusability (use methods in shell, management commands, other views)
- Maintainability (logic in one place, not scattered)
- Readability (views tell the story clearly)
- DRY (Don't Repeat Yourself)

---

## Key Decisions Made

### Event Planning Architecture
1. **Upvote Threshold**: Event creator sets `required_num_upvotes` when creating proposal
2. **Planning Interface**: Same event details page, planning features show when status == PLANNING
3. **Date Voting**: Users vote for multiple acceptable dates, creator confirms winning date
4. **Supply System**: Open contribution, quantity tracking, users commit to bringing items
5. **Attendance**: Three-tier system (Yes/Maybe/No), separate from upvotes
6. **Transitions**:
   - Auto PROPOSAL → PLANNING when threshold reached
   - Manual PLANNING → SCHEDULED when creator confirms date

### Development Methodology
1. **Learning by Doing**: David implements features himself
2. **Mentorship Model**: Claude guides, reviews, explains
3. **Fat Models Pattern**: Business logic in models, thin views for orchestration
4. **Test-Driven**: Write tests for all new functionality with explanations

---

## Files Created This Session

1. `.claude/prompts/EVENT_PLANNING_ROADMAP.md` - 10-phase implementation guide
2. `.claude/prompts/FAT_MODELS_GUIDE.md` - Design pattern with code examples

**Status**: Not yet staged or committed (to be staged at session end)

---

## Next Session Tasks

### Immediate Priority: Event Planning Features Implementation

**Phase 1 - Database Setup** (David will implement):
- [ ] Create SupplyItem model with business logic methods
- [ ] Create SupplyCommitment model with auto-update on save/delete
- [ ] Create AttendanceCommitment model with status management
- [ ] Decide: Event.selected_date field vs ProposedDate.is_selected
- [ ] Decide: Plan.volunteers relationship to AttendanceCommitment
- [ ] Create migrations and apply
- [ ] Test models in Django shell
- [ ] Register new models in admin.py

**After Phase 1**:
- David will submit code for review
- Claude will review following Fat Models, Thin Views principles
- Together write tests for the new models
- Proceed to Phase 2 (Auto-Create Plan on Status Change)

**Development Workflow**:
1. David implements a phase following roadmap
2. David submits code with: "I implemented Phase X, here's what I changed"
3. Claude reviews code, suggests improvements with explanations
4. Together write tests for new functionality
5. Move to next phase

---

## Important Notes for Future Sessions

### Development Approach
- **David writes code** - learning by doing
- **Claude mentors** - guides, reviews, explains design decisions
- **Fat Models, Thin Views** - enforce this pattern consistently
- **Test as you go** - write tests for each phase

### Technical Context
- Repository is now public on GitHub
- All security hardening from previous session is complete
- Django 5.2.8, Python 3.x, Tailwind 4.x (standalone CLI)
- Current test coverage: 22 tests, targeting 80%+

### IDE Context
- David using Neovim with LazyVim config
- Still learning Neovim - may need IDE help
- Can assist with file navigation, search/replace, Git operations, etc.

### Phase 1 MVP Focus
Event Planning Features is first priority:
- Date proposal and voting system
- Supply list with commitment tracking
- Attendance commitment system (Yes/Maybe/No)
- Proper state transitions (PROPOSAL → PLANNING → SCHEDULED)

### Code Review Focus
When David submits code, check:
- Is business logic in models, not views?
- Are views thin and focused on orchestration?
- Do model methods return useful tuples?
- Are permission checks in model methods?
- Can the logic be tested without HTTP?
- Are there proper docstrings?
- Edge cases handled?

---

## Session Context (Unchanged)

- David building ProjectCTW as learning experience
- Focus on security best practices
- Write tests for all new functionality (explain as you write)
- Help with code comments and documentation
- Explain design decisions (David learning design principles)
- Ask clarifying questions when intent unclear
- Goal: Launch Colorado Springs pilot, expand globally
- Future: Open source (NOW PUBLIC!) + non-profit organization

---

---

# Session Details - 2025-11-26 (Afternoon)

## Session Summary
This session focused on completing open source preparation tasks, conducting a comprehensive security audit, implementing critical security improvements, and preparing the project for public release.

---

## Work Completed

### 1. Open Source Documentation (Completed)
**Files Created/Modified**:
- `/home/david/Programming/dl2574/projectCTW/CODE_OF_CONDUCT.md` - Created (Contributor Covenant 2.1)
- `/home/david/Programming/dl2574/projectCTW/CONTRIBUTING.md` - Created (comprehensive contribution guide)
- `/home/david/Programming/dl2574/projectCTW/README.md` - Enhanced with professional structure
- `/home/david/Programming/dl2574/projectCTW/LICENSE` - Added AGPL-3.0 license

**Details**:
- Added Contributor Covenant 2.1 as Code of Conduct
- Created detailed contributing guidelines including setup, workflow, testing, and PR process
- Completely rewrote README with project overview, features, tech stack, installation guide, and development commands
- Updated all contact information (info@projectctw.com, github.com/dl2574)
- Added AGPL-3.0 license to protect open source mission

### 2. Security Audit & Hardening (Completed)
**Comprehensive security review conducted across 7 areas**:

**Critical Security Fixes (5)**:
1. ✅ **HTTPS Redirect** - Enabled `SECURE_SSL_REDIRECT` for production (settings.py:178-179)
2. ✅ **HTMX CSRF Protection** - Verified already configured via `hx-headers` in base.html:16
3. ✅ **Security Headers** - Added HSTS (1-year), X-Frame-Options (DENY), Content-Type-NoSniff, XSS-Filter
4. ✅ **ALLOWED_HOSTS** - Fixed dev/prod separation, removed https:// prefix, added both www/non-www domains
5. ✅ **Event Status Bug** - Added missing `event.save()` in upvoteEvent (events/views.py:102)

**Medium Priority Fixes (2)**:
6. ✅ **Comment Validation** - Replaced direct POST access with Django form validation (events/views.py:65-79)
7. ✅ **Allauth Deprecations** - Updated to new configuration format (ACCOUNT_LOGIN_METHODS, ACCOUNT_SIGNUP_FIELDS)

**Files Modified**:
- `projectCTW/settings.py` - Security headers, HTTPS redirect, ALLOWED_HOSTS, allauth config
- `events/views.py` - Comment validation, event save bug fix
- `requirements.txt` - Django upgrade 5.0.6 → 5.2.8
- `.github/workflows/ci.yml` - Added DEBUG=True to fix test failures caused by HTTPS redirect

**Security Audit Results**:
- ✅ No hardcoded secrets found
- ✅ No secrets in git history
- ✅ .env properly gitignored
- ✅ No raw SQL queries (Django ORM throughout)
- ✅ CSRF protection on all forms and AJAX
- ✅ Authentication checks on sensitive views
- ✅ All tests passing (22/22, 0 warnings)

### 3. Infrastructure & Testing
**CI/CD Fix**:
- Fixed GitHub Actions test failures caused by HTTPS redirect
- Added `DEBUG: 'True'` to CI environment variables
- Ensures tests run in debug mode while production uses secure settings

**Test Results**:
- All 22 tests passing
- Zero deprecation warnings (fixed django-allauth config)
- Verified security fixes don't break functionality

### 4. Commits Made This Session
1. `a674321` - Add open source documentation for public release preparation
2. `e07c8ce` - Implement comprehensive security improvements and Django upgrade
3. `811d1b9` - Fix GitHub Actions test failures caused by HTTPS redirect
4. (Final) - Add AGPL-3.0 license

---

## Security Posture: Production-Ready ✅

**Current Security Features**:
- ✅ HTTPS enforcement with HSTS (1-year, subdomains, preload)
- ✅ Comprehensive security headers (clickjacking, XSS, MIME-sniffing protection)
- ✅ CSRF protection on all forms and HTMX requests
- ✅ Proper input validation using Django forms
- ✅ Host header attack protection (ALLOWED_HOSTS)
- ✅ Session cookies secured (HTTPS only)
- ✅ No hardcoded secrets, clean git history
- ✅ Proper environment separation (dev vs prod)

**Remaining Optional Improvements (Low Priority)**:
- Rate limiting (prevent brute force, spam)
- Content Security Policy headers
- Security event logging
- Automated dependency scanning

---

## Open Source Release Status

**✅ Ready for Public Release**

All critical requirements met:
- ✅ LICENSE file (AGPL-3.0)
- ✅ README.md (comprehensive)
- ✅ CONTRIBUTING.md (detailed guidelines)
- ✅ CODE_OF_CONDUCT.md (Contributor Covenant)
- ✅ Security hardening complete
- ✅ All tests passing
- ✅ No secrets exposed

**To Make Repository Public**:
1. Go to GitHub repository settings
2. Scroll to "Danger Zone"
3. Click "Change visibility" → "Make public"
4. Confirm

**Post-Launch Actions**:
- Share on civic tech communities
- Post on Django forums
- Add repository topics/tags
- Enable GitHub Discussions (optional)

---

## Next Session Priorities

**Phase 1 MVP Development** - User chose to continue with core features:

**High Priority (Not Started)**:
1. **Event Planning Features**:
   - Date proposal system (propose, vote, select winning date)
   - Supply list functionality (add items, mark fulfilled, track contributors)
   - Volunteer commitment system (commit to attend, show count, reminders)
   - Planning → Scheduled status transition

2. **Event Check-in System**:
   - QR code generation for events
   - QR code scanning for attendance
   - Basic geofencing for location verification
   - Manual check-in option for organizers
   - Event completion workflow

3. **User Profile Enhancements**:
   - Profile photo upload and management
   - Display created/upvoted/attended events
   - Basic volunteer statistics
   - Edit profile functionality

4. **Testing Expansion**:
   - Increase test coverage to 80%+ (currently: basic coverage)
   - Integration tests for complete workflows
   - Test all event status transitions

**Current Test Coverage**: 22 tests, basic model/view coverage
**Target Test Coverage**: 80%+ with integration tests

---

## Important Notes for Future Sessions

1. **Security**: Production-ready, all critical issues addressed
2. **Open Source**: Ready to make repository public
3. **Phase 1 MVP**: Event planning, check-in, and profiles are next priorities
4. **Testing**: Need significant expansion with guidance
5. **Django Version**: Now on 5.2.8 (upgraded from 5.0.6)
6. **CI/CD**: GitHub Actions working correctly with security settings

---

## Session Context (Unchanged)

- David is building ProjectCTW as a learning experience
- Focus on security best practices
- Write tests for all new functionality (explain as you write)
- Help with code comments and documentation
- Explain design decisions (David learning design principles)
- Ask clarifying questions when intent unclear
- Goal: Launch Colorado Springs pilot, then expand globally
- Future: Open source + non-profit organization

---
---

# Session Details - 2025-11-24

## Session Summary
This session focused on analyzing the ProjectCTW codebase, creating comprehensive documentation, developing a detailed roadmap, and discussing open source and non-profit strategies.

---

## Work Completed

### 1. Created CLAUDE.md
**File**: `/home/david/Programming/dl2574/projectCTW/CLAUDE.md`

Created a comprehensive guidance document for future Claude Code instances including:
- Project overview and core workflow explanation
- Complete tech stack details (Django 5.x, Tailwind 4.x, Alpine.js, HTMX)
- **Critical note**: Project uses Tailwind 4.x standalone CLI (NOT npm/npx) - breaking changes from 3.x
- All development commands (runserver, migrations, testing, static files)
- Custom management commands (`python manage.py tailwind -w`, `python manage.py tailwind -d`)
- Detailed architecture breakdown of all Django apps:
  - **base**: Core site functionality, custom management commands
  - **events**: Event management (Event, Plan, ProposedDate, Comment models)
  - **userProfile**: Custom User model with UUID primary keys, email-based auth
  - **notifications**: Notification system with abstract base model
- Testing standards and patterns
- CI/CD pipeline details (GitHub Actions � Railway deployment)
- Security configuration
- Common development patterns and code examples
- Environment variables reference

### 2. Created DEVELOPMENT_ROADMAP.md
**File**: `/home/david/Programming/dl2574/projectCTW/.claude/prompts/DEVELOPMENT_ROADMAP.md`

Developed a comprehensive 7-phase development roadmap with checkbox tracking:

**Phase 1: MVP - Core Event Workflow** (Current Priority)
- Complete event proposal, upvoting, and planning systems
- Build check-in and attendance verification with geofencing
- Implement basic user profiles with photo upload
- Expand test coverage significantly (target: 80%+)
- Location enhancements (physical/online/hybrid toggle)

**Phase 2: User Experience & Engagement**
- User leveling and points system (tied to moderation permissions)
- Event tagging system (activity type, target audience, impact area)
- Geographic filtering (user-configurable radius: 5-100+ miles)
- In-app notification system with preferences
- Volunteer resume generation and PDF export

**Phase 3: Moderation & Community Safety**
- Moderator tools and dashboard (remove events, ban users, edit content)
- User reporting system with categories
- Audit logging for all moderation actions
- Community guidelines enforcement

**Phase 4: Sponsor System**
- Sponsor account type with verification workflow
- Auto-approve with limits, manual verification for larger commitments
- Sponsorship offer system (sponsors create standing offers)
- Resource matching between sponsors and event supply lists
- Sponsor recognition and impact tracking

**Phase 5: Integrations & Infrastructure**
- Email notifications (SendGrid/Mailgun/AWS SES)
- Image storage & CDN (S3/Cloudinary)
- Background task queue (Celery + Redis)
- Payment processing (Stripe for sponsor donations)
- Geolocation services (geofencing for check-in, distance calculations)
- Calendar integration (iCal export, "Add to Calendar")
- SMS notifications (Twilio) for critical updates

**Phase 6: Analytics & Impact Tracking**
- Personal analytics dashboard (hours, impact score, streaks)
- Event organizer dashboard with post-event reporting
- Public impact dashboard (total events, volunteers, hours, geographic distribution)
- Analytics integration (Plausible/Google Analytics)
- Social sharing with Open Graph meta tags
- Interactive map view of events

**Phase 7: Privacy, Compliance & Polish**
- Privacy controls (private by default, granular sharing options)
- GDPR compliance with data export functionality
- Security hardening and OWASP review
- Performance optimization (caching, query optimization)
- Accessibility (WCAG 2.1 AA compliance)
- Database review and optimization

**Additional Sections:**
- Technical debt and ongoing maintenance checklist
- Launch strategy for Colorado Springs pilot
- Future considerations (mobile app, API, internationalization)

---

## Strategic Decisions Discussed

### Non-Profit Formation Strategy

**Recommendation**: Launch first, formalize later

**Timeline:**
1. **Now - 6 months**: Personal project, MVP development
2. **6-12 months**: Colorado Springs pilot, gather impact data
3. **12-18 months**: Form non-profit with demonstrated impact
4. **18+ months**: Apply for 501(c)(3) tax-exempt status

**Pre-Non-Profit Steps:**
- Keep detailed development records (for in-kind donation valuation)
- Track community impact metrics
- Build relationships with potential board members
- Research fiscal sponsorship options
- Document all expenses

**Benefits for ProjectCTW:**
- Tax-deductible donations from sponsors
- Grant eligibility from foundations
- Increased credibility and trust
- Volunteer liability protection
- Mission-lock prevents commercial exploitation

### Open Source Strategy

**Recommendation**: YES - Go open source soon (after basic security cleanup)

**Why Open Source Makes Sense:**
- Mission alignment with community empowerment values
- Transparency builds trust for civic platform
- Accelerates development through community contributions
- Attracts civic-tech enthusiasts and volunteers
- Strengthens non-profit applications
- Other cities can deploy their own instances
- Reduces vendor lock-in concerns

**Recommended License: GNU AGPL-3.0**
- Copyleft ensures derivatives remain open source
- Network use protection (modified SaaS versions must share source)
- Prevents commercial exploitation without contribution
- Protects community-focused mission
- Compatible with non-profit goals

**Alternative Considered**: MIT License (more permissive, simpler, but allows commercialization)

**Protection Strategy:**
- Trademark "ProjectCTW" / "Project Change The World" (~$250-500)
- Open source code, but protect brand/name
- Prevents confusing forks or commercial impersonators

**Governance Model:**
- **Initially**: Benevolent Dictator (David maintains final authority)
- **After Non-Profit**: Board governance + Technical Steering Committee
- **Long-term**: Community-driven with RFC process

**Sustainability Model (Compatible with Non-Profit):**
1. Grants and foundations (Knight Foundation, Mozilla, Code for America)
2. Sponsored features (sponsors fund development, get credit)
3. Hosted service ("ProjectCTW Cloud" for cities/organizations)
4. Support contracts (priority support, implementation assistance)
5. Donations (individual, GitHub Sponsors, corporate)

### Open Source Action Plan

**Immediate (Next 1-2 Months):**
- [ ] Continue MVP development (Phase 1)
- [ ] Security cleanup (fix obvious vulnerabilities)
- [ ] Documentation (README, CONTRIBUTING.md, CODE_OF_CONDUCT.md)
- [ ] Choose license (AGPL-3.0 recommended)
- [ ] Repository setup (clean history, remove sensitive data)

**Short-term (2-4 Months):**
- [ ] Make repository public
- [ ] Community outreach (civic tech communities, Django forums)
- [ ] Colorado Springs pilot launch
- [ ] Accept first contributors

**Medium-term (6-12 Months):**
- [ ] Fiscal sponsorship partnership
- [ ] Apply for grants
- [ ] Build potential board
- [ ] Community growth

**Long-term (12-18 Months):**
- [ ] Form 501(c)(3) non-profit
- [ ] Transfer IP to non-profit
- [ ] Establish formal governance
- [ ] Multiple revenue streams active

---

## Feature Completeness Status

Based on discussion with David:

| Feature | Status |
|---------|--------|
| Event proposals and upvoting | Partially implemented |
| Event planning (date voting, supply lists) | Initiated, needs significant work |
| Sponsor accounts | Not started |
| Event check-in system | Not started |
| Volunteer resume/event history | Not started |
| User profiles | Initiated, needs significant work |

**Frontend State:**
- Mostly functional with established theme
- Some sections have dummy data (e.g., user profile photo is stock image, cannot be changed)
- Mobile responsiveness is a priority
- No specific mobile app planned currently

**Notifications:**
- Both in-app and email notifications required
- Email backend currently disabled in settings
- Notification models exist but need expansion

**Testing:**
- David has limited testing experience and needs guidance
- Current test coverage inadequate
- Should aim for 80%+ coverage on critical paths
- Tests needed for models, views, forms, and complete workflows

---

## Key Requirements & Decisions

### Event Features

**Location Handling:**
- Events need physical/online/hybrid options (not yet implemented)
- Geographic filtering: user-configurable radius (5, 10, 25, 50, 100+ miles)
- Events filtered by region, adjustable by user
- Future: geofencing for event attendance verification

**Event Tags:**
- Multiple tags per event
- Tag types envisioned: activity type (Gardening, Carpentry, Plumbing, Electrical, Cleanup, Education)
- May expand to include target audience, impact area
- Open to exploring this functionality further

**Event Workflow (Critical for MVP):**
1. Proposal � Upvotes � Planning � Scheduled � Execution � Completed
2. Check-in system with QR codes and geofencing
3. Attendance verification
4. Event completion summary

### User System

**User Leveling System:**
- All commented-out User model features are important (experience tagging, phone, following/followers, level)
- Points earned for:
  - Creating events
  - Attending events
  - Upvoting (smaller amount)
  - Bonus for event completion
- Higher levels grant increased permissions
- Eventually become moderators at high levels
- Level progression system integrated with site permissions

**User Profiles:**
- Private by default with opt-in sharing
- Users control what information is visible
- Profile photos (currently dummy/stock image)
- Event history and volunteer resume

**Privacy:**
- Private by default, users enable what they want to share
- Data export functionality required (GDPR)
- Granular privacy settings needed

### Sponsor System

**Sponsor Account Type:**
- Created by businesses
- Cannot volunteer for events
- See events in planning stage
- View event resource requirements
- Make sponsorship offers
- Donate resources to events

**Sponsor Verification:**
- Recommendation: Auto-approve with limits initially
- Manual verification for larger commitments
- Requirements: business email, tax ID, business license
- Admin verification dashboard
- Verified badge display

**Sponsor Tiers:**
- Not fully thought through yet
- Monetary donations
- In-kind donations
- Resource offers

### Moderation System

**Moderator Capabilities:**
- Dissolve events not aligned with application spirit
- Remove events
- Review/remove comments
- Ban/suspend users who violate guidelines
- Override/edit content as needed

**Reporting & Accountability:**
- User reporting system required
- Report categories: spam, inappropriate content, harassment, misinformation, off-topic
- All moderation actions logged for accountability
- Moderators gained through user leveling system

### Integrations Required

**Confirmed integrations needed:**
- Payment processors (Stripe recommended)
- Geolocation services (for geofencing attendance, event location planning)
- Calendar exports (iCal, Google Calendar, Apple Calendar, Outlook)
- Email service provider (SendGrid, Mailgun, AWS SES)
- Image storage/CDN (S3, Cloudinary)
- Background task queue (Celery/Redis)
- SMS notifications (Twilio)
- Analytics (Plausible or Google Analytics)
- Social sharing (Open Graph)
- Mapping/visualization (for event discovery)

### Analytics & Reporting

**Personal Metrics:**
- Volunteer hours
- Events attended
- Events created
- Impact score
- Level and progress
- Achievements

**Event Metrics:**
- Attendance count
- Resources donated
- Completion status
- Sponsor contributions

**Site-Wide Metrics:**
- Total events completed
- Total volunteers
- Total volunteer hours
- Events by category
- Geographic distribution
- Impact dashboard (public-facing)

**Post-Event Reporting:**
- Not fully thought through yet
- Should capture outcomes and impact
- Event organizer needs

---

## Technical Considerations

### Current State

**No Performance Issues Yet:**
- Very little data to test with currently
- Will need monitoring as it scales

**No Security Testing:**
- Should conduct security audit before open sourcing
- OWASP Top 10 review needed
- Rate limiting, input validation review

**Database Design:**
- David is new to database design
- Current models may need review
- Location field needs enhancement (physical/online/hybrid)
- Models generally okay but should be validated

**Development Experience:**
- No friction in local development
- Railway deployments working well
- Migrations going smoothly

### Testing Needs

**Current Gaps:**
- Limited test coverage
- David has little testing experience
- Needs guidance on testing best practices

**Testing Strategy:**
- Start with model tests (object creation, methods, relationships)
- Add view tests (permissions, templates, context, POST handling)
- Form tests (validation, custom logic)
- Integration tests for complete workflows
- Aim for 80%+ coverage on critical paths
- Use Django's TestCase with setUpTestData
- Always use get_user_model() for user creation

**Testing Support Needed:**
- Examples of good tests
- Guidance on what to test
- Help writing comprehensive test suites
- Testing as part of Phase 1 MVP

---

## Launch Strategy

### Colorado Springs Pilot

**Initial Launch:**
- Start locally in Colorado Springs, CO
- Plan for eventual global expansion
- Build locally, scale globally approach

**Pre-Launch:**
- Complete Phase 1 MVP
- Beta test with 10-20 users
- Gather feedback and iterate
- Partner with local organizations
- Seed initial events
- Create launch materials

**Launch:**
- Soft launch to Colorado Springs area
- Close monitoring
- Quick iteration on feedback
- Target: 100-500 initial users
- Establish moderation practices

**Post-Launch:**
- Expand to nearby Colorado cities
- Add Phase 2+ features
- Build case studies and success stories
- Plan national/global expansion

---

## Resources to Explore

### Open Source
- Choose a License: https://choosealicense.com/
- Open Source Guides: https://opensource.guide/
- Civic Tech Field Guide: https://civictech.guide/

### Non-Profit Formation
- Harbor Compliance (formation service)
- Foundation Center (grant research)
- National Council of Nonprofits

### Civic Tech Community
- Code for America (civic tech brigades network)
- Digital Public Goods Alliance
- Fast Forward (tech non-profit accelerator)

---

## Next Session Tasks

### Immediate Priorities (To be completed this session):
1. CONTRIBUTING.md - Draft contribution guidelines
2. CODE_OF_CONDUCT.md - Draft code of conduct
3. README.md - Review and enhance with better content
4. Stage all changes

### Future Session Priorities:
- Security review before open sourcing
- Continue Phase 1 MVP development
- Expand test coverage with guidance
- Database model review

### Phase 1 MVP Focus Areas:
- Complete event proposal system
- Finish upvoting mechanism with auto-transition
- Implement event planning (date voting, supply lists)
- Build check-in system with QR codes
- User profile enhancements (photo upload)
- Expand test coverage significantly

### Open Source Preparation:
- Security cleanup
- Remove any remaining hardcoded secrets
- Clean commit history if needed
- Set up issue templates
- Choose final license (AGPL-3.0 recommended)
- Prepare repository for public launch

---

## Important Notes for Future Sessions

1. **Tailwind 4.x**: Always reference Tailwind 4.x documentation, NOT 3.x - breaking changes
2. **Custom User Model**: Always use `get_user_model()`, email-based auth, UUID primary keys
3. **Testing**: David needs guidance and help writing comprehensive tests
4. **Security**: Conduct review before making repository public
5. **Database Models**: May need review/optimization - David is new to database design
6. **Comments**: Help David write good comments for self-documentation
7. **Design Decisions**: Explain reasoning when making design changes (David learning)
8. **Open Source Soon**: After security cleanup and documentation completion
9. **Non-Profit Later**: After 12-18 months with demonstrated impact

---

## Files Created/Modified This Session

1. `/home/david/Programming/dl2574/projectCTW/CLAUDE.md` - Created: Comprehensive codebase guidance
2. `/home/david/Programming/dl2574/projectCTW/.claude/prompts/DEVELOPMENT_ROADMAP.md` - Created: 7-phase development roadmap
3. `/home/david/Programming/dl2574/projectCTW/.claude/prompts/SESSION_DETAILS.md` - Created: This file
4. `/home/david/Programming/dl2574/projectCTW/CONTRIBUTING.md` - To be created
5. `/home/david/Programming/dl2574/projectCTW/CODE_OF_CONDUCT.md` - To be created
6. `/home/david/Programming/dl2574/projectCTW/README.md` - To be enhanced

---

## Session Context

- David is building ProjectCTW as a learning experience
- Focus on security best practices
- Write tests for all new functionality (explain as you write)
- Help with code comments and documentation
- Explain design decisions (David learning design principles)
- Ask clarifying questions when intent unclear
- Goal: Launch Colorado Springs pilot, then expand globally
- Future: Open source + non-profit organization
