# apistd Implementation Tasks

## Phase 1: Project Setup

### 1.1 Initialize Git Repository
- [ ] Initialize git repository in project root
- [ ] Create .gitignore file with Python patterns
- [ ] Create initial commit

### 1.2 Create Package Structure
- [ ] Create `apistd/` main directory
- [ ] Create `apistd/core/` subdirectory
- [ ] Create `apistd/framework/` subdirectory
- [ ] Create `apistd/middleware/` subdirectory
- [ ] Create `apistd/extensions/` subdirectory
- [ ] Create `apistd/debug/` subdirectory
- [ ] Create `apistd/config/` subdirectory
- [ ] Create `apistd/migration/` subdirectory
- [ ] Create `__init__.py` files in each directory

### 1.3 Setup Package Metadata
- [ ] Create `pyproject.toml` with project metadata
- [ ] Configure build system (setuptools)
- [ ] Define package dependencies
- [ ] Set version to 1.0.0

---

## Phase 2: Core Module Implementation

### 2.1 Constants (core/constants.py)
- [ ] Implement `ResponseFields` class with field constants
- [ ] Implement `ErrorCodes` class with error code constants
- [ ] Implement `ConfigKeys` class with config key constants

### 2.2 Status Codes (core/status.py)
- [ ] Implement `StatusCode` IntEnum with all standard codes
- [ ] Implement `HTTPStatusMapper` class
- [ ] Add `to_http_status()` static method
- [ ] Add `from_http_status()` static method

### 2.3 Exceptions (core/exceptions.py)
- [ ] Implement base `APIException` class
- [ ] Implement `ValidationError` exception
- [ ] Implement `AuthenticationError` exception
- [ ] Implement `AuthorizationError` exception
- [ ] Implement `NotFoundError` exception
- [ ] Implement `to_response()` method for each exception

### 2.4 Response Core (core/response.py)
- [ ] Implement `Response` class with code, message, data, timestamp
- [ ] Implement `to_dict()` method
- [ ] Implement `to_json()` method
- [ ] Implement `from_dict()` class method
- [ ] Implement `SuccessResponse` subclass
- [ ] Implement `ErrorResponse` subclass with error_detail

---

## Phase 3: Configuration Module

### 3.1 Default Config (config/default.py)
- [ ] Define `DEFAULT_CONFIG` dictionary
- [ ] Set debug default to False
- [ ] Set request_id_header default to "X-Request-ID"
- [ ] Set enable_timing default to True
- [ ] Set slow_query_threshold default to 100ms

### 3.2 Config Schema (config/schema.py)
- [ ] Implement `ConfigSchema` dataclass
- [ ] Implement `validate_config()` function
- [ ] Add type validation for all config fields
- [ ] Create `configure()` function for runtime config updates

---

## Phase 4: Framework Integration

### 4.1 Base Adapter (framework/base.py)
- [ ] Implement abstract `FrameworkAdapter` class
- [ ] Define `install()` abstract method
- [ ] Define `response_handler()` abstract method
- [ ] Define `error_handler()` abstract method

### 4.2 FastAPI Integration (framework/fastapi.py)
- [ ] Implement `FastAPIAdapter` class
- [ ] Implement `install()` method for FastAPI
- [ ] Implement middleware `__call__()` method
- [ ] Register exception handlers for APIException
- [ ] Implement `inject_response()` dependency injection
- [ ] Implement `APIResponse` class for DI

### 4.3 Flask Integration (framework/flask.py)
- [ ] Implement `FlaskAdapter` class
- [ ] Implement `install()` method for Flask
- [ ] Register error handlers
- [ ] Implement `api_response` decorator
- [ ] Implement `auto_convert` decorator for migration

### 4.4 Compatibility (framework/compat.py)
- [ ] Implement `CompatibilityWrapper` class
- [ ] Implement `convert()` method for old format
- [ ] Implement `adapt()` method to restore old format
- [ ] Support configurable key mapping

---

## Phase 5: Middleware Components

### 5.1 Request ID Middleware (middleware/request_id.py)
- [ ] Implement `RequestIDMiddleware` class
- [ ] Generate UUID for request if not provided
- [ ] Extract request ID from header
- [ ] Add request ID to response headers
- [ ] Implement `get_request_id()` context function

### 5.2 Timer Middleware (middleware/timer.py)
- [ ] Implement `TimerMiddleware` class
- [ ] Measure request execution time
- [ ] Add X-Execution-Time header to response
- [ ] Log warnings for slow requests (threshold configurable)
- [ ] Implement `get_execution_time()` context function

