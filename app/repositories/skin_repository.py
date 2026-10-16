from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import SkinsTable
from app.schemas.enums import SkinCategory, SkinCurrency, SkinRarity
from app.schemas.skin import SkinCreate, SkinUpdate


class SkinsRepository:
    def __init__(self, db: Session):
        self.db = db

    # esto puede devolver el objeto o none asi que los dos en el hit
    def create_skin(self, skin_data: SkinCreate) -> SkinsTable | None:
        stmt = select(SkinsTable).where(SkinsTable.slug == skin_data.slug)
        existing = self.db.scalars(stmt).first()
        if existing:
            return None
        new = SkinsTable(
            name=skin_data.name,
            slug=skin_data.slug,
            description=skin_data.description,
            category=skin_data.category,
            rarity=skin_data.rarity,
            price=skin_data.price,
            currency=skin_data.currency,
            stock_total=skin_data.stock_total,
            is_limited=skin_data.is_limited,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.db.add(new)
        self.db.flush()
        self.db.refresh(new)

        return new

    def get_active_skin_by_id(self, skin_id: int) -> SkinsTable | None:
        stmt = select(SkinsTable).where(SkinsTable.id == skin_id, SkinsTable.is_active)
        skin = self.db.scalars(stmt).first()
        if skin is None:
            return None

        return skin

    def get_skin_by_slug(self, slug: str) -> SkinsTable | None:
        stmt = select(SkinsTable).where(SkinsTable.slug == slug, SkinsTable.is_active)
        skin = self.db.scalars(stmt).first()
        if skin is None:
            return None

        return skin

    def update_skin(self, skin_id: int, skin_data: SkinUpdate) -> SkinsTable | None:
        stmt = select(SkinsTable).where(SkinsTable.id == skin_id)
        to_update = self.db.scalars(stmt).first()
        if to_update is None:
            return None
        update_data = skin_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(to_update, key, value)

        to_update.updated_at = datetime.now(UTC)

        return to_update

    def deactivate_skin_by_id(self, skin_id: int) -> SkinsTable | None:
        stmt = select(SkinsTable).where(SkinsTable.id == skin_id)
        to_deactivate = self.db.scalars(stmt).first()
        if to_deactivate is None:
            return None
        to_deactivate.is_active = False

        return to_deactivate

    def activate_skin_by_id(self, skin_id: int) -> SkinsTable | None:
        stmt = select(SkinsTable).where(
            SkinsTable.id == skin_id, SkinsTable.is_active == False
        )
        to_activate = self.db.scalars(stmt).first()
        if to_activate is None:
            return None
        to_activate.is_active = True

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
        # 1. Consulta base: Empezamos trayendo solo las skins activas
        # los stmt se acumulan para devolver una consulta con muchos parametros
        stmt = select(SkinsTable).where(SkinsTable.is_active)

        # 2. Aplicar filtros dinámicos con condicionales de Python
        if category is not None:
            stmt = stmt.where(SkinsTable.category == category)

        if rarity is not None:
            stmt = stmt.where(SkinsTable.rarity == rarity)

        if currency is not None:
            stmt = stmt.where(SkinsTable.currency == currency)

        if is_limited is not None:
            stmt = stmt.where(SkinsTable.is_limited == is_limited)

        # 3. Calcular la Paginación (Offset y Limit)
        # Fórmula: offset = (page - 1) * page_size
        offset = (page - 1) * page_size

        stmt = stmt.limit(page_size).offset(offset)

        # 4. Ejecutar la consulta y devolver los resultados
        return list(self.db.scalars(stmt).all())

    # bloquea la skin par aque no se use si ya esta para otra operacion
    def get_skin_with_lock(self, skin_id: int) -> SkinsTable | None:
        # con el with update se bloquea la consulta a la misma skin por si depronto
        # ya esta en un proceso de compra no la pueda haceer otro user
        stmt = select(SkinsTable).where(SkinsTable.id == skin_id).with_for_update()
        return self.db.scalars(stmt).first()

    # ==================================================
    # no se borran skins ya que se supone deben quedar en historicos y inventarios
    # ===================================================
