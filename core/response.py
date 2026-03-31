import time
import psutil
import os
from typing import Any, Optional, Dict

# Try to use optimized JSON serializer if available
try:
    from optimization import FastJSON
    _json_serializer = FastJSON()
    _use_optimization = True
except ImportError:
    import json
    _json_serializer = None
    _use_optimization = False

from core.constants import ResponseFields
from config import get_config
from formats.registry import ResponseFormatterRegistry


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
        """Convert response to JSON string using optimized serializer"""
        data = self.to_dict()
        
        if _use_optimization:
            # Use optimized FastJSON (orjson/ujson/json with optimizations)
            return _json_serializer.dumps(data).decode('utf-8')
        else:
            # Fallback to standard json
            import json
            return json.dumps(data, ensure_ascii=False, separators=(',', ':'))

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
