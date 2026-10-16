from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.skin import SkinResponse


class CartItemCreate(BaseModel):
    # el usuario solo envia estos datos el carrito se encarga de
    # crearlo el backewnd
    skin_id: int = Field(description="ID of the skin")
    quantity: int = Field(description="quantity of items", gt=0)
    model_config = {"json_schema_extra": {"examples": [{"skin_id": 2, "quantity": 5}]}}


class CartItemResponse(BaseModel):
    id: int = Field(description="cart item ID")
    cart_id: int = Field(description="cart ID")
    skin_id: int = Field(description="skin ID")
    quantity: int = Field(description="quantity")
    skin: SkinResponse = Field(description="skin details")

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    id: int = Field(description="cart ID")
    created_at: datetime = Field(description="cart creation date")
    updated_at: datetime = Field(description="cart update date ")
    items: list[CartItemResponse] = Field(description="items in cart")
    user_id: int = Field(description="user ID")

    model_config = ConfigDict(from_attributes=True)


class UpdateItemQuantity(BaseModel):
    quantity: int = Field(description=" new quantity", gt=0)
    model_config = {"json_schema_extra": {"examples": [{"quantity": 5}]}}
