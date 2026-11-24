from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import CartItemsTable, CartsTable


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_cart_by_user_id(self, user_id: int) -> CartsTable | None:
        stmt = select(CartsTable).where(CartsTable.user_id == user_id)
        return self.db.scalars(statement=stmt).first()

    def create_cart(self, user_id: int) -> CartsTable:
        new = CartsTable(
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            user_id=user_id,
        )

        self.db.add(new)
        self.db.flush()
        self.db.refresh(new)

        return new

    def get_cart_item(self, cart_id: int, skin_id: int) -> CartItemsTable | None:
        stmt = select(CartItemsTable).where(
            CartItemsTable.skin_id == skin_id, CartItemsTable.cart_id == cart_id
        )

        return self.db.scalars(statement=stmt).first()

    def add_item(self, cart_id: int, skin_id: int, quantity: int) -> CartItemsTable:
        new = CartItemsTable(cart_id=cart_id, skin_id=skin_id, quantity=quantity)

        self.db.add(new)
        self.db.flush()
        self.db.refresh(new)

        return new

    def update_item_quantity(
        self, item: CartItemsTable, quantity: int
    ) -> CartItemsTable:
        item.quantity = quantity

        self.db.flush()

        return item

    def delete_item(self, item: CartItemsTable) -> None:

        self.db.delete(item)

    def delete_all_items(self, cart: CartsTable) -> CartsTable:
        cart.items = []

        self.db.flush()
        self.db.refresh(cart)

        return cart
