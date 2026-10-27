from fastapi import APIRouter, Depends, Query

from app.api.dependencies.auth_dependencies import require_admin
from app.api.dependencies.catalog_dependencies import get_catalog_service
from app.models.models import UsersTable
from app.schemas.enums import SkinCategory, SkinCurrency, SkinRarity
from app.schemas.skin import SkinCreate, SkinListResponse, SkinResponse, SkinUpdate
from app.services.catalog_service import CatalogService

router = APIRouter(prefix="/api/v5.0", tags=["Catalog"])

# =====================================
#      ENDPOINTS DE CATALOGO USERS
# =====================================


@router.get("/skins", status_code=200, response_model=SkinListResponse)
def get_skins(
    catalog_service: CatalogService = Depends(get_catalog_service),  # noqa: B008
    category: SkinCategory | None = None,
    rarity: SkinRarity | None = None,
    currency: SkinCurrency | None = None,
    is_limited: bool | None = None,
    # validamos el page y el page size
    page: int = Query(1, ge=1, description="Numero de pagina minimo 1"),
    page_size: int = Query(10, ge=1, le=50, description="Elementos por pagina"),
) -> SkinListResponse:

    skins = catalog_service.get_skins(
        category=category,
        rarity=rarity,
        currency=currency,
        is_limited=is_limited,
        page=page,
        page_size=page_size,
    )
    # aqui lo hacemos explicito po mypy pero ya lo hacia pidantic solo
    return SkinListResponse.model_validate({"skins": skins})


@router.get("/skins/{skin_id}", status_code=200, response_model=SkinResponse)
def get_skin_by_id_route(
    skin_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service),  # noqa: B008
) -> SkinResponse:

    return catalog_service.get_skin_by_id(skin_id=skin_id)


# =====================================
#      ENDPOINTS DE CATALOGO Admin
# =====================================


@router.post("/admin/skins", status_code=201, response_model=SkinResponse)
def create_skin_by_admin(
    skin_data: SkinCreate,
    catalog_service: CatalogService = Depends(get_catalog_service),  # noqa: B008
    admin: UsersTable = Depends(require_admin),  # noqa: B008
) -> SkinResponse:
    return catalog_service.create_skin(skin_data=skin_data)


@router.patch("/admin/skins/{skin_id}", status_code=200, response_model=SkinResponse)
def update_skin_by_admin(
    skin_id: int,
    skin_data: SkinUpdate,
    catalog_service: CatalogService = Depends(get_catalog_service),  # noqa: B008
    admin: UsersTable = Depends(require_admin),  # noqa: B008
) -> SkinResponse:

    return catalog_service.update_skin(skin_id=skin_id, skin_data=skin_data)


@router.patch(
    "/admin/skins/{skin_id}/activate", status_code=200, response_model=SkinResponse
)
def activate_skin_by_admin(
    skin_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service),  # noqa: B008
    admin: UsersTable = Depends(require_admin),  # noqa: B008
) -> SkinResponse:

    return catalog_service.activate_skin(skin_id=skin_id)


# en realidad solo desactiva una skin
@router.delete("/admin/skins/{skin_id}", status_code=204)
def deactivate_skin_by_admin(
    skin_id: int,
    catalog_service: CatalogService = Depends(get_catalog_service),  # noqa: B008
    admin: UsersTable = Depends(require_admin),  # noqa: B008
) -> None:

    return catalog_service.deactivate_skin(skin_id=skin_id)
