import time
from typing import Any, Dict, Optional


class RequestDataCollector:
    def __init__(self, request: Any):
        self.method: str = getattr(request, "method", "UNKNOWN")
        self.url: str = str(getattr(request, "url", ""))
        self.headers: Dict = dict(getattr(request, "headers", {}))
        self.body: Any = getattr(request, "body", None)
        self.query_params: Dict = getattr(request, "query_params", {})
        self.timestamp: float = time.time()

    def collect(self) -> Dict:
        return {
            "method": self.method,
            "url": self.url,
            "headers": dict(self.headers),
            "query_params": dict(self.query_params),
            "timestamp": self.timestamp,
        }


class ResponseDataCollector:
    def __init__(
        self,
        response: Any,
        status_code: int = None,
        execution_time: float = None
    ):
        self.status_code: int = status_code or getattr(response, "status_code", 200)
        self.headers: Dict = dict(getattr(response, "headers", {}))
        self.body: Any = getattr(response, "body", None)
        self.execution_time: float = execution_time or 0

    def collect(self) -> Dict:
        return {
            "status_code": self.status_code,
            "headers": self.headers,
            "execution_time": self.execution_time,
        }
