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
    response = await call_next(request)
    process_time = time.time() - start_time

    # Registrar métricas
    HTTP_REQUESTS.labels(request.method, request.url.path, response.status_code).inc()
    HTTP_LATENCY.labels(request.url.path).observe(process_time)

    response.headers["X-Request-ID"] = req_id
    return response
