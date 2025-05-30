// Test login functionality
import axios from 'axios';

const API_URL = 'http://localhost:8000';

async function testLogin() {
  try {
    console.log('Testing login with sona123/sonadas@123...');
    
    // Attempt login
    const loginResponse = await axios.post(`${API_URL}/auth/login`, {
      username_or_email: 'sona123',
      password: 'sonadas@123'
    });
    
    console.log('Login successful!');
    console.log('Access token:', loginResponse.data.access.substring(0, 15) + '...');
    console.log('Refresh token:', loginResponse.data.refresh.substring(0, 15) + '...');
    
    // Test token verification
    const token = loginResponse.data.access;
    try {
      const verifyResponse = await axios.post(`${API_URL}/auth/token/verify/`, {
        token: token
      });
      console.log('Token verification successful:', verifyResponse.data);
    } catch (verifyError) {
      console.error('Token verification failed:', verifyError.response?.status, verifyError.response?.data);
    }
    
    // Test token refresh
    const refreshToken = loginResponse.data.refresh;
    try {
      const refreshResponse = await axios.post(`${API_URL}/auth/token/refresh/`, {
        refresh: refreshToken
      });
      console.log('Token refresh successful!');
      console.log('New access token:', refreshResponse.data.access.substring(0, 15) + '...');
    } catch (refreshError) {
      console.error('Token refresh failed:', refreshError.response?.status, refreshError.response?.data);
    }
    
  } catch (error) {
    console.error('Login failed:', error.message);
    if (error.response) {
      console.error('Status:', error.response.status);
      console.error('Data:', error.response.data);
    }
  }
}

testLogin();

// Run this script with: node src/test-login.js 