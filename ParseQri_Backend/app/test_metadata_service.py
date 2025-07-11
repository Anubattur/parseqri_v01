#!/usr/bin/env python3
"""
Test script for metadata extraction service
"""

import asyncio
import traceback
import sys

# Add better error handling
try:
    from app.services.metadata_extraction import metadata_extraction_service
    from app.schemas.db import DBConfigOut, DBType
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this script from the ParseQri_Backend directory")
    print(f"Current Python path: {sys.path}")
    traceback.print_exc()
    sys.exit(1)

async def test_metadata_extraction():
    """Test the metadata extraction service"""
    try:
        print("Testing metadata extraction service...")
        print(f"Metadata extraction service: {metadata_extraction_service}")
        
        # Create a test database configuration
        config = DBConfigOut(
            id=1,
            user_id=1,
            host="localhost",
            port=3306,
            db_name="test_db",
            db_user="test_user",
            db_password="root",
            db_type=DBType.mysql
        )
        
        # Test the metadata extraction service
        print("Extracting metadata...")
        result = await metadata_extraction_service.extract_metadata(config, "1")
        
        # Print the result
        print(f"Status: {result['status']}")
        print(f"Message: {result['message']}")
        print(f"Extraction method: {result.get('extraction_method', 'unknown')}")
        
        # Print any errors
        if result["status"] == "error":
            print(f"Error: {result['message']}")
        
        return result["status"] == "success"
    except Exception as e:
        print(f"Error during test: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_metadata_extraction())
        print(f"Test {'succeeded' if success else 'failed'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1) 