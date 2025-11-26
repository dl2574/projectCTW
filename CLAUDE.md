# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ProjectCTW (Project Change The World) is a Django 5.x web application that enables community members to propose, plan, and execute volunteer projects. Users can propose events, vote on proposals, coordinate event details, and track volunteer participation.

### Core Workflow
1. **Proposal Stage**: Users create event proposals (e.g., park cleanup, community garden)
2. **Planning Stage**: Events with sufficient upvotes move to planning where users coordinate dates, supplies, and details
3. **Scheduled/Execution**: Approved events occur and users check-in to verify attendance
4. **Completed**: Event summaries are generated and added to participants' volunteer resumes

## Tech Stack

- **Backend**: Django 5.0.6 with PostgreSQL (production) and SQLite (development)
- **Frontend**: Tailwind CSS 4.x (standalone CLI), Alpine.js, HTMX
- **Authentication**: django-allauth (email-based authentication)
- **Static Files**: WhiteNoise with compressed manifest storage
- **Testing**: Django's built-in test framework (unit tests in each app)
- **Deployment**: Railway (CI/CD via GitHub Actions on main branch)

### Critical Tailwind Note
This project uses **Tailwind 4.x** via the standalone CLI tool (NOT npm/npx). Tailwind 4.x has breaking changes from 3.x. Always reference Tailwind 4.x documentation when suggesting CSS classes.

## Development Commands

### Environment Setup
```bash
# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
# Create .env file with: SECRET_KEY, DEBUG, DATABASE_URL (optional)
```

### Running the Development Server
```bash
# Run Django development server
python manage.py runserver

# Run Tailwind in watch mode (in separate terminal)
python manage.py tailwind --watch
# Or shorthand:
python manage.py tailwind -w
```

### Database Operations
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
# Note: Requires email, username, first_name, last_name (custom User model)
```

### Testing
```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test events
python manage.py test userProfile
python manage.py test base

# Run specific test file
python manage.py test events.tests.test_models

# Run specific test class
python manage.py test events.tests.test_models.EventTests

# Run specific test method
python manage.py test events.tests.test_models.EventTests.test_event_creation
```

### Static Files & Deployment Prep
```bash
# Compile and minify Tailwind, then collect static files (for deployment)
python manage.py tailwind --deploy
# Or shorthand:
python manage.py tailwind -d

# Collect static files only
python manage.py collectstatic
```

### Custom Management Commands
```bash
# Reset SECRET_KEY in .env file
python manage.py resetsecret

# Tailwind CSS compiler
python manage.py tailwind [-w|--watch] [-d|--deploy]
```

## Architecture & Code Structure

### Django Apps

**base** - Core site functionality (home, about pages)
- Contains base templates and views
- Custom management commands (`tailwind`, `resetsecret`)

**events** - Event management system
- **Models**: `Event`, `Plan`, `ProposedDate`, `Comment`
- Event status flow: PROPOSAL → PLANNING → SCHEDULED → COMPLETED/ARCHIVED
- Events use UUID primary keys
- Voting system via ManyToMany relationship on upvotes
- Key methods: `number_of_upvotes()`, `user_upvoted()`, `set_required_num_upvotes()`

**userProfile** - Custom user model and profile management
- **Models**: `User` (extends AbstractUser)
- Uses UUID primary keys instead of integer IDs
- Email-based authentication (USERNAME_FIELD = 'email')
- Methods: `get_full_name()`, `get_short_name()`, `get_age()`
- Custom forms for django-allauth integration

**notifications** - Notification system
- **Models**: `Notification` (abstract base), `EventStatusChange`, `FriendRequest`
- Abstract base model pattern for notification inheritance

### Key Configuration Details

**Custom User Model**: `userProfile.User`
- Email is the primary authentication field
- UUID primary keys for all users
- When creating users in tests/code, always use `get_user_model()`

**Authentication**:
- django-allauth with custom forms (`CustomLoginForm`, `CustomSignupForm`)
- Password only entered once during signup
- Login redirect: "home", Logout redirect: "home"

**Static Files**:
- Source: `/static/` (CSS in `static/css/`, JS in `static/js/`)
- Collected to: `/staticfiles/` (via WhiteNoise)
- Tailwind input: `static/css/input.css`
- Tailwind output: `static/css/main.css`

**Database**:
- Development: SQLite (`db.sqlite3`)
- Production: PostgreSQL via `DATABASE_URL` environment variable
- Uses `environs` for environment configuration

### URL Structure
```
/                    - base app (home, about)
/accounts/           - django-allauth (login, signup, password reset)
/account/            - userProfile app (profile pages)
/events/             - events app (proposals, planning, details)
/admin/              - Django admin
/__reload__/         - django-browser-reload (dev only)
```

### Testing Standards
- Each app has a `tests/` directory with `test_models.py`, `test_views.py`, `test_forms.py`
- Use `setUpTestData` for test fixtures
- Always use `get_user_model()` for user creation in tests
- Test files follow Django's TestCase pattern

## CI/CD Pipeline

**Branch Strategy**:
- **development**: Active development branch
- **main**: Production branch (auto-deploys to www.projectctw.com)

**GitHub Actions Workflow** (`.github/workflows/*.yml`):
1. Runs on push/PR to main or development
2. Sets up PostgreSQL service
3. Installs dependencies
4. Runs migrations
5. Executes `python manage.py test`
6. If main branch and tests pass → Railway auto-deploys

**Deployment** (Railway):
- Uses `Procfile`: `web: python manage.py migrate && gunicorn projectCTW.wsgi --log-file -`
- Auto-migrates database on deploy
- Runs on Gunicorn WSGI server

## Security Configuration

- `SECRET_KEY`: Loaded from environment variables (never commit)
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- CSRF trusted origins: projectctw.com domains
- Email authentication only (no username/password combos)
- PostgreSQL in production, proper password validators enabled

## Common Development Patterns

### Creating a New Event Model Instance
```python
from events.models import Event
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(email="user@example.com")

event = Event.objects.create(
    name="Community Garden",
    description="Plant vegetables",
    location="Central Park",
    created_by=user,
    required_num_upvotes=5
)
event.upvotes.add(user)
```

### Working with Custom User Model
```python
from django.contrib.auth import get_user_model

User = get_user_model()

# Create user
user = User.objects.create_user(
    username="johndoe",
    email="john@example.com",
    password="securepass123",
    first_name="John",
    last_name="Doe"
)
```

### Status Progression Logic
Events follow a state machine pattern via `StatusCode` choices. When implementing status changes, ensure proper validation and notification triggers for users who upvoted or are participating.

## Environment Variables

Required in `.env` file:
- `SECRET_KEY`: Django secret key
- `DEBUG`: Boolean (True for development, False for production)
- `DATABASE_URL`: PostgreSQL connection string (optional, defaults to SQLite)

Email configuration (currently disabled in settings.py):
- `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_API_KEY`, `EMAIL_PORT`, `FROM_EMAIL`

## Notes for Future Development

- Media files stored in `static/images/` (MEDIA_ROOT)
- User model has commented-out fields for future features: experience tagging, phone, following/followers, level system
- Email backend is currently disabled but configuration exists
- Frontend uses django-crispy-forms with crispy-tailwind for form rendering
- django-browser-reload enabled for hot reloading during development
