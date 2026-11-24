from enum import Enum


class SkinRarity(str, Enum):
    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class SkinCategory(str, Enum):
    WEAPON = "weapon"
    CHARACTER = "character"
    EMOTE = "emote"
    BANNER = "banner"
    COLLECTIBLE = "collectible"


class SkinCurrency(str, Enum):
    COLOMBIAN_PESOS = "COP"
    DOLLARS = "USD"
    EUROS = "EUR"
    AUS_DOLLAR = "AUD"
    YEN = "YEN"


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class OrderStatus(str, Enum):
    PENDING_PAYMENT = "pending_payment"
    PAYMENT_CONFIRMED = "payment_confirmed"
    PAYMENT_FAILED = "payment_failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    COMPLETED = "completed"
