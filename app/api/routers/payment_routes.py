from fastapi import APIRouter, Depends, Header, Request

from app.api.dependencies.payment_dependencies import (
    get_payment_service,
    verify_webhook_signature,
)
from app.schemas.payment import PaymentWebhookPayload
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post("/payments", status_code=200)
async def payment_webhook(
    request: Request,
    x_signature: str | None = Header(
        None, description="Webhook signature for security"
    ),
    payment_service: PaymentService = Depends(  # noqa: B008
        get_payment_service
    ),
):
    """
    Endpoint que recibe los webhooks asíncronos de la pasarela de pagos simulada.
    Es idempotente gracias al `event_id`.
    """
    body = await request.body()
    verify_webhook_signature(body, x_signature)

    payload = PaymentWebhookPayload.model_validate_json(body)

    result = payment_service.process_payment_webhook(
        event_id=payload.event_id,
        payment_id=payload.payment_id,
        order_id=payload.order_id,
        status=payload.status,
    )
    # Hacer commit explícito de la transacción si todo sale bien
    return result
