#!/bin/bash
set -e

echo "Cleaning local build..."
rm -rf build
mkdir -p build

echo "Running CMake..."
cmake -B build -S .

echo "Building project..."
cmake --build build

echo "Done! You can run it with: ./build/pricer"
