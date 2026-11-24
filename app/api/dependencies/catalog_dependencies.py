from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.skin_repository import SkinsRepository
from app.services.catalog_service import CatalogService


def get_catalog_service(
    db: Session = Depends(get_db),  # noqa: B008
) -> CatalogService:
    skin_repo = SkinsRepository(db=db)
    return CatalogService(repository=skin_repo, db=db)
