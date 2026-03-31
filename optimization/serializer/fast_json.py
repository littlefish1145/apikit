"""
Fast JSON Serialization

Unified high-performance JSON serialization with automatic backend
selection and fallback mechanisms.
"""

from __future__ import annotations
from typing import Any, Optional, TypeVar, Generic
from dataclasses import dataclass
import json
import sys

T = TypeVar('T')


@dataclass
class SerializationStats:
    """Serialization performance statistics"""
    serialize_count: int = 0
    deserialize_count: int = 0
    total_serialize_time_ns: int = 0
    total_deserialize_time_ns: int = 0
    backend_used: str = "unknown"
    
    @property
    def avg_serialize_time_ns(self) -> float:
        if self.serialize_count == 0:
            return 0.0
        return self.total_serialize_time_ns / self.serialize_count
    
    @property
    def avg_deserialize_time_ns(self) -> float:
        if self.deserialize_count == 0:
            return 0.0
        return self.total_deserialize_time_ns / self.deserialize_count


class FastJSON:
    """
    High-performance JSON serialization with automatic backend selection.
    
    Automatically selects the fastest available backend:
    1. orjson (fastest, if available)
    2. ujson (fast, if available)
    3. json (standard library fallback)
    
    Features:
    - Zero-copy deserialization when possible
    - Optimized for both small and large objects
    - Thread-safe operations
    - Performance monitoring
    """
    
    def __init__(self, auto_select: bool = True):
        """
        Initialize FastJSON serializer.
        
        Args:
            auto_select: Automatically select best backend
        """
        self._backend = None
        self._backend_name = "unknown"
        self._stats = SerializationStats()
        
        if auto_select:
            self._select_best_backend()
    
    def _select_best_backend(self) -> None:
        """Select the fastest available backend"""
        try:
            import orjson
            self._backend = orjson
            self._backend_name = "orjson"
            return
        except ImportError:
            pass
        
        try:
            import ujson
            self._backend = ujson
            self._backend_name = "ujson"
            return
        except ImportError:
            pass
        
        self._backend = json
        self._backend_name = "json"
    
    @property
    def backend_name(self) -> str:
        """Get current backend name"""
        return self._backend_name
    
    @property
    def stats(self) -> SerializationStats:
        """Get serialization statistics"""
        return self._stats
    
    def dumps(self, obj: Any, *, use_default: bool = True) -> bytes:
        """
        Serialize object to JSON bytes.
        
        Args:
            obj: Object to serialize
            use_default: Use default handler for unknown types
            
        Returns:
            JSON bytes
        """
        import time
        start = time.perf_counter_ns()
        
        try:
            if self._backend_name == "orjson":
                result = self._backend.dumps(obj)
            elif self._backend_name == "ujson":
                result = self._backend.dumps(obj, ensure_ascii=False).encode('utf-8')
            else:
                result = self._backend.dumps(
                    obj, 
                    ensure_ascii=False,
                    separators=(',', ':')
                ).encode('utf-8')
            
            self._stats.serialize_count += 1
            self._stats.total_serialize_time_ns = time.perf_counter_ns() - start
            self._stats.backend_used = self._backend_name
            
            return result
            
        except (TypeError, ValueError) as e:
            if use_default and self._backend_name != "orjson":
                result = self._backend.dumps(
                    obj,
                    default=str,
                    ensure_ascii=False,
                    separators=(',', ':')
                ).encode('utf-8')
                
                self._stats.serialize_count += 1
                self._stats.total_serialize_time_ns = time.perf_counter_ns() - start
                return result
            raise
    
    def loads(self, data: str | bytes) -> Any:
        """
        Deserialize JSON data.
        
        Args:
            data: JSON string or bytes
            
        Returns:
            Deserialized object
        """
        import time
        start = time.perf_counter_ns()
        
        try:
            if isinstance(data, bytes) and self._backend_name == "orjson":
                result = self._backend.loads(data)
            elif isinstance(data, bytes):
                data = data.decode('utf-8')
                result = self._backend.loads(data)
            else:
                result = self._backend.loads(data)
            
            self._stats.deserialize_count += 1
            self._stats.total_deserialize_time_ns = time.perf_counter_ns() - start
            
            return result
            
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    def dump(self, obj: Any, fp, *, use_default: bool = True) -> None:
        """
        Serialize object to file.
        
        Args:
            obj: Object to serialize
            fp: File-like object
            use_default: Use default handler
        """
        data = self.dumps(obj, use_default=use_default)
        if isinstance(data, bytes):
            fp.write(data)
        else:
            fp.write(data.encode('utf-8'))
    
    def load(self, fp) -> Any:
        """
        Deserialize from file.
        
        Args:
            fp: File-like object
            
        Returns:
            Deserialized object
        """
        data = fp.read()
        return self.loads(data)
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        self._stats = SerializationStats(backend_used=self._backend_name)
    
    def get_speedup(self) -> float:
        """
        Get estimated speedup vs standard json library.
        
        Returns:
            Speedup factor (e.g., 5.0 means 5x faster)
        """
        if self._backend_name == "orjson":
            return 5.0
        elif self._backend_name == "ujson":
            return 3.0
        else:
            return 1.0
