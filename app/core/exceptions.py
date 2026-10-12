"""Custom exceptions"""


class AppException(Exception):
    """Base application exception"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class UnauthorizedException(AppException):
    """401 Unauthorized"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, status_code=401)


class ForbiddenException(AppException):
    """403 Forbidden"""

    def __init__(self, message: str = "Forbidden"):
        super().__init__(message, status_code=403)


class NotFoundException(AppException):
    """404 Not Found"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)


class ConflictException(AppException):
    """409 Conflict"""

    def __init__(self, message: str = "Conflict"):
        super().__init__(message, status_code=409)


class ValidationException(AppException):
    """400 Bad Request"""

    def __init__(self, message: str = "Validation error"):
        super().__init__(message, status_code=400)

