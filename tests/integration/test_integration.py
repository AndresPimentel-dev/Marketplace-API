from datetime import UTC, datetime, timedelta
from decimal import Decimal

from app.core.security import hash_password
from app.models.models import (
    InventoryItemsTable,
    OrdersStatus,
    OrdersTable,
    SkinsTable,
    UsersTable,
)
from app.repositories.cart_repository import CartRepository
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.skin_repository import SkinsRepository
from app.repositories.user_repository import UserRepository
from app.schemas.skin import SkinCreate, SkinUpdate

# =====================================================
#            TESTS USER_REPOSITORY
# ====================================================


def test_create_user_repository(get_db_test):
    email = "email@gamil.com"
    password = hash_password("password_fake")
    repo = UserRepository(db=get_db_test)

    create_user = repo.create_user(email, password)

    assert create_user is not None
    assert create_user.email == email
    assert create_user.hashed_password == password


def test_get_by_email_repository(get_db_test):
    email = "email@gamil.com"
    password = hash_password("password_fake")
    repo = UserRepository(db=get_db_test)
    repo.create_user(email, password)
    user = repo.get_user_by_email(email)

    assert user is not None
    assert user.email == email
    assert user.hashed_password == password


def test_get_by_non_existing_email_repository(get_db_test):
    repo = UserRepository(db=get_db_test)
    user = repo.get_user_by_email("inexintingemail@gmail")

    assert user is None


# =====================================================
#            TESTS SKIN_REPOSITORY
# ====================================================


def test_create_skin_repository(get_db_test):
    repo = SkinsRepository(db=get_db_test)
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
    # aqui se convierte a un modelo de pidantic para que no de errores
    create_skin = repo.create_skin(skin_data=skin_data)

    assert create_skin is not None
    assert create_skin.name == "Redline"
    assert create_skin.category == "weapon"
    assert create_skin.currency == "USD"


def test_create_skin_repeated_slug(get_db_test):
    repo = SkinsRepository(db=get_db_test)
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
    repo.create_skin(skin_data=skin_data)
    response = repo.create_skin(skin_data=skin_data)

    assert response is None


def test_get_active_skin_by_id(get_db_test):
    repo = SkinsRepository(get_db_test)
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
    # aqui se convierte a un modelo de pidantic para que no de errores
    new = repo.create_skin(skin_data=skin_data)
    request = repo.get_active_skin_by_id(new.id)

    assert request.id == new.id
    assert request is not None
    assert request.name == "Redline"


def test_get_nonexisting_active_skin_by_id(get_db_test):
    repo = SkinsRepository(get_db_test)
    request = repo.get_active_skin_by_id(5)

    assert request is None


def test_get_skin_by_slug(get_db_test):
    repo = SkinsRepository(get_db_test)
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
    repo.create_skin(skin_data=skin_data)
    request = repo.get_skin_by_slug("redline")

    assert request is not None
    assert request.name == "Redline"
    assert request.currency == "USD"


def test_get_nonexisting_skin_by_slug(get_db_test):
    repo = SkinsRepository(get_db_test)
    request = repo.get_skin_by_slug("redline")

    assert request is None


def test_update_skin(get_db_test):
    repo = SkinsRepository(get_db_test)
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
    new = repo.create_skin(skin_data=data)
    new_data = SkinUpdate(
        name="new_name", description="new_desciption", category="weapon", currency="USD"
    )
    to_update = repo.update_skin(skin_id=new.id, skin_data=new_data)

    assert to_update is not None
    assert to_update.name == "new_name"
    assert to_update.slug == "redline"
    assert to_update.description == "new_desciption"
    assert to_update.category == "weapon"
    assert to_update.rarity == "rare"
    assert to_update.stock_total == 100


def test_update_nonexisting_skin(get_db_test):
    repo = SkinsRepository(get_db_test)
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
    to_update = repo.update_skin(skin_id=2, skin_data=data)

    assert to_update is None


