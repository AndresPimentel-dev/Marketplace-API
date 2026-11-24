from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.middleware.middleware import observability_middleware
from app.api.routers.auth_router import router as auth_router
from app.api.routers.cart_router import router as cart_router
from app.api.routers.catalog_router import router as catalog_router
from app.api.routers.inventory_router import router as inventory_router
from app.api.routers.orders_router import router as orders_router
from app.api.routers.payment_routes import router as payments_router
from app.core.exceptions import BusinessException

# from app.api.routers import users as users_router

app = FastAPI()
app.middleware("http")(observability_middleware)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    # generate_latest retorna bytes, CONTENT_TYPE_LATEST es 'text/plain; version=0.0.4'
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


# un atrapador de errores de fast api que ya conoce tus errores y hace el raise
# este anda pendiente de las respuestas de los endpoints
@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(auth_router)
app.include_router(catalog_router)
app.include_router(cart_router)
app.include_router(inventory_router)
app.include_router(orders_router)
app.include_router(payments_router)
# app.include_router(users_router)
