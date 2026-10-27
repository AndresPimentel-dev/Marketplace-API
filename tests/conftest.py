from ast import YieldFrom
from yaml import compose_all
from alembic.config import Config
import os

from alembic import command

os.environ.setdefault(
    "DATABASE_URL",
    "sqlite:///mi_db_prueba.db",
)
os.environ.setdefault("SECRET_KEY", "supersecretallaveparqatokensfalsosdeprueba")
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.security import create_access_token
from app.core.config import settings
from app.db.session import Base, get_db
from app.main import app
from app.models.models import (
    OrdersStatus,
    OrdersTable,
    SkinCategory,
    SkinCurrency,
    SkinRarity,
    SkinsTable,
    UsersTable,
)

DB_URL = settings.DATABASE_URL
engine = create_engine(url=DB_URL)
SessionTesting = sessionmaker(autoflush=False, autocommit=False, bind=engine)


@pytest.fixture(autouse=True)
def create_tables():
    # usamos ahora las migraciones de alembic en la base de datos postgres de pruebas
    alembic_cfg = Config("alembic.ini")
    engine = create_engine(url=DB_URL)

    with engine.connect() as connection:
        connection.execute(text("DROP SCHEMA public CASCADE; CREATE SCHEMA public;"))
        connection.commit()
    engine.dispose()

    command.upgrade(alembic_cfg, "head")
    
    yield

@pytest.fixture
def get_db_test():
    db = SessionTesting()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def cliente():
    def get_db_test():
        db = SessionTesting()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = get_db_test
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(get_db_test):
    """Crea un usuario administrador directamente en la base de datos."""
    admin = UsersTable(
        email="admin@test.com",
        hashed_password="hashed_password_mock",  # O usa tu función de hash real
        role="admin",  # O el enum/valor que use tu sistema para administradores
        created_at=datetime.now(UTC),
    )
    get_db_test.add(admin)
    get_db_test.commit()
    get_db_test.refresh(admin)
    return admin


@pytest.fixture
def admin_token_headers(admin_user):
    """Genera los headers de autenticación para el admin."""
    # Genera el token usando tu lógica real de seguridad
    token = create_access_token(data={"sub": admin_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_skin(get_db_test):
    """Crea una skin directamente en la BD para probar consultas (GET)."""
    # Ajusta los campos según tu modelo real de SkinTable
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
    get_db_test.add(skin)
    get_db_test.commit()
    get_db_test.refresh(skin)
    return skin


@pytest.fixture
def normal_user(get_db_test):
    """Crea un usuario regular para las pruebas del carrito."""
    user = UsersTable(
        email="user@test.com",
        hashed_password="hashed_password_mock",
        created_at=datetime.now(UTC),
    )
    get_db_test.add(user)
    get_db_test.commit()
    get_db_test.refresh(user)
    return user


@pytest.fixture
def user_token_headers(normal_user):
    """Genera los headers de autenticación para el usuario regular."""
    token = create_access_token(data={"sub": normal_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def sample_order(get_db_test, normal_user, sample_skin):
    """Crea una orden directamente en la BD para probar consultas y pagos."""
    order = OrdersTable(
        user_id=normal_user.id,
        status=OrdersStatus.PENDING_PAYMENT,  # O el estado inicial que maneje tu app
        total_amount=sample_skin.price,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(minutes=10),
    )
    get_db_test.add(order)
    get_db_test.commit()
    get_db_test.refresh(order)
    return order