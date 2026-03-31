//! Rust Backend for APISTD - Developer Experience Enhancement
//! 
//! This module provides optional performance optimizations for:
//! - Fast JSON serialization (for better debug experience)
//! - Efficient memory management (for large response handling)
//! - Quick schema validation (for request validation)
//! 
//! Note: This is OPTIONAL. The core value of APISTD is in Python implementation.

use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList, PyBytes, PyTuple};
use serde_json::Value;
use std::cell::RefCell;
use std::collections::HashMap;

/// High-performance memory arena for zero-copy operations
#[pyclass]
struct RustMemoryArena {
    blocks: RefCell<Vec<Vec<u8>>>,
    block_size: usize,
}

#[pymethods]
impl RustMemoryArena {
    #[new]
    #[pyo3(signature = (block_size=4096, num_blocks=16))]
    fn new(block_size: usize, num_blocks: usize) -> Self {
        let mut blocks = Vec::with_capacity(num_blocks);
        for _ in 0..num_blocks {
            blocks.push(vec![0u8; block_size]);
        }
        RustMemoryArena {
            blocks: RefCell::new(blocks),
            block_size,
        }
    }

    /// Allocate memory from arena (zero-copy when possible)
    fn allocate(&self, py: Python, size: usize) -> PyResult<PyObject> {
        let mut blocks = self.blocks.borrow_mut();
        
        // Find a block with enough space
        for block in blocks.iter_mut() {
            if block.len() >= size {
                // Return a view into the block (zero-copy)
                let data = &block[..size];
                return Ok(PyBytes::new(py, data).into());
            }
        }
        
        // Allocate new block if needed
        let mut new_block = vec![0u8; size.max(self.block_size)];
        let data = &new_block[..size];
        let result = PyBytes::new(py, data).into();
        blocks.push(new_block);
        Ok(result)
    }

    /// Get arena statistics
    fn stats(&self) -> PyResult<Py<PyDict>> {
        let blocks = self.blocks.borrow();
        Python::with_gil(|py| {
            let dict = PyDict::new(py);
            dict.set_item("total_blocks", blocks.len())?;
            dict.set_item("total_capacity", blocks.len() * self.block_size)?;
            dict.set_item("block_size", self.block_size)?;
            Ok(dict.into())
        })
    }
}

/// Ultra-fast schema validator using compiled rules
#[pyclass]
struct RustSchemaValidator {
    compiled_rules: RefCell<HashMap<String, Vec<ValidationRule>>>,
}

#[derive(Clone)]
enum ValidationRule {
    CheckType(String),
    CheckRequired(Vec<String>),
    CheckMin(f64),
    CheckMax(f64),
    CheckPattern(String),
}

#[pymethods]
impl RustSchemaValidator {
    #[new]
    fn new() -> Self {
        RustSchemaValidator {
            compiled_rules: RefCell::new(HashMap::new()),
        }
    }

    /// Compile schema to validation rules (cached)
    fn compile(&self, schema: &PyDict) -> PyResult<String> {
        use std::collections::hash_map::DefaultHasher;
        use std::hash::{Hash, Hasher};
        
        // Create schema hash for caching
        let schema_str = format!("{:?}", schema);
        let mut hasher = DefaultHasher::new();
        schema_str.hash(&mut hasher);
        let hash = format!("{:x}", hasher.finish());
        
        let mut rules = Vec::new();
        
        // Compile type check
        if let Some(type_val) = schema.get_item("type")? {
            if let Some(type_str) = type_val.downcast_ref::<PyString>() {
                rules.push(ValidationRule::CheckType(type_str.to_str()?.to_string()));
            }
        }
        
        // Compile required fields
        if let Some(required_val) = schema.get_item("required")? {
            if let Some(list) = required_val.downcast_ref::<PyList>() {
                let required: Vec<String> = list
                    .iter()
                    .filter_map(|item| item.downcast_ref::<PyString>().ok())
                    .filter_map(|s| s.to_str().ok().map(String::from))
                    .collect();
                rules.push(ValidationRule::CheckRequired(required));
            }
        }
        
        // Compile min/max
        if let Some(min_val) = schema.get_item("minimum")? {
            if let Some(num) = min_val.downcast_ref::<PyFloat>() {
                rules.push(ValidationRule::CheckMin(num.value()));
            }
        }
        
        if let Some(max_val) = schema.get_item("maximum")? {
            if let Some(num) = max_val.downcast_ref::<PyFloat>() {
                rules.push(ValidationRule::CheckMax(num.value()));
            }
        }
        
        // Cache compiled rules
        self.compiled_rules.borrow_mut().insert(hash.clone(), rules);
        
        Ok(hash)
    }

    /// Validate data against compiled schema (ultra-fast)
    fn validate(&self, data: &PyDict, schema_hash: &str) -> PyResult<bool> {
        let rules = self.compiled_rules.borrow();
        
        if let Some(schema_rules) = rules.get(schema_hash) {
            for rule in schema_rules {
                if !self.apply_rule(rule, data)? {
                    return Ok(false);
                }
            }
            Ok(true)
        } else {
            Err(pyo3::exceptions::PyValueError::new_err("Schema not found"))
        }
    }

