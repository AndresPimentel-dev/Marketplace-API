from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.security import decode_token
from app.db.session import get_db
from app.models.models import UsersTable
from app.repositories.user_repository import UserRepository
from app.schemas.enums import UserRole
from app.services.auth_service import AuthService

oauth_scheme = OAuth2PasswordBearer(tokenUrl="/api/v5.0/auth/login")


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:  # noqa: B008
    user_repo = UserRepository(db=db)

    return user_repo


def get_current_user(
    token: str = Depends(oauth_scheme),
    user_repo: UserRepository = Depends(get_user_repo),  # noqa: B008
) -> UsersTable:
    data = decode_token(token=token)

    if data is None or data["token_type"] != "access":
        raise UnauthorizedException(message="unauthenticated")

    user = user_repo.get_user_by_email(data["email"])

    if user is None:
        raise UnauthorizedException(message="unauthenticated")

    return user


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:  # noqa: B008
    user_repo = UserRepository(db=db)

    return AuthService(user_repo, db)


def require_admin(
    current_user=Depends(get_current_user),  # noqa: B008
) -> UsersTable:
    if current_user.role != UserRole.ADMIN:
        raise ForbiddenException(message="Admin privileges required")

    return current_user
