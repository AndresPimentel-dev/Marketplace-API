from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.core.exceptions import BadRequestException, NotFoundException
from app.models.models import CartItemsTable, CartsTable
from app.repositories.cart_repository import CartRepository
from app.repositories.skin_repository import SkinsRepository
from app.schemas.cart import CartItemCreate, UpdateItemQuantity


class CartService:
    def __init__(
        self, cart_repo: CartRepository, skin_repo: SkinsRepository, db: Session
    ):
        self.skin_repo = skin_repo
        self.cart_repo = cart_repo
        self.db = db

    def get_user_cart(self, user_id: int) -> CartsTable:
        cart = self.cart_repo.get_cart_by_user_id(user_id=user_id)
        if cart is None:
            raise NotFoundException(message="Cart not found")

        return cart

    def add_item_to_cart(self, user_id: int, data: CartItemCreate) -> CartItemsTable:
        cart = self.cart_repo.get_cart_by_user_id(user_id=user_id)
        if cart is None:
            cart = self.cart_repo.create_cart(user_id=user_id)
        skin = self.skin_repo.get_active_skin_by_id(skin_id=data.skin_id)
        if skin is None:
            raise NotFoundException(message="Skin Not found")

        available_stock = skin.stock_total - skin.stock_sold - skin.stock_reserved
        if data.quantity > available_stock:
            raise BadRequestException(message="there is not enough stock")

        item = self.cart_repo.get_cart_item(cart_id=cart.id, skin_id=data.skin_id)
        if item:
            cart.updated_at = datetime.now(UTC)
            return self.cart_repo.update_item_quantity(
                item=item, quantity=data.quantity
            )
        cart.updated_at = datetime.now(UTC)
        new = self.cart_repo.add_item(
            cart_id=cart.id, skin_id=data.skin_id, quantity=data.quantity
        )
        self.db.commit()
        return new

    def update_item(
        self, user_id: int, skin_id: int, data: UpdateItemQuantity
    ) -> CartItemsTable:
        cart = self.cart_repo.get_cart_by_user_id(user_id=user_id)
        if cart is None:
            raise NotFoundException(message="Cart not found")
        item = self.cart_repo.get_cart_item(cart_id=cart.id, skin_id=skin_id)
        if item is None:
            raise NotFoundException("Item not found")
        skin = self.skin_repo.get_active_skin_by_id(skin_id=item.skin_id)

        available_stock = skin.stock_total - skin.stock_sold - skin.stock_reserved
        if data.quantity > available_stock:
            raise BadRequestException(message="there is not enough stock")

        to_update = self.cart_repo.update_item_quantity(
            item=item, quantity=data.quantity
        )
        cart.updated_at = datetime.now(UTC)
        self.db.commit()

        return to_update

    def delete_item(self, user_id: int, skin_id: int) -> None:
        cart = self.cart_repo.get_cart_by_user_id(user_id=user_id)
        if cart is None:
            raise NotFoundException(message="Cart not found")
        item = self.cart_repo.get_cart_item(cart_id=cart.id, skin_id=skin_id)
        if item is None:
            raise NotFoundException(message="Item not found")
        self.cart_repo.delete_item(item=item)
        cart.updated_at = datetime.now(UTC)
        self.db.commit()

    def empy_cart(self, user_id: int) -> CartsTable | None:
        cart = self.cart_repo.get_cart_by_user_id(user_id=user_id)
        if cart is None:
            raise NotFoundException(message="Cart not found")

        to_delete = self.cart_repo.delete_all_items(cart=cart)
        self.db.commit()
        return to_delete
