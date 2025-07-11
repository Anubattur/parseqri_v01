# Environment Configuration Setup

## Overview

The `main.py` script has been refactored to use environment variables for configuration instead of hardcoded values. This makes it flexible and allows you to connect to any database without modifying the code.

## Installation Requirements

First, install the required dependency:

```bash
pip install python-dotenv
```

## Environment Variables Setup

### Option 1: Create a .env file (Recommended)

Create a `.env` file in the `TextToSQL_Agent` directory with the following template:

```env
# Database Configuration (Primary/Internal Database)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=root
DB_NAME=parseqri
DB_TYPE=mysql

# External Database Configuration (For external connections)
EXTERNAL_DB_HOST=localhost
EXTERNAL_DB_PORT=3306
EXTERNAL_DB_USER=root
EXTERNAL_DB_PASSWORD=root
EXTERNAL_DB_NAME=sakila
EXTERNAL_DB_TYPE=mysql

# LLM Configuration
LLM_MODEL_SCHEMA=mistral
LLM_MODEL_INTENT=llama3.1
LLM_MODEL_SQL=qwen2.5
LLM_MODEL_VALIDATION=orca2
LLM_MODEL_RESPONSE=mistral
LLM_MODEL_VISUALIZATION=llama3.1
LLM_MODEL_METADATA=llama3.1
LLM_API_BASE=http://localhost:11434

# Paths Configuration
DATA_FOLDER=../data/input
CHROMA_PERSIST_DIR=../data/db_storage
CACHE_DIR=cache
LOG_FILE=../data/query_logs/textsql.log

# API Configuration
API_BASE_URL=http://localhost:8000
```

### Option 2: Set System Environment Variables

You can also set these as system environment variables instead of using a .env file:

**Windows (PowerShell):**
```powershell
$env:DB_HOST="your_host"
$env:DB_USER="your_username"
$env:DB_PASSWORD="your_password"
# ... etc
```

**Linux/Mac (Bash):**
```bash
export DB_HOST="your_host"
export DB_USER="your_username"
export DB_PASSWORD="your_password"
# ... etc
```

## Configuration Variables Explained

### Database Configuration
- `DB_HOST`: Database server hostname/IP
- `DB_PORT`: Database server port
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_NAME`: Database name
- `DB_TYPE`: Database type (mysql, postgres)

### External Database Configuration
These are used when connecting to external databases via `--db-id` parameter:
- `EXTERNAL_DB_*`: Same as above but for external database connections

### LLM Configuration
- `LLM_MODEL_*`: Different LLM models for different agents
- `LLM_API_BASE`: Base URL for LLM API (e.g., Ollama)

### Path Configuration
- `DATA_FOLDER`: Where input files are stored
- `CHROMA_PERSIST_DIR`: ChromaDB storage directory
- `CACHE_DIR`: Cache directory for query cache
- `LOG_FILE`: Log file location

## Usage Examples

### Connecting to Different Databases

**MySQL Database:**
```env
DB_TYPE=mysql
DB_HOST=mysql-server.example.com
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=mydatabase
```

**PostgreSQL Database:**
```env
DB_TYPE=postgres
DB_HOST=postgres-server.example.com
DB_PORT=5432
DB_USER=myuser
DB_PASSWORD=mypassword
DB_NAME=mydatabase
```

### Using Different LLM Models

```env
LLM_MODEL_SQL=codellama
LLM_MODEL_VISUALIZATION=llama3.1
LLM_API_BASE=http://localhost:11434
```

## Benefits of This Refactoring

1. **🔐 Security**: No hardcoded credentials in source code
2. **🔄 Flexibility**: Easy to switch between different databases
3. **🚀 Deployment**: Different configurations for dev/staging/production
4. **📦 File Operations**: Uses `shutil.copy2()` to preserve file metadata
5. **🧭 Path Handling**: Consistent use of `pathlib.Path` throughout
6. **🧠 Error Handling**: Better validation of ChromaDB collections
7. **⚡ Performance**: Validates ChromaDB content before assuming it's valid

## Fallback Behavior

If the `.env` file is missing or environment variables are not set, the system will:
1. Use the hardcoded defaults (same as before)
2. Display a warning message
3. Continue to function normally

This ensures backward compatibility while encouraging the use of proper configuration.

## Migration from Old System

If you were using the system before this refactor:
1. Create a `.env` file with your current database settings
2. No other changes needed - the system will work exactly as before
3. You can now easily switch between databases by modifying the `.env` file

## Troubleshooting

### "python-dotenv not installed" Warning
```bash
pip install python-dotenv
```

### Database Connection Issues
1. Check your `.env` file syntax
2. Verify database credentials
3. Ensure database server is running
4. Check network connectivity

### ChromaDB Validation Errors
The system now validates ChromaDB collections more thoroughly. If you see validation errors:
```bash
python main.py --init-chromadb --user your_user_id
```

This will reinitialize the ChromaDB collection with proper validation. 