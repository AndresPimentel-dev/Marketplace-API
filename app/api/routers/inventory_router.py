from fastapi import APIRouter, Depends, status

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.inventory_dependencies import get_inventory_service
from app.models.models import UsersTable
from app.schemas.inventory import InventoryItemResponse
from app.services.inventory_service import InventoryService

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get(
    "/user/", response_model=list[InventoryItemResponse], status_code=status.HTTP_200_OK
)
def get_user_inventory(
    user_id: int,
    service: InventoryService = Depends(get_inventory_service),  # noqa: B008
    current: UsersTable = Depends(get_current_user),  # noqa: B008
):

    return service.get_user_inventory(current.id)


@router.get(
    "/{inventory_item_id}",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_200_OK,
)
def get_inventory_item(
    inventory_item_id: int,
    service: InventoryService = Depends(get_inventory_service),  # noqa: B008
    current: UsersTable = Depends(get_current_user),  # noqa: B008
):

    return service.get_inventory_item(inventory_item_id, user_id=current.id)
