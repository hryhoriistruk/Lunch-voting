# Contributing to Lunch Voting Service

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/Lunch-voting.git`
3. Navigate to the project: `cd Lunch-voting`
4. Create a virtual environment: `python -m venv venv`
5. Activate the virtual environment:
   - macOS/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
6. Install dependencies: `make install-dev`
7. Copy environment file: `cp .env.example .env`
8. Run migrations: `make migrate`
9. Seed database (optional): `make seed`

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting: `make format`
- Run flake8 for linting: `make lint`
- Maximum line length: 100 characters
- Maximum complexity: 10

## Pre-commit Hooks

Install pre-commit hooks to automatically check code before committing:

```bash
pre-commit install
```

Hooks will run automatically before each commit. You can also run them manually:

```bash
pre-commit run --all-files
```

## Testing

Run tests with coverage:

```bash
make test-cov
```

Coverage reports are generated in `htmlcov/`.

## Commit Messages

Follow conventional commit format:

- `feat: add new feature`
- `fix: fix bug`
- `docs: update documentation`
- `style: code style changes`
- `refactor: code refactoring`
- `test: add or update tests`
- `chore: maintenance tasks`

Example:
```
feat: add API rate limiting

Add rate limiting to prevent abuse:
- 100 requests/day for anonymous users
- 1000 requests/day for authenticated users
```

## Pull Request Process

1. Create a new branch: `git checkout -b feature/your-feature-name`
2. Make your changes
3. Run tests: `make test`
4. Run linter: `make lint`
5. Commit your changes with clear messages
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a pull request

## Project Structure

```
lunch_voting/
├── apps/
│   ├── accounts/      # User management
│   ├── core/         # Shared utilities
│   ├── menus/        # Menu management
│   ├── restaurants/  # Restaurant management
│   └── votes/        # Voting logic
├── config/           # Django settings
├── .github/          # GitHub Actions CI/CD
└── tests/            # Test files
```

## Guidelines

- Keep functions small and focused
- Write docstrings for complex functions
- Add tests for new features
- Update documentation for API changes
- Follow SOLID principles
- Use services layer for business logic

## Questions?

Feel free to open an issue for questions or discussion.
