# AIDataQueryAgent - Integrated PDF/Image to SQL Query System

This project integrates two modular AI agent systems:

1. **Conversion Tool**: Converts PDF and image files to structured CSV data
2. **TextToSQL Agent**: Transforms CSV data into an SQL database and answers natural language queries

## Directory Structure

```
AIDataQueryAgent/
├── conversion_tool/
│   ├── main.py
│   ├── input_agent.py
│   ├── parser_agent.py
│   ├── preprocessing_agent.py
│   ├── conversion_agent_csv.py
│   └── ...
├── TextToSQL_Agent/
│   ├── main.py                # Unified Entry Point
│   ├── simplified_query.py    # Simplified version without LLM dependencies
│   ├── agents/
│   │   ├── data_ingestion.py
│   │   ├── data_preprocessing.py
│   │   ├── sql_generation.py
│   │   ├── sql_validation.py
│   │   ├── query_execution.py
│   │   ├── response_formatting.py
│   │   └── ...
│   ├── core/
│   │   └── orchestrator.py    # Central controller
│   └── ...
├── data/
│   ├── input/                 # Place PDF and image files here
│   ├── csv_output/            # Generated CSV files
│   ├── db_storage/            # SQLite databases
│   └── query_logs/            # System logs
```

## How to Use

### 1. Setup

Ensure all dependencies are installed:

```bash
# Install conversion_tool dependencies
cd conversion_tool
pip install -r requirements.txt

# Install TextToSQL_Agent dependencies
cd ../TextToSQL_Agent
pip install -r requirements.txt
```

### 2. Process PDF/Image Files

1. Place your PDF or image files in the `data/input/` directory.
2. Run the integrated tool:

```bash
cd TextToSQL_Agent
python main.py
```

This will:
- Convert the PDF/image files to CSV using the conversion_tool
- Copy the resulting CSV to data/csv_output/
- Ingest the CSV into an SQLite database

### 3. Query Your Data

Once your data is processed, you can query it using natural language:

```bash
cd TextToSQL_Agent
python main.py "What is the average value in column X?"
```

The system will:
- Convert your natural language query to SQL
- Execute the SQL query against your database
- Return a human-readable response

### 4. Simplified Version (No LLM Dependencies)

If you don't have access to local language models (Ollama), you can use the simplified version:

```bash
cd TextToSQL_Agent
python simplified_query.py process  # Process files in data/input
python simplified_query.py info     # Show database information
python simplified_query.py "SELECT * FROM table_name"  # Execute SQL directly
```

This version provides:
- PDF/Image to CSV conversion
- CSV to SQLite database ingestion
- Direct SQL query execution
- Schema and data exploration

## Features

- **Automated Workflow**: From PDF/image to SQL database to query results
- **Error Handling**: Comprehensive error checking and logging
- **Data Integrity**: Validates both input and output at each step
- **Natural Language Interface**: Ask questions in plain English (requires Ollama)
- **Direct SQL Interface**: Execute SQL queries directly (simplified version)

## Requirements

- Python 3.8+
- Tesseract OCR (for image processing)
- Ollama (optional, for natural language queries)
- See requirements.txt files in each subdirectory for additional dependencies

## Troubleshooting

If you encounter issues:

1. Check the logs in `data/query_logs/`
2. Ensure Tesseract is properly installed for image processing
3. Verify that input files are in `data/input/` directory
4. If using the natural language interface, ensure Ollama is installed and running
5. For dependency issues, try running `pip install -r requirements.txt` in both directories 