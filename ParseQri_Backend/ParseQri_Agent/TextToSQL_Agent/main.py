import sys
import os
import json
import subprocess
import argparse
from pathlib import Path
import time
import requests
import shutil
from typing import Dict, List, Optional, Any
from core.orchestrator import TextSQLOrchestrator
from utils.data_folder_monitor import DataFolderMonitor
import sqlalchemy
from sqlalchemy import inspect, create_engine, text

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed. Using hardcoded defaults.")
    print("Install with: pip install python-dotenv")
    print("Create a .env file with your database configuration.")

# Configuration class to handle environment variables with fallbacks
class Config:
    """Configuration class to handle environment variables with fallbacks"""
    
    # Database Configuration
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '3306'))
    DB_USER: str = os.getenv('DB_USER', 'root')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'root')
    DB_NAME: str = os.getenv('DB_NAME', 'parseqri')
    DB_TYPE: str = os.getenv('DB_TYPE', 'mysql')
    
    # External Database Configuration
    EXTERNAL_DB_HOST: str = os.getenv('EXTERNAL_DB_HOST', 'localhost')
    EXTERNAL_DB_PORT: int = int(os.getenv('EXTERNAL_DB_PORT', '3306'))
    EXTERNAL_DB_USER: str = os.getenv('EXTERNAL_DB_USER', 'root')
    EXTERNAL_DB_PASSWORD: str = os.getenv('EXTERNAL_DB_PASSWORD', 'root')
    EXTERNAL_DB_NAME: str = os.getenv('EXTERNAL_DB_NAME', os.getenv('EXTERNAL_DB_DATABASE', 'your_database'))
    EXTERNAL_DB_TYPE: str = os.getenv('EXTERNAL_DB_TYPE', 'mysql')
    
    # LLM Configuration
    LLM_MODEL_SCHEMA: str = os.getenv('LLM_MODEL_SCHEMA', 'mistral')
    LLM_MODEL_INTENT: str = os.getenv('LLM_MODEL_INTENT', 'llama3.1')
    LLM_MODEL_SQL: str = os.getenv('LLM_MODEL_SQL', 'qwen2.5')
    LLM_MODEL_VALIDATION: str = os.getenv('LLM_MODEL_VALIDATION', 'orca2')
    LLM_MODEL_RESPONSE: str = os.getenv('LLM_MODEL_RESPONSE', 'mistral')
    LLM_MODEL_VISUALIZATION: str = os.getenv('LLM_MODEL_VISUALIZATION', 'llama3.1')
    LLM_MODEL_METADATA: str = os.getenv('LLM_MODEL_METADATA', 'llama3.1')
    LLM_API_BASE: str = os.getenv('LLM_API_BASE', 'http://localhost:11434')
    
    # Paths Configuration
    DATA_FOLDER: str = os.getenv('DATA_FOLDER', '../data/input')
    CHROMA_PERSIST_DIR: str = os.getenv('CHROMA_PERSIST_DIR', '../data/db_storage')
    CACHE_DIR: str = os.getenv('CACHE_DIR', 'cache')
    LOG_FILE: str = os.getenv('LOG_FILE', '../data/query_logs/textsql.log')
    
    # API Configuration
    API_BASE_URL: str = os.getenv('API_BASE_URL', 'http://localhost:8000')
    
    @classmethod
    def get_db_url(cls, use_external: bool = False) -> str:
        """Build database URL from configuration"""
        if use_external:
            host, port, user, password, db_name, db_type = (
                cls.EXTERNAL_DB_HOST, cls.EXTERNAL_DB_PORT, cls.EXTERNAL_DB_USER,
                cls.EXTERNAL_DB_PASSWORD, cls.EXTERNAL_DB_NAME, cls.EXTERNAL_DB_TYPE
            )
        else:
            host, port, user, password, db_name, db_type = (
                cls.DB_HOST, cls.DB_PORT, cls.DB_USER,
                cls.DB_PASSWORD, cls.DB_NAME, cls.DB_TYPE
            )
        
        if db_type == "mysql":
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"
        elif db_type == "postgres":
            return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
        else:
            print(f"Warning: Unsupported database type '{db_type}', defaulting to MySQL")
            return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db_name}"

