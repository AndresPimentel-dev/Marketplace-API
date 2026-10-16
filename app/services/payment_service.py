from datetime import UTC, datetime

from prometheus_client import Counter
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    NotFoundException,
)
from app.core.logging import logger
from app.models.models import InventoryItemsTable, OrdersStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.skin_repository import SkinsRepository

PAYMENT_COUNTER = Counter(
    "Successfull payments counter", "payment counter", ["status", "description", "id"]
)


class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        order_repo: OrderRepository,
        skin_repo: SkinsRepository,
        db: Session,
    ):
        self.payment_repo = payment_repo
        self.order_repo = order_repo
        self.skin_repo = skin_repo
        self.db = db

    def process_payment_webhook(
        self, event_id: str, payment_id: str, order_id: int, status: str
    ) -> dict:
        # 1. VERIFICAR IDEMPOTENCIA
        if self.payment_repo.is_event_processed(event_id=event_id):
            logger.error(
                "Webhook already processed, ignoring duplicate",
                extra={
                    "props": {"event_type": "webhook.ignored", "event_id": event_id}
                },
            )
            return {
                "status": "already_processed",
                "message": "Webhook event already handled.",
            }

        # 2. BUSCAR LA ORDEN
        order = self.order_repo.get_order_by_id(order_id=order_id)
        if not order:
            raise NotFoundException(message=f"Order not found: {order_id}")

        if order.status != OrdersStatus.PENDING_PAYMENT:
            raise BadRequestException(
                message={
                    "status": "ignored",
                    "message": f"Order is already in state: {order.status}",
                }
            )

        # 3. PROCESAR SEGÚN EL ESTADO DEL PAGO
        if status == "succeeded":
            order.status = OrdersStatus.PAYMENT_CONFIRMED
            order.updated_at = datetime.now(UTC)

            # Actualizar stock (quitar de reservado, sumar a vendido) y entregar al inventario
            for item in order.items:
                skin = self.skin_repo.get_skin_with_lock(item.skin_id)
                if skin:
                    skin.stock_reserved -= item.quantity
                    skin.stock_sold += item.quantity

                    # Crear el item en el inventario del usuario
                    for _ in range(item.quantity):
                        inventory_item = InventoryItemsTable(
                            user_id=order.user_id,
                            skin_id=skin.id,
                            order_id=order.id,
                            acquired_at=datetime.now(UTC),
                        )
                        self.db_add_inventory(
                            inventory_item
                        )  # O tu método para añadir al inventario

        elif status == "failed":
            order.status = OrdersStatus.PAYMENT_FAILED
            order.updated_at = datetime.now(UTC)

            # Liberar stock reservado (rollback de stock)
            for item in order.items:
                skin = self.skin_repo.get_skin_with_lock(item.skin_id)
                logger.error(
                    "Payment failed, releasing stock reservation",
                    extra={
                        "props": {
                            "event_type": "payment.failed",
                            "order_id": order_id,
                            "payment_id": payment_id,
                        }
                    },
                )
                if skin:
                    skin.stock_reserved -= item.quantity

        else:
            raise BadRequestException(f"Unknown payment status: {status}")

        # 4. MARCAR EVENTO COMO PROCESADO PARA IDEMPOTENCIA
        self.payment_repo.mark_event_as_processed(
            event_id=event_id, event_type=f"payment_{status}"
        )
        PAYMENT_COUNTER.labels(
            "successfull payment", "payment completed", payment_id
        ).inc()
        logger.info(
            "Payment successful, skin delivered to inventory",
            extra={
                "props": {
                    "event_type": "payment.completed",
                    "order_id": order_id,
                    "payment_id": payment_id,
                }
            },
        )
        return {
            "status": "success",
            "message": f"Webhook processed successfully for order {order_id}",
        }
