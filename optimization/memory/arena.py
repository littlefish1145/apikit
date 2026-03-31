"""
Memory Arena - High-performance memory pool allocator

Pre-allocates memory blocks to reduce malloc overhead and enable
memory reuse for zero-garbage operations.
"""

from __future__ import annotations
from typing import Optional
from dataclasses import dataclass, field
import threading


@dataclass
class ArenaStats:
    """Statistics for memory arena usage"""
    total_allocated: int = 0
    total_freed: int = 0
    active_blocks: int = 0
    peak_usage: int = 0
    allocation_count: int = 0
    reuse_count: int = 0


class MemoryArena:
    """
    Memory pool for efficient allocation and reuse.
    
    Pre-allocates large blocks of memory and serves smaller
    allocations from these blocks, reducing system calls and
    enabling memory reuse.
    """
    
    def __init__(self, block_size: int = 4096, num_blocks: int = 16):
        """
        Initialize memory arena.
        
        Args:
            block_size: Size of each pre-allocated block in bytes
            num_blocks: Number of blocks to pre-allocate
        """
        self.block_size = block_size
        self.initial_blocks = num_blocks
        self._blocks: list[bytearray] = []
        self._free_blocks: list[bytearray] = []
        self._active_views: dict[int, memoryview] = {}
        self._lock = threading.Lock()
        self._stats = ArenaStats()
        
        self._initialize_blocks()
    
    def _initialize_blocks(self) -> None:
        """Pre-allocate memory blocks"""
        for _ in range(self.initial_blocks):
            block = bytearray(self.block_size)
            self._blocks.append(block)
            self._free_blocks.append(block)
        self._stats.active_blocks = len(self._blocks)
    
    def allocate(self, size: int) -> memoryview:
        """
        Allocate memory of given size.
        
        Args:
            size: Number of bytes to allocate
            
        Returns:
            memoryview to the allocated memory region
        """
        if size <= 0:
            raise ValueError("Size must be positive")
        
        with self._lock:
            self._stats.allocation_count += 1
            
            if size <= self.block_size:
                return self._allocate_from_block(size)
            else:
                return self._allocate_large_block(size)
    
    def _allocate_from_block(self, size: int) -> memoryview:
        """Allocate from existing block"""
        if self._free_blocks:
            block = self._free_blocks.pop()
            self._stats.reuse_count += 1
        else:
            block = bytearray(self.block_size)
            self._blocks.append(block)
            self._stats.active_blocks += 1
        
        self._stats.total_allocated += size
        if self._stats.total_allocated > self._stats.peak_usage:
            self._stats.peak_usage = self._stats.total_allocated
        
        view = memoryview(block)[:size]
        block_id = id(block)
        self._active_views[block_id] = view
        
        return view
    
    def _allocate_large_block(self, size: int) -> memoryview:
        """Allocate large block directly"""
        block = bytearray(size)
        self._blocks.append(block)
        self._stats.total_allocated += size
        self._stats.active_blocks += 1
        
        view = memoryview(block)
        self._active_views[id(block)] = view
        
        return view
    
    def deallocate(self, view: memoryview) -> None:
        """
        Return memory to the pool.
        
        Args:
            view: memoryview to deallocate
        """
        with self._lock:
            obj = view.obj
            if obj is not None:
                block_id = id(obj)
                if block_id in self._active_views:
                    del self._active_views[block_id]
                    self._free_blocks.append(obj)
                    self._stats.total_freed += len(view)
    
    def reset(self) -> None:
        """Reset arena and free all allocations"""
        with self._lock:
            self._free_blocks.clear()
            self._active_views.clear()
            
            for block in self._blocks:
                self._free_blocks.append(block)
            
            self._stats.total_allocated = 0
            self._stats.total_freed = 0
            self._stats.allocation_count = 0
            self._stats.reuse_count = 0
    
    def stats(self) -> ArenaStats:
        """Get arena statistics"""
        with self._lock:
            return ArenaStats(
                total_allocated=self._stats.total_allocated,
                total_freed=self._stats.total_freed,
                active_blocks=self._stats.active_blocks,
                peak_usage=self._stats.peak_usage,
                allocation_count=self._stats.allocation_count,
                reuse_count=self._stats.reuse_count,
            )
    
    def utilization(self) -> float:
        """Get memory utilization ratio (0.0 - 1.0)"""
        stats = self.stats()
        if stats.active_blocks == 0:
            return 0.0
        total_capacity = stats.active_blocks * self.block_size
        return stats.peak_usage / total_capacity if total_capacity > 0 else 0.0
