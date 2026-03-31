"""
Batched Processing - Request Batching for Throughput Optimization

Groups multiple requests together for batch processing to improve throughput.
"""

from __future__ import annotations
from typing import Any, Callable, List, Optional, Generic, TypeVar
import threading
import time
from collections import deque

T = TypeVar('T')
R = TypeVar('R')


class BatchedProcessor(Generic[T, R]):
    """
    Batches requests for improved throughput.
    
    Features:
    - Configurable batch size
    - Timeout-based flushing
    - Automatic batch processing
    - Performance statistics
    """
    
    def __init__(self, 
                 processor: Callable[[List[T]], List[R]],
                 batch_size: int = 100,
                 flush_interval: float = 0.1,
                 max_pending: int = 10000):
        """
        Initialize batched processor.
        
        Args:
            processor: Function to process batches
            batch_size: Maximum batch size
            flush_interval: Seconds between automatic flushes
            max_pending: Maximum pending requests
        """
        self._processor = processor
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._max_pending = max_pending
        
        self._queue: deque[tuple[T, threading.Event, Optional[R]]] = deque()
        self._lock = threading.Lock()
        self._flush_thread: Optional[threading.Thread] = None
        self._running = True
        self._last_flush = time.time()
        
        self._processed_count = 0
        self._batch_count = 0
        
        self._start_flush_thread()
    
    def _start_flush_thread(self) -> None:
        """Start background flush thread"""
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
    
    def _flush_loop(self) -> None:
        """Background flush loop"""
        while self._running:
            time.sleep(self._flush_interval)
            
            with self._lock:
                if self._queue and (time.time() - self._last_flush) >= self._flush_interval:
                    self._flush_batch()
    
    def submit(self, item: T) -> R:
        """
        Submit item for batched processing.
        
        Args:
            item: Item to process
            
        Returns:
            Processed result
        """
        event = threading.Event()
        
        with self._lock:
            if len(self._queue) >= self._max_pending:
                self._flush_batch()
            
            self._queue.append((item, event, None))
            
            if len(self._queue) >= self._batch_size:
                self._flush_batch()
        
        event.wait()
        
        with self._lock:
            for queued_item, queued_event, result in self._queue:
                if queued_item is item:
                    return result
        
        raise RuntimeError("Item not found in queue")
    
    def _flush_batch(self) -> None:
        """Flush current batch"""
        if not self._queue:
            return
        
        batch_items = []
        batch_indices = []
        
        while self._queue and len(batch_items) < self._batch_size:
            item, event, _ = self._queue.popleft()
            batch_items.append(item)
            batch_indices.append(len(batch_items) - 1)
        
        if not batch_items:
            return
        
        self._last_flush = time.time()
        
        try:
            results = self._processor(batch_items)
            
            with self._lock:
                for i, result in enumerate(results):
                    if i < len(batch_indices):
                        idx = batch_indices[i]
                        event = self._queue[idx][1] if idx < len(self._queue) else None
                        if event:
                            event.set()
                
                self._processed_count += len(results)
                self._batch_count += 1
                
        except Exception as e:
            for _, event, _ in [(self._queue[i][1],) for i in batch_indices]:
                if event:
                    event.set()
    
    def flush(self) -> None:
        """Manually flush pending items"""
        with self._lock:
            self._flush_batch()
    
    def stop(self) -> None:
        """Stop processor"""
        self._running = False
        self.flush()
        
        if self._flush_thread:
            self._flush_thread.join(timeout=2.0)
    
    def stats(self) -> dict:
        """Get processing statistics"""
        with self._lock:
            return {
                "processed_count": self._processed_count,
                "batch_count": self._batch_count,
                "pending_count": len(self._queue),
                "batch_size": self._batch_size,
                "avg_batch_size": self._processed_count / self._batch_count if self._batch_count > 0 else 0,
            }
