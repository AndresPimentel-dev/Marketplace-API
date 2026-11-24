from unittest.mock import MagicMock

import pytest

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.models import CartItemsTable, CartsTable, SkinsTable, UsersTable
from app.schemas.auth import LoginRequest, UserCreate
from app.schemas.cart import CartItemCreate, UpdateItemQuantity
from app.schemas.skin import SkinCreate, SkinUpdate
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.catalog_service import CatalogService

# =======================================
#       TEST DE SEGURIDAD Y DEPENDENCIAS
# =======================================


def test_generate_password():
    password = "password_fake"
    hash = hash_password(password)

    assert isinstance(hash, str)
    assert password != hash
    assert hash is not None


def test_verify_password():
    password = "password_fake"
    hash = hash_password(password)
    verify = verify_password(password, hash)

    assert isinstance(verify, bool)
    assert verify is True


def test_verify_fake_password():
    password = "password_fake"
    hash = hash_password(password)
    verify = verify_password("other", hash)

    assert isinstance(verify, bool)
    assert verify is False


def test_create_access_token():
    data = {"sub": "fakeemail"}
    create = create_access_token(data)

    assert isinstance(create, str)
    assert create is not None


def test_verify_access_token():
    data = {"sub": "fakeemail"}
    token = create_access_token(data=data)
    decode = decode_token(token=token)

    assert isinstance(decode, dict)
    assert decode is not None
    assert decode["email"] == "fakeemail"
    assert decode["token_type"] == "access"


def test_create_refresh_token():
    data = {"sub": "fakeemail"}
    token = create_refresh_token(data=data)

    assert isinstance(token, str)
    assert token is not None


def test_verify_refresh_token():
    data = {"sub": "fakeemail"}
    token = create_refresh_token(data=data)
    decode = decode_token(token=token)

    assert isinstance(decode, dict)
    assert decode is not None
    assert decode["email"] == "fakeemail"
    assert decode["token_type"] == "refresh"


# =======================================
#       TEST DE AuthService
# =======================================


def test_register_user(get_db_test):
    mock_repo = MagicMock()
    mock_repo.get_user_by_email.return_value = None

    false_user = UsersTable(email="fakeemail@gmail.com", hashed_password="fakepassword")
    mock_repo.create_user.return_value = false_user

    service = AuthService(user_repository=mock_repo, db=get_db_test)
    register_date = UserCreate(email="fakeemail@gmail.com", password="fakepassword")

    result = service.register_user(register_date)

    assert result is not None


def test_register_duplicated_email(get_db_test):
    mock_repo = MagicMock()
    mock_repo.get_user_by_email.return_value = UsersTable(
        email="fake@gmail.com", hashed_password="fake"
    )
    service = AuthService(user_repository=mock_repo, db=get_db_test)
    register_date = UserCreate(email="fakeemail@gmail.com", password="fakepassword")

    with pytest.raises(ConflictException):
        service.register_user(register_date)


def test_login_user_success(get_db_test):
    mock_repo = MagicMock()

    pass_hash = hash_password("fakepassword")

    fake_user = UsersTable(email="fakeemail@gmail.com", hashed_password=pass_hash)
    mock_repo.get_user_by_email.return_value = fake_user

    service = AuthService(user_repository=mock_repo, db=get_db_test)
    login_data = LoginRequest(email="fakeemail@gmail.com", password="fakepassword")

    tokens = service.login_user(login_data)

    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.token_type == "bearer"


def test_login_user_not_found(get_db_test):
    mock_repo = MagicMock()

    mock_repo.get_user_by_email.return_value = None

    service = AuthService(user_repository=mock_repo, db=get_db_test)
    login_data = LoginRequest(email="fakeemail@gmail.com", password="fakepassword")

    with pytest.raises(UnauthorizedException):
        service.login_user(login_data)


def test_login_user_incorrect_password(get_db_test):
    mock_repo = MagicMock()
    pass_hash = hash_password("fakepassword")

    fake_user = UsersTable(email="fakeemail@gmail.com", hashed_password=pass_hash)
    mock_repo.get_user_by_email.return_value = fake_user

    service = AuthService(user_repository=mock_repo, db=get_db_test)
    login_data = LoginRequest(
        email="fakeemail@gmail.com", password="fpassword_Incorrect"
    )

    with pytest.raises(UnauthorizedException):
        service.login_user(login_data)


