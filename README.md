# EVE Healthcare — Diagnostic Booking API

Backend service for diagnostic test bookings and simulated payments, built for the EVE Healthcare SDE assignment.

## Tech Stack

- **FastAPI** — REST API with automatic OpenAPI docs
- **PostgreSQL** — primary database
- **SQLAlchemy** — ORM and schema modeling
- **JWT** — authentication
- **Docker Compose** — local development environment
- **pytest** — unit and integration tests

## Quick Start (Docker)

```bash
docker compose up --build
```

API: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

## Local Setup (without Docker)

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start PostgreSQL and create a database named `eve_diagnostics`.
4. Copy environment variables:

```bash
copy .env.example .env
```

5. Run the API:

```bash
uvicorn app.main:app --reload
```

## Run Tests

```bash
pytest -v
```

## API Endpoints

### Authentication
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | No | Register a new user |
| POST | `/auth/login` | No | Login and receive JWT |

### Diagnostic Centres
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/centres` | No | Create centre with tests |
| GET | `/centres` | No | List centres (paginated) |
| GET | `/centres/{id}` | No | Get centre details |
| POST | `/centres/{id}/tests` | No | Add test to centre |

### Bookings
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/bookings` | Yes | Create booking |
| GET | `/bookings/{id}` | Yes | Get own booking |
| POST | `/bookings/{id}/cancel` | Yes | Cancel pending booking |

### Payments
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/payments` | Yes | Simulate payment (SUCCESS/FAILED) |
| POST | `/payments/webhook` | No | Provider webhook (idempotent) |

## Example Flow

```bash
# 1. Sign up
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@example.com","full_name":"Prateek","password":"securepass123"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"patient@example.com","password":"securepass123"}'

# 3. Create centre
curl -X POST http://localhost:8000/centres \
  -H "Content-Type: application/json" \
  -d '{"name":"EVE Diagnostics","location":"Hauz Khas, Delhi","tests":[{"name":"CBC","price":"499.00"}]}'

# 4. Create booking (use token from login)
curl -X POST http://localhost:8000/bookings \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"test_id":1,"centre_id":1,"appointment_at":"2026-10-01T10:00:00Z"}'

# 5. Simulate payment
curl -X POST http://localhost:8000/payments \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"booking_id":1,"simulate_success":true}'
```

## Database Schema

```
users
  - id, email (unique), full_name, password_hash, created_at

diagnostic_centres
  - id, name, location, created_at

diagnostic_tests
  - id, centre_id (FK), name, price, created_at

bookings
  - id, user_id (FK), test_id (FK), centre_id (FK)
  - appointment_at, amount, status (PENDING|CONFIRMED|FAILED|CANCELLED)
  - created_at, updated_at

payments
  - id, booking_id (FK), amount, status (SUCCESS|FAILED)
  - provider_event_id (unique, nullable) — used for webhook idempotency
  - created_at, updated_at
```

### Design Decisions

- **Booking amount** is derived from the test price at booking time (snapshot), so price changes do not affect existing bookings.
- **Centre/test consistency** is validated when creating a booking — a test must belong to the selected centre.
- **Webhook idempotency** uses a unique `provider_event_id`. Duplicate events return the existing payment without changing state.
- **Authorization** ensures users can only access their own bookings and payments.

## Edge Cases Handled

- Duplicate email on signup → `409 Conflict`
- Invalid login credentials → `401 Unauthorized`
- Missing/invalid JWT → `401 Unauthorized`
- Accessing another user's booking → `403 Forbidden`
- Invalid centre/test/booking IDs → `404 Not Found`
- Booking in the past → `409 Conflict`
- Test not offered by selected centre → `409 Conflict`
- Payment on non-pending booking → `409 Conflict`
- Webhook amount mismatch → `409 Conflict`
- Duplicate webhook events → idempotent (same response, no duplicate records)
- Race condition on duplicate webhook → handled via DB unique constraint + retry lookup

## Assumptions

1. Centre creation is public (no admin role) to keep the assignment scope small.
2. Payment webhook does not require provider authentication (would add HMAC signature verification in production).
3. One successful payment per booking; repeated payment attempts on confirmed bookings are rejected.
4. Timezone-aware datetimes are used for appointments.
5. Tables are auto-created on startup for simplicity; Alembic migrations would be added for production.

## Bonus Features Included

- Docker & docker-compose
- Swagger/OpenAPI (FastAPI `/docs`)
- Structured logging
- Pagination on centre listing
- Comprehensive pytest suite

## What I Would Improve With More Time

- Role-based access (admin vs patient)
- Alembic migrations instead of `create_all`
- Webhook signature verification
- Redis caching for centre listings
- Background retry queue for failed webhook processing
- Rate limiting on auth endpoints
- CI pipeline with automated test runs
