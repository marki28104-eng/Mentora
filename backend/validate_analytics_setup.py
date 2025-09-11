#!/usr/bin/env python3
"""
Validation script to check if the advanced analytics setup is complete and correct.
"""

import os
import sys
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report the result."""
    if os.path.exists(file_path):
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (MISSING)")
        return False

def check_requirements():
    """Check if requirements.txt contains necessary ML packages."""
    print("\nChecking requirements.txt...")
    
    required_packages = [
        'scikit-learn',
        'numpy',
        'pandas',
        'scipy',
        'httpx',
        'joblib'
    ]
    
    try:
        with open('requirements.txt', 'r') as f:
            content = f.read().lower()
        
        missing_packages = []
        for package in required_packages:
            if package.lower() in content:
                print(f"✓ {package} found in requirements.txt")
            else:
                print(f"✗ {package} missing from requirements.txt")
                missing_packages.append(package)
        
        return len(missing_packages) == 0
        
    except FileNotFoundError:
        print("✗ requirements.txt not found")
        return False

def check_docker_setup():
    """Check Docker configuration."""
    print("\nChecking Docker setup...")
    
    files_to_check = [
        ('Dockerfile', 'Main Dockerfile'),
        ('docker-compose.analytics.yml', 'Analytics Docker Compose override'),
        ('.env', 'Analytics environment template')
    ]
    
    all_present = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_present = False
    
    # Check Dockerfile content for ML dependencies
    try:
        with open('Dockerfile', 'r') as f:
            dockerfile_content = f.read()
        
        if 'libgomp1' in dockerfile_content and 'libopenblas-dev' in dockerfile_content:
            print("✓ Dockerfile contains ML runtime dependencies")
        else:
            print("✗ Dockerfile missing ML runtime dependencies")
            all_present = False
            
        if 'gcc' in dockerfile_content and 'g++' in dockerfile_content:
            print("✓ Dockerfile contains ML build dependencies")
        else:
            print("✗ Dockerfile missing ML build dependencies")
            all_present = False
            
    except FileNotFoundError:
        print("✗ Cannot check Dockerfile content")
        all_present = False
    
    return all_present

def check_source_files():
    """Check if all source files are present."""
    print("\nChecking source files...")
    
    files_to_check = [
        ('src/services/advanced_analytics_service.py', 'Advanced Analytics Service'),
        ('src/api/routers/advanced_analytics.py', 'Advanced Analytics API Router'),
        ('src/api/schemas/analytics.py', 'Analytics Schemas'),
        ('src/config/settings.py', 'Configuration Settings'),
        ('test/test_advanced_analytics_service.py', 'Service Tests'),
        ('test/test_advanced_analytics_api.py', 'API Tests')
    ]
    
    all_present = True
    for file_path, description in files_to_check:
        if not check_file_exists(file_path, description):
            all_present = False
    
    return all_present

def check_configuration():
    """Check configuration settings."""
    print("\nChecking configuration...")
    
    try:
        # Add src to path to import settings
        sys.path.insert(0, 'src')
        from config.settings import (
            ANALYTICS_MIN_DATA_POINTS_FOR_TRAINING,
            ANALYTICS_ENABLE_REAL_TIME_PERSONALIZATION,
            ANALYTICS_ENABLE_PREDICTIVE_MODELS,
            ANALYTICS_ENABLE_COHORT_ANALYSIS
        )
        
        print("✓ Analytics configuration variables are defined")
        print(f"  - Min data points for training: {ANALYTICS_MIN_DATA_POINTS_FOR_TRAINING}")
        print(f"  - Real-time personalization: {ANALYTICS_ENABLE_REAL_TIME_PERSONALIZATION}")
        print(f"  - Predictive models: {ANALYTICS_ENABLE_PREDICTIVE_MODELS}")
        print(f"  - Cohort analysis: {ANALYTICS_ENABLE_COHORT_ANALYSIS}")
        
        return True
        
    except ImportError as e:
        print(f"✗ Cannot import analytics configuration: {e}")
        return False

def check_test_files():
    """Check if test files are present and valid."""
    print("\nChecking test files...")
    
    test_files = [
        'test_ml_dependencies.py',
        'test_docker_build.sh'
    ]
    
    all_present = True
    for test_file in test_files:
        if not check_file_exists(test_file, f'Test file: {test_file}'):
            all_present = False
    
    return all_present

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("Advanced Analytics Setup Validation")
    print("=" * 60)
    
    checks = [
        ("Requirements", check_requirements),
        ("Docker Setup", check_docker_setup),
        ("Source Files", check_source_files),
        ("Configuration", check_configuration),
        ("Test Files", check_test_files)
    ]
    
    all_passed = True
    results = {}
    
    for check_name, check_function in checks:
        try:
            result = check_function()
            results[check_name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"✗ Error running {check_name} check: {e}")
            results[check_name] = False
            all_passed = False
    
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for check_name, result in results.items():
        status = "PASS" if result else "FAIL"
        icon = "✓" if result else "✗"
        print(f"{icon} {check_name}: {status}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("✓ ALL CHECKS PASSED!")
        print("The advanced analytics setup is complete and ready for Docker deployment.")
        print("\nNext steps:")
        print("1. Copy .env.analytics.example to .env and configure your values")
        print("2. Run: docker-compose -f docker-compose.yml -f docker-compose.analytics.yml up --build")
        print("3. Test the setup with: ./test_docker_build.sh")
        return 0
    else:
        print("✗ SOME CHECKS FAILED!")
        print("Please fix the issues above before deploying to Docker.")
        return 1

if __name__ == "__main__":
    sys.exit(main())