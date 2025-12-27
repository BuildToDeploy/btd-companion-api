#!/usr/bin/env python3
"""
Database migration runner for BTD Companion
Executes SQL migration scripts in order
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import get_settings


def run_migrations():
    """Run all migration scripts in order"""
    settings = get_settings()
    
    # Parse DATABASE_URL
    db_url = settings.database_url
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("[Migration] Connected to database")
        
        # Get migration scripts directory
        scripts_dir = Path(__file__).parent
        
        # Find and run migration scripts in order
        migration_files = sorted([f for f in scripts_dir.glob("*.sql")])
        
        for migration_file in migration_files:
            print(f"[Migration] Running {migration_file.name}...")
            
            with open(migration_file, 'r') as f:
                sql = f.read()
            
            try:
                cursor.execute(sql)
                print(f"[Migration] ✓ {migration_file.name} completed")
            except Exception as e:
                print(f"[Migration] ✗ {migration_file.name} failed: {str(e)}")
                # Continue with other migrations
        
        cursor.close()
        conn.close()
        print("[Migration] All migrations completed!")
        
    except Exception as e:
        print(f"[Migration] Connection error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()
