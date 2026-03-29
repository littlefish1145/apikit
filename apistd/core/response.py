import json
import time
import psutil
import os
from typing import Any, Optional, Dict
from apistd.core.constants import ResponseFields
from apistd.config import get_config
from apistd.formats.registry import ResponseFormatterRegistry


class Response:
    def __init__(
        self,
        code: int = 200,
        message: str = "",
        data: Any = None,
        timestamp: float = None
    ):
        self.code = code
        self.message = message
        self.data = data
        self.timestamp = timestamp or time.time()

    def to_dict(self, debug: bool = False) -> dict:
        config = get_config()
        format_name = config.response_format

        formatter = ResponseFormatterRegistry.get(format_name)
        if not formatter:
            format_name = ResponseFormatterRegistry.get_default()
            formatter = ResponseFormatterRegistry.get(format_name)

        debug_info = None
        if debug:
            debug_info = self._get_debug_info()

        return formatter(self.code, self.message, self.data, debug_info)

    def _get_debug_info(self) -> Dict:
        process = psutil.Process(os.getpid())
        return {
            "memory_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(),
            "timestamp": time.time()
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> 'Response':
        return cls(
            code=data.get(ResponseFields.CODE, 200),
            message=data.get(ResponseFields.MESSAGE, ""),
            data=data.get(ResponseFields.DATA),
            timestamp=data.get(ResponseFields.TIMESTAMP)
        )


class SuccessResponse(Response):
    def __init__(
        self,
        data: Any = None,
        message: str = "Success",
        code: int = 200
    ):
        super().__init__(code=code, message=message, data=data)


class ErrorResponse(Response):
    def __init__(
        self,
        message: str = "Error",
        code: int = 500,
        error_detail: Any = None
    ):
        super().__init__(code=code, message=message, data=None)
        self.error_detail = error_detail

    def to_dict(self, debug: bool = False) -> dict:
        config = get_config()
        format_name = config.response_format

        formatter = ResponseFormatterRegistry.get(format_name)
        if not formatter:
            format_name = ResponseFormatterRegistry.get_default()
            formatter = ResponseFormatterRegistry.get(format_name)

        debug_info = None
        if debug:
            debug_info = self._get_debug_info()

        result = formatter(self.code, self.message, self.data, debug_info)

        if self.error_detail is not None:
            if format_name == "alibaba":
                result["error_detail"] = self.error_detail
            else:
                result[ResponseFields.ERROR_DETAIL] = self.error_detail

        return result
