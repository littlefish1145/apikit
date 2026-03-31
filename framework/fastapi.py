import time
import psutil
import os
import traceback
from typing import Callable, Optional, Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import Response as StarletteResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Try to use optimized JSON serializer
try:
    from optimization import FastJSON
    _json_serializer = FastJSON()
    _use_optimization = True
except ImportError:
    import json
    _json_serializer = None
    _use_optimization = False

from core.response import Response, SuccessResponse, ErrorResponse
from core.exceptions import APIException
from framework.base import FrameworkAdapter
from config import get_config
from middleware.request_id import get_request_id, get_request_start_time


class FormattedJSONResponse(StarletteResponse):
    default_indent = 2
    default_ensure_ascii = False

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: dict = None,
        media_type: str = "application/json",
        background: Any = None,
        indent: int = None,
        ensure_ascii: bool = None
    ):
        self.indent = indent if indent is not None else self.default_indent
        self.ensure_ascii = ensure_ascii if ensure_ascii is not None else self.default_ensure_ascii
        super().__init__(content, status_code, headers, media_type, background)

    def render(self, content: Any) -> bytes:
        """Render content to JSON bytes using optimized serializer"""
        if _use_optimization and self.indent is None:
            # Use optimized serializer (no indent for performance)
            return _json_serializer.dumps(content)
        else:
            # Fallback to standard json (supports indent)
            import json
            return json.dumps(
                content,
                indent=self.indent,
                ensure_ascii=self.ensure_ascii,
                separators=(',', ':') if self.indent is None else None
            ).encode("utf-8")


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
        app.add_exception_handler(RequestValidationError, self._handle_validation_error)
        app.add_exception_handler(StarletteHTTPException, self._handle_http_exception)
        app.add_exception_handler(Exception, self._handle_generic_exception)

    async def _middleware_dispatch(self, request: Request, call_next):
        from middleware.request_id import RequestIDMiddleware

        config = get_config()
        start_time = time.time()

        request_id_middleware = RequestIDMiddleware(header_name=config.request_id_header)
        request_id_middleware.process_request(request)

        response = await call_next(request)

        execution_time = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id_middleware.get_request_id()
        response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"

        if config.debug:
            process = psutil.Process(os.getpid())
            memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
            response.headers["X-Debug-Memory"] = f"{memory_mb}MB"

        return response

    def _get_response(self, error_response: ErrorResponse, status_code: int):
        config = get_config()
        if config.debug:
            return FormattedJSONResponse(content=error_response.to_dict(debug=True), status_code=status_code)
        return FormattedJSONResponse(content=error_response.to_dict(debug=False), status_code=status_code)

    async def _handle_api_exception(self, request: Request, exc: APIException):
        config = get_config()
        error_response = exc.to_response(debug=config.debug)
        return self._get_response(error_response, exc.status_code)

    async def _handle_validation_error(self, request: Request, exc: RequestValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "loc": list(error.get("loc", [])),
                "msg": error.get("msg", ""),
                "type": error.get("type", ""),
                "input": error.get("input", ""),
            })

        error_response = ErrorResponse(
            message="Validation failed",
            code=422,
            error_detail={
                "type": "RequestValidationError",
                "errors": errors,
            }
        )
        return self._get_response(error_response, 422)

    async def _handle_http_exception(self, request: Request, exc: StarletteHTTPException):
        error_response = ErrorResponse(
            message=str(exc.detail) if exc.detail else self._get_http_message(exc.status_code),
            code=exc.status_code,
            error_detail={
                "type": "HTTPException",
                "status_code": exc.status_code,
            }
        )
        return self._get_response(error_response, exc.status_code)

    async def _handle_generic_exception(self, request: Request, exc: Exception):
        error_response = ErrorResponse(
            message=str(exc) or "Internal server error",
            code=500,
            error_detail={
                "type": type(exc).__name__,
                "exception": str(exc),
            }
        )
        return self._get_response(error_response, 500)

    def _get_http_message(self, status_code: int) -> str:
        messages = {
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
        }
        return messages.get(status_code, "HTTP Error")

    def response_handler(self, response: Response, debug: bool = False) -> StarletteResponse:
        config = get_config()
        debug = debug or config.debug

        if debug:
            return FormattedJSONResponse(content=response.to_dict(debug=debug), status_code=response.code)
        return FormattedJSONResponse(content=response.to_dict(debug=debug), status_code=response.code)

    def error_handler(self, exception: Exception, debug: bool = False) -> ErrorResponse:
        if isinstance(exception, APIException):
            return exception.to_response(debug=debug)
        return ErrorResponse(message=str(exception), code=500)


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

    def to_response(self, debug: bool = False) -> StarletteResponse:
        if self.success:
            response = SuccessResponse(data=self.data, message=self.message)
        else:
            response = ErrorResponse(message=self.message, code=500)

        config = get_config()
        debug = debug or config.debug

        if debug:
            return FormattedJSONResponse(content=response.to_dict(debug=debug), status_code=200 if self.success else 500)
        return FormattedJSONResponse(content=response.to_dict(debug=debug), status_code=200 if self.success else 500)


def inject_response(config: dict = None) -> Callable:
    def dependency(
        success: bool = True,
        message: str = "Success",
        data: Any = None
    ) -> APIResponse:
        return APIResponse(success=success, message=message, data=data)
    return dependency
