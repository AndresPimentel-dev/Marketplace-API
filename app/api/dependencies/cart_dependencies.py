from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.cart_repository import CartRepository
from app.repositories.skin_repository import SkinsRepository
from app.services.cart_service import CartService


def get_cart_service(db: Session = Depends(get_db)) -> CartService:  # noqa: B008
    cart_repo = CartRepository(db=db)
    skin_repo = SkinsRepository(db=db)
    return CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=db)
