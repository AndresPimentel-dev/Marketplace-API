# 🎮 Nexus Market

### A backend for a limited digital gaming cosmetics marketplace

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Alembic](https://img.shields.io/badge/Alembic-Migrations-6BA81E?logo=alembic&logoColor=white)](https://alembic.sqlalchemy.org/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Loki](https://img.shields.io/badge/Grafana_Loki-Logging-F46800?logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)
[![JWT Auth](https://img.shields.io/badge/JWT-Authentication-000000?logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![Celery](https://img.shields.io/badge/Celery-Task_Queue-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-Message_Broker-DC382D?logo=redis&logoColor=white)](https://redis.io/)

**Nexus Market** is a backend project for a fictional gaming cosmetics marketplace where players can browse, purchase, and manage digital items such as weapon skins, character cosmetics, emotes, and collectibles.

The project focuses on backend engineering fundamentals that become important beyond basic CRUD applications: transactional consistency, concurrent inventory reservations, secure authentication, asynchronous payment processing, automated testing, and operational observability.

> **Project status:** In development. This README describes the intended system and its technical goals. Features, infrastructure, and test results should be marked as implemented only after they have been built and verified.

---

## Features

- Concurrency
- Observability
- User registration and authentication
- JWT authentication
- Ecomerce Service
- Products Management
- PostgreSQL
- Database migrations
- Automated tests
- Docker

## 🎯 Overview

Nexus Market simulates the backend of a digital storefront for a fictional game called **Nexus Rift**.

Users can explore a catalog of digital cosmetics, add items to their carts, place orders, and receive purchased items in their digital inventories.

The main engineering challenge is handling limited-edition items during high-demand releases, also known as *limited drops*.

For example, if a skin has only 10 units available and 100 users attempt to purchase it simultaneously, the system must ensure that no more than 10 units are reserved or sold.

This requires more than endpoint validation. It requires correct database transactions, concurrency control, inventory invariants, and carefully managed order and payment states.

The project also explores asynchronous workflows and observability, keeping the architecture within the scope of a maintainable backend application rather than introducing unnecessary microservices.

### Project goals

- Design a REST API with clearly separated responsibilities.
- Implement authentication and resource-level authorization.
- Model a commerce workflow using PostgreSQL and SQLAlchemy.
- Prevent overselling during concurrent purchases.
- Handle simulated payment notifications safely and idempotently.
- Execute background tasks using Celery and Redis.
- Test business logic, API behavior, database integration, and concurrency.
- Containerize the application and its supporting services.
- Expose useful metrics and structured logs for troubleshooting.

## ✨ Core Features

The following table describes the intended feature set. Update each status as implementation progresses.

| Feature | Description | Status |
|---|---|---|
| Authentication | User registration, login, JWT access and refresh tokens | Planned |
| Authorization | User and administrator roles | Planned |
| Cosmetics catalog | Browse, search, filter, and paginate items | Planned |
| Shopping cart | Add, update, and remove items | Planned |
| Orders | Create orders and preserve purchase-time prices | Planned |
| Limited drops | Manage limited stock and temporary reservations | Planned |
| Concurrency control | Prevent inventory overselling | Planned |
| Simulated payments | Process successful and failed payment outcomes | Planned |
| Payment webhooks | Verify and process events idempotently | Planned |
| Digital inventory | Deliver purchased items to user accounts | Planned |
| Background jobs | Execute asynchronous tasks with Celery | Planned |
| Database migrations | Manage schema changes with Alembic | Planned |
| Automated tests | Unit, API, integration, and concurrency tests | Planned |
| Containerization | Run application dependencies through Docker Compose | Planned |
| Observability | Metrics, dashboards, and centralized logs | Planned |
| CI pipeline | Automate code checks, tests, and image builds | Planned |

## 🛠️ Tech Stack

The intended technology stack is selected to address specific engineering problems.

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API and request validation |
| SQLAlchemy | Database access and ORM |
| PostgreSQL | Persistent storage and transactional consistency |
| Alembic | Database schema migrations |
| Redis | Celery message broker and optional caching |
| Celery | Asynchronous background processing |
| Pytest | Automated testing |
| Docker | Application and dependency containerization |
| Docker Compose | Local multi-service environment |
| GitHub Actions | Continuous integration |
| Prometheus | Metrics collection |
| Grafana | Metrics visualization and dashboards |
| Loki | Log aggregation and querying |

The architecture uses PostgreSQL as the source of truth for orders, payments, and inventory. Redis is not intended to replace the relational database or serve as the authoritative record of purchases.

## 🏗️ Architecture

Nexus Market is designed as a modular backend application with a separate worker process for background tasks.

```mermaid
flowchart TD
    Client[Client]
    API[FastAPI Application]
    Services[Business Services]
    DB[(PostgreSQL)]
    Redis[(Redis)]
    Worker[Celery Worker]
    Prom[Prometheus]
    Loki[Loki]
    Grafana[Grafana]

    Client --> API
    API --> Services
    Services --> DB
    API --> Redis
    Redis --> Worker
    Worker --> DB
    API --> Prom
    Worker --> Loki
    Prom --> Grafana
    Loki --> Grafana
```

The diagram represents the intended architecture. The exact metrics and logging collection paths will depend on the final configuration.

### Main components

**API layer**

Responsible for HTTP routing, request validation, authentication dependencies, response schemas, and error handling.

**Service layer**

Contains business rules such as order creation, stock reservation, payment transitions, and inventory delivery.

**Repository and database layer**

Handles persistence through SQLAlchemy and PostgreSQL, including transactions, constraints, and concurrency control.

**Background worker**

Processes tasks that do not need to block the original HTTP request, such as reservation expiration and payment-related processing.

**Observability stack**

Collects application metrics and logs to help inspect request behavior, failed operations, task execution, and system performance.

The goal is to maintain clear boundaries without splitting the application into multiple independently deployed business services prematurely.

## 🛒 Purchase Workflow

A typical purchase follows this lifecycle:

```mermaid
flowchart TD
    A[Browse Catalog] --> B[Add Items to Cart]
    B --> C[Submit Checkout]
    C --> D{Validate Stock}
    D -->|Unavailable| E[Reject Checkout]
    D -->|Available| F[Create Order and Reservations]
    F --> G[Pending Payment]
    G --> H[Simulated Payment Provider]
    H --> I{Payment Result}
    I -->|Success| J[Confirm Payment]
    J --> K[Commit Inventory Delivery]
    K --> L[Completed Order]
    I -->|Failure| M[Release Reservations]
    M --> N[Cancel Order]
```

The checkout process is intended to:

1. Authenticate the user and load their cart.
2. Validate the requested items and quantities.
3. Start a database transaction.
4. Lock the relevant inventory records or use an equivalent atomic concurrency-control strategy.
5. Verify that sufficient stock remains available.
6. Create the order, order items, and stock reservations.
7. Preserve the purchase-time price of each item.
8. Clear the cart only when checkout succeeds.
9. Commit the transaction.
10. Initiate the simulated payment workflow.
11. Complete the order and deliver the items after successful payment.

If any required stock reservation fails, the checkout must not leave behind a partially reserved cart.

## 🔒 Inventory and Concurrency

Concurrency control is one of the central engineering goals of Nexus Market.

Consider a limited drop with the following inventory:

- Total stock: 10 units
- Available stock: 10 units
- Concurrent purchase attempts: 100

The expected behavior is that no more than 10 units can be successfully reserved. The remaining requests must be rejected or handled according to the application's inventory policy.

### Inventory invariant

The system must preserve:

```text
stock_sold + stock_reserved <= stock_total
```

Available stock is calculated as:

```text
available_stock = stock_total - stock_sold - stock_reserved
```

### Intended approach

The implementation will use PostgreSQL transactions and appropriate concurrency controls to prevent competing requests from reserving the same units.

Depending on the operation, this may involve row-level locking with `SELECT ... FOR UPDATE`, atomic conditional updates, or a combination of database constraints and transaction logic.

The essential requirement is that checking availability and reserving stock cannot be separated into an unsafe read-then-write sequence.

### Reservation lifecycle

A reservation temporarily holds inventory while a payment is pending.

- **Created:** available stock decreases.
- **Confirmed:** reserved stock is converted into sold stock.
- **Failed or expired:** the reservation is released and the stock becomes available again.

Reservations are intended to expire after a configurable period, such as 10 minutes.

The final implementation must ensure that payment confirmation and reservation expiration cannot both successfully finalize conflicting outcomes.

### Concurrency test objective

A key acceptance test will submit 100 concurrent purchase attempts against 10 available units.

Expected result:

- Successful reservations: 10
- Rejected attempts due to unavailable stock: 90
- Oversold inventory: 0

These are target results, not a claim that the test has already passed. Actual results should be documented after running the test against the real database configuration.

## 📦 Orders and Payments

### Order lifecycle

Orders will follow explicit state transitions rather than allowing arbitrary status changes.

| State | Meaning |
|---|---|
| `PENDING_PAYMENT` | The order has been created and awaits payment |
| `PAYMENT_CONFIRMED` | The payment has been confirmed |
| `PAYMENT_FAILED` | The payment attempt has failed |
| `CANCELLED` | The order has been cancelled |
| `EXPIRED` | The payment or reservation deadline has expired |
| `COMPLETED` | The purchase has been finalized and the inventory delivered |

Only valid transitions will be permitted. For example, a completed order must not return to `PENDING_PAYMENT`.

The implementation should define the exact transitions and their transactional effects in one clearly identifiable part of the business logic.

### Price snapshots

Each order item will store the unit price applied when the order was created.

This prevents historical orders from changing when catalog prices are updated.

For example, if an item was purchased for `$9.99` and its catalog price later increases to `$19.99`, the existing order must retain the original `$9.99` unit price.

### Simulated payment provider

The project will use a mock payment provider instead of processing real money.

The simulated provider will support successful and failed payment outcomes and notify the application through a webhook endpoint.

This allows the backend to demonstrate payment-related state transitions without requiring live payment credentials or real financial transactions.

### Webhook idempotency

Webhook providers may deliver the same event more than once because of retries or network failures.

Nexus Market is designed to record processed webhook event identifiers and ensure that duplicate events do not deliver the same items repeatedly or finalize the same purchase twice.

The intended processing flow is:

1. Receive the webhook.
2. Verify its signature.
3. Validate the event and its associated payment.
4. Detect whether the event has already been processed.
5. Apply the appropriate state transition transactionally.
6. Record the processed event.
7. Return an appropriate response.

The event record and business changes must be committed consistently. Concurrent deliveries of the same event must also be handled safely.

## 🔐 Authentication and Security

The intended security model includes:

- Password hashing instead of storing plaintext passwords.
- JWT access tokens and refresh tokens.
- User and administrator roles.
- Protected endpoints for personal orders and inventory.
- Ownership checks when accessing individual resources.
- Request validation for identifiers, quantities, prices, and state transitions.
- Webhook signature verification.
- Environment-based configuration for secrets.
- Consistent error responses without exposing sensitive internal details.

Authentication alone is not sufficient for authorization. For example, a user must not be able to access another user's order simply by changing the order ID in the request.

Administrator-only operations will manage catalog items, stock, and limited drops.

Payment signatures, passwords, access tokens, and other secrets must never be written to application logs.

## 🗄️ Database Design

The planned relational model includes the following entities:

| Entity | Responsibility |
|---|---|
| `users` | User accounts, password hashes, and roles |
| `skins` | Catalog items, prices, rarity, and stock information |
| `carts` | Shopping carts associated with users |
| `cart_items` | Items and quantities in each cart |
| `orders` | Order ownership, status, total, and expiration |
| `order_items` | Purchased items, quantities, and price snapshots |
| `payments` | Payment identifiers, amounts, and statuses |
| `reservations` | Temporarily reserved inventory |
| `inventory_items` | Digital items acquired by users |
| `processed_webhook_events` | Webhook event identifiers used for deduplication |

The exact schema, indexes, foreign keys, unique constraints, and transaction boundaries will be documented alongside the implementation.

### Data integrity considerations

- Order items reference their parent orders.
- Prices and totals are validated and represented using appropriate decimal types rather than floating-point arithmetic.
- Historical purchase prices are stored independently of current catalog prices.
- Database constraints protect critical relationships and uniqueness requirements.
- Stock changes occur within controlled transactions.
- Alembic migrations manage schema evolution.

PostgreSQL is the authoritative store for the commerce workflow.

## ⚙️ Background Processing

Celery and Redis will support work that should not unnecessarily block HTTP requests.

Planned tasks include:

- Processing simulated payment operations.
- Expiring outstanding reservations.
- Sending purchase confirmation notifications.
- Reconciling pending orders.

Background tasks must account for retries and potential duplicate execution. A retry must not cause duplicate inventory delivery or an invalid order transition.

Celery is used where asynchronous processing provides a practical benefit, not as a replacement for ordinary synchronous business logic.

## 📊 Observability

The project aims to provide useful operational visibility rather than simply including monitoring tools in the technology stack.

### Prometheus

Planned application metrics include:

- HTTP request counts and latency.
- HTTP error rates.
- Orders created and completed.
- Successful and failed payments.
- Stock reservation failures.
- Background task outcomes and execution duration.

Metric names and labels will be finalized during implementation. Labels should avoid unbounded values such as individual user IDs or order IDs.

### Grafana

The planned dashboard will organize metrics into three areas:

**API performance**
- Request volume
- Latency
- Error rates

**Commerce**
- Order outcomes
- Payment outcomes
- Reservation failures

**Background processing**
- Task success and failure counts
- Task execution duration

### Loki and structured logging

Application logs should use structured fields to make related events easier to investigate.

Examples of useful events include:

- `order.created`
- `payment.completed`
- `payment.failed`
- `stock.reserved`
- `stock.reservation_failed`# 🎮 Nexus Market

### A backend for a limited digital gaming cosmetics marketplace

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerization-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

**Nexus Market** is a backend project for a fictional gaming cosmetics marketplace where players can browse, purchase, and manage digital items such as weapon skins, character cosmetics, emotes, and collectibles.

The project focuses on backend engineering fundamentals that become important beyond basic CRUD applications: transactional consistency, concurrent inventory reservations, secure authentication, asynchronous payment processing, automated testing, and operational observability.

> **Project status:** In development. This README describes the intended system and its technical goals. Features, infrastructure, and test results should be marked as implemented only after they have been built and verified.

---


## 🎯 Overview

Nexus Market simulates the backend of a digital storefront for a fictional game called **Nexus Rift**.

Users can explore a catalog of digital cosmetics, add items to their carts, place orders, and receive purchased items in their digital inventories.

The main engineering challenge is handling limited-edition items during high-demand releases, also known as *limited drops*.

For example, if a skin has only 10 units available and 100 users attempt to purchase it simultaneously, the system must ensure that no more than 10 units are reserved or sold.

This requires more than endpoint validation. It requires correct database transactions, concurrency control, inventory invariants, and carefully managed order and payment states.

The project also explores asynchronous workflows and observability, keeping the architecture within the scope of a maintainable backend application rather than introducing unnecessary microservices.

### Project goals

- Design a REST API with clearly separated responsibilities.
- Implement authentication and resource-level authorization.
- Model a commerce workflow using PostgreSQL and SQLAlchemy.
- Prevent overselling during concurrent purchases.
- Handle simulated payment notifications safely and idempotently.
- Execute background tasks using Celery and Redis.
- Test business logic, API behavior, database integration, and concurrency.
- Containerize the application and its supporting services.
- Expose useful metrics and structured logs for troubleshooting.

## ✨ Core Features

The following table describes the intended feature set. Update each status as implementation progresses.

| Feature | Description | Status |
|---|---|---|
| Authentication | User registration, login, JWT access and refresh tokens | Planned |
| Authorization | User and administrator roles | Planned |
| Cosmetics catalog | Browse, search, filter, and paginate items | Planned |
| Shopping cart | Add, update, and remove items | Planned |
| Orders | Create orders and preserve purchase-time prices | Planned |
| Limited drops | Manage limited stock and temporary reservations | Planned |
| Concurrency control | Prevent inventory overselling | Planned |
| Simulated payments | Process successful and failed payment outcomes | Planned |
| Payment webhooks | Verify and process events idempotently | Planned |
| Digital inventory | Deliver purchased items to user accounts | Planned |
| Background jobs | Execute asynchronous tasks with Celery | Planned |
| Database migrations | Manage schema changes with Alembic | Planned |
| Automated tests | Unit, API, integration, and concurrency tests | Planned |
| Containerization | Run application dependencies through Docker Compose | Planned |
| Observability | Metrics, dashboards, and centralized logs | Planned |
| CI pipeline | Automate code checks, tests, and image builds | Planned |

## 🛠️ Tech Stack

The intended technology stack is selected to address specific engineering problems.

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API and request validation |
| SQLAlchemy | Database access and ORM |
| PostgreSQL | Persistent storage and transactional consistency |
| Alembic | Database schema migrations |
| Redis | Celery message broker and optional caching |
| Celery | Asynchronous background processing |
| Pytest | Automated testing |
| Docker | Application and dependency containerization |
| Docker Compose | Local multi-service environment |
| GitHub Actions | Continuous integration |
| Prometheus | Metrics collection |
| Grafana | Metrics visualization and dashboards |
| Loki | Log aggregation and querying |

The architecture uses PostgreSQL as the source of truth for orders, payments, and inventory. Redis is not intended to replace the relational database or serve as the authoritative record of purchases.

## 🏗️ Architecture

Nexus Market is designed as a modular backend application with a separate worker process for background tasks.

```mermaid
flowchart TD
    Client[Client]
    API[FastAPI Application]
    Services[Business Services]
    DB[(PostgreSQL)]
    Redis[(Redis)]
    Worker[Celery Worker]
    Prom[Prometheus]
    Loki[Loki]
    Grafana[Grafana]

    Client --> API
    API --> Services
    Services --> DB
    API --> Redis
    Redis --> Worker
    Worker --> DB
    API --> Prom
    Worker --> Loki
    Prom --> Grafana
    Loki --> Grafana
```

The diagram represents the intended architecture. The exact metrics and logging collection paths will depend on the final configuration.

### Main components

**API layer**

Responsible for HTTP routing, request validation, authentication dependencies, response schemas, and error handling.

**Service layer**

Contains business rules such as order creation, stock reservation, payment transitions, and inventory delivery.

**Repository and database layer**

Handles persistence through SQLAlchemy and PostgreSQL, including transactions, constraints, and concurrency control.

**Background worker**

Processes tasks that do not need to block the original HTTP request, such as reservation expiration and payment-related processing.

**Observability stack**

Collects application metrics and logs to help inspect request behavior, failed operations, task execution, and system performance.

The goal is to maintain clear boundaries without splitting the application into multiple independently deployed business services prematurely.

## 🛒 Purchase Workflow

A typical purchase follows this lifecycle:

```mermaid
flowchart TD
    A[Browse Catalog] --> B[Add Items to Cart]
    B --> C[Submit Checkout]
    C --> D{Validate Stock}
    D -->|Unavailable| E[Reject Checkout]
    D -->|Available| F[Create Order and Reservations]
    F --> G[Pending Payment]
    G --> H[Simulated Payment Provider]
    H --> I{Payment Result}
    I -->|Success| J[Confirm Payment]
    J --> K[Commit Inventory Delivery]
    K --> L[Completed Order]
    I -->|Failure| M[Release Reservations]
    M --> N[Cancel Order]
```

The checkout process is intended to:

1. Authenticate the user and load their cart.
2. Validate the requested items and quantities.
3. Start a database transaction.
4. Lock the relevant inventory records or use an equivalent atomic concurrency-control strategy.
5. Verify that sufficient stock remains available.
6. Create the order, order items, and stock reservations.
7. Preserve the purchase-time price of each item.
8. Clear the cart only when checkout succeeds.
9. Commit the transaction.
10. Initiate the simulated payment workflow.
11. Complete the order and deliver the items after successful payment.

If any required stock reservation fails, the checkout must not leave behind a partially reserved cart.

## 🔒 Inventory and Concurrency

Concurrency control is one of the central engineering goals of Nexus Market.

Consider a limited drop with the following inventory:

- Total stock: 10 units
- Available stock: 10 units
- Concurrent purchase attempts: 100

The expected behavior is that no more than 10 units can be successfully reserved. The remaining requests must be rejected or handled according to the application's inventory policy.

### Inventory invariant

The system must preserve:

```text
stock_sold + stock_reserved <= stock_total
```

Available stock is calculated as:

```text
available_stock = stock_total - stock_sold - stock_reserved
```

### Intended approach

The implementation will use PostgreSQL transactions and appropriate concurrency controls to prevent competing requests from reserving the same units.

Depending on the operation, this may involve row-level locking with `SELECT ... FOR UPDATE`, atomic conditional updates, or a combination of database constraints and transaction logic.

The essential requirement is that checking availability and reserving stock cannot be separated into an unsafe read-then-write sequence.

### Reservation lifecycle

A reservation temporarily holds inventory while a payment is pending.

- **Created:** available stock decreases.
- **Confirmed:** reserved stock is converted into sold stock.
- **Failed or expired:** the reservation is released and the stock becomes available again.

Reservations are intended to expire after a configurable period, such as 10 minutes.

The final implementation must ensure that payment confirmation and reservation expiration cannot both successfully finalize conflicting outcomes.

### Concurrency test objective

A key acceptance test will submit 100 concurrent purchase attempts against 10 available units.

Expected result:

- Successful reservations: 10
- Rejected attempts due to unavailable stock: 90
- Oversold inventory: 0

These are target results, not a claim that the test has already passed. Actual results should be documented after running the test against the real database configuration.

## 📦 Orders and Payments

### Order lifecycle

Orders will follow explicit state transitions rather than allowing arbitrary status changes.

| State | Meaning |
|---|---|
| `PENDING_PAYMENT` | The order has been created and awaits payment |
| `PAYMENT_CONFIRMED` | The payment has been confirmed |
| `PAYMENT_FAILED` | The payment attempt has failed |
| `CANCELLED` | The order has been cancelled |
| `EXPIRED` | The payment or reservation deadline has expired |
| `COMPLETED` | The purchase has been finalized and the inventory delivered |

Only valid transitions will be permitted. For example, a completed order must not return to `PENDING_PAYMENT`.

The implementation should define the exact transitions and their transactional effects in one clearly identifiable part of the business logic.

### Price snapshots

Each order item will store the unit price applied when the order was created.

This prevents historical orders from changing when catalog prices are updated.

For example, if an item was purchased for `$9.99` and its catalog price later increases to `$19.99`, the existing order must retain the original `$9.99` unit price.

### Simulated payment provider

The project will use a mock payment provider instead of processing real money.

The simulated provider will support successful and failed payment outcomes and notify the application through a webhook endpoint.

This allows the backend to demonstrate payment-related state transitions without requiring live payment credentials or real financial transactions.

### Webhook idempotency

Webhook providers may deliver the same event more than once because of retries or network failures.

Nexus Market is designed to record processed webhook event identifiers and ensure that duplicate events do not deliver the same items repeatedly or finalize the same purchase twice.

The intended processing flow is:

1. Receive the webhook.
2. Verify its signature.
3. Validate the event and its associated payment.
4. Detect whether the event has already been processed.
5. Apply the appropriate state transition transactionally.
6. Record the processed event.
7. Return an appropriate response.

The event record and business changes must be committed consistently. Concurrent deliveries of the same event must also be handled safely.

## 🔐 Authentication and Security

The intended security model includes:

- Password hashing instead of storing plaintext passwords.
- JWT access tokens and refresh tokens.
- User and administrator roles.
- Protected endpoints for personal orders and inventory.
- Ownership checks when accessing individual resources.
- Request validation for identifiers, quantities, prices, and state transitions.
- Webhook signature verification.
- Environment-based configuration for secrets.
- Consistent error responses without exposing sensitive internal details.

Authentication alone is not sufficient for authorization. For example, a user must not be able to access another user's order simply by changing the order ID in the request.

Administrator-only operations will manage catalog items, stock, and limited drops.

Payment signatures, passwords, access tokens, and other secrets must never be written to application logs.

## 🗄️ Database Design

The planned relational model includes the following entities:

| Entity | Responsibility |
|---|---|
| `users` | User accounts, password hashes, and roles |
| `skins` | Catalog items, prices, rarity, and stock information |
| `carts` | Shopping carts associated with users |
| `cart_items` | Items and quantities in each cart |
| `orders` | Order ownership, status, total, and expiration |
| `order_items` | Purchased items, quantities, and price snapshots |
| `payments` | Payment identifiers, amounts, and statuses |
| `reservations` | Temporarily reserved inventory |
| `inventory_items` | Digital items acquired by users |
| `processed_webhook_events` | Webhook event identifiers used for deduplication |

The exact schema, indexes, foreign keys, unique constraints, and transaction boundaries will be documented alongside the implementation.

### Data integrity considerations

- Order items reference their parent orders.
- Prices and totals are validated and represented using appropriate decimal types rather than floating-point arithmetic.
- Historical purchase prices are stored independently of current catalog prices.
- Database constraints protect critical relationships and uniqueness requirements.
- Stock changes occur within controlled transactions.
- Alembic migrations manage schema evolution.

PostgreSQL is the authoritative store for the commerce workflow.

## ⚙️ Background Processing

Celery and Redis will support work that should not unnecessarily block HTTP requests.

Planned tasks include:

- Processing simulated payment operations.
- Expiring outstanding reservations.
- Sending purchase confirmation notifications.
- Reconciling pending orders.

Background tasks must account for retries and potential duplicate execution. A retry must not cause duplicate inventory delivery or an invalid order transition.

Celery is used where asynchronous processing provides a practical benefit, not as a replacement for ordinary synchronous business logic.

## 📊 Observability

The project aims to provide useful operational visibility rather than simply including monitoring tools in the technology stack.

### Prometheus

Planned application metrics include:

- HTTP request counts and latency.
- HTTP error rates.
- Orders created and completed.
- Successful and failed payments.
- Stock reservation failures.
- Background task outcomes and execution duration.

Metric names and labels will be finalized during implementation. Labels should avoid unbounded values such as individual user IDs or order IDs.

### Grafana

The planned dashboard will organize metrics into three areas:

**API performance**
- Request volume
- Latency
- Error rates

**Commerce**
- Order outcomes
- Payment outcomes
- Reservation failures

**Background processing**
- Task success and failure counts
- Task execution duration

### Loki and structured logging

Application logs should use structured fields to make related events easier to investigate.

Examples of useful events include:

- `order.created`
- `payment.completed`
- `payment.failed`
- `stock.reserved`
- `stock.reservation_failed`
- `webhook.processed`

Where appropriate, logs will include a request ID and relevant operation identifiers. Sensitive credentials and tokens will be excluded.

## 🧪 Testing Strategy

The testing strategy is designed to verify both business behavior and the correctness of database operations.

| Test level | Primary purpose |
|---|---|
| Unit tests | Validate business rules and state transitions in isolation |
| API tests | Verify HTTP responses, validation, authentication, and authorization |
| Integration tests | Exercise persistence and workflows against real dependencies |
| Concurrency tests | Verify that simultaneous purchases cannot oversell inventory |

### Important test scenarios

- User registration and authentication.
- Access restrictions for administrative endpoints.
- Order ownership and authorization.
- Cart validation and price calculations.
- Successful and failed checkout operations.
- Transaction rollback when a reservation fails.
- Reservation expiration and stock release.
- Duplicate payment webhook delivery.
- Inventory delivery after successful payment.
- Background task retries.
- Simultaneous purchase attempts against limited stock.

Critical inventory and locking tests should run against PostgreSQL with the required schema and database features. SQLite alone is not sufficient to validate PostgreSQL-specific locking behavior.

Redis and Celery integration tests should use the actual services when their behavior is part of what the test intends to verify.

The goal is to run the appropriate tests automatically in CI and make failures reproducible.

## 📁 Project Structure

The following is the proposed organization. The final structure may change as the implementation evolves.

```text
nexus-market/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies/
│   │   └── middleware/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── tasks/
│   ├── db/
│   │   ├── session.py
│   │   └── migrations/
│   ├── observability/
│   └── main.py
├── tests/
│   ├── unit/
│   ├── api/
│   ├── integration/
│   └── concurrency/
├── prometheus/
├── grafana/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Getting Started

The following is the intended local development workflow. Commands and configuration should be adjusted to match the files that actually exist in the repository.

### Prerequisites

- Python 3.12 or a compatible project-supported version.
- Docker and Docker Compose.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/AndresPimentel-dev/Nexus-Market.git
cd Nexus-Market
```

Replace the repository URL if the final GitHub repository uses a different name or location.

### 2. Configure environment variables

Create a local environment file from the example:

```bash
cp .env.example .env
```

Populate the required values in `.env`. Never commit real credentials or production secrets.

### 3. Start the services

Once the Docker Compose configuration is implemented:

```bash
docker compose up --build -d
```

### 4. Apply database migrations

If Alembic has been configured in the application:

```bash
docker compose exec api alembic upgrade head
```

### 5. Inspect the application

Once the API is running and the relevant routes are configured, FastAPI's interactive documentation is typically available at:

```text
http://localhost:443/docs
```

The commands above describe the expected workflow. They are not guaranteed to work until the corresponding Docker, environment, and migration configuration has been implemented.

## 🔧 Environment Configuration

The application will use environment variables for configuration. The exact variable names should match the settings implementation.

Example of the configuration categories:

```dotenv
POSTGRES_USER=POSTGRES_USER_EXAMPLe
POSTGRES_PASSWORD=POSTGRES_PASSWORD_EXAMPLE
SECRET_KEY=SECRET_KEY_EXAMPLE
ADMIN_EMAIL=ADMIN_EMAIL@EXAMPLE.COM
ADMIN_PASSWORD=ADMIN_PASSWORD_EXAMPLE
```

These values are illustrative. The final configuration must define the actual required variables, defaults, validation rules, and secret-management practices.

Use separate configuration for local development and CI where appropriate. Do not reuse example secrets in a public deployment.

## 📖 API Documentation

The API is intended to expose REST endpoints grouped by domain.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Register an account |
| `POST` | `/auth/login` | Authenticate a user |
| `POST` | `/auth/refresh` | Refresh an access token |
| `GET` | `/auth/me` | Retrieve the current user's profile |
| `GET` | `/skins` | Browse the cosmetics catalog |
| `GET` | `/skins/{skin_id}` | Retrieve a catalog item |
| `GET` | `/cart` | Retrieve the current user's cart |
| `POST` | `/cart/items` | Add an item to the cart |
| `PATCH` | `/cart/items/{item_id}` | Update a cart item |
| `DELETE` | `/cart/items/{item_id}` | Remove a cart item |
| `POST` | `/orders` | Initiate checkout and create an order |
| `GET` | `/orders` | List the current user's orders |
| `GET` | `/orders/{order_id}` | Retrieve an order |
| `GET` | `/inventory` | Retrieve the user's digital inventory |
| `POST` | `/admin/skins` | Create a catalog item |
| `PATCH` | `/admin/skins/{skin_id}` | Update a catalog item |
| `POST` | `/admin/drops` | Create a limited drop |
| `POST` | `/webhooks/payments` | Receive simulated payment events |

This is the planned endpoint surface, not a guarantee that every route is currently available. Actual request schemas, response formats, status codes, and authorization requirements should be documented in the generated API specification.

## 🔄 Continuous Integration

The intended CI pipeline will validate changes before they are merged.

Planned checks include:

1. Install project dependencies.
2. Run linting and formatting checks.
3. Run static type checks where configured.
4. Execute unit tests.
5. Start the required services for integration tests.
6. Run API, database, and concurrency tests.
7. Build the Docker image.

The pipeline will use disposable test infrastructure where required, including PostgreSQL and Redis. Tests must not depend on production credentials or production data.

The initial goal is a reliable, reproducible CI pipeline, not an unnecessarily complex deployment platform.

## 🧠 Architecture Decisions

Several design choices are central to the project.

### PostgreSQL as the source of truth

Orders, payments, and inventory require durable persistence and transactional guarantees. Redis may support background processing and caching, but it does not replace PostgreSQL for authoritative commerce state.

### Reservations instead of immediate sales

Inventory is temporarily reserved during checkout so that concurrent purchases cannot claim the same available units.

### Idempotent payment handling

Payment events can be delivered more than once. Persisted event tracking and transactional state transitions are intended to prevent duplicate processing from causing duplicate side effects.

### A modular monolith instead of microservices

The project will keep business domains separated within one application. This reduces deployment and operational complexity while preserving clear boundaries for testing and maintenance.

### A mock payment provider instead of real payments

Simulated payments allow the project to focus on backend workflow correctness without handling actual financial transactions or requiring live payment credentials.

Detailed Architecture Decision Records can be maintained under `docs/adr/` as the implementation progresses.

## 🗺️ Roadmap

The development plan prioritizes working functionality before infrastructure polish.

- [ ] **Phase 1 — Foundation:** Application setup, configuration, PostgreSQL, SQLAlchemy, Alembic, and authentication.
- [ ] **Phase 2 — Catalog:** Cosmetics, categories, rarity, filtering, pagination, and administrative operations.
- [ ] **Phase 3 — Cart and orders:** Cart management, order creation, order items, and price snapshots.
- [ ] **Phase 4 — Inventory consistency:** Stock reservations, transactions, concurrency control, and overselling tests.
- [ ] **Phase 5 — Payments:** Simulated provider, payment states, signed webhooks, and idempotency.
- [ ] **Phase 6 — Background processing:** Celery tasks, Redis, reservation expiration, and retry-safe operations.
- [ ] **Phase 7 — Testing and CI:** Automated test suites, real dependency integration tests, and Docker image validation.
- [ ] **Phase 8 — Observability:** Structured logs, request IDs, Prometheus metrics, Grafana dashboards, and Loki integration.
- [ ] **Phase 9 — Documentation and deployment:** Verified setup instructions, API examples, architecture decisions, and a reproducible demonstration.

A phase should be considered complete only when its behavior is implemented and verified, not merely when its dependencies have been added.

## ⚠️ Limitations

Nexus Market is a portfolio project, not a production commerce platform.

The intended scope includes simulated payments, a fictional catalog, and a single deployable backend application. It does not claim to provide real payment processing, production-grade fraud prevention, multi-region availability, or the operational guarantees of a mature commercial marketplace.

Security, concurrency, retries, and data consistency remain implementation and testing responsibilities. Using a particular technology does not, by itself, guarantee that those concerns have been solved correctly.

The project will document verified functionality and known limitations as development progresses.

## 👨‍💻 Author

**Andres Pimentel**

Systems Engineering Student | Backend Development

GitHub: [@AndresPimentel-dev](https://github.com/AndresPimentel-dev)

Nexus Market is a personal backend engineering project focused on building practical experience with Python, API design, relational databases, concurrency, asynchronous processing, automated testing, and observability.

---

*Built to explore the engineering problems behind reliable digital commerce, one transaction at a time.*
- `webhook.processed`

Where appropriate, logs will include a request ID and relevant operation identifiers. Sensitive credentials and tokens will be excluded.

## 🧪 Testing Strategy

The testing strategy is designed to verify both business behavior and the correctness of database operations.

| Test level | Primary purpose |
|---|---|
| Unit tests | Validate business rules and state transitions in isolation |
| API tests | Verify HTTP responses, validation, authentication, and authorization |
| Integration tests | Exercise persistence and workflows against real dependencies |
| Concurrency tests | Verify that simultaneous purchases cannot oversell inventory |

### Important test scenarios

- User registration and authentication.
- Access restrictions for administrative endpoints.
- Order ownership and authorization.
- Cart validation and price calculations.
- Successful and failed checkout operations.
- Transaction rollback when a reservation fails.
- Reservation expiration and stock release.
- Duplicate payment webhook delivery.
- Inventory delivery after successful payment.
- Background task retries.
- Simultaneous purchase attempts against limited stock.

Critical inventory and locking tests should run against PostgreSQL with the required schema and database features. SQLite alone is not sufficient to validate PostgreSQL-specific locking behavior.

Redis and Celery integration tests should use the actual services when their behavior is part of what the test intends to verify.

The goal is to run the appropriate tests automatically in CI and make failures reproducible.

## 📁 Project Structure

The following is the proposed organization. The final structure may change as the implementation evolves.

```text
nexus-market/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── dependencies/
│   │   └── middleware/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── logging.py
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── tasks/
│   ├── db/
│   │   ├── session.py
│   │   └── migrations/
│   ├── observability/
│   └── main.py
├── tests/
│   ├── unit/
│   ├── api/
│   ├── integration/
│   └── concurrency/
├── docs/
│   └── adr/
├── monitoring/
│   ├── prometheus/
│   └── grafana/
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── pyproject.toml
└── README.md
```

## 🚀 Getting Started

The following is the intended local development workflow. Commands and configuration should be adjusted to match the files that actually exist in the repository.

### Prerequisites

- Python 3.12 or a compatible project-supported version.
- Docker and Docker Compose.
- Git.

### 1. Clone the repository

```bash
git clone https://github.com/AndresPimentel-dev/Nexus-Market.git
cd Nexus-Market
```

Replace the repository URL if the final GitHub repository uses a different name or location.

### 2. Configure environment variables

Create a local environment file from the example:

```bash
cp .env.example .env
```

Populate the required values in `.env`. Never commit real credentials or production secrets.

### 3. Start the services

Once the Docker Compose configuration is implemented:

```bash
docker compose up --build -d
```

### 4. Apply database migrations

If Alembic has been configured in the application:

```bash
docker compose exec api alembic upgrade head
```

### 5. Inspect the application

Once the API is running and the relevant routes are configured, FastAPI's interactive documentation is typically available at:

```text
http://localhost:8000/docs
```

The commands above describe the expected workflow. They are not guaranteed to work until the corresponding Docker, environment, and migration configuration has been implemented.

## 🔧 Environment Configuration

The application will use environment variables for configuration. The exact variable names should match the settings implementation.

Example of the configuration categories:

```dotenv
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000

DATABASE_URL=postgresql+psycopg://user:password@postgres:5432/nexus_market

REDIS_URL=redis://redis:6379/0

JWT_SECRET_KEY=replace_with_a_secure_random_secret
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=15
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

PAYMENT_WEBHOOK_SECRET=replace_with_a_local_webhook_secret
```

These values are illustrative. The final configuration must define the actual required variables, defaults, validation rules, and secret-management practices.

Use separate configuration for local development and CI where appropriate. Do not reuse example secrets in a public deployment.

## 📖 API Documentation

The API is intended to expose REST endpoints grouped by domain.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/auth/register` | Register an account |
| `POST` | `/auth/login` | Authenticate a user |
| `POST` | `/auth/refresh` | Refresh an access token |
| `GET` | `/auth/me` | Retrieve the current user's profile |
| `GET` | `/skins` | Browse the cosmetics catalog |
| `GET` | `/skins/{skin_id}` | Retrieve a catalog item |
| `GET` | `/cart` | Retrieve the current user's cart |
| `POST` | `/cart/items` | Add an item to the cart |
| `PATCH` | `/cart/items/{item_id}` | Update a cart item |
| `DELETE` | `/cart/items/{item_id}` | Remove a cart item |
| `POST` | `/orders` | Initiate checkout and create an order |
| `GET` | `/orders` | List the current user's orders |
| `GET` | `/orders/{order_id}` | Retrieve an order |
| `GET` | `/inventory` | Retrieve the user's digital inventory |
| `POST` | `/admin/skins` | Create a catalog item |
| `PATCH` | `/admin/skins/{skin_id}` | Update a catalog item |
| `POST` | `/admin/drops` | Create a limited drop |
| `POST` | `/webhooks/payments` | Receive simulated payment events |

This is the planned endpoint surface, not a guarantee that every route is currently available. Actual request schemas, response formats, status codes, and authorization requirements should be documented in the generated API specification.

## 🔄 Continuous Integration

The intended CI pipeline will validate changes before they are merged.

Planned checks include:

1. Install project dependencies.
2. Run linting and formatting checks.
3. Run static type checks where configured.
4. Execute unit tests.
5. Start the required services for integration tests.
6. Run API, database, and concurrency tests.
7. Build the Docker image.

The pipeline will use disposable test infrastructure where required, including PostgreSQL and Redis. Tests must not depend on production credentials or production data.

The initial goal is a reliable, reproducible CI pipeline, not an unnecessarily complex deployment platform.

## 🧠 Architecture Decisions

Several design choices are central to the project.

### PostgreSQL as the source of truth

Orders, payments, and inventory require durable persistence and transactional guarantees. Redis may support background processing and caching, but it does not replace PostgreSQL for authoritative commerce state.

### Reservations instead of immediate sales

Inventory is temporarily reserved during checkout so that concurrent purchases cannot claim the same available units.

### Idempotent payment handling

Payment events can be delivered more than once. Persisted event tracking and transactional state transitions are intended to prevent duplicate processing from causing duplicate side effects.

### A modular monolith instead of microservices

The project will keep business domains separated within one application. This reduces deployment and operational complexity while preserving clear boundaries for testing and maintenance.

### A mock payment provider instead of real payments

Simulated payments allow the project to focus on backend workflow correctness without handling actual financial transactions or requiring live payment credentials.

Detailed Architecture Decision Records can be maintained under `docs/adr/` as the implementation progresses.

## 🗺️ Roadmap

The development plan prioritizes working functionality before infrastructure polish.

- [ ] **Phase 1 — Foundation:** Application setup, configuration, PostgreSQL, SQLAlchemy, Alembic, and authentication.
- [ ] **Phase 2 — Catalog:** Cosmetics, categories, rarity, filtering, pagination, and administrative operations.
- [ ] **Phase 3 — Cart and orders:** Cart management, order creation, order items, and price snapshots.
- [ ] **Phase 4 — Inventory consistency:** Stock reservations, transactions, concurrency control, and overselling tests.
- [ ] **Phase 5 — Payments:** Simulated provider, payment states, signed webhooks, and idempotency.
- [ ] **Phase 6 — Background processing:** Celery tasks, Redis, reservation expiration, and retry-safe operations.
- [ ] **Phase 7 — Testing and CI:** Automated test suites, real dependency integration tests, and Docker image validation.
- [ ] **Phase 8 — Observability:** Structured logs, request IDs, Prometheus metrics, Grafana dashboards, and Loki integration.
- [ ] **Phase 9 — Documentation and deployment:** Verified setup instructions, API examples, architecture decisions, and a reproducible demonstration.

A phase should be considered complete only when its behavior is implemented and verified, not merely when its dependencies have been added.

## ⚠️ Limitations

Nexus Market is a portfolio project, not a production commerce platform.

The intended scope includes simulated payments, a fictional catalog, and a single deployable backend application. It does not claim to provide real payment processing, production-grade fraud prevention, multi-region availability, or the operational guarantees of a mature commercial marketplace.

Security, concurrency, retries, and data consistency remain implementation and testing responsibilities. Using a particular technology does not, by itself, guarantee that those concerns have been solved correctly.

The project will document verified functionality and known limitations as development progresses.

## 👨‍💻 Author

**Andres Pimentel**

Systems Engineering Student | Backend Development

GitHub: [@AndresPimentel-dev](https://github.com/AndresPimentel-dev)

Nexus Market is a personal backend engineering project focused on building practical experience with Python, API design, relational databases, concurrency, asynchronous processing, automated testing, and observability.

---

*Built to explore the engineering problems behind reliable digital commerce, one transaction at a time.*