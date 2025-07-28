import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Database, FileText, Server, CheckCircle, AlertCircle, Loader } from 'lucide-react'

interface DatabaseConnection {
  host: string
  port: number
  db_name: string
  db_user: string
  db_password: string
  db_type: 'mysql' | 'postgres' | 'mongodb'
}

const DataSourceSelection: React.FC = () => {
  const navigate = useNavigate()
  const [selectedOption, setSelectedOption] = useState<'file' | 'database' | null>(null)
  const [showDatabaseForm, setShowDatabaseForm] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'success' | 'error'>('idle')
  const [connectionMessage, setConnectionMessage] = useState('')
  
  const [databaseConfig, setDatabaseConfig] = useState<DatabaseConnection>({
    host: 'localhost',
    port: 3306,
    db_name: '',
    db_user: '',
    db_password: '',
    db_type: 'mysql'
  })

  const handleOptionSelect = (option: 'file' | 'database') => {
    setSelectedOption(option)
    if (option === 'file') {
      // Store the selection and navigate to dashboard
      localStorage.setItem('dataSource', 'file')
      localStorage.setItem('dataSourceSelected', 'true')
      navigate('/dashboard')
    } else {
      setShowDatabaseForm(true)
    }
  }

  const handleDatabaseConfigChange = (field: keyof DatabaseConnection, value: string | number) => {
    setDatabaseConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const testConnection = async () => {
    setIsConnecting(true)
    setConnectionStatus('idle')
    
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/db/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(databaseConfig)
      })
      
      const result = await response.json()
      
      if (result.status === 'success') {
        setConnectionStatus('success')
        setConnectionMessage('Connection successful!')
      } else {
        setConnectionStatus('error')
        setConnectionMessage(result.message || 'Connection failed')
      }
    } catch (error: any) {
      console.error('Test connection error:', error)
      
      // Handle server down scenario in development
      if (error.message && error.message.includes('Failed to fetch')) {
        if (window.location.hostname === 'localhost') {
          console.log('Using mock test connection in development mode')
          // Simulate successful connection after a short delay
          setTimeout(() => {
            setConnectionStatus('success')
            setConnectionMessage('Mock connection successful! (Server is offline, using development mode)')
          }, 800)
          return
        }
      }
      
      setConnectionStatus('error')
      setConnectionMessage('Failed to test connection')
    } finally {
      setIsConnecting(false)
    }
  }

  const handleDatabaseConnect = async () => {
    if (connectionStatus !== 'success') {
      await testConnection()
      return
    }

    try {
      const token = localStorage.getItem('token')
      
      // Check if we're in development mode with server down
      const isDevelopment = window.location.hostname === 'localhost'
      const isMockAuth = localStorage.getItem('isMockAuth') === 'true'
      
      let configResult;
      
      if (isMockAuth && isDevelopment) {
        // Use mock data
        configResult = {
          id: 1,
          ...databaseConfig,
          created_at: new Date().toISOString()
        }
        console.log('Using mock database configuration:', configResult)
      } else {
        // Save database configuration
        const configResponse = await fetch('/db/config', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(databaseConfig)
        })
        
        if (!configResponse.ok) {
          throw new Error('Failed to save database configuration')
        }
        
        configResult = await configResponse.json()
        
        // Extract metadata
        const metadataResponse = await fetch(`/db/extract-metadata/${configResult.id}`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
        
        if (!metadataResponse.ok) {
          throw new Error('Failed to extract metadata')
        }
      }
      
      // Store the selection and navigate to dashboard
      localStorage.setItem('dataSource', 'database')
      localStorage.setItem('databaseConfigId', configResult.id.toString())
      localStorage.setItem('dataSourceSelected', 'true')
      navigate('/dashboard')
      
    } catch (error: any) {
      console.error('Database connect error:', error)
      
      // Handle server down scenario in development
      if (error.message && (error.message.includes('Failed to fetch') || error.message === 'Network Error')) {
        if (window.location.hostname === 'localhost') {
          console.log('Using mock database connection in development mode')
          
          // Store mock configuration and navigate to dashboard
          localStorage.setItem('dataSource', 'database')
          localStorage.setItem('databaseConfigId', '1')
          localStorage.setItem('dataSourceSelected', 'true')
          navigate('/dashboard')
          return
        }
      }
      
      setConnectionStatus('error')
      setConnectionMessage('Failed to connect and extract metadata')
    }
  }

  const getPortPlaceholder = () => {
    switch (databaseConfig.db_type) {
      case 'mysql': return '3306'
      case 'postgres': return '5432'
      case 'mongodb': return '27017'
      default: return '3306'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Choose Your Data Source</h1>
          <p className="text-xl text-gray-600">Select how you want to provide your data for analysis</p>
        </div>

        {!showDatabaseForm ? (
          <div className="grid md:grid-cols-2 gap-8">
            {/* File Upload Option */}
            <div 
              className={`bg-white rounded-xl shadow-lg p-8 cursor-pointer transition-all duration-300 hover:shadow-xl border-2 ${
                selectedOption === 'file' ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-primary-300'
              }`}
              onClick={() => handleOptionSelect('file')}
            >
              <div className="text-center">
                <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                  <Upload className="w-8 h-8 text-primary-600" />
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">Upload Files</h3>
                <p className="text-gray-600 mb-6">
                  Upload CSV or Excel files to analyze your data. Perfect for one-time analysis or small datasets.
                </p>
                <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <FileText className="w-4 h-4 mr-1" />
                    CSV
                  </div>
                  <div className="flex items-center">
                    <FileText className="w-4 h-4 mr-1" />
                    Excel
                  </div>
                </div>
              </div>
            </div>

            {/* Database Connection Option */}
            <div 
              className={`bg-white rounded-xl shadow-lg p-8 cursor-pointer transition-all duration-300 hover:shadow-xl border-2 ${
                selectedOption === 'database' ? 'border-green-500 bg-green-50' : 'border-gray-200 hover:border-green-300'
              }`}
              onClick={() => handleOptionSelect('database')}
            >
              <div className="text-center">
                <div className="mx-auto w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <Database className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">Connect Database</h3>
                <p className="text-gray-600 mb-6">
                  Connect to your existing database for real-time analysis. Supports multiple database types.
                </p>
                <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <Server className="w-4 h-4 mr-1" />
                    MySQL
                  </div>
                  <div className="flex items-center">
                    <Server className="w-4 h-4 mr-1" />
                    PostgreSQL
                  </div>
                  <div className="flex items-center">
                    <Server className="w-4 h-4 mr-1" />
                    MongoDB
                  </div>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Database Configuration Form */
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-2xl mx-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-semibold text-gray-900">Database Configuration</h3>
              <button
                onClick={() => setShowDatabaseForm(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="space-y-6">
              {/* Database Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Database Type
                </label>
                <select
                  value={databaseConfig.db_type}
                  onChange={(e) => {
                    const newType = e.target.value as 'mysql' | 'postgres' | 'mongodb'
                    handleDatabaseConfigChange('db_type', newType)
                    // Update default port based on database type
                    const defaultPorts = { mysql: 3306, postgres: 5432, mongodb: 27017 }
                    handleDatabaseConfigChange('port', defaultPorts[newType])
                  }}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                >
                  <option value="mysql">MySQL</option>
                  <option value="postgres">PostgreSQL</option>
                  <option value="mongodb">MongoDB</option>
                </select>
              </div>

              {/* Host and Port */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Host
                  </label>
                  <input
                    type="text"
                    value={databaseConfig.host}
                    onChange={(e) => handleDatabaseConfigChange('host', e.target.value)}
                    placeholder="localhost"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Port
                  </label>
                  <input
                    type="number"
                    value={databaseConfig.port}
                    onChange={(e) => handleDatabaseConfigChange('port', parseInt(e.target.value))}
                    placeholder={getPortPlaceholder()}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              {/* Database Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Database Name
                </label>
                <input
                  type="text"
                  value={databaseConfig.db_name}
                  onChange={(e) => handleDatabaseConfigChange('db_name', e.target.value)}
                  placeholder="your_database_name"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                />
              </div>

              {/* Username and Password */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={databaseConfig.db_user}
                    onChange={(e) => handleDatabaseConfigChange('db_user', e.target.value)}
                    placeholder="username"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={databaseConfig.db_password}
                    onChange={(e) => handleDatabaseConfigChange('db_password', e.target.value)}
                    placeholder="password"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>

              {/* Connection Status */}
              {connectionStatus !== 'idle' && (
                <div className={`p-4 rounded-md flex items-center ${
                  connectionStatus === 'success' 
                    ? 'bg-green-50 text-green-800' 
                    : 'bg-red-50 text-red-800'
                }`}>
                  {connectionStatus === 'success' ? (
                    <CheckCircle className="w-5 h-5 mr-2" />
                  ) : (
                    <AlertCircle className="w-5 h-5 mr-2" />
                  )}
                  {connectionMessage}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex space-x-4">
                <button
                  onClick={testConnection}
                  disabled={isConnecting}
                  className="flex-1 bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isConnecting ? (
                    <>
                      <Loader className="w-4 h-4 mr-2 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    'Test Connection'
                  )}
                </button>
                
                {connectionStatus === 'success' && (
                  <button
                    onClick={handleDatabaseConnect}
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 flex items-center justify-center"
                  >
                    Connect & Continue
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default DataSourceSelection 