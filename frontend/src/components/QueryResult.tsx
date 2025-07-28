import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { 
  RiCodeSSlashLine, 
  RiMessage2Line, 
  RiBarChartFill,
  RiDownload2Line,
  RiFullscreenLine,
  RiFullscreenExitLine,
  RiShareLine,
  RiQuestionLine,
  RiDeleteBinLine,
  RiThumbUpLine,
  RiThumbUpFill,
  RiThumbDownLine,
  RiThumbDownFill
} from 'react-icons/ri'
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
import { Bar, Line, Pie } from 'react-chartjs-2'

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

const COLORS = ['#010080', '#000066', '#00004d', '#000033', '#0000ff', '#3333ff', '#6666ff']

interface QueryResultProps {
  answer: string;
  sqlQuery: string;
  data: any[];
  chartType?: 'bar' | 'line' | 'pie';
  question?: string;
  onDelete?: () => void;
  onLike?: () => void;
  onDislike?: () => void;
}

const QueryResult = ({ 
  answer, 
  sqlQuery, 
  data,
  chartType = 'bar',
  question = '',
  onDelete,
  onLike,
  onDislike
}: QueryResultProps) => {
  const [activeTab, setActiveTab] = useState<'answer' | 'sql' | 'viz'>('answer')
  const [fullscreen, setFullscreen] = useState(false)
  const [copied, setCopied] = useState(false)
  const [liked, setLiked] = useState(false)
  const [disliked, setDisliked] = useState(false)

  // Use the question prop if available, otherwise try to extract it from the answer
  const extractedQuestion = (() => {
    if (question && question.trim()) {
      return question;
    }
    
    // Fallback: try to extract from the answer
    const match = answer.match(/^Based on "(.*?)"/) || answer.match(/^Here's a visualization based on "(.*?)"/);
    return match ? match[1] : '';
  })();

  const renderChart = () => {
    if (!data || data.length === 0) {
      return (
        <div className="flex flex-col items-center justify-center h-64">
          <RiBarChartFill size={48} className="text-gray-300 dark:text-dark-600" />
          <p className="mt-4 text-gray-500 dark:text-gray-400">No data to visualize</p>
        </div>
      )
    }

    const chartData = {
      labels: data.map(item => item.name),
      datasets: [
        {
          label: 'Value',
          data: data.map(item => item.value),
          backgroundColor: chartType === 'pie' ? COLORS : '#010080',
          borderColor: chartType === 'pie' ? COLORS.map(color => color + '88') : '#010080',
          borderWidth: 1,
        }
      ]
    }

    const chartOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top' as const,
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          titleColor: '#000',
          bodyColor: '#000',
          borderColor: 'rgba(0, 0, 0, 0.1)',
          borderWidth: 1,
          padding: 10,
          displayColors: true,
          boxPadding: 2,
        }
      }
    }

    switch (chartType) {
      case 'bar':
        return (
          <div className="h-[300px]">
            <Bar data={chartData} options={chartOptions} />
          </div>
        )
      case 'line':
        return (
          <div className="h-[300px]">
            <Line data={chartData} options={chartOptions} />
          </div>
        )
      case 'pie':
        return (
          <div className="h-[300px]">
            <Pie data={chartData} options={{
              ...chartOptions,
              plugins: {
                ...chartOptions.plugins,
                legend: {
                  position: 'right' as const,
                }
              }
            }} />
          </div>
        )
      default:
        return null
    }
  }

  const exportCSV = () => {
    if (!data || data.length === 0) return
    
    // Convert data to CSV format
    const headers = Object.keys(data[0]).join(',')
    const rows = data.map(row => Object.values(row).join(','))
    const csv = [headers, ...rows].join('\n')
    
    // Create and download CSV file
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.setAttribute('href', url)
    a.setAttribute('download', 'query_result.csv')
    a.click()
  }

  const shareResult = () => {
    // Copy the SQL query to clipboard
    navigator.clipboard.writeText(sqlQuery).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    })
  }

  const handleLike = () => {
    if (disliked) {
      setDisliked(false)
    }
    setLiked(!liked)
    if (onLike) {
      onLike()
    }
  }

  const handleDislike = () => {
    if (liked) {
      setLiked(false)
    }
    setDisliked(!disliked)
    if (onDislike) {
      onDislike()
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className={`w-full bg-white dark:bg-dark-900 rounded-xl shadow-md overflow-hidden mt-6 ${
        fullscreen ? 'fixed inset-0 z-50 mt-0 rounded-none' : ''
      }`}
    >
      <div className="border-b border-gray-200 dark:border-dark-700">
        <nav className="flex -mb-px p-1">
          <button
            className={`py-3 px-5 border-b-2 font-medium text-sm flex items-center space-x-2 transition-all duration-200 ${
              activeTab === 'answer'
                ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('answer')}
          >
            <RiMessage2Line size={18} />
            <span>Answer</span>
          </button>
          <button
            className={`py-3 px-5 border-b-2 font-medium text-sm flex items-center space-x-2 transition-all duration-200 ${
              activeTab === 'sql'
                ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('sql')}
          >
            <RiCodeSSlashLine size={18} />
            <span>SQL Query</span>
          </button>
          <button
            className={`py-3 px-5 border-b-2 font-medium text-sm flex items-center space-x-2 transition-all duration-200 ${
              activeTab === 'viz'
                ? 'border-primary-600 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
            }`}
            onClick={() => setActiveTab('viz')}
          >
            <RiBarChartFill size={18} />
            <span>Visualization</span>
          </button>
          <div className="flex-1"></div>
          <div className="flex items-center">
            {onDelete && (
              <motion.button
                className="p-2 mx-1 rounded-full text-gray-500 hover:text-red-500 dark:text-gray-400 dark:hover:text-red-400 hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors"
                onClick={onDelete}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
              >
                <RiDeleteBinLine size={18} />
              </motion.button>
            )}
            <motion.button
              className="p-2 mx-1 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors"
              onClick={shareResult}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <RiShareLine size={18} />
              <AnimatePresence>
                {copied && (
                  <motion.div 
                    className="absolute top-12 right-0 bg-green-500 text-white text-xs px-2 py-1 rounded shadow-md"
                    initial={{ opacity: 0, y: -5 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                  >
                    Copied!
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.button>
            <motion.button
              className="p-2 mx-1 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors"
              onClick={exportCSV}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <RiDownload2Line size={18} />
            </motion.button>
            <motion.button
              className="p-2 mx-1 rounded-full text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-dark-800 transition-colors"
              onClick={() => setFullscreen(!fullscreen)}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              {fullscreen ? <RiFullscreenExitLine size={18} /> : <RiFullscreenLine size={18} />}
            </motion.button>
          </div>
        </nav>
      </div>
      <div className={`p-6 ${fullscreen ? 'h-[calc(100vh-64px)] overflow-auto' : ''}`}>
        <AnimatePresence mode="wait">
          {activeTab === 'answer' && (
            <motion.div 
              key="answer"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="prose dark:prose-invert max-w-none relative"
            >
              {extractedQuestion && (
                <div className="mb-4">
                  <div className="flex items-center mb-2">
                    <RiQuestionLine size={20} className="text-primary-600 dark:text-primary-400 mr-2" />
                    <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                      {extractedQuestion}
                    </h3>
                  </div>
                  <div className="h-0.5 bg-gray-100 dark:bg-dark-700 w-full my-3"></div>
                </div>
              )}
              <div className="prose prose-gray dark:prose-invert max-w-none prose-headings:text-gray-900 dark:prose-headings:text-white prose-p:text-gray-800 dark:prose-p:text-gray-200 prose-strong:text-gray-900 dark:prose-strong:text-white prose-code:text-primary-600 dark:prose-code:text-primary-400 prose-code:bg-gray-100 dark:prose-code:bg-gray-800 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-pre:bg-gray-100 dark:prose-pre:bg-gray-800 prose-blockquote:border-primary-500 prose-blockquote:text-gray-700 dark:prose-blockquote:text-gray-300 pb-12">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code: ({ node, inline, className, children, ...props }: any) => {
                      const match = /language-(\w+)/.exec(className || '')
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={vscDarkPlus as any}
                          language={match[1]}
                          PreTag="div"
                          className="rounded-lg text-sm"
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      )
                    },
                    h1: ({ children }: any) => (
                      <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4 mt-6">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }: any) => (
                      <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-3 mt-5">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }: any) => (
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2 mt-4">
                        {children}
                      </h3>
                    ),
                    p: ({ children }: any) => (
                      <p className="text-gray-800 dark:text-gray-200 mb-3 leading-relaxed">
                        {children}
                      </p>
                    ),
                    ul: ({ children }: any) => (
                      <ul className="list-disc pl-6 mb-3 text-gray-800 dark:text-gray-200 space-y-1">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }: any) => (
                      <ol className="list-decimal pl-6 mb-3 text-gray-800 dark:text-gray-200 space-y-1">
                        {children}
                      </ol>
                    ),
                    li: ({ children }: any) => (
                      <li className="text-gray-800 dark:text-gray-200">
                        {children}
                      </li>
                    ),
                    blockquote: ({ children }: any) => (
                      <blockquote className="border-l-4 border-primary-500 pl-4 py-2 mb-3 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 italic">
                        {children}
                      </blockquote>
                    ),
                    table: ({ children }: any) => (
                      <div className="overflow-x-auto mb-4">
                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                          {children}
                        </table>
                      </div>
                    ),
                    thead: ({ children }: any) => (
                      <thead className="bg-gray-50 dark:bg-gray-800">
                        {children}
                      </thead>
                    ),
                    tbody: ({ children }: any) => (
                      <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                        {children}
                      </tbody>
                    ),
                    th: ({ children }: any) => (
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        {children}
                      </th>
                    ),
                    td: ({ children }: any) => (
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-200">
                        {children}
                      </td>
                    ),
                    strong: ({ children }: any) => (
                      <strong className="font-semibold text-gray-900 dark:text-white">
                        {children}
                      </strong>
                    ),
                    em: ({ children }: any) => (
                      <em className="italic text-gray-800 dark:text-gray-200">
                        {children}
                      </em>
                    ),
                    a: ({ children, href }: any) => (
                      <a 
                        href={href} 
                        className="text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 underline transition-colors"
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        {children}
                      </a>
                    )
                  }}
                >
                  {answer}
                </ReactMarkdown>
              </div>
              
              {/* Like/Dislike buttons */}
              <div className="absolute bottom-2 right-2 flex items-center space-x-2">
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleLike}
                  className={`p-2 rounded-full transition-colors ${
                    liked 
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400' 
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-green-50 dark:hover:bg-green-900/20 hover:text-green-600 dark:hover:text-green-400'
                  }`}
                  title="Like this response"
                >
                  {liked ? <RiThumbUpFill size={16} /> : <RiThumbUpLine size={16} />}
                </motion.button>
                
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={handleDislike}
                  className={`p-2 rounded-full transition-colors ${
                    disliked 
                      ? 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400' 
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400'
                  }`}
                  title="Dislike this response"
                >
                  {disliked ? <RiThumbDownFill size={16} /> : <RiThumbDownLine size={16} />}
                </motion.button>
              </div>
            </motion.div>
          )}
          {activeTab === 'sql' && (
            <motion.div 
              key="sql"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden rounded-lg"
            >
              <SyntaxHighlighter
                language="sql"
                style={vscDarkPlus}
                className="text-sm rounded-lg"
                wrapLines={true}
                wrapLongLines={true}
              >
                {sqlQuery}
              </SyntaxHighlighter>
            </motion.div>
          )}
          {activeTab === 'viz' && (
            <motion.div 
              key="viz"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="mt-4 chart-container"
            >
              {renderChart()}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}

export default QueryResult 