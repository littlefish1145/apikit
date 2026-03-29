from typing import Any, Optional
from apistd.core.response import ErrorResponse
from apistd.core.status import HTTPStatusMapper


class APIException(Exception):
    def __init__(
        self,
        message: str,
        code: int = -1,
        status_code: int = 500,
        error_detail: Any = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.error_detail = error_detail

    def to_response(self) -> ErrorResponse:
        return ErrorResponse(
            message=self.message,
            code=self.code,
            error_detail=self.error_detail
        )


class ValidationError(APIException):
    def __init__(self, message: str = "Validation failed", error_detail: Any = None):
        super().__init__(
            message=message,
            code=1001,
            status_code=422,
            error_detail=error_detail
        )


class AuthenticationError(APIException):
    def __init__(self, message: str = "Authentication failed", error_detail: Any = None):
        super().__init__(
            message=message,
            code=1002,
            status_code=401,
            error_detail=error_detail
        )


class AuthorizationError(APIException):
    def __init__(self, message: str = "Access denied", error_detail: Any = None):
        super().__init__(
            message=message,
            code=1003,
            status_code=403,
            error_detail=error_detail
        )


class NotFoundError(APIException):
    def __init__(self, message: str = "Resource not found", error_detail: Any = None):
        super().__init__(
            message=message,
            code=1004,
            status_code=404,
            error_detail=error_detail
        )


class InternalError(APIException):
    def __init__(self, message: str = "Internal server error", error_detail: Any = None):
        super().__init__(
            message=message,
            code=5000,
            status_code=500,
            error_detail=error_detail
        )
