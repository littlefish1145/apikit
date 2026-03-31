"""
Zero-Copy Buffer Implementation

Provides zero-copy memory operations using Python's memoryview protocol.
Eliminates unnecessary data copying for maximum performance.
"""

from __future__ import annotations
from typing import Optional, Union, Any
import struct


class ZeroCopyBuffer:
    """
    Zero-copy buffer for efficient memory operations.
    
    Uses memoryview to provide slice operations without copying data.
    Supports efficient read/write operations with bounds checking.
    """
    
    def __init__(self, data: Union[bytes, bytearray, memoryview, int]):
        """
        Initialize zero-copy buffer.
        
        Args:
            data: Initial data or size (int) for buffer
        """
        if isinstance(data, int):
            self._buffer = bytearray(data)
        elif isinstance(data, (bytes, bytearray)):
            self._buffer = bytearray(data)
        elif isinstance(data, memoryview):
            self._buffer = bytearray(data.tobytes())
        else:
            raise TypeError(f"Unsupported type: {type(data)}")
        
        self._view = memoryview(self._buffer)
        self._readonly = False
    
    @property
    def nbytes(self) -> int:
        """Get buffer size in bytes"""
        return len(self._buffer)
    
    @property
    def view(self) -> memoryview:
        """Get memoryview of buffer"""
        return self._view
    
    def __getitem__(self, key: Union[int, slice]) -> Union[int, memoryview]:
        """
        Access buffer data without copying.
        
        Args:
            key: Index or slice
            
        Returns:
            Single byte (int) or memoryview (slice)
        """
        if isinstance(key, slice):
            return self._view[key]
        return self._buffer[key]
    
    def __setitem__(self, key: Union[int, slice], value: Union[int, bytes, memoryview]) -> None:
        """
        Set buffer data.
        
        Args:
            key: Index or slice
            value: Data to write
        """
        if isinstance(key, slice):
            if isinstance(value, memoryview):
                self._buffer[key] = value.tobytes()
            elif isinstance(value, bytes):
                self._buffer[key] = value
            else:
                raise TypeError(f"Unsupported value type: {type(value)}")
        else:
            self._buffer[key] = value
    
    def __len__(self) -> int:
        """Get buffer length"""
        return len(self._buffer)
    
    def read(self, offset: int = 0, size: Optional[int] = None) -> memoryview:
        """
        Read data from buffer without copying.
        
        Args:
            offset: Start offset
            size: Number of bytes to read (None for rest of buffer)
            
        Returns:
            memoryview to the data
        """
        if size is None:
            return self._view[offset:]
        return self._view[offset:offset + size]
    
    def write(self, data: Union[bytes, memoryview], offset: int = 0) -> int:
        """
        Write data to buffer.
        
        Args:
            data: Data to write
            offset: Write offset
            
        Returns:
            Number of bytes written
        """
        if isinstance(data, memoryview):
            data = data.tobytes()
        
        end = offset + len(data)
        if end > len(self._buffer):
            raise ValueError("Write exceeds buffer size")
        
        self._buffer[offset:end] = data
        return len(data)
    
    def slice(self, start: int, end: int) -> memoryview:
        """
        Create zero-copy slice.
        
        Args:
            start: Start offset
            end: End offset
            
        Returns:
            memoryview to the slice
        """
        return self._view[start:end]
    
    def pack(self, offset: int, format: str, *values: Any) -> int:
        """
        Pack values into buffer using struct format.
        
        Args:
            offset: Write offset
            format: struct format string
            values: Values to pack
            
        Returns:
            Number of bytes written
        """
        data = struct.pack(format, *values)
        return self.write(data, offset)
    
    def unpack(self, offset: int, format: str) -> tuple:
        """
        Unpack values from buffer.
        
        Args:
            offset: Read offset
            format: struct format string
            
        Returns:
            Unpacked values
        """
        size = struct.calcsize(format)
        data = self._view[offset:offset + size]
        return struct.unpack(format, data)
    
    def copy_from(self, source: ZeroCopyBuffer, src_offset: int = 0, 
                  dst_offset: int = 0, size: Optional[int] = None) -> int:
        """
        Copy data from another buffer without intermediate copies.
        
        Args:
            source: Source buffer
            src_offset: Source offset
            dst_offset: Destination offset
            size: Bytes to copy (None for all available)
            
        Returns:
            Number of bytes copied
        """
        if size is None:
            size = min(
                source.nbytes - src_offset,
                self.nbytes - dst_offset
            )
        
        self._buffer[dst_offset:dst_offset + size] = source._buffer[src_offset:src_offset + size]
        return size
    
    def tobytes(self) -> bytes:
        """Convert buffer to bytes (creates copy)"""
        return bytes(self._buffer)
    
    def make_readonly(self) -> None:
        """Make buffer read-only"""
        self._readonly = True
    
    @property
    def readonly(self) -> bool:
        """Check if buffer is read-only"""
        return self._readonly
