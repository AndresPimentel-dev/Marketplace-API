from fastapi import APIRouter, Depends

from app.api.dependencies.auth_dependencies import get_current_user
from app.api.dependencies.cart_dependencies import get_cart_service
from app.models.models import UsersTable
from app.schemas.cart import (
    CartItemCreate,
    CartItemResponse,
    CartResponse,
    UpdateItemQuantity,
)
from app.services.cart_service import CartService

router = APIRouter(prefix="/api/v5.0", tags=["Cart"])


@router.post("/cart/items", status_code=200, response_model=CartItemResponse)
def add_skin_to_cart(
    data: CartItemCreate,
    cart_service: CartService = Depends(get_cart_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> CartItemResponse:

    return cart_service.add_item_to_cart(user_id=current_user.id, data=data)


@router.get("/cart", status_code=200, response_model=CartResponse)
def get_cart_user(
    cart_service: CartService = Depends(get_cart_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> CartResponse:

    return cart_service.get_user_cart(user_id=current_user.id)


@router.patch("/cart/items/{skin_id}", status_code=200, response_model=CartItemResponse)
def update_amount_skin(
    skin_id: int,
    data: UpdateItemQuantity,
    cart_service: CartService = Depends(get_cart_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> CartItemResponse:
    return cart_service.update_item(user_id=current_user.id, skin_id=skin_id, data=data)


@router.delete("/cart/items/{skin_id}", status_code=204)
def delete_item(
    skin_id: int,
    cart_service: CartService = Depends(get_cart_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> None:
    cart_service.delete_item(user_id=current_user.id, skin_id=skin_id)


@router.delete("/cart/items", status_code=204)
def empty_cart(
    cart_service: CartService = Depends(get_cart_service),  # noqa: B008
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> None:

    return cart_service.empy_cart(user_id=current_user.id)
