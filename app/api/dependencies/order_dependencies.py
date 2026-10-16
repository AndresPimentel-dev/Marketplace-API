from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.cart_repository import CartRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.skin_repository import SkinsRepository
from app.services.order_service import OrderService


def get_order_service(db: Session = Depends(get_db)):  # noqa: B008
    order_repo = OrderRepository(db=db)
    skin_repo = SkinsRepository(db=db)
    cart_repo = CartRepository(db=db)
    return OrderService(
        skin_repo=skin_repo, cart_repo=cart_repo, order_repo=order_repo, db=db
    )
