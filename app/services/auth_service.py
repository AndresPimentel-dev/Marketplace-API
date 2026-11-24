from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate


class AuthService:
    def __init__(self, user_repository: UserRepository, db: Session):
        self.user_repository = user_repository
        self.db = db

    def register_user(self, user_create: UserCreate) -> TokenResponse:
        existing = self.user_repository.get_user_by_email(user_create.email)
        if existing:
            raise ConflictException(message="Email already used")
        hashed_password = hash_password(user_create.password)
        new = self.user_repository.create_user(user_create.email, hashed_password)
        self.db.commit()
        return TokenResponse(
            access_token=create_access_token(data={"sub": new.email}),
            refresh_token=create_refresh_token(data={"sub": new.email}),
            token_type="bearer",
        )

    def login_user(self, login_request: LoginRequest) -> TokenResponse:
        user = self.user_repository.get_user_by_email(login_request.email)
        if user is None or not verify_password(
            login_request.password, user.hashed_password
        ):
            raise UnauthorizedException(message="Invalid email or password")
        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        return TokenResponse(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    def refresh_token(self, refresh_token: str) -> TokenResponse:
        data = decode_token(token=refresh_token)
        if data is None or data.get("token_type") != "refresh":
            raise UnauthorizedException(message="unauthorized")
        email = data["email"]
        user = self.user_repository.get_user_by_email(email=email)
        if user is None or not user.is_active:
            raise UnauthorizedException(message="unauthorized")
        new_access_token = create_access_token(data={"sub": user.email})
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
