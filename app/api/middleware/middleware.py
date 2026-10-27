import time
import uuid

from fastapi import Request
from prometheus_client import Counter, Histogram

# Definición de métricas
HTTP_REQUESTS = Counter(
    "http_requests_total", "Total HTTP Requests", ["method", "endpoint", "status"]
)
HTTP_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP Request Latency", ["endpoint"]
)


async def observability_middleware(request: Request, call_next):
    # Asignar Request ID
    req_id = request.headers.get("X-Request-ID", f"req_{uuid.uuid4().hex[:6]}")

    start_time = time.time()
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception:
        status_code = 500
        raise
    finally:
        process_time = time.time() - start_time
        # Extraer plantilla de ruta (e.g. /orders/{id}) para evitar explosión de cardinalidad
        route = request.scope.get("route")
        endpoint = route.path if route and hasattr(route, "path") else request.url.path

        HTTP_REQUESTS.labels(
            method=request.method, endpoint=endpoint, status=status_code
        ).inc()
        HTTP_LATENCY.labels(endpoint=endpoint).observe(process_time)

    response.headers["X-Request-ID"] = req_id
    return response
