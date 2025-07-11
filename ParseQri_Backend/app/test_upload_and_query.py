import requests
import json
import os

# Test API with file upload and query
base_url = "http://localhost:8000"

# Login with the test user
login_data = {
    "username_or_email": "testuser",
    "password": "testpassword123"
}

try:
    print("Logging in...")
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"Login response: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print(f"Login successful")
        
        access_token = token_data["access"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        # Create a default database configuration
        print("\nCreating default database configuration...")
        response = requests.post(f"{base_url}/db/default-config", headers=headers)
        print(f"Default config response: {response.status_code}")
        
        if response.status_code == 200:
            db_config = response.json()
            print(f"Database config created: {db_config}")
            db_id = db_config["id"]
            
            # Upload a CSV file
            csv_file_path = "../ParseQri_Agent/data/sample_data/test_data.csv"
            
            if os.path.exists(csv_file_path):
                print(f"\nUploading CSV file: {csv_file_path}")
                
                with open(csv_file_path, 'rb') as f:
                    files = {'file': f}
                    
                    response = requests.post(f"{base_url}/data/upload/{db_id}", files=files, headers=headers)
                    print(f"Upload response: {response.status_code}")
                    print(f"Upload result: {response.text}")
                    
                    if response.status_code == 200:
                        # Now test a query on the uploaded data
                        query_data = {
                            "query": "Show me all data from test_data table",
                            "user_id": "testuser",
                            "visualization": False
                        }
                        
                        print("\nTesting text-to-sql endpoint with uploaded data...")
                        response = requests.post(f"{base_url}/api/text-to-sql", json=query_data, headers=headers)
                        print(f"Text-to-SQL response: {response.status_code}")
                        print(f"Response: {response.text}")
                    else:
                        print("Upload failed, skipping query test")
            else:
                print(f"CSV file not found: {csv_file_path}")
                
                # Try a simple query anyway
                query_data = {
                    "query": "Show me available tables",
                    "user_id": "testuser", 
                    "visualization": False
                }
                
                print("\nTesting text-to-sql endpoint...")
                response = requests.post(f"{base_url}/api/text-to-sql", json=query_data, headers=headers)
                print(f"Text-to-SQL response: {response.status_code}")
                print(f"Response: {response.text}")
        else:
            print(f"Failed to create database config: {response.text}")
        
    else:
        print(f"Login failed: {response.text}")
        
except Exception as e:
    print(f"Error: {e}") 