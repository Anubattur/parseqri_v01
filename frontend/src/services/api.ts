import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Check if we're in development mode
const isDevelopment = window.location.hostname === 'localhost';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Add auth token to requests
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add a response interceptor to handle 401 Unauthorized errors
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // If the error is 401 Unauthorized and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to get a new token using the refresh token
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
          // No refresh token, redirect to login
          window.location.href = '/login';
          return Promise.reject(error);
        }
        
        // Skip refresh attempt if using admin bypass token
        if (refreshToken === 'admin-bypass-refresh-token') {
          // Manually set the Authorization header
          originalRequest.headers.Authorization = 'Bearer admin-bypass-token';
          return axios(originalRequest);
        }
        
        const response = await apiClient.post('/auth/token/refresh/', {
          refresh: refreshToken
        });
        
        if (response.data.access) {
          // Save the new access token
          localStorage.setItem('token', response.data.access);
          
          // Update the current request with the new token
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          
          // Retry the original request
          return axios(originalRequest);
        }
      } catch (refreshError) {
        // If refresh token also fails, redirect to login
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
      }
    }
    
    return Promise.reject(error);
  }
);

// Mock authentication for development when server is down
const useMockAuth = (error) => {
  console.warn('Backend server unreachable, using mock authentication:', error);
  return isDevelopment;
};

