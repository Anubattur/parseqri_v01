import React from 'react'
import QueryResult from './QueryResult'

const MarkdownTestResponse = () => {
  // Sample markdown-formatted AI response
  const sampleMarkdownResponse = `## Sales Analysis Results

Based on your query about **top 10 customers by revenue**, here are the key findings:

### Top Performing Customers

1. **CustomerA** - Generated \`$125,450.00\` in total revenue
2. **CustomerB** - Generated \`$98,760.50\` in total revenue  
3. **CustomerC** - Generated \`$87,230.25\` in total revenue

### Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Revenue** | $1,234,567.89 |
| **Average Order Value** | $456.78 |
| **Number of Orders** | 2,703 |

### Key Insights

- The **top 3 customers** account for **25.3%** of total revenue
- Customer retention rate is **89.2%** for high-value customers
- Most orders occur during **Q4** (holiday season)

> **Note**: This data represents the last 12 months of sales activity.

### Recommendations

- Focus on **customer retention** programs for top performers
- Implement **loyalty rewards** for customers spending over $50,000
- Consider **seasonal promotions** during Q1-Q3 to boost sales

---

*Analysis completed on ${new Date().toLocaleDateString()}*`

  const sampleSqlQuery = `SELECT 
    customer_name,
    SUM(order_total) as total_revenue,
    COUNT(order_id) as order_count,
    AVG(order_total) as avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY customer_name
ORDER BY total_revenue DESC
LIMIT 10;`

  const sampleData = [
    { name: 'CustomerA', value: 125450 },
    { name: 'CustomerB', value: 98760.50 },
    { name: 'CustomerC', value: 87230.25 },
    { name: 'CustomerD', value: 76543.21 },
    { name: 'CustomerE', value: 65432.10 }
  ]

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">
        Markdown Formatting Demo
      </h1>
      
      <div className="mb-4 p-4 bg-primary-50 dark:bg-primary-900/20 rounded-lg border border-primary-200 dark:border-primary-800">
        <p className="text-primary-800 dark:text-primary-200">
          <strong>Demo:</strong> This shows how AI responses will look with markdown formatting enabled.
          The AI will now return structured, well-formatted responses with headers, tables, lists, and emphasis.
        </p>
      </div>

      <QueryResult 
        answer={sampleMarkdownResponse}
        sqlQuery={sampleSqlQuery}
        data={sampleData}
        chartType="bar"
        question="Show me the top 10 customers by revenue"
        onLike={() => console.log('Liked demo response')}
        onDislike={() => console.log('Disliked demo response')}
      />
    </div>
  )
}

export default MarkdownTestResponse 