import logging
from typing import Optional, Any
from starlette.requests import Request

logger = logging.getLogger("apistd")


class DebugMiddleware:
    def __init__(self, enabled: bool = None):
        self.enabled = enabled

    def process_request(self, request: Request) -> None:
        if not self.enabled:
            return

        logger.debug(f"Request: {request.method} {request.url.path}")

    def process_response(self, request: Request, response: Any) -> None:
        if not self.enabled:
            return

        debug_info = {
            "path": request.url.path,
            "method": request.method,
        }
        response.headers["X-Debug-Info"] = str(debug_info)
        logger.debug(f"Response debug info: {debug_info}")
