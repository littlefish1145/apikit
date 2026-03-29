import json
import time
from typing import Any, Optional, Dict
from apistd.core.constants import ResponseFields


class Response:
    def __init__(
        self,
        code: int = 0,
        message: str = "",
        data: Any = None,
        timestamp: float = None
    ):
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = timestamp or time.time()

    def to_dict(self) -> dict:
        result = {
            ResponseFields.CODE: self.code,
            ResponseFields.MESSAGE: self.message,
            ResponseFields.DATA: self.data,
            ResponseFields.TIMESTAMP: self.timestamp
        }
        if self.code != 0 and hasattr(self, 'error_detail'):
            result[ResponseFields.ERROR_DETAIL] = self.error_detail
        return result

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> 'Response':
        return cls(
            code=data.get(ResponseFields.CODE, 0),
            message=data.get(ResponseFields.MESSAGE, ""),
            data=data.get(ResponseFields.DATA),
            timestamp=data.get(ResponseFields.TIMESTAMP)
        )


class SuccessResponse(Response):
    def __init__(
        self,
        data: Any = None,
        message: str = "Success",
        code: int = 0
    ):
        super().__init__(code=code, message=message, data=data)


class ErrorResponse(Response):
    def __init__(
        self,
        message: str = "Error",
        code: int = -1,
        error_detail: Any = None
    ):
        super().__init__(code=code, message=message, data=None)
        self.error_detail = error_detail

    def to_dict(self) -> dict:
        result = super().to_dict()
        if self.error_detail is not None:
            result[ResponseFields.ERROR_DETAIL] = self.error_detail
        return result
