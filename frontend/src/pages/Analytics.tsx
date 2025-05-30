import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { motion } from 'framer-motion'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip as ChartTooltip,
  Legend as ChartLegend
} from 'chart.js'
import { Line, Bar, Pie } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  ChartTooltip,
  ChartLegend
)

const COLORS = ['#1e70f2', '#0ca6eb', '#58b0ff', '#bce0ff', '#0369a0', '#075784', '#0c496c']

const Analytics = () => {
  const [dateRange, setDateRange] = useState('month')

  // Mock data for analytics
  const revenueData = [
    { name: 'Jan', value: 4000 },
    { name: 'Feb', value: 3000 },
    { name: 'Mar', value: 2000 },
    { name: 'Apr', value: 2780 },
    { name: 'May', value: 1890 },
    { name: 'Jun', value: 2390 },
    { name: 'Jul', value: 3490 },
    { name: 'Aug', value: 4200 },
    { name: 'Sep', value: 5000 },
    { name: 'Oct', value: 4300 },
    { name: 'Nov', value: 4800 },
    { name: 'Dec', value: 5200 }
  ]

  const categoryData = [
    { name: 'Electronics', value: 35 },
    { name: 'Clothing', value: 25 },
    { name: 'Home & Garden', value: 15 },
    { name: 'Books', value: 10 },
    { name: 'Toys', value: 8 },
    { name: 'Other', value: 7 }
  ]

  const customerData = [
    { name: 'New', value: 2400 },
    { name: 'Returning', value: 4567 },
    { name: 'Inactive', value: 1398 }
  ]

  const topProductsData = [
    { name: 'Product A', value: 3200 },
    { name: 'Product B', value: 2800 },
    { name: 'Product C', value: 2500 },
    { name: 'Product D', value: 2100 },
    { name: 'Product E', value: 1900 }
  ]

  // Chart.js data and options 
  const lineChartData = {
    labels: revenueData.map(item => item.name),
    datasets: [
      {
        label: 'Revenue',
        data: revenueData.map(item => item.value),
        borderColor: '#1e70f2',
        backgroundColor: 'rgba(30, 112, 242, 0.1)',
        tension: 0.4,
      }
    ]
  }
  
  const lineChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
  }

  const pieChartData = {
    labels: categoryData.map(item => item.name),
    datasets: [
      {
        data: categoryData.map(item => item.value),
        backgroundColor: COLORS,
        borderColor: COLORS.map(color => color + '88'),
        borderWidth: 1,
      }
    ]
  }
  
  const pieChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right' as const,
      },
    },
  }

  const customerChartData = {
    labels: customerData.map(item => item.name),
    datasets: [
      {
        data: customerData.map(item => item.value),
        backgroundColor: COLORS.slice(0, 3),
        borderColor: COLORS.slice(0, 3).map(color => color + '88'),
        borderWidth: 1,
      }
    ]
  }

  const barChartData = {
    labels: topProductsData.map(item => item.name),
    datasets: [
      {
        label: 'Sales',
        data: topProductsData.map(item => item.value),
        backgroundColor: '#1e70f2',
      }
    ]
  }
  
  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: 'y' as const,
    plugins: {
      legend: {
        position: 'top' as const,
      },
    },
    scales: {
      x: {
        beginAtZero: true,
      }
    }
  }

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-dark-950">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex items-center justify-between mb-8">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Analytics</h1>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  View insights and trends from your data
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700 dark:text-gray-300">Time Range:</span>
                <select
                  value={dateRange}
                  onChange={(e) => setDateRange(e.target.value)}
                  className="bg-white dark:bg-dark-800 border border-gray-300 dark:border-dark-700 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="week">Last Week</option>
                  <option value="month">Last Month</option>
                  <option value="quarter">Last Quarter</option>
                  <option value="year">Last Year</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Revenue Over Time */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
              >
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Revenue Over Time</h2>
                <div className="h-80">
                  <Line data={lineChartData} options={lineChartOptions} />
                </div>
              </motion.div>
              
              {/* Sales by Category */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.1 }}
                className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
              >
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Sales by Category</h2>
                <div className="h-80">
                  <Pie data={pieChartData} options={pieChartOptions} />
                </div>
              </motion.div>
              
              {/* Customer Segments */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.2 }}
                className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
              >
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Customer Segments</h2>
                <div className="h-80">
                  <Pie data={customerChartData} options={pieChartOptions} />
                </div>
              </motion.div>
              
              {/* Top Products */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 }}
                className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
              >
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Top Products</h2>
                <div className="h-80">
                  <Bar data={barChartData} options={barChartOptions} />
                </div>
              </motion.div>
            </div>
            
            {/* Key Metrics Summary */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.4 }}
              className="mt-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
              <div className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase">Total Revenue</h3>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">$48,290</p>
                <div className="mt-1 flex items-center">
                  <span className="text-green-500 text-sm font-medium">▲ 12.5%</span>
                  <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">from previous period</span>
                </div>
              </div>
              
              <div className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase">Orders</h3>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">1,463</p>
                <div className="mt-1 flex items-center">
                  <span className="text-green-500 text-sm font-medium">▲ 8.2%</span>
                  <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">from previous period</span>
                </div>
              </div>
              
              <div className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase">Conversion Rate</h3>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">3.6%</p>
                <div className="mt-1 flex items-center">
                  <span className="text-red-500 text-sm font-medium">▼ 1.8%</span>
                  <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">from previous period</span>
                </div>
              </div>
              
              <div className="bg-white dark:bg-dark-900 rounded-xl shadow-md p-6">
                <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase">Avg. Order Value</h3>
                <p className="mt-2 text-3xl font-bold text-gray-900 dark:text-white">$33.00</p>
                <div className="mt-1 flex items-center">
                  <span className="text-green-500 text-sm font-medium">▲ 4.2%</span>
                  <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">from previous period</span>
                </div>
              </div>
            </motion.div>
          </div>
        </main>
      </div>
    </div>
  )
}

export default Analytics 