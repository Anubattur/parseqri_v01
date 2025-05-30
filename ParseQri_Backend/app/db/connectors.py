from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import psycopg2
from app.core.exceptions import DatabaseConnectionError, DataInsertionError
from app.schemas.db import DBConfigOut
import os

class PostgresConnector:
    def __init__(self, config: DBConfigOut):
        self.config = config
        self.connection = None
        self.engine = None
        # Always connect immediately on initialization
        self.connect()

    def connect(self) -> None:
        """
        Establishes a connection to the PostgreSQL database.
        Creates the database if it doesn't exist.
        """
        try:
            # First try to connect to the default 'postgres' database to check if our target database exists
            try:
                # Connect to default postgres database
                temp_conn = psycopg2.connect(
                    user=self.config.db_user,
                    password=self.config.db_password,
                    host=self.config.host,
                    port=self.config.port,
                    database="postgres"
                )
                temp_conn.autocommit = True
                cursor = temp_conn.cursor()
                
                # Check if the database exists
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.config.db_name}'")
                exists = cursor.fetchone()
                
                # If it doesn't exist, create it
                if not exists:
                    print(f"Creating PostgreSQL database: {self.config.db_name}")
                    cursor.execute(f"CREATE DATABASE {self.config.db_name}")
                
                cursor.close()
                temp_conn.close()
            except Exception as e:
                print(f"Warning: Could not check or create database: {str(e)}")
            
            # Now connect to the target database
            self.engine = create_engine(
                f"postgresql://{self.config.db_user}:{self.config.db_password}@{self.config.host}:{self.config.port}/{self.config.db_name}"
            )
            self.connection = self.engine.connect()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Executes an SQL query on the PostgreSQL database.
        
        Args:
            query: The SQL query to execute
            params: Query parameters
        """
        if not self.connection:
            self.connect()
        try:
            # In SQLAlchemy 1.4, begin a transaction explicitly
            with self.connection.begin():
                self.connection.execute(text(query), params or {})
                # No need to commit, the transaction context manager handles it
        except Exception as e:
            raise DatabaseConnectionError(f"Query execution failed: {str(e)}")
    
    def fetch_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Executes a query and returns the results.
        
        Args:
            query: The SQL query to execute
            params: Query parameters
            
        Returns:
            A list of dictionaries containing the query results
        """
        if not self.connection:
            self.connect()
        try:
            result = self.connection.execute(text(query), params or {})
            # Fixed: Convert row objects to dictionaries properly
            return [dict(zip(row.keys(), row)) for row in result]
        except Exception as e:
            raise DatabaseConnectionError(f"Query execution failed: {str(e)}")

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """
        Inserts data into a table.
        
        Args:
            table: The table to insert data into
            data: A list of dictionaries with column names as keys
        """
        if not self.connection:
            self.connect()
        try:
            if not data:
                return
                
            keys = data[0].keys()
            columns = ", ".join(keys)
            placeholders = ", ".join([f":{key}" for key in keys])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            # Use transaction context manager
            with self.connection.begin():
                for row in data:
                    self.connection.execute(text(query), row)
                # No need to commit, the transaction context manager handles it
        except Exception as e:
            raise DataInsertionError(f"Data insertion failed: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves schema information for a specified table.
        
        Args:
            table_name: The name of the table
            
        Returns:
            A list of dictionaries with column information
        """
        # Modified query with proper column names and aliases
        query = """
            SELECT 
                column_name AS column_name, 
                data_type AS data_type, 
                is_nullable AS is_nullable,
                column_default AS column_default
            FROM 
                information_schema.columns
            WHERE 
                table_name = :table_name
            ORDER BY 
                ordinal_position;
        """
        try:
            return self.fetch_query(query, {"table_name": table_name})
        except Exception as e:
            # Fall back to a direct psycopg2 implementation if the SQLAlchemy approach fails
            try:
                # Connect directly with psycopg2
                conn = psycopg2.connect(
                    user=self.config.db_user,
                    password=self.config.db_password,
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.db_name
                )
                cursor = conn.cursor()
                
                # Execute query
                cursor.execute(
                    """
                    SELECT 
                        column_name, 
                        data_type, 
                        is_nullable,
                        column_default
                    FROM 
                        information_schema.columns
                    WHERE 
                        table_name = %s
                    ORDER BY 
                        ordinal_position;
                    """, 
                    (table_name,)
                )
                
                # Get columns names from cursor description
                columns = [desc[0] for desc in cursor.description]
                
                # Fetch all rows and convert to dictionaries
                rows = cursor.fetchall()
                result = []
                for row in rows:
                    result.append({
                        "column_name": row[0],
                        "data_type": row[1],
                        "is_nullable": row[2],
                        "column_default": row[3]
                    })
                
                cursor.close()
                conn.close()
                return result
            except Exception as fallback_error:
                raise DatabaseConnectionError(f"Failed to get table schema (both methods): {str(e)} | {str(fallback_error)}")
    
    def list_tables(self) -> List[str]:
        """
        Lists all tables in the current database.
        
        Returns:
            A list of table names
        """
        try:
            query = """
                SELECT 
                    table_name 
                FROM 
                    information_schema.tables 
                WHERE 
                    table_schema='public' 
                ORDER BY 
                    table_name;
            """
            result = self.fetch_query(query)
            return [row["table_name"] for row in result]
        except Exception as e:
            # Fallback to direct psycopg2 if SQLAlchemy approach fails
            try:
                # Connect directly with psycopg2
                conn = psycopg2.connect(
                    user=self.config.db_user,
                    password=self.config.db_password,
                    host=self.config.host,
                    port=self.config.port,
                    database=self.config.db_name
                )
                cursor = conn.cursor()
                
                # Execute query
                cursor.execute(
                    """
                    SELECT 
                        table_name 
                    FROM 
                        information_schema.tables 
                    WHERE 
                        table_schema='public' 
                    ORDER BY 
                        table_name;
                    """
                )
                
                # Fetch all rows
                tables = [row[0] for row in cursor.fetchall()]
                
                cursor.close()
                conn.close()
                return tables
            except Exception as fallback_error:
                raise DatabaseConnectionError(f"Failed to list tables (both methods): {str(e)} | {str(fallback_error)}")

    def close(self) -> None:
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            if self.engine:
                self.engine.dispose()
            self.connection = None

# For backwards compatibility with existing code
DatabaseConnector = PostgresConnector 