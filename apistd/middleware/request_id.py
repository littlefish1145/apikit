import uuid
import time
from contextvars import ContextVar
from typing import Optional

_request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
_request_start_time_var: ContextVar[Optional[float]] = ContextVar('request_start_time', default=None)


class RequestIDMiddleware:
    def __init__(self, header_name: str = "X-Request-ID"):
        self.header_name = header_name
        self._request_id: Optional[str] = None

    def process_request(self, request) -> None:
        self._request_id = request.headers.get(self.header_name)
        if not self._request_id:
            self._request_id = str(uuid.uuid4())
        _request_id_var.set(self._request_id)
        _request_start_time_var.set(time.time())

    def process_response(self, request, response) -> None:
        if self._request_id:
            response.headers[self.header_name] = self._request_id

    def get_request_id(self) -> str:
        return self._request_id or ""


def get_request_id() -> str:
    return _request_id_var.get() or ""


def set_request_id(request_id: str) -> None:
    _request_id_var.set(request_id)


def get_request_start_time() -> float:
    return _request_start_time_var.get() or time.time()


def set_request_start_time(start_time: float) -> None:
    _request_start_time_var.set(start_time)
