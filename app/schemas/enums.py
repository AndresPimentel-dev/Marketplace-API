from enum import Enum


class SkinRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class SkinCategory(str, Enum):
    WEAPON = "weapon"
    CHARACTHER = "character"
    EMOTE = "emote"
    BANNER = "banner"
    COLLECTIBLE = "collectible"


class SkinCurrency(str, Enum):
    COLOMBIN_PESOS = "COP"
    DOLLARS = "USD"
    EUROS = "EUR"
    AUS_DOLLAR = "AUSD"
    YEN = "YEN"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "PEDING_PAYMENT"
    PAYMENT_CONFIRMED = "PAYMET_CONFIRMED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"