def get_available_users() -> List[str]:
    """Get available user IDs from storage directory"""
    storage_dir = Path(Config.CHROMA_PERSIST_DIR)
    if not storage_dir.exists():
        return ["default_user"]
    
    users = []
    for item in storage_dir.iterdir():
        if item.is_dir():
            users.append(item.name)
    
    return users if users else ["default_user"]

def get_external_database_config(db_id: Optional[int]) -> Optional[Dict[str, Any]]:
    """Fetch external database configuration directly from database"""
    try:
        if not db_id:
            return None
            
        print(f"Fetching database config for ID: {db_id}")
        
        # Import SQLAlchemy components for direct database access
        from sqlalchemy import create_engine, text
        from sqlalchemy.orm import sessionmaker
        
        # Connect directly to the main ParseQri database to get user database configurations
        # This avoids the HTTP timeout issue
        main_db_url = "mysql+pymysql://root:root@localhost:3306/parseqri"
        
        try:
            engine = create_engine(main_db_url)
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
            
            with SessionLocal() as session:
                # Query the user_databases table directly
                result = session.execute(
                    text("SELECT id, user_id, db_type, host, port, db_name, db_user, db_password FROM user_databases WHERE id = :db_id"),
                    {"db_id": db_id}
                ).fetchone()
                
                if result:
                    db_config = {
                        "id": result[0],
                        "user_id": result[1], 
                        "db_type": result[2],
                        "host": result[3],
                        "port": result[4],
                        "db_name": result[5],
                        "db_user": result[6],
                        "db_password": result[7]
                    }
                    print(f"Successfully fetched database config: {db_config['db_name']} ({db_config['db_type']})")
                    return db_config
                else:
                    print(f"No database configuration found for ID: {db_id}")
                    
        except Exception as e:
            print(f"Error accessing main database: {e}")
        
        # Fallback: Use environment variables if database access fails
        print("Falling back to environment variables for database config")
        return {
            "id": db_id,
            "db_type": Config.EXTERNAL_DB_TYPE,
            "host": Config.EXTERNAL_DB_HOST,
            "port": Config.EXTERNAL_DB_PORT,
            "db_name": Config.EXTERNAL_DB_NAME,
            "db_user": Config.EXTERNAL_DB_USER,
            "db_password": Config.EXTERNAL_DB_PASSWORD
        }
        
    except Exception as e:
        print(f"Error fetching database config: {e}")
        return None

def update_config_for_external_db(config: Dict[str, Any], db_config: Dict[str, Any]) -> Dict[str, Any]:
    """Update agent configuration to use external database"""
    try:
        # Build database URL based on type
        if db_config["db_type"] == "mysql":
            db_url = f"mysql+pymysql://{db_config['db_user']}:{db_config['db_password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
        elif db_config["db_type"] == "postgres":
            db_url = f"postgresql://{db_config['db_user']}:{db_config['db_password']}@{db_config['host']}:{db_config['port']}/{db_config['db_name']}"
        else:
            print(f"Unsupported database type: {db_config['db_type']}")
            return config
        
        # Update all database-related configurations
        if "agents" in config:
            # Update schema understanding agent
            if "schema_understanding" in config["agents"]:
                config["agents"]["schema_understanding"]["params"]["db_url"] = db_url
                config["agents"]["schema_understanding"]["params"]["schema"] = db_config["db_name"]
            
            # Update query execution agent
            if "query_execution" in config["agents"]:
                config["agents"]["query_execution"]["params"]["mysql_url"] = db_url
            
            # Update mysql handler agent
            if "mysql_handler" in config["agents"]:
                config["agents"]["mysql_handler"]["params"]["db_url"] = db_url
                config["agents"]["mysql_handler"]["params"]["schema"] = db_config["db_name"]
        
        # Update database defaults
        if "database" in config:
            config["database"]["default_db_name"] = db_config["db_name"]
        
        print(f"Configuration updated to use external database: {db_config['db_name']}")
        return config
        
    except Exception as e:
        print(f"Error updating config for external database: {e}")
        return config

