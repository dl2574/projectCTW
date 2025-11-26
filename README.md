# ProjectCTW - Project Change The World

**Empowering communities to propose, plan, and execute volunteer projects together.**

[![License](https://img.shields.io/badge/license-TBD-blue.svg)](LICENSE)
[![Django](https://img.shields.io/badge/Django-5.0.6-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the Application](#running-the-application)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Running Tests](#running-tests)
  - [Common Commands](#common-commands)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

---

## About

**ProjectCTW** (Project Change The World) is a web platform that enables community members to collaboratively improve their neighborhoods through volunteer events. Users can propose project ideas, vote on proposals they support, coordinate event details, and build verified volunteer resumes.

### The Workflow

1. **Propose** - Community members propose volunteer project ideas (e.g., park cleanup, community garden, playground repair)
2. **Vote** - Users upvote proposals they want to participate in
3. **Plan** - Events with sufficient upvotes move to planning, where users coordinate dates, supplies, and logistics
4. **Execute** - Volunteers check in at events to verify attendance
5. **Complete** - Event summaries are generated and added to participants' volunteer resumes

### Vision

Starting as a pilot in Colorado Springs, CO, ProjectCTW aims to become a global platform for grassroots community improvement, eventually operating as a non-profit organization.

---

## Features

### Current Features (MVP in Progress)

- ✅ User authentication (email-based via django-allauth)
- ✅ Event proposal creation
- ✅ Event upvoting system
- ✅ Event detail pages
- ✅ Basic user profiles
- ✅ Event status progression (Proposal → Planning → Scheduled → Completed)
- 🚧 Event planning (date voting, supply lists) - *In Progress*
- 🚧 User profile enhancements - *In Progress*

### Planned Features

See our [Development Roadmap](.claude/prompts/DEVELOPMENT_ROADMAP.md) for the complete feature plan.

**Phase 1 Priorities:**
- Event check-in system with QR codes and geofencing
- Complete event planning workflow
- Profile photo upload
- Comprehensive test coverage

**Future Phases:**
- User leveling and points system
- Event tagging and geographic filtering
- Sponsor accounts for businesses to support events
- Moderation tools and community safety
- Volunteer resume generation (PDF export)
- Analytics and impact tracking
- Privacy controls and GDPR compliance

---

## Tech Stack

### Backend
- **Django 5.0.6** - Web framework
- **PostgreSQL** - Production database
- **SQLite** - Development database
- **django-allauth** - Authentication
- **WhiteNoise** - Static file serving
- **Gunicorn** - WSGI server (production)

### Frontend
- **Tailwind CSS 4.x** - Styling (via standalone CLI)
- **Alpine.js** - Lightweight JavaScript framework
- **HTMX** - Dynamic interactions

### Infrastructure
- **Railway** - Hosting and deployment
- **GitHub Actions** - CI/CD pipeline
- **Git/GitHub** - Version control

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git
- PostgreSQL (optional, for production-like setup)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/dl2574/projectCTW.git
   cd projectCTW
   ```

2. **Create and activate a virtual environment**

   ```bash
   # Linux/Mac
   python -m venv .venv
   source .venv/bin/activate

   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:

   ```env
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   DATABASE_URL=  # Optional: Leave empty to use SQLite
   ```

   To generate a secure SECRET_KEY:
   ```bash
   python manage.py resetsecret
   ```

5. **Run database migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**

   ```bash
   python manage.py createsuperuser
   ```

   You'll be prompted for:
   - Email
   - Username
   - First name
   - Last name
   - Password

### Running the Application

You'll need two terminal windows:

**Terminal 1 - Django development server:**
```bash
python manage.py runserver
```

**Terminal 2 - Tailwind CSS (watch mode):**
```bash
python manage.py tailwind -w
```

Access the application at `http://localhost:8000`

---

## Development

### Project Structure

```
projectCTW/
├── base/              # Core site functionality (home, about pages)
├── events/            # Event management (Event, Plan, ProposedDate, Comment models)
├── userProfile/       # Custom User model and profiles
├── notifications/     # Notification system
├── projectCTW/        # Django project settings
├── static/            # Static files (CSS, JS, images)
├── staticfiles/       # Collected static files (generated)
├── templates/         # HTML templates
├── .claude/           # Claude Code configuration and documentation
├── manage.py          # Django management script
└── requirements.txt   # Python dependencies
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for a specific app
python manage.py test events

# Run a specific test file
python manage.py test events.tests.test_models

# Run a specific test class
python manage.py test events.tests.test_models.EventTests
```

**Note**: We're actively expanding test coverage. Contributions of tests are highly valued!

### Common Commands

**Database:**
```bash
python manage.py makemigrations  # Create new migrations
python manage.py migrate         # Apply migrations
```

**Static Files:**
```bash
python manage.py tailwind -w     # Watch mode (development)
python manage.py tailwind -d     # Deploy mode (minified, production-ready)
python manage.py collectstatic   # Collect static files
```

**Utilities:**
```bash
python manage.py createsuperuser # Create admin user
python manage.py resetsecret     # Generate new SECRET_KEY in .env
```

### Important Notes

- **Tailwind 4.x**: This project uses Tailwind CSS 4.x via the standalone CLI (NOT npm/npx). Tailwind 4.x has breaking changes from 3.x - always reference the [Tailwind 4.x documentation](https://tailwindcss.com/docs).

- **Custom User Model**: This project uses a custom User model (`userProfile.User`) with email-based authentication and UUID primary keys. Always use `get_user_model()` instead of importing User directly.

- **Environment Variables**: Never commit `.env` files or secrets. Use environment variables for all sensitive configuration.

---

## Deployment

### CI/CD Pipeline

- **Development Branch** → Merge to `main` after testing
- **Main Branch** → Triggers GitHub Actions
- **GitHub Actions** → Runs tests
- **Railway** → Auto-deploys if tests pass

Production URL: [www.projectctw.com](https://www.projectctw.com)

### Deployment Process

1. All development happens on the `development` branch
2. Create pull requests to merge into `main`
3. GitHub Actions runs the test suite
4. If tests pass, Railway automatically deploys to production
5. Database migrations run automatically via `Procfile`

---

## Contributing

We welcome contributions! ProjectCTW is working towards becoming an open source project.

### How to Contribute

1. Read the [Contributing Guidelines](CONTRIBUTING.md)
2. Review the [Code of Conduct](CODE_OF_CONDUCT.md)
3. Check the [Development Roadmap](.claude/prompts/DEVELOPMENT_ROADMAP.md)
4. Fork the repository and create a feature branch
5. Make your changes with tests
6. Submit a pull request to the `development` branch

### Areas Where We Need Help

- Expanding test coverage (especially integration tests)
- Frontend improvements and mobile responsiveness
- Security review and hardening
- Documentation improvements
- Feature development (see roadmap)

---

## Roadmap

ProjectCTW is under active development. Our roadmap includes 7 phases:

1. **Phase 1: MVP** - Core event workflow (current focus)
2. **Phase 2: User Experience** - Leveling, tags, notifications
3. **Phase 3: Moderation** - Community safety tools
4. **Phase 4: Sponsors** - Business sponsorship system
5. **Phase 5: Integrations** - Email, payments, storage
6. **Phase 6: Analytics** - Impact tracking and reporting
7. **Phase 7: Compliance** - Privacy, GDPR, accessibility

See the complete [Development Roadmap](.claude/prompts/DEVELOPMENT_ROADMAP.md) for detailed feature lists and checkboxes.

---

## License

License to be determined. AGPL-3.0 is under consideration to ensure the project remains open source and community-focused.

---

## Contact

**Project Maintainer**: David

- GitHub: [github.com/dl2574/projectCTW](https://github.com/dl2574/projectCTW)
- Website: [www.projectctw.com](https://www.projectctw.com)
- Email: info@projectctw.com

---

## Acknowledgments

Built with:
- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Alpine.js](https://alpinejs.dev/)
- [HTMX](https://htmx.org/)
- [django-allauth](https://django-allauth.readthedocs.io/)

---

**Working towards building better communities together.**
