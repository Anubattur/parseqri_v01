# ParseQri Product Document

## 1. Introduction
ParseQri is an AI-powered data analysis platform that enables users to query CSV data using natural language. The system provides a seamless experience where users can upload CSV files through an intuitive interface and immediately start exploring their data using plain English queries. ParseQri automatically processes these files, extracts metadata, creates appropriate database schemas, and makes the data available for querying without requiring users to have SQL knowledge.

## 2. Problem Statement
Traditionally, data analysis requires specialized technical skills such as knowledge of SQL, database management, and data modeling. This creates significant barriers for non-technical users who need to extract insights from their data. Current solutions either:
- Require users to learn complex query languages
- Depend on data teams to create reports, causing delays
- Offer limited analysis capabilities for non-technical users
- Lack the ability to understand the context and relationships in data

ParseQri addresses these challenges by providing an intuitive interface that allows anyone to analyze data through natural language, democratizing access to data insights.

## 3. Scope
The ParseQri platform encompasses:

**In Scope:**
- CSV file upload and processing
- Natural language to SQL query conversion
- Database schema creation and management
- Query execution and results visualization
- User authentication and data security
- Metadata extraction and indexing
- Error handling and user feedback
- Multi-user support with isolated data access

**Out of Scope:**
- ETL for extremely large datasets (>100GB)
- Support for non-CSV file formats (initial release)
- Automated data cleaning and transformation
- Real-time data streaming
- Complex data integration with third-party systems

## 4. Enabling Technology
ParseQri leverages several cutting-edge technologies to deliver its capabilities:

- **AI and Natural Language Processing**: 
  - Language models for understanding natural language queries
  - Semantic search using vector embeddings
  - ChromaDB for metadata indexing

- **Backend Technologies**:
  - FastAPI for high-performance API endpoints
  - SQLAlchemy for database ORM
  - PostgreSQL for relational data storage
  - Redis for caching and session management
  - Python ecosystem (Pandas, NumPy) for data processing

- **Frontend Technologies**:
  - React with TypeScript for type-safe UI development
  - TailwindCSS for responsive design
  - Chart.js for data visualization
  - Framer Motion for smooth animations
  - React Router for client-side routing

- **DevOps and Infrastructure**:
  - Docker for containerization
  - Authentication using JWT tokens
  - RESTful API architecture

## 5. Workflow & Architecture

### High-Level Workflow
```
┌─────────────┐     ┌──────────────┐     ┌────────────────┐     ┌───────────────┐
│  User       │────▶│ File Upload  │────▶│ File Processing│────▶│ Data Available│
│  Interface  │     │ Component    │     │ Pipeline       │     │ for Querying  │
└─────────────┘     └──────────────┘     └────────────────┘     └───────────────┘
       │                                                               ▲
       │                                                               │
       │               ┌───────────────┐     ┌────────────────┐       │
       └──────────────▶│ NL Query      │────▶│ SQL Generation │───────┘
                       │ Interface     │     │ & Execution    │
                       └───────────────┘     └────────────────┘
```

### Detailed Architecture
```
┌─────────────────────────────────────┐
│           Frontend                  │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ File Upload │  │ Query       │   │
│  │ Component   │  │ Interface   │   │
│  └─────────────┘  └─────────────┘   │
│         │               │           │
└─────────┼───────────────┼───────────┘
          │               │
          ▼               ▼
┌─────────────────────────────────────┐
│           Backend API               │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Auth        │  │ File        │   │
│  │ Service     │  │ Service     │   │
│  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Query       │  │ Results     │   │
│  │ Service     │  │ Service     │   │
│  └─────────────┘  └─────────────┘   │
└─────────┼───────────────┼───────────┘
          │               │
          ▼               ▼
┌─────────────────────────────────────┐
│         ParseQri Agent              │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ File Watcher│  │ TextToSQL   │   │
│  │ System      │  │ Agent       │   │
│  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ Metadata    │  │ DB Schema   │   │
│  │ Extractor   │  │ Generator   │   │
│  └─────────────┘  └─────────────┘   │
└─────────┼───────────────┼───────────┘
          │               │
          ▼               ▼
┌─────────────────────────────────────┐
│         Data Storage                │
│  ┌─────────────┐  ┌─────────────┐   │
│  │ PostgreSQL  │  │ ChromaDB    │   │
│  │ (Data)      │  │ (Metadata)  │   │
│  └─────────────┘  └─────────────┘   │
│  ┌─────────────┐                    │
│  │ Redis       │                    │
│  │ (Cache)     │                    │
│  └─────────────┘                    │
└─────────────────────────────────────┘
```

