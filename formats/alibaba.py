import time
from typing import Any, Optional, Dict
from pydantic import BaseModel, ConfigDict


class AlibabaFormat(BaseModel):
    model_config = ConfigDict(extra='allow')

    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp or int(time.time())
        }


class StandardFormat(BaseModel):
    model_config = ConfigDict(extra='allow')

    code: int = 200
    message: str = "success"
    data: Any = None
    timestamp: float = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp or time.time()
        }


class SimpleFormat(BaseModel):
    model_config = ConfigDict(extra='allow')

    code: int = 200
    message: str = "success"
    data: Any = None

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }


FORMATTERS = {
    "alibaba": AlibabaFormat,
    "standard": StandardFormat,
    "simple": SimpleFormat,
}


def get_formatter(format_name: str):
    return FORMATTERS.get(format_name, StandardFormat)
