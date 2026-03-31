"""
Schema Compiler - Pre-compile JSON Schema for Fast Validation

Compiles JSON Schema into optimized bytecode for rapid validation.
"""

from __future__ import annotations
from typing import Any, Optional, List, Dict
from dataclasses import dataclass
from enum import Enum, auto


class OpCode(Enum):
    """Validation bytecode operations"""
    CHECK_TYPE = auto()
    CHECK_REQUIRED = auto()
    CHECK_MIN = auto()
    CHECK_MAX = auto()
    CHECK_PATTERN = auto()
    CHECK_ENUM = auto()
    CHECK_ITEMS = auto()
    CHECK_PROPERTIES = auto()
    JUMP_IF_INVALID = auto()
    RETURN_VALID = auto()
    RETURN_INVALID = auto()


@dataclass
class Instruction:
    """Bytecode instruction"""
    opcode: OpCode
    operand: Any = None


@dataclass
class CompiledSchema:
    """Compiled schema ready for validation"""
    bytecode: List[Instruction]
    schema_hash: str
    source_schema: dict


class SchemaCompiler:
    """
    Compiles JSON Schema into optimized bytecode.
    
    Pre-compiles schema validation rules into a simple bytecode
    language that can be executed much faster than interpreting
    the schema repeatedly.
    """
    
    def __init__(self):
        """Initialize schema compiler"""
        self._cache: Dict[str, CompiledSchema] = {}
    
    def compile(self, schema: dict) -> CompiledSchema:
        """
        Compile JSON Schema to bytecode - optimized for minimal overhead.
        
        Args:
            schema: JSON Schema dict
            
        Returns:
            CompiledSchema with bytecode
        """
        # Use fast id-based caching for same object
        schema_id = id(schema)
        if schema_id in self._cache:
            return self._cache[schema_id]
        
        # Only compile if schema has validation rules
        if len(schema) <= 1:
            # Trivial schema, return empty bytecode
            compiled = CompiledSchema(
                bytecode=[],
                schema_hash=str(schema_id),
                source_schema=schema
            )
            self._cache[schema_id] = compiled
            return compiled
        
        bytecode = self._compile_schema(schema)
        compiled = CompiledSchema(
            bytecode=bytecode,
            schema_hash=str(schema_id),
            source_schema=schema
        )
        
        self._cache[schema_id] = compiled
        return compiled
    
    def _compile_schema(self, schema: dict, path: str = "") -> List[Instruction]:
        """Compile schema to bytecode instructions"""
        instructions = []
        
        if "type" in schema:
            instructions.append(Instruction(
                OpCode.CHECK_TYPE,
                {"type": schema["type"], "path": path or "root"}
            ))
        
        if "required" in schema:
            instructions.append(Instruction(
                OpCode.CHECK_REQUIRED,
                {"fields": schema["required"], "path": path or "root"}
            ))
        
        if "minimum" in schema:
            instructions.append(Instruction(
                OpCode.CHECK_MIN,
                {"value": schema["minimum"], "path": path or "root"}
            ))
        
        if "maximum" in schema:
            instructions.append(Instruction(
                OpCode.CHECK_MAX,
                {"value": schema["maximum"], "path": path or "root"}
            ))
        
        if "pattern" in schema:
            import re
            instructions.append(Instruction(
                OpCode.CHECK_PATTERN,
                {"pattern": re.compile(schema["pattern"]), "path": path or "root"}
            ))
        
        if "enum" in schema:
            instructions.append(Instruction(
                OpCode.CHECK_ENUM,
                {"values": set(schema["enum"]), "path": path or "root"}
            ))
        
        if "properties" in schema:
            for prop, prop_schema in schema["properties"].items():
                sub_path = f"{path}.{prop}" if path else prop
                sub_instructions = self._compile_schema(prop_schema, sub_path)
                instructions.append(Instruction(
                    OpCode.CHECK_PROPERTIES,
                    {"property": prop, "sub_schema": sub_instructions}
                ))
        
        if "items" in schema:
            sub_instructions = self._compile_schema(schema["items"], f"{path}[]")
            instructions.append(Instruction(
                OpCode.CHECK_ITEMS,
                {"sub_schema": sub_instructions}
            ))
        
        instructions.append(Instruction(OpCode.RETURN_VALID))
        
        return instructions
    
    def clear_cache(self) -> None:
        """Clear compilation cache"""
        self._cache.clear()
    
    def cache_size(self) -> int:
        """Get cache size"""
        return len(self._cache)
