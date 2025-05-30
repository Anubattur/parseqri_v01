import React, { useState } from 'react';
import { authService } from '../services/api';

const LoginTest: React.FC = () => {
  const [username, setUsername] = useState('sona123');
  const [password, setPassword] = useState('sonadas@123');
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async () => {
    setIsLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await authService.login(username, password);
      setResult({
        success: true,
        tokens: {
          access: response.access?.substring(0, 15) + '...',
          refresh: response.refresh?.substring(0, 15) + '...',
        },
        localStorage: {
          token: localStorage.getItem('token')?.substring(0, 15) + '...',
          refresh_token: localStorage.getItem('refresh_token')?.substring(0, 15) + '...',
          username: localStorage.getItem('username'),
        }
      });
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'An error occurred during login');
      setResult({
        success: false,
        error: err.response?.data || err.message,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-lg mx-auto bg-white rounded-lg shadow-md mt-10">
      <h2 className="text-2xl font-bold mb-4">Login Test</h2>
      
      <div className="mb-4">
        <label className="block text-gray-700 mb-2">Username:</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
      </div>
      
      <div className="mb-4">
        <label className="block text-gray-700 mb-2">Password:</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
      </div>
      
      <button
        onClick={handleLogin}
        disabled={isLoading}
        className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
      >
        {isLoading ? 'Loading...' : 'Test Login'}
      </button>
      
      {error && (
        <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
        </div>
      )}
      
      {result && (
        <div className="mt-4">
          <h3 className="font-bold text-lg">{result.success ? 'Login Successful!' : 'Login Failed'}</h3>
          <pre className="mt-2 p-3 bg-gray-100 rounded overflow-auto text-sm">
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default LoginTest; 