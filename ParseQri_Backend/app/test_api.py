import requests
import json

# Test API registration and login
base_url = "http://localhost:8000"

# Register a test user
register_data = {
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpassword123"
}

try:
    print("Registering test user...")
    response = requests.post(f"{base_url}/auth/register", json=register_data)
    print(f"Registration response: {response.status_code}")
    if response.status_code == 200:
        print(f"User registered: {response.json()}")
    else:
        print(f"Registration failed: {response.text}")
        
    # Login with the test user
    login_data = {
        "username_or_email": "testuser",
        "password": "testpassword123"
    }
    
    print("\nLogging in...")
    response = requests.post(f"{base_url}/auth/login", json=login_data)
    print(f"Login response: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        print(f"Login successful: {token_data}")
        
        # Test the text-to-sql endpoint
        access_token = token_data["access"]
        headers = {"Authorization": f"Bearer {access_token}"}
        
        query_data = {
            "query": "Show me all data",
            "user_id": "testuser",
            "visualization": False
        }
        
        print("\nTesting text-to-sql endpoint...")
        response = requests.post(f"{base_url}/api/text-to-sql", json=query_data, headers=headers)
        print(f"Text-to-SQL response: {response.status_code}")
        print(f"Response: {response.text}")
        
    else:
        print(f"Login failed: {response.text}")
        
except Exception as e:
    print(f"Error: {e}") 