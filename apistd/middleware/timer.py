import time
from contextvars import ContextVar
from typing import Optional

_execution_time_var: ContextVar[Optional[float]] = ContextVar('execution_time', default=None)


class TimerMiddleware:
    def __init__(self, threshold_ms: float = 1000):
        self.threshold_ms = threshold_ms
        self._start_time: float = 0
        self._execution_time: float = 0

    def process_request(self, request) -> None:
        self._start_time = time.perf_counter()

    def process_response(self, request, response) -> None:
        self._execution_time = (time.perf_counter() - self._start_time) * 1000
        response.headers["X-Execution-Time"] = f"{self._execution_time:.2f}ms"
        _execution_time_var.set(self._execution_time)

        if self._execution_time > self.threshold_ms:
            import logging
            logger = logging.getLogger("apistd")
            logger.warning(
                f"Slow request detected: {request.url.path} took {self._execution_time:.2f}ms"
            )

    def get_execution_time(self) -> float:
        return self._execution_time


def get_execution_time() -> float:
    return _execution_time_var.get() or 0
