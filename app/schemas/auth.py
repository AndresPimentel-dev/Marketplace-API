from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr = Field(description="User email", min_length=1, max_length=50)
    password: str = Field(description="Secure password", min_length=8, max_length=100)
    model_config = {
        "json_schema_extra": {
            "examples": [
                {"email": "Fakeemail@gmail.com", "password": "Fakepassword123"}
            ]
        }
    }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


####refreshtoken@#############


class TokenResponse(BaseModel):
    access_token: str = Field(description="access token in str")
    refresh_token: str = Field(description="refresh token")
    token_type: str = Field(description="token type")


class RefreshTokenRequest(BaseModel):
    refresh_token: str
