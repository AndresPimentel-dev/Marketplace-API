from datetime import date

from pydantic import BaseModel, Field

from app.schemas.skin import SkinResponse


class InventoryItemResponse(BaseModel):
    user_id: int = Field(description="User unique ID")
    skin_id: int = Field(description="Skin unique ID")
    acquired_at: date = Field(description="date of acquirement")
    order_id: int = Field(description="Order unique ID")


class InventoryResponse(BaseModel):
    user_id: int = Field(description="User unique ID")
    skins: list[SkinResponse] = Field(description="User unique ID")
