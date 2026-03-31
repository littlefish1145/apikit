"""
LRU Cache Implementation

Thread-safe Least Recently Used cache with TTL support.
"""

from __future__ import annotations
from typing import Any, Optional, Generic, TypeVar
from collections import OrderedDict
import threading
import time

T = TypeVar('T')


class LRUCache(Generic[T]):
    """
    Thread-safe LRU cache with optional TTL.
    
    Features:
    - O(1) get/set operations
    - Automatic eviction of least recently used items
    - Optional time-to-live for entries
    - Thread-safe with read-write locks
    - Cache statistics and monitoring
    """
    
    def __init__(self, capacity: int = 1000, ttl_seconds: Optional[float] = None):
        """
        Initialize LRU cache.
        
        Args:
            capacity: Maximum number of entries
            ttl_seconds: Time-to-live in seconds (None for no expiry)
        """
        self._capacity = capacity
        self._ttl = ttl_seconds
        self._cache: OrderedDict[str, tuple[T, float]] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[T]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            value, timestamp = self._cache[key]
            
            if self._ttl and (time.time() - timestamp) > self._ttl:
                del self._cache[key]
                self._misses += 1
                return None
            
            self._cache.move_to_end(key)
            self._hits += 1
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
            
            while len(self._cache) > self._capacity:
                self._cache.popitem(last=False)
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
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
    
    def contains(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists and not expired
        """
        return self.get(key) is not None
    
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
    
    def hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total
    
    def stats(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            return {
                "size": len(self._cache),
                "capacity": self._capacity,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": self.hit_rate(),
                "utilization": len(self._cache) / self._capacity if self._capacity > 0 else 0.0,
            }
    
    def reset_stats(self) -> None:
        """Reset statistics"""
        with self._lock:
            self._hits = 0
            self._misses = 0
    
    def keys(self) -> list:
        """Get all cache keys"""
        with self._lock:
            return list(self._cache.keys())
    
    def values(self) -> list:
        """Get all cache values"""
        with self._lock:
            return [v for v, _ in self._cache.values()]
    
    def items(self) -> list:
        """Get all cache items"""
        with self._lock:
            return [(k, v) for k, (v, _) in self._cache.items()]
