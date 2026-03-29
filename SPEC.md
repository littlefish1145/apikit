# apistd - API Response Standardization Package

## 1. Project Overview

### Project Name
`apistd` - API Response Standardization

### Project Type
Python Package with Git Repository

### Core Functionality
A comprehensive Python library that standardizes API response formats across different web frameworks, providing unified response structure (code, message, data, timestamp), debugging capabilities, and migration tools for legacy projects.

### Target Users
- Python web developers using FastAPI, Flask, Django, Sanic, or Quart
- API developers who need consistent response formats
- Teams migrating from legacy API implementations
- Developers requiring debug/tracing capabilities in development

---

## 2. Package Architecture

### Directory Structure

```
apistd/
├── __init__.py                 # Main entry point with public API
├── core/
│   ├── __init__.py
│   ├── response.py             # Response core class (Response, SuccessResponse, ErrorResponse)
│   ├── status.py               # Status code management (StatusCode enum, HTTPStatusMapper)
│   ├── exceptions.py           # Exception definitions (APIException, ValidationError, etc.)
│   └── constants.py            # Constant definitions (ResponseFields, ErrorCodes, etc.)
├── framework/
│   ├── __init__.py
│   ├── base.py                 # Framework base class (FrameworkAdapter)
│   ├── fastapi.py              # FastAPI integration (middleware, dependency injection)
│   ├── flask.py                # Flask integration (decorators, hooks)
│   └── compat.py               # Legacy project compatibility (CompatibilityWrapper)
├── middleware/
│   ├── __init__.py
│   ├── request_id.py           # Request ID middleware (X-Request-ID header handling)
│   ├── timer.py                # Timing middleware (execution time recording)
│   └── debug.py                # Debug middleware (development mode features)
├── extensions/
│   ├── __init__.py
│   ├── pagination.py           # Pagination extension (PageResult, paginate helper)
│   ├── validation.py           # Validation error handling (ValidationErrorFormatter)
│   └── database.py             # ORM integration (SQL query logging, slow query warnings)
├── debug/
│   ├── __init__.py
│   ├── logger.py               # Debug logger (DebugLogger, SQL query log)
│   ├── collector.py            # Data collector (RequestDataCollector, ResponseDataCollector)
│   └── panel.py                # Debug panel (DebugPanel, ExecutionTracePanel)
├── config/
│   ├── __init__.py
│   ├── default.py              # Default configuration (DefaultConfig)
│   └── schema.py               # Configuration validation (ConfigSchema, validate_config)
└── migration/
    ├── __init__.py
    ├── adapter.py              # Response adapter (ResponseAdapter, format_converter)
    └── wrapper.py              # Migration wrapper (MigrationWrapper, auto_convert)
```

---

## 3. Core Functionality Specification

### 3.1 Response Core (core/response.py)

#### Response Class
```python
class Response:
    code: int           # Status code (0 for success, error code for failure)
    message: str        # Human-readable message
    data: Any           # Response payload
    timestamp: float    # Unix timestamp

    def __init__(self, code: int = 0, message: str = "", data: Any = None, timestamp: float = None):
    def to_dict(self) -> dict:
    def to_json(self) -> str:
    @classmethod
    def from_dict(cls, data: dict) -> 'Response':
```

#### SuccessResponse Class
```python
class SuccessResponse(Response):
    def __init__(self, data: Any = None, message: str = "Success", code: int = 0):
```

#### ErrorResponse Class
```python
class ErrorResponse(Response):
    def __init__(self, message: str = "Error", code: int = -1, error_detail: Any = None):
    error_detail: Any   # Structured error details
```

### 3.2 Status Code Management (core/status.py)

#### StatusCode Enum
```python
class StatusCode(IntEnum):
    # Success codes
    SUCCESS = 0
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204

    # Client error codes
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server error codes
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503
```

#### HTTPStatusMapper
```python
class HTTPStatusMapper:
    @staticmethod
    def to_http_status(code: int) -> int:
    @staticmethod
    def from_http_status(http_status: int) -> int:
```

### 3.3 Exception Definitions (core/exceptions.py)

```python
class APIException(Exception):
    def __init__(self, message: str, code: int = -1, status_code: int = 500, error_detail: Any = None):

class ValidationError(APIException):
    def __init__(self, message: str = "Validation failed", error_detail: Any = None):

class AuthenticationError(APIException):
    def __init__(self, message: str = "Authentication failed", error_detail: Any = None):

class AuthorizationError(APIException):
    def __init__(self, message: str = "Access denied", error_detail: Any = None):

class NotFoundError(APIException):
    def __init__(self, message: str = "Resource not found", error_detail: Any = None):
```

### 3.4 Constants (core/constants.py)

