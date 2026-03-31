"""
Streaming - Stream Processing for Large Data

Incremental processing and serialization for large datasets.
"""

from __future__ import annotations
from typing import Any, Iterator, AsyncIterator, Optional, Callable
import io


class StreamingSerializer:
    """
    Stream large data for serialization without loading everything into memory.
    
    Features:
    - Incremental serialization
    - Backpressure control
    - Memory-efficient processing
    """
    
    def __init__(self, chunk_size: int = 8192):
        """
        Initialize streaming serializer.
        
        Args:
            chunk_size: Size of chunks in bytes
        """
        self._chunk_size = chunk_size
    
    def stream_serialize(self, iterator: Iterator[dict]) -> Iterator[bytes]:
        """
        Serialize iterator to JSON stream.
        
        Args:
            iterator: Iterator of dicts
            
        Yields:
            JSON chunks
        """
        yield b'['
        
        first = True
        for item in iterator:
            if not first:
                yield b','
            first = False
            
            import json
            yield json.dumps(item, separators=(',', ':')).encode('utf-8')
        
        yield b']'
    
    def stream_deserialize(self, stream: Iterator[bytes]) -> Iterator[dict]:
        """
        Deserialize JSON stream.
        
        Args:
            stream: Iterator of bytes
            
        Yields:
            Deserialized dicts
        """
        import json
        
        buffer = b''
        in_array = False
        current_item = b''
        
        for chunk in stream:
            buffer += chunk
            
            while buffer:
                if not in_array:
                    if buffer.startswith(b'['):
                        in_array = True
                        buffer = buffer[1:]
                    else:
                        break
                
                for i, byte in enumerate(buffer):
                    if byte == ord('['):
                        in_array = True
                    elif byte == ord(']'):
                        if current_item:
                            yield json.loads(current_item.decode('utf-8'))
                        return
                    elif byte == ord(',') and in_array:
                        if current_item:
                            yield json.loads(current_item.decode('utf-8'))
                            current_item = b''
                    else:
                        current_item += bytes([byte])
                
                buffer = b''
    
    async def async_stream_serialize(self, 
                                    async_iterator: AsyncIterator[dict]) -> AsyncIterator[bytes]:
        """
        Async serialize iterator.
        
        Args:
            async_iterator: Async iterator of dicts
            
        Yields:
            JSON chunks
        """
        yield b'['
        
        first = True
        async for item in async_iterator:
            if not first:
                yield b','
            first = False
            
            import json
            chunk = json.dumps(item, separators=(',', ':')).encode('utf-8')
            yield chunk
        
        yield b']'
