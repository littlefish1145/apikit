from typing import Callable, Optional, Any, Dict
from flask import Flask, request, jsonify, Response as FlaskResponse
from functools import wraps

from apistd.core.response import Response, SuccessResponse, ErrorResponse
from apistd.core.exceptions import APIException
from apistd.framework.base import FrameworkAdapter


class FlaskAdapter(FrameworkAdapter):
    def __init__(self):
        self.app: Optional[Flask] = None
        self.config: dict = {}

    def install(self, app: Flask, config: dict = None) -> None:
        self.app = app
        if config:
            self.config = config

        app.register_error_handler(APIException, self._handle_api_exception)
        app.before_request(self._before_request)
        app.after_request(self._after_request)

    def _handle_api_exception(self, exc: APIException):
        error_response = exc.to_response()
        return jsonify(error_response.to_dict()), exc.status_code

    def _before_request(self):
        from apistd.middleware.request_id import get_request_id, set_request_id
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            import uuid
            request_id = str(uuid.uuid4())
        set_request_id(request_id)

    def _after_request(self, response: FlaskResponse):
        from apistd.middleware.request_id import get_request_id
        request_id = get_request_id()
        if request_id:
            response.headers["X-Request-ID"] = request_id
        return response

    def response_handler(self, response: Response) -> tuple:
        http_status = 200 if response.code == 0 else 500
        return jsonify(response.to_dict()), http_status

    def error_handler(self, exception: Exception) -> ErrorResponse:
        if isinstance(exception, APIException):
            return exception.to_response()
        return ErrorResponse(message=str(exception), code=-1)


def api_response(f: Callable = None, *, message: str = None) -> Callable:
    if f is None:
        def decorator(fn: Callable) -> Callable:
            @wraps(fn)
            def wrapper(*args, **kwargs):
                result = fn(*args, **kwargs)
                if isinstance(result, Response):
                    return jsonify(result.to_dict()), 200 if result.code == 0 else 500
                return jsonify(SuccessResponse(data=result, message=message or "Success").to_dict()), 200
            return wrapper
        return decorator

    @wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        if isinstance(result, Response):
            return jsonify(result.to_dict()), 200 if result.code == 0 else 500
        return jsonify(SuccessResponse(data=result, message=message or "Success").to_dict()), 200
    return wrapper


def auto_convert(old_response_key: str = None) -> Callable:
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            if old_response_key and isinstance(result, dict) and old_response_key in result:
                old_data = result[old_response_key]
                return jsonify(SuccessResponse(data=old_data).to_dict()), 200
            return jsonify(SuccessResponse(data=result).to_dict()), 200
        return wrapper
    return decorator