```python
class ResponseFields:
    CODE = "code"
    MESSAGE = "message"
    DATA = "data"
    TIMESTAMP = "timestamp"
    ERROR_DETAIL = "error_detail"
    REQUEST_ID = "request_id"
    EXECUTION_TIME = "execution_time"

class ErrorCodes:
    SUCCESS = 0
    UNKNOWN_ERROR = -1
    VALIDATION_ERROR = 1001
    AUTH_ERROR = 1002
    NOT_FOUND = 1004
    INTERNAL_ERROR = 5000

class ConfigKeys:
    DEBUG = "debug"
    REQUEST_ID_HEADER = "request_id_header"
    ENABLE_TIMING = "enable_timing"
    ENABLE_SQL_LOG = "enable_sql_log"
    SLOW_QUERY_THRESHOLD = "slow_query_threshold"
    RESPONSE_FORMATTER = "response_formatter"
    BEFORE_HOOKS = "before_hooks"
    AFTER_HOOKS = "after_hooks"
```

---

## 4. Framework Integration Specification

### 4.1 Framework Base (framework/base.py)

```python
class FrameworkAdapter(ABC):
    @abstractmethod
    def install(self, app: Any, config: dict = None):
        pass

    @abstractmethod
    def response_handler(self, response: Response) -> Any:
        pass

    @abstractmethod
    def error_handler(self, exception: Exception) -> Response:
        pass
```

### 4.2 FastAPI Integration (framework/fastapi.py)

#### FastAPIAdapter
```python
class FastAPIAdapter(FrameworkAdapter):
    def install(self, app: FastAPI, config: dict = None):
        # Register exception handlers
        # Add middleware
        # Register dependency injection

    async def __call__(self, request: Request, call_next):
        # Middleware implementation
```

#### Dependency Injection
```python
def inject_response(config: dict = None) -> Callable:
    # Dependency for FastAPI routes

class APIResponse:
    def __init__(self, success: bool = True, message: str = "", data: Any = None):
    def to_response(self) -> JSONResponse:
```

### 4.3 Flask Integration (framework/flask.py)

#### FlaskAdapter
```python
class FlaskAdapter(FrameworkAdapter):
    def install(self, app: Flask, config: dict = None):
        # Register error handlers
        # Register before/after request handlers

@app.errorhandler(APIException)
def handle_api_exception(e):
    return e.to_response()
```

#### Decorators
```python
def api_response(f: Callable = None, *, message: str = None) -> Callable:
    # Decorator for Flask routes

def auto_convert(old_response_key: str = None) -> Callable:
    # Migration decorator
```

### 4.4 Compatibility (framework/compat.py)

```python
class CompatibilityWrapper:
    def __init__(self, old_format_map: dict = None):
        # Map old response keys to new format

    def convert(self, old_response: Any) -> Response:
        # Convert legacy response format

    def adapt(self, response: Response) -> Any:
        # Adapt to original format if needed
```

---

## 5. Middleware Specification

### 5.1 Request ID Middleware (middleware/request_id.py)

```python
class RequestIDMiddleware:
    def __init__(self, header_name: str = "X-Request-ID"):
        self.header_name = header_name

    async def __call__(self, request: Request, call_next):
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        response = await call_next(request)
        response.headers[self.header_name] = request_id
        return response

def get_request_id() -> str:
    # Get current request ID from context
```

### 5.2 Timer Middleware (middleware/timer.py)

```python
class TimerMiddleware:
    def __init__(self, threshold_ms: float = 1000):
        self.threshold_ms = threshold_ms

    async def __call__(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        execution_time = (time.perf_counter() - start_time) * 1000

        if execution_time > self.threshold_ms:
            # Log slow request warning
            pass

        response.headers["X-Execution-Time"] = f"{execution_time:.2f}ms"
        return response

def get_execution_time() -> float:
    # Get current execution time from context
```

### 5.3 Debug Middleware (middleware/debug.py)

```python
class DebugMiddleware:
    def __init__(self, enabled: bool = None):
        self.enabled = enabled  # Auto-enable in debug mode

    async def __call__(self, request: Request, call_next):
        # Collect request data
        # Add debug headers
        # Attach debug info to response
```

---

## 6. Extensions Specification

### 6.1 Pagination (extensions/pagination.py)

```python
class PageResult:
    items: List[Any]       # Current page items
    total: int             # Total item count
    page: int              # Current page number
    page_size: int         # Items per page
    total_pages: int       # Total page count

    def __init__(self, items: List[Any], total: int, page: int, page_size: int):
    def to_response(self, message: str = "Success") -> Response:

def paginate(items: List[Any], total: int, page: int, page_size: int) -> PageResult:
def create_page_result(items: List[Any], total: int, page: int, page_size: int) -> PageResult:
```

