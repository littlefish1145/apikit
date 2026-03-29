from typing import Callable, Optional, Any
from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from apistd.core.response import Response, SuccessResponse, ErrorResponse
from apistd.core.exceptions import APIException
from apistd.framework.base import FrameworkAdapter
from apistd.config import get_config


class FastAPIAdapter(FrameworkAdapter):
    def __init__(self):
        self.app: Optional[FastAPI] = None
        self.config: dict = {}

    def install(self, app: FastAPI, config: dict = None) -> None:
        self.app = app
        if config:
            self.config = config

        app.add_middleware(BaseHTTPMiddleware, dispatch=self._middleware_dispatch)
        app.add_exception_handler(APIException, self._handle_api_exception)

    async def _middleware_dispatch(self, request: Request, call_next):
        from apistd.middleware.request_id import RequestIDMiddleware
        from apistd.middleware.timer import TimerMiddleware
        from apistd.middleware.debug import DebugMiddleware

        config = get_config()

        request_id_middleware = RequestIDMiddleware(
            header_name=config.request_id_header
        )
        timer_middleware = TimerMiddleware(
            threshold_ms=config.slow_query_threshold
        )
        debug_middleware = DebugMiddleware(enabled=config.debug)

        request_id_middleware.process_request(request)
        response = await call_next(request)
        timer_middleware.process_response(request, response)

        if config.debug:
            debug_middleware.process_response(request, response)

        response.headers["X-Request-ID"] = request_id_middleware.get_request_id()
        return response

    async def _handle_api_exception(self, request: Request, exc: APIException):
        error_response = exc.to_response()
        return JSONResponse(
            content=error_response.to_dict(),
            status_code=exc.status_code
        )

    def response_handler(self, response: Response) -> JSONResponse:
        http_status = 200 if response.code == 0 else 500
        return JSONResponse(
            content=response.to_dict(),
            status_code=http_status
        )

    def error_handler(self, exception: Exception) -> ErrorResponse:
        if isinstance(exception, APIException):
            return exception.to_response()
        return ErrorResponse(message=str(exception), code=-1)


class APIResponse:
    def __init__(
        self,
        success: bool = True,
        message: str = "Success",
        data: Any = None
    ):
        self.success = success
        self.message = message
        self.data = data

    def to_response(self) -> JSONResponse:
        if self.success:
            response = SuccessResponse(data=self.data, message=self.message)
        else:
            response = ErrorResponse(message=self.message, code=-1)
        return JSONResponse(
            content=response.to_dict(),
            status_code=200 if self.success else 500
        )


def inject_response(config: dict = None) -> Callable:
    def dependency(
        success: bool = True,
        message: str = "Success",
        data: Any = None
    ) -> APIResponse:
        return APIResponse(success=success, message=message, data=data)
    return dependency
