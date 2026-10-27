from datetime import UTC, datetime

from app.core.logging import logger
from app.db.session import SessionLocal
from app.models.models import OrdersStatus, OrdersTable, SkinsTable
from app.worker.celery_app import celery_app


@celery_app.task(name="expire_stale_reservations")
def expire_stale_reservations():
    """
    Busca órdenes pendientes que ya superaron su tiempo límite,
    libera el stock reservado y marca la orden como CANCELLED o EXPIRED.
    """
    db = SessionLocal()
    try:
        now = datetime.now(UTC)

        # 1. Buscar órdenes vencidas en estado PENDING_PAYMENT
        stale_orders = (
            db.query(OrdersTable)
            .filter(
                OrdersTable.status == OrdersStatus.PENDING_PAYMENT,
                OrdersTable.expires_at < now,
            )
            .all()
        )

        if not stale_orders:
            return "No stale reservations found."

        for order in stale_orders:
            # 2. Cambiar estado de la orden a CANCELLED
            order.status = OrdersStatus.CANCELLED
            order.updated_at = now

            # 3. Devolver el stock reservado a las skins
            for item in order.items:
                skin = (
                    db.query(SkinsTable).filter(SkinsTable.id == item.skin_id).first()
                )
                if skin:
                    # Liberamos el stock reservado evitando valores negativos
                    skin.stock_reserved = max(0, skin.stock_reserved - item.quantity)
                    skin.updated_at = now

            logger.info(
                "Stock reservation expired",
                extra={
                    "props": {
                        "event_type": "stock.reservation_expired",
                        "order_id": order.id,
                    }
                },
            )

        # 4. Guardar cambios en la base de datos
        db.commit()
        return f"Successfully expired {len(stale_orders)} orders."

    except Exception as e:
        db.rollback()
        logger.error(f"Error expiring reservations: {e}")
        raise
    finally:
        db.close()
