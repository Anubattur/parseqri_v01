import { useState } from 'react'
import Sidebar from '../components/Sidebar'
import Header from '../components/Header'
import { motion } from 'framer-motion'
import { 
  RiFileTextLine, 
  RiDownloadLine, 
  RiRefreshLine, 
  RiCalendarLine,
  RiFilter2Line
} from 'react-icons/ri'

interface Report {
  id: string;
  name: string;
  description: string;
  date: string;
  status: 'ready' | 'generating' | 'failed';
  type: 'pdf' | 'csv' | 'excel';
  size?: string;
}

const Reports = () => {
  const [isGenerating, setIsGenerating] = useState(false)
  const [selectedReport, setSelectedReport] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')

  // Mock data for reports
  const [reports, setReports] = useState<Report[]>([
    {
      id: '1',
      name: 'Monthly Sales Summary',
      description: 'Detailed breakdown of sales performance for the month',
      date: '2023-10-15',
      status: 'ready',
      type: 'pdf',
      size: '1.2 MB'
    },
    {
      id: '2',
      name: 'Customer Demographics',
      description: 'Analysis of customer data and segmentation',
      date: '2023-10-10',
      status: 'ready',
      type: 'excel',
      size: '3.7 MB'
    },
    {
      id: '3',
      name: 'Product Performance',
      description: 'Metrics on product sales and revenue contribution',
      date: '2023-10-05',
      status: 'ready',
      type: 'csv',
      size: '985 KB'
    }
  ])

  const generateReport = async (type: string) => {
    setIsGenerating(true)
    
    try {
      // Simulate API call with a delay
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Add new report to the list
      const newReport: Report = {
        id: Date.now().toString(),
        name: type === 'sales' 
          ? 'Sales Performance Report' 
          : type === 'inventory' 
            ? 'Inventory Status Report' 
            : 'Customer Engagement Report',
        description: type === 'sales' 
          ? 'Comprehensive analysis of sales metrics and trends' 
          : type === 'inventory' 
            ? 'Current inventory levels and restocking recommendations' 
            : 'User engagement patterns and retention metrics',
        date: new Date().toISOString().split('T')[0],
        status: 'generating',
        type: 'pdf'
      }
      
      setReports(prev => [newReport, ...prev])
      
      // Simulate report generation completion
      setTimeout(() => {
        setReports(prev => 
          prev.map(report => 
            report.id === newReport.id 
              ? { ...report, status: 'ready', size: '1.8 MB' } 
              : report
          )
        )
      }, 3000)
      
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadReport = (id: string) => {
    const report = reports.find(r => r.id === id)
    if (!report || report.status !== 'ready') return
    
    // In a real app, this would initiate a file download
    alert(`Downloading ${report.name} (${report.size})`)
  }

  const deleteReport = (id: string) => {
    setReports(prev => prev.filter(report => report.id !== id))
  }

  const refreshReport = (id: string) => {
    setReports(prev => 
      prev.map(report => 
        report.id === id 
          ? { ...report, status: 'generating' } 
          : report
      )
    )
    
    // Simulate refreshing to ready state after delay
    setTimeout(() => {
      setReports(prev => 
        prev.map(report => 
          report.id === id 
            ? { ...report, status: 'ready', date: new Date().toISOString().split('T')[0] } 
            : report
        )
      )
    }, 2000)
  }

  const filteredReports = filter === 'all' 
    ? reports 
    : reports.filter(report => report.type === filter)

  return (
    <div className="flex h-screen bg-gray-50 dark:bg-dark-950">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="max-w-7xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Reports</h1>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Generate and download reports from your data
                </p>
              </div>
              
              <div className="mt-4 md:mt-0 flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => generateReport('sales')}
                  disabled={isGenerating}
                  className="btn-primary flex items-center justify-center"
                >
                  {isGenerating ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Generating...
                    </>
                  ) : (
                    <>
                      <RiFileTextLine className="mr-2" />
                      Generate Sales Report
                    </>
                  )}
                </button>
                <div className="relative">
                  <select
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                    className="appearance-none block w-full bg-white dark:bg-dark-800 border border-gray-300 dark:border-dark-700 rounded-md px-3 py-2 pr-8 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="all">All Types</option>
                    <option value="pdf">PDF</option>
                    <option value="csv">CSV</option>
                    <option value="excel">Excel</option>
                  </select>
                  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
                    <RiFilter2Line />
                  </div>
                </div>
              </div>
            </div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="bg-white dark:bg-dark-900 rounded-xl shadow-md overflow-hidden"
            >
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-dark-700">
                  <thead className="bg-gray-50 dark:bg-dark-800">
                    <tr>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Name
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Date
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Type
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Size
                      </th>
                      <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Status
                      </th>
                      <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-dark-900 divide-y divide-gray-200 dark:divide-dark-700">
                    {filteredReports.length > 0 ? (
                      filteredReports.map((report) => (
                        <tr 
                          key={report.id} 
                          className={`${
                            selectedReport === report.id ? 'bg-primary-50 dark:bg-primary-900/10' : ''
                          } hover:bg-gray-50 dark:hover:bg-dark-800 cursor-pointer transition-colors`}
                          onClick={() => setSelectedReport(selectedReport === report.id ? null : report.id)}
                        >
                          <td className="px-6 py-4 text-sm">
                            <div className="font-medium text-gray-900 dark:text-white">{report.name}</div>
                            <div className="text-gray-500 dark:text-gray-400 text-xs mt-1">{report.description}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            <div className="flex items-center">
                              <RiCalendarLine className="mr-2 text-gray-400 dark:text-gray-500" />
                              {report.date}
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium uppercase">
                              {report.type}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                            {report.size || '-'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              report.status === 'ready' 
                                ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400' 
                                : report.status === 'generating' 
                                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-400'
                                  : 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-400'
                            }`}>
                              {report.status === 'generating' && (
                                <svg className="animate-spin -ml-0.5 mr-1.5 h-2 w-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                              )}
                              {report.status === 'ready' ? 'Ready' : report.status === 'generating' ? 'Generating' : 'Failed'}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <div className="flex items-center justify-end space-x-2">
                              {report.status === 'ready' ? (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    downloadReport(report.id)
                                  }}
                                  className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300"
                                >
                                  <RiDownloadLine size={18} />
                                </button>
                              ) : (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    refreshReport(report.id)
                                  }}
                                  className="text-yellow-600 hover:text-yellow-700 dark:text-yellow-400 dark:hover:text-yellow-300"
                                  disabled={report.status === 'generating'}
                                >
                                  <RiRefreshLine size={18} />
                                </button>
                              )}
                              <button
                                onClick={(e) => {
                                  e.stopPropagation()
                                  deleteReport(report.id)
                                }}
                                className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                              >
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                                  <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="px-6 py-10 text-center text-sm text-gray-500 dark:text-gray-400">
                          No reports found. Generate a new report to get started.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </motion.div>
            
            {selectedReport && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                className="mt-6 bg-white dark:bg-dark-900 rounded-xl shadow-md p-6"
              >
                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Report Details</h2>
                {reports.filter(r => r.id === selectedReport).map(report => (
                  <div key={report.id} className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Name</h3>
                      <p className="mt-1 text-sm text-gray-900 dark:text-white">{report.name}</p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Description</h3>
                      <p className="mt-1 text-sm text-gray-900 dark:text-white">{report.description}</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Generated On</h3>
                        <p className="mt-1 text-sm text-gray-900 dark:text-white">{report.date}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">File Type</h3>
                        <p className="mt-1 text-sm text-gray-900 dark:text-white uppercase">{report.type}</p>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Size</h3>
                        <p className="mt-1 text-sm text-gray-900 dark:text-white">{report.size || 'Unknown'}</p>
                      </div>
                    </div>
                    <div className="pt-4 flex justify-end">
                      {report.status === 'ready' && (
                        <button
                          onClick={() => downloadReport(report.id)}
                          className="btn-primary flex items-center"
                        >
                          <RiDownloadLine className="mr-2" />
                          Download Report
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </motion.div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

export default Reports

 