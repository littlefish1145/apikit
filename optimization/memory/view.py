"""
Memory View - Type-safe memory interpretation

Provides type-safe views over raw memory for interpreting bytes
as different data types without copying.
"""

from __future__ import annotations
from typing import Union, Optional, Any
import struct
import sys


class MemoryView:
    """
    Type-safe memory view for interpreting raw bytes.
    
    Provides convenient methods to read/write different data types
    from/to a memory buffer without copying.
    """
    
    def __init__(self, data: Union[bytes, bytearray, memoryview], 
                 byteorder: str = 'little'):
        """
        Initialize memory view.
        
        Args:
            data: Underlying data buffer
            byteorder: Byte order ('little' or 'big')
        """
        if isinstance(data, (bytes, bytearray)):
            self._view = memoryview(data)
        elif isinstance(data, memoryview):
            self._view = data
        else:
            raise TypeError(f"Unsupported type: {type(data)}")
        
        self._byteorder = byteorder
        self._offset = 0
    
    @property
    def nbytes(self) -> int:
        """Get view size in bytes"""
        return len(self._view)
    
    @property
    def offset(self) -> int:
        """Get current offset"""
        return self._offset
    
    def seek(self, offset: int) -> MemoryView:
        """
        Set current offset.
        
        Args:
            offset: New offset
            
        Returns:
            self for chaining
        """
        self._offset = offset
        return self
    
    def read_int8(self, offset: Optional[int] = None) -> int:
        """Read signed 8-bit integer"""
        pos = offset if offset is not None else self._offset
        value = self._view[pos]
        if value >= 128:
            value -= 256
        self._offset = pos + 1
        return value
    
    def read_uint8(self, offset: Optional[int] = None) -> int:
        """Read unsigned 8-bit integer"""
        pos = offset if offset is not None else self._offset
        value = self._view[pos]
        self._offset = pos + 1
        return value
    
    def read_int16(self, offset: Optional[int] = None) -> int:
        """Read signed 16-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}h'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 2
        return value
    
    def read_uint16(self, offset: Optional[int] = None) -> int:
        """Read unsigned 16-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}H'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 2
        return value
    
    def read_int32(self, offset: Optional[int] = None) -> int:
        """Read signed 32-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}i'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 4
        return value
    
    def read_uint32(self, offset: Optional[int] = None) -> int:
        """Read unsigned 32-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}I'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 4
        return value
    
    def read_int64(self, offset: Optional[int] = None) -> int:
        """Read signed 64-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}q'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 8
        return value
    
    def read_uint64(self, offset: Optional[int] = None) -> int:
        """Read unsigned 64-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}Q'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 8
        return value
    
    def read_float32(self, offset: Optional[int] = None) -> float:
        """Read 32-bit float"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}f'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 4
        return value
    
    def read_float64(self, offset: Optional[int] = None) -> float:
        """Read 64-bit float"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}d'
        value = struct.unpack_from(fmt, self._view, pos)[0]
        self._offset = pos + 8
        return value
    
    def read_string(self, length: int, offset: Optional[int] = None,
                    encoding: str = 'utf-8') -> str:
        """
        Read string of given length.
        
        Args:
            length: String length in bytes
            offset: Read offset
            encoding: String encoding
            
        Returns:
            Decoded string
        """
        pos = offset if offset is not None else self._offset
        data = self._view[pos:pos + length]
        self._offset = pos + length
        return data.tobytes().decode(encoding)
    
    def write_int8(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write signed 8-bit integer"""
        pos = offset if offset is not None else self._offset
        if value < 0:
            value += 256
        self._view[pos] = value & 0xFF
        self._offset = pos + 1
        return self
    
    def write_uint8(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write unsigned 8-bit integer"""
        pos = offset if offset is not None else self._offset
        self._view[pos] = value & 0xFF
        self._offset = pos + 1
        return self
    
    def write_int16(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write signed 16-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}h'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 2
        return self
    
    def write_uint16(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write unsigned 16-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}H'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 2
        return self
    
    def write_int32(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write signed 32-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}i'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 4
        return self
    
    def write_uint32(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write unsigned 32-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}I'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 4
        return self
    
    def write_int64(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write signed 64-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}q'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 8
        return self
    
    def write_uint64(self, value: int, offset: Optional[int] = None) -> MemoryView:
        """Write unsigned 64-bit integer"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}Q'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 8
        return self
    
    def write_float32(self, value: float, offset: Optional[int] = None) -> MemoryView:
        """Write 32-bit float"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}f'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 4
        return self
    
    def write_float64(self, value: float, offset: Optional[int] = None) -> MemoryView:
        """Write 64-bit float"""
        pos = offset if offset is not None else self._offset
        fmt = f'{self._byteorder}d'
        struct.pack_into(fmt, self._view, pos, value)
        self._offset = pos + 8
        return self
    
    def write_string(self, value: str, offset: Optional[int] = None,
                     encoding: str = 'utf-8') -> MemoryView:
        """
        Write string.
        
        Args:
            value: String to write
            offset: Write offset
            encoding: String encoding
            
        Returns:
            self for chaining
        """
        pos = offset if offset is not None else self._offset
        data = value.encode(encoding)
        self._view[pos:pos + len(data)] = data
        self._offset = pos + len(data)
        return self
    
    def slice(self, start: int, end: int) -> MemoryView:
        """
        Create sub-view.
        
        Args:
            start: Start offset
            end: End offset
            
        Returns:
            New MemoryView
        """
        return MemoryView(self._view[start:end], self._byteorder)
    
    def tobytes(self) -> bytes:
        """Convert to bytes"""
        return self._view.tobytes()
