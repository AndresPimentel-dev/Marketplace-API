from concurrent.futures import ThreadPoolExecutor
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


# ===================
# this test must be done in a postgres database because sqlite
# does not handle concurrency correctly
# ===================
def test_concurrency_create_order_endpoint(get_db_test, cliente):
    """agregamos los dos usuarios que competiran concurrentemente por comprar
    la skin limitada para demostrar que SELECT FOR UPDATE evita el oversell"""
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

    def post_order(token):
        return cliente.post(
            "/api/v5.0/orders", headers={"Authorization": f"Bearer {token}"}
        )

    with (
        patch("app.services.order_service.expire_stale_reservations.apply_async"),
        ThreadPoolExecutor(max_workers=2) as executor,
    ):
        future_1 = executor.submit(post_order, token_user_1)
        future_2 = executor.submit(post_order, token_user_2)
        response_1 = future_1.result()
        response_2 = future_2.result()

    statuses = [response_1.status_code, response_2.status_code]
    assert 201 in statuses
    assert 400 in statuses

    success_resp = response_1 if response_1.status_code == 201 else response_2
    fail_resp = response_2 if response_1.status_code == 201 else response_1

    assert success_resp.json()["user_id"] in [user_1.id, user_2.id]
    assert fail_resp.json()["detail"] == "Insufficient stock for skin"
