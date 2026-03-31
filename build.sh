#!/bin/bash
# Build script for Rust backend on Linux/macOS

set -e

echo "Building Rust backend..."

cd optimization/backend/rust_backend

# Build release version
cargo build --release

# Copy the compiled library
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    cp target/release/librust_backend.dylib ../../rust_backend_lib.so
    echo "✅ macOS library built: rust_backend_lib.so"
else
    # Linux
    cp target/release/librust_backend.so ../../rust_backend_lib.so
    echo "✅ Linux library built: rust_backend_lib.so"
fi

echo "✅ Build complete!"
