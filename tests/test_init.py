"""
Basic Import and Initialization Test

Verifies that all optimization modules can be imported and initialized correctly.
"""

import sys
sys.path.insert(0, 'c:/Users/fish_/Desktop/apikit')


def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    from optimization import (
        FastJSON,
        MemoryArena,
        ZeroCopyBuffer,
        MemoryView,
        SchemaCompiler,
        SchemaCache,
        FastValidator,
        BackendSelector,
        LRUCache,
        BatchedProcessor,
    )
    
    print("✓ All imports successful")


def test_fast_json():
    """Test FastJSON functionality"""
    print("\nTesting FastJSON...")
    
    from optimization import FastJSON
    
    fast_json = FastJSON()
    
    test_data = {"name": "test", "value": 123, "active": True}
    
    serialized = fast_json.dumps(test_data)
    deserialized = fast_json.loads(serialized)
    
    assert deserialized == test_data, "Serialization/deserialization failed"
    
    print(f"✓ FastJSON working (backend: {fast_json.backend_name})")
    print(f"  Speedup estimate: {fast_json.get_speedup()}x")


def test_memory_arena():
    """Test MemoryArena functionality"""
    print("\nTesting MemoryArena...")
    
    from optimization import MemoryArena
    
    arena = MemoryArena(block_size=4096, num_blocks=8)
    
    view1 = arena.allocate(100)
    view2 = arena.allocate(200)
    
    assert len(view1) == 100
    assert len(view2) == 200
    
    stats = arena.stats()
    assert stats.allocation_count == 2
    
    print(f"✓ MemoryArena working")
    print(f"  Allocations: {stats.allocation_count}")
    print(f"  Reuse rate: {stats.reuse_count / stats.allocation_count * 100:.1f}%")


def test_zero_copy_buffer():
    """Test ZeroCopyBuffer functionality"""
    print("\nTesting ZeroCopyBuffer...")
    
    from optimization import ZeroCopyBuffer
    
    buffer = ZeroCopyBuffer(1024)
    
    buffer.write(b"Hello, World!", 0)
    data = buffer.read(0, 13)
    
    assert data.tobytes() == b"Hello, World!"
    
    slice_view = buffer.slice(0, 5)
    assert slice_view.tobytes() == b"Hello"
    
    print(f"✓ ZeroCopyBuffer working")
    print(f"  Buffer size: {buffer.nbytes} bytes")


def test_schema_validation():
    """Test schema validation functionality"""
    print("\nTesting Schema Validation...")
    
    from optimization import SchemaCompiler, FastValidator
    
    schema = {
        "type": "object",
        "required": ["id", "name"],
        "properties": {
            "id": {"type": "integer", "minimum": 1},
            "name": {"type": "string"}
        }
    }
    
    valid_data = {"id": 123, "name": "Test"}
    invalid_data = {"id": 0, "name": 123}
    
    compiler = SchemaCompiler()
    validator = FastValidator(compiler)
    
    result_valid = validator.validate(valid_data, schema)
    result_invalid = validator.validate(invalid_data, schema)
    
    assert result_valid.valid, "Valid data should pass validation"
    assert not result_invalid.valid, "Invalid data should fail validation"
    
    print(f"✓ Schema validation working")
    print(f"  Valid data: {result_valid.valid}")
    print(f"  Invalid data: {not result_invalid.valid} (correctly rejected)")


def test_lru_cache():
    """Test LRU cache functionality"""
    print("\nTesting LRU Cache...")
    
    from optimization import LRUCache
    
    cache = LRUCache(capacity=100)
    
    cache.set("key1", "value1")
    cache.set("key2", "value2")
    
    assert cache.get("key1") == "value1"
    assert cache.get("key2") == "value2"
    
    stats = cache.stats()
    assert stats["hits"] == 2
    
    print(f"✓ LRU Cache working")
    print(f"  Hit rate: {stats['hit_rate'] * 100:.1f}%")
    print(f"  Size: {stats['size']}/{stats['capacity']}")


def test_backend_selector():
    """Test backend selection"""
    print("\nTesting Backend Selector...")
    
    from optimization import BackendSelector
    
    selector = BackendSelector()
    best_backend = selector.get_best_backend()
    capabilities = selector.get_capabilities()
    
    print(f"✓ Backend Selector working")
    print(f"  Selected backend: {best_backend.value}")
    print(f"  Available backends: {', '.join(capabilities['available_backends'])}")
    print(f"  Platform: {capabilities['platform']}")


def test_batched_processor():
    """Test batched processor"""
    print("\nTesting Batched Processor...")
    
    from optimization import BatchedProcessor
    
    def process_batch(items):
        return [x * 2 for x in items]
    
    processor = BatchedProcessor(
        process_batch,
        batch_size=10,
        flush_interval=0.01
    )
    
    result = processor.submit(5)
    assert result == 10
    
    stats = processor.stats()
    
    print(f"✓ Batched Processor working")
    print(f"  Processed: {stats['processed_count']} items")
    print(f"  Batches: {stats['batch_count']}")
    
    processor.stop()


def main():
    """Run all tests"""
    print("="*80)
    print("APISTD OPTIMIZATION MODULE - INITIALIZATION TEST")
    print("="*80)
    
    try:
        test_imports()
        test_fast_json()
        test_memory_arena()
        test_zero_copy_buffer()
        test_schema_validation()
        test_lru_cache()
        test_backend_selector()
        test_batched_processor()
        
        print("\n" + "="*80)
        print("ALL TESTS PASSED ✓")
        print("="*80)
        
        return True
        
    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