def get_mysql_tables(user_id: Optional[str] = None) -> List[str]:
    """Get available tables directly from MySQL"""
    try:
        # Priority 1: Environment variables (highest priority)
        if os.getenv('EXTERNAL_DB_ENABLED', '').lower() == 'true' and os.getenv('EXTERNAL_DB_NAME'):
            db_url = Config.get_db_url(use_external=True)
            schema_name = Config.EXTERNAL_DB_NAME
            print(f"Using external database from environment: {Config.EXTERNAL_DB_NAME}")
        else:
            # Priority 2: Configuration file (fallback)
            external_config_path = Path("external_db_config.json")
            use_external_db = external_config_path.exists()
            
            if use_external_db:
                # Load external database configuration
                with external_config_path.open('r') as f:
                    external_config = json.load(f)
                    external_db = external_config.get("external_database", {})
                    
                if external_db.get("enabled", False):
                    db_url = f"mysql+pymysql://{external_db['user']}:{external_db['password']}@{external_db['host']}:{external_db['port']}/{external_db['database']}"
                    schema_name = external_db['database']
                    print(f"Using external database from config file: {external_db['database']}")
                else:
                    db_url = Config.get_db_url()
                    schema_name = Config.DB_NAME
            else:
                # Priority 3: Default internal database
                db_url = Config.get_db_url()
                schema_name = Config.DB_NAME
        
        engine = create_engine(db_url)
        with engine.connect() as conn:
            inspector = inspect(engine)
            all_tables = inspector.get_table_names(schema=schema_name)
            
            if use_external_db:
                # For external databases, return all tables (no user filtering)
                return all_tables
            else:
                # For internal databases, apply user filtering
                if user_id:
                    # Filter tables for specific user
                    tables = [table for table in all_tables if table.startswith(f"{user_id}_")]
                else:
                    # Get all tables with user ID info
                    tables = []
                    user_tables = {}
                    
                    for table in all_tables:
                        parts = table.split("_", 1)
                        if len(parts) > 1:
                            user_id = parts[0]
                            table_name = parts[1]
                            if user_id not in user_tables:
                                user_tables[user_id] = []
                            user_tables[user_id].append(table_name)
                    
                    # Format table info
                    for user, tables_list in user_tables.items():
                        for table in tables_list:
                            tables.append(f"{user}: {table}")
                            
                return tables
            
    except Exception as e:
        print(f"Error connecting to MySQL: {e}")
        return []

def validate_chromadb_collection(user_id: str) -> bool:
    """Validate ChromaDB collection exists and has valid content"""
    try:
        collection_base_path = Path(Config.CHROMA_PERSIST_DIR) / user_id
        
        # Check if the base directory exists
        if not collection_base_path.exists():
            return False
        
        # Check for essential ChromaDB files
        required_files = ['chroma.sqlite3']
        for file_name in required_files:
            if not (collection_base_path / file_name).exists():
                print(f"Missing ChromaDB file: {file_name}")
                return False
        
        # Check if there are any collection directories with valid structure
        collection_dirs = [d for d in collection_base_path.iterdir() if d.is_dir()]
        if not collection_dirs:
            print("No collection directories found")
            return False
        
        # Validate at least one collection has the required files
        for collection_dir in collection_dirs:
            required_collection_files = ['data_level0.bin', 'header.bin', 'length.bin', 'link_lists.bin']
            if all((collection_dir / file_name).exists() for file_name in required_collection_files):
                return True
        
        print("No valid collection structure found")
        return False
        
    except Exception as e:
        print(f"Error validating ChromaDB collection: {e}")
        return False

