"""
Rust Backend - High-performance implementations

This module loads the compiled Rust shared library (.pyd/.so)
"""

# Try to import the compiled Rust module (.pyd file)
try:
    # Import from parent directory where we copied the .pyd file
    import sys
    import os
    _parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, _parent_dir)
    
    from rust_backend_lib import (
        RustResponse,
        RustMemoryArena,
        RustSchemaValidator,
        rust_serialize,
        rust_deserialize,
        rust_serialize_batch,
    )
    RUST_AVAILABLE = True
except ImportError as e:
    RUST_AVAILABLE = False
    RustResponse = None
    RustMemoryArena = None
    RustSchemaValidator = None
    rust_serialize = None
    rust_deserialize = None
    rust_serialize_batch = None
    
    # Log the error for debugging
    import warnings
    warnings.warn(f"Rust backend not available: {e}")

__all__ = [
    "RUST_AVAILABLE",
    "RustResponse",
    "RustMemoryArena", 
    "RustSchemaValidator",
    "rust_serialize",
    "rust_deserialize",
    "rust_serialize_batch",
]
