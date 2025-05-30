import requests
import json

# Test that the token refresh endpoint can handle both formats
def test_token_refresh():
    base_url = "http://localhost:8000"
    
    # First, login to get a refresh token
    print("Logging in to get refresh token...")
    try:
        login_response = requests.post(
            f"{base_url}/auth/login",
            json={"username_or_email": "sona123", "password": "sonadas@123"}
        )
        print(f"Login status code: {login_response.status_code}")
        
        if login_response.status_code == 200:
            refresh_token = login_response.json().get("refresh")
            print(f"Got refresh token: {refresh_token[:10]}...")
            
            # Test with object format { refresh: "token" }
            print("\nTesting token refresh with object format...")
            try:
                response = requests.post(
                    f"{base_url}/auth/token/refresh/",
                    json={"refresh": refresh_token}
                )
                print(f"Status code: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except Exception as e:
                print(f"Error: {str(e)}")
            
            # Test with direct string format "token"
            print("\nTesting token refresh with direct string format...")
            try:
                response = requests.post(
                    f"{base_url}/auth/token/refresh/",
                    json=refresh_token
                )
                print(f"Status code: {response.status_code}")
                print(f"Response: {json.dumps(response.json(), indent=2)}")
            except Exception as e:
                print(f"Error: {str(e)}")
        else:
            print(f"Login failed: {login_response.text}")
    except Exception as e:
        print(f"Error during login: {str(e)}")

if __name__ == "__main__":
    test_token_refresh() 