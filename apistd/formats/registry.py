import time
from typing import Any, Callable, Dict


class ResponseFormatterRegistry:
    _formatters: Dict[str, Callable] = {}
    _default_format: str = "default"

    @classmethod
    def register(cls, name: str, formatter: Callable) -> None:
        cls._formatters[name] = formatter

    @classmethod
    def get(cls, name: str) -> Callable:
        return cls._formatters.get(name)

    @classmethod
    def list_formatters(cls) -> list:
        return list(cls._formatters.keys())

    @classmethod
    def set_default(cls, name: str) -> None:
        if name in cls._formatters:
            cls._default_format = name

    @classmethod
    def get_default(cls) -> str:
        return cls._default_format


def register_format(name: str, formatter: Callable) -> None:
    ResponseFormatterRegistry.register(name, formatter)


def _default_formatter(code: int, message: str, data: Any, debug_info: Dict = None) -> dict:
    from apistd.core.constants import ResponseFields
    result = {
        ResponseFields.CODE: code,
        ResponseFields.MESSAGE: message,
        ResponseFields.DATA: data,
        ResponseFields.TIMESTAMP: time.time()
    }
    if debug_info:
        result["_debug"] = debug_info
    return result


def _simple_formatter(code: int, message: str, data: Any, debug_info: Dict = None) -> dict:
    result = {
        "code": code,
        "message": message,
        "data": data
    }
    if debug_info:
        result["_debug"] = debug_info
    return result


def _alibaba_formatter(code: int, message: str, data: Any, debug_info: Dict = None) -> dict:
    result = {
        "code": code,
        "message": message,
        "data": data,
        "timestamp": int(time.time())
    }
    if debug_info:
        result["_debug"] = debug_info
    return result


ResponseFormatterRegistry.register("default", _default_formatter)
ResponseFormatterRegistry.register("simple", _simple_formatter)
ResponseFormatterRegistry.register("alibaba", _alibaba_formatter)
