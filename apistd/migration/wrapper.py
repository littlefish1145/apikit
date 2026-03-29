from typing import Any, Callable, Optional
from functools import wraps
from apistd.migration.adapter import ResponseAdapter


class MigrationWrapper:
    def __init__(self, adapter: ResponseAdapter = None, compat_mode: bool = True):
        self.adapter = adapter or ResponseAdapter()
        self.compat_mode = compat_mode

    def wrap(self, func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            if self.compat_mode:
                return result

            converted = self.adapter.convert(result)
            return converted
        return wrapper

    def wrap_app(self, app: Any) -> Any:
        if hasattr(app, "before_request"):
            original_before_request = app.before_request

            def wrapped_before_request():
                return original_before_request()

            app.before_request = wrapped_before_request

        if hasattr(app, "after_request"):
            original_after_request = app.after_request

            def wrapped_after_request(response):
                return original_after_request(response)

            app.after_request = wrapped_after_request

        return app


def auto_convert(old_key_map: dict = None):
    def decorator(f: Callable) -> Callable:
        adapter = ResponseAdapter(old_key_map=old_key_map or {})

        @wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            converted = adapter.convert(result)
            return converted
        return wrapper
    return decorator