def test_register_user_email_existing(get_db_test):
    mock_repo = MagicMock()
    mock_repo.get_user_by_email.return_value = UsersTable(
        email="emailexisting@gmail.com", hashed_password="fakepassword"
    )

    service = AuthService(user_repository=mock_repo, db=get_db_test)
    register_data = UserCreate(email="fakeemail@gmail.com", password="fakepassword")

    with pytest.raises(ConflictException):
        service.register_user(register_data)


# =======================================
#       TEST DE CatalogService
# =======================================


def test_create_skin(get_db_test):
    mock_repo = MagicMock()
    mock_repo.create_skin.return_value = SkinsTable()

    data = SkinCreate(
        name="Redline",
        slug="redline",
        description="Old desc",
        category="weapon",
        rarity="rare",
        price=20.00,
        currency="USD",
        stock_total=100,
        is_limited=False,
    )

    service = CatalogService(repository=mock_repo, db=get_db_test)

    result = service.create_skin(data)
    assert result is not None


def test_create_error_skin(get_db_test):
    mock_repo = MagicMock()
    mock_repo.create_skin.return_value = None

    service = CatalogService(repository=mock_repo, db=get_db_test)
    skin_data = SkinCreate(
        name="Redline",
        slug="redline",
        description="Old desc",
        category="weapon",
        rarity="rare",
        price=20.00,
        currency="USD",
        stock_total=100,
        is_limited=False,
    )

    with pytest.raises(ConflictException):
        service.create_skin(skin_data)


def test_get_skin_by_slug(get_db_test):
    mock_repo = MagicMock()
    mock_repo.get_skin_by_slug.return_value = SkinsTable()

    service = CatalogService(repository=mock_repo, db=get_db_test)

    result = service.get_skin_by_slug("redline")
    assert result is not None


