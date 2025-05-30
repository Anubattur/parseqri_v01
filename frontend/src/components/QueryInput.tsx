import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { RiSendPlaneFill, RiMicLine, RiCloseLine, RiQuestionLine } from 'react-icons/ri'

interface QueryInputProps {
  onSubmitQuery: (query: string) => void;
  isLoading: boolean;
}

const SUGGESTED_QUERIES = [
  "Show me sales by region",
  "What are our top 10 customers?",
  "Compare quarterly revenue"
]

const QueryInput = ({ onSubmitQuery, isLoading }: QueryInputProps) => {
  const [query, setQuery] = useState('')
  const [isFocused, setIsFocused] = useState(false)
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    // Filter suggestions based on current input
    if (query && query.length > 2) {
      const filtered = SUGGESTED_QUERIES.filter(
        suggestion => suggestion.toLowerCase().includes(query.toLowerCase())
      )
      setFilteredSuggestions(filtered)
    } else {
      setFilteredSuggestions([])
    }
  }, [query])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !isLoading) {
      onSubmitQuery(query)
      setQuery('')
      setFilteredSuggestions([])
    }
  }

  const handleFocus = () => {
    setIsFocused(true)
  }

  const handleBlur = () => {
    // Delay to allow click on suggestions
    setTimeout(() => {
      setIsFocused(false)
    }, 150)
  }

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion)
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  const handleClearInput = () => {
    setQuery('')
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  const handleExampleClick = (example: string) => {
    setQuery(example)
    if (inputRef.current) {
      inputRef.current.focus()
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full bg-white dark:bg-dark-900 rounded-xl shadow-md p-4"
    >
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-center relative">
          <motion.div
            animate={{ rotate: isLoading ? [0, 360] : 0 }}
            transition={{ repeat: isLoading ? Infinity : 0, duration: 1.5, ease: "linear" }}
            className="absolute left-3 text-gray-400"
          >
            <RiQuestionLine size={20} />
          </motion.div>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={handleFocus}
            onBlur={handleBlur}
            placeholder="Ask a question about your data..."
            className="flex-1 bg-gray-50 dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-lg pl-10 pr-10 py-3 focus:outline-none focus:ring-2 focus:ring-primary-500 dark:text-white transition-all duration-300"
            disabled={isLoading}
          />
          {query && !isLoading && (
            <button
              type="button"
              onClick={handleClearInput}
              className="absolute right-14 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
            >
              <RiCloseLine size={20} />
            </button>
          )}
          <motion.button
            type="submit"
            className={`absolute right-3 rounded-full p-2 ${
              isLoading || !query.trim() 
                ? 'bg-gray-200 dark:bg-dark-700 text-gray-400 dark:text-gray-500' 
                : 'bg-primary-600 text-white hover:bg-primary-700'
            } transition-colors duration-300`}
            disabled={isLoading || !query.trim()}
            whileHover={{ scale: isLoading || !query.trim() ? 1 : 1.05 }}
            whileTap={{ scale: isLoading || !query.trim() ? 1 : 0.95 }}
          >
            {isLoading ? (
              <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                className="h-5 w-5 border-2 border-gray-400 dark:border-gray-500 border-t-transparent rounded-full" 
              />
            ) : (
              <RiSendPlaneFill size={18} />
            )}
          </motion.button>
        </div>

        {/* Voice input button (for future implementation) */}
        <motion.button
          type="button"
          className="mt-2 p-2 rounded-full bg-gray-100 dark:bg-dark-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-dark-700 transition-colors float-right"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          title="Voice input (coming soon)"
        >
          <RiMicLine size={16} />
        </motion.button>
      </form>

      <AnimatePresence>
        {isFocused && filteredSuggestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-2 bg-white dark:bg-dark-800 rounded-lg border border-gray-200 dark:border-dark-700 shadow-lg overflow-hidden z-10"
          >
            <ul>
              {filteredSuggestions.map((suggestion, index) => (
                <motion.li 
                  key={index}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                >
                  <button
                    type="button"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-dark-700 text-gray-800 dark:text-gray-200 transition-colors"
                  >
                    {suggestion}
                  </button>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="mt-3 text-sm text-gray-500 dark:text-gray-400">
        <p>Examples: 
          {["Top 10 customers by revenue", "Monthly sales for last year"].map((example, index) => (
            <motion.button 
              key={index}
              onClick={() => handleExampleClick(example)}
              className="mx-2 text-primary-600 dark:text-primary-400 hover:underline"
              disabled={isLoading}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              {example}
            </motion.button>
          ))}
        </p>
      </div>
    </motion.div>
  )
}

export default QueryInput 