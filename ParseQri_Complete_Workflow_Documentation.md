# ParseQri Complete Workflow Documentation

## Overview
ParseQri is an AI-powered data analysis platform that allows users to connect to external databases (MySQL, PostgreSQL, MongoDB) or upload CSV files, and then query their data using natural language. This document explains the complete workflow from database connection to receiving the final answer.

## Architecture Overview

ParseQri follows a **layered agent-based architecture** with multiple specialized components:

1. **Frontend Layer** (React + TypeScript)
2. **Backend API Layer** (FastAPI)
3. **AI Agent Pipeline** (TextToSQL Agent System)
4. **Data Storage Layer** (MySQL + ChromaDB)

---

## Complete Workflow: Database Connection to Final Answer

### Phase 1: Database Connection & Setup

#### 1.1 Frontend Data Source Selection (`DataSourceSelection.tsx`)
```
User Interface Flow:
├── User selects "Database Connection" option
├── Fills database configuration form:
│   ├── Database Type (MySQL/PostgreSQL/MongoDB)
│   ├── Host (e.g., localhost)
│   ├── Port (e.g., 3306 for MySQL)
│   ├── Database Name (e.g., sakila)
│   ├── Username & Password
│   └── Test Connection button
└── Connection Status: Success/Error
```

#### 1.2 Backend Database Connection Testing (`/db/routes.py`)
```python
POST /db/test-connection
├── Receives database configuration
├── Creates temporary DBConfigOut object
├── Calls DatabaseConnectorFactory.test_connection()
├── Returns: {"status": "success/error", "message": "..."}
```

#### 1.3 Database Configuration Storage
```python
POST /db/config
├── Saves database configuration to PostgreSQL
├── Creates UserDatabase record with user_id
├── Returns database config ID
```

#### 1.4 Metadata Extraction (`/db/extract-metadata/{config_id}`)
```python
POST /db/extract-metadata/{config_id}
├── Retrieves stored database configuration
├── Calls metadata_extraction_service.extract_metadata()
├── Extracts schema information from external database
├── Stores metadata in ChromaDB for fast retrieval
├── Returns: metadata structure with tables and columns
```

**Files Involved:**
- `frontend/src/pages/DataSourceSelection.tsx`
- `ParseQri_Backend/app/db/routes.py`
- `ParseQri_Backend/app/db/connectors.py`
- `ParseQri_Backend/app/services/metadata_extraction.py`

---

### Phase 2: Natural Language Query Processing

#### 2.1 Frontend Query Input (`QueryPage.tsx` + `QueryInput.tsx`)
```
User Interface:
├── User types natural language question
├── Example: "Show me all customers from Japan"
├── Calls textToSqlService.processQuery(query, true)
└── Displays loading state
```

#### 2.2 Backend API Entry Point (`/routes/api.py`)
```python
POST /api/query
├── Receives: {"query": "Show me all customers from Japan"}
├── Extracts user_id from JWT token
├── Gets user's database configuration
├── Calls TextToSQL Agent pipeline
```

#### 2.3 TextToSQL Agent Orchestrator (`TextToSQL_Agent/core/orchestrator.py`)

This is the **main coordination hub** that manages the entire AI processing pipeline:

```python
process_query(user_question, db_name, table_name, user_id)
├── Initialize QueryContext with user question and metadata
├── Step 1: Query Cache Check
├── Step 2: Query Routing & Metadata Retrieval
├── Step 3: Intent Classification
├── Step 4: SQL Generation Pipeline OR Visualization Pipeline
└── Return processed QueryContext
```

---

### Phase 3: AI Agent Pipeline Processing

The orchestrator coordinates multiple specialized agents in sequence:

#### 3.1 Query Cache Agent (`agents/query_cache.py`)
```python
Purpose: Check if identical query was processed before
├── Searches cache for user_question + table_name + user_id
├── If cache hit: Returns cached SQL query
├── If cache miss: Continues to next agent
└── File Location: cache/query_cache.joblib
```

#### 3.2 Query Router Agent (`agents/query_router.py`)
```python
Purpose: Determine processing path and user context
├── Validates user_id exists
├── Determines which agents to invoke next
├── Routes to: ['metadata_indexer', 'mysql_handler']
└── Returns: {"next_steps": ["metadata_indexer", "mysql_handler"]}
```

