# Lunch Voting Service

A REST API that helps employees decide where to have lunch. Restaurants
upload a menu for the day, employees vote for one, and everybody can see
the running results.

Built with **Django + Django REST Framework**, **JWT auth**, **PostgreSQL**,
**Docker/docker-compose**, and tested with **PyTest**.

## Contents

- [Features](#features)
- [Architecture](#architecture)
- [Running with Docker (recommended)](#running-with-docker-recommended)
- [Running locally without Docker](#running-locally-without-docker)
- [Authentication](#authentication)
- [API reference](#api-reference)
- [API documentation](#api-documentation)
- [Mobile app backward compatibility](#mobile-app-backward-compatibility)
- [Voting rules](#voting-rules)
- [Running tests](#running-tests)
- [Linting](#linting)
- [Security](#security)
- [Monitoring](#monitoring)

## Features

- JWT-based authentication (access + refresh tokens)
- Two roles: **Admin** (manages restaurants, menus, employee accounts) and
  **Employee** (votes for lunch)
- Restaurants publish exactly one menu per day; re-uploading a menu for a
  day that already has one safely replaces its items
- Employees vote once per day and can change their mind until a
  configurable cut-off hour
- Endpoints that support two response shapes (legacy / current) driven by
  the mobile app's build version, so users on an older app build keep
  working without a forced update
- API rate limiting to prevent abuse
- CORS support for mobile app integration
- Interactive API documentation (Swagger UI / ReDoc)
- Health check endpoint for monitoring
- Structured logging with configurable levels
- Security headers and HTTPS support for production
- **Performance optimizations**: Database indexes for frequently queried fields
- **Caching**: Menu and results caching to reduce database load
- **Enhanced validation**: Deadline validation for voting, role-based access control

## Architecture

The project favors small, single-responsibility modules over large files,
so any endpoint can be understood by reading two or three short files:

```
config/                  Django project settings, root URL config
apps/
  core/                  Cross-cutting concerns shared by every app
    versioning.py        Reads the mobile app's build version header
    permissions.py        IsAdmin / IsEmployee role checks
    pagination.py         Default list pagination
    exceptions.py          Uniform error response shape
  accounts/              Custom User model (role: ADMIN/EMPLOYEE), employee creation
  restaurants/           Restaurant CRUD
  menus/                 Daily menus + menu items, "today's menu" endpoint
  votes/                 Voting business rules + results aggregation
```

Within each domain app, responsibilities are split the same way:

- `models.py` - persistence and DB-level constraints (e.g. "one menu per
  restaurant per day" is a real unique constraint, not just app logic)
- `serializers.py` - request/response shape and field-level validation
- `services.py` - business rules that don't belong in a view or a
  serializer (e.g. the vote-deadline rule, results aggregation)
- `views.py` - thin: parses the request, calls a service or the ORM,
  returns a response
- `tests/` - one test module per concern

This keeps each file short and makes the "why" (business rule) easy to find
separately from the "how" (HTTP plumbing).

## Running with Docker (recommended)

Requirements: Docker and Docker Compose.

```bash
cp .env.example .env
docker-compose up --build
```

This starts PostgreSQL and the Django app, waits for the database to be
ready, runs migrations automatically (see `entrypoint.sh`), and serves the
API at `http://localhost:8000`.

Create an admin user (needed to create restaurants/menus/employees):

```bash
docker-compose exec web python manage.py createsuperuser
```

## Running locally without Docker

Requirements: Python 3.12+, a running PostgreSQL instance.

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

cp .env.example .env
# edit .env if your local Postgres isn't on localhost/5432 with those credentials

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Authentication

All endpoints except token creation require a JWT access token in the
`Authorization` header.

```bash
# Obtain a token pair
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'

# -> {"access": "...", "refresh": "..."}

# Use the access token
curl http://localhost:8000/api/v1/restaurants/ \
  -H "Authorization: Bearer <access-token>"

# Refresh an expired access token
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh-token>"}'
```

## API reference

| Method | Endpoint                                   | Role     | Description                                  |
|--------|---------------------------------------------|----------|-----------------------------------------------|
| POST   | `/api/v1/auth/token/`                       | -        | Obtain JWT access + refresh tokens            |
| POST   | `/api/v1/auth/token/refresh/`               | -        | Refresh an access token                       |
| POST   | `/api/v1/employees/`                        | Admin    | Create a new employee account                 |
| GET    | `/api/v1/employees/`                        | Admin    | List employees                                |
| POST   | `/api/v1/restaurants/`                      | Admin    | Create a restaurant                           |
| GET    | `/api/v1/restaurants/`                      | Any user | List restaurants                              |
| GET/PUT/DELETE | `/api/v1/restaurants/<id>/`           | Admin (write) / Any (read) | Manage a single restaurant  |
| POST   | `/api/v1/restaurants/<id>/menus/`            | Admin    | Upload (or replace) the menu for a given day  |
| GET    | `/api/v1/menus/today/`                      | Any user | Get every restaurant's menu for today         |
| POST   | `/api/v1/votes/`                            | Employee | Vote for a menu (today only)                  |
| GET    | `/api/v1/votes/results/today/`              | Any user | Get today's voting results                    |

### Example: create a restaurant (admin)

```bash
curl -X POST http://localhost:8000/api/v1/restaurants/ \
  -H "Authorization: Bearer <admin-access-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Sunny Kitchen", "address": "1 Main St"}'
```

### Example: upload today's menu (admin)

```bash
curl -X POST http://localhost:8000/api/v1/restaurants/1/menus/ \
  -H "Authorization: Bearer <admin-access-token>" \
  -H "Content-Type: application/json" \
  -d '{
        "date": "2026-08-28",
        "items": [
          {"name": "Tomato soup", "price": "3.00"},
          {"name": "Grilled chicken", "price": "7.90"}
        ]
      }'
```

### Example: create an employee (admin)

```bash
curl -X POST http://localhost:8000/api/v1/employees/ \
  -H "Authorization: Bearer <admin-access-token>" \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "email": "alice@example.com", "password": "a-strong-password"}'
```

### Example: get today's menu (employee)

```bash
curl http://localhost:8000/api/v1/menus/today/ \
  -H "Authorization: Bearer <employee-access-token>" \
  -H "X-App-Version: 2.1.0"
```

### Example: vote (employee)

```bash
curl -X POST http://localhost:8000/api/v1/votes/ \
  -H "Authorization: Bearer <employee-access-token>" \
  -H "Content-Type: application/json" \
  -d '{"menu_id": 1}'
```

### Example: today's results

```bash
curl http://localhost:8000/api/v1/votes/results/today/ \
  -H "Authorization: Bearer <employee-access-token>" \
  -H "X-App-Version: 2.1.0"
```

## API documentation

Interactive API documentation is available via drf-spectacular:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

These provide a browsable interface to explore all endpoints, request/response formats, and authentication requirements.

## Mobile app backward compatibility

The mobile app always sends its build number in the `X-App-Version`
header. The backend compares it against `APP_VERSION_BREAKPOINT`
(configurable via env, default `2.0.0`) and serves one of two response
shapes on two endpoints:

- `GET /api/menus/today/`
- `GET /api/votes/results/today/`

**Legacy clients** (`X-App-Version` below the breakpoint, or missing
entirely - treated as legacy since an un-updated app never learned to send
the header) receive a flat structure, e.g. for the menu endpoint:

```json
[
  {"menu_item_id": 1, "dish": "Tomato soup", "price": "3.00",
   "restaurant_id": 1, "restaurant": "Sunny Kitchen"}
]
```

**Current clients** (`X-App-Version` at or above the breakpoint) receive
menus grouped by restaurant:

```json
[
  {"id": 1, "date": "2026-08-28", "restaurant_id": 1,
   "restaurant_name": "Sunny Kitchen",
   "items": [{"id": 1, "name": "Tomato soup", "price": "3.00"}]}
]
```

All the branching lives in `apps/core/versioning.py` (which decides
"legacy or not") and in each endpoint's `views.py` (which picks the
matching serializer) - no version-string comparisons scattered around the
codebase.

## Voting rules

- An employee can only vote for a menu published **today**.
- An employee can change their vote the same day, but only **before**
  `VOTE_DEADLINE_HOUR` (default `11`, i.e. 11:00 server local time,
  configurable via the `.env` file). After the deadline, the vote is
  locked for the day.
- Results include every restaurant that published a menu today, even ones
  with zero votes so far.

## Running tests

Tests run against a real PostgreSQL database (matching production), using
`pytest-django`.

```bash
# with Docker
docker-compose exec web pytest

# locally
pytest

# with coverage report
pytest --cov=apps --cov-report=html
```

The suite covers, among other things:

- JWT login success/failure and that endpoints require authentication
- Role enforcement (admin-only vs employee-only endpoints)
- Menu upload, including that a same-day re-upload replaces items instead
  of creating a duplicate menu
- The legacy vs. current response shape for both versioned endpoints
- Vote casting, the "today's menu only" rule, and the deadline rule for
  changing a vote
- Results aggregation and ordering

### Test Coverage

The project uses `coverage.py` to measure test coverage. Coverage reports are
generated in both terminal and HTML format. To view the HTML report:

```bash
pytest --cov=apps --cov-report=html
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

## Linting

```bash
flake8 .
```

Configuration lives in `.flake8` (100-char line length, migrations excluded).

## Pre-commit Hooks

The project includes pre-commit hooks for code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

Hooks include:
- Black code formatter
- Flake8 linter
- Trailing whitespace removal
- YAML validation
- Large file detection

## Makefile

A Makefile is provided for common development tasks:

```bash
make help           # Show all available commands
make install        # Install production dependencies
make install-dev    # Install development dependencies
make run            # Run development server
make migrate        # Run database migrations
makeseed           # Seed database with sample data
make test           # Run tests
make test-cov       # Run tests with coverage
make lint           # Run flake8
make clean          # Clean up cache files
make docker-build   # Build Docker containers
make docker-up      # Start Docker containers
make docker-down    # Stop Docker containers
make docker-test    # Run tests in Docker
```

## CI/CD

The project includes a GitHub Actions workflow that automatically runs tests and
linting on every push and pull request to the `main` and `develop` branches.

The CI pipeline:
- Sets up Python 3.12 environment
- Installs dependencies
- Runs flake8 for code quality checks
- Executes tests with PostgreSQL service
- Generates coverage reports
- Uploads coverage reports as artifacts

### Docker Compose for Testing

A separate `docker-compose.test.yml` is provided for running tests in isolation:

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

This uses a separate test database and automatically generates coverage reports.

## Seed Data

For demo or testing purposes, you can seed the database with sample data:

```bash
python manage.py seed_data
```

This creates:
- 1 admin user (username: `admin`, password: `admin123`)
- 3 employee users (alice, bob, charlie with password `username123`)
- 3 restaurants (Sunny Kitchen, Green Bowl, Pasta House)
- Today's menus with sample items for each restaurant

## Security

The application includes several security features:

- **JWT Authentication**: Access tokens expire after 30 minutes, refresh tokens after 7 days
- **Rate Limiting**: 100 requests/day for anonymous users, 1000 requests/day for authenticated users
- **CORS**: Configurable allowed origins for mobile app integration
- **Security Headers**: Content-Type nosniff, XSS filter, X-Frame-Options DENY
- **HTTPS Support**: Configurable SSL redirect, HSTS, and secure cookies for production

For production deployment, set the following environment variables:

```bash
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Monitoring

### Health Check

A health check endpoint is available at `/health/` for monitoring systems and load balancers:

```bash
curl http://localhost:8000/health/
```

Returns:
- `200 OK` with `{"status": "healthy", "checks": {"database": "ok"}}` when healthy
- `503 Service Unavailable` with error details when unhealthy

### Logging

Structured logging is configured with the following levels (configurable via environment):

- `LOG_LEVEL`: Root logger level (default: INFO)
- `DJANGO_LOG_LEVEL`: Django-specific logging (default: INFO)
- `DB_LOG_LEVEL`: Database query logging (default: WARNING)

Logs include timestamp, log level, module, process/thread ID, and message for debugging and monitoring.
