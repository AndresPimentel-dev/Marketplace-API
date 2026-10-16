from datetime import datetime

from app.core.logging import logger
from app.db.session import SessionLocal
from app.models.models import OrdersStatus, OrdersTable, SkinsTable
from app.worker.celery_app import celery_app


@celery_app.task(name="expire_stale_reservations")
def expire_stale_reservations():
    """
    Busca órdenes pendientes que ya superaron su tiempo límite,
    libera el stock reservado y marca la orden como EXPIRED.
    """
    db = SessionLocal()
    try:
        now = datetime.now

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
            # 2. Cambiar estado de la orden a EXPIRED
            order.status = OrdersStatus.EXPIRED

            # 3. Devolver el stock reservado a las skins
            for item in order.items:
                skin = (
                    db.query(SkinsTable).filter(SkinsTable.id == item.skin_id).first()
                )
                if skin and skin.is_limited:
                    # Liberamos el stock reservado
                    skin.stock_reserved -= item.quantity

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
        logger.error("Error expiring reservations", extra=str(e))
        raise
    finally:
        db.close()  # Importante cerrar la sesión de base de datos del worker
