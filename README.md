# 🎮 Nexus Market — High-Concurrency Gaming Cosmetics Marketplace API

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Celery](https://img.shields.io/badge/Celery-5.4+-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Metrics-E6522C?logo=prometheus&logoColor=white)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Dashboards-F46800?logo=grafana&logoColor=white)](https://grafana.com/)
[![Loki](https://img.shields.io/badge/Grafana_Loki-Structured_Logs-F46800?logo=grafana&logoColor=white)](https://grafana.com/oss/loki/)

**Nexus Market** es una API backend RESTful de alto rendimiento diseñada para una tienda digital de cosméticos de videojuegos (*skins*, coleccionables, estandartes y armas). 

El proyecto resuelve los desafíos críticos de ingeniería de backend que surgen más allá del CRUD convencional: **control de concurrencia y prevención de sobreventa (*overselling*) en lanzamientos limitados**, **reservas transaccionales de inventario con expiración asíncrona**, **webhooks de pagos idempotentes y verificados criptográficamente (HMAC-SHA256)** y un **stack integral de observabilidad en tiempo real**.

---

## 📋 Tabla de Contenidos

1. [Problema de Negocio y Desafíos Técnicos](#-problema-de-negocio-y-desafíos-técnicos)
2. [Arquitectura del Sistema](#-arquitectura-del-sistema)
3. [Decisiones Clave de Ingeniería](#-decisiones-clave-de-ingeniería)
   - [Concurrencia e Invariante de Inventario](#1-concurrencia-e-invariante-de-inventario)
   - [Ciclo de Vida de Órdenes y Pagos](#2-ciclo-de-vida-de-órdenes-y-pagos)
   - [Seguridad Criptográfica en Webhooks](#3-seguridad-criptográfica-en-webhooks)
   - [Workers Asíncronos para Expiración de Reservas](#4-workers-asíncronos-para-expiración-de-reservas)
4. [Stack Tecnológico](#-stack-tecnológico)
5. [Estructura del Proyecto](#-estructura-del-proyecto)
6. [Catálogo de Endpoints de la API](#-catálogo-de-endpoints-de-la-api)
7. [Observabilidad, Métricas y Logs](#-observabilidad-métricas-y-logs)
8. [Puesta en Marcha con Docker Compose](#-puesta-en-marcha-con-docker-compose)
9. [Configuración Local y Desarrollo](#-configuración-local-y-desarrollo)
10. [Estrategia de Pruebas Automatizadas](#-estrategia-de-pruebas-automatizadas)
11. [Autor](#-autor)

---

## 🎯 Problema de Negocio y Desafíos Técnicos

Durante un *limited drop* (lanzamiento de cosméticos exclusivos de edición limitada), cientos o miles de usuarios intentan adquirir un stock finito (por ejemplo, 10 unidades) en el mismo segundo exacto.

Un backend tradicional que ejecuta una secuencia ingenua de lectura y escritura (`SELECT stock` -> validar en Python -> `UPDATE stock`) sufre de **condiciones de carrera (*Race Conditions*)**, provocando sobreventa de productos (*overselling*), inconsistencia financiera y degradación del servicio.

**Nexus Market resuelve esto mediante:**
- **Bloqueo pesimista a nivel de fila (`SELECT ... FOR UPDATE`)**: Garantiza que transacciones simultáneas compitan en cola a nivel de PostgreSQL, serializando de forma segura la reserva de stock.
- **Reservas transaccionales con TTL (Time-To-Live)**: El stock se aparta temporalmente (10 minutos) con un estado `pending_payment`. Si el usuario no paga, Celery + Redis liberan el stock automáticamente.
- **Webhook de pagos con firma HMAC-SHA256 e Idempotencia**: La pasarela de pagos notifica el resultado mediante webhook firmado. Se protege la ruta contra falsificación de payloads y se garantiza idempotencia estricta para evitar entregas dobles de inventario frente a reintentos de red.

---

## 🏗️ Arquitectura del Sistema

El proyecto sigue una arquitectura en capas limpia (*Controller / Service / Repository / Database*) estructurada como un **Monolito Modular** altamente escalable:

```mermaid
flowchart TD
    Client([Cliente / Frontend / Swagger])
    Caddy[Caddy Reverse Proxy :80/:443]
    FastAPI[FastAPI Application :8000]
    
    subgraph Core App
        AuthRouter[Auth Router]
        CatalogRouter[Catalog Router]
        CartRouter[Cart Router]
        OrderRouter[Orders & Checkout Router]
        WebhookRouter[Payment Webhook Router]
        Services[Service Layer: Order, Payment, Catalog, Cart]
        Repos[Repositories: DB Transactions & Queries]
    end

    subgraph Data Stores
        PostgreSQL[(PostgreSQL 15)]
        Redis[(Redis 7)]
    end

    subgraph Async Processing
        CeleryWorker[Celery Background Worker]
    end

    subgraph Observability
        Prometheus[Prometheus Scraper]
        Loki[Grafana Loki]
        Alloy[Grafana Alloy Log Collector]
        Grafana[Grafana Dashboards :3000]
    end

    Client --> Caddy
    Caddy --> FastAPI
    FastAPI --> AuthRouter & CatalogRouter & CartRouter & OrderRouter & WebhookRouter
    AuthRouter & CatalogRouter & CartRouter & OrderRouter & WebhookRouter --> Services
    Services --> Repos
    Repos -->|Row-level Lock / Atomic TX| PostgreSQL
    Services -->|Dispatch Task Countdown 600s| Redis
    Redis --> CeleryWorker
    CeleryWorker -->|Expire Stale Reservations| PostgreSQL
    
    FastAPI -->|/metrics| Prometheus
    Prometheus --> Grafana
    FastAPI & CeleryWorker -->|Docker Logs| Alloy
    Alloy --> Loki
    Loki --> Grafana
```

---

## 🔒 Decisiones Clave de Ingeniería

### 1. Concurrencia e Invariante de Inventario

El stock de cada cosmético se modela con tres contadores explícitos:
- `stock_total`: Cantidad máxima emitida.
- `stock_reserved`: Cantidad apartada en órdenes pendientes de pago.
- `stock_sold`: Cantidad efectivamente vendida y entregada.

**Invariante matemático estricto:**
$$\text{stock\_sold} + \text{stock\_reserved} \le \text{stock\_total}$$
$$\text{available\_stock} = \text{stock\_total} - \text{stock\_sold} - \text{stock\_reserved}$$

Para reservar stock sin condiciones de carrera, el repositorio adquiere un candado pesimista en la base de datos:
```python
# app/repositories/skin_repository.py
def get_skin_with_lock(self, skin_id: int) -> SkinsTable | None:
    stmt = select(SkinsTable).where(SkinsTable.id == skin_id).with_for_update()
    return self.db.scalars(stmt).first()
```
Toda la operación (verificar disponibilidad, incrementar `stock_reserved`, crear ítems de orden y vaciar carrito) se ejecuta dentro de la misma transacción atómica de SQLAlchemy.

### 2. Ciclo de Vida de Órdenes y Pagos

El flujo de compra se desglosa en 4 fases desacopladas y atómicas:

```mermaid
sequenceDiagram
    autonumber
    actor User as Usuario
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Worker as Celery Worker
    participant Gateway as Mock Payment Gateway

    User->>API: POST /api/v5.0/orders (Crear orden desde Carrito)
    activate API
    API->>DB: Lock Skins (FOR UPDATE) & Verificar Stock
    API->>DB: Incrementar stock_reserved, crear Order (PENDING_PAYMENT)
    API->>Worker: Programar expire_stale_reservations (Countdown: 600s)
    API-->>User: 201 Created (Order ID, expires_at: now + 10m)
    deactivate API

    User->>API: POST /api/v5.0/checkout (Iniciar pago)
    activate API
    API->>DB: Crear registro PaymentsTable (PENDING)
    API-->>User: 200 OK (payment_id, mock checkout_url, webhook payload firmado)
    deactivate API

    Note over Gateway: Simulación externa de cobro
    Gateway->>API: POST /webhooks/payments (X-Signature HMAC-SHA256)
    activate API
    API->>API: Validar HMAC-SHA256 con WEBHOOK_SECRET
    API->>DB: Verificar Idempotencia (ProcessedWebhookEventsTable)
    API->>DB: Validar estado de orden y vigencia (not expired)
    alt Pago Succeeded
        API->>DB: Order -> PAYMENT_CONFIRMED, Payment -> SUCCEEDED
        API->>DB: stock_reserved -= qty, stock_sold += qty
        API->>DB: Crear registros en InventoryItemsTable
    else Pago Failed
        API->>DB: Order -> PAYMENT_FAILED, Payment -> FAILED
        API->>DB: stock_reserved -= qty (liberar stock)
    end
    API->>DB: Registrar event_id en processedwebhooksstable
    API-->>Gateway: 200 OK
    deactivate API
```

### 3. Seguridad Criptográfica en Webhooks

Los webhooks asíncronos son vectores de ataque comunes si no se autentican. Para mitigar falsificaciones:
1. **Firma HMAC-SHA256**: La pasarela calcula un hash criptográfico sobre el cuerpo HTTP crudo utilizando una clave compartida (`WEBHOOK_SECRET`).
2. **Validación en Tiempo Constante**: Se valida la firma con `hmac.compare_digest` para neutralizar ataques de temporización (*timing attacks*).
3. **Idempotencia Transaccional**: La tabla `processedwebhooksstable` registra el `event_id`. Si la pasarela reintenta el webhook por latencia de red, el sistema detecta el duplicado y responde `already_processed` de inmediato sin duplicar ítems ni transferir stock por segunda vez.

### 4. Workers Asíncronos para Expiración de Reservas

Si un usuario abandona el proceso de pago, el stock reservado no puede quedar bloqueado indefinidamente.
- Al crear la orden, se despacha una tarea diferida de Celery: `expire_stale_reservations.apply_async(countdown=600)`.
- Si la orden continúa en `pending_payment` tras 10 minutos, el worker cambia el estado a `cancelled` y reintegra el `stock_reserved` al inventario disponible de forma segura.

---

## 🛠️ Stack Tecnológico

| Capa / Herramienta | Tecnología | Justificación Técnica |
|---|---|---|
| **Lenguaje** | Python 3.11+ | Tipado estricto, alto desempeño y sintaxis moderna. |
| **Framework API** | FastAPI | Validación automática por schemas con Pydantic v2 y rendimiento asíncrono. |
| **ORM & Database** | SQLAlchemy 2.0 & PostgreSQL 15 | Control granular de transacciones ACID, tipos nativos (Enum, Decimal, UUID) y soporte de `FOR UPDATE`. |
| **Migraciones** | Alembic | Versionado declarativo e incremental de base de datos. |
| **Autenticación** | OAuth2 + JWT (PyJWT) & Passlib (Bcrypt) | Tokens Bearer sin estado con hash de contraseñas de alta seguridad. |
| **Cola de Tareas** | Celery 5.4 + Redis 7 | Procesamiento asíncrono y tareas programadas desacopladas del ciclo HTTP. |
| **Proxy Inverso** | Caddy 2 | Enrutamiento perimetral, compresión y soporte TLS. |
| **Métricas** | Prometheus Client | Exposición de métricas de negocio y latencias en `/metrics`. |
| **Visualización** | Grafana 10+ | Dashboards unificados de rendimiento, órdenes y tasas de error. |
| **Logging Centralizado** | Grafana Alloy + Loki | Ingesta y consulta estructurada de logs en formato JSON. |
| **Testing** | Pytest + TestClient + Factory mocks | Pruebas unitarias, de integración, cobertura de API y pruebas de concurrencia real multi-hilo. |

---

## 📁 Estructura del Proyecto

```text
Marketplace-API/
├── app/
│   ├── api/
│   │   ├── dependencies/       # Inyección de dependencias (Auth, DB, Services)
│   │   ├── middleware/         # Observabilidad y Correlation ID
│   │   └── routers/            # Controladores HTTP (Auth, Cart, Catalog, Orders, Webhook)
│   ├── core/
│   │   ├── config.py           # Variables de entorno validadas con Pydantic Settings
│   │   ├── exceptions.py       # Excepciones de negocio personalizadas
│   │   ├── logging.py          # Configuración de logs estructurados en JSON
│   │   └── security.py         # Hashing Bcrypt, generación y validación de JWT
│   ├── db/
│   │   └── session.py          # Engine de SQLAlchemy y generador de sesiones
│   ├── models/
│   │   └── models.py           # Modelos ORM (Users, Skins, Orders, Payments, Inventory)
│   ├── repositories/           # Capa de acceso a datos pura (Skins, Orders, Payments, Cart)
│   ├── schemas/                # Modelos Pydantic de entrada/salida (DTOs)
│   ├── services/               # Lógica de negocio (OrderService, PaymentService, etc.)
│   ├── tasks/                  # Tareas asíncronas de Celery (expire_stale_reservations)
│   ├── worker/                 # Configuración de Celery App
│   └── main.py                 # Punto de entrada de FastAPI
├── alembic/                    # Scripts de migraciones de base de datos
├── alloy/                      # Configuración de Grafana Alloy
├── grafana/                    # Provisionamiento de Datasources para Grafana
├── loki/                       # Configuración de Grafana Loki
├── tests/
│   ├── api/                    # Pruebas de endpoints y de concurrencia con ThreadPoolExecutor
│   ├── integration/            # Pruebas de integración de repositorios y base de datos
│   ├── unit/                   # Pruebas unitarias de servicios y seguridad
│   └── conftest.py             # Fixtures de Pytest, DB de pruebas y clientes
├── create_admin.py             # Script de inicialización de superusuario
├── docker-compose.yml          # Orquestación de contenedores para producción/staging
├── requirements.txt            # Dependencias del proyecto
└── README.md
```

---

## 🌐 Catálogo de Endpoints de la API

La API expone sus rutas principales bajo el prefijo `/api/v5.0` y el webhook bajo `/webhooks`.

### 🔑 Autenticación & Usuarios
- `POST /api/v5.0/auth/register` — Registro de nuevo usuario (retorna Access + Refresh Tokens).
- `POST /api/v5.0/auth/login` — Autenticación con formulario OAuth2 (retorna Access + Refresh Tokens).
- `POST /api/v5.0/auth/refresh` — Renovación de token JWT mediante Refresh Token válido.
- `GET /api/v5.0/auth/me` — Perfil y datos del usuario autenticado actual.

### 🎨 Catálogo de Skins
- `GET /api/v5.0/skins` — Listado con soporte de filtros (`category`, `rarity`, `currency`, `is_limited`) y paginación (`page`, `page_size`).
- `GET /api/v5.0/skins/{skin_id}` — Detalle de una skin activa.
- `POST /api/v5.0/skins` — *[Admin]* Creación de nuevo cosmético o drop limitado.
- `PATCH /api/v5.0/skins/{skin_id}` — *[Admin]* Actualización de precio, descripción o estado.
- `DELETE /api/v5.0/skins/{skin_id}` — *[Admin]* Desactivación lógica de una skin.

### 🛒 Carrito de Compras
- `GET /api/v5.0/cart` — Obtener el carrito activo del usuario y subtotal acumulado.
- `POST /api/v5.0/cart/items` — Agregar una skin al carrito con cantidad solicitada.
- `PATCH /api/v5.0/cart/items/{item_id}` — Actualizar cantidad de un ítem en el carrito.
- `DELETE /api/v5.0/cart/items/{item_id}` — Remover un ítem del carrito.

### 📦 Órdenes y Checkout
- `POST /api/v5.0/orders` — **Crear orden a partir del carrito**. Reserva atómicamente el stock bajo candado pesimista y programa la expiración asíncrona a 10 min.
- `GET /api/v5.0/orders` — Listado de órdenes del usuario autenticado.
- `GET /api/v5.0/orders/{order_id}` — Consulta detallada de una orden.
- `POST /api/v5.0/checkout` — Inicia el proceso de pago, persiste el registro en `PaymentsTable` (`pending`) y genera el payload simulado con firma HMAC.

### 💳 Webhook de Pagos
- `POST /webhooks/payments` — Recibe eventos asíncronos de la pasarela de pagos.
  - **Header requerido**: `X-Signature: <hex_hmac_sha256>`.
  - Procesa estados `succeeded` y `failed`.
  - Garantiza idempotencia mediante `event_id`.

### 🎒 Inventario de Usuario
- `GET /api/v5.0/inventory/user` — Consulta los cosméticos efectivamente adquiridos y acreditados al usuario tras pagos confirmados.
- `GET /api/v5.0/inventory/{inventory_item_id}` — Detalle de un ítem del inventario propio.

### 📊 Salud y Observabilidad
- `GET /health` — Health check simple del servicio (`{"status": "ok"}`).
- `GET /metrics` — Exposición de métricas en formato estándar Prometheus.

---

## 📈 Observabilidad, Métricas y Logs

El proyecto incorpora un stack completo de observabilidad para monitorizar el estado interno de la aplicación en producción:

### Métricas Prometheus Personalizadas
- `http_requests_total`: Conteo total de solicitudes HTTP segmentadas por método, ruta y código de estado.
- `http_request_duration_seconds`: Histograma de latencia de las respuestas HTTP.
- `orders_created_total`: Total de órdenes generadas por estado.
- `payments_total`: Total de transacciones de pago procesadas por estado (`succeeded`, `failed`).
- `stock_reservation_failures_total`: Contador de fallos por stock insuficiente durante compras concurrentes.
- `tasks_created_total`: Métrica de tareas asíncronas despachadas hacia Celery.

### Logging Estructurado con Grafana Loki & Alloy
Todos los eventos importantes de la aplicación (creación de órdenes, eventos de webhook, rollback de reservas y autenticaciones) se emiten en formato JSON estructurado con contexto enriquecido (`event_type`, `order_id`, `payment_id`, `user_id`), capturados de forma transparente por **Grafana Alloy** y agregados en **Loki**.

---

## 🐳 Puesta en Marcha con Docker Compose

La arquitectura completa (API, base de datos de producción, base de datos de test, Redis, Worker de Celery, Caddy, Prometheus, Grafana, Loki y Alloy) se levanta con un solo comando:

### 1. Clonar el repositorio y configurar variables
```bash
git clone https://github.com/AndresPimentel-dev/Marketplace-API.git
cd Marketplace-API
cp .env.example .env
```

Configura tu archivo `.env` según tus necesidades:
```env
POSTGRES_USER=admin_market
POSTGRES_PASSWORD=super_secure_password
SECRET_KEY=clave_secreta_jwt_para_firmar_tokens_de_produccion_2026
WEBHOOK_SECRET=super_webhook_secret_key
ADMIN_EMAIL=admin@nexusmarket.com
ADMIN_PASSWORD=admin_master_password
```

### 2. Iniciar los servicios
```bash
docker compose up --build -d
```

Durante el arranque:
1. PostgreSQL inicializa la base de datos principal y de tests.
2. El contenedor `migrations` corre `alembic upgrade head` y genera automáticamente el superadministrador inicial con `create_admin.py`.
3. El contenedor `tests_and_quality` corre la suite completa de pruebas (`pytest`, `ruff check`, `ruff format --check`) antes de habilitar el servicio de API.
4. El contenedor de API y el Worker Celery inician con sus dependencias listas.

### 3. Accesos y Paneles
- **Swagger UI / Documentación interactiva:** `http://localhost/docs` (o vía Caddy en puertos `80`/`443`)
- **Métricas Prometheus:** `http://localhost/metrics`
- **Grafana:** `http://localhost:3000` (Usuario: `admin` / Password: `admin`)
  - Dashboards y orígenes de datos (Prometheus y Loki) preconfigurados.

---

## 💻 Configuración Local y Desarrollo

Para ejecutar el proyecto fuera de contenedores para desarrollo local:

### 1. Entorno Virtual
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Base de Datos y Redis
Asegúrate de tener instancias locales de PostgreSQL y Redis en ejecución, y configura tu `.env`:
```env
DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/skin_ecomerce
SECRET_KEY=secret_key_local_development
WEBHOOK_SECRET=super_webhook_secret_key
```

### 3. Ejecutar Migraciones y Crear Administrador
```bash
alembic upgrade head
python create_admin.py
```

### 4. Iniciar Servidor de Desarrollo
```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Iniciar Worker de Celery (Terminal separada)
```bash
celery -A app.worker.celery_app.celery_app worker --loglevel=info
```

---

## 🧪 Estrategia de Pruebas Automatizadas

La suite de pruebas automatizadas está diseñada para validar el comportamiento del sistema bajo condiciones normales y extremas:

```bash
# Ejecutar todas las pruebas con pytest
pytest -v

# Ejecutar únicamente las pruebas de concurrencia
pytest tests/api/test_concurrency.py -v

# Ejecutar análisis de formato y linting con ruff
ruff check .
ruff format --check
```

### Cobertura de la Suite de Pruebas:
1. **Pruebas Unitarias (`tests/unit/`)**:
   - Algoritmos de hashing Bcrypt y validación de contraseñas.
   - Generación, expiración y decodificación de tokens JWT.
   - Lógica aislada de servicios con repositorios mockeados.
2. **Pruebas de Integración (`tests/integration/`)**:
   - Operaciones reales sobre PostgreSQL/SQLite de prueba.
   - Inserciones de catálogo, búsquedas con filtros y transacciones de carritos.
3. **Pruebas de Endpoints de la API (`tests/api/test_api.py`)**:
   - Flujo completo de registro, login y refresh token.
   - Flujo de checkout y creación de órdenes.
   - **Validación del webhook de pagos**: Verificación de rechazo ante firmas ausentes o inválidas (401), procesamiento exitoso (200), manejo de pagos fallidos con liberación de stock y prueba estricta de idempotencia ante payloads duplicados.
4. **Pruebas de Concurrencia Real (`tests/api/test_concurrency.py`)**:
   - Dos hilos paralelos (`concurrent.futures.ThreadPoolExecutor`) compitiendo simultáneamente por adquirir las últimas 5 unidades de una skin limitada.
   - Se valida de forma determinista que solo una orden resulte exitosa (201) y la transacción competidora sea rechazada de inmediato con error de stock insuficiente (400), demostrando la efectividad de `SELECT ... FOR UPDATE`.

---

## 👨‍💻 Autor

**Andres Pimentel**
- **GitHub:** [@AndresPimentel-dev](https://github.com/AndresPimentel-dev)
- **Rol:** Backend Developer / Estudiante de Ingeniería de Sistemas

*Proyecto desarrollado con un enfoque riguroso en consistencia transaccional, seguridad en pasarelas de pago y diseño backend de alta disponibilidad.*