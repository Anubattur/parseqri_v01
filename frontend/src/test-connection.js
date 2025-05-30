// Test connection to backend API
import axios from 'axios';

const API_URL = 'http://localhost:8000';

async function testConnection() {
  try {
    // Test the root endpoint
    const rootResponse = await axios.get(API_URL);
    console.log('Root endpoint response:', rootResponse.data);

    // Test the auth token verification endpoint
    try {
      const tokenResponse = await axios.post(`${API_URL}/auth/token/verify/`, {
        token: 'test-token'  // Send token in correct format as an object with token field
      });
      console.log('Token verification response:', tokenResponse.data);
    } catch (tokenError) {
      console.log('Expected token verification error (with invalid token):', tokenError.response?.status, tokenError.response?.data);
    }

    console.log('Connection test completed successfully!');
  } catch (error) {
    console.error('Connection test failed:', error.message);
    if (error.response) {
      console.error('Response status:', error.response.status);
      console.error('Response data:', error.response.data);
    }
  }
}

testConnection();

// Run this script with: node src/test-connection.js 