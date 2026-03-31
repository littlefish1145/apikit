"""
APISTD - 让 FastAPI/Flask 开发更简单

统一的导出模块，提供便捷的导入接口。
"""

# Core components
from core.response import Response, SuccessResponse, ErrorResponse, Success, Error
from core.exceptions import APIException, ValidationError, NotFoundError, AuthenticationError, AuthorizationError
from core.status import StatusCode

# Extensions
from extensions.pagination import PageResult, paginate

# Framework adapters
from framework.fastapi import FastAPIAdapter, FormattedJSONResponse
from framework.flask import FlaskAdapter

# Config
from config.default import configure, get_config

# Middleware helpers
from middleware.request_id import get_request_id
from middleware.timer import get_execution_time

# Format registry
from formats.registry import ResponseFormatterRegistry, register_format

# Optimization modules (optional)
try:
    from optimization import (
        FastJSON,
        MemoryArena,
        ZeroCopyBuffer,
        SchemaCompiler,
        FastValidator,
        BackendSelector,
        LRUCache,
        BatchedProcessor
    )
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False

# Rust backend (optional - high performance)
try:
    from optimization.backend import RustResponse, RUST_AVAILABLE
except ImportError:
    RustResponse = None
    RUST_AVAILABLE = False

__version__ = "1.0.0"
__all__ = [
    # Core
    "Response",
    "SuccessResponse",
    "ErrorResponse",
    "Success",  # Smart factory
    "Error",    # Smart factory
    "APIException",
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    "AuthorizationError",
    "StatusCode",
    
    # Extensions
    "PageResult",
    "paginate",
    
    # Framework adapters
    "FastAPIAdapter",
    "FlaskAdapter",
    "FormattedJSONResponse",
    
    # Config
    "configure",
    "get_config",
    
    # Middleware helpers
    "get_request_id",
    "get_execution_time",
    
    # Format registry
    "ResponseFormatterRegistry",
    "register_format",
    
    # Optimization (if available)
    "FastJSON",
    "MemoryArena",
    "ZeroCopyBuffer",
    "SchemaCompiler",
    "FastValidator",
    "BackendSelector",
    "LRUCache",
    "BatchedProcessor",
    "OPTIMIZATION_AVAILABLE",
    
    # Rust backend (if available)
    "RustResponse",
    "RUST_AVAILABLE",
]