### 5.3 Debug Middleware (middleware/debug.py)
- [ ] Implement `DebugMiddleware` class
- [ ] Auto-enable in debug mode
- [ ] Collect request data for debugging
- [ ] Add debug headers to response
- [ ] Attach debug information to response

---

## Phase 6: Extensions

### 6.1 Pagination (extensions/pagination.py)
- [ ] Implement `PageResult` class
- [ ] Calculate total_pages from total and page_size
- [ ] Implement `to_response()` method
- [ ] Implement `paginate()` helper function
- [ ] Implement `create_page_result()` factory function

### 6.2 Validation Errors (extensions/validation.py)
- [ ] Implement `ValidationErrorFormatter` class
- [ ] Implement `format()` for standard validation errors
- [ ] Implement `format_pydantic()` for Pydantic errors
- [ ] Implement `format_custom()` for custom validators

### 6.3 Database Integration (extensions/database.py)
- [ ] Implement `SQLLogger` class
- [ ] Log SQL queries with duration
- [ ] Identify slow queries (configurable threshold)
- [ ] Implement `get_slow_queries()` method
- [ ] Implement `DatabaseExtension` class

---

## Phase 7: Debug Module

### 7.1 Logger (debug/logger.py)
- [ ] Implement `DebugLogger` class
- [ ] Configure logging format
- [ ] Implement `debug()`, `info()`, `warning()`, `error()` methods
- [ ] Implement `SQLDebugLogger` subclass
- [ ] Add query logging methods

### 7.2 Data Collector (debug/collector.py)
- [ ] Implement `RequestDataCollector` class
- [ ] Collect method, URL, headers, body, query params
- [ ] Implement `collect()` method
- [ ] Implement `ResponseDataCollector` class
- [ ] Collect status code, headers, body, execution time
- [ ] Implement `collect()` method

### 7.3 Debug Panel (debug/panel.py)
- [ ] Implement `DebugPanel` class
- [ ] Combine request and response data
- [ ] Implement `render()` method
- [ ] Implement `get_execution_trace()` method

---

## Phase 8: Migration Tools

### 8.1 Response Adapter (migration/adapter.py)
- [ ] Implement `ResponseAdapter` class
- [ ] Support custom old/new key mapping
- [ ] Implement `convert()` method
- [ ] Implement `adapt()` method
- [ ] Implement `FormatConverter` utility class

### 8.2 Migration Wrapper (migration/wrapper.py)
- [ ] Implement `MigrationWrapper` class
- [ ] Implement `wrap()` method for functions
- [ ] Implement `wrap_app()` method for applications
- [ ] Implement `auto_convert` decorator
- [ ] Support compat mode (no modification of original response)

---

## Phase 9: Main Package Entry

### 9.1 Package Init (__init__.py)
- [ ] Import all public API classes
- [ ] Set `__version__` to "1.0.0"
- [ ] Define `__all__` list
- [ ] Create convenient imports for users

### 9.2 Sub-package Inits
- [ ] Update core/__init__.py
- [ ] Update framework/__init__.py
- [ ] Update middleware/__init__.py
- [ ] Update extensions/__init__.py
- [ ] Update debug/__init__.py
- [ ] Update config/__init__.py
- [ ] Update migration/__init__.py

---

## Phase 10: Documentation & Testing

### 10.1 README
- [ ] Create README.md with installation instructions
- [ ] Add basic usage examples
- [ ] Document framework integration
- [ ] Add API reference summary

### 10.2 Testing
- [ ] Verify package can be imported
- [ ] Test Response class serialization
- [ ] Test SuccessResponse and ErrorResponse
- [ ] Test pagination functionality
- [ ] Verify all framework adapters install correctly

---

## Implementation Order

1. **Phase 1**: Project Setup (Git + directories)
2. **Phase 2**: Core Module (constants, status, exceptions, response)
3. **Phase 3**: Configuration Module
4. **Phase 4**: Framework Integration
5. **Phase 5**: Middleware Components
6. **Phase 6**: Extensions
7. **Phase 7**: Debug Module
8. **Phase 8**: Migration Tools
9. **Phase 9**: Main Package Entry
10. **Phase 10**: README & Testing

---

## Notes

- All modules should follow existing Python conventions
- Use type hints where possible
- Docstrings should be comprehensive
- Ensure backwards compatibility where specified
