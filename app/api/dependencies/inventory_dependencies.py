from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.skin_repository import SkinsRepository
from app.services.inventory_service import InventoryService


def get_inventory_service(
    db: Session = Depends(get_db),  # noqa: B008
) -> InventoryService:
    skin_repo = SkinsRepository(db=db)
    inventory_repo = InventoryRepository(db=db)
    return InventoryService(skin_repo=skin_repo, inventory_repo=inventory_repo, db=db)
