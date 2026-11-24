import hashlib
import hmac

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.skin_repository import SkinsRepository
from app.repositories.webhook_events_repository import WebhookEventsRepository
from app.services.payment_service import PaymentService


def get_payment_service(
    db: Session = Depends(get_db),  # noqa: B008
) -> PaymentService:
    return PaymentService(
        payment_repo=PaymentRepository(db),
        order_repo=OrderRepository(db),
        skin_repo=SkinsRepository(db),
        webhook_repo=WebhookEventsRepository(db),
        db=db,
    )


def verify_webhook_signature(
    payload_bytes: bytes, signature_header: str | None
) -> None:
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
