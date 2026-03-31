"""
SIMD-Accelerated JSON Parsing

Utilizes SIMD instructions for parallel JSON parsing when available.
"""

from __future__ import annotations
from typing import Any, Optional
import sys
import json


class SIMDJSONBackend:
    """
    SIMD-accelerated JSON backend.
    
    Attempts to use simdjson library for ultra-fast parsing.
    Falls back to standard json if not available.
    """
    
    def __init__(self):
        """Initialize SIMD JSON backend"""
        self._simdjson = None
        self._available = False
        self._use_simd = False
        
        self._detect_simd_support()
    
    def _detect_simd_support(self) -> None:
        """Detect SIMD support and select best implementation"""
        try:
            import simdjson
            self._simdjson = simdjson
            self._available = True
            self._use_simd = True
        except ImportError:
            self._available = False
            self._use_simd = False
    
    @property
    def available(self) -> bool:
        """Check if SIMD JSON is available"""
        return self._available
    
    @property
    def using_simd(self) -> bool:
        """Check if SIMD is being used"""
        return self._use_simd
    
    def dumps(self, obj: Any, **kwargs) -> bytes:
        """
        Serialize to JSON bytes.
        
        Note: simdjson is primarily for parsing, not serialization.
        We use standard json for serialization with optimizations.
        
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
    
    def loads(self, data: bytes | str) -> Any:
        """
        Deserialize from JSON using SIMD when available.
        
        Args:
            data: JSON bytes or string
            
        Returns:
            Deserialized object
        """
        if self._use_simd and self._simdjson:
            try:
                if isinstance(data, bytes):
                    return self._simdjson.loads(data)
                else:
                    return self._simdjson.loads(data.encode('utf-8'))
            except Exception:
                pass
        
        if isinstance(data, bytes):
            data = data.decode('utf-8')
        
        return json.loads(data)
    
    def parse(self, data: bytes) -> Any:
        """
        Parse JSON bytes with SIMD acceleration.
        
        Args:
            data: JSON bytes
            
        Returns:
            Parsed object
        """
        if self._use_simd and self._simdjson:
            try:
                parser = self._simdjson.Parser()
                return parser.parse(data)
            except Exception:
                pass
        
        return json.loads(data.decode('utf-8'))
    
    def get_simd_info(self) -> dict:
        """
        Get SIMD capability information.
        
        Returns:
            dict with SIMD info
        """
        import platform
        
        info = {
            "available": self._available,
            "using_simd": self._use_simd,
            "architecture": platform.machine(),
            "processor": platform.processor(),
        }
        
        if self._use_simd:
            try:
                import cpuinfo
                info["cpu_info"] = cpuinfo.get_cpu_info()
            except ImportError:
                pass
        
        return info
