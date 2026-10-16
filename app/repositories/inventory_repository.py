from datetime import UTC, datetime

from sqlalchemy.orm import Session

# Ajusta la importación de tu modelo InventoryItemsTable según la estructura de tu proyecto
from app.models.models import InventoryItemsTable


class InventoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_inventory(self, user_id: int) -> list[InventoryItemsTable]:

        return (
            self.db.query(InventoryItemsTable)
            .filter(InventoryItemsTable.user_id == user_id)
            .all()
        )

    def get_by_id(
        self, inventory_item_id: int, user_id: int
    ) -> InventoryItemsTable | None:

        return (
            self.db.query(InventoryItemsTable)
            .filter(
                InventoryItemsTable.id == inventory_item_id,
                InventoryItemsTable.user_id == user_id,
            )
            .first()
        )

    def get_by_user_and_skin(
        self, user_id: int, skin_id: int
    ) -> InventoryItemsTable | None:

        return (
            self.db.query(InventoryItemsTable)
            .filter(
                InventoryItemsTable.user_id == user_id,
                InventoryItemsTable.skin_id == skin_id,
            )
            .first()
        )

    def create(self, user_id: int, skin_id: int, order_id: int) -> InventoryItemsTable:

        inventory_item = InventoryItemsTable(
            user_id=user_id,
            skin_id=skin_id,
            order_id=order_id,
            acquired_at=datetime.now(UTC),
        )
        self.db.add(inventory_item)
        self.db.flush()
        self.db.refresh(inventory_item)
        return inventory_item

    def db_add_inventory(self, inventory_item: InventoryItemsTable):
        # Ayudante interno para añadir al inventario (puedes moverlo a un inventory_repository si prefieres)
        self.db.add(inventory_item)
        self.db.flush()
        self.db.refresh(inventory_item)