## 6. System Architecture

### Frontend Components
- **Authentication Module**: Handles user login, registration, and session management
- **File Upload Component**: Provides drag-and-drop functionality for CSV files
- **Query Interface**: Allows users to enter natural language queries
- **Results Viewer**: Displays query results in tabular and visual formats
- **Visualization Engine**: Generates charts and graphs based on query results

### Backend Components
- **FastAPI Server**: Core API server handling requests and responses
- **Authentication Service**: Manages JWT tokens and user permissions
- **File Processing Service**: Validates, transforms, and stores uploaded files
- **Database Connector**: Interfaces with PostgreSQL for data operations
- **Cache Manager**: Optimizes performance through Redis caching

### ParseQri Agent Components
- **File Watcher**: Monitors input directory for new files
- **Metadata Extractor**: Analyzes files to extract schema information
- **TextToSQL Agent**: Converts natural language to SQL queries
- **Database Schema Generator**: Creates appropriate database tables
- **Query Executor**: Runs generated SQL and returns results

### Data Storage
- **PostgreSQL**: Primary relational database for storing user data and CSV content
- **ChromaDB**: Vector database for semantic metadata indexing
- **Redis**: In-memory cache for session data and frequent queries
- **File Storage**: System for storing original CSV files and temporary data

## 7. Data Engineering

### Data Types and Processing
- **Structured Data**:
  - CSV files with headers
  - Tabular data with various column types (text, numeric, datetime)
  - Metadata about tables, columns, and relationships

- **Derived Data**:
  - Vector embeddings of column names and descriptions
  - Statistical summaries of column data
  - Query result sets and visualizations

### Database Architecture
- **PostgreSQL Configuration**:
  - Multiple schemas for multi-user isolation
  - Dynamic table creation based on CSV structure
  - Optimized indexing for query performance
  - Connection pooling for scalability

- **ChromaDB Implementation**:
  - Semantic indexing of table and column metadata
  - Vector embeddings for similarity search
  - Persistent storage for embeddings

- **Redis Usage**:
  - Session caching
  - Frequently accessed query results
  - Background task management

### Data Flow
1. CSV file uploaded by user
2. File validated and stored in temporary location
3. File processed and loaded into PostgreSQL
4. Metadata extracted and stored in ChromaDB
5. Data becomes available for querying
6. Natural language queries converted to SQL
7. SQL executed against PostgreSQL
8. Results returned to user interface

## 8. Deployment

### Cloud Deployment
- **Container Orchestration**:
  - Docker containers for each component
  - Kubernetes for orchestration (optional for scaling)
  - CI/CD pipeline for automated deployments

- **Cloud Providers**:
  - AWS: EC2 for compute, RDS for PostgreSQL, ElastiCache for Redis
  - Azure: App Service, Azure Database for PostgreSQL, Azure Cache for Redis
  - GCP: Compute Engine, Cloud SQL, Memorystore

- **Scaling Strategy**:
  - Horizontal scaling of API servers
  - Database connection pooling
  - Load balancing for high availability

### Local Deployment
- **Development Environment**:
  - Docker Compose for local containers
  - Virtual environment for Python dependencies
  - Node.js for frontend development

- **On-Premises Requirements**:
  - Linux/Windows server with Docker support
  - PostgreSQL database server
  - Sufficient storage for data files
  - Memory requirements based on expected data volume

- **Installation Process**:
  1. Clone repository and install dependencies
  2. Configure environment variables
  3. Initialize database schemas
  4. Start backend services
  5. Build and serve frontend application

### Security Considerations
- JWT-based authentication
- HTTPS for all communications
- Data encryption at rest
- Regular security updates
- Input validation and sanitization 