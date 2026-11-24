from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UsersTable(Base):
    __tablename__ = "userstable"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(
        String(50), index=True, unique=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SqlEnum(UserRole), default=UserRole.USER, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    cart: Mapped["CartsTable"] = relationship(back_populates="owner", uselist=False)
    orders: Mapped[list["OrdersTable"]] = relationship(back_populates="assignee_user")
    inventoryitems: Mapped[list["InventoryItemsTable"]] = relationship(
        back_populates="owner"
    )


class SkinCategory(str, Enum):
    WEAPON = "weapon"
    CHARACTHER = "character"
    EMOTE = "emote"
    BANNER = "banner"
    COLLECTIBLE = "collectible"


class SkinRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class SkinCurrency(str, Enum):
    COLOMBIAN_PESOS = "COP"
    DOLLARS = "USD"
    EUROS = "EUR"
    AUS_DOLLAR = "AUD"
    YEN = "YEN"


class SkinsTable(Base):
    __tablename__ = "skinstable"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[SkinCategory] = mapped_column(
        SqlEnum(SkinCategory), nullable=False
    )
    rarity: Mapped[SkinRarity] = mapped_column(SqlEnum(SkinRarity), nullable=False)
    # precision la cantidad maxima de digitos que puede tener y scale que siempre habra dos decimales.
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    currency: Mapped[SkinCurrency] = mapped_column(
        SqlEnum(SkinCurrency), nullable=False, default=SkinCurrency.DOLLARS
    )
    stock_total: Mapped[int] = mapped_column(Integer, nullable=False)
    # anado una restriccion para evaluar que el stock no sea menor a cero o negativo
    stock_reserved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    stock_sold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    # se juntan todos en el mismo no diferentes
    __table_args__ = (
        CheckConstraint("stock_total >= 0", name="check_stock_total_non_negative"),
        CheckConstraint(
            "stock_reserved >= 0", name="check_stock_reserved_non_negative"
        ),
        CheckConstraint("stock_sold >= 0", name="check_stock_sold_non_negative"),
    )
    is_limited: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # se usa datetime ya que en pidantic usamos tambien datetime y ese viene con fecha y hora todo
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    # agregar timezone
    cart_items: Mapped[list["CartItemsTable"]] = relationship(back_populates="skin")

    order_items: Mapped[list["OrdersItemsTable"]] = relationship(back_populates="skin")

    inventory_items: Mapped[list["InventoryItemsTable"]] = relationship(
        back_populates="skin"
    )


class CartsTable(Base):
    __tablename__ = "cartstable"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user_id: Mapped[int] = mapped_column(
        ForeignKey("userstable.id"), nullable=False, unique=True
    )
    owner: Mapped["UsersTable"] = relationship(back_populates="cart")

    # agregamos all delete orphan para que borre los items cuando se borre el carrito
    # le decimos al orm que cuando borremos el carrito emita delete atodos lo items
    # el cascade=all significa lo que le pase al carrito aplicaselo a sus items
    # el delete orphan significa que si saco un item de mi carrito borrelo ya que queda huerfano
    items: Mapped[list["CartItemsTable"]] = relationship(
        back_populates="assignee_cart", cascade="all, delete-orphan"
    )


class CartItemsTable(Base):
    __tablename__ = "cartitemstable"

    id: Mapped[int] = mapped_column(primary_key=True)

    # esta es una intruccion que se le envia a la db donde le dices que si se borrra una columna
    # en la tabla de cartstable borre todas las filas en estya tabla que dependan de ella
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("cartstable.id", ondelete="CASCADE"), nullable=False
    )
    assignee_cart: Mapped["CartsTable"] = relationship(back_populates="items")

    skin_id: Mapped[int] = mapped_column(ForeignKey("skinstable.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_quantity_greater_0"),
        # aqui se le dice que no puede haber un carrito con dos skin iguales
        UniqueConstraint("cart_id", "skin_id", name="one_skin_per_cart_constrain"),
    )
    skin: Mapped["SkinsTable"] = relationship(back_populates="cart_items")


class OrdersStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_FAILED = "payment_failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class OrdersTable(Base):
    __tablename__ = "orderstable"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[OrdersStatus] = mapped_column(
        SqlEnum(OrdersStatus), nullable=False, default=OrdersStatus.PENDING_PAYMENT
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False, default=1.0
    )
    currency: Mapped[SkinCurrency] = mapped_column(
        SqlEnum(SkinCurrency), default=SkinCurrency.DOLLARS, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("userstable.id"))
    assignee_user: Mapped["UsersTable"] = relationship(back_populates="orders")
    Inventoryitems: Mapped[list["InventoryItemsTable"]] = relationship(
        back_populates="order"
    )
    items: Mapped[list["OrdersItemsTable"]] = relationship(
        back_populates="assignee_order", cascade="all, delete-orphan"
    )
    payment: Mapped["PaymentsTable"] = relationship(back_populates="order")


class OrdersItemsTable(Base):
    __tablename__ = "ordersitemstable"

    id: Mapped[int] = mapped_column(primary_key=True)

    # si se llega a desaparecer el id por que se borra la orden borramos todos sus hijos por eso ondelete
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orderstable.id", ondelete="CASCADE"), nullable=False
    )
    assignee_order: Mapped["OrdersTable"] = relationship(back_populates="items")
    skin: Mapped["SkinsTable"] = relationship(back_populates="order_items")

    skin_id: Mapped[int] = mapped_column(ForeignKey("skinstable.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)


class InventoryItemsTable(Base):
    __tablename__ = "inventoryitemstable"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("userstable.id"), nullable=False)
    owner: Mapped["UsersTable"] = relationship(back_populates="inventoryitems")
    skin_id: Mapped[int] = mapped_column(ForeignKey("skinstable.id"), nullable=False)
    skin: Mapped["SkinsTable"] = relationship(back_populates="inventory_items")
    order_id: Mapped[int] = mapped_column(ForeignKey("orderstable.id"), nullable=False)
    order: Mapped["OrdersTable"] = relationship(back_populates="Inventoryitems")
    acquired_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


# se guarda la operacion del pago y asociarlo a la orden y saber el status del pago
class PaymentsTable(Base):
    __tablename__ = "paymentstable"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orderstable.id"), nullable=False, unique=True
    )
    payment_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        SqlEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    order: Mapped["OrdersTable"] = relationship(back_populates="payment")


class ProcessedWebhookEventsTable(Base):
    __tablename__ = "processedwebhooksstable"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_id: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=True)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


# ====================================
#
# el flujo es usuario anade a su carrito las skins que quiere comprar, luego da en comprar
# en ese moento se genera una order en la cual cada item es cada skin que el usuario tenia en su carrito
# y tambien se crear un payment para guardar los estados de los pagos y se pone un defaul pending
# hay se llama al servicio de cobro el envia un id y tambien se guarda en payments
# luego el servicio envia los estados como un pago fallido o completado si no que lo envia muchas veces
# para evitar el problema de que cada vez que el servicio envie un pago se envie otra skin se guarda un evento
# en processedwebhookevents y cada que recive el actualizado de pago del servicio de pago hay consulta
# y si no esta lo crea y ya
# si ya existe no hace nada
#
# ===================================
