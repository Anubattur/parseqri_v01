#!/usr/bin/env python3
"""
Test script to verify that the integration between conversion_tool and TextToSQL_Agent works.
This script will:
1. Create a sample test file in data/input
2. Run the TextToSQL_Agent main.py to process it
3. Verify the CSV output and database creation
4. Run a test query
"""
import os
import sys
import subprocess
import time
import asyncio
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

def check_agent_version():
    """Check which TextToSQL_Agent version is available"""
    # Check if new agent structure exists
    if (TEXTSQL_AGENT_DIR / "api.py").exists():
        return "new"
    # Check if old agent structure exists
    elif (TEXTSQL_AGENT_DIR / "main.py").exists():
        return "old"
    else:
        return "none"

def run_processing():
    """Run the TextToSQL_Agent processing"""
    print("\nRunning TextToSQL_Agent processing...")
    
    agent_version = check_agent_version()
    
    if agent_version == "new":
        # Create a simple test script for the new agent structure
        test_script_path = TEXTSQL_AGENT_DIR / "test_process.py"
        with open(test_script_path, 'w') as f:
            f.write("""
import asyncio
import sys
from pathlib import Path
from core import TextToSQLPipeline
from models.data_models import PipelineRequest

async def process_csv(csv_path):
    # Create pipeline
    async with TextToSQLPipeline() as pipeline:
        # Create request for processing CSV
        request = PipelineRequest(
            user_id="test_user",
            query=f"Import data from {Path(csv_path).name}",
            options={
                "csv_path": csv_path,
                "table_name": "test_data"
            }
        )
        
        # Mock auth token for local use
        auth_token = "local_development_token"
        
        # Process the request
        response = await pipeline.process(request, auth_token)
        
        # Print results
        if response.success:
            print(f"SUCCESS: Data imported")
            if response.natural_answer:
                print(response.natural_answer)
        else:
            print(f"ERROR: {response.error}")
            
        return response.success

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_process.py <csv_path>")
        sys.exit(1)
        
    csv_path = sys.argv[1]
    success = asyncio.run(process_csv(csv_path))
    sys.exit(0 if success else 1)
""")

        # Run the test script
        result = subprocess.run(
            [sys.executable, "test_process.py", str(INPUT_DIR / "test_data.csv")],
            cwd=str(TEXTSQL_AGENT_DIR),
            capture_output=True,
            text=True
        )
        
        # Clean up test script
        test_script_path.unlink(missing_ok=True)
    else:
        # Use old TextToSQL_Agent
        result = subprocess.run(
            [sys.executable, "main.py", "--upload", str(INPUT_DIR / "test_data.csv"), "--user", "test_user", "--table", "test_data"],
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
    
    agent_version = check_agent_version()
    
    if agent_version == "new":
        # New agent might store data differently, check both possible locations
        db_paths = [
            DB_STORAGE_DIR / "test_user" / "test_data.db",
            DB_STORAGE_DIR / "query_data.db",
            DB_STORAGE_DIR / "test_user.db"
        ]
        
        db_found = False
        for db_path in db_paths:
            if db_path.exists():
                db_found = True
                db_file = db_path
                break
                
        if not db_found:
            print(f"ERROR: Database file not found in any expected location")
            return False
    else:
        # Old agent stored data in a standard location
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
        
        # Check for either extracted_data or test_data table
        expected_tables = ["extracted_data", "test_data"]
        table_found = False
        table_name = None
        
        for table in expected_tables:
            if table in tables['name'].values:
                table_found = True
                table_name = table
                break
                
        if not table_found:
            print(f"ERROR: Expected table not found in database. Available tables: {tables['name'].values}")
            return False
        
        # Check table contents
        data = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5", conn)
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
    
    agent_version = check_agent_version()
    
    if agent_version == "new":
        # Create a simple test script for the new agent structure
        test_script_path = TEXTSQL_AGENT_DIR / "test_query.py"
        with open(test_script_path, 'w') as f:
            f.write("""
import asyncio
import sys
from core import TextToSQLPipeline
from models.data_models import PipelineRequest

async def run_query(query_text):
    # Create pipeline
    async with TextToSQLPipeline() as pipeline:
        # Create request
        request = PipelineRequest(
            user_id="test_user",
            query=query_text
        )
        
        # Mock auth token for local use
        auth_token = "local_development_token"
        
        # Process the request
        response = await pipeline.process(request, auth_token)
        
        # Print results
        if response.success:
            print(f"SQL Query: {response.sql_query}")
            print(f"Natural Answer: {response.natural_answer}")
        else:
            print(f"ERROR: {response.error}")
            
        return response.success

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_query.py <query_text>")
        sys.exit(1)
        
    query_text = sys.argv[1]
    success = asyncio.run(run_query(query_text))
    sys.exit(0 if success else 1)
""")

        # Run the test script
        query = "What is the average price by category?"
        result = subprocess.run(
            [sys.executable, "test_query.py", query],
            cwd=str(TEXTSQL_AGENT_DIR),
            capture_output=True,
            text=True
        )
        
        # Clean up test script
        test_script_path.unlink(missing_ok=True)
    else:
        # Use old TextToSQL_Agent
        query = "What is the average price by category?"
        result = subprocess.run(
            [sys.executable, "main.py", query, "--user", "test_user"],
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
    print("=== TESTING INTEGRATION BETWEEN CONVERSION_TOOL AND TEXTSQL_AGENT ===")
    
    try:
        # Check which agent version we're using
        agent_version = check_agent_version()
        if agent_version == "new":
            print("Using new TextToSQL_Agent implementation")
        elif agent_version == "old":
            print("Using original TextToSQL_Agent implementation")
        else:
            print("ERROR: TextToSQL_Agent not found!")
            return
        
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
        
        print("\n=== TEST PASSED: Integration is working correctly ===")
        
    except Exception as e:
        print(f"\nTest FAILED with error: {str(e)}")
    
    finally:
        # Clean up test files
        clean_up()

if __name__ == "__main__":
    main() 