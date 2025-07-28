import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { RiMailLine, RiLockLine, RiEyeLine, RiEyeOffLine, RiUserLine } from 'react-icons/ri'
import { authService } from '../services/api'

interface RegisterProps {
  setIsAuthenticated: (value: boolean) => void;
}

const Register = ({ setIsAuthenticated }: RegisterProps) => {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    // Basic validation
    if (!name || !email || !password) {
      setError('All fields are required')
      return
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long')
      return
    }
    
    setIsLoading(true)
    
    try {
      // Call the registration API
      const response = await authService.register(name, email, password)
      
      // After successful registration, login the user
      const loginResponse = await authService.login(name, password)
      
      // Set authenticated state and save token
      setIsAuthenticated(true)
      localStorage.setItem('token', loginResponse.access_token)
      localStorage.setItem('username', name)
      
      // Set flag indicating this is a new user registration
      sessionStorage.setItem('newUserRegistration', 'true')
      
      // New users need to select their data source
      navigate('/data-source')
    } catch (error: any) {
      console.error('Registration error:', error)
      
      // Handle specific error types
      if (error.message === 'Network Error') {
        setError('Unable to connect to the server. Using offline mode for development.')
        
        // If we're in development and mock auth is enabled, proceed to data source selection
        if (localStorage.getItem('isMockAuth') === 'true') {
          setTimeout(() => {
            setIsAuthenticated(true)
            sessionStorage.setItem('newUserRegistration', 'true')
            navigate('/data-source')
          }, 1500)
        }
      } else {
        setError(error.response?.data?.detail || 'Registration failed. Please try again.')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div 
      className="min-h-screen flex flex-col justify-center relative"
      style={{
        backgroundImage: `url('/ins_magar.jpg')`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      {/* Background overlay */}
      <div className="absolute inset-0 bg-black bg-opacity-25"></div>
      
      {/* Content */}
      <div className="relative z-10">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <Link to="/">
            <motion.div 
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="flex justify-center"
            >
              <span className="text-3xl font-bold text-white drop-shadow-lg">ParseQri</span>
            </motion.div>
          </Link>
          <motion.h2 
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="mt-4 text-center text-2xl font-bold text-white drop-shadow-lg"
          >
            Create your account
          </motion.h2>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="backdrop-blur-md bg-white/20 dark:bg-gray-900/20 py-8 px-6 shadow-2xl rounded-2xl sm:px-10 border border-white/30"
          >
            <form className="space-y-6" onSubmit={handleSubmit}>
              {error && (
                <div className="bg-red-50/80 dark:bg-red-900/40 text-red-700 dark:text-red-400 p-3 rounded-lg text-sm backdrop-blur-sm">
                  {error}
                </div>
              )}
              
              <div>
                <label htmlFor="name" className="block text-sm font-medium text-white drop-shadow-sm">
                  User Name
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <RiUserLine className="h-5 w-5 text-gray-300" />
                  </div>
                  <input
                    id="name"
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="w-full pl-10 pr-3 py-2 border border-white/30 rounded-md bg-white/10 backdrop-blur-sm text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="johndoe"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-white drop-shadow-sm">
                  Email address
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <RiMailLine className="h-5 w-5 text-gray-300" />
                  </div>
                  <input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full pl-10 pr-3 py-2 border border-white/30 rounded-md bg-white/10 backdrop-blur-sm text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-white drop-shadow-sm">
                  Password
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <RiLockLine className="h-5 w-5 text-gray-300" />
                  </div>
                  <input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    className="w-full pl-10 pr-10 py-2 border border-white/30 rounded-md bg-white/10 backdrop-blur-sm text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="••••••••"
                  />
                  <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-gray-300 hover:text-white focus:outline-none"
                    >
                      {showPassword ? (
                        <RiEyeOffLine className="h-5 w-5" />
                      ) : (
                        <RiEyeLine className="h-5 w-5" />
                      )}
                    </button>
                  </div>
                </div>
                <p className="mt-1 text-xs text-gray-300 drop-shadow-sm">
                  Password must be at least 8 characters long
                </p>
              </div>

              <div className="flex items-center">
                <input
                  id="terms"
                  type="checkbox"
                  required
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <label htmlFor="terms" className="ml-2 block text-sm text-white drop-shadow-sm">
                  I agree to the{' '}
                  <a href="#" className="font-medium text-primary-300 hover:text-primary-200 drop-shadow-sm">
                    Terms of Service
                  </a>{' '}
                  and{' '}
                  <a href="#" className="font-medium text-primary-300 hover:text-primary-200 drop-shadow-sm">
                    Privacy Policy
                  </a>
                </label>
              </div>

              <div>
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600/80 hover:bg-primary-700/80 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed backdrop-blur-sm"
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Creating account...
                    </>
                  ) : (
                    'Create account'
                  )}
                </button>
              </div>
            </form>
            
            
          </motion.div>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 text-center text-sm text-white drop-shadow-lg"
          >
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary-300 hover:text-primary-200 drop-shadow-sm">
              Sign in
            </Link>
          </motion.p>
        </div>
      </div>
    </div>
  )
}

export default Register 