def initialize_chromadb_collection(user_id: str, force: bool = False) -> bool:
    """Initialize ChromaDB collection for a user from MySQL data"""
    try:
        # First check if there's already valid data for this user in ChromaDB
        if not force and validate_chromadb_collection(user_id):
            print(f"Valid ChromaDB collection already exists for user {user_id}")
            return True
        
        # Clean up corrupted data if force is True
        if force:
            collection_path = Path(Config.CHROMA_PERSIST_DIR) / user_id
            if collection_path.exists():
                print(f"Removing existing ChromaDB data for user {user_id}")
                shutil.rmtree(collection_path)
            
        # Get orchestrator with all agents
        config_path = Path("config.json")
        if not config_path.exists():
            create_default_config(config_path)
            
        orchestrator = TextSQLOrchestrator(str(config_path))
        
        # Get the metadata_indexer agent
        if 'metadata_indexer' not in orchestrator.agents:
            print("Metadata indexer agent not available")
            return False
            
        metadata_indexer = orchestrator.agents['metadata_indexer']
        
        # Get list of tables for this user
        mysql_tables = get_mysql_tables(user_id)
        if not mysql_tables:
            print(f"No MySQL tables found for user {user_id}")
            return False
            
        # For each table, create a metadata entry
        for full_table_name in mysql_tables:
            # Get table name without user prefix
            table_name = full_table_name[len(f"{user_id}_"):]
            
            # Create minimal metadata document
            print(f"Creating metadata entry for table: {table_name}")
            metadata_indexer.save_metadata_to_chroma(
                user_id=user_id,
                table_name=table_name,
                columns={"table": "MySQL table"}  # Placeholder for columns
            )
            
        print(f"Successfully initialized ChromaDB collection for user {user_id}")
        return True
        
    except Exception as e:
        print(f"Error initializing ChromaDB collection: {e}")
        return False

