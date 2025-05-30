import requests
import json

# Test that the token verification endpoint can handle both formats
def test_token_verification():
    base_url = "http://localhost:8000"
    
    # Test with object format { token: "test-token" }
    print("Testing with object format...")
    try:
        response = requests.post(
            f"{base_url}/auth/token/verify/",
            json={"token": "test-token"}
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    # Test with direct string format "test-token"
    print("\nTesting with direct string format...")
    try:
        response = requests.post(
            f"{base_url}/auth/token/verify/",
            json="test-token"
        )
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_token_verification() 