import React, { useState, useEffect } from 'react';
import { testConnection } from '../services/api';

const TestConnection: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState<string>('Testing connection...');

  useEffect(() => {
    const checkConnection = async () => {
      try {
        const result = await testConnection();
        if (result.success) {
          setStatus('success');
          setMessage(`Connected to API: ${JSON.stringify(result.data)}`);
        } else {
          setStatus('error');
          setMessage(`Connection failed: ${result.error}`);
        }
      } catch (error: any) {
        setStatus('error');
        setMessage(`Connection error: ${error.message}`);
      }
    };

    checkConnection();
  }, []);

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>API Connection Test</h2>
      {status === 'loading' && <p>Testing connection...</p>}
      {status === 'success' && (
        <div style={{ padding: '10px', backgroundColor: '#e6ffe6', borderRadius: '5px' }}>
          <p>✅ Connection successful!</p>
          <pre>{message}</pre>
        </div>
      )}
      {status === 'error' && (
        <div style={{ padding: '10px', backgroundColor: '#ffe6e6', borderRadius: '5px' }}>
          <p>❌ Connection failed!</p>
          <pre>{message}</pre>
        </div>
      )}
    </div>
  );
};

export default TestConnection; 