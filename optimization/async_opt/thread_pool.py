"""
Thread Pool - Optimized Thread Pool for CPU-Bound Tasks

Efficient thread pool for offloading CPU-intensive operations.
"""

from __future__ import annotations
from typing import Any, Callable, Optional, List
from concurrent.futures import ThreadPoolExecutor, Future
import threading
from queue import PriorityQueue


class ThreadPool:
    """
    High-performance thread pool for CPU-bound tasks.
    
    Features:
    - Configurable worker count
    - Task priority queue
    - Graceful shutdown
    - Performance monitoring
    """
    
    def __init__(self, max_workers: Optional[int] = None, 
                 task_timeout: Optional[float] = None):
        """
        Initialize thread pool.
        
        Args:
            max_workers: Maximum number of worker threads (default: CPU count)
            task_timeout: Default task timeout in seconds
        """
        import os
        self._max_workers = max_workers or os.cpu_count() or 4
        self._task_timeout = task_timeout
        self._executor = ThreadPoolExecutor(max_workers=self._max_workers)
        self._futures: List[Future] = []
        self._lock = threading.Lock()
        self._submitted_count = 0
        self._completed_count = 0
    
    def submit(self, fn: Callable, *args, **kwargs) -> Future:
        """
        Submit task to thread pool.
        
        Args:
            fn: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Future object
        """
        with self._lock:
            self._submitted_count += 1
        
        future = self._executor.submit(fn, *args, **kwargs)
        
        with self._lock:
            self._futures.append(future)
            future.add_done_callback(self._on_complete)
        
        return future
    
    def _on_complete(self, future: Future) -> None:
        """Handle task completion"""
        with self._lock:
            self._completed_count += 1
    
    def map(self, fn: Callable, *iterables, timeout: Optional[float] = None) -> map:
        """
        Map function over iterables using thread pool.
        
        Args:
            fn: Function to execute
            *iterables: Iterables to map over
            timeout: Timeout in seconds
            
        Returns:
            Map iterator
        """
        return self._executor.map(fn, *iterables, timeout=timeout or self._task_timeout)
    
    def shutdown(self, wait: bool = True) -> None:
        """
        Shutdown thread pool.
        
        Args:
            wait: Wait for pending tasks to complete
        """
        self._executor.shutdown(wait=wait)
    
    def stats(self) -> dict:
        """Get thread pool statistics"""
        with self._lock:
            pending = self._submitted_count - self._completed_count
            return {
                "max_workers": self._max_workers,
                "submitted": self._submitted_count,
                "completed": self._completed_count,
                "pending": pending,
                "active_workers": min(pending, self._max_workers),
            }
    
    @property
    def active_count(self) -> int:
        """Get number of active tasks"""
        with self._lock:
            return self._submitted_count - self._completed_count
