class MarzbanError(Exception):
    """Base exception for all Marzban errors"""

    code: int

    def __str__(self) -> str:
        return str(self.code)

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self}')"


class DetailedMarzbanError(MarzbanError):
    """Base exception for all Marzban errors with detailed message"""

    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        message = f"HTTP error code: {self.code}, Message: '{self.message}'"
        return message

    def __repr__(self) -> str:
        return f"{type(self).__name__}('{self}')"


class UnauthorizedError(MarzbanError):
    """Exception raised when token is invalid"""

    code = 401


class ForbiddenError(MarzbanError):
    """Exception raised when you are not allowed"""

    code = 403


class NotFoundError(DetailedMarzbanError):
    """Exception raised when object is not found"""

    code = 404


class ConflictError(DetailedMarzbanError):
    """Exception raised when object already exists"""

    code = 409


class ValidationError(DetailedMarzbanError):
    """Exception raised when there is a validation error in request body"""

    code = 422

    def __init__(self, detail: dict) -> None:
        self.message = ";".join([f"{k}: {v}" for k, v in detail.items()])
