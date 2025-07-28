import React, { useState } from 'react'
import { motion } from 'framer-motion'
import QueryInput from '../components/QueryInput'
import QueryResult from '../components/QueryResult'
import { textToSqlService } from '../services/api'

const QueryPage = () => {
  const [loading, setLoading] = useState(false)
  const [queryResult, setQueryResult] = useState<{
    answer: string
    sqlQuery: string
    data: any[]
    chartType: 'bar' | 'line' | 'pie'
    question: string
  } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleQuerySubmit = async (query: string) => {
    setLoading(true)
    setError(null)
    
    try {
      // Call the textToSql service to process the query
      const response = await textToSqlService.processQuery(query, true)
      
      // Format the response for the QueryResult component
      setQueryResult({
        answer: response.answer,
        sqlQuery: response.sql_query,
        data: response.data || [],
        chartType: response.chart_type || 'bar',
        question: response.question || query
      })
    } catch (err: any) {
      console.error('Error processing query:', err)
      setError(err.message || 'An error occurred while processing your query')
      setQueryResult(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-5xl">
      <motion.h1 
        className="text-3xl font-bold text-center mb-8 text-gray-800 dark:text-white"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        ParseQri Data Query
      </motion.h1>
      
      <QueryInput 
        onSubmitQuery={handleQuerySubmit} 
        isLoading={loading} 
      />
      
      {error && (
        <motion.div 
          className="mt-6 p-4 bg-red-100 dark:bg-red-900/30 border border-red-300 dark:border-red-800 rounded-lg text-red-700 dark:text-red-400"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          <p>{error}</p>
        </motion.div>
      )}
      
      {queryResult && (
        <QueryResult 
          answer={queryResult.answer} 
          sqlQuery={queryResult.sqlQuery}
          data={queryResult.data}
          chartType={queryResult.chartType}
          question={queryResult.question}
          onLike={() => console.log('Liked response:', queryResult.question)}
          onDislike={() => console.log('Disliked response:', queryResult.question)}
        />
      )}
    </div>
  )
}

export default QueryPage 