from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies.auth_dependencies import get_auth_service, get_current_user
from app.models.models import UsersTable
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
)
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v5.0", tags=["Authentication"])

# ==============================================================
#            ENDPOINTS DE AUTENTICACION
# ==============================================================


@router.post("/auth/register", status_code=201, response_model=TokenResponse)
def register_user_endpoint(
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> TokenResponse:

    return auth_service.register_user(user_create=data)


@router.post("/auth/login", status_code=200, response_model=TokenResponse)
# puedo usar el modelo de pydantic que cree o el from de security aqui uso el de requestfrom
# para que probrar los endpoints me sea mucho mas facil
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),  # noqa: B008
    auth_service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> TokenResponse:
    # convierto el from data de requestform en el modelo que espera el servicio y no conservo todo
    data = LoginRequest(
        email=form_data.username,  # en este caso seria username por que asi lo registra el request from
        # pero hay podria poner el email sin problema
        password=form_data.password,
    )

    return auth_service.login_user(login_request=data)


@router.post("/auth/refresh", response_model=TokenResponse, status_code=200)
def refresh_token(
    data: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),  # noqa: B008
) -> TokenResponse:

    return auth_service.refresh_token(refresh_token=data.refresh_token)


@router.get("/auth/me", status_code=200, response_model=UserResponse)
def get_loged_user(
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
) -> UserResponse:

    return current_user


@router.post("/auth/logout", status_code=204)
def logout_user(
    current_user: UsersTable = Depends(get_current_user),  # noqa: B008
):
    return Response(status_code=204)
