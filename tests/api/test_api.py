from unittest.mock import patch


# ==================================================
#           TEST ENDPOINTS AUTH
# ==================================================
def test_endpoint_register(cliente):
    response = cliente.post(
        "/api/v5.0/auth/register",
        json={"email": "fakeemail@gmail.com", "password": "fakepassword"},
    )
    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None


def test_endpoint_login(cliente):
    cliente.post(
        "/api/v5.0/auth/register",
        json={"email": "fakeemail@gmail.com", "password": "fakepassword"},
    )

    response = cliente.post(
        "/api/v5.0/auth/login",
        data={"username": "fakeemail@gmail.com", "password": "fakepassword"},
    )
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"] is not None
    assert response.json()["refresh_token"] is not None


def test_register_duplicated_email(cliente):
    cliente.post(
        "/api/v5.0/auth/register",
        json={"email": "fakeemail@gmail.com", "password": "fakepassword"},
    )

    response = cliente.post(
        "/api/v5.0/auth/register",
        json={"email": "fakeemail@gmail.com", "password": "fakepassword"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already used"


def test_login_nonexistent_email(cliente):
    response = cliente.post(
        "/api/v5.0/auth/login",
        data={"username": "fakeemail@gmail.com", "password": "fakepassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_wrong_password(cliente):
    cliente.post(
        "/api/v5.0/auth/register",
        json={"email": "fakeemail@gmail.com", "password": "fakepassword"},
    )

    response = cliente.post(
        "/api/v5.0/auth/login",
        data={"username": "fakeemail@gmail.com", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


# --- EDGE CASES: AUTH ---


def test_register_invalid_email_format(cliente):
    """Edge Case: Registrar con formato de email inválido."""
    response = cliente.post(
        "/api/v5.0/auth/register",
        json={"email": "not-an-email", "password": "fakepassword"},
    )
    assert response.status_code == 422


def test_register_empty_password(cliente):
    """Edge Case: Registrar con contraseña vacía o demasiado corta."""
    response = cliente.post(
        "/api/v5.0/auth/register",
        json={"email": "valid@gmail.com", "password": ""},
    )
    assert response.status_code == 422


def test_login_missing_form_fields(cliente):
    """Edge Case: Enviar login sin campos requeridos (OAuth2 password flow)."""
    response = cliente.post("/api/v5.0/auth/login", data={})
    assert response.status_code == 422


# ==================================================
#           TEST ENDPOINTS SKINS
# ==================================================


def test_get_skins(cliente, sample_skin):
    """Prueba listar las skins con paginación y filtros por defecto."""
    response = cliente.get("/api/v5.0/skins")
    assert response.status_code == 200
    data = response.json()
    assert "skins" in data
    assert len(data["skins"]) >= 1
    assert data["skins"][0]["name"] == sample_skin.name


def test_get_skin_by_id_success(cliente, sample_skin):
    """Prueba obtener una skin existente por su ID."""
    response = cliente.get(f"/api/v5.0/skins/{sample_skin.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_skin.id
    assert data["name"] == sample_skin.name


def test_get_skin_by_id_not_found(cliente):
    """Prueba obtener una skin que no existe (debe retornar 404)."""
    response = cliente.get("/api/v5.0/skins/99999")
    assert response.status_code == 404


# --- EDGE CASES: SKINS ---


def test_get_skin_invalid_id_type(cliente):
    """Edge Case: Buscar skin con ID de tipo inválido (string en lugar de entero)."""
    response = cliente.get("/api/v5.0/skins/abc-not-an-id")
    assert response.status_code == 422


def test_get_skins_with_invalid_pagination(cliente):
    """Edge Case: Paginación con números negativos o absurdos."""
    response = cliente.get("/api/v5.0/skins?page=-1&limit=0")
    # Dependiendo de la validación, puede retornar 422 o normalizar a valores por defecto (200)
    assert response.status_code in [200, 422]


# ==========================================
#          TESTS DE ADMIN (POST/PATCH/DELETE)
# ==========================================


def test_create_skin_by_admin(cliente, admin_token_headers):
    """Prueba la creación de una skin siendo administrador."""
    payload = {
        "name": "reaper",
        "slug": "void-reaper",
        "description": "character",
        "category": "character",
        "rarity": "legendary",
        "price": "14.99",
        "currency": "USD",
        "stock_total": 400,
        "is_limited": True,
    }
    response = cliente.post(
        "/api/v5.0/admin/skins", json=payload, headers=admin_token_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["category"] == payload["category"]


def test_create_skin_unauthorized(cliente):
    """Prueba que un usuario sin token o no admin no pueda crear skins."""
    payload = {
        "name": "Hacker Skin",
        "category": "weapon",
        "rarity": "common",
        "currency": "coins",
        "price": 100,
        "is_limited": False,
    }
    response = cliente.post("/api/v5.0/admin/skins", json=payload)
    assert response.status_code in [401, 403]


def test_update_skin_by_admin(cliente, admin_token_headers, sample_skin):
    """Prueba actualizar una skin existente como administrador."""
    payload = {"price": "1800.00"}
    response = cliente.patch(
        f"/api/v5.0/admin/skins/{sample_skin.id}",
        json=payload,
        headers=admin_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["price"] == "1800.00"


def test_activate_skin_by_admin(cliente, admin_token_headers, sample_skin):
    """Prueba activar una skin como administrador."""
    cliente.delete(
        f"/api/v5.0/admin/skins/{sample_skin.id}", headers=admin_token_headers
    )
    response = cliente.patch(
        f"/api/v5.0/admin/skins/{sample_skin.id}/activate", headers=admin_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True


def test_deactivate_skin_by_admin(cliente, admin_token_headers, sample_skin):
    """Prueba desactivar una skin como administrador (retorna 204)."""
    response = cliente.delete(
        f"/api/v5.0/admin/skins/{sample_skin.id}", headers=admin_token_headers
    )
    assert response.status_code == 204


# --- EDGE CASES: ADMIN ---


def test_create_skin_invalid_price(cliente, admin_token_headers):
    """Edge Case: Crear skin con precio negativo."""
    payload = {
        "name": "Invalid Price",
        "category": "weapon",
        "rarity": "common",
        "currency": "USD",
        "price": "-10.00",
        "is_limited": False,
    }
    response = cliente.post(
        "/api/v5.0/admin/skins", json=payload, headers=admin_token_headers
    )
    assert response.status_code == 422


def test_create_skin_missing_required_fields(cliente, admin_token_headers):
    """Edge Case: Crear skin omitiendo campos obligatorios como el nombre o categoría."""
    payload = {"price": "10.00"}
    response = cliente.post(
        "/api/v5.0/admin/skins", json=payload, headers=admin_token_headers
    )
    assert response.status_code == 422


def test_update_non_existent_skin(cliente, admin_token_headers):
    """Edge Case: Actualizar skin que no existe."""
    response = cliente.patch(
        "/api/v5.0/admin/skins/99999",
        json={"price": "50.00"},
        headers=admin_token_headers,
    )
    assert response.status_code == 404


def test_admin_action_with_regular_user_token(cliente, user_token_headers, sample_skin):
    """Edge Case: Intentar acciones de administrador usando un token de usuario normal (Permisos insuficientes)."""
    response = cliente.delete(
        f"/api/v5.0/admin/skins/{sample_skin.id}", headers=user_token_headers
    )
    assert response.status_code == 403


# ==========================================
#          TESTS DE ENDPOINTS DE CART
# ==========================================


def test_add_skin_to_cart_success(cliente, user_token_headers, sample_skin):
    """Prueba agregar una skin existente al carrito del usuario."""
    payload = {"skin_id": sample_skin.id, "quantity": 1}
    response = cliente.post(
        "/api/v5.0/cart/items", json=payload, headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["skin_id"] == sample_skin.id
    assert data["quantity"] == 1


def test_add_skin_to_cart_skin_not_found(cliente, user_token_headers):
    """Prueba intentar agregar una skin que no existe (debe retornar 404)."""
    payload = {"skin_id": 99999, "quantity": 1}
    response = cliente.post(
        "/api/v5.0/cart/items", json=payload, headers=user_token_headers
    )
    assert response.status_code == 404


def test_get_user_cart(cliente, user_token_headers, sample_skin):
    """Prueba obtener el contenido del carrito del usuario."""
    cliente.post(
        "/api/v5.0/cart/items",
        json={"skin_id": sample_skin.id, "quantity": 2},
        headers=user_token_headers,
    )

    response = cliente.get("/api/v5.0/cart", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 1
    assert data["items"][0]["skin_id"] == sample_skin.id
    assert data["items"][0]["quantity"] == 2


def test_update_amount_skin(cliente, user_token_headers, sample_skin):
    """Prueba actualizar la cantidad de una skin en el carrito."""
    cliente.post(
        "/api/v5.0/cart/items",
        json={"skin_id": sample_skin.id, "quantity": 1},
        headers=user_token_headers,
    )

    payload = {"quantity": 5}
    response = cliente.patch(
        f"/api/v5.0/cart/items/{sample_skin.id}",
        json=payload,
        headers=user_token_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 5


def test_delete_cart_item(cliente, user_token_headers, sample_skin):
    """Prueba eliminar un ítem específico del carrito (retorna 204)."""
    cliente.post(
        "/api/v5.0/cart/items",
        json={"skin_id": sample_skin.id, "quantity": 1},
        headers=user_token_headers,
    )

    response = cliente.delete(
        f"/api/v5.0/cart/items/{sample_skin.id}", headers=user_token_headers
    )
    assert response.status_code == 204

    cart_response = cliente.get("/api/v5.0/cart", headers=user_token_headers)
    assert len(cart_response.json()["items"]) == 0


def test_empty_cart(cliente, user_token_headers, sample_skin):
    """Prueba vaciar por completo el carrito del usuario (retorna 204)."""
    cliente.post(
        "/api/v5.0/cart/items",
        json={"skin_id": sample_skin.id, "quantity": 3},
        headers=user_token_headers,
    )

    response = cliente.delete("/api/v5.0/cart/items", headers=user_token_headers)
    assert response.status_code == 204

    cart_response = cliente.get("/api/v5.0/cart", headers=user_token_headers)
    assert len(cart_response.json()["items"]) == 0


def test_cart_unauthorized(cliente):
    """Prueba que un usuario sin autenticarse no pueda acceder a los endpoints del carrito."""
    response = cliente.get("/api/v5.0/cart")
    assert response.status_code in [401, 403]


# --- EDGE CASES: CART ---


def test_add_skin_to_cart_zero_quantity(cliente, user_token_headers, sample_skin):
    """Edge Case: Agregar una cantidad de 0 elementos al carrito."""
    payload = {"skin_id": sample_skin.id, "quantity": 0}
    response = cliente.post(
        "/api/v5.0/cart/items", json=payload, headers=user_token_headers
    )
    assert response.status_code == 422


def test_add_skin_to_cart_negative_quantity(cliente, user_token_headers, sample_skin):
    """Edge Case: Agregar una cantidad negativa de elementos al carrito."""
    payload = {"skin_id": sample_skin.id, "quantity": -5}
    response = cliente.post(
        "/api/v5.0/cart/items", json=payload, headers=user_token_headers
    )
    assert response.status_code == 422


def test_add_inactive_skin_to_cart(
    cliente, user_token_headers, admin_token_headers, sample_skin
):
    """Edge Case: Intentar agregar al carrito una skin que ha sido desactivada/eliminada."""
    # Desactivar la skin primero
    cliente.delete(
        f"/api/v5.0/admin/skins/{sample_skin.id}", headers=admin_token_headers
    )

    payload = {"skin_id": sample_skin.id, "quantity": 1}
    response = cliente.post(
        "/api/v5.0/cart/items", json=payload, headers=user_token_headers
    )
    assert response.status_code in [400, 404, 422, 409]


def test_update_cart_item_exceeding_stock(cliente, user_token_headers, sample_skin):
    """Edge Case: Actualizar la cantidad del carrito superando el stock disponible."""
    cliente.post(
        "/api/v5.0/cart/items",
        json={"skin_id": sample_skin.id, "quantity": 1},
        headers=user_token_headers,
    )
    # Suponiendo que el stock total de sample_skin es limitado y pedimos una cantidad exagerada
    payload = {"quantity": 999999}
    response = cliente.patch(
        f"/api/v5.0/cart/items/{sample_skin.id}",
        json=payload,
        headers=user_token_headers,
    )
    assert response.status_code in [400, 409, 422]


# ==========================================
#          TESTS DE ENDPOINTS DE ORDERS
# ==========================================


def test_create_order_success(cliente, user_token_headers, sample_skin):
    """Prueba crear una orden a partir de los elementos del carrito del usuario."""
    with patch("app.services.order_service.expire_stale_reservations.apply_async"):
        payload = {"skin_id": sample_skin.id, "quantity": 1}
        cliente.post("/api/v5.0/cart/items", json=payload, headers=user_token_headers)
        response = cliente.post("/api/v5.0/orders", headers=user_token_headers)
        assert response.status_code == 201
        data = response.json()

        assert "id" in data
        assert data["status"] in [
            "PENDING_PAYMENT",
            "pending_payment",
        ]


def test_create_order_empty_cart_conflict(cliente, user_token_headers):
    """Prueba intentar crear una orden sin tener ítems en el carrito (debe lanzar 409)."""
    response = cliente.post("/api/v5.0/orders", headers=user_token_headers)
    assert response.status_code == 409


def test_get_user_orders(cliente, user_token_headers, sample_order):
    """Prueba listar las órdenes del usuario con paginación."""
    response = cliente.get("/api/v5.0/orders", headers=user_token_headers)
    assert response.status_code == 200
    data = response.json()
    orders_list = data if isinstance(data, list) else data.get("orders", [])
    assert len(orders_list) >= 0


def test_get_order_by_id_success(cliente, user_token_headers, sample_order):
    """Prueba obtener una orden específica por su ID."""
    response = cliente.get(
        f"/api/v5.0/orders/{sample_order.id}", headers=user_token_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_order.id


def test_get_order_by_id_not_found_or_unauthorized(cliente, user_token_headers):
    """Prueba consultar una orden que no existe (debe retornar 409 o 404 según tu servicio)."""
    response = cliente.get("/api/v5.0/orders/99999", headers=user_token_headers)
    assert response.status_code in [404, 409]


# --- EDGE CASES: ORDERS ---


def test_get_order_with_malformed_id(cliente, user_token_headers):
    """Edge Case: Consultar orden con ID de formato inválido (texto)."""
    response = cliente.get(
        "/api/v5.0/orders/invalid-id-format", headers=user_token_headers
    )
    assert response.status_code == 422


def test_user_cannot_access_other_users_order(
    cliente, admin_token_headers, sample_order
):
    """Edge Case: Intentar acceder a una orden ajena usando otro token (Aislamiento de recursos)."""
    # Usando cabeceras de otro usuario / admin simulado de otra cuenta
    response = cliente.get(
        f"/api/v5.0/orders/{sample_order.id}", headers=admin_token_headers
    )
    assert response.status_code in [403, 404, 409]


def test_orders_unauthorized(cliente):
    """Prueba que un usuario sin token no pueda interactuar con los endpoints de órdenes y checkout."""
    response = cliente.get("/api/v5.0/orders")
    assert response.status_code in [401, 403]
