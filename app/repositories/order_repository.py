from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import OrdersTable
from app.schemas.enums import OrderStatus


class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_order_by_id(self, order_id: int) -> OrdersTable | None:
        stmt = select(OrdersTable).where(OrdersTable.id == order_id)

        return self.db.scalars(statement=stmt).first()

    def get_orders_associated_to_user_id(
        self, user_id: int, page: int = 1, page_size: int = 10
    ) -> list[OrdersTable]:
        stmt = select(OrdersTable).where(OrdersTable.user_id == user_id)
        offset = (page - 1) * page_size
        stmt = stmt.limit(page_size).offset(offset)

        return self.db.scalars(statement=stmt).all()

    def update_order_status(
        self, order: OrdersTable, new_status: OrderStatus
    ) -> OrdersTable:
        order.status = new_status
        order.updated_at = datetime.now(UTC)

        self.db.flush()
        self.db.refresh(order)

        return order

    def create_order(self, order: OrdersTable) -> OrdersTable:

        self.db.add(order)
        self.db.flush()
        self.db.refresh(order)

        return order
