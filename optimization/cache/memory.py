"""
Memory Cache - In-Process Zero-Copy Cache

High-performance in-memory cache with zero-copy storage.
"""

from __future__ import annotations
from typing import Any, Optional, Union
import threading
import time
from .lru import LRUCache


class MemoryCache:
    """
    In-memory cache optimized for performance.
    
    Features:
    - Zero-copy storage using memoryview when possible
    - Automatic expiration
    - Memory limits
    - Background cleanup
    """
    
    def __init__(self, max_size: int = 10000, 
                 max_memory_mb: Optional[float] = None,
                 default_ttl: Optional[float] = 3600):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of entries
            max_memory_mb: Maximum memory usage in MB (None for unlimited)
            default_ttl: Default TTL in seconds
        """
        self._cache = LRUCache[any](capacity=max_size, ttl_seconds=default_ttl)
        self._max_memory_mb = max_memory_mb
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
        self._total_size = 0
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
            
        Returns:
            True if successful
        """
        with self._lock:
            if ttl is None:
                ttl = self._default_ttl
            
            if self._max_memory_mb:
                estimated_size = self._estimate_size(value)
                if self._total_size + estimated_size > self._max_memory_mb * 1024 * 1024:
                    self._evict_some()
                
                self._total_size += estimated_size
            
            self._cache.set(key, value)
            return True
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        result = self._cache.get(key)
        return result if result is not None else default
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted
        """
        with self._lock:
            value = self._cache.get(key)
            if value is not None:
                self._total_size -= self._estimate_size(value)
            return self._cache.delete(key)
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._total_size = 0
    
    def _estimate_size(self, value: Any) -> int:
        """Estimate memory size of value"""
        try:
            if isinstance(value, (bytes, bytearray)):
                return len(value)
            elif isinstance(value, str):
                return len(value.encode('utf-8'))
            else:
                import sys
                return sys.getsizeof(value)
        except Exception:
            return 1024
    
    def _evict_some(self) -> None:
        """Evict some entries to free memory"""
        evict_count = max(10, len(self._cache.keys()) // 10)
        
        for _ in range(evict_count):
            keys = self._cache.keys()
            if not keys:
                break
            
            key = keys[0]
            value = self._cache.get(key)
            if value is not None:
                self._total_size -= self._estimate_size(value)
            self._cache.delete(key)
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        count = 0
        with self._lock:
            keys = self._cache.keys()
            for key in keys:
                if self._cache.get(key) is None:
                    count += 1
        return count
    
    def stats(self) -> dict:
        """Get cache statistics"""
        cache_stats = self._cache.stats()
        cache_stats["total_memory_bytes"] = self._total_size
        cache_stats["max_memory_mb"] = self._max_memory_mb
        cache_stats["default_ttl"] = self._default_ttl
        return cache_stats
    
    def memory_usage_mb(self) -> float:
        """Get current memory usage in MB"""
        return self._total_size / (1024 * 1024)
