from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

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
    )


@router.post("/payments", status_code=200)
def payment_webhook(
    payload: PaymentWebhookPayload,
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
    # (Opcional avanzado) Validar firma aquí si deseas simular seguridad real
    # if not x_signature or x_signature != "expected_secret":
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid webhook signature")

    result = payment_service.process_payment_webhook(
        event_id=payload.event_id,
        payment_id=payload.payment_id,
        order_id=payload.order_id,
        status=payload.status,
    )
    # Hacer commit explícito de la transacción si todo sale bien
    db.commit()
    return result
