from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import ProcessedWebhookEventsTable


class WebhookEventsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_webhook_event_by_id(
        self, event_id: str
    ) -> ProcessedWebhookEventsTable | None:
        stmt = select(ProcessedWebhookEventsTable).where(
            ProcessedWebhookEventsTable.event_id == event_id
        )
        event = self.db.scalars(statement=stmt).first()

        return event

    def create_webhook_events(self, event_id: str) -> ProcessedWebhookEventsTable:
        new_event = ProcessedWebhookEventsTable(
            event_id=event_id, processed_at=datetime.now(UTC)
        )
        self.db.add(new_event)
        self.db.flush()
        self.db.refresh(new_event)

        return new_event
