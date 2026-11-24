from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.models import SkinsTable
from app.repositories.skin_repository import SkinsRepository
from app.schemas.enums import SkinCategory, SkinCurrency, SkinRarity
from app.schemas.skin import SkinCreate, SkinUpdate


class CatalogService:
    def __init__(self, repository: SkinsRepository, db: Session):
        self.repository = repository
        self.db = db

    def create_skin(self, skin_data: SkinCreate) -> SkinsTable:
        new = self.repository.create_skin(skin_data)
        if new is None:
            raise ConflictException(message="Slug already used")
        self.db.commit()
        return new

    def get_skin_by_slug(self, slug: str) -> SkinsTable:
        skin = self.repository.get_skin_by_slug(slug)
        if skin is None:
            raise NotFoundException(message="Skin not found")

        return skin

    def get_skin_by_id(self, skin_id: int) -> SkinsTable:
        skin = self.repository.get_active_skin_by_id(skin_id=skin_id)
        if skin is None:
            raise NotFoundException(message="Skin not found")
        return skin

    def update_skin(self, skin_id: int, skin_data: SkinUpdate) -> SkinsTable:
        to_update = self.repository.update_skin(skin_id, skin_data)
        if to_update is None:
            raise NotFoundException(message="Skin not found")
        self.db.commit()

        return to_update

    def deactivate_skin(self, skin_id: int) -> SkinsTable:
        to_deactivate = self.repository.deactivate_skin_by_id(skin_id)
        if to_deactivate is None:
            raise NotFoundException(message="Skin not found")
        self.db.commit()

        return to_deactivate

    def activate_skin(self, skin_id: int) -> SkinsTable:
        to_activate = self.repository.activate_skin_by_id(skin_id=skin_id)
        if to_activate is None:
            raise NotFoundException(message="Skin not found")
        self.db.commit()

        return to_activate

    def get_skins(
        self,
        category: SkinCategory | None = None,
        rarity: SkinRarity | None = None,
        currency: SkinCurrency | None = None,
        is_limited: bool | None = None,
        page: int = 1,
        page_size: int = 10,
    ) -> list[SkinsTable]:

        # El servicio simplemente delega al repositorio

        return self.repository.get_skins(
            category=category,
            rarity=rarity,
            currency=currency,
            is_limited=is_limited,
            page=page,
            page_size=page_size,
        )