def test_get_skin_by_slug_error(get_db_test):
    mock_repo = MagicMock()
    mock_repo.get_skin_by_slug.return_value = None

    service = CatalogService(repository=mock_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.get_skin_by_slug("slug_not_exist")


def test_get_skin_by_id(get_db_test):
    mock_repo = MagicMock()
    mock_repo.get_active_skin_by_id.return_value = SkinsTable()

    service = CatalogService(repository=mock_repo, db=get_db_test)

    result = service.get_skin_by_id(skin_id=1)
    assert result is not None


def test_get_skin_by_id_error(get_db_test):
    mock_repo = MagicMock()
    mock_repo.get_active_skin_by_id.return_value = None

    service = CatalogService(repository=mock_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.get_skin_by_id(5)


###Test por confirmar


def test_update_skin(get_db_test):
    mock_repo = MagicMock()
    mock_repo.update_skin.return_value = SkinsTable()

    data = SkinUpdate(
        name="Redline",
        slug="redline",
        description="Old desc",
        category="weapon",
        rarity="rare",
        price=20.00,
        currency="USD",
        stock_total=100,
        is_limited=False,
    )

    service = CatalogService(repository=mock_repo, db=get_db_test)

    result = service.update_skin(skin_id=5, skin_data=data)
    assert result is not None


def test_update_skin_error(get_db_test):
    mock_repo = MagicMock()
    mock_repo.update_skin.return_value = None

    data = SkinUpdate(
        name="Redline",
        slug="redline",
        description="Old desc",
        category="weapon",
        rarity="rare",
        price=20.00,
        currency="USD",
        stock_total=100,
        is_limited=False,
    )

    service = CatalogService(repository=mock_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.update_skin(skin_id=5, skin_data=data)


# =============================================================
#           TEST CART SERVICES
# =============================================================


def test_get_user_cart(get_db_test):
    mock_repo = MagicMock()
    skin_repo = MagicMock()
    mock_repo.get_cart_by_user_id.return_value = CartsTable(user_id=1, id=1)
    service = CartService(cart_repo=mock_repo, skin_repo=skin_repo, db=get_db_test)
    response = service.get_user_cart(user_id=1)

    assert response is not None
    assert response.id == 1


def test_get_nonexisting_user_cart(get_db_test):
    mock_repo = MagicMock()
    skin_repo = MagicMock()
    mock_repo.get_cart_by_user_id.return_value = None
    service = CartService(cart_repo=mock_repo, skin_repo=skin_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.get_user_cart(user_id=1)


def test_add_item_to_cart(get_db_test):
    cart_repo = MagicMock()
    skin_repo = MagicMock()
    item_mock = CartItemCreate(skin_id=1, quantity=1)
    cart_repo.get_cart_item.return_value = None
    skin_repo.get_active_skin_by_id.return_value = SkinsTable(
        name="Redline",
        slug="redline",
        description="Old desc",
        category="weapon",
        rarity="rare",
        price=20.00,
        currency="USD",
        stock_total=100,
        stock_sold=0,
        stock_reserved=0,
        is_limited=False,
    )
    cart_repo.add_item.return_value = CartItemsTable(id=1, cart_id=1)
    service = CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=get_db_test)
    response = service.add_item_to_cart(user_id=1, data=item_mock)
    assert response is not None
    assert response.id == 1


def test_add_nonexisting_to_cart(get_db_test):
    cart_repo = MagicMock()
    skin_repo = MagicMock()
    cart_repo.get_cart_by_user_id.return_value = CartsTable(id=1)
    skin_repo.get_active_skin_by_id.return_value = None
    service = CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.add_item_to_cart(user_id=1, data=CartItemCreate(skin_id=1, quantity=1))


def test_update_item(get_db_test):
    cart_repo = MagicMock()
    skin_repo = MagicMock()
    mock_skin = MagicMock()
    mock_skin.stock_total = 100
    mock_skin.stock_sold = 0
    mock_skin.stock_reserved = 0
    skin_repo.get_active_skin_by_id.return_value = mock_skin
    cart_repo.get_cart_by_user_id.return_value = CartsTable(id=1)
    cart_repo.get_cart_item.return_value = CartItemsTable(id=1, skin_id=1)
    cart_repo.update_item_quantity.return_value = CartItemsTable(id=1, skin_id=1)
    service = CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=get_db_test)
    response = service.update_item(
        user_id=1, skin_id=1, data=UpdateItemQuantity(quantity=5)
    )

    assert response is not None
    assert response.id == 1


def test_update_item_cart_nonexisting(get_db_test):
    cart_repo = MagicMock()
    skin_repo = MagicMock()
    cart_repo.get_cart_by_user_id.return_value = None
    cart_repo.get_cart_item.return_value = CartItemsTable(id=1, skin_id=1)
    cart_repo.update_item_quantity.return_value = CartItemsTable(id=1, skin_id=1)
    service = CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.update_item(user_id=1, skin_id=1, data=UpdateItemQuantity(quantity=5))


def test_update_item_not_existing_item(get_db_test):
    cart_repo = MagicMock()
    skin_repo = MagicMock()
    cart_repo.get_cart_by_user_id.return_value = CartsTable(id=1)
    cart_repo.get_cart_item.return_value = None
    cart_repo.update_item_quantity.return_value = CartItemsTable(id=1, skin_id=1)
    service = CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.update_item(user_id=1, skin_id=1, data=UpdateItemQuantity(quantity=5))


def test_delete_item(get_db_test):
    cart_repo = MagicMock()
    skin_repo = MagicMock()
    cart_repo.get_cart_by_user_id.return_value = CartsTable(id=1)
    cart_repo.get_cart_item.return_value = CartItemsTable(id=1, skin_id=1)
    cart_repo.delete_item.return_value = None
    service = CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=get_db_test)
    response = service.delete_item(user_id=1, skin_id=1)

    assert response is None


def test_delete_item_nonexisting_item(get_db_test):
    cart_repo = MagicMock()
    skin_repo = MagicMock()
    cart_repo.get_cart_by_user_id.return_value = CartsTable(id=1)
    cart_repo.get_cart_item.return_value = None
    cart_repo.delete_item.return_value = None
    service = CartService(cart_repo=cart_repo, skin_repo=skin_repo, db=get_db_test)

    with pytest.raises(NotFoundException):
        service.delete_item(user_id=1, skin_id=1)