### 6.2 Validation Errors (extensions/validation.py)

```python
class ValidationErrorFormatter:
    @staticmethod
    def format(error: ValidationError) -> ErrorResponse:
    @staticmethod
    def format_pydantic(errors: List[dict]) -> ErrorResponse:
    @staticmethod
    def format_custom(validator_name: str, message: str) -> ErrorResponse:
```

### 6.3 Database Integration (extensions/database.py)

```python
class SQLLogger:
    def __init__(self, threshold_ms: float = 100):
        self.threshold_ms = threshold_ms
        self.queries: List[dict] = []

    def log_query(self, query: str, duration: float, params: Any = None):
    def get_slow_queries(self) -> List[dict]:
    def clear(self):

class DatabaseExtension:
    def __init__(self, config: dict = None):
    def install(self, app: Any):
```

---

## 7. Debug Module Specification

### 7.1 Logger (debug/logger.py)

```python
class DebugLogger:
    def __init__(self, name: str = "apistd"):
        self.logger = logging.getLogger(name)

    def debug(self, message: str, **kwargs):
    def info(self, message: str, **kwargs):
    def warning(self, message: str, **kwargs):
    def error(self, message: str, **kwargs):

class SQLDebugLogger(DebugLogger):
    def log_query(self, query: str, duration: float, params: Any = None):
    def log_slow_query(self, query: str, duration: float, params: Any = None):
```

### 7.2 Data Collector (debug/collector.py)

```python
class RequestDataCollector:
    def __init__(self, request: Any):
        self.method: str
        self.url: str
        self.headers: dict
        self.body: Any
        self.query_params: dict
        self.timestamp: float

    def collect(self) -> dict:

class ResponseDataCollector:
    def __init__(self, response: Any):
        self.status_code: int
        self.headers: dict
        self.body: Any
        self.execution_time: float

    def collect(self) -> dict:
```

### 7.3 Debug Panel (debug/panel.py)

```python
class DebugPanel:
    def __init__(self, request_data: dict, response_data: dict):
        self.request_data = request_data
        self.response_data = response_data

    def render(self) -> dict:
    def get_execution_trace(self) -> List[dict]:
```

---

## 8. Configuration Specification

### 8.1 Default Config (config/default.py)

```python
DEFAULT_CONFIG = {
    "debug": False,
    "request_id_header": "X-Request-ID",
    "enable_timing": True,
    "enable_sql_log": False,
    "slow_query_threshold": 100,
    "response_formatter": None,
    "before_hooks": [],
    "after_hooks": [],
    "timestamp_format": "iso",
    "timezone": "UTC",
}
```

### 8.2 Config Schema (config/schema.py)

```python
class ConfigSchema:
    debug: bool = False
    request_id_header: str = "X-Request-ID"
    enable_timing: bool = True
    enable_sql_log: bool = False
    slow_query_threshold: float = 100
    response_formatter: Callable = None
    before_hooks: List[Callable] = field(default_factory=list)
    after_hooks: List[Callable] = field(default_factory=list)
    timestamp_format: str = "iso"
    timezone: str = "UTC"

def validate_config(config: dict) -> ConfigSchema:
    # Validate and return typed config
```

---

## 9. Migration Tools Specification

### 9.1 Response Adapter (migration/adapter.py)

```python
class ResponseAdapter:
    def __init__(self, old_key_map: dict = None, new_key_map: dict = None):
        self.old_key_map = old_key_map
        self.new_key_map = new_key_map

    def convert(self, old_response: Any) -> Response:
        # Convert old response to new format

    def adapt(self, new_response: Response, old_format: str = None) -> Any:
        # Convert new response back to old format

class FormatConverter:
    @staticmethod
    def to_apistd_format(data: dict, mapping: dict = None) -> Response:
    @staticmethod
    def from_apistd_format(response: Response, format_name: str = None) -> dict:
```

### 9.2 Migration Wrapper (migration/wrapper.py)

```python
class MigrationWrapper:
    def __init__(self, adapter: ResponseAdapter = None, compat_mode: bool = True):
        self.adapter = adapter
        self.compat_mode = compat_mode

    def wrap(self, func: Callable) -> Callable:
        # Wrap function to auto-convert responses

    def wrap_app(self, app: Any) -> Any:
        # Wrap Flask/FastAPI app

@decorator
def auto_convert(old_key_map: dict = None):
    # Decorator for automatic conversion
```

---

## 10. Main Entry Point (__init__.py)

