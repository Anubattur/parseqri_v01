from typing import Any, Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine, MetaData, Table, Column, inspect
from sqlalchemy.types import Integer, String, Float, Boolean
from app.core.exceptions import SchemaGenerationError, DataInsertionError
from app.db.connectors import DatabaseConnectorFactory, MySQLConnector, PostgresConnector, MongoDBConnector
from app.schemas.db import DBConfigOut
from app.schemas.data import SchemaMetadata
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sql_type(type_name: str) -> Any:
    type_map = {
        "Integer": Integer,
        "String": String,
        "Float": Float,
        "Boolean": Boolean
    }
    return type_map.get(type_name, String)

def infer_sql_type(dtype: str) -> Any:
    if pd.api.types.is_integer_dtype(dtype):
        return Integer
    elif pd.api.types.is_float_dtype(dtype):
        return Float
    elif pd.api.types.is_bool_dtype(dtype):
        return Boolean
    else:
        return String

def clean_column_name(name: str) -> str:
    """Clean column name to make it SQL-compliant."""
    # Replace spaces and special characters with underscores
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Convert to lowercase for consistency
    cleaned = cleaned.lower()
    # Ensure it's not empty
    if not cleaned:
        cleaned = 'column'
    return cleaned

class UniversalSchemaManager:
    """
    Universal schema manager that works with MySQL, PostgreSQL, and MongoDB.
    """
    
    # Mapping from pandas dtypes to SQL data types
    MYSQL_TYPE_MAPPING = {
        'int64': 'INT',
        'float64': 'DOUBLE',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'DATETIME',
        'timedelta64[ns]': 'TIME',
        'object': 'TEXT',
        'category': 'VARCHAR(255)',
        'string': 'TEXT'
    }
    
    POSTGRES_TYPE_MAPPING = {
        'int64': 'INTEGER',
        'float64': 'DOUBLE PRECISION',
        'bool': 'BOOLEAN',
        'datetime64[ns]': 'TIMESTAMP',
        'timedelta64[ns]': 'INTERVAL',
        'object': 'TEXT',
        'category': 'TEXT',
        'string': 'TEXT'
    }
    
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.db_type = self._detect_db_type()
        self.schema_cache = {}
    
    def _detect_db_type(self):
        """Detect the database type from the connector."""
        if isinstance(self.db_connector, MySQLConnector):
            return 'mysql'
        elif isinstance(self.db_connector, PostgresConnector):
            return 'postgres'
        elif isinstance(self.db_connector, MongoDBConnector):
            return 'mongodb'
        else:
            # Default to mysql for backward compatibility
            return 'mysql'
    
    def _get_type_mapping(self):
        """Get the appropriate type mapping for the database."""
        if self.db_type == 'mysql':
            return self.MYSQL_TYPE_MAPPING
        elif self.db_type == 'postgres':
            return self.POSTGRES_TYPE_MAPPING
        else:
            return self.MYSQL_TYPE_MAPPING  # Default
    
    def infer_schema_from_csv(self, csv_path: str, sample_size: int = 1000) -> Dict[str, str]:
        """
        Infers schema from a CSV file.
        
        Args:
            csv_path: Path to the CSV file
            sample_size: Number of rows to sample for type inference
            
        Returns:
            Dictionary mapping column names to their SQL data types
        """
        try:
            # Read a sample of the CSV file
            df = pd.read_csv(csv_path, nrows=sample_size)
            
            # Get the appropriate type mapping
            type_mapping = self._get_type_mapping()
            
            # Infer schema from DataFrame
            schema = {}
            for col_name, dtype in df.dtypes.items():
                # Clean column name (remove special characters and spaces)
                clean_col_name = clean_column_name(col_name)
                
                # Map pandas dtype to SQL type
                sql_type = type_mapping.get(str(dtype), 'TEXT' if self.db_type == 'postgres' else 'VARCHAR(255)')
                
                # Check for date/time columns
                if 'date' in col_name.lower() or 'time' in col_name.lower():
                    # Try to convert to datetime
                    try:
                        df[col_name] = pd.to_datetime(df[col_name])
                        sql_type = 'TIMESTAMP' if self.db_type == 'postgres' else 'DATETIME'
                    except:
                        pass
                
                schema[clean_col_name] = sql_type
            
            return schema
        except Exception as e:
            logger.error(f"Error inferring schema from CSV: {e}")
            raise
    
    def create_table_from_schema(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Creates a new table using the provided schema.
        
        Args:
            table_name: Name of the table to create
            schema: Dictionary mapping column names to SQL data types
        """
        try:
            if self.db_type == 'mongodb':
                # For MongoDB, we don't need to create tables explicitly
                logger.info(f"MongoDB collection '{table_name}' will be created automatically on first insert")
                return
            
            # Create the table if it doesn't exist
            if self.db_type == 'mysql':
                column_defs = [f"`{col_name}` {data_type}" for col_name, data_type in schema.items()]
                query = f"""
                CREATE TABLE IF NOT EXISTS `{table_name}` (
                    {', '.join(column_defs)}
                );
                """
            else:  # PostgreSQL
                column_defs = [f'"{col_name}" {data_type}' for col_name, data_type in schema.items()]
                query = f"""
                CREATE TABLE IF NOT EXISTS "{table_name}" (
                    {', '.join(column_defs)}
                );
                """
            
            self.db_connector.execute_query(query)
            
            # Cache the schema for this table
            self.schema_cache[table_name] = schema
            
            logger.info(f"Created table '{table_name}' with schema: {schema}")
        except Exception as e:
            logger.error(f"Error creating table from schema: {e}")
            raise
    
    def load_csv_to_table(self, table_name: str, csv_path: str, 
                           create_if_not_exists: bool = True,
                           batch_size: int = 1000) -> int:
        """
        Loads data from a CSV file into a table.
        
        Args:
            table_name: Name of the target table
            csv_path: Path to the CSV file
            create_if_not_exists: If True, creates the table if it doesn't exist
            batch_size: Number of rows to insert at once
            
        Returns:
            Number of rows inserted
        """
        try:
            # If needed, infer schema and create table
            if create_if_not_exists:
                schema = self.infer_schema_from_csv(csv_path)
                self.create_table_from_schema(table_name, schema)
            
            # Read CSV in chunks and insert
            total_rows = 0
            for chunk in pd.read_csv(csv_path, chunksize=batch_size):
                # Clean column names
                chunk.columns = [clean_column_name(col) for col in chunk.columns]
                
                # Handle NaN values - replace with None for MySQL compatibility
                chunk = chunk.replace({np.nan: None})
                
                # Also handle inf and -inf values
                chunk = chunk.replace([np.inf, -np.inf], None)
                
                # Convert to list of dictionaries
                records = chunk.to_dict('records')
                
                # Insert data
                if records:
                    if self.db_type == 'mongodb':
                        # For MongoDB, use collection insert
                        collection = self.db_connector.database[table_name]
                        collection.insert_many(records)
                    else:
                        # For SQL databases
                        self.db_connector.insert_data(table_name, records)
                    
                    total_rows += len(records)
                    logger.info(f"Inserted {len(records)} rows into table '{table_name}'")
            
            logger.info(f"Total {total_rows} rows loaded from {csv_path} to table '{table_name}'")
            return total_rows
        except Exception as e:
            logger.error(f"Error loading CSV to table: {e}")
            raise
    
    def get_table_metadata(self, table_name: str) -> Dict[str, Any]:
        """
        Retrieves metadata for a table, including column names, types, etc.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with table metadata compatible with SchemaMetadata
        """
        try:
            # Try to get column info using the connector
            try:
                if self.db_type == 'mongodb':
                    column_info = self.db_connector.get_collection_schema(table_name)
                else:
                    column_info = self.db_connector.get_table_schema(table_name)
            except Exception as e:
                logger.error(f"Error getting column info from database: {e}")
                
                # Fall back to using the cached schema if we have it
                if table_name in self.schema_cache:
                    logger.info(f"Using cached schema for table '{table_name}'")
                    # Convert cached schema to column info format
                    column_info = []
                    for col_name, data_type in self.schema_cache[table_name].items():
                        column_info.append({
                            "column_name": col_name,
                            "data_type": data_type,
                            "is_nullable": "YES",
                            "column_default": None
                        })
                else:
                    # Raise error if we can't get column info
                    raise
            
            # Create a metadata dictionary that matches SchemaMetadata format
            metadata = {
                "table_name": table_name,
                "columns": [
                    {
                        "name": col.get("column_name"),
                        "type": col.get("data_type")
                    } for col in column_info
                ]
            }
            
            # Cache this schema
            self.schema_cache[table_name] = {
                col.get("column_name"): col.get("data_type") for col in column_info
            }
            
            return metadata
        except Exception as e:
            logger.error(f"Error getting table metadata: {e}")
            raise
    
    def get_database_metadata(self) -> Dict[str, Any]:
        """
        Retrieves metadata for all tables in the database.
        
        Returns:
            Dictionary with database metadata
        """
        try:
            if self.db_type == 'mongodb':
                tables = self.db_connector.list_collections()
            else:
                tables = self.db_connector.list_tables()
            
            metadata = {
                "tables": {}
            }
            
            for table in tables:
                metadata["tables"][table] = self.get_table_metadata(table)
            
            return metadata
        except Exception as e:
            logger.error(f"Error getting database metadata: {e}")
            raise
            
    def create_table_from_csv(self, table_name: str, csv_path: str) -> Dict[str, Any]:
        """
        Creates a table from a CSV file and loads the data into it.
        
        This method combines infer_schema_from_csv, create_table_from_schema, and load_csv_to_table.
        
        Args:
            table_name: Name of the table to create
            csv_path: Path to the CSV file
            
        Returns:
            Dictionary with table metadata
        """
        try:
            # Infer schema from CSV
            schema = self.infer_schema_from_csv(csv_path)
            
            # Create table using the schema
            self.create_table_from_schema(table_name, schema)
            
            # Load data into the table
            rows_loaded = self.load_csv_to_table(table_name, csv_path, create_if_not_exists=False)
            
            # Get and return table metadata
            metadata = self.get_table_metadata(table_name)
            
            # Add information about the loaded data
            metadata["rows_loaded"] = rows_loaded
            
            return metadata
        except Exception as e:
            logger.error(f"Error creating table from CSV: {e}")
            raise
    
    def get_schema_metadata(self, table_name: str) -> Dict[str, Any]:
        """
        Gets metadata for a specific table schema
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary containing table metadata
        """
        try:
            return self.get_table_metadata(table_name)
        except Exception as e:
            logger.error(f"Error getting schema metadata for table {table_name}: {e}")
            return {}

    def get_all_tables(self) -> List[str]:
        """
        Get all table names in the database
        
        Returns:
            List of table names
        """
        try:
            if self.db_type == 'mongodb':
                # For MongoDB, get all collection names
                query = "db.listCollections()"  # This would need to be handled by the connector
                result = self.db_connector.execute_query(query)
                return [doc['name'] for doc in result]
            else:
                # For SQL databases
                if self.db_type == 'mysql':
                    query = "SHOW TABLES"
                elif self.db_type == 'postgres':
                    query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                else:
                    query = "SHOW TABLES"  # Default to MySQL syntax
                
                result = self.db_connector.execute_query(query)
                
                if isinstance(result, list) and result:
                    # Handle different result formats
                    if isinstance(result[0], tuple):
                        return [row[0] for row in result]
                    elif isinstance(result[0], dict):
                        # For MySQL, the column might be named differently
                        if self.db_type == 'mysql':
                            # MySQL SHOW TABLES returns results with a dynamic column name
                            first_key = list(result[0].keys())[0]
                            return [row[first_key] for row in result]
                        else:
                            return [row['table_name'] for row in result]
                    else:
                        return [str(row) for row in result]
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting all tables: {e}")
            return []

# For backwards compatibility
SchemaManager = UniversalSchemaManager
PostgresSchemaManager = UniversalSchemaManager