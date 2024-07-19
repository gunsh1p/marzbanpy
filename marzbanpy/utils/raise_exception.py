from ..marzban_response import MarzbanResponse
from ..exceptions import (
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    ConflictError,
    ValidationError,
)


def raise_exception_on_status(response: MarzbanResponse) -> None:
    match response.status:
        case 200:
            return None
        case 401:
            raise UnauthorizedError()
        case 403:
            raise ForbiddenError()
        case 404:
            detail: str = response.content["detail"]
            raise NotFoundError(detail)
        case 409:
            detail: str = response.content["detail"]
            raise ConflictError(detail)
        case 422:
            detail: dict = response.content["detail"]
            raise ValidationError(detail)
