"""Backend selection and implementation modules"""

from .selector import BackendSelector

# Try to import Rust backend if available
try:
    from .rust_backend import rust_serialize, rust_deserialize, rust_serialize_batch
    from .rust_backend import RustMemoryArena, RustSchemaValidator, RustResponse
    RUST_AVAILABLE = True
except ImportError:
    RUST_AVAILABLE = False

__all__ = ["BackendSelector", "RUST_AVAILABLE"]
if RUST_AVAILABLE:
    __all__.extend(["rust_serialize", "rust_deserialize", "rust_serialize_batch"])
    __all__.extend(["RustMemoryArena", "RustSchemaValidator", "RustResponse"])
