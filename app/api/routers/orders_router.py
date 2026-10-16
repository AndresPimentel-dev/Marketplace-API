from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.order_dependencies import get_order_service
from app.models.models import UsersTable
from app.schemas.order import OrderListResponse, OrderResponse, PaymentCreateRequest
from app.services.order_service import OrderService

router = APIRouter(prefix="/api/v5.0", tags=["Orders"])

# ========================================================
#                   CART ROUTES
# ========================================================


@router.post("/orders", status_code=201, response_model=OrderResponse)
def create_order_route(
    order_service: OrderService = Depends(get_order_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> OrderResponse:

    return order_service.create_order(user_id=current_user.id)


@router.get("/orders", status_code=200, response_model=OrderListResponse)
def get_orders_route(
    order_service: OrderService = Depends(get_order_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
    page: int = Query(1, ge=1, description="page number"),
    page_size: int = Query(10, ge=10, le=50, description="page size"),
) -> OrderListResponse:
    orders = order_service.get_user_orders(
        user_id=current_user.id, page=page, page_size=page_size
    )
    return OrderListResponse.construct(orders)


@router.get("/orders/{order_id}", status_code=200, response_model=OrderResponse)
def get_order_route(
    order_id: int,
    order_service: OrderService = Depends(get_order_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> OrderResponse:

    return order_service.get_order(user_id=current_user.id, order_id=order_id)


@router.post("/checkout", status_code=200)
def initiate_mock_payment(
    payload: PaymentCreateRequest,
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
    order_service: OrderService = Depends(get_order_service),  # noqa: B008
):
    """
    Simula que el usuario va a pagar su orden.
    Este endpoint llama a la "pasarela de pagos simulada" (que vive en nuestro propio sistema
    o simula un servicio externo) para iniciar la transacción de cobro.
    """

    # 1. Validar que la orden pertenezca al usuario y esté en estado PENDING_PAYMENT
    # (Esto lo puedes delegar a tu OrderService o PaymentService)
    order = order_service.get_order(user_id=current_user.id, order_id=payload.order_id)

    if order.status == "payment_confirmed":
        raise HTTPException(status_code=409, detail="order already processed")

    # 2. Generar IDs únicos para la simulación
    payment_id = f"pay_{current_user.id}_{order.id}"
    event_id = f"evt_{current_user.id}_{order.id}_success"

    # 3. SIMULACIÓN DE LA PASARELA EXTERNA:
    # En un entorno real, aquí harías un request HTTP con `httpx` a la pasarela real
    # (ej. Stripe). Como es simulada, nosotros mismos podemos disparar el Webhook
    # de forma automática (o dejar que un botón en tu frontend lo haga).

    # Para esta demo, simularemos que la pasarela externa responde al instante
    # llamando a nuestro propio webhook de éxito:

    webhook_payload = {
        "event_id": event_id,
        "payment_id": payment_id,
        "order_id": order.id,
        "status": "succeeded",  # Puedes cambiar a "failed" para probar errores
    }

    return {
        "message": "Payment initiated successfully via mock gateway",
        "payment_id": payment_id,
        "checkout_url": f"https://mock-gateway.nexusmarket.internal/pay/{payment_id}",
        "simulated_webhook_payload_to_send": webhook_payload,
    }
