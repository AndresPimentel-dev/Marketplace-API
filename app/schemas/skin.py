from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.enums import SkinCategory, SkinCurrency, SkinRarity


class SkinCreate(BaseModel):
    name: str = Field(description="skins name", min_length=1, max_length=50)
    slug: str = Field(description="skin slug", min_length=1, max_length=100)
    description: str = Field(
        description="skin description", min_length=1, max_length=255
    )
    ########## en los enums no se una min o max lenght
    category: SkinCategory = Field(description="skin category")
    rarity: SkinRarity = Field(description="skin rarity")
    price: Decimal = Field(
        description="price of skin",
        gt=0,  # es solo mayor a 0
    )
    currency: SkinCurrency = Field(description="currency skin")
    stock_total: int = Field(
        description="total stock avaible",
        ge=0,  ### significa que debe ser mayor o 0
    )
    is_limited: bool = Field(description="Is a limated objects?")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
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
            ]
        }
    }


class SkinResponse(BaseModel):
    id: int = Field(description="Skin unique ID")
    name: str = Field(description="skin name", min_length=1, max_length=50)
    slug: str = Field(description="skin slug", min_length=1, max_length=100)
    description: str = Field(
        description="skin description", min_length=1, max_length=255
    )
    category: SkinCategory = Field(description="skin category")
    rarity: SkinRarity = Field(description="skin rarity")
    price: Decimal = Field(description="skin price")
    currency: SkinCurrency = Field(description=" skin currency")
    stock_total: int = Field(description="total sotck")
    stock_reserved: int = Field(description="reserved stock")
    stock_sold: int = Field(description="sold stock")
    is_limited: bool = Field(description="is limited object")
    is_active: bool = Field(description="is active")

    model_config = ConfigDict(from_attributes=True)


class SkinListResponse(BaseModel):
    skins: list[SkinResponse]

    model_config = ConfigDict(from_attributes=True)


class SkinUpdate(BaseModel):
    name: str | None = Field(
        description="skins name",
        min_length=1,  # optional devuelve None y puede error
        max_length=50,
        default=None,
    )
    description: str | None = Field(
        description="skin description", min_length=1, max_length=255, default=None
    )
    category: SkinCategory | None = Field(description="skin category", default=None)
    rarity: SkinRarity | None = Field(description="skin rarity", default=None)
    price: Decimal | None = Field(description="price of skin", gt=0, default=None)
    currency: SkinCurrency | None = Field(description="currency skin", default=None)
    is_limited: bool | None = Field(description="Is a limated objects?", default=None)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "reaper",
                    "description": "Character",
                    "category": "character",
                    "rarity": "legendary",
                    "price": "14.99",
                    "currency": "usd",
                    "is_limited": True,
                }
            ]
        }
    }