def main():
    """Main entry point for the integrated PDF/Image to SQL query system"""
    # Get available users
    available_users = get_available_users()
    default_user = available_users[0] if available_users else "default_user"
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="ParseQri Text-to-SQL Agent")
    parser.add_argument('query', nargs='?', help='Natural language query to process')
    parser.add_argument('--user', '-u', type=str, default=default_user, 
                      help=f'User ID for multi-user support (available: {", ".join(available_users)})')
    parser.add_argument('--upload', type=str, help='Path to CSV file to upload')
    parser.add_argument('--table', type=str, help='Suggested table name for CSV upload')
    parser.add_argument('--viz', '--visualization', action='store_true', help='Force visualization mode')
    parser.add_argument('--list-tables', action='store_true', help='List available tables for the user')
    parser.add_argument('--list-all-tables', action='store_true', help='List all tables in the database')
    parser.add_argument('--init-chromadb', action='store_true', help='Initialize ChromaDB collection for user')
    parser.add_argument('--db-id', type=int, help='Database ID for API integration')
    
    args = parser.parse_args()
    
    # Validate user ID
    current_user = args.user
    if current_user not in available_users:
        print(f"Warning: User '{current_user}' not found. Available users: {', '.join(available_users)}")
        print(f"Using '{default_user}' instead.")
        current_user = default_user
    
    print(f"Current user: {current_user}")
    
    # Load configuration
    config_path = Path("config.json")
    if not config_path.exists():
        create_default_config(config_path)
    
    # Load the configuration
    with config_path.open('r') as f:
        config = json.load(f)
    
    # If database ID is provided, fetch external database configuration
    if args.db_id:
        external_db_config = get_external_database_config(args.db_id)
        if external_db_config:
            print(f"Using external database: {external_db_config['db_name']} ({external_db_config['db_type']})")
            # Update config to use external database
            config = update_config_for_external_db(config, external_db_config)
            
            # Write updated config to a temporary file
            temp_config_path = Path("config_external.json")
            with temp_config_path.open('w') as f:
                json.dump(config, f, indent=2)
            config_path = temp_config_path
        else:
            print(f"Warning: Could not fetch database config for ID {args.db_id}, using default configuration")
    
    # Initialize the orchestrator
    orchestrator = TextSQLOrchestrator(str(config_path))
    
    # Handle the init-chromadb command
    if args.init_chromadb:
        initialize_chromadb_collection(current_user, force=True)
        return
    
    # Handle the list-all-tables command
    if args.list_all_tables:
        all_tables = get_mysql_tables()
        
        if all_tables:
            print("\nAll tables in MySQL (user: table):")
            for table in all_tables:
                print(f"  - {table}")
        else:
            print("  No MySQL tables found")
            
        return
    
    # Handle the list-tables command
    if args.list_tables:
        # Direct access to the mysql_handler and metadata_indexer agents
        if 'mysql_handler' in orchestrator.agents and 'metadata_indexer' in orchestrator.agents:
            mysql_handler = orchestrator.agents['mysql_handler']
            metadata_indexer = orchestrator.agents['metadata_indexer']
            
            # Get tables from MySQL
            tables = mysql_handler.list_user_tables(current_user)
            
            # Get tables from ChromaDB
            try:
                metadata_tables = metadata_indexer.list_user_tables(current_user)
            except Exception as e:
                print(f"Warning: Unable to get tables from ChromaDB: {e}")
                metadata_tables = []
            
            print(f"\nTables available for user {current_user}:")
            if tables:
                print("\nMySQL Tables:")
                for table in tables:
                    # Show table name without user prefix for clarity
                    if table.startswith(f"{current_user}_"):
                        display_name = table[len(f"{current_user}_"):]
                    else:
                        display_name = table
                    print(f"  - {display_name} (full name: {table})")
            else:
                print("  No MySQL tables found")
                
            if metadata_tables:
                print("\nMetadata Indexed Tables:")
                for table in metadata_tables:
                    print(f"  - {table['table_name']} ({table['column_count']} columns)")
            else:
                print("  No metadata indexed tables found")
                
            # If no ChromaDB metadata, offer to initialize it
            if tables and not metadata_tables:
                print("\nNo ChromaDB metadata found but MySQL tables exist.")
                print("You can initialize the ChromaDB collection with:")
                print(f"  python main.py --init-chromadb --user {current_user}")
            
            return
    
    # Handle file upload
    if args.upload:
        upload_path = Path(args.upload)
        print(f"Uploading file: {upload_path} for user: {current_user}")
        
        if not upload_path.exists():
            print(f"Error: File not found: {upload_path}")
            return
            
        print("File exists, proceeding with upload")
        
        # Process CSV upload
        table_name = args.table or upload_path.stem
        print(f"Using table name: {table_name}")
        
        # Check if metadata_indexer is available
        if 'metadata_indexer' in orchestrator.agents:
            print("Metadata indexer agent is available")
            metadata_indexer = orchestrator.agents['metadata_indexer']
        else:
            print("WARNING: Metadata indexer agent is NOT available")
        
        context = orchestrator.process_upload(
            csv_file=str(upload_path),
            user_id=current_user,
            suggested_table_name=table_name,
            db_id=args.db_id
        )
        
        # Display results
        if hasattr(context, 'table_name') and context.table_name:
            print(f"\nSuccessfully uploaded data to table: {context.table_name}")
            print("You can now query this data with:")
            print(f"  python main.py \"your question about the data\" --user {current_user}")
        else:
            print("\nError uploading data. Check the logs for more information.")
            
        return
    
    # Check if PDF/image processing is needed
    pdf_processing_needed = check_for_pdfs_or_images()

    if pdf_processing_needed:
        print("Found new PDF or image files to process")
        # Step 1: Run the conversion tool to convert PDF/images to CSV
        print("\nStep 1: Converting PDF/images to CSV...")
        try:
            # Ensure the input directory exists in conversion_tool
            conversion_pdfs_path = Path("../conversion_tool/pdfs")
            conversion_pdfs_path.mkdir(exist_ok=True)
            
            # Copy the files from data/input to conversion_tool/pdfs
            copy_input_files()
            
            # Get the current Python interpreter path
            python_executable = sys.executable
            print(f"Using Python interpreter: {python_executable}")
            
            # Run the conversion tool
            conversion_result = subprocess.run(
                [python_executable, "../conversion_tool/main.py"],
                cwd="../conversion_tool",
                capture_output=True, 
                text=True
            )
            
            if conversion_result.returncode != 0:
                print("Error running conversion tool:")
                print(conversion_result.stderr)
                return
                
            print("Conversion completed successfully")
            
            # Step 2: Copy the CSV output to our data directory
            print("\nStep 2: Copying CSV output to data directory...")
            csv_output_path = Path("../data/csv_output")
            csv_output_path.mkdir(exist_ok=True)
            
            # Copy the CSV file from conversion_tool/csv_output to data/csv_output
            copy_csv_files()
            
        except Exception as e:
            print(f"Error during PDF/image conversion: {str(e)}")
            return
    
    # Step 3: If CSV files are present, process and ingest them 
    # This is now handled by the upload argument, but we keep this for backward compatibility
    if not args.query and not args.upload and not args.list_tables:
        print("\nNo query or upload operation provided.")
        print("You can:")
        print("- Run a query with: python main.py 'Your query' --user <user_id>")
        print("- Upload a CSV with: python main.py --upload path/to/file.csv --user <user_id>")
        print("- List tables with: python main.py --list-tables --user <user_id>")
        print("\nExiting...")
        return
    
    # Step 4: Process query if provided
    if args.query:
        user_question = args.query
        print(f"\nProcessing query: {user_question}")
        
        # Check for visualization flag
        force_visualization = args.viz
        
        # Get the user's database path - dynamically based on user ID
        user_db_path = Path(Config.CHROMA_PERSIST_DIR) / current_user
        
        # Check if ChromaDB needs initialization
        if not validate_chromadb_collection(current_user):
            print(f"ChromaDB collection not found or invalid for user {current_user}, attempting to initialize...")
            initialize_chromadb_collection(current_user)
        
        # Process query with user_id
        context = orchestrator.process_query(
            user_question, 
            str(user_db_path) if user_db_path.exists() else "", # Use empty string if path doesn't exist
            "",  # Table name will be determined by metadata lookup
            user_id=current_user,
            force_visualization=force_visualization
        )
        
        # Display results
        if context.needs_visualization:
            print("\nVisualization response:")
            if context.visualization_data and 'html_path' in context.visualization_data:
                html_path = Path(context.visualization_data['html_path'])
                
                # Create a clickable file:// URL for the terminal
                file_url = f"file:///{html_path.resolve().as_posix()}"
                
                print(f"\nVisualization saved. Click this link to view: {file_url}")
                print("The visualization should open automatically in your default browser.")
                print("If it doesn't open, please click on the link above.")
            else:
                print(f"Visualization data: {context.visualization_data}")
        else:
            print("\nSQL Query:")
            print(context.sql_query)
            print("\nResponse:")
            print(context.formatted_response)

