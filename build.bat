@echo off
REM Build script for Rust backend on Windows

echo Building Rust backend...

cd optimization / backend / rust_backend

REM Build release version
cargo build --release

REM Copy the compiled library
copy target\release\rust_backend.dll ..\..\rust_backend.pyd
echo.
echo ✅ Windows library built: rust_backend.pyd
echo.
echo ✅ Build complete!

cd ..\..\..
