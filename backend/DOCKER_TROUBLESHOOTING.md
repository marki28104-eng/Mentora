# Docker Build Troubleshooting Guide

## Common Issues and Solutions

### 1. Package Not Available Error

**Error:**
```
Package libatlas-base-dev is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source
```

**Solution:**
This occurs when using newer Debian versions where package names have changed. The Dockerfile has been updated to use the correct packages:

- ❌ `libatlas-base-dev` (obsolete)
- ✅ `libopenblas-dev` (current)

**Fixed in:** The main Dockerfile now uses `libopenblas-dev` instead of `libatlas-base-dev`.

### 2. ML Package Build Failures

**Error:**
```
Failed building wheel for numpy/scipy/scikit-learn
```

**Solution:**
Ensure all build dependencies are installed:

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc6-dev \
    libffi-dev \
    libssl-dev \
    gfortran \
    && rm -rf /var/lib/apt/lists/*
```

### 3. Runtime Import Errors

**Error:**
```
ImportError: libopenblas.so.0: cannot open shared object file
```

**Solution:**
Ensure runtime dependencies are installed in the final stage:

```dockerfile
RUN apt-get install -y --no-install-recommends \
    libgomp1 \
    libopenblas-dev \
    liblapack-dev \
    libblas-dev \
    gfortran
```

### 4. Memory Issues During Build

**Error:**
```
Killed (out of memory)
```

**Solution:**
Increase Docker memory limits or use multi-stage builds:

```bash
# Increase Docker Desktop memory to 4GB+
# Or use build args to limit parallel jobs
docker build --build-arg MAKEFLAGS="-j1" .
```

## Testing Your Build

### Quick ML Test

Use the simplified test Dockerfile:

```bash
# Build and test ML dependencies only
docker build -f Dockerfile.ml-test -t ml-test .
docker run --rm ml-test
```

### Full Application Test

```bash
# Build full application
docker build -t app-test .

# Test ML imports
docker run --rm app-test python -c "
import numpy as np
import pandas as pd
import sklearn
print('✓ All ML packages working')
"
```

### Automated Testing

Run the comprehensive test script:

```bash
./test_docker_build.sh
```

## Platform-Specific Issues

### Apple Silicon (M1/M2)

If building on Apple Silicon, you might need to specify the platform:

```bash
docker build --platform linux/amd64 -t your-app .
```

Or use multi-platform builds:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t your-app .
```

### ARM64 vs AMD64

The current Dockerfile works on both architectures, but package availability might vary:

- **ARM64**: All packages available in Debian Trixie
- **AMD64**: All packages available in Debian Trixie

## Debugging Steps

### 1. Check Package Availability

```bash
# Start a container with the base image
docker run -it python:3.10-slim bash

# Update package lists
apt-get update

# Search for packages
apt-cache search openblas
apt-cache search atlas
```

### 2. Test Individual Packages

```bash
# Test each ML package individually
docker run --rm python:3.10-slim bash -c "
apt-get update && 
apt-get install -y gcc g++ libopenblas-dev && 
pip install numpy && 
python -c 'import numpy; print(numpy.__version__)'
"
```

### 3. Check Build Logs

Enable verbose output:

```bash
docker build --progress=plain --no-cache .
```

## Alternative Solutions

### Use Pre-built Images

Consider using images with ML packages pre-installed:

```dockerfile
FROM jupyter/scipy-notebook:latest
# Your application code here
```

### Use Conda

Alternative package manager that handles system dependencies:

```dockerfile
FROM continuumio/miniconda3
COPY environment.yml .
RUN conda env create -f environment.yml
```

### Use pip with pre-compiled wheels

Ensure you're using wheels instead of building from source:

```dockerfile
RUN pip install --only-binary=all numpy pandas scikit-learn
```

## Getting Help

If you continue to have issues:

1. Check the Docker build logs carefully
2. Verify your Docker version and available memory
3. Test with the simplified `Dockerfile.ml-test`
4. Check if the issue is platform-specific
5. Consider using alternative base images

## Verification Commands

After successful build, verify everything works:

```bash
# Test ML imports
docker run --rm your-image python -c "
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
print('✓ All ML packages imported successfully')
"

# Test analytics service imports (if applicable)
docker run --rm your-image python -c "
import sys
sys.path.append('/path/to/your/app')
# Add your specific import tests here
"
```