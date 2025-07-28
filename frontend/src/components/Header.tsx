import { useState, useEffect } from 'react'
import { RiMoonLine, RiSunLine, RiUserLine } from 'react-icons/ri'
import { motion } from 'framer-motion'

const Header = () => {
  const [darkMode, setDarkMode] = useState(false)
  const [username, setUsername] = useState('User')

  useEffect(() => {
    // Check if dark mode is set in localStorage
    const isDarkMode = localStorage.getItem('darkMode') === 'true'
    setDarkMode(isDarkMode)
    
    // Apply dark mode to document
    if (isDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }

    // Get username from localStorage or use default
    const storedUsername = localStorage.getItem('username')
    if (storedUsername) {
      setUsername(storedUsername)
    }
  }, [])

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode
    setDarkMode(newDarkMode)
    localStorage.setItem('darkMode', String(newDarkMode))
    
    if (newDarkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  return (
    <header className="bg-white dark:bg-dark-900 border-b border-gray-200 dark:border-dark-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-semibold text-gray-900 dark:text-white">Dashboard</h1>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={toggleDarkMode}
              className="p-2 rounded-full text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-dark-800"
              aria-label="Toggle dark mode"
            >
              {darkMode ? <RiSunLine size={20} /> : <RiMoonLine size={20} />}
            </button>
            
            <div className="flex items-center space-x-2">
              <div className="h-8 w-8 rounded-full bg-primary-600 flex items-center justify-center text-white">
                <RiUserLine />
              </div>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{username}</span>
            </div>
            {/* C2C Advanced Systems Logo */}
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="flex items-center"
            >
              <motion.img 
                src={darkMode ? "/c2c_logo_dark.png" : "/c2c_logo_light.png"}
                alt="C2C Advanced Systems" 
                className="h-12 w-auto"
                whileHover={{ scale: 1.05 }}
                transition={{ duration: 0.2 }}
              />
            </motion.div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header 