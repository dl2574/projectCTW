# Contributing to ProjectCTW

Thank you for your interest in contributing to ProjectCTW! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Features](#suggesting-features)

## Code of Conduct

This project adheres to a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to info@projectctw.com.

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (for production) or SQLite (for development)
- Tailwind CSS 4.x standalone CLI
- Git

### Setting Up Your Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/dl2574/projectCTW.git
   cd projectCTW
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```
   Note: You'll need to provide email, username, first_name, and last_name.

7. **Run the development server**

   In one terminal:
   ```bash
   python manage.py runserver
   ```

   In another terminal (for Tailwind CSS):
   ```bash
   python manage.py tailwind -w
   ```

8. **Access the application**

   Visit `http://localhost:8000` in your browser.

## Development Workflow

### Branching Strategy

- `main`: Production branch (auto-deploys to www.projectctw.com)
- `development`: Active development branch
- Feature branches: Create from `development` with descriptive names (e.g., `feature/event-check-in`, `fix/upvote-bug`)

### Creating a Feature Branch

```bash
git checkout development
git pull origin development
git checkout -b feature/your-feature-name
```

### Keeping Your Branch Updated

```bash
git checkout development
git pull origin development
git checkout feature/your-feature-name
git merge development
```

## Coding Standards

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Write docstrings for complex functions and classes
- Keep functions focused and single-purpose

### Django Best Practices

- Use Django's built-in features when possible (don't reinvent the wheel)
- Always use `get_user_model()` instead of importing User directly
- Use class-based views where appropriate
- Follow Django's model field naming conventions
- Add `help_text` to model fields where helpful

### Frontend (Tailwind CSS)

- **Important**: This project uses **Tailwind CSS 4.x**, which has breaking changes from 3.x
- Use Tailwind utility classes; avoid custom CSS when possible
- Ensure responsive design (mobile-first approach)
- Test across different screen sizes

### Comments and Documentation

- Add comments for complex logic that isn't self-evident
- Explain "why" in comments, not just "what"
- Update documentation when changing functionality
- Keep CLAUDE.md updated with architectural changes

### Security

- Never commit sensitive data (API keys, passwords, SECRET_KEY)
- Always use environment variables for secrets
- Validate and sanitize user input
- Follow OWASP security best practices
- Be mindful of SQL injection, XSS, and CSRF vulnerabilities

## Testing Guidelines

### Writing Tests

We strive for high test coverage (target: 80%+). All new features should include tests.

**Test Organization:**
- Each Django app has a `tests/` directory
- Separate test files: `test_models.py`, `test_views.py`, `test_forms.py`
- Use descriptive test method names (e.g., `test_event_moves_to_planning_when_upvote_threshold_met`)

**Testing Best Practices:**
- Use `setUpTestData` for test fixtures
- Always use `get_user_model()` for creating test users
- Test both success and failure cases
- Test permissions and authentication
- Test form validation (valid and invalid data)
- Test model methods and properties
- Test complete workflows for critical features

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

# Run a specific test method
python manage.py test events.tests.test_models.EventTests.test_event_creation
```

### Test Coverage

We aim for 80%+ test coverage on critical paths. When adding new features:

1. Write tests for model creation and methods
2. Write tests for views (GET and POST requests)
3. Write tests for form validation
4. Write integration tests for complete workflows
5. Test edge cases and error handling

## Submitting Changes

### Before Submitting a Pull Request

1. **Run tests** - Ensure all tests pass
   ```bash
   python manage.py test
   ```

2. **Check code style** - Ensure your code follows PEP 8

3. **Update documentation** - Update relevant documentation for your changes

4. **Test manually** - Test your changes in the browser

5. **Write clear commit messages**
   - Use present tense ("Add feature" not "Added feature")
   - First line: brief summary (50 characters or less)
   - Additional details in subsequent lines if needed

   Example:
   ```
   Add event check-in functionality with QR codes

   - Implement QR code generation for events
   - Add check-in view and template
   - Include basic geofencing validation
   - Add tests for check-in workflow
   ```

### Pull Request Process

1. **Push your branch to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Target the `development` branch
   - Use a clear, descriptive title
   - Fill out the PR template (if provided)
   - Reference any related issues

3. **PR Description Should Include:**
   - What changed and why
   - How to test the changes
   - Screenshots (for UI changes)
   - Any breaking changes or migration notes

4. **Code Review**
   - Address feedback from reviewers
   - Make requested changes in new commits
   - Respond to comments and questions

5. **Merging**
   - PRs will be merged by maintainers after approval
   - Your branch will be deleted after merging

## Reporting Bugs

### Before Reporting

- Check if the bug has already been reported in [Issues](https://github.com/dl2574/projectCTW/issues)
- Try to reproduce the bug on the latest `development` branch
- Gather relevant information (browser, OS, steps to reproduce)

### Bug Report Template

When creating a bug report, include:

1. **Description**: Clear description of the bug
2. **Steps to Reproduce**: Numbered steps to reproduce the behavior
3. **Expected Behavior**: What you expected to happen
4. **Actual Behavior**: What actually happened
5. **Screenshots**: If applicable
6. **Environment**:
   - OS and version
   - Browser and version
   - Python version
   - Django version
7. **Additional Context**: Any other relevant information

## Suggesting Features

We welcome feature suggestions! Please:

1. **Check existing feature requests** to avoid duplicates
2. **Explain the use case** - Why is this feature needed?
3. **Describe the solution** - What would you like to see?
4. **Consider alternatives** - Are there other ways to solve this?
5. **Provide context** - How does this align with the project goals?

Feature requests will be reviewed and prioritized based on:
- Alignment with project vision
- Community value
- Implementation complexity
- Availability of contributors

## Development Roadmap

See [DEVELOPMENT_ROADMAP.md](.claude/prompts/DEVELOPMENT_ROADMAP.md) for the project's planned features and phases.

## Questions?

If you have questions about contributing:

1. Check the [CLAUDE.md](CLAUDE.md) file for technical details
2. Review existing [Issues and Pull Requests](https://github.com/dl2574/projectCTW)
3. Open a discussion or issue
4. Contact the maintainers at info@projectctw.com

## License

By contributing to ProjectCTW, you agree that your contributions will be licensed under the same license as the project (to be determined - AGPL-3.0 recommended).

---

**Thank you for contributing to ProjectCTW and helping build better communities together!**
