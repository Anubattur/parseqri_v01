#!/usr/bin/env python3
"""
Test script for the extract_metadata endpoint
"""

import asyncio
import traceback
import sys
import httpx
import json

async def test_extract_metadata_endpoint():
    """Test the extract_metadata endpoint"""
    try:
        print("Testing extract_metadata endpoint...")
        
        # First, login to get a token
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            # Login
            try:
                login_data = {
                    "username_or_email": "testuser",  # Replace with a valid username or email
                    "password": "password123"  # Replace with a valid password
                }
                
                print("Logging in...")
                login_response = await client.post("/auth/login", json=login_data)
                login_response.raise_for_status()
                
                token_data = login_response.json()
                token = token_data.get("access_token")
                
                if not token:
                    print("No token in response")
                    return False
                    
                print("Got authentication token")
                
                # Get database configurations
                headers = {"Authorization": f"Bearer {token}"}
                
                print("Getting database configurations...")
                db_response = await client.get("/db/config", headers=headers)
                db_response.raise_for_status()
                
                db_configs = db_response.json().get("data", [])
                if not db_configs:
                    print("No database configurations found")
                    return False
                    
                print(f"Found {len(db_configs)} database configurations")
                
                # Use the first database configuration
                db_id = db_configs[0].get("id")
                print(f"Using database ID: {db_id}")
                
                # Test extract metadata endpoint
                print(f"Making POST request to /db/extract-metadata/{db_id}")
                extract_response = await client.post(
                    f"/db/extract-metadata/{db_id}",
                    headers=headers
                )
                
                # Log response status
                print(f"Response status: {extract_response.status_code}")
                
                # Log response content
                try:
                    response_json = extract_response.json()
                    print(f"Response JSON: {json.dumps(response_json, indent=2)}")
                    
                    # Check for success
                    if response_json.get("success") or response_json.get("status") == "success":
                        print("Extract metadata succeeded")
                        return True
                    else:
                        print("Extract metadata failed")
                        print(f"Error: {response_json.get('message')}")
                        return False
                        
                except Exception as e:
                    print(f"Failed to parse JSON: {e}")
                    print(f"Response text: {extract_response.text}")
                    return False
                    
            except httpx.HTTPStatusError as e:
                print(f"HTTP error: {e.response.status_code} - {e.response.text}")
                return False
                
            except Exception as e:
                print(f"Request error: {e}")
                return False
    except Exception as e:
        print(f"Error during test: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(test_extract_metadata_endpoint())
        print(f"Test {'succeeded' if success else 'failed'}")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        sys.exit(1) 