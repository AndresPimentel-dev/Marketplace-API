from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import PaymentsTable, ProcessedWebhookEventsTable


class PaymentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_payment_by_order_id(self, order_id: int) -> PaymentsTable | None:
        stmt = select(PaymentsTable).where(PaymentsTable.order_id == order_id)
        return self.db.scalars(stmt).first()

    def create_payment(self, payment: PaymentsTable) -> PaymentsTable:
        self.db.add(payment)
        self.db.flush()
        self.db.refresh(payment)
        return payment

    def is_event_processed(self, event_id: str) -> bool:
        stmt = select(ProcessedWebhookEventsTable).where(
            ProcessedWebhookEventsTable.event_id == event_id
        )
        result = self.db.scalars(stmt).first()
        return result is not None

    def mark_event_as_processed(self, event_id: str, event_type: str) -> None:
        event_record = ProcessedWebhookEventsTable(
            event_id=event_id,
            event_type=event_type,
            processed_at=datetime.now(UTC),
        )
        self.db.add(event_record)
        self.db.flush()
        self.db.refresh(event_record)