def check_for_pdfs_or_images() -> bool:
    """Check if there are PDF or image files in the input directory"""
    input_dir = Path(Config.DATA_FOLDER)
    
    if not input_dir.exists():
        return False
        
    pdf_files = list(input_dir.glob("*.pdf"))
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"]:
        image_files.extend(list(input_dir.glob(ext)))
    
    return len(pdf_files) > 0 or len(image_files) > 0

def copy_input_files():
    """Copy files from data/input to conversion_tool/pdfs using shutil.copy2"""
    input_dir = Path(Config.DATA_FOLDER)
    output_dir = Path("../conversion_tool/pdfs")
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    try:
        # Copy PDF files
        pdf_files = list(input_dir.glob("*.pdf"))
        for pdf_file in pdf_files:
            target_path = output_dir / pdf_file.name
            shutil.copy2(pdf_file, target_path)
            print(f"Copied {pdf_file.name} to conversion tool")
        
        # Copy image files
        image_extensions = ["*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"]
        for ext in image_extensions:
            image_files = list(input_dir.glob(ext))
            for img_file in image_files:
                target_path = output_dir / img_file.name
                shutil.copy2(img_file, target_path)
                print(f"Copied {img_file.name} to conversion tool")
                
    except Exception as e:
        print(f"Error copying input files: {e}")
        raise

def copy_csv_files():
    """Copy CSV files from conversion_tool/csv_output to data/csv_output using shutil.copy2"""
    conversion_output = Path("../conversion_tool/csv_output")
    data_dir = Path("../data/csv_output")
    
    # Ensure data directory exists
    data_dir.mkdir(exist_ok=True)
    
    try:
        # Copy all CSV files
        csv_files = list(conversion_output.glob("*.csv"))
        for csv_file in csv_files:
            target_path = data_dir / csv_file.name
            shutil.copy2(csv_file, target_path)
            print(f"Copied {csv_file.name} to data/csv_output")
            
    except Exception as e:
        print(f"Error copying CSV files: {e}")
        raise

