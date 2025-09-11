#!/usr/bin/env python3
"""
Database migration script to create analytics tables.

This script creates the analytics tables in the database.
Run this script after adding the analytics models to ensure the tables are created.

Usage:
    python create_analytics_tables.py
"""

import sys
import os
from pathlib import Path

# Add the backend src directory to the Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

from db.database import engine, Base
from db.models import db_analytics  # Import to register models with Base

def create_analytics_tables():
    """Create analytics tables in the database."""
    try:
        print("Creating analytics tables...")
        
        # Create only the analytics tables
        # This will create tables for all models that inherit from Base
        # but only if they don't already exist
        Base.metadata.create_all(bind=engine)
        
        print("✓ Analytics tables created successfully!")
        
        # List the analytics tables that should have been created
        analytics_tables = [
            "user_behavior_data",
            "learning_patterns", 
            "user_learning_profiles",
            "engagement_metrics"
        ]
        
        print("\nAnalytics tables:")
        for table in analytics_tables:
            print(f"  - {table}")
            
    except Exception as e:
        print(f"✗ Error creating analytics tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_analytics_tables()