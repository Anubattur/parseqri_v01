import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import QueryInput from '../components/QueryInput'
import QueryResult from '../components/QueryResult'
import FileUpload from '../components/FileUpload'
import { motion, AnimatePresence } from 'framer-motion'
import { RiDatabaseLine, RiFileListLine, RiArrowRightLine, RiCloseLine, RiErrorWarningLine, RiDeleteBinLine } from 'react-icons/ri'
import { sqlService, authService, apiDiagnostic, datasetService, dbService, textToSqlService } from '../services/api'

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(false)
  const [queryResults, setQueryResults] = useState<{
    answer: string;
    sqlQuery: string;
    data: any[];
    chartType: 'bar' | 'line' | 'pie';
    question?: string;
    timestamp?: number;
  }[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [currentDataset, setCurrentDataset] = useState<string | null>(null)
  const [currentDatasetId, setCurrentDatasetId] = useState<number | null>(null)
  const [showWelcome, setShowWelcome] = useState(true)
  const [recentQueries, setRecentQueries] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const [authStatus, setAuthStatus] = useState<{isAuthenticated: boolean, message?: string}>({isAuthenticated: true})
  const navigate = useNavigate()

  useEffect(() => {
    // Check authentication status on page load
    checkAuthStatus();
    
    // Check if the user has dismissed the welcome message before
    const hasSeenWelcome = localStorage.getItem('hasSeenWelcome');
    
    // Proper way to handle boolean values in localStorage
    if (hasSeenWelcome && JSON.parse(hasSeenWelcome) === false) {
      setShowWelcome(true);
    }

    // Load any recent queries from local storage
    const storedQueries = localStorage.getItem('recentQueries')
    if (storedQueries) {
      setRecentQueries(JSON.parse(storedQueries))
    }
  }, [])

  const checkAuthStatus = async () => {
    try {
      // Check if token exists in localStorage
      const token = localStorage.getItem('token');
      if (!token) {
        setAuthStatus({isAuthenticated: false, message: "No authentication token found"});
        navigate('/login');
        return;
      }
      
      // Verify token validity
      const authResult = await authService.checkAuth();
      if (!authResult.isAuthenticated) {
        setAuthStatus({isAuthenticated: false, message: "Authentication token expired or invalid"});
        navigate('/login');
      } else {
        setAuthStatus({isAuthenticated: true});
      }
    } catch (error) {
      console.error("Auth check error:", error);
      setAuthStatus({isAuthenticated: false, message: "Failed to verify authentication"});
    }
  };

  const handleSubmitQuery = async (query: string) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Store the query in recent queries
      const updatedQueries = [query, ...recentQueries.slice(0, 4)]
      setRecentQueries(updatedQueries)
      localStorage.setItem('recentQueries', JSON.stringify(updatedQueries))
      
      // Check auth status again before making the API call
      const tokenInfo = apiDiagnostic.checkToken();
      if (!tokenInfo.hasToken) {
        throw new Error("Authentication required. Please log in.");
      }
      
      // Use the TextToSQL agent service to process the query
      const response = await textToSqlService.processQuery(query, true);
      
      console.log("TextToSQL Response:", JSON.stringify(response, null, 2)); // Detailed debug log
      
      // Convert the data to the format expected by QueryResult
      let formattedData = response.data || [];
      
      const newResult = {
        answer: response.answer,
        sqlQuery: response.sql_query,
        data: formattedData,
        chartType: response.chart_type as 'bar' | 'line' | 'pie' || 'bar',
        question: response.question || query,
        timestamp: Date.now()
      };
      
      // Add the new result to the array of results
      setQueryResults(prev => [newResult, ...prev]);
    } catch (err: any) {
      console.error('Error processing query:', err)
      
      // Check if it's an auth error
      if (err.response?.status === 401) {
        setError("Authentication error. Please log in again.");
        navigate('/login');
        return;
      }
      
      setError(err.response?.data?.error || err.message || 'Failed to process your query. Please try again.')
      // Set an error response
      const errorResult = {
        answer: "Sorry, I encountered an error while processing your query.",
        sqlQuery: "",
        data: [],
        chartType: 'bar' as 'bar' | 'line' | 'pie',
        question: query,
        timestamp: Date.now()
      };
      
      setQueryResults(prev => [errorResult, ...prev]);
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileUpload = async (file: File) => {
    setIsUploading(true)
    setError('')
    
    try {
      // Get current user information
      const user = await authService.getCurrentUser();
      
      if (!user || !user.id) {
        throw new Error('Unable to get user information. Please login again.');
      }
      
      // Try to get existing database configurations
      let dbId = 1; // Default
      try {
        const configs = await dbService.getConfigs();
        if (configs && configs.length > 0) {
          // Use the first available config
          dbId = configs[0].id;
        } else {
          // Create a default configuration if none exists
          console.log('No database configuration found, creating default...');
          const defaultConfig = await dbService.createDefaultConfig();
          dbId = defaultConfig.id;
        }
      } catch (configError) {
        console.warn('Error getting database configs, creating default:', configError);
        // Create a default configuration
        try {
          const defaultConfig = await dbService.createDefaultConfig();
          dbId = defaultConfig.id;
        } catch (defaultConfigError) {
          console.error('Failed to create default config:', defaultConfigError);
          throw new Error('Unable to create database configuration. Please try again later.');
        }
      }
      
      // Upload the file to the backend
      const response = await datasetService.uploadCsv(file, dbId);
      
      // Set the current dataset name 
      setCurrentDataset(file.name);
      
      // Use the actual database id returned from the response if available
      setCurrentDatasetId(response.id || dbId);
      
      // Show success message
      console.log('File uploaded successfully:', response);
      
    } catch (error: any) {
      console.error('Error uploading file:', error);
      
      // Set error message
      const errorMessage = error.message || 'Failed to upload file. Please try again.';
      setError(errorMessage);
    } finally {
      setIsUploading(false)
    }
  }

  const dismissWelcome = () => {
    setShowWelcome(false);
    // Proper way to store boolean values in localStorage
    localStorage.setItem('hasSeenWelcome', JSON.stringify(true));
  }

  const suggestedQueries = [
    'What are the top 5 products by revenue?',
    'Show me monthly sales for the past year',
    'Which customers have the highest lifetime value?',
    'What is the revenue trend by quarter?'
  ]

  const handleDeleteQuery = (e: React.MouseEvent, indexToDelete: number) => {
    e.stopPropagation(); // Prevent triggering the parent button click
    
    const updatedQueries = recentQueries.filter((_, index) => index !== indexToDelete);
    setRecentQueries(updatedQueries);
    localStorage.setItem('recentQueries', JSON.stringify(updatedQueries));
  };

  // Function to clear all chat history
  const clearChatHistory = () => {
    setQueryResults([]);
  }

  // Function to delete a specific query result
  const handleDeleteResult = (timestamp: number | undefined) => {
    if (!timestamp) return;
    
    setQueryResults(prev => prev.filter(result => result.timestamp !== timestamp));
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-dark-950">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            {!authStatus.isAuthenticated && (
              <motion.div 
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl px-6 py-4 mb-6 relative"
              >
                <div className="flex items-center">
                  <RiErrorWarningLine size={24} className="text-red-600 dark:text-red-400 mr-2" />
                  <div>
                    <h2 className="text-lg font-semibold text-red-800 dark:text-red-300">Authentication Error</h2>
                    <p className="text-red-700 dark:text-red-400">{authStatus.message || "Please log in again"}</p>
                  </div>
                </div>
                <div className="mt-3">
                  <button 
                    onClick={() => navigate('/login')}
                    className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-md"
                  >
                    Go to Login
                  </button>
                </div>
              </motion.div>
            )}
          
            <AnimatePresence>
              {showWelcome && (
                <motion.div 
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.5 }}
                  className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-xl px-6 py-4 mb-6 relative"
                >
                  <button 
                    onClick={dismissWelcome} 
                    className="absolute right-3 top-3 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                  >
                    <RiCloseLine size={20} />
                  </button>
                  <h2 className="text-lg font-semibold text-primary-800 dark:text-primary-300 mb-2">Welcome to ParseQri!</h2>
                  <p className="text-primary-700 dark:text-primary-400 mb-3">
                    Ask questions in natural language and get instant SQL queries, visualizations, and insights.
                  </p>
                  <div className="flex flex-wrap gap-2">
                    <button 
                      onClick={() => handleSubmitQuery("What are our top 5 selling products?")}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 dark:bg-primary-800/30 text-primary-800 dark:text-primary-300 hover:bg-primary-200 dark:hover:bg-primary-800/50 transition-colors"
                    >
                      Try a sample query <RiArrowRightLine className="ml-1" />
                    </button>
                    <button
                      onClick={() => {
                        const fileInput = document.querySelector('input[type="file"]');
                        if (fileInput instanceof HTMLElement) {
                          fileInput.click();
                        }
                      }}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-primary-100 dark:bg-primary-800/30 text-primary-800 dark:text-primary-300 hover:bg-primary-200 dark:hover:bg-primary-800/50 transition-colors"
                    >
                      Upload a CSV <RiArrowRightLine className="ml-1" />
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-6"
              >
                <div className="flex">
                  <RiErrorWarningLine size={24} className="text-red-500 dark:text-red-400 mr-3" />
                  <div>
                    <h3 className="text-sm font-medium text-red-800 dark:text-red-300">Error</h3>
                    <p className="mt-1 text-sm text-red-700 dark:text-red-400">{error}</p>
                  </div>
                </div>
              </motion.div>
            )}
            
            <div className="mb-8">
              <motion.h1 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="text-2xl font-bold text-gray-900 dark:text-white"
              >
                Dashboard
              </motion.h1>
              <motion.p 
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="mt-1 text-sm text-gray-600 dark:text-gray-400"
              >
                Ask questions about your data and get instant insights
              </motion.p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-6">
              <div className="md:col-span-2">
                <QueryInput 
                  onSubmitQuery={handleSubmitQuery} 
                  isLoading={isLoading} 
                />
                
                <AnimatePresence>
                  {recentQueries.length > 0 && queryResults.length === 0 && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.3 }}
                      className="mt-4 bg-white dark:bg-dark-900 rounded-xl shadow-md p-4"
                    >
                      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Recent Queries</h3>
                      <div className="space-y-2">
                        {recentQueries.map((query, index) => (
                          <motion.button
                            key={index}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            onClick={() => handleSubmitQuery(query)}
                            className="block w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-800 rounded-lg transition-colors relative group"
                          >
                            {query}
                            <RiDeleteBinLine 
                              className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-red-500 dark:text-gray-500 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                              size={16}
                              onClick={(e) => handleDeleteQuery(e, index)}
                            />
                          </motion.button>
                        ))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
                
                {queryResults.length > 0 && (
                  <div className="mt-6 space-y-6">
                    {queryResults.map((result, index) => (
                      <motion.div
                        key={result.timestamp || index}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                      >
                        <QueryResult 
                          answer={result.answer}
                          sqlQuery={result.sqlQuery}
                          data={result.data}
                          chartType={result.chartType}
                          question={result.question}
                          onDelete={() => handleDeleteResult(result.timestamp)}
                        />
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>
              
              <div className="space-y-6">
                <FileUpload 
                  onFileUpload={handleFileUpload}
                  isUploading={isUploading}
                />
                
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
                >
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Suggested Queries</h3>
                  <ul className="space-y-2">
                    {suggestedQueries.map((query, index) => (
                      <motion.li 
                        key={index}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                      >
                        <button
                          onClick={() => handleSubmitQuery(query)}
                          className="w-full text-left p-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors text-sm flex items-center group"
                          disabled={isLoading}
                        >
                          <span className="flex-1">{query}</span>
                          <RiArrowRightLine className="opacity-0 group-hover:opacity-100 transition-opacity ml-2 text-primary-600" />
                        </button>
                      </motion.li>
                    ))}
                  </ul>
                </motion.div>
                
                <AnimatePresence>
                  {currentDataset && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5 }}
                      className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
                    >
                      <div className="flex items-center mb-4">
                        <RiDatabaseLine size={20} className="text-primary-600 dark:text-primary-400 mr-2" />
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">Current Dataset</h3>
                      </div>
                      <div className="flex items-center rounded-lg bg-gray-50 dark:bg-dark-800 p-3">
                        <RiFileListLine size={16} className="text-gray-500 dark:text-gray-400 mr-2" />
                        <span className="text-sm text-gray-700 dark:text-gray-300 truncate">
                          {currentDataset}
                        </span>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Dashboard 