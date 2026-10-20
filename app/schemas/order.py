from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.skin import SkinCurrency, SkinResponse


class OrdersStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_FAILED = "payment_failed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class OrderItemResponse(BaseModel):
    id: int = Field(description="order Item ID")
    order_id: int = Field(description="Order ID")
    skin_id: int = Field(description="Skin ID")
    skin: SkinResponse = Field(description="Skin")
    quantity: int = Field(description="Purchased quantity")
    unit_price: float = Field(description="price")
    subtotal: float = Field(description="subtotal")

    model_config = {"from_attributes": True}


class OrderResponse(BaseModel):
    id: int = Field(description="order unique ID")
    user_id: int = Field(description="User ID")
    status: OrdersStatus = Field(description="current order state")
    total_amount: float = Field(description="total order price")
    currency: SkinCurrency = Field(description="currency of thge order")
    expires_at: datetime
    items: list[OrderItemResponse] = Field(description="list of items")

    model_config = ConfigDict(from_attributes=True)


class OrderListResponse(BaseModel):
    orders: list[OrderResponse]


class PaymentCreateRequest(BaseModel):
    order_id: int
    payment_method: str = Field(
        "mock_card", description="Método de pago simulado", min_length=1, max_length=50
    )
