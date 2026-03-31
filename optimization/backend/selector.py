"""
Backend Selector - Automatic Backend Selection

Intelligently selects the best available backend based on
system capabilities and performance characteristics.
"""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import sys
import platform


class BackendType(Enum):
    """Available backend types"""
    RUST = "rust"
    ORJSON = "orjson"
    UJSON = "ujson"
    SIMDJSON = "simdjson"
    PYTHON = "python"
    STANDARD = "standard"


@dataclass
class BackendInfo:
    """Information about a backend"""
    backend_type: BackendType
    available: bool
    performance_score: float
    features: List[str]
    description: str


class BackendSelector:
    """
    Automatically selects the best available backend.
    
    Detects system capabilities and available libraries to choose
    the optimal backend for serialization and validation.
    """
    
    def __init__(self):
        """Initialize backend selector"""
        self._backends: Dict[BackendType, BackendInfo] = {}
        self._selected_backend: Optional[BackendType] = None
        self._detect_backends()
    
    def _detect_backends(self) -> None:
        """Detect available backends"""
        self._detect_rust_backend()
        self._detect_orjson()
        self._detect_ujson()
        self._detect_simdjson()
        self._detect_python_backend()
        
        self._select_best()
    
    def _detect_rust_backend(self) -> None:
        """Detect Rust backend availability"""
        try:
            import importlib.util
            # Try multiple possible locations
            spec = importlib.util.find_spec("optimization.backend.rust_backend")
            if spec is None:
                spec = importlib.util.find_spec("rust_backend")
            available = spec is not None
            
            self._backends[BackendType.RUST] = BackendInfo(
                backend_type=BackendType.RUST,
                available=available,
                performance_score=10.0 if available else 0.0,
                features=["zero-copy", "memory-safe", "maximum-performance"],
                description="Rust extension backend (PyO3)"
            )
        except Exception:
            self._backends[BackendType.RUST] = BackendInfo(
                backend_type=BackendType.RUST,
                available=False,
                performance_score=0.0,
                features=[],
                description="Rust extension backend (not available)"
            )
    
    def _detect_orjson(self) -> None:
        """Detect orjson availability"""
        try:
            import orjson
            self._backends[BackendType.ORJSON] = BackendInfo(
                backend_type=BackendType.ORJSON,
                available=True,
                performance_score=9.0,
                features=["fast-serialization", "numpy-support", "rfc-compliant"],
                description="orjson - Ultra-fast JSON library"
            )
        except ImportError:
            self._backends[BackendType.ORJSON] = BackendInfo(
                backend_type=BackendType.ORJSON,
                available=False,
                performance_score=0.0,
                features=[],
                description="orjson (not installed)"
            )
    
    def _detect_ujson(self) -> None:
        """Detect ujson availability"""
        try:
            import ujson
            self._backends[BackendType.UJSON] = BackendInfo(
                backend_type=BackendType.UJSON,
                available=True,
                performance_score=7.0,
                features=["fast-serialization", "compatible"],
                description="ujson - Fast JSON library"
            )
        except ImportError:
            self._backends[BackendType.UJSON] = BackendInfo(
                backend_type=BackendType.UJSON,
                available=False,
                performance_score=0.0,
                features=[],
                description="ujson (not installed)"
            )
    
    def _detect_simdjson(self) -> None:
        """Detect simdjson availability"""
        try:
            import simdjson
            self._backends[BackendType.SIMDJSON] = BackendInfo(
                backend_type=BackendType.SIMDJSON,
                available=True,
                performance_score=8.5,
                features=["simd-accelerated", "parallel-parsing"],
                description="simdjson - SIMD-accelerated JSON parser"
            )
        except ImportError:
            self._backends[BackendType.SIMDJSON] = BackendInfo(
                backend_type=BackendType.SIMDJSON,
                available=False,
                performance_score=0.0,
                features=[],
                description="simdjson (not installed)"
            )
    
    def _detect_python_backend(self) -> None:
        """Detect Python backend"""
        self._backends[BackendType.PYTHON] = BackendInfo(
            backend_type=BackendType.PYTHON,
            available=True,
            performance_score=5.0,
            features=["pure-python", "no-dependencies", "portable"],
            description="Optimized Python backend"
        )
        
        self._backends[BackendType.STANDARD] = BackendInfo(
            backend_type=BackendType.STANDARD,
            available=True,
            performance_score=1.0,
            features=["standard-library", "always-available"],
            description="Standard library json module"
        )
    
    def _select_best(self) -> None:
        """Select the best available backend"""
        available_backends = [
            (backend_type, info)
            for backend_type, info in self._backends.items()
            if info.available
        ]
        
        if not available_backends:
            self._selected_backend = BackendType.STANDARD
            return
        
        best = max(available_backends, key=lambda x: x[1].performance_score)
        self._selected_backend = best[0]
    
    def get_best_backend(self) -> BackendType:
        """
        Get the best available backend.
        
        Returns:
            Best backend type
        """
        return self._selected_backend or BackendType.STANDARD
    
    def get_capabilities(self) -> dict:
        """
        Get system capabilities.
        
        Returns:
            dict with capability information
        """
        return {
            "selected_backend": self._selected_backend.value if self._selected_backend else "none",
            "available_backends": [
                backend.value for backend, info in self._backends.items()
                if info.available
            ],
            "platform": platform.platform(),
            "python_version": sys.version,
            "architecture": platform.machine(),
            "processor": platform.processor(),
        }
    
    def get_backend_info(self, backend_type: BackendType) -> Optional[BackendInfo]:
        """
        Get information about a specific backend.
        
        Args:
            backend_type: Backend type
            
        Returns:
            BackendInfo or None
        """
        return self._backends.get(backend_type)
    
    def list_backends(self) -> List[BackendInfo]:
        """
        List all backends with their status.
        
        Returns:
            List of BackendInfo
        """
        return list(self._backends.values())
    
    def is_backend_available(self, backend_type: BackendType) -> bool:
        """
        Check if a specific backend is available.
        
        Args:
            backend_type: Backend type
            
        Returns:
            True if available
        """
        info = self._backends.get(backend_type)
        return info.available if info else False
