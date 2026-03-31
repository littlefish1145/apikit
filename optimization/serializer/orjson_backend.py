"""
orjson Backend for Ultra-Fast JSON Serialization

Direct orjson integration with numpy/pandas support.
"""

from __future__ import annotations
from typing import Any, Optional
import sys


class OrlsonBackend:
    """
    orjson-based JSON backend with extended type support.
    
    Provides the fastest possible JSON serialization with support for:
    - numpy arrays
    - pandas DataFrames
    - datetime objects
    - UUID objects
    - Custom types via default handler
    """
    
    def __init__(self):
        """Initialize orjson backend"""
        try:
            import orjson
            self._orjson = orjson
            self._available = True
        except ImportError:
            self._available = False
            self._orjson = None
    
    @property
    def available(self) -> bool:
        """Check if orjson is available"""
        return self._available
    
    def dumps(self, obj: Any, *, option: Optional[int] = None) -> bytes:
        """
        Serialize to JSON bytes.
        
        Args:
            obj: Object to serialize
            option: orjson options (bitmask)
            
        Returns:
            JSON bytes
        """
        if not self._available:
            raise ImportError("orjson is not installed")
        
        if option is None:
            option = self._orjson.OPT_NON_STR_KEYS | self._orjson.OPT_SERIALIZE_DATACLASS
        
        return self._orjson.dumps(obj, option=option)
    
    def loads(self, data: bytes | str) -> Any:
        """
        Deserialize from JSON.
        
        Args:
            data: JSON bytes or string
            
        Returns:
            Deserialized object
        """
        if not self._available:
            raise ImportError("orjson is not installed")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return self._orjson.loads(data)
    
    def dumps_ndarray(self, arr) -> bytes:
        """
        Serialize numpy array efficiently.
        
        Args:
            arr: numpy array
            
        Returns:
            JSON bytes
        """
        if not self._available:
            raise ImportError("orjson is not installed")
        
        try:
            import numpy as np
        except ImportError:
            raise ImportError("numpy is not installed")
        
        return self._orjson.dumps({
            "dtype": str(arr.dtype),
            "shape": arr.shape,
            "data": arr.tolist()
        })
    
    def loads_ndarray(self, data: bytes) -> Any:
        """
        Deserialize numpy array.
        
        Args:
            data: JSON bytes
            
        Returns:
            numpy array
        """
        if not self._available:
            raise ImportError("orjson is not installed")
        
        try:
            import numpy as np
        except ImportError:
            raise ImportError("numpy is not installed")
        
        obj = self._orjson.loads(data)
        return np.array(obj["data"], dtype=obj["dtype"]).reshape(obj["shape"])