// Authentication services
export const authService = {
  register: async (username: string, email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/register', {
        username,
        email,
        password
      });
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock auth
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock registration service');
        return {
          id: 'mock-user-id',
          username,
          email,
          message: 'Mock registration successful'
        };
      }
      
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  },

  login: async (username_or_email: string, password: string) => {
    try {
      const response = await apiClient.post('/auth/login', {
        username_or_email,
        password
      });
      
      // For JWT standard response handling
      if (response.data.access && response.data.refresh) {
        // Store both tokens
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        return response.data;
      } else if (response.data.access_token) {
        // Fallback for non-standard response
        localStorage.setItem('token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        return response.data;
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error: any) {
      // If server is down and we're in development, use mock auth
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock login service');
        const mockToken = 'mock-jwt-token-' + Math.random().toString(36).substring(2);
        const mockRefreshToken = 'mock-refresh-token-' + Math.random().toString(36).substring(2);
        
        // Store mock tokens
        localStorage.setItem('token', mockToken);
        localStorage.setItem('refresh_token', mockRefreshToken);
        localStorage.setItem('isMockAuth', 'true');
        
        return {
          access: mockToken,
          refresh: mockRefreshToken,
          user: {
            id: 'mock-user-id',
            username: username_or_email
          }
        };
      }
      
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  },

  getCurrentUser: async () => {
    try {
      // Check if using mock auth
      if (localStorage.getItem('isMockAuth') === 'true') {
        return {
          id: 'mock-user-id',
          username: localStorage.getItem('username') || 'mock_user',
          email: 'mock@example.com'
        };
      }
      
      const response = await apiClient.get('/auth/me');
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock auth
      if (error.message === 'Network Error' && useMockAuth(error)) {
        return {
          id: 'mock-user-id',
          username: localStorage.getItem('username') || 'mock_user',
          email: 'mock@example.com'
        };
      }
      
      if (error.response?.status === 401) {
        // Token is invalid or expired
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        throw new Error('Session expired. Please login again.');
      }
      throw error;
    }
  },

  checkAuth: async () => {
    try {
      const token = localStorage.getItem('token');
      
      // Check if using mock auth
      if (localStorage.getItem('isMockAuth') === 'true') {
        return { isAuthenticated: true };
      }
      
      // Check if it's the admin bypass token
      if (token === 'admin-bypass-token') {
        return { isAuthenticated: true };
      }
      
      // No token available
      if (!token) {
        return { isAuthenticated: false };
      }
      
      // Regular token verification
      const response = await apiClient.post('/auth/token/verify/', { 
        token: token 
      });
      return { isAuthenticated: true };
    } catch (error) {
      // If server is down and we're in development, use mock auth
      if (error.message === 'Network Error' && useMockAuth(error)) {
        return { isAuthenticated: !!localStorage.getItem('token') };
      }
      
      return { isAuthenticated: false, error };
    }
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('username');
    localStorage.removeItem('isMockAuth');
    
    // Redirect to landing page
    window.location.href = '/';
  },
};

// SQL Generator services
export const sqlService = {
  generateSql: async (query: string, datasetId?: number) => {
    const response = await apiClient.post('/sql/generate/', { 
      query, 
      dataset_id: datasetId 
    });
    return response.data;
  },
  validateSql: async (sqlQuery: string) => {
    const response = await apiClient.post('/sql/validate/', { sql_query: sqlQuery });
    return response.data;
  },
  executeSql: async (sqlQuery: string, datasetId?: number, queryId?: number) => {
    const response = await apiClient.post('/sql/execute/', { 
      sql_query: sqlQuery,
      dataset_id: datasetId,
      query_id: queryId
    });
    return response.data;
  },
  // New TextSQL endpoint that combines generation, execution and visualization
  processTextSQL: async (query: string, datasetId?: number) => {
    const response = await apiClient.post('/sql/textsql/', { 
      query, 
      dataset_id: datasetId 
    });
    return response.data;
  },
};

// Visualizer services
export const visualizerService = {
  generateVisualization: async (queryId: number, chartType?: string) => {
    const response = await apiClient.post('/visualizer/generate/', { 
      query_id: queryId,
      chart_type: chartType 
    });
    return response.data;
  },
  getRecommendedChartType: async (data: any[]) => {
    const response = await apiClient.post('/visualizer/recommend-chart/', { data });
    return response.data;
  },
  exportData: async (queryId: number, format: 'csv' | 'json') => {
    const response = await apiClient.post('/visualizer/export/', { 
      query_id: queryId,
      format 
    }, {
      responseType: 'blob'
    });
    return response.data;
  },
};

// Dataset services
export const datasetService = {
  getDatasets: async () => {
    try {
      const response = await apiClient.get('/datasets/');
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock data
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock datasets');
        return [
          {
            id: 1,
            name: 'Sample Dataset 1',
            type: 'CSV',
            created_at: new Date().toISOString(),
            size: 1024,
            tables: 1,
            status: 'active'
          },
          {
            id: 2,
            name: 'Sample Dataset 2',
            type: 'CSV',
            created_at: new Date(Date.now() - 86400000).toISOString(),
            size: 2048,
            tables: 1,
            status: 'active'
          }
        ];
      }
      throw error;
    }
  },
  uploadDataset: async (formData: FormData) => {
    try {
      const response = await apiClient.post('/datasets/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock data
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock dataset upload');
        const fileName = formData.get('file') instanceof File ? (formData.get('file') as File).name : 'unknown.csv';
        return {
          id: Math.floor(Math.random() * 1000) + 3,
          name: fileName,
          type: 'CSV',
          created_at: new Date().toISOString(),
          size: Math.floor(Math.random() * 10000),
          tables: 1,
          status: 'active'
        };
      }
      throw error;
    }
  },
  uploadCsv: async (file: File, dbId: number) => {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await apiClient.post(`/data/upload/${dbId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock data
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock CSV upload');
        return {
          id: dbId || Math.floor(Math.random() * 1000) + 3,
          name: file.name,
          type: 'CSV',
          created_at: new Date().toISOString(),
          size: file.size,
          status: 'active'
        };
      }
      throw error;
    }
  },
  getDatasetDetails: async (datasetId: number) => {
    const response = await apiClient.get(`/datasets/${datasetId}/`);
    return response.data;
  },
  getDatasetData: async (datasetId: number, limit?: number, offset?: number) => {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());
    
    const response = await apiClient.get(`/datasets/${datasetId}/data?${params.toString()}`);
    return response.data;
  },
  getUserDatasets: async () => {
    const response = await apiClient.get('/user/datasets/');
    return response.data;
  },
  // Alternative endpoints to try
  getMyDatasets: async () => {
    const response = await apiClient.get('/datasets/mine/');
    return response.data;
  },
  getDatasets_v2: async () => {
    const response = await apiClient.get('/api/datasets/');
    return response.data;
  },
  getDatasetSchema: async (datasetId: number) => {
    const response = await apiClient.get(`/datasets/${datasetId}/schema`);
    return response.data;
  },
  getDatabaseTables: async (databaseId: number) => {
    const response = await apiClient.get(`/db/${databaseId}/tables`);
    return response.data;
  },
};

// API diagnostic function to check URLs and auth status
export const apiDiagnostic = {
  checkAPIStatus: async () => {
    try {
      // Check if server is available
      const response = await fetch(`${API_URL}/auth/token/verify/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          token: localStorage.getItem('token') || '' 
        })
      });
      return {
        serverAvailable: true,
        status: response.status,
        statusText: response.statusText
      };
    } catch (error) {
      return { 
        serverAvailable: false,
        error: error
      };
    }
  },
  checkToken: () => {
    const token = localStorage.getItem('token');
    const refreshToken = localStorage.getItem('refresh_token');
    return {
      hasToken: !!token,  
      hasRefreshToken: !!refreshToken,
      tokenInfo: token ? {
        length: token.length,
        firstChars: token.substring(0, 10) + '...',
        lastChars: '...' + token.substring(token.length - 10)
      } : null
    };
  }
};

