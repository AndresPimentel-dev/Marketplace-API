from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import Enum

from prometheus_client import Counter
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.core.logging import logger
from app.models.models import OrdersItemsTable, OrdersTable
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.skin_repository import SkinsRepository
from app.tasks.reservation_task import expire_stale_reservations


class OrdersStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_FAILED = "payment_failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


ORDERS_COUNTER = Counter(
    "total orders created",
    "orders created counter",
    ["status", "description", "order_id"],
)
WORKER_COUNTER = Counter(
    "total tasks created",
    "tasks created counter",
    ["status", "description", "order_id"],
)
STOCK_RESERVATION_FAILURES_TOTAL = Counter(
    "total failed reservations",
    "failures counter",
    ["status", "description", "skin_id"],
)


class OrderService:
    def __init__(
        self,
        skin_repo: SkinsRepository,
        cart_repo: CartRepository,
        order_repo: OrderRepository,
        db: Session,
    ):
        self.skin_repo = skin_repo
        self.cart_repo = cart_repo
        self.order_repo = order_repo
        self.db = db

    def create_order(self, user_id: int) -> OrdersTable:
        cart = self.cart_repo.get_cart_by_user_id(user_id=user_id)
        if cart is None or cart.items == []:
            raise ConflictException("Cart Not Found or Empty")
        currency = (
            self.skin_repo.get_active_skin_by_id(cart.items[0].skin_id)
        ).currency
        order_items = []
        total_amount = Decimal("0.00")
        for item in cart.items:
            skin = self.skin_repo.get_skin_with_lock(item.skin_id)
            # valida que la skin este activa o exista si no error
            if skin is None:
                raise BadRequestException(message=f"Not active skin: {skin}")
            # valida que todas las skins esten en la mismas currency para que no
            # haya problemas de paso
            if skin.currency != currency:
                raise BadRequestException(message="Cannot process different currencies")
            # valida que la skin tenga stock para poder crear la orden si no hay st
            available_stock = skin.stock_total - skin.stock_sold - skin.stock_reserved
            if skin.is_limited and available_stock < item.quantity:
                STOCK_RESERVATION_FAILURES_TOTAL.labels(
                    "failed", "Insufficient stock for skin", skin.id
                ).inc()
                raise BadRequestException(message="Insufficient stock for skin")
            # aumenta el stock reservado
            skin.stock_reserved += item.quantity
            subtotal = skin.price * item.quantity
            order_item = OrdersItemsTable(
                skin_id=skin.id,
                quantity=item.quantity,
                unit_price=skin.price,
                subtotal=subtotal,
            )
            order_items.append(order_item)
            total_amount += subtotal

        order = OrdersTable(
            status=OrdersStatus.PENDING_PAYMENT,
            total_amount=total_amount,
            currency=currency,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            user_id=user_id,
            items=order_items,
        )
        self.cart_repo.delete_all_items(cart=cart)
        new_order = self.order_repo.create_order(order=order)
        # aqui se envia la tarea a redis con la etiqueta de que se ejecute en 600
        expire_stale_reservations.apply_async(countdown=600)
        self.db.commit()
        ORDERS_COUNTER.labels("created", "order created correctly", new_order.id).inc()
        WORKER_COUNTER.labels("created", "task created correctly", new_order.id).inc()
        logger.info(
            "Order created and stock reserved",
            extra={
                "props": {
                    "event_type": "order.created",
                    "order_id": new_order.id,
                    "user_id": user_id,
                }
            },
        )
        return new_order

    def get_order(self, user_id: int, order_id: int) -> OrdersTable:
        order = self.order_repo.get_order_by_id(order_id=order_id)
        if order is None or order.user_id != user_id:
            raise ConflictException(message="Not Found or Unauthorized")

        return order

    def get_user_orders(self, user_id: int, page: int = 1, page_size: int = 10):
        return self.order_repo.get_orders_associated_to_user_id(
            user_id=user_id, page=page, page_size=page_size
        )

    def update_order_status(
        self, order_id: int, new_status: OrdersStatus
    ) -> OrdersTable:
        order = self.order_repo.get_order_by_id(order_id=order_id)
        if order is None:
            raise NotFoundException(message="Order not found")
        to_update = self.order_repo.update_order_status(
            order=order, new_status=new_status
        )
        self.db.commit()

        return to_update
