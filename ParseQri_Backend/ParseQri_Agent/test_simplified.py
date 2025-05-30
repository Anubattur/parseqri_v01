#!/usr/bin/env python3
"""
Test script to verify that the integration between conversion_tool and TextToSQL_Agent works
using the simplified_query.py script.
"""
import os
import sys
import subprocess
import time
from pathlib import Path
import sqlite3
import pandas as pd

# Define paths
ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = ROOT_DIR / "data" / "input"
CSV_OUTPUT_DIR = ROOT_DIR / "data" / "csv_output"
DB_STORAGE_DIR = ROOT_DIR / "data" / "db_storage"
TEXTSQL_AGENT_DIR = ROOT_DIR / "TextToSQL_Agent"

def setup_test_environment():
    """Set up directories and create a sample test file"""
    # Create directories
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DB_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create a test CSV file directly in data/input
    # (Bypassing PDF parsing for testing purposes)
    test_csv_path = INPUT_DIR / "test_data.csv"
    
    # Create sample data for testing
    sample_data = pd.DataFrame({
        'product_id': range(1, 11),
        'product_name': [f'Product {i}' for i in range(1, 11)],
        'price': [10.5 + i for i in range(10)],
        'quantity': [i * 5 for i in range(1, 11)],
        'category': ['Electronics', 'Clothing', 'Food', 'Electronics', 'Toys', 
                     'Food', 'Clothing', 'Toys', 'Electronics', 'Food']
    })
    
    # Write the test CSV
    sample_data.to_csv(test_csv_path, index=False)
    print(f"Created test file: {test_csv_path}")
    
    return test_csv_path

def run_processing():
    """Run the simplified_query.py processing"""
    print("\nRunning simplified_query.py process...")
    
    python_executable = sys.executable
    
    result = subprocess.run(
        [python_executable, "simplified_query.py", "process"],
        cwd=str(TEXTSQL_AGENT_DIR),
        capture_output=True,
        text=True
    )
    
    print("\nProcessing output:")
    print(result.stdout)
    
    if result.returncode != 0:
        print("Error in processing:")
        print(result.stderr)
        return False
    
    return True

def verify_outputs():
    """Verify that the processing created the expected outputs"""
    # Check if CSV file was copied to csv_output directory
    expected_csv = CSV_OUTPUT_DIR / "test_data.csv"
    if not expected_csv.exists():
        print(f"ERROR: Expected CSV file not found: {expected_csv}")
        return False
    
    # Check if the database was created
    db_file = DB_STORAGE_DIR / "query_data.db"
    if not db_file.exists():
        print(f"ERROR: Database file not found: {db_file}")
        return False
    
    # Verify database contents
    try:
        conn = sqlite3.connect(str(db_file))
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
        print("\nDatabase tables:")
        print(tables)
        
        if "test_data" not in tables['name'].values:
            print("ERROR: Expected 'test_data' table not found in database")
            return False
        
        # Check table contents
        data = pd.read_sql("SELECT * FROM test_data LIMIT 5", conn)
        print("\nSample data from database:")
        print(data)
        
        conn.close()
    except Exception as e:
        print(f"ERROR: Failed to verify database: {e}")
        return False
    
    print("\nVerification PASSED: CSV and database were created successfully")
    return True

def run_test_query():
    """Run a test query against the database"""
    print("\nRunning test query...")
    
    query = "SELECT category, AVG(price) as avg_price FROM test_data GROUP BY category"
    
    python_executable = sys.executable
    
    result = subprocess.run(
        [python_executable, "simplified_query.py", query],
        cwd=str(TEXTSQL_AGENT_DIR),
        capture_output=True,
        text=True
    )
    
    print("\nQuery result:")
    print(result.stdout)
    
    if result.returncode != 0:
        print("Error running query:")
        print(result.stderr)
        return False
    
    return True

def clean_up():
    """Clean up the test files"""
    test_file = INPUT_DIR / "test_data.csv"
    if test_file.exists():
        test_file.unlink()
        print(f"Removed test file: {test_file}")

def main():
    """Main test function"""
    print("=== TESTING INTEGRATION WITH SIMPLIFIED QUERY SYSTEM ===")
    
    try:
        # Setup test environment with sample file
        test_file = setup_test_environment()
        
        # Run the processing
        if not run_processing():
            print("\nTest FAILED: Processing step failed")
            return
        
        # Verify outputs
        if not verify_outputs():
            print("\nTest FAILED: Verification step failed")
            return
        
        # Run a test query
        if not run_test_query():
            print("\nTest FAILED: Test query failed")
            return
        
        print("\n=== TEST PASSED: Integration with simplified system is working correctly ===")
        
    except Exception as e:
        print(f"\nTest FAILED with error: {str(e)}")
    
    finally:
        # Clean up test files
        clean_up()

if __name__ == "__main__":
    main() 