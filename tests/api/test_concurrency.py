from datetime import UTC, datetime
from unittest.mock import patch

from app.core.security import create_access_token
from app.models.models import (
    SkinCategory,
    SkinCurrency,
    SkinRarity,
    SkinsTable,
    UsersTable,
)


def test_concurrency_create_order_endpoint(get_db_test, cliente):
    """agregamos los dos usuarios que competiran por agregar objetos
    al carro y tambien la skin a competir"""
    user_1 = UsersTable(
        email="fakeemaildeuser1@gmail.com",
        hashed_password="asjdbjhasvdas",
        created_at=datetime.now(UTC),
    )
    user_2 = UsersTable(
        email="fakeemaiasdfldeuser1@gmail.com",
        hashed_password="asasfasdfjdbjhasvdas",
        created_at=datetime.now(UTC),
    )
    skin = SkinsTable(
        name="nombre",
        slug="slug al azar",
        description="skin nueva",
        category=SkinCategory.BANNER,
        rarity=SkinRarity.COMMON,
        price=11.15,
        currency=SkinCurrency.DOLLARS,
        stock_total=5,
        is_limited=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    get_db_test.add(user_2)
    get_db_test.add(user_1)
    get_db_test.add(skin)
    get_db_test.commit()
    get_db_test.refresh(user_2)
    get_db_test.refresh(user_1)
    get_db_test.refresh(skin)

    payload = {"skin_id": skin.id, "quantity": 5}
    token_user_1 = create_access_token(data={"sub": user_1.email})
    cliente.post(
        "/api/v5.0/cart/items",
        json=payload,
        headers={"Authorization": f"Bearer {token_user_1}"},
    )
    token_user_2 = create_access_token(data={"sub": user_2.email})
    cliente.post(
        "/api/v5.0/cart/items",
        json={"skin_id": skin.id, "quantity": 5},
        headers={"Authorization": f"Bearer {token_user_2}"},
    )
    with patch("app.services.order_service.expire_stale_reservations.apply_async"):
        response_user_1 = cliente.post(
            "/api/v5.0/orders", headers={"Authorization": f"Bearer {token_user_1}"}
        )
        response_user_2 = cliente.post(
            "/api/v5.0/orders", headers={"Authorization": f"Bearer {token_user_2}"}
        )

    assert response_user_1.status_code == 201
    assert response_user_1.json()["user_id"] == user_1.id
    assert response_user_2.status_code == 400
    assert response_user_2.json()["detail"] == "Insufficient stock for skin"
