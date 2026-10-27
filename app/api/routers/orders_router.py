import hashlib
import hmac
import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.order_dependencies import get_order_service
from app.core.config import settings
from app.db.session import get_db
from app.models.models import OrdersStatus, PaymentsTable, PaymentStatus, UsersTable
from app.repositories.payment_repository import PaymentRepository
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
    return OrderListResponse.model_validate({"orders": orders})


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
    db: Session = Depends(get_db),  # noqa: B008
):
    """
    Simula que el usuario va a pagar su orden.
    Este endpoint llama a la "pasarela de pagos simulada" (que vive en nuestro propio sistema
    o simula un servicio externo) para iniciar la transacción de cobro.
    """

    # 1. Validar que la orden pertenezca al usuario y esté en estado PENDING_PAYMENT
    order = order_service.get_order(user_id=current_user.id, order_id=payload.order_id)

    if order.status != OrdersStatus.PENDING_PAYMENT:
        raise HTTPException(
            status_code=409, detail=f"Order is already in state: {order.status}"
        )

    # 2. Generar IDs únicos para la simulación
    payment_id = f"pay_{current_user.id}_{order.id}"
    event_id = f"evt_{current_user.id}_{order.id}_success"

    # 3. Persistir o actualizar el registro de pago en PaymentsTable
    payment_repo = PaymentRepository(db)
    existing_payment = payment_repo.get_payment_by_order_id(order_id=order.id)
    if not existing_payment:
        new_payment = PaymentsTable(
            order_id=order.id,
            payment_id=payment_id,
            amount=order.total_amount,
            status=PaymentStatus.PENDING,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        payment_repo.create_payment(new_payment)
    else:
        payment_id = existing_payment.payment_id

    db.commit()

    # 4. SIMULACIÓN DE LA PASARELA EXTERNA
    webhook_payload = {
        "event_id": event_id,
        "payment_id": payment_id,
        "order_id": order.id,
        "status": "succeeded",
    }

    # Calcular firma HMAC para conveniencia del llamador/tests
    payload_raw = json.dumps(webhook_payload, separators=(",", ":")).encode("utf-8")
    signature = hmac.new(
        settings.WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_raw,
        digestmod=hashlib.sha256,
    ).hexdigest()

    return {
        "message": "Payment initiated successfully via mock gateway",
        "payment_id": payment_id,
        "checkout_url": f"https://mock-gateway.nexusmarket.internal/pay/{payment_id}",
        "simulated_webhook_payload_to_send": webhook_payload,
        "simulated_webhook_signature": signature,
    }
