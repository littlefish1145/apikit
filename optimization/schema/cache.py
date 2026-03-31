"""
Schema Cache - LRU Cache for Compiled Schemas

Efficiently caches compiled schemas to avoid recompilation.
"""

from __future__ import annotations
from typing import Any, Optional, Dict, Generic, TypeVar
from collections import OrderedDict
import threading
import time

T = TypeVar('T')


class LRUCache(Generic[T]):
    """
    Thread-safe LRU cache implementation.
    
    Uses OrderedDict for O(1) get/set operations.
    Supports TTL (time-to-live) for cache entries.
    """
    
    def __init__(self, capacity: int = 1000, ttl_seconds: Optional[float] = None):
        """
        Initialize LRU cache.
        
        Args:
            capacity: Maximum number of entries
            ttl_seconds: Time-to-live for entries (None for no expiry)
        """
        self._capacity = capacity
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[T, float]] = OrderedDict()
        self._lock = threading.RLock()
    
    def get(self, key: str) -> Optional[T]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            value, timestamp = self._cache[key]
            
            if self._ttl and (time.time() - timestamp) > self._ttl:
                del self._cache[key]
                return None
            
            self._cache.move_to_end(key)
            return value
    
    def set(self, key: str, value: T) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            
            self._cache[key] = (value, time.time())
            
            if len(self._cache) > self._capacity:
                self._cache.popitem(last=False)
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
    
    def size(self) -> int:
        """Get current cache size"""
        with self._lock:
            return len(self._cache)
    
    def capacity(self) -> int:
        """Get cache capacity"""
        return self._capacity
    
    def stats(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            return {
                "size": len(self._cache),
                "capacity": self._capacity,
                "utilization": len(self._cache) / self._capacity if self._capacity > 0 else 0.0,
            }


class SchemaCache:
    """
    Specialized cache for compiled schemas.
    
    Provides schema-specific caching with LRU eviction
    and optional TTL support.
    """
    
    def __init__(self, capacity: int = 1000, ttl_seconds: Optional[float] = 3600):
        """
        Initialize schema cache.
        
        Args:
            capacity: Maximum cached schemas
            ttl_seconds: Cache TTL (default 1 hour)
        """
        self._cache = LRUCache[any](capacity=capacity, ttl_seconds=ttl_seconds)
        self._hits = 0
        self._misses = 0
        self._lock = threading.Lock()
    
    def get(self, schema_hash: str) -> Optional[Any]:
        """
        Get compiled schema from cache.
        
        Args:
            schema_hash: Schema hash as key
            
        Returns:
            Compiled schema or None
        """
        result = self._cache.get(schema_hash)
        
        with self._lock:
            if result is not None:
                self._hits += 1
            else:
                self._misses += 1
        
        return result
    
    def set(self, schema_hash: str, compiled_schema: Any) -> None:
        """
        Cache compiled schema.
        
        Args:
            schema_hash: Schema hash as key
            compiled_schema: Compiled schema to cache
        """
        self._cache.set(schema_hash, compiled_schema)
    
    def hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        with self._lock:
            self._hits = 0
            self._misses = 0
    
    def stats(self) -> dict:
        """Get cache statistics"""
        cache_stats = self._cache.stats()
        cache_stats["hits"] = self._hits
        cache_stats["misses"] = self._misses
        cache_stats["hit_rate"] = self.hit_rate()
        return cache_stats