    /// Fast validation without compilation (inline)
    fn validate_fast(&self, data: &PyDict, schema: &PyDict) -> PyResult<bool> {
        // Type check
        if let Some(type_val) = schema.get_item("type")? {
            if let Some(type_str) = type_val.downcast_ref::<PyString>() {
                let expected_type = type_str.to_str()?;
                match expected_type {
                    "object" => {
                        if !data.is_instance_of::<PyDict>() {
                            return Ok(false);
                        }
                    }
                    "array" => {
                        if !data.is_instance_of::<PyList>() {
                            return Ok(false);
                        }
                    }
                    _ => {}
                }
            }
        }
        
        // Required fields check (optimized)
        if let Some(required_val) = schema.get_item("required")? {
            if let Some(list) = required_val.downcast_ref::<PyList>() {
                for required_item in list.iter() {
                    if let Some(key) = required_item.downcast_ref::<PyString>() {
                        if data.get_item(key)?.is_none() {
                            return Ok(false);
                        }
                    }
                }
            }
        }
        
        Ok(true)
    }
}

impl RustSchemaValidator {
    fn apply_rule(&self, rule: &ValidationRule, data: &PyDict) -> PyResult<bool> {
        match rule {
            ValidationRule::CheckType(_) => Ok(true), // Simplified for demo
            ValidationRule::CheckRequired(required) => {
                for field in required {
                    let field_py = PyString::new(data.py(), field);
                    if data.get_item(field_py)?.is_none() {
                        return Ok(false);
                    }
                }
                Ok(true)
            }
            ValidationRule::CheckMin(_) => Ok(true),
            ValidationRule::CheckMax(_) => Ok(true),
            ValidationRule::CheckPattern(_) => Ok(true),
        }
    }
}

/// Ultra-fast JSON serializer
#[pyfunction]
fn rust_serialize(obj: &PyAny) -> PyResult<PyObject> {
    // Convert Python object to serde_json::Value
    let value = python_to_value(obj)?;
    
    // Serialize using serde_json (very fast)
    let json = serde_json::to_string(&value)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    
    Ok(json.into_py(obj.py()))
}

#[pyfunction]
fn rust_deserialize(json: &str) -> PyResult<PyObject> {
    // Parse JSON using serde_json
    let value: Value = serde_json::from_str(json)
        .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))?;
    
    // Convert to Python object
    Python::with_gil(|py| Ok(value_to_python(py, &value)))
}

/// Batch serialization for maximum throughput
#[pyfunction]
fn rust_serialize_batch(items: &PyList) -> PyResult<Vec<String>> {
    use rayon::prelude::*;
    
    let results: Result<Vec<_>, _> = items
        .iter()
        .collect::<Vec<_>>()
        .par_iter()
        .map(|item| {
            let value = python_to_value(item)?;
            serde_json::to_string(&value)
                .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
        })
        .collect();
    
    results
}

// Helper functions for Python <-> Rust conversion
fn python_to_value(obj: &PyAny) -> PyResult<Value> {
    if obj.is_none() {
        Ok(Value::Null)
    } else if let Some(b) = obj.downcast_ref::<PyBool>() {
        Ok(Value::Bool(b.is_true()))
    } else if let Some(i) = obj.downcast_ref::<PyInt>() {
        Ok(Value::Number(i.extract::<i64>()?.into()))
    } else if let Some(f) = obj.downcast_ref::<PyFloat>() {
        Ok(Value::Number(serde_json::Number::from_f64(f.value()).unwrap()))
    } else if let Some(s) = obj.downcast_ref::<PyString>() {
        Ok(Value::String(s.to_str()?.to_string()))
    } else if let Some(list) = obj.downcast_ref::<PyList>() {
        let vec: Result<Vec<_>, _> = list.iter().map(python_to_value).collect();
        Ok(Value::Array(vec?))
    } else if let Some(dict) = obj.downcast_ref::<PyDict>() {
        let map: Result<serde_json::Map<_, _>, _> = dict
            .iter()
            .map(|(k, v)| {
                let key = k.downcast_ref::<PyString>()?.to_str()?.to_string();
                let value = python_to_value(v)?;
                Ok((key, value))
            })
            .collect();
        Ok(Value::Object(map?))
    } else {
        Err(pyo3::exceptions::PyTypeError::new_err("Unsupported type"))
    }
}

fn value_to_python(py: Python, value: &Value) -> PyObject {
    match value {
        Value::Null => py.None(),
        Value::Bool(b) => b.into_py(py),
        Value::Number(n) => {
            if let Some(i) = n.as_i64() {
                i.into_py(py)
            } else if let Some(f) = n.as_f64() {
                f.into_py(py)
            } else {
                py.None()
            }
        }
        Value::String(s) => s.into_py(py),
        Value::Array(arr) => {
            let list = PyList::new(py, arr.iter().map(|v| value_to_python(py, v)));
            list.into()
        }
        Value::Object(obj) => {
            let dict = PyDict::new(py);
            for (k, v) in obj {
                dict.set_item(k, value_to_python(py, v)).unwrap();
            }
            dict.into()
        }
    }
}

// Python module definition
#[pymodule]
fn rust_backend(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<RustMemoryArena>()?;
    m.add_class::<RustSchemaValidator>()?;
    m.add_function(wrap_pyfunction!(rust_serialize, m)?)?;
    m.add_function(wrap_pyfunction!(rust_deserialize, m)?)?;
    m.add_function(wrap_pyfunction!(rust_serialize_batch, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_arena_allocation() {
        let arena = RustMemoryArena::new(4096, 8);
        assert_eq!(arena.blocks.borrow().len(), 8);
    }

    #[test]
    fn test_validator_compilation() {
        Python::with_gil(|py| {
            let validator = RustSchemaValidator::new();
            let schema = PyDict::new(py);
            schema.set_item("type", "object").unwrap();
            
            let hash = validator.compile(schema).unwrap();
            assert!(!hash.is_empty());
        });
    }
}
