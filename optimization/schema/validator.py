"""
Fast Schema Validator

Executes compiled schema bytecode for rapid validation.
"""

from __future__ import annotations
from typing import Any, Optional, List, Tuple
from dataclasses import dataclass
from .compiler import SchemaCompiler, CompiledSchema, OpCode, Instruction


@dataclass
class ValidationError:
    """Validation error details"""
    path: str
    message: str
    expected: Any = None
    actual: Any = None


@dataclass
class ValidationResult:
    """Validation result"""
    valid: bool
    errors: List[ValidationError]
    
    def __bool__(self) -> bool:
        return self.valid


class FastValidator:
    """
    High-performance schema validator.
    
    Executes pre-compiled schema bytecode for fast validation.
    Provides detailed error messages and short-circuit evaluation.
    """
    
    def __init__(self, compiler: Optional[SchemaCompiler] = None):
        """
        Initialize validator.
        
        Args:
            compiler: SchemaCompiler instance (creates one if None)
        """
        self._compiler = compiler or SchemaCompiler()
        self._compiled_schemas: dict = {}
    
    def validate(self, data: Any, schema: dict, 
                 short_circuit: bool = True) -> ValidationResult:
        """
        Validate data against schema - optimized for speed.
        
        For simple schemas, use direct validation (faster than bytecode).
        For complex schemas, use compiled bytecode.
        
        Args:
            data: Data to validate
            schema: JSON Schema
            short_circuit: Stop on first error
            
        Returns:
            ValidationResult with errors if any
        """
        # For very simple schemas, direct validation is faster
        if len(schema) <= 2 and "type" in schema:
            errors = self._quick_validate(data, schema)
            return ValidationResult(valid=len(errors) == 0, errors=errors)
        
        # For complex schemas, use compiled bytecode
        compiled = self._compiler.compile(schema)
        
        # Skip execution if no bytecode (trivial schema)
        if not compiled.bytecode:
            return ValidationResult(valid=True, errors=[])
        
        errors = self._execute_bytecode(data, compiled.bytecode)
        return ValidationResult(valid=len(errors) == 0, errors=errors)
    
    def _quick_validate(self, data: Any, schema: dict) -> List[ValidationError]:
        """Quick validation for simple schemas - no bytecode overhead"""
        errors = []
        
        # Type check
        if "type" in schema:
            expected = schema["type"]
            type_map = {
                "string": str, "integer": int, "number": (int, float),
                "boolean": bool, "array": list, "object": dict, "null": type(None),
            }
            python_type = type_map.get(expected)
            if python_type and not isinstance(data, python_type):
                errors.append(ValidationError(
                    path="root", message=f"Expected {expected}",
                    expected=expected, actual=type(data).__name__
                ))
        
        # Required check
        if isinstance(data, dict) and "required" in schema:
            for field in schema["required"]:
                if field not in data:
                    errors.append(ValidationError(
                        path=f".{field}", message="Required field missing",
                        expected=field, actual=None
                    ))
        
        return errors
    
    def validate_fast(self, data: Any, schema_hash: str) -> bool:
        """
        Fast validation without error details.
        
        Args:
            data: Data to validate
            schema_hash: Hash of pre-compiled schema
            
        Returns:
            True if valid, False otherwise
        """
        if schema_hash not in self._compiled_schemas:
            raise ValueError(f"Schema not found: {schema_hash}")
        
        compiled = self._compiled_schemas[schema_hash]
        errors = self._execute_bytecode(data, compiled.bytecode)
        return len(errors) == 0
    
    def _execute_bytecode(self, data: Any, 
                         bytecode: List[Instruction]) -> List[ValidationError]:
        """Execute validation bytecode"""
        errors = []
        
        for instruction in bytecode:
            error = self._execute_instruction(data, instruction)
            if error:
                errors.append(error)
        
        return errors
    
    def _execute_instruction(self, data: Any, 
                            instruction: Instruction) -> Optional[ValidationError]:
        """Execute single instruction"""
        op = instruction.opcode
        operand = instruction.operand
        
        if op == OpCode.CHECK_TYPE:
            return self._check_type(data, operand)
        
        elif op == OpCode.CHECK_REQUIRED:
            return self._check_required(data, operand)
        
        elif op == OpCode.CHECK_MIN:
            return self._check_min(data, operand)
        
        elif op == OpCode.CHECK_MAX:
            return self._check_max(data, operand)
        
        elif op == OpCode.CHECK_PATTERN:
            return self._check_pattern(data, operand)
        
        elif op == OpCode.CHECK_ENUM:
            return self._check_enum(data, operand)
        
        elif op == OpCode.CHECK_PROPERTIES:
            return self._check_properties(data, operand)
        
        elif op == OpCode.CHECK_ITEMS:
            return self._check_items(data, operand)
        
        return None
    
    def _check_type(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check type constraint"""
        expected_type = operand["type"]
        path = operand["path"]
        
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        
        python_type = type_map.get(expected_type)
        if python_type is None:
            return None
        
        if not isinstance(data, python_type):
            return ValidationError(
                path=path,
                message=f"Expected type {expected_type}",
                expected=expected_type,
                actual=type(data).__name__
            )
        
        return None
    
    def _check_required(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check required fields"""
        if not isinstance(data, dict):
            return None
        
        fields = operand["fields"]
        path = operand["path"]
        
        for field in fields:
            if field not in data:
                return ValidationError(
                    path=f"{path}.{field}",
                    message=f"Required field missing",
                    expected=field,
                    actual=None
                )
        
        return None
    
    def _check_min(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check minimum value"""
        if not isinstance(data, (int, float)):
            return None
        
        min_val = operand["value"]
        path = operand["path"]
        
        if data < min_val:
            return ValidationError(
                path=path,
                message=f"Value below minimum",
                expected=f">= {min_val}",
                actual=data
            )
        
        return None
    
    def _check_max(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check maximum value"""
        if not isinstance(data, (int, float)):
            return None
        
        max_val = operand["value"]
        path = operand["path"]
        
        if data > max_val:
            return ValidationError(
                path=path,
                message=f"Value above maximum",
                expected=f"<= {max_val}",
                actual=data
            )
        
        return None
    
    def _check_pattern(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check regex pattern"""
        if not isinstance(data, str):
            return None
        
        pattern = operand["pattern"]
        path = operand["path"]
        
        if not pattern.match(data):
            return ValidationError(
                path=path,
                message=f"Pattern mismatch",
                expected=pattern.pattern,
                actual=data
            )
        
        return None
    
    def _check_enum(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check enum values"""
        path = operand["path"]
        values = operand["values"]
        
        if data not in values:
            return ValidationError(
                path=path,
                message=f"Value not in enum",
                expected=list(values),
                actual=data
            )
        
        return None
    
    def _check_properties(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check object properties"""
        if not isinstance(data, dict):
            return None
        
        prop = operand["property"]
        sub_schema = operand["sub_schema"]
        
        if prop not in data:
            return None
        
        return self._execute_bytecode(data[prop], sub_schema)
    
    def _check_items(self, data: Any, operand: dict) -> Optional[ValidationError]:
        """Check array items"""
        if not isinstance(data, list):
            return None
        
        sub_schema = operand["sub_schema"]
        
        for i, item in enumerate(data):
            errors = self._execute_bytecode(item, sub_schema)
            if errors:
                return errors[0]
        
        return None
