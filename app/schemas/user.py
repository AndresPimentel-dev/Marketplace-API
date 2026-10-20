from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.enums import UserRole


class UserResponse(BaseModel):
    id: int = Field(description="User unique ID")
    email: EmailStr = Field(description="User email", max_length=50)
    role: UserRole = Field(description="User role")
    model_config = ConfigDict(from_attributes=True)
