import hashlib
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.skin_repository import SkinsRepository
from app.schemas.payment import PaymentWebhookPayload
from app.services.payment_service import PaymentService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


def get_payment_service(
    db: Session = Depends(get_db),  # noqa: B008
) -> PaymentService:
    return PaymentService(
        payment_repo=PaymentRepository(db),
        order_repo=OrderRepository(db),
        skin_repo=SkinsRepository(db),
        db=db,
    )


def verify_webhook_signature(payload_bytes: bytes, signature_header: str | None) -> None:
    if not signature_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature",
        )

    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256,
    ).hexdigest()

    # Support optional 'sha256=' prefix or direct hex
    provided = signature_header.removeprefix("sha256=")

    if not hmac.compare_digest(expected_signature, provided):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature",
        )


@router.post("/payments", status_code=200)
async def payment_webhook(
    request: Request,
    x_signature: str | None = Header(
        None, description="Webhook signature for security"
    ),
    payment_service: PaymentService = Depends(  # noqa: B008
        get_payment_service
    ),
    db: Session = Depends(get_db),  # noqa: B008
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
    db.commit()
    return result
