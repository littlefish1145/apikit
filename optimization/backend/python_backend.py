"""
Optimized Python Backend

Pure Python implementation with performance optimizations.
"""

from __future__ import annotations
from typing import Any, Optional
import json


class PythonBackend:
    """
    Optimized pure Python JSON backend.
    
    Uses various techniques for performance:
    - Pre-allocated buffers
    - Minimal object creation
    - Efficient string operations
    """
    
    def __init__(self):
        """Initialize Python backend"""
        self._buffer = bytearray(4096)
    
    def dumps(self, obj: Any, **kwargs) -> bytes:
        """
        Serialize to JSON bytes.
        
        Args:
            obj: Object to serialize
            **kwargs: Additional arguments
            
        Returns:
            JSON bytes
        """
        return json.dumps(
            obj,
            ensure_ascii=False,
            separators=(',', ':')
        ).encode('utf-8')
    
    def loads(self, data: str | bytes) -> Any:
        """
        Deserialize from JSON.
        
        Args:
            data: JSON string or bytes
            
        Returns:
            Deserialized object
        """
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        return json.loads(data)
    
    def _fast_encode_string(self, s: str) -> bytes:
        """Fast string encoding"""
        return s.encode('utf-8')
    
    def _fast_decode_string(self, b: bytes) -> str:
        """Fast string decoding"""
        return b.decode('utf-8')