def test_deactivate_skin_by_id(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    skin = repo.create_skin(
        SkinCreate(
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
    )

    deactivated = repo.deactivate_skin_by_id(skin_id=skin.id)

    assert deactivated.is_active is False


def test_deactivate_nonexisting_skin_by_id(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    to_deactivate = repo.deactivate_skin_by_id(skin_id=2)

    assert to_deactivate is None


def test_activate_skin_by_id(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    skin = repo.create_skin(
        SkinCreate(
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
    )
    repo.deactivate_skin_by_id(skin_id=skin.id)
    repo.activate_skin_by_id(skin_id=skin.id)
    activate = repo.get_active_skin_by_id(skin_id=skin.id)
    assert activate is not None
    assert activate.name == "Redline"


def test_activate_nonexisting_skin_by_id(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    to_activate = repo.activate_skin_by_id(skin_id=2)

    assert to_activate is None


def test_get_skins_with_filters_and_pagination_by_category(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    repo.create_skin(
        SkinCreate(
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
    )
    request = repo.get_skins(category="weapon")

    assert request is not None
    assert isinstance(request, list)
    assert request[0].name == "Redline"
    assert request[0].slug == "redline"


def test_get_skins_with_filters_and_pagination_by_rarity(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    repo.create_skin(
        SkinCreate(
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
    )
    request = repo.get_skins(rarity="rare")

    assert request is not None
    assert isinstance(request, list)
    assert request[0].name == "Redline"
    assert request[0].slug == "redline"


def test_get_skins_with_filters_and_pagination_by_currency(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    repo.create_skin(
        SkinCreate(
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
    )
    request = repo.get_skins(currency="USD")

    assert request is not None
    assert isinstance(request, list)
    assert request[0].name == "Redline"
    assert request[0].slug == "redline"


def test_get_skins_with_filters_and_pagination_by_is_limited(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    repo.create_skin(
        SkinCreate(
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
    )
    request = repo.get_skins(is_limited=False)

    assert request is not None
    assert isinstance(request, list)
    assert request[0].name == "Redline"
    assert request[0].slug == "redline"


def test_get_skins_with_filters_and_pagination_by_all(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    repo.create_skin(
        SkinCreate(
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
    )
    request = repo.get_skins(category="weapon", rarity="rare", is_limited=False)

    assert request is not None
    assert isinstance(request, list)
    assert request[0].name == "Redline"
    assert request[0].slug == "redline"


def test_get_notexisting_skins_with_filters_and_pagination_by_category(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    request = repo.get_skins(category="weapon")

    assert request == []


def test_get_notexisting_skins_with_filters_and_pagination_by_rarity(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    request = repo.get_skins(rarity="weapon")

    assert request == []


def test_get_notexisting_skins_with_filters_and_pagination_by_currency(get_db_test):
    repo = SkinsRepository(db=get_db_test)
    request = repo.get_skins(currency="USD")

    assert request == []


# =====================================================
#            TESTS CART_REPOSITORY
# ====================================================


def test_create_cart(get_db_test):
    repo = CartRepository(db=get_db_test)
    response = repo.create_cart(user_id=1)

    assert response is not None
    assert response.user_id == 1


def test_get_cart_by_user_id(get_db_test):
    repo = CartRepository(db=get_db_test)
    repo.create_cart(user_id=1)
    response = repo.get_cart_by_user_id(user_id=1)

    assert response is not None
    assert response.user_id == 1


def test_get_nonexisting_cart_by_ser_id(get_db_test):
    repo = CartRepository(db=get_db_test)
    response = repo.get_cart_by_user_id(user_id=1)

    assert response is None


def test_add_item(get_db_test):
    repo = CartRepository(db=get_db_test)
    cart = repo.create_cart(user_id=1)
    response = repo.add_item(cart_id=cart.id, skin_id=1, quantity=1)

    assert response is not None
    assert response.skin_id == 1
    assert response.cart_id == cart.id
    assert response.quantity == 1


def test_get_cart_item(get_db_test):
    repo = CartRepository(db=get_db_test)
    cart = repo.create_cart(user_id=1)
    repo.add_item(cart_id=cart.id, skin_id=1, quantity=1)
    response = repo.get_cart_item(cart_id=cart.id, skin_id=1)

    assert response.cart_id == cart.id
    assert response.skin_id == 1
    assert response.quantity == 1


def test_get_nonexisting_cart_item(get_db_test):
    repo = CartRepository(db=get_db_test)
    response = repo.get_cart_item(cart_id=1, skin_id=1)

    assert response is None


def test_update_item_quantity(get_db_test):
    repo = CartRepository(db=get_db_test)
    cart = repo.create_cart(user_id=1)
    item = repo.add_item(cart_id=cart.id, skin_id=1, quantity=1)
    response = repo.update_item_quantity(item=item, quantity=5)

    assert response is not None
    assert response.quantity == 5
    assert response.skin_id == 1


def test_delete_item(get_db_test):
    repo = CartRepository(db=get_db_test)
    cart = repo.create_cart(user_id=1)
    item = repo.add_item(cart_id=cart.id, skin_id=1, quantity=1)
    response = repo.delete_item(item=item)

    assert response is None


# =====================================================
#            TESTS ORDER_REPOSITORY
# ====================================================


def test_create_order_success(get_db_test):
    """Verifica la creación exitosa de una orden con sus campos iniciales."""
    repo = OrderRepository(db=get_db_test)

    # Crear usuario previo (dependencia de llave foránea si aplica)
    user = UsersTable(
        id=1,
        email="user@test.com",
        hashed_password="testuser",
        created_at=datetime.now(UTC),
    )
    get_db_test.add(user)
    get_db_test.commit()

    new_order = OrdersTable(
        status=OrdersStatus.PENDING_PAYMENT,
        total_amount=Decimal("150.00"),
        currency="USD",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
        user_id=1,
    )

    created = repo.create_order(new_order)
    get_db_test.commit()

    assert created.id is not None
    assert created.status == OrdersStatus.PENDING_PAYMENT
    assert created.total_amount == Decimal("150.00")
    assert created.user_id == 1


def test_get_order_by_id_success(get_db_test):
    """Verifica que se pueda recuperar una orden existente por su ID."""
    repo = OrderRepository(db=get_db_test)

    user = UsersTable(
        id=1,
        email="user@test.com",
        hashed_password="testuser",
        created_at=datetime.now(UTC),
    )
    order = OrdersTable(
        status=OrdersStatus.PENDING_PAYMENT,
        total_amount=Decimal("50.00"),
        currency="USD",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
        user_id=1,
    )
    get_db_test.add_all([user, order])
    get_db_test.commit()

    retrieved = repo.get_order_by_id(order.id)

    assert retrieved is not None
    assert retrieved.id == order.id
    assert retrieved.total_amount == Decimal("50.00")


def test_get_order_by_id_not_found_edge(get_db_test):
    """Edge Case: Intentar buscar una orden con un ID que no existe retorna None."""
    repo = OrderRepository(db=get_db_test)

    retrieved = repo.get_order_by_id(9999)
    assert retrieved is None


def test_get_orders_associated_to_user_id_success(get_db_test):
    """Verifica que devuelva todas las órdenes asociadas a un usuario específico."""
    repo = OrderRepository(db=get_db_test)

    user1 = UsersTable(
        id=1,
        email="user1@test.com",
        hashed_password="user1",
        created_at=datetime.now(UTC),
    )
    user2 = UsersTable(
        id=2,
        email="user2@test.com",
        hashed_password="user2",
        created_at=datetime.now(UTC),
    )

    order1 = OrdersTable(
        status=OrdersStatus.PENDING_PAYMENT,
        total_amount=Decimal("10.00"),
        currency="USD",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
        user_id=1,
    )
    order2 = OrdersTable(
        status=OrdersStatus.COMPLETED,
        total_amount=Decimal("20.00"),
        currency="USD",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
        user_id=1,
    )
    order3 = OrdersTable(
        status=OrdersStatus.PENDING_PAYMENT,
        total_amount=Decimal("30.00"),
        currency="USD",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
        user_id=2,
    )

    get_db_test.add_all([user1, user2, order1, order2, order3])
    get_db_test.commit()

    user_orders = repo.get_orders_associated_to_user_id(user_id=1)

    assert len(user_orders) == 2
    assert all(o.user_id == 1 for o in user_orders)


def test_get_orders_associated_to_user_id_empty_edge(get_db_test):
    """Edge Case: Usuario sin órdenes retorna una lista vacía."""
    repo = OrderRepository(db=get_db_test)
    user = UsersTable(
        id=1,
        email="user1@test.com",
        hashed_password="user1",
        created_at=datetime.now(UTC),
    )
    get_db_test.add(user)
    get_db_test.commit()

    user_orders = repo.get_orders_associated_to_user_id(user_id=1)
    assert user_orders == []


def test_get_orders_pagination_edge(get_db_test):
    """Edge Case: Comportamiento de la paginación (page y page_size)."""
    repo = OrderRepository(db=get_db_test)
    user = UsersTable(
        id=1,
        email="user1@test.com",
        hashed_password="user1",
        created_at=datetime.now(UTC),
    )
    get_db_test.add(user)

    # Crear 5 órdenes para el mismo usuario
    orders = [
        OrdersTable(
            status=OrdersStatus.PENDING_PAYMENT,
            total_amount=Decimal(f"{i}.00"),
            currency="USD",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            expires_at=datetime.now(UTC),
            user_id=1,
        )
        for i in range(1, 6)
    ]
    get_db_test.add_all(orders)
    get_db_test.commit()

    # Página 1, tamaño 2 -> Debe traer los elementos 1 y 2
    page_1 = repo.get_orders_associated_to_user_id(user_id=1, page=1, page_size=2)
    assert len(page_1) == 2
    assert page_1[0].total_amount == Decimal("1.00")
    assert page_1[1].total_amount == Decimal("2.00")

    # Página 2, tamaño 2 -> Debe traer los elementos 3 y 4
    page_2 = repo.get_orders_associated_to_user_id(user_id=1, page=2, page_size=2)
    assert len(page_2) == 2
    assert page_2[0].total_amount == Decimal("3.00")
    assert page_2[1].total_amount == Decimal("4.00")

    # Página 3, tamaño 2 -> Debe traer el elemento restante (5)
    page_3 = repo.get_orders_associated_to_user_id(user_id=1, page=3, page_size=2)
    assert len(page_3) == 1
    assert page_3[0].total_amount == Decimal("5.00")


def test_update_order_status_success(get_db_test):
    """Verifica que el estado de la orden cambie y actualice la fecha de modificación."""
    repo = OrderRepository(db=get_db_test)

    user = UsersTable(
        id=1,
        email="user@test.com",
        hashed_password="testuser",
        created_at=datetime.now(UTC),
    )
    order = OrdersTable(
        status=OrdersStatus.PENDING_PAYMENT,
        total_amount=Decimal("100.00"),
        currency="USD",
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC),
        user_id=1,
    )
    get_db_test.add_all([user, order])
    get_db_test.commit()

    old_updated_at = order.updated_at

    updated_order = repo.update_order_status(order, OrdersStatus.COMPLETED)
    get_db_test.commit()

    assert updated_order.status == OrdersStatus.COMPLETED
    assert updated_order.updated_at >= old_updated_at


# =====================================================
#            TESTS INVENTORY_REPOSITORY
# ====================================================


def seed_base_dependencies(db_session):
    user1 = UsersTable(
        id=1,
        email="user1@test.com",
        hashed_password="user1",
        created_at=datetime.now(UTC),
    )
    user2 = UsersTable(
        id=2,
        email="user2@test.com",
        hashed_password="user2",
        created_at=datetime.now(UTC),
    )
    skin1 = SkinsTable(
        name="Redline",
        slug="redsline",
        description="Old desc",
        category="weapon",
        rarity="rare",
        price=20.00,
        currency="USD",
        stock_total=100,
        is_limited=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    skin2 = SkinsTable(
        name="Redline",
        slug="redlsine",
        description="Old desc",
        category="weapon",
        rarity="rare",
        price=20.00,
        currency="USD",
        stock_total=100,
        is_limited=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    order1 = OrdersTable(
        id=1,
        status=OrdersStatus.COMPLETED,
        total_amount=10.0,
        currency="USD",
        user_id=1,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )

    db_session.add_all([user1, user2, skin1, skin2, order1])
    db_session.commit()


# --- 2. Pruebas de Integración ---


def test_create_inventory_item_success(get_db_test):
    """Verifica la creación exitosa de un item en el inventario."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    item = repo.create(user_id=1, skin_id=100, order_id=1)
    get_db_test.commit()

    assert item.id is not None
    assert item.user_id == 1
    assert item.skin_id == 100
    assert item.order_id == 1


def test_get_user_inventory_success(get_db_test):
    """Verifica que devuelva todos los items que le pertenecen a un usuario."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    # Añadir 2 items para el usuario 1 y 1 item para el usuario 2
    repo.create(user_id=1, skin_id=100, order_id=1)
    repo.create(user_id=1, skin_id=200, order_id=1)
    repo.create(user_id=2, skin_id=100, order_id=1)
    get_db_test.commit()

    inventory_user_1 = repo.get_user_inventory(user_id=1)

    assert len(inventory_user_1) == 2
    assert all(item.user_id == 1 for item in inventory_user_1)


def test_get_user_inventory_empty_edge(get_db_test):
    """Edge Case: Un usuario sin inventario retorna una lista vacía."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    inventory = repo.get_user_inventory(user_id=1)
    assert inventory == []


def test_get_by_id_success(get_db_test):
    """Verifica que se pueda obtener un item específico por su ID y su dueño."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    created_item = repo.create(user_id=1, skin_id=100, order_id=1)
    get_db_test.commit()

    found_item = repo.get_by_id(inventory_item_id=created_item.id, user_id=1)

    assert found_item is not None
    assert found_item.id == created_item.id
    assert found_item.skin_id == 100


def test_get_by_id_security_isolation_edge(get_db_test):
    """Edge Case: Intentar acceder a un item de inventario que pertenece a otro usuario retorna None."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    # Item creado para el usuario 1
    created_item = repo.create(user_id=1, skin_id=100, order_id=1)
    get_db_test.commit()

    # Usuario 2 intenta consultar el item del usuario 1
    found_item = repo.get_by_id(inventory_item_id=created_item.id, user_id=2)

    assert found_item is None


def test_get_by_id_not_found_edge(get_db_test):
    """Edge Case: Consultar un ID de inventario que no existe retorna None."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    found_item = repo.get_by_id(inventory_item_id=9999, user_id=1)
    assert found_item is None


def test_get_by_user_and_skin_success(get_db_test):
    """Verifica que se pueda buscar un item de inventario cruzando el user_id y el skin_id."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    repo.create(user_id=1, skin_id=200, order_id=1)
    get_db_test.commit()

    found = repo.get_by_user_and_skin(user_id=1, skin_id=200)

    assert found is not None
    assert found.user_id == 1
    assert found.skin_id == 200


def test_get_by_user_and_skin_not_found_edge(get_db_test):
    """Edge Case: Buscar una combinación de usuario y skin que no posee retorna None."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    found = repo.get_by_user_and_skin(user_id=1, skin_id=999)
    assert found is None


def test_db_add_inventory_helper_success(get_db_test):
    """Verifica que el método auxiliar `db_add_inventory` agregue correctamente el objeto a la sesión."""
    seed_base_dependencies(get_db_test)
    repo = InventoryRepository(db=get_db_test)

    new_item = InventoryItemsTable(
        user_id=1, skin_id=100, order_id=1, acquired_at=datetime.now(UTC)
    )
    repo.db_add_inventory(new_item)
    get_db_test.commit()

    assert new_item.id is not None

    # Comprobar que realmente persiste en la base de datos
    retrieved = repo.get_by_id(new_item.id, user_id=1)
    assert retrieved is not None
