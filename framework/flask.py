import time
import psutil
import os
import traceback
from typing import Callable, Optional, Any, Dict
from flask import Flask, request, jsonify, Response as FlaskResponse, make_response
from functools import wraps

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
from middleware.request_id import get_request_id, set_request_id, get_request_start_time


def formatted_jsonify(data, indent=2, ensure_ascii=False):
    """
    Create JSON response using optimized serializer when available.
    
    When optimization is enabled and no indent is needed, uses FastJSON
    (orjson/ujson) for better performance. Falls back to standard json
    when indent is required or optimization is not available.
    """
    if _use_optimization and indent is None:
        # Use optimized serializer (no indent for performance)
        json_bytes = _json_serializer.dumps(data)
        response = make_response(json_bytes.decode('utf-8') if isinstance(json_bytes, bytes) else json_bytes)
    else:
        # Fallback to standard json (supports indent)
        import json
        json_str = json.dumps(
            data,
            indent=indent,
            ensure_ascii=ensure_ascii,
            separators=(',', ':') if indent is None else None
        )
        response = make_response(json_str)
    
    response.headers["Content-Type"] = "application/json"
    return response


class FlaskAdapter(FrameworkAdapter):
    def __init__(self):
        self.app: Optional[Flask] = None
        self.config: dict = {}
        self._request_start_time: float = 0

    def install(self, app: Flask, config: dict = None) -> None:
        self.app = app
        if config:
            self.config = config

        app.register_error_handler(APIException, self._handle_api_exception)
        app.register_error_handler(Exception, self._handle_generic_exception)
        app.before_request(self._before_request)
        app.after_request(self._after_request)

        self._setup_swagger(app)

    def _setup_swagger(self, app: Flask) -> None:
        try:
            from flask_swagger_ui import get_swaggerui_blueprint
            SWAGGER_URL = '/api/docs'
            API_URL = '/static/swagger.json'
            app.register_blueprint(
                get_swaggerui_blueprint(SWAGGER_URL, API_URL),
                url_prefix=SWAGGER_URL
            )
        except ImportError:
            pass

    def _get_response(self, error_response: ErrorResponse, status_code: int):
        config = get_config()
        if config.debug:
            start_time = get_request_start_time()
            execution_time = (time.time() - start_time) * 1000 if start_time else 0
            error_dict = error_response.to_dict()
            error_dict["_debug"] = {
                "execution_time_ms": round(execution_time, 2),
                "memory_mb": round(psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024, 2),
                "request_id": get_request_id(),
            }
            return formatted_jsonify(error_dict), status_code
        return formatted_jsonify(error_response.to_dict()), status_code

    def _handle_api_exception(self, exc: APIException):
        config = get_config()
        error_response = exc.to_response(debug=config.debug)
        return self._get_response(error_response, exc.status_code)

    def _handle_generic_exception(self, exc: Exception):
        error_response = ErrorResponse(
            message=str(exc) or "Internal server error",
            code=500,
            error_detail={
                "type": type(exc).__name__,
                "exception": str(exc),
            }
        )
        return self._get_response(error_response, 500)

    def _before_request(self):
        self._request_start_time = time.time()
        from middleware.request_id import set_request_start_time
        set_request_start_time(self._request_start_time)

        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())
        set_request_id(request_id)

    def _after_request(self, response: FlaskResponse):
        config = get_config()
        request_id = get_request_id()

        if request_id:
            response.headers["X-Request-ID"] = request_id

        execution_time = (time.time() - self._request_start_time) * 1000
        response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"

        if config.debug:
            process = psutil.Process(os.getpid())
            memory_mb = round(process.memory_info().rss / 1024 / 1024, 2)
            response.headers["X-Debug-Memory"] = f"{memory_mb}MB"

        return response

    def response_handler(self, response: Response, debug: bool = False) -> tuple:
        config = get_config()
        should_debug = debug or config.debug

        if should_debug:
            return formatted_jsonify(response.to_dict()), response.code
        return formatted_jsonify(response.to_dict()), response.code

    def error_handler(self, exception: Exception, debug: bool = False) -> ErrorResponse:
        if isinstance(exception, APIException):
            return exception.to_response(debug=debug)
        return ErrorResponse(message=str(exception), code=500)


def api_response(f: Callable = None, *, message: str = None) -> Callable:
    if f is None:
        def decorator(fn: Callable) -> Callable:
            @wraps(fn)
            def wrapper(*args, **kwargs):
                result = fn(*args, **kwargs)
                config = get_config()
                should_debug = config.debug
                if isinstance(result, Response):
                    if should_debug:
                        return formatted_jsonify(result.to_dict()), 200 if result.code < 400 else result.code
                    return formatted_jsonify(result.to_dict()), 200 if result.code < 400 else result.code
                resp = SuccessResponse(data=result, message=message or "Success")
                if should_debug:
                    return formatted_jsonify(resp.to_dict()), 200
                return formatted_jsonify(resp.to_dict()), 200
            return wrapper
        return decorator

    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        config = get_config()
        should_debug = config.debug
        if isinstance(result, Response):
            if should_debug:
                return formatted_jsonify(result.to_dict()), 200 if result.code < 400 else result.code
            return formatted_jsonify(result.to_dict()), 200 if result.code < 400 else result.code
        resp = SuccessResponse(data=result, message=message or "Success")
        if should_debug:
            return formatted_jsonify(resp.to_dict()), 200
        return formatted_jsonify(resp.to_dict()), 200
    return wrapper


def auto_convert(old_response_key: str = None) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            config = get_config()
            should_debug = config.debug
            if old_response_key and isinstance(result, dict) and old_response_key in result:
                old_data = result[old_response_key]
                resp = SuccessResponse(data=old_data)
            else:
                resp = SuccessResponse(data=result)

            if should_debug:
                return formatted_jsonify(resp.to_dict()), 200
            return formatted_jsonify(resp.to_dict()), 200
        return wrapper
    return decorator
