from datetime import UTC, datetime

from prometheus_client import Counter
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.core.logging import logger
from app.models.models import InventoryItemsTable, OrdersStatus, PaymentStatus
from app.repositories.order_repository import OrderRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.skin_repository import SkinsRepository
from app.repositories.webhook_events_repository import WebhookEventsRepository

PAYMENT_COUNTER = Counter("payments_total", "Total payments processed", ["status"])


class PaymentService:
    def __init__(
        self,
        payment_repo: PaymentRepository,
        order_repo: OrderRepository,
        skin_repo: SkinsRepository,
        webhook_repo: WebhookEventsRepository,
        db: Session,
    ):
        self.payment_repo = payment_repo
        self.order_repo = order_repo
        self.skin_repo = skin_repo
        self.webhook_repo = webhook_repo
        self.db = db

    def process_payment_webhook(
        self, event_id: str, payment_id: str, order_id: int, status: str
    ) -> dict:

        # 1. VERIFICAR IDEMPOTENCIA
        try:
            self.webhook_repo.create_webhook_events(event_id)
        except IntegrityError:
            raise ConflictException("event already processed")
        try:
            # 2. BUSCAR LA ORDEN
            order = self.order_repo.get_order_with_lock_by_id(order_id=order_id)
            if not order:
                raise NotFoundException(message=f"Order not found: {order_id}")

            if order.status != OrdersStatus.PENDING_PAYMENT:
                raise BadRequestException(
                    message=f"Order is already in state: {order.status}"
                )

            # Validar si la orden ha expirado
            now = datetime.now(UTC)
            if order.expires_at:
                order_expires_at = order.expires_at
                if order_expires_at.tzinfo is None:
                    order_expires_at = order_expires_at.replace(tzinfo=UTC)
                if now > order_expires_at:
                    order.status = OrdersStatus.CANCELLED
                    order.updated_at = now
                    for item in order.items:
                        skin = self.skin_repo.get_skin_with_lock(item.skin_id)
                        logger.error(
                            "Payment cancelled, releasing stock reservation",
                            extra={
                                "props": {
                                    "event_type": "payment.failed",
                                    "order_id": order_id,
                                    "payment_id": payment_id,
                                }
                            },
                        )
                        if skin:
                            skin.stock_reserved = max(
                                0, skin.stock_reserved - item.quantity
                            )
                            skin.updated_at = now
                    self.db.commit()
                    raise BadRequestException(message="Order has expired")

            # 3. VALIDAR IDENTIFICADOR DE PAGO
            payment = self.payment_repo.get_payment_by_payment_id(payment_id=payment_id)
            if payment is None:
                raise NotFoundException("payment not found")
            if payment and payment.order_id != order.id:
                raise BadRequestException(
                    message=f"Payment ID {payment_id} does not belong to order {order_id}"
                )

            # 4. PROCESAR SEGÚN EL ESTADO DEL PAGO
            if status == "succeeded":
                order.status = OrdersStatus.PAYMENT_CONFIRMED
                order.updated_at = now

                if payment:
                    payment.status = PaymentStatus.SUCCEEDED
                    payment.updated_at = now

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
                                acquired_at=now,
                            )
                            self.db.add(inventory_item)

            elif status == "failed":
                order.status = OrdersStatus.PAYMENT_FAILED
                order.updated_at = now

                if payment:
                    payment.status = PaymentStatus.FAILED
                    payment.updated_at = now

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
                        skin.stock_reserved = max(
                            0, skin.stock_reserved - item.quantity
                        )
                        skin.updated_at = now

            else:
                raise BadRequestException(f"Unknown payment status: {status}")

            # 4. MARCAR EVENTO COMO PROCESADO PARA IDEMPOTENCIA
            self.payment_repo.mark_event_as_processed(
                event_id=event_id, event_type=f"payment_{status}"
            )
            PAYMENT_COUNTER.labels(status=status).inc()
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
            self.db.commit()
            return {
                "status": "success",
                "message": f"Webhook processed successfully for order {order_id}",
            }
        except (BadRequestException, NotFoundException, Exception, IntegrityError) as e:
            # 3. ¡SALVAVIDAS CRUCIAL!
            # Pase lo que pase (error de negocio o error inesperado),
            # limpiamos la transacción y LIBERAMOS EL BLOQUEO FOR UPDATE.
            self.db.rollback()

            # Opcional: loguear el error si es necesario
            logger.error(f"Error procesando webhook, haciendo rollback: {e!s}")

            # Volvemos a lanzar la excepción para que el framework responda con el 400, 404, etc.
            raise