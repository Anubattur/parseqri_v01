from typing import Any, Dict, List, Optional
from sqlalchemy import create_engine, text
from sqlalchemy.sql import text
import mysql.connector
import psycopg2
import pymongo
from app.core.exceptions import DatabaseConnectionError, DataInsertionError
from app.schemas.db import DBConfigOut, DBType
import os
import chromadb
from sentence_transformers import SentenceTransformer

class ChromaDBManager:
    """Centralized ChromaDB manager for all users and data sources"""
    
    def __init__(self, persist_dir: str = "./data/chroma_storage"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
    def get_collection(self, collection_name: str = "unified_metadata"):
        """Get or create a unified collection for all metadata"""
        try:
            collection = self.client.get_collection(collection_name)
        except:
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        return collection
    
    def store_table_metadata(self, user_id: int, source_type: str, source_name: str, 
                           table_name: str, schema_info: Dict[str, Any]):
        """Store table metadata in ChromaDB with user context"""
        collection = self.get_collection()
        
        # Create metadata document
        metadata_text = f"""
        Table: {table_name}
        Source: {source_name} ({source_type})
        User: {user_id}
        Columns: {', '.join([f"{col['column_name']} ({col['data_type']})" for col in schema_info.get('columns', [])])}
        Description: Table from {source_type} database containing {len(schema_info.get('columns', []))} columns
        """
        
        # Generate embedding
        embedding = self.encoder.encode(metadata_text).tolist()
        
        # Store in ChromaDB
        doc_id = f"{user_id}_{source_type}_{source_name}_{table_name}"
        collection.upsert(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[metadata_text],
            metadatas=[{
                "user_id": str(user_id),
                "source_type": source_type,
                "source_name": source_name,
                "table_name": table_name,
                "column_count": len(schema_info.get('columns', []))
            }]
        )
    
    def search_relevant_tables(self, user_id: int, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant tables based on query"""
        collection = self.get_collection()
        
        # Generate query embedding
        query_embedding = self.encoder.encode(query).tolist()
        
        # Search ChromaDB
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=limit,
            where={"user_id": str(user_id)}
        )
        
        return results

class MySQLConnector:
    def __init__(self, config: DBConfigOut):
        self.config = config
        self.connection = None
        self.engine = None
        self.connect()

    def connect(self) -> None:
        """Establishes a connection to the MySQL database."""
        try:
            # Create database if it doesn't exist
            temp_conn = mysql.connector.connect(
                user=self.config.db_user,
                password=self.config.db_password,
                host=self.config.host,
                port=self.config.port
            )
            cursor = temp_conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.config.db_name}")
            cursor.close()
            temp_conn.close()
            
            # Connect to the target database
            self.engine = create_engine(
                f"mysql+pymysql://{self.config.db_user}:{self.config.db_password}@{self.config.host}:{self.config.port}/{self.config.db_name}"
            )
            self.connection = self.engine.connect()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to MySQL: {str(e)}")

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Executes an SQL query on the MySQL database."""
        if not self.connection:
            self.connect()
        try:
            with self.connection.begin():
                self.connection.execute(text(query), params or {})
        except Exception as e:
            raise DatabaseConnectionError(f"Query execution failed: {str(e)}")
    
    def fetch_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes a query and returns the results."""
        if not self.connection:
            self.connect()
        try:
            result = self.connection.execute(text(query), params or {})
            # Fix for SQLAlchemy result handling - properly convert to list of dicts
            columns = list(result.keys())
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            raise DatabaseConnectionError(f"Query execution failed: {str(e)}")

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Inserts data into a table."""
        if not self.connection:
            self.connect()
        try:
            if not data:
                return
                
            keys = data[0].keys()
            columns = ", ".join(keys)
            placeholders = ", ".join([f":{key}" for key in keys])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            with self.connection.begin():
                for row in data:
                    self.connection.execute(text(query), row)
        except Exception as e:
            raise DataInsertionError(f"Data insertion failed: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Retrieves schema information for a specified table."""
        query = """
            SELECT 
                COLUMN_NAME as column_name,
                DATA_TYPE as data_type,
                IS_NULLABLE as is_nullable,
                COLUMN_DEFAULT as column_default
            FROM 
                INFORMATION_SCHEMA.COLUMNS
            WHERE 
                TABLE_NAME = :table_name AND TABLE_SCHEMA = :schema
            ORDER BY 
                ORDINAL_POSITION;
        """
        try:
            return self.fetch_query(query, {"table_name": table_name, "schema": self.config.db_name})
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to get table schema: {str(e)}")
    
    def list_tables(self) -> List[str]:
        """Lists all tables in the current database."""
        try:
            query = """
                SELECT 
                    TABLE_NAME as table_name
                FROM 
                    INFORMATION_SCHEMA.TABLES 
                WHERE 
                    TABLE_SCHEMA = :schema
                ORDER BY 
                    TABLE_NAME;
            """
            result = self.fetch_query(query, {"schema": self.config.db_name})
            return [row["table_name"] for row in result]
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to list tables: {str(e)}")

    def close(self) -> None:
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            if self.engine:
                self.engine.dispose()
            self.connection = None

class PostgresConnector:
    def __init__(self, config: DBConfigOut):
        self.config = config
        self.connection = None
        self.engine = None
        self.connect()

    def connect(self) -> None:
        """Establishes a connection to the PostgreSQL database."""
        try:
            # Create database if it doesn't exist
            try:
                temp_conn = psycopg2.connect(
                    user=self.config.db_user,
                    password=self.config.db_password,
                    host=self.config.host,
                    port=self.config.port,
                    database="postgres"
                )
                temp_conn.autocommit = True
                cursor = temp_conn.cursor()
                
                cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{self.config.db_name}'")
                exists = cursor.fetchone()
                
                if not exists:
                    cursor.execute(f"CREATE DATABASE {self.config.db_name}")
                
                cursor.close()
                temp_conn.close()
            except Exception as e:
                print(f"Warning: Could not check or create database: {str(e)}")
            
            # Connect to the target database
            self.engine = create_engine(
                f"postgresql://{self.config.db_user}:{self.config.db_password}@{self.config.host}:{self.config.port}/{self.config.db_name}"
            )
            self.connection = self.engine.connect()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to PostgreSQL: {str(e)}")

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> None:
        """Executes an SQL query on the PostgreSQL database."""
        if not self.connection:
            self.connect()
        try:
            with self.connection.begin():
                self.connection.execute(text(query), params or {})
        except Exception as e:
            raise DatabaseConnectionError(f"Query execution failed: {str(e)}")
    
    def fetch_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes a query and returns the results."""
        if not self.connection:
            self.connect()
        try:
            result = self.connection.execute(text(query), params or {})
            # Fix for SQLAlchemy result handling - properly convert to list of dicts
            columns = list(result.keys())
            rows = result.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            raise DatabaseConnectionError(f"Query execution failed: {str(e)}")

    def insert_data(self, table: str, data: List[Dict[str, Any]]) -> None:
        """Inserts data into a table."""
        if not self.connection:
            self.connect()
        try:
            if not data:
                return
                
            keys = data[0].keys()
            columns = ", ".join(keys)
            placeholders = ", ".join([f":{key}" for key in keys])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            with self.connection.begin():
                for row in data:
                    self.connection.execute(text(query), row)
        except Exception as e:
            raise DataInsertionError(f"Data insertion failed: {str(e)}")
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Retrieves schema information for a specified table."""
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
            raise DatabaseConnectionError(f"Failed to get table schema: {str(e)}")
    
    def list_tables(self) -> List[str]:
        """Lists all tables in the current database."""
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
            raise DatabaseConnectionError(f"Failed to list tables: {str(e)}")

    def close(self) -> None:
        """Closes the database connection."""
        if self.connection:
            self.connection.close()
            if self.engine:
                self.engine.dispose()
            self.connection = None

class MongoDBConnector:
    def __init__(self, config: DBConfigOut):
        self.config = config
        self.client = None
        self.database = None
        self.connect()

    def connect(self) -> None:
        """Establishes a connection to the MongoDB database."""
        try:
            connection_string = f"mongodb://{self.config.db_user}:{self.config.db_password}@{self.config.host}:{self.config.port}/{self.config.db_name}"
            self.client = pymongo.MongoClient(connection_string)
            self.database = self.client[self.config.db_name]
            # Test connection
            self.client.admin.command('ping')
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to connect to MongoDB: {str(e)}")

    def list_collections(self) -> List[str]:
        """Lists all collections in the current database."""
        try:
            return self.database.list_collection_names()
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to list collections: {str(e)}")

    def get_collection_schema(self, collection_name: str) -> List[Dict[str, Any]]:
        """Retrieves schema information for a specified collection."""
        try:
            collection = self.database[collection_name]
            # Sample a few documents to infer schema
            sample_docs = list(collection.find().limit(100))
            
            if not sample_docs:
                return []
            
            # Infer schema from sample documents
            schema = {}
            for doc in sample_docs:
                for key, value in doc.items():
                    if key not in schema:
                        schema[key] = type(value).__name__
            
            return [{"column_name": key, "data_type": data_type, "is_nullable": "YES", "column_default": None} 
                   for key, data_type in schema.items()]
        except Exception as e:
            raise DatabaseConnectionError(f"Failed to get collection schema: {str(e)}")

    def close(self) -> None:
        """Closes the database connection."""
        if self.client:
            self.client.close()
            self.client = None

class DatabaseConnectorFactory:
    """Factory class to create appropriate database connectors"""
    
    @staticmethod
    def create_connector(config: DBConfigOut):
        """Create a database connector based on the database type"""
        if config.db_type == DBType.mysql:
            return MySQLConnector(config)
        elif config.db_type == DBType.postgres:
            return PostgresConnector(config)
        elif config.db_type == DBType.mongodb:
            return MongoDBConnector(config)
        else:
            raise ValueError(f"Unsupported database type: {config.db_type}")
    
    @staticmethod
    def test_connection(config: DBConfigOut) -> bool:
        """Test database connection without storing the connector"""
        try:
            connector = DatabaseConnectorFactory.create_connector(config)
            connector.close()
            return True
        except Exception as e:
            print(f"Database connection test failed: {str(e)}")
            return False

# Initialize global ChromaDB manager
chroma_manager = ChromaDBManager()

# For backwards compatibility
DatabaseConnector = MySQLConnector 