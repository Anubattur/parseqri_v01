# ParseQri - AI-Powered Data Analysis and SQL Generation

ParseQri is a sophisticated platform that allows users to upload CSV files and query them using natural language. The system automatically processes the files, extracts metadata, and makes the data available for querying.

## Key Components

### Frontend
- Modern React application with TypeScript
- File upload component with drag-and-drop functionality
- Query interface for natural language queries

### Backend
- FastAPI server handling authentication, file uploads, and database operations
- Background processing for CSV files
- Automatic indexing of metadata

### ParseQri Agent
- Intelligent data processing pipeline
- Real-time file monitoring system
- ChromaDB integration for semantic metadata indexing
- SQL generation from natural language

## CSV File Upload Flow

The file upload process follows these steps:

1. **Frontend Upload**: User drags and drops or selects a CSV file in the UI
2. **Backend Processing**: 
   - File is saved in a temporary location and validated
   - File is copied to `ParseQri_Backend/ParseQri_Agent/data/input` directory
   - File is processed by the database connector to create tables

3. **Agent Processing**:
   - The watcher script monitors the `data/input` directory and detects new files
   - The file is processed by the TextToSQL Agent
   - Metadata is extracted and indexed into ChromaDB
   - The database schema is created and stored in PostgreSQL

4. **Data Availability**:
   - After processing, the data becomes available for querying
   - Users can ask natural language questions about their data
   - The system generates SQL, retrieves results, and formats responses

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   # Backend
   cd ParseQri_Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Configure Environment**:
   - Set up PostgreSQL database
   - Configure ChromaDB storage location
   - Update environment variables as needed

3. **Run the Applications**:
   ```bash
   # Start Backend
   cd ParseQri_Backend
   python -m app.main
   
   # Start Frontend
   cd frontend
   npm run dev
   ```

4. **Using the System**:
   - Upload CSV files through the UI
   - Wait for processing to complete
   - Start querying your data using natural language

## Folder Structure

- `frontend/`: React application with TypeScript
- `ParseQri_Backend/`: FastAPI server and database operations
  - `app/`: API endpoints and core functionality
  - `ParseQri_Agent/`: Intelligent data processing
    - `data/input/`: Input directory for uploaded files
    - `data/db_storage/`: ChromaDB storage location
    - `TextToSQL_Agent/`: SQL generation engine

## Troubleshooting

- **File Upload Issues**: Check permissions on input directories
- **Processing Failures**: View logs in the terminal or API responses
- **Query Errors**: Ensure data was properly indexed in ChromaDB 