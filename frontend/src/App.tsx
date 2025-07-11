import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { useEffect, useState } from 'react'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import Databases from './pages/Databases'
import Analytics from './pages/Analytics'
import Reports from './pages/Reports'
import Login from './pages/Login'
import Register from './pages/Register'
import DataSourceSelection from './pages/DataSourceSelection'
import ProtectedRoute from './components/ProtectedRoute'
import LoginTest from './components/LoginTest'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false)

  useEffect(() => {
    // Check if user is authenticated (token exists in localStorage)
    const token = localStorage.getItem('token')
    setIsAuthenticated(!!token)
  }, [])

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login setIsAuthenticated={setIsAuthenticated} />} />
      <Route path="/register" element={<Register setIsAuthenticated={setIsAuthenticated} />} />
      <Route path="/login-test" element={<LoginTest />} />
      
      {/* Data Source Selection - Protected Route */}
      <Route 
        path="/data-source" 
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <DataSourceSelection />
          </ProtectedRoute>
        } 
      />
      
      {/* Protected Routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/databases" 
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Databases />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/analytics" 
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Analytics />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/reports" 
        element={
          <ProtectedRoute isAuthenticated={isAuthenticated}>
            <Reports />
          </ProtectedRoute>
        } 
      />
    </Routes>
  )
}

export default App 