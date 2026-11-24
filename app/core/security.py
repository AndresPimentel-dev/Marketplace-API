from datetime import UTC, datetime, timedelta

import jwt
from pwdlib import PasswordHash

from app.core.config import settings

password_hash_context = PasswordHash.recommended()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKENS_EXPIRE_MINUTES = 15


## Funciones de hashing
def hash_password(password: str) -> str:
    return password_hash_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash_context.verify(plain_password, hashed_password)


## Funciones de tokens


def create_access_token(data: dict) -> str:
    datos_a_firmar = data.copy()

    # Le agregamos una fecha de expiración al token
    expiracion = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKENS_EXPIRE_MINUTES)
    datos_a_firmar.update({"exp": expiracion, "type": "access"})

    # Creamos y firmamos el token usando PyJWT
    token = jwt.encode(datos_a_firmar, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(data: dict) -> str:
    datos_a_firmar = data.copy()

    # Le agregamos una fecha de expiración al token
    expiracion = datetime.now(UTC) + timedelta(days=7)
    datos_a_firmar.update({"exp": expiracion, "type": "refresh"})

    # Creamos y firmamos el token usando PyJWT
    token = jwt.encode(datos_a_firmar, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")
        exp = payload.get("exp")
        if not email or not token_type or not exp:
            return None
    except jwt.InvalidTokenError:
        return None
    return {"email": email, "token_type": token_type, "exp": exp}
