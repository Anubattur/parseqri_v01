# ParseQri - PostgreSQL Data Parsing and Analysis API

ParseQri is a powerful API for PostgreSQL database management, data ingestion, and schema extraction. It allows users to connect to PostgreSQL databases, upload CSV files, and automatically create database schemas.

## Features

- **PostgreSQL Integration**: Connect to PostgreSQL databases with support for automatic database creation
- **User Authentication**: Secure JWT-based authentication system
- **CSV Data Ingestion**: Automatic parsing and schema generation from CSV files to PostgreSQL tables
- **Schema Metadata Extraction**: Capture and store table and column information for future use
- **Per-User Database Management**: Each user can manage multiple PostgreSQL database connections

## Installation

### Prerequisites

- Python 3.8+ 
- PostgreSQL database

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/parseqri.git
   cd parseqri
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/parseqri
   SECRET_KEY=your_secret_key
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

### Running the API

**Development mode**:
```bash
uvicorn app.main:app --reload
```

**Production mode**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker

You can also run the application using Docker:

```bash
# Build the Docker image
docker build -t parseqri .

# Run the container
docker run -p 8000:8000 --env-file .env parseqri
```

## API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Flow

### 1. Register and Login

First, create a user account and get an authentication token:

```bash
# Register a new user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "user@example.com", "password": "securepassword"}'

# Login to get a token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "testuser", "password": "securepassword"}'
```

The login response will include an access token that you'll use for all authenticated requests:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Create a Database Configuration

Configure a PostgreSQL database connection:

```bash
curl -X POST http://localhost:8000/api/db/config \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "localhost",
    "port": 5432,
    "db_name": "mydatabase",
    "db_user": "postgres",
    "db_password": "yourpassword"
  }'
```

The response will include the configuration ID (`id`) that you'll use when uploading data.

### 3. Upload a CSV File

Upload a CSV file to create a table in your PostgreSQL database:

```bash
curl -X POST http://localhost:8000/api/upload/csv \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@path/to/your/data.csv" \
  -F "table_name=your_table_name" \
  -F "db_config_id=1" \
  -F "create_if_not_exists=true"
```

The response will indicate that the file is being processed.

### 4. Retrieve Schema Information

Get the schema for a specific table:

```bash
curl -X GET http://localhost:8000/api/db/1/tables/your_table_name/metadata \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Database Configuration Example

### PostgreSQL
```json
{
  "host": "localhost",
  "port": 5432,
  "db_name": "mydatabase",
  "db_user": "postgres",
  "db_password": "yourpassword"
}
```

## Project Structure

```
parseqri/
├── app/                    # Main application package
│   ├── auth/               # Authentication logic
│   ├── core/               # Core utilities
│   │   ├── config.py       # Configuration settings
│   │   ├── database.py     # Database connection
│   │   ├── security.py     # Security utilities
│   │   └── exceptions.py   # Custom exceptions
│   ├── db/                 # Database connection and schema management
│   │   ├── connectors.py   # PostgreSQL connector
│   │   └── schema_manager.py # Schema management utilities
│   ├── routes/             # API routes
│   │   └── api.py          # Main API routes
│   ├── schemas/            # Pydantic models
│   └── main.py             # FastAPI application setup
├── uploads/                # Temporary storage for uploads
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
└── README.md               # Project documentation
```

## Development

### Running Tests

```bash
pytest app/tests/
```

## License

[MIT License](LICENSE) 