```python
from apistd.core.response import Response, SuccessResponse, ErrorResponse
from apistd.core.status import StatusCode, HTTPStatusMapper
from apistd.core.exceptions import APIException, ValidationError, NotFoundError
from apistd.extensions.pagination import PageResult, paginate
from apistd.config import Config, configure

__version__ = "1.0.0"

__all__ = [
    "Response",
    "SuccessResponse",
    "ErrorResponse",
    "StatusCode",
    "HTTPStatusMapper",
    "APIException",
    "ValidationError",
    "NotFoundError",
    "PageResult",
    "paginate",
    "configure",
    "FastAPIAdapter",
    "FlaskAdapter",
    "RequestIDMiddleware",
    "TimerMiddleware",
    "DebugMiddleware",
]
```

---

## 11. Technical Requirements

### Python Version Support
- Python 3.8+
- Python 3.9+
- Python 3.10+
- Python 3.11+
- Python 3.12+

### Dependencies
- `typing` (standard library)
- `datetime` (standard library)
- `enum` (standard library)
- `uuid` (standard library)
- `time` (standard library)
- `logging` (standard library)

### Optional Dependencies
- `fastapi` (for FastAPI integration)
- `flask` (for Flask integration)
- `pydantic` (for validation integration)
- `django` (for Django integration, optional)

---

## 12. Usage Examples

### Basic Usage
```python
from apistd import Response, SuccessResponse, ErrorResponse

# Success response
response = SuccessResponse(data={"user_id": 1}, message="User found")

# Error response
error = ErrorResponse(message="Invalid input", code=1001, error_detail={"field": "email"})

# Custom response
custom = Response(code=0, message="OK", data={"key": "value"})
```

### FastAPI Integration
```python
from fastapi import FastAPI
from apistd.framework.fastapi import FastAPIAdapter, inject_response

app = FastAPI()
adapter = FastAPIAdapter()
adapter.install(app, config={"debug": True})

@app.get("/users/{user_id}")
async def get_user(user_id: int, api_response: APIResponse = Depends(inject_response())):
    return api_response(data={"user_id": user_id})
```

### Flask Integration
```python
from flask import Flask, jsonify
from apistd.framework.flask import FlaskAdapter, api_response

app = Flask(__name__)
adapter = FlaskAdapter()
adapter.install(app)

@app.route("/users/<int:user_id>", methods=["GET"])
@api_response
def get_user(user_id):
    return {"user_id": user_id}
```

### Pagination
```python
from apistd.extensions.pagination import paginate

@app.get("/users")
async def list_users(page: int = 1, page_size: int = 20):
    users, total = get_users_from_db(page, page_size)
    return paginate(users, total, page, page_size)
```

---

## 13. Response Format Specification

### Success Response
```json
{
    "code": 0,
    "message": "Success",
    "data": { ... },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### Error Response
```json
{
    "code": -1,
    "message": "Error description",
    "error_detail": { ... },
    "timestamp": "2024-01-15T10:30:00.000Z",
    "request_id": "uuid-string"
}
```

### Paginated Response
```json
{
    "code": 0,
    "message": "Success",
    "data": {
        "items": [ ... ],
        "total": 100,
        "page": 1,
        "page_size": 20,
        "total_pages": 5
    },
    "timestamp": "2024-01-15T10:30:00.000Z"
}
```

---

## 14. Acceptance Criteria

### Core Functionality
- [ ] Response class correctly serializes to dict and JSON
- [ ] SuccessResponse and ErrorResponse work correctly
- [ ] StatusCode enum contains all standard codes
- [ ] HTTPStatusMapper correctly maps between codes
- [ ] APIException can be raised and caught properly

### Framework Integration
- [ ] FastAPI adapter installs middleware and exception handlers
- [ ] Flask adapter registers error handlers and decorators
- [ ] Dependency injection works in FastAPI routes
- [ ] Decorator works correctly in Flask routes

### Middleware
- [ ] RequestIDMiddleware generates/validates request IDs
- [ ] TimerMiddleware measures and reports execution time
- [ ] DebugMiddleware enables debug features in debug mode

### Extensions
- [ ] PageResult correctly calculates pagination metadata
- [ ] ValidationErrorFormatter formats validation errors
- [ ] SQLLogger logs queries and identifies slow queries

### Debug
- [ ] DebugLogger outputs formatted debug messages
- [ ] RequestDataCollector collects request information
- [ ] ResponseDataCollector collects response information

### Configuration
- [ ] DefaultConfig provides sensible defaults
- [ ] ConfigSchema validates configuration values
- [ ] configure() function updates global config

### Migration
- [ ] ResponseAdapter converts old format to new format
- [ ] MigrationWrapper wraps functions for auto-conversion
- [ ] Compat mode preserves original response format

### Package
- [ ] Package installs correctly via pip
- [ ] All public API is accessible from apistd.__init__
- [ ] Version number is correct
