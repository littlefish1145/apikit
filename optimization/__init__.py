"""
Performance Optimization Module for apistd

Zero-overhead abstractions with maximum performance through:
- Zero-copy memory management
- Pre-compiled Schema validation
- Optimized serialization (orjson, SIMD)
- Intelligent backend selection
- Async optimizations
"""

from .memory.zero_copy import ZeroCopyBuffer
from .memory.arena import MemoryArena
from .memory.view import MemoryView
from .schema.compiler import SchemaCompiler
from .schema.cache import SchemaCache
from .schema.validator import FastValidator
from .serializer.fast_json import FastJSON
from .backend.selector import BackendSelector
from .cache.lru import LRUCache
from .async_opt.batched import BatchedProcessor

__version__ = "1.0.0"

__all__ = [
    "ZeroCopyBuffer",
    "MemoryArena", 
    "MemoryView",
    "SchemaCompiler",
    "SchemaCache",
    "FastValidator",
    "FastJSON",
    "BackendSelector",
    "LRUCache",
    "BatchedProcessor",
]
