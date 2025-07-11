# ParseQri Setup Instructions

## Overview
ParseQri has been updated to support multiple database types (MySQL, PostgreSQL, MongoDB) with optimized ChromaDB integration for metadata storage. Users can now choose between file uploads or connecting their own databases.

## Prerequisites

### Required Software
1. **Python 3.8+**
2. **Node.js 16+**
3. **MySQL Server** (primary database)
4. **Optional**: PostgreSQL, MongoDB (for external database connections)

### Python Dependencies
```bash
cd ParseQri_Backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd frontend
npm install
```

## Database Setup

### 1. MySQL Setup (Primary Database)
```sql
-- Create database
CREATE DATABASE parseqri;

-- Create user (optional)
CREATE USER 'parseqri_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON parseqri.* TO 'parseqri_user'@'localhost';
FLUSH PRIVILEGES;
```

### 2. Environment Configuration
Create a `.env` file in `ParseQri_Backend/`:
```env
# Database Configuration (MySQL)
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/parseqri

# JWT Configuration
SECRET_KEY=your-secret-key-here-make-it-long-and-random
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# Optional: Redis Configuration for caching
REDIS_URL=redis://localhost:6379/0

# Optional: ChromaDB Configuration
CHROMA_PERSIST_DIR=./data/chroma_storage
```

## Running the Application

### 1. Start Backend
```bash
cd ParseQri_Backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## New Features

### 1. Data Source Selection
After login, users are redirected to a data source selection page where they can choose:
- **File Upload**: Upload CSV/Excel files (traditional workflow)
- **Database Connection**: Connect to external MySQL, PostgreSQL, or MongoDB databases

### 2. Database Connection Flow
1. Select "Connect Database" option
2. Choose database type (MySQL/PostgreSQL/MongoDB)
3. Enter connection details:
   - Host
   - Port
   - Database name
   - Username
   - Password
4. Test connection
5. If successful, metadata is automatically extracted and stored in ChromaDB
6. Proceed to dashboard with database connection active

### 3. Optimized ChromaDB Integration
- **Unified Storage**: All metadata stored in a single ChromaDB instance
- **User Context**: Metadata tagged with user IDs for isolation
- **Semantic Search**: Natural language queries can find relevant tables/collections
- **Multi-Source Support**: Handles metadata from files, MySQL, PostgreSQL, and MongoDB

### 4. Dashboard Updates
- **Conditional UI**: File upload disabled when database is connected
- **Data Source Indicator**: Shows current data source type
- **Quick Actions**: Easy switching between data sources

## API Endpoints

### New Database Endpoints
- `POST /api/db/test-connection` - Test database connection
- `POST /api/db/config` - Save database configuration
- `POST /api/db/extract-metadata/{config_id}` - Extract and store metadata
- `GET /api/db/search-metadata` - Search metadata using natural language

### Existing Endpoints
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /api/upload` - File upload
- `POST /api/query` - Natural language query processing

## Database Migration

### From PostgreSQL to MySQL
If you're migrating from the previous PostgreSQL setup:

1. **Export existing data** (if needed):
```bash
pg_dump parseqri > backup.sql
```

2. **Update environment variables** to use MySQL
3. **Run the application** - tables will be created automatically
4. **Re-upload files or reconnect databases** to rebuild metadata

## Troubleshooting

### Common Issues

1. **MySQL Connection Error**
   - Ensure MySQL server is running
   - Check credentials in `.env` file
   - Verify database exists

2. **ChromaDB Permission Error**
   - Ensure write permissions for `./data/chroma_storage` directory
   - Check disk space

3. **Frontend API Connection Error**
   - Verify backend is running on port 8000
   - Check CORS settings in `main.py`

4. **Database Metadata Extraction Fails**
   - Verify external database credentials
   - Check network connectivity
   - Ensure user has read permissions on target database

### Logs and Debugging
- Backend logs: Check console output where uvicorn is running
- Frontend logs: Check browser developer console
- Database logs: Check MySQL error logs

## Development Notes

### Key Changes Made
1. **Requirements**: Replaced `psycopg2-binary` with `mysql-connector-python`, `PyMySQL`, `pymongo`
2. **Database Config**: Updated default from PostgreSQL to MySQL
3. **Connectors**: Added `DatabaseConnectorFactory` for multi-database support
4. **ChromaDB**: Centralized manager with user-based isolation
5. **Frontend**: New data source selection page and conditional UI
6. **Routes**: Added database connection testing and metadata extraction

### Architecture
```
Frontend (React/TypeScript)
├── Data Source Selection Page
├── Dashboard (conditional UI)
└── Database Connection Form

Backend (FastAPI/Python)
├── MySQL (primary database)
├── ChromaDB (metadata storage)
├── Multi-database connectors
└── Metadata extraction service

External Databases (optional)
├── MySQL
├── PostgreSQL
└── MongoDB
```

## Security Considerations
- Database passwords are stored in the primary MySQL database
- Consider encrypting sensitive connection details
- Use environment variables for configuration
- Implement proper access controls for external database connections

## Next Steps
1. Test with your specific database configurations
2. Upload sample data or connect test databases
3. Try natural language queries
4. Monitor ChromaDB storage and performance
5. Consider implementing database connection pooling for production use 