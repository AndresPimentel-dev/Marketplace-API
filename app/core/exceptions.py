class BusinessException(Exception):
    """Excepción base para errores de negocio controlados."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(BusinessException):
    """Usado cuando un recurso no existe en la BD (404)."""

    def __init__(self, message: str = "Recurso no encontrado"):
        super().__init__(message=message, status_code=404)


class BadRequestException(BusinessException):
    """Usado cuando la petición rompe una regla de negocio (400).
    Ej: Intentar comprar más stock del disponible, carrito vacío al pagar."""

    def __init__(self, message: str = "Petición incorrecta"):
        super().__init__(message=message, status_code=400)


class ConflictException(BusinessException):
    """Usado cuando hay un conflicto de estado (409).
    Ej: El usuario ya tiene un carrito activo, o intenta registrar un email que ya existe."""

    def __init__(self, message: str = "Conflicto en la operación"):
        super().__init__(message=message, status_code=409)


class UnauthorizedException(BusinessException):
    """Usado cuando el usuario no está autenticado o su token expiró (401)."""

    def __init__(self, message: str = "No autorizado"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(BusinessException):
    """Usado cuando el usuario está autenticado pero NO tiene permisos (403).
    Ej: Un cliente normal intentando borrar un producto del catálogo."""

    def __init__(self, message: str = "Acceso denegado"):
        super().__init__(message=message, status_code=403)
