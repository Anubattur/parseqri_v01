import { NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  RiDashboardLine, 
  RiBarChartBoxLine, 
  RiFileListLine,
  RiLogoutBoxLine
} from 'react-icons/ri'
import { authService } from '../services/api'

const Sidebar = () => {
  const handleLogout = () => {
    authService.logout()
  }

  return (
    <motion.div 
      initial={{ x: -100, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="h-screen w-64 bg-white dark:bg-dark-900 border-r border-gray-200 dark:border-dark-700 flex flex-col"
    >
      <div className="p-6">
        <h1 className="text-2xl font-bold text-primary-600">
          ParseQri
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          Text-to-SQL Platform
        </p>
      </div>

      <nav className="flex-1 px-4 py-4">
        <ul className="space-y-2">
          <li>
            <NavLink 
              to="/dashboard" 
              className={({ isActive }) => 
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  isActive 
                    ? 'bg-primary-50 dark:bg-dark-800 text-primary-600 dark:text-primary-400' 
                    : 'hover:bg-gray-100 dark:hover:bg-dark-800'
                }`
              }
            >
              <RiDashboardLine size={20} />
              <span>Dashboard</span>
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/analytics" 
              className={({ isActive }) => 
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  isActive 
                    ? 'bg-primary-50 dark:bg-dark-800 text-primary-600 dark:text-primary-400' 
                    : 'hover:bg-gray-100 dark:hover:bg-dark-800'
                }`
              }
            >
              <RiBarChartBoxLine size={20} />
              <span>Analytics</span>
            </NavLink>
          </li>
          <li>
            <NavLink 
              to="/reports" 
              className={({ isActive }) => 
                `flex items-center space-x-3 px-4 py-3 rounded-lg transition-all ${
                  isActive 
                    ? 'bg-primary-50 dark:bg-dark-800 text-primary-600 dark:text-primary-400' 
                    : 'hover:bg-gray-100 dark:hover:bg-dark-800'
                }`
              }
            >
              <RiFileListLine size={20} />
              <span>Reports</span>
            </NavLink>
          </li>
        </ul>
      </nav>

      <div className="p-4 border-t border-gray-200 dark:border-dark-700">
        <button
          onClick={handleLogout}
          className="flex items-center space-x-3 w-full px-4 py-3 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-800 transition-all"
        >
          <RiLogoutBoxLine size={20} />
          <span>Logout</span>
        </button>
      </div>
    </motion.div>
  )
}

export default Sidebar 