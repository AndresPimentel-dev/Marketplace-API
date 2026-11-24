# Marketplace API

[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![Railway](https://img.shields.io/badge/Deployed-Railway-0B0D0E?logo=railway&logoColor=white)](https://railway.app/)

Marketplace API is a production-oriented backend for a digital skin marketplace. It manages authentication, a categorized and filterable catalog, shopping carts, inventory, orders, payment webhooks, limited-stock reservations, and background cleanup tasks.

The project uses FastAPI for the public API, PostgreSQL for transactional persistence, Redis as the Celery broker and result backend, SQLAlchemy/Alembic for data access and migrations, and Prometheus, Grafana, Loki, and Grafana Alloy for observability. It is packaged with Docker and has an active deployment on Railway.

> API documentation is exposed by FastAPI at `/docs` and the OpenAPI specification at `/openapi.json`.

## Table of contents

- [Features](#features)
- [Architecture](#architecture)
- [Request and payment flows](#request-and-payment-flows)
- [API overview](#api-overview)
- [Data model](#data-model)
- [Observability](#observability)
- [Deployment on Railway](#deployment-on-railway)
- [Local development](#local-development)
- [Environment variables](#environment-variables)
- [Database migrations](#database-migrations)
- [Testing and quality](#testing-and-quality)
- [Project structure](#project-structure)
- [Security considerations](#security-considerations)

## Features

### Users and authentication

- User registration and login
- Password hashing with Argon2 through `pwdlib`
- JWT access tokens with a 15-minute lifetime
- JWT refresh tokens with a 7-day lifetime
- Current-user lookup and logout endpoints
- Role-aware authorization for administrator operations

### Catalog

- Public skin listing and detail endpoints
- Filtering by category, rarity, currency, and limited status
- Pagination for catalog results
- Administrator create, update, activate, and deactivate operations
- Product categories and currencies modeled as controlled enums

### Cart and inventory

- One persistent cart per user
- Add, update, list, delete, and empty cart operations
- Owned digital inventory after successful payment
- Inventory lookup and individual inventory item retrieval

### Orders and stock

- Checkout from the authenticated user's cart
- Atomic stock reservation using database row locks
- Currency consistency validation across cart items
- Reserved stock, sold stock, and total stock tracking
- Ten-minute order expiration window
- Automatic release of expired reservations
- Background Celery task for stale-order cleanup

### Payments

- Signed payment webhook endpoint
- HMAC-SHA256 signature verification
- Idempotency protection by `event_id`
- Payment success, failure, and expiration handling
- Automatic inventory delivery after a successful payment
- Prometheus counters for processed payments

## Architecture

```mermaid
flowchart LR
    Client[Web or API Client]
    Caddy[Caddy reverse proxy]
    API[FastAPI application\nAPI v5.0]
    DB[(PostgreSQL 15)]
    Redis[(Redis 7\nBroker + backend)]
    Worker[Celery worker]
    Beat[Celery Beat\n60-second schedule]
    Cleanup[Reservation cleanup task]
    Prometheus[Prometheus]
    Alloy[Grafana Alloy]
    Loki[Loki]
    Grafana[Grafana]

    Client -->|HTTP / HTTPS| Caddy
    Caddy --> API
    API -->|SQLAlchemy| DB
    API -->|dispatch countdown task| Redis
    Redis --> Worker
    Worker --> DB
    Beat -->|periodic task trigger| Redis
    Worker --> Cleanup

    API -->|/metrics on port 8000| Prometheus
    Prometheus --> Grafana
    API -->|container logs| Alloy
    Worker -->|container logs| Alloy
    Alloy --> Loki
    Loki --> Grafana
```

### Component responsibilities

| Component | Responsibility |
|---|---|
| FastAPI | REST API, authentication, business rules, Swagger UI, health and metrics endpoints |
| PostgreSQL | Users, products, carts, orders, inventory, payments, and webhook-event persistence |
| Redis | Celery message broker, result backend, and task queue |
| Celery Worker | Executes reservation cleanup and asynchronous work |
| Celery Beat | Publishes the reservation cleanup task on its configured schedule |
| Caddy | Optional local reverse proxy with automatic HTTPS behavior when configured with a real host |
| Prometheus | Scrapes FastAPI `/metrics` every five seconds in the Docker Compose stack |
| Grafana Alloy | Collects Docker container logs and forwards them to Loki |
| Loki | Stores and indexes application/container logs |
| Grafana | Visualizes Prometheus metrics and Loki logs |
| Railway | Hosts the deployed Marketplace API service and production environment |

## Request and payment flows

### Order creation

1. The authenticated user sends the cart to the order endpoint.
2. The service verifies that the cart exists and is not empty.
3. It locks each skin row while checking availability and currency consistency.
4. For limited skins, it verifies that `stock_total - stock_sold - stock_reserved` covers the requested quantity.
5. It increments `stock_reserved`, creates the order, clears the cart, and commits the transaction.
6. A Celery task is scheduled with a ten-minute countdown.

### Payment webhook

1. The payment provider sends an HTTP POST to `/webhooks/payments`.
2. The API checks the raw request body against `X-Signature` using HMAC-SHA256.
3. The service inserts the `event_id` into the webhook-event table for idempotency.
4. The order is loaded with a database lock and validated as pending and unexpired.
5. **Succeeded:** the reserved quantity is moved to sold stock and digital items are added to the user's inventory.
6. **Failed:** the reserved quantity is released and the order is marked as payment failed.
7. **Expired:** the reservation is released and the order is cancelled.

### Stale reservation cleanup

Celery Beat schedules `expire_stale_reservations` every 60 seconds. The task finds pending-payment orders whose `expires_at` has passed, locks or updates the affected rows, restores reserved stock with a non-negative guard, marks orders cancelled, and commits the transaction.

## API overview

All API routes use `/api/v5.0` unless explicitly noted otherwise.

| Area | Method | Route | Authentication |
|---|---|---|---|
| Health | `GET` | `/health` | Public |
| Metrics | `GET` | `/metrics` | Public; expose carefully |
| Authentication | `POST` | `/api/v5.0/auth/register` | Public |
| Authentication | `POST` | `/api/v5.0/auth/login` | Public |
| Authentication | `POST` | `/api/v5.0/auth/refresh` | Refresh token in body |
| Authentication | `GET` | `/api/v5.0/auth/me` | Bearer access token |
| Authentication | `POST` | `/api/v5.0/auth/logout` | Bearer access token |
| Catalog | `GET` | `/api/v5.0/skins` | Public |
| Catalog | `GET` | `/api/v5.0/skins/{skin_id}` | Public |
| Catalog | `POST` | `/api/v5.0/admin/skins` | Admin |
| Catalog | `PATCH` | `/api/v5.0/admin/skins/{skin_id}` | Admin |
| Catalog | `PATCH` | `/api/v5.0/admin/skins/{skin_id}/activate` | Admin |
| Catalog | `DELETE` | `/api/v5.0/admin/skins/{skin_id}` | Admin |
| Cart | `POST` | `/api/v5.0/cart/items` | Bearer access token |
| Cart | `GET` | `/api/v5.0/cart` | Bearer access token |
| Cart | `PATCH` | `/api/v5.0/cart/items/{skin_id}` | Bearer access token |
| Cart | `DELETE` | `/api/v5.0/cart/items/{skin_id}` | Bearer access token |
| Cart | `DELETE` | `/api/v5.0/cart/items` | Bearer access token |
| Inventory | `GET` | `/api/v5.0/inventory/user` | Bearer access token |
| Inventory | `GET` | `/api/v5.0/inventory/{inventory_item_id}` | Bearer access token |
| Orders | `POST` | `/api/v5.0/orders` | Bearer access token |
| Orders | `GET` | `/api/v5.0/orders` | Bearer access token |
| Orders | `GET` | `/api/v5.0/orders/{order_id}` | Bearer access token |
| Payments | `POST` | `/webhooks/payments` | HMAC webhook signature |

Example login with OAuth2 form data:

```bash
curl -X POST "http://localhost:8000/api/v5.0/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=strong-password"
```

Example authenticated request:

```bash
curl "http://localhost:8000/api/v5.0/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Data model

The main entities and relationships are:

- `UsersTable` — account, role, activation state, cart, orders, and inventory
- `SkinsTable` — marketplace item, price, currency, category, rarity, and stock counters
- `CartsTable` and `CartItemsTable` — one cart per user and one entry per skin
- `OrdersTable` and `OrdersItemsTable` — order state, totals, expiration, and line items
- `PaymentsTable` — external payment identifier and payment status
- `InventoryItemsTable` — delivered skin ownership associated with an order
- `WebhookEventsTable` — processed webhook event IDs for idempotency

Orders move through pending payment, confirmed, failed, cancelled, or completed states. Database constraints reject negative stock counters and non-positive cart quantities.

## Observability

A middleware assigns a request ID and exports HTTP counters and latency histograms. Every observed request records method, route, and status labels while route templates are preferred to avoid cardinality growth.

### Exported metrics

The `/metrics` endpoint exposes Prometheus-format metrics, including:

- `http_requests_total` — total HTTP requests by method, route, and status
- `http_request_duration_seconds` — request latency histogram
- `payments_total` — payments processed by status
- Celery, order, stock, and process metrics where instrumented
- Python runtime and process metrics collected by `prometheus_client`

### Grafana metrics view

![Prometheus metrics in Grafana](docs/images/metrics.png)

The project exposes `/metrics` for Prometheus scraping and uses Grafana dashboards for real-time visualization. The 15-second view above shows HTTP and process metrics from the running API stack.

### Centralized logs

![Docker container logs collected in Grafana Loki](docs/images/logs.png)

Grafana Alloy discovers Docker containers, relabels container names, and forwards their logs to Loki. Grafana can then filter by container, query log text, and correlate service output with metrics.

### Swagger UI

![Marketplace API Swagger documentation](docs/images/swagger.png)

FastAPI automatically provides the interactive Swagger interface and groups routes by authentication, catalog, cart, inventory, orders, and webhooks.

## Deployment on Railway

The repository includes a Dockerfile and can be deployed as a Docker-based Railway service.

![Railway project deployment](docs/images/railway1.png)

The deployed service is connected to a GitHub repository and is marked as active after a successful deployment. Railway rebuilds or redeploys from repository changes according to the project trigger configuration.

![Successful Railway deployment](docs/images/railway2.png)

### Recommended Railway setup

1. Create a Railway project and add a PostgreSQL plugin/database.
2. Create a Redis service if Celery is used in production.
3. Deploy this repository as the API service.
4. Use the repository Dockerfile or let Railway detect it automatically.
5. Set `DATABASE_URL`, `SECRET_KEY`, and `WEBHOOK_SECRET` in service variables.
6. Run Alembic migrations against the production database before accepting traffic.
7. Configure the public domain and health check path to `/health`.
8. Deploy a separate Celery worker service using:

```bash
celery -A app.worker.celery_app.celery_app worker --loglevel=info
```

9. Optionally deploy Celery Beat:

```bash
celery -A app.worker.celery_app beat --loglevel=info
```

> In a production Railway deployment, API, worker, Beat, PostgreSQL, and Redis should use separate appropriate services and shared private networking. Redis currently uses the Docker Compose service name `redis`; update or provide a compatible Redis URL for a split-cloud deployment if you change the Celery configuration.

## Local development

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- PostgreSQL 15 or Docker
- Redis 7 or Docker

### Run the complete Docker Compose stack

Create a `.env` file:

```dotenv
POSTGRES_USER=marketplace
POSTGRES_PASSWORD=change-me
SECRET_KEY=replace-with-a-long-random-secret
WEBHOOK_SECRET=replace-with-a-random-webhook-secret
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me
GRAFANA_USER=admin
GRAFANA_PASSWORD=change-me
```

Then start the stack:

```bash
docker compose up --build
```

The compose file starts PostgreSQL, Redis, migrations, tests, the API, Caddy, Celery worker, Celery Beat, Prometheus, Loki, Grafana Alloy, and Grafana.

Common endpoints:

- API health: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`
- Metrics: `http://localhost:8000/metrics`
- Grafana: `http://localhost:3000`
- Caddy HTTP/HTTPS: `http://localhost` / `https://localhost`

### Run the API directly

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export DATABASE_URL="postgresql+psycopg2://user:password@localhost:5432/skin_ecomerce"
export SECRET_KEY="replace-with-a-long-random-secret"
export WEBHOOK_SECRET="replace-with-a-random-webhook-secret"

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The application settings require `DATABASE_URL`, `SECRET_KEY`, and `WEBHOOK_SECRET`.

## Environment variables

| Variable | Required | Purpose |
|---|---:|---|
| `DATABASE_URL` | Yes | SQLAlchemy PostgreSQL connection URL |
| `SECRET_KEY` | Yes | HS256 signing key for JWT access and refresh tokens |
| `WEBHOOK_SECRET` | Yes | Shared secret for webhook HMAC-SHA256 verification |
| `POSTGRES_USER` | Compose | PostgreSQL administrator/application user |
| `POSTGRES_PASSWORD` | Compose | PostgreSQL password |
| `ADMIN_EMAIL` | Compose migrations | Initial administrator email |
| `ADMIN_PASSWORD` | Compose migrations | Initial administrator password |
| `GRAFANA_USER` | Optional | Grafana initial administrator name; defaults to `admin` |
| `GRAFANA_PASSWORD` | Optional | Grafana initial administrator password; defaults to `admin` |

Never commit real secrets. Use Railway variables or a local `.env` file excluded from version control.

## Database migrations

The project uses Alembic:

```bash
# Apply all migrations
alembic upgrade head

# Create a migration after changing SQLAlchemy models
alembic revision --autogenerate -m "describe the change"

# Roll back one migration
alembic downgrade -1
```

The migration container in Docker Compose runs `alembic upgrade head` and then executes `create_admin.py` before the API becomes available.

## Testing and quality

```bash
pytest
ruff check .
ruff format --check
```

The test stack uses a separate PostgreSQL database named `skin_ecomerce_test`. Docker Compose also includes a test-and-quality service that runs pytest, Ruff linting, and a Ruff formatting check before starting the API.

Test suites cover API behavior, integration flows, unit behavior, and concurrency where available under `tests/`.

## Project structure

```text
app/
├── api/
│   ├── dependencies/       # FastAPI dependency and authorization providers
│   ├── middleware/         # Request IDs and Prometheus instrumentation
│   └── routers/            # Authentication, catalog, cart, inventory, order, and payment routes
├── core/                   # Configuration, exceptions, logging, and security helpers
├── db/                     # SQLAlchemy engine and session factory
├── models/                 # SQLAlchemy database models and enums
├── repositories/           # Database query and persistence operations
├── schemas/                # Pydantic request and response models
├── services/               # Core application and business rules
├── tasks/                  # Celery reservation cleanup task
└── worker/                 # Celery application configuration
alembic/                    # Database migrations
alloy/                      # Grafana Alloy Docker log configuration
grafana/                    # Grafana data source provisioning
loki/                       # Loki configuration
docs/images/                # Deployment, API, metrics, and log screenshots
tests/                      # Unit, API, integration, and concurrency tests
```

## Security considerations

- Use a cryptographically strong `SECRET_KEY`; rotating it invalidates existing JWT signatures.
- Access tokens expire after 15 minutes and refresh tokens after seven days.
- Store the webhook secret as a protected environment variable and rotate it together with the provider configuration.
- Require HMAC verification before processing payment webhook data.
- Do not expose `/metrics` publicly unless access is restricted or the information is acceptable for your threat model.
- Change the default Grafana credentials supplied by the Compose file.
- Use HTTPS and private networking for database, Redis, and internal observability services in production.
- Review CORS and public-route configuration before exposing the API to browsers.

## License

See [LICENSE](LICENSE) for repository licensing terms.