// Database configuration services
export const dbService = {
  getConfigs: async () => {
    try {
      const response = await apiClient.get('/db/config');
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock data
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock database configs');
        return [
          {
            id: 1,
            db_type: 'mysql',
            host: 'localhost',
            port: 3306,
            db_name: 'mock_database',
            db_user: 'mock_user',
            created_at: new Date().toISOString()
          }
        ];
      }
      throw error;
    }
  },
  createConfig: async (config: {
    db_type: string;
    host: string;
    port: number;
    db_name: string;
    db_user: string;
    db_password: string;
  }) => {
    try {
      const response = await apiClient.post('/db/config', config);
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock data
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock database config creation');
        return {
          id: 1,
          ...config,
          db_password: '******', // Don't return actual password
          created_at: new Date().toISOString()
        };
      }
      throw error;
    }
  },
  createDefaultConfig: async () => {
    try {
      const response = await apiClient.post('/db/default-config');
      return response.data;
    } catch (error: any) {
      // If server is down and we're in development, use mock data
      if (error.message === 'Network Error' && useMockAuth(error)) {
        console.log('Using mock default database config');
        return {
          id: 1,
          db_type: 'mysql',
          host: 'localhost',
          port: 3306,
          db_name: 'default_db',
          db_user: 'default_user',
          db_password: '******', // Don't return actual password
          created_at: new Date().toISOString()
        };
      }
      throw error;
    }
  }
};

// Test connection utility
export const testConnection = async () => {
  try {
    const response = await apiClient.get('/');
    console.log('API Connection successful:', response.data);
    return { success: true, data: response.data };
  } catch (error: any) {
    console.error('API Connection failed:', error.message);
    return { success: false, error: error.message };
  }
};

// Interface for TextToSQL API request
interface TextToSQLRequest {
  query: string;
  user_id?: string;
  visualization?: boolean;
}

// Interface for TextToSQL API response
interface TextToSQLResponse {
  answer: string;
  sql_query: string;
  data: any[];
  chart_type: 'bar' | 'line' | 'pie';
  question: string;
}

// Text to SQL service for natural language query processing with the agent
export const textToSqlService = {
  // Send a natural language query to the text-to-SQL endpoint
  processQuery: async (query: string, visualization: boolean = false, userId: string = 'default_user'): Promise<TextToSQLResponse> => {
    try {
      const response = await apiClient.post<TextToSQLResponse>(
        `/api/text-to-sql`, 
        {
          query,
          user_id: userId,
          visualization
        }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error processing query:', error);
      if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail);
      }
      throw error;
    }
  }
};

// Add endpoint discovery utility
export const endpointDiscovery = {
  checkEndpoint: async (endpoint: string) => {
    try {
      const response = await apiClient.get(endpoint);
      return { exists: true, status: response.status, data: response.data };
    } catch (error: any) {
      return { 
        exists: false, 
        status: error.response?.status || 0, 
        error: error.response?.data || error.message 
      };
    }
  },
  
  discoverDatasetEndpoints: async () => {
    const possibleEndpoints = [
      '/datasets/',
      '/api/datasets/',
      '/user/datasets/',
      '/datasets/mine/',
      '/data/datasets/',
      '/api/data/datasets/',
      '/user/data/',
      '/data/',
      '/tables/'
    ];
    
    const results = {};
    
    for (const endpoint of possibleEndpoints) {
      console.log(`Testing endpoint: ${endpoint}`);
      const result = await endpointDiscovery.checkEndpoint(endpoint);
      results[endpoint] = result;
      
      if (result.exists) {
        console.log(`✅ Found working endpoint: ${endpoint}`, result);
      } else {
        console.log(`❌ Endpoint not available: ${endpoint} (${result.status})`);
      }
    }
    
    return results;
  }
};

export default apiClient; 