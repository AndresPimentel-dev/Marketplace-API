from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.skin_repository import (
    SkinsRepository,
)  # Para verificar si la skin existe y su propiedad stackable


class InventoryService:
    def __init__(
        self,
        skin_repo: SkinsRepository,
        inventory_repo: InventoryRepository,
        db: Session,
    ):
        self.inventory_repo = inventory_repo
        self.skin_repo = skin_repo
        self.db = db

    def get_user_inventory(self, user_id: int):
        return self.inventory_repo.get_user_inventory(user_id)

    def get_inventory_item(self, inventory_item_id: int, user_id: int):
        item = self.inventory_repo.get_by_id(inventory_item_id, user_id)
        if not item:
            raise NotFoundException(message="El item de inventario no existe.")
        return item

    def deliver_skin(self, user_id: int, skin_id: int, order_id: int):
        # 1. Verificar que la skin exista
        skin = self.skin_repo.get_by_id(skin_id)
        if not skin:
            raise NotFoundException(message="Skin not found")

        # 2. Validar reglas de unicidad o stackable
        self.inventory_repo.get_by_user_and_skin(user_id, skin_id)
        new_item = self.inventory_repo.create(
            user_id=user_id, skin_id=skin_id, order_id=order_id
        )
        self.db.commit()

        return new_item
