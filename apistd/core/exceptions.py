import traceback
import sys
import linecache
from typing import Any, Optional, List, Dict
from apistd.core.response import ErrorResponse
from apistd.core.status import HTTPStatusMapper


def _get_traceback_list(exc: Exception) -> List[Dict]:
    tb_list = []
    for tb in traceback.extract_tb(exc.__traceback__):
        tb_list.append({
            "file": tb.filename,
            "line": tb.lineno,
            "function": tb.name,
            "code": tb.line
        })
    return tb_list


def _get_current_traceback() -> List[Dict]:
    tb_list = []
    for frame_summary in traceback.extract_stack():
        tb_list.append({
            "file": frame_summary.filename,
            "line": frame_summary.lineno,
            "function": frame_summary.name,
            "code": frame_summary.line
        })
    return tb_list


class APIException(Exception):
    def __init__(
        self,
        message: str,
        code: int = 500,
        status_code: int = 500,
        error_detail: Any = None,
        context: Dict = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.error_detail = error_detail
        self.context = context or {}

    def to_response(self, debug: bool = False) -> ErrorResponse:
        exc_type = type(self).__name__
        error_detail = self.error_detail or {}

        if debug:
            if isinstance(error_detail, dict):
                enhanced_detail = {
                    "type": exc_type,
                    "message": self.message,
                    "traceback": _get_traceback_list(self),
                }
                if self.context:
                    enhanced_detail["context"] = self.context
                enhanced_detail.update(error_detail)
            else:
                enhanced_detail = {
                    "type": exc_type,
                    "message": self.message,
                    "detail": error_detail,
                    "traceback": _get_traceback_list(self),
                    "context": self.context
                }
        else:
            if isinstance(error_detail, dict):
                enhanced_detail = {
                    "type": exc_type,
                    "message": self.message,
                }
                if self.context:
                    enhanced_detail["context"] = self.context
                enhanced_detail.update(error_detail)
            else:
                enhanced_detail = {
                    "type": exc_type,
                    "message": self.message,
                    "detail": error_detail,
                    "context": self.context
                }

        return ErrorResponse(
            message=self.message,
            code=self.code,
            error_detail=enhanced_detail
        )


class ValidationError(APIException):
    def __init__(self, message: str = "Validation failed", error_detail: Any = None, context: Dict = None):
        super().__init__(
            message=message,
            code=422,
            status_code=422,
            error_detail=error_detail,
            context=context
        )


class AuthenticationError(APIException):
    def __init__(self, message: str = "Authentication failed", error_detail: Any = None, context: Dict = None):
        super().__init__(
            message=message,
            code=401,
            status_code=401,
            error_detail=error_detail,
            context=context
        )


class AuthorizationError(APIException):
    def __init__(self, message: str = "Access denied", error_detail: Any = None, context: Dict = None):
        super().__init__(
            message=message,
            code=403,
            status_code=403,
            error_detail=error_detail,
            context=context
        )


class NotFoundError(APIException):
    def __init__(self, message: str = "Resource not found", error_detail: Any = None, context: Dict = None):
        super().__init__(
            message=message,
            code=404,
            status_code=404,
            error_detail=error_detail,
            context=context
        )


class InternalError(APIException):
    def __init__(self, message: str = "Internal server error", error_detail: Any = None, context: Dict = None):
        super().__init__(
            message=message,
            code=500,
            status_code=500,
            error_detail=error_detail,
            context=context
        )


class DatabaseError(APIException):
    def __init__(self, message: str = "Database error", error_detail: Any = None, context: Dict = None):
        super().__init__(
            message=message,
            code=500,
            status_code=500,
            error_detail=error_detail,
            context=context
        )