#### 3.3 Metadata Indexer Agent (`agents/metadata_indexer.py`)
```python
Purpose: Retrieve relevant schema information for query
├── User-specific ChromaDB collection: {user_id}_metadata
├── Semantic search for relevant tables/columns
├── Input: user_question = "Show me all customers from Japan"
├── ChromaDB Search: Finds relevant metadata about customer table
├── Returns: relevant_metadata with table schema and descriptions
└── Storage: ../data/db_storage/{user_id}/chroma.sqlite3
```

**Key Schema Retrieval Process:**
```python
# ChromaDB stores metadata like:
{
  "table_name": "customer",
  "columns": ["customer_id", "first_name", "last_name", "country"],
  "column_descriptions": {
    "customer_id": "Unique identifier for customer",
    "country": "Customer's country of residence"
  }
}
```

#### 3.4 Intent Classification Agent (`agents/intent_classification.py`)
```python
Purpose: Determine if query needs data retrieval or visualization
├── LLM Model: llama3.1
├── Analyzes: "Show me all customers from Japan"
├── Classification:
│   ├── needs_visualization: false (simple data retrieval)
│   └── query_type: "data_retrieval"
├── Routes to: _process_sql_query() OR _process_visualization()
```

#### 3.5 Schema Understanding Agent (`agents/schema_understanding.py`)
```python
Purpose: Get detailed schema information from database
├── Connects to MySQL database: parseqri schema
├── Retrieves table structure for user's tables
├── Returns: {"customer_id": "int", "first_name": "varchar", ...}
└── Adds schema to context.schema
```

#### 3.6 SQL Generation Agent (`agents/sql_generation.py`)
```python
Purpose: Convert natural language to SQL query
├── LLM Model: qwen2.5
├── Input Prompt:
│   ├── User Question: "Show me all customers from Japan"
│   ├── Table Name: customer_{user_id} or customer (for external DB)
│   ├── Schema: {customer_id: int, first_name: varchar, country: varchar}
│   └── Metadata Descriptions: column meanings
├── LLM Processing: Generates SQL query
├── Output: "SELECT * FROM customer WHERE country = 'Japan'"
└── Adds user_id filter if needed for internal tables
```

**SQL Generation Prompt Example:**
```
Generate an SQL query to answer: "Show me all customers from Japan"

Database information:
- Table name: customer
- This is an external database (Sakila). Use table names directly.

Table schema:
- customer_id: int
- first_name: varchar
- last_name: varchar  
- country: varchar

IMPORTANT: Return only the SQL query.
```

#### 3.7 SQL Validation Agent (`agents/sql_validation.py`)
```python
Purpose: Validate generated SQL syntax and logic
├── LLM Model: orca2
├── Checks: Syntax errors, table/column existence, logical correctness
├── Returns: {sql_valid: true/false, sql_issues: "..."}
└── If invalid: Returns error to user
```

#### 3.8 MySQL Handler Agent (`agents/mysql_handler.py`)
```python
Purpose: Handle database-specific operations and user context
├── For external databases: Use original table names
├── For internal databases: Apply user_id suffix to table names
├── Validates user permissions and table access
└── Modifies SQL query if needed for user context
```

#### 3.9 Query Execution Agent (`agents/query_execution.py`)
```python
Purpose: Execute SQL query against database
├── Database Connection: MySQL engine (parseqri database)
├── Executes: "SELECT * FROM customer WHERE country = 'Japan'"
├── Returns: Pandas DataFrame with query results
└── Error Handling: Connection issues, syntax errors, no results
```

#### 3.10 Response Formatting Agent (`agents/response_formatting.py`)
```python
Purpose: Format results into user-friendly response
├── LLM Model: mistral
├── Input: Raw DataFrame results + original question
├── Processing:
│   ├── Analyzes data patterns
│   ├── Creates natural language summary
│   ├── Suggests chart type (bar, line, pie)
│   └── Formats data for frontend display
├── Output: {
│     "answer": "Found 15 customers from Japan",
│     "sql_query": "SELECT * FROM customer WHERE country = 'Japan'",
│     "data": [...],
│     "chart_type": "bar"
│   }
```

#### 3.11 Query Cache Agent (Storage)
```python
Purpose: Store successful query for future use
├── Caches: {user_question + table + user_id: sql_query}
├── Storage: cache/query_cache.joblib
└── Improves performance for repeated queries
```

---

### Phase 4: Response Delivery

#### 4.1 Backend API Response (`/routes/api.py`)
```python
├── Receives QueryContext from orchestrator
├── Extracts formatted response
├── Returns JSON:
{
  "answer": "Found 15 customers from Japan",
  "sql_query": "SELECT * FROM customer WHERE country = 'Japan'",
  "data": [...customer records...],
  "chart_type": "bar",
  "success": true
}
```