def create_default_config(config_path: Path):
    """Create a default configuration file if none exists"""
    default_config = {
        "agents": {
            "data_ingestion": {
                "module": "agents.data_ingestion",
                "class": "DataIngestionAgent",
                "params": {}
            },
            "schema_understanding": {
                "module": "agents.schema_understanding",
                "class": "SchemaUnderstandingAgent",
                "params": {
                    "llm_model": Config.LLM_MODEL_SCHEMA,
                    "api_base": Config.LLM_API_BASE
                }
            },
            "intent_classifier": {
                "module": "agents.intent_classification",
                "class": "IntentClassificationAgent",
                "params": {
                    "llm_model": Config.LLM_MODEL_INTENT,
                    "api_base": Config.LLM_API_BASE
                }
            },
            "sql_generation": {
                "module": "agents.sql_generation",
                "class": "SQLGenerationAgent",
                "params": {
                    "llm_model": Config.LLM_MODEL_SQL,
                    "api_base": Config.LLM_API_BASE
                }
            },
            "sql_validation": {
                "module": "agents.sql_validation",
                "class": "SQLValidationAgent",
                "params": {
                    "llm_model": Config.LLM_MODEL_VALIDATION,
                    "api_base": Config.LLM_API_BASE
                }
            },
            "query_execution": {
                "module": "agents.query_execution",
                "class": "QueryExecutionAgent",
                "params": {
                    "mysql_url": Config.get_db_url()
                }
            },
            "response_formatting": {
                "module": "agents.response_formatting",
                "class": "ResponseFormattingAgent",
                "params": {
                    "llm_model": Config.LLM_MODEL_RESPONSE,
                    "api_base": Config.LLM_API_BASE
                }
            },
            "visualization": {
                "module": "agents.visualization",
                "class": "VisualizationAgent",
                "params": {
                    "llm_model": Config.LLM_MODEL_VISUALIZATION,
                    "api_base": Config.LLM_API_BASE
                }
            },
            "data_preprocessing": {
                "module": "agents.data_preprocessing",
                "class": "DataPreprocessingAgent",
                "params": {}
            },
            "query_cache": {
                "module": "agents.query_cache",
                "class": "QueryCacheAgent",
                "params": {
                    "cache_dir": Config.CACHE_DIR
                }
            },
            "schema_management": {
                "module": "agents.schema_management",
                "class": "SchemaManagementAgent",
                "params": {}
            },
            "advanced_visualization": {
                "module": "agents.advanced_visualization",
                "class": "AdvancedVisualizationAgent",
                "params": {}
            },
            "metadata_indexer": {
                "module": "agents.metadata_indexer",
                "class": "MetadataIndexerAgent",
                "params": {
                    "llm_model": Config.LLM_MODEL_METADATA,
                    "api_base": Config.LLM_API_BASE,
                    "chroma_persist_dir": Config.CHROMA_PERSIST_DIR
                }
            },
            "mysql_handler": {
                "module": "agents.mysql_handler",
                "class": "MySQLHandlerAgent",
                "params": {
                    "db_url": Config.get_db_url(),
                    "schema": Config.DB_NAME
                }
            },
            "query_router": {
                "module": "agents.query_router",
                "class": "QueryRouterAgent",
                "params": {}
            }
        },
        "database": {
            "default_db_name": "",  # This will be determined dynamically
            "default_table_name": "",  # This will be determined dynamically
            "data_folder": Config.DATA_FOLDER,
            "mysql": {
                "db_url": Config.get_db_url(),
                "schema": Config.DB_NAME
            }
        },
        "logging": {
            "level": "INFO",
            "file": Config.LOG_FILE
        }
    }
    
    with config_path.open('w') as f:
        json.dump(default_config, f, indent=2)
    
    print(f"Created default configuration file: {config_path}")

if __name__ == "__main__":
    main() 