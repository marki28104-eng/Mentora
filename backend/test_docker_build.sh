#!/bin/bash

# Test script to verify Docker build works with ML dependencies

set -e

echo "Testing Docker build for advanced analytics..."

# Test 1: Build and test ML dependencies with simplified Dockerfile
echo "Building ML test Docker image..."
docker build -f Dockerfile.ml-test -t mentora-ml-test .

echo "Testing ML dependencies in Docker container..."
docker run --rm mentora-ml-test

# Test 2: Build the full application Docker image
echo "Building full application Docker image..."
docker build -t mentora-backend-analytics-test .

echo "Testing that the application can import analytics modules..."
docker run --rm mentora-backend-analytics-test python -c "
import sys
sys.path.append('/home/app/web/app')
try:
    print('Testing basic imports...')
    import numpy as np
    import pandas as pd
    import sklearn
    print('✓ All ML packages imported successfully in full Docker image')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"

echo "Docker build test completed successfully!"

# Cleanup
echo "Cleaning up test images..."
docker rmi mentora-ml-test || true
docker rmi mentora-backend-analytics-test || true