#### 4.2 Frontend Display (`QueryPage.tsx` + `QueryResult.tsx`)
```
UI Components:
├── QueryResult displays:
│   ├── Natural language answer
│   ├── Generated SQL query (expandable)
│   ├── Data table with results
│   └── Chart visualization (if applicable)
└── Error handling for failed queries
```

---

## Configuration Files & Key Components

### 1. Agent Configuration (`TextToSQL_Agent/config.json`)
```json
{
  "agents": {
    "metadata_indexer": {
      "module": "agents.metadata_indexer",
      "class": "MetadataIndexerAgent",
      "params": {
        "llm_model": "llama3.1",
        "chroma_persist_dir": "../data/db_storage"
      }
    },
    "sql_generation": {
      "module": "agents.sql_generation", 
      "class": "SQLGenerationAgent",
      "params": {
        "llm_model": "qwen2.5"
      }
    }
    // ... other agents
  }
}
```

### 2. Database Storage Locations
```
ChromaDB Metadata Storage:
├── ParseQri_Backend/ParseQri_Agent/data/db_storage/
│   ├── {user_id}/
│   │   ├── chroma.sqlite3 (metadata index)
│   │   └── metadata_{table_name}.json (metadata logs)
│   └── default_user/ (fallback user)

MySQL Database:
├── Host: localhost:3306
├── Database: parseqri
├── Tables: {table_name}_{user_id} (internal) or original names (external)

Query Cache:
├── ParseQri_Backend/ParseQri_Agent/TextToSQL_Agent/cache/
│   └── query_cache.joblib
```

### 3. Data Models (`models/data_models.py`)
```python
class QueryContext:
    user_question: str
    db_name: str  
    table_name: str
    user_id: str
    schema: Dict[str, str]
    sql_query: str
    query_results: pd.DataFrame
    formatted_response: str
    cache_hit: bool
    relevant_metadata: Dict
```

---

## Error Handling & Fallbacks

### 1. Database Connection Errors
```python
├── Test connection fails → Return error to user
├── Metadata extraction fails → Use fallback schema
├── MySQL unavailable → Fallback to SQLite (if available)
```

### 2. AI Processing Errors  
```python
├── LLM unavailable → Return error message
├── SQL generation fails → Request retry or rephrase
├── SQL validation fails → Show validation errors
├── Query execution fails → Database error message
```

### 3. User Context Issues
```python
├── No user_id → Use default_user or first available user
├── User has no tables → Prompt to upload data first
├── Table not found → List available tables for user
```

---

## Performance Optimizations

### 1. Caching Mechanisms
- **Query Cache**: Stores successful query translations
- **Metadata Cache**: ChromaDB for fast schema retrieval  
- **Connection Pooling**: SQLAlchemy engine for database connections

### 2. User Isolation
- **Multi-tenant Design**: Each user has separate ChromaDB collection
- **User-specific Tables**: Internal tables have user_id suffix
- **Permission Validation**: Users can only access their own data

### 3. Async Processing
- **Background Monitoring**: File watcher for automatic processing
- **Parallel Agents**: Multiple LLM models for different tasks
- **Streaming Responses**: Real-time feedback to users

---

## External Dependencies

### 1. LLM Models (via Ollama)
```
├── llama3.1: Intent classification, metadata extraction
├── qwen2.5: SQL generation  
├── mistral: Schema understanding, response formatting
├── orca2: SQL validation
└── codellama: Visualization generation
```

### 2. Databases
```
├── MySQL: Main data storage and external database connections
├── PostgreSQL: User management and configuration storage  
├── ChromaDB: Vector storage for metadata indexing
└── SQLite: Fallback for local file processing
```

### 3. Python Libraries
```
├── FastAPI: Backend web framework
├── SQLAlchemy: Database ORM
├── Pandas: Data processing
├── ChromaDB: Vector database
├── Ollama: LLM interface
```

---

## Summary

The ParseQri workflow implements a sophisticated **AI agent pipeline** that transforms natural language questions into executable SQL queries. The key innovation is the **multi-agent orchestration** where each agent has a specific responsibility:

1. **Metadata extraction and indexing** for fast schema retrieval
2. **User context management** for multi-tenant data isolation  
3. **Intent-driven processing** for appropriate response generation
4. **Caching mechanisms** for improved performance
5. **Error handling and fallbacks** for robust operation

This architecture allows ParseQri to handle both **external database connections** (like your Sakila database) and **internal CSV uploads** through a unified natural language interface, providing users with an intuitive way to explore and analyze their data. 