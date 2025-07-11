import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional
from models.data_models import QueryContext, AgentResponse
from sqlalchemy import inspect
import re

class QueryExecutionAgent:
    """
    Agent responsible for executing SQL queries against databases.
    Handles both SQLite and MySQL connections with user context awareness.
    """
    
    def __init__(self, mysql_url="mysql+pymysql://root:root@localhost:3306/parseqri"):
        """
        Initialize the Query Execution Agent.
        
        Args:
            mysql_url: MySQL connection URL
        """
        self.mysql_url = mysql_url
        
        # Create SQLAlchemy engine
        try:
            self.engine = create_engine(self.mysql_url)
            print(f"MySQL connection established successfully for query execution")
        except Exception as e:
            self.engine = None
            print(f"Error connecting to MySQL: {e}")
        
    def process(self, context: QueryContext) -> AgentResponse:
        """Process an SQL query execution request"""
        try:
            if not context.sql_query:
                return AgentResponse(
                    success=False,
                    message="No SQL query to execute"
                )
            
            # Ensure user_id is set (find available user if missing)
            if not context.user_id:
                available_users = self._get_available_users()
                if available_users:
                    context.user_id = available_users[0]
                    print(f"No user ID provided for query execution, using available user: {context.user_id}")
                else:
                    context.user_id = "default_user"
                    print("No user ID provided and no users available, using default_user")
            else:
                # Validate if user exists in the database
                available_users = self._get_available_users()
                if available_users and context.user_id not in available_users:
                    print(f"Warning: User '{context.user_id}' not found. Available users: {', '.join(available_users)}")
                    if available_users:
                        context.user_id = available_users[0]
                        print(f"Using available user: {context.user_id}")
            
            # Remove any erroneous "user_id = 'X'" conditions from the query to avoid errors
            # This is a more elegant approach than trying to add conditions
            sql_query = context.sql_query
            
            # Execute the query without additional filtering
            # First, try to execute with MySQL if we have a properly configured engine
            if self.engine:
                # Execute with MySQL
                results = self.execute_postgres_query(sql_query)
                if results is not None:
                    # Query executed successfully
                    print(f"Successfully executed query for user {context.user_id}")
                else:
                    # Fallback to SQLite if MySQL fails and a DB name is provided
                    if context.db_name and context.db_name.endswith('.db'):
                        print(f"MySQL execution failed, falling back to SQLite for user {context.user_id}")
                        results = self.execute_sqlite_query(sql_query, context.db_name)
            elif context.db_name and context.db_name.endswith('.db'):
                # No MySQL engine or user_id, use SQLite (for backward compatibility)
                print(f"Using SQLite for user {context.user_id} with database {context.db_name}")
                results = self.execute_sqlite_query(sql_query, context.db_name)
            else:
                # No valid database connection
                return AgentResponse(
                    success=False,
                    message=f"No valid database connection available for user {context.user_id}"
                )
            
            if results is None:
                return AgentResponse(
                    success=False,
                    message="Failed to execute SQL query"
                )
            
            # Check for empty results
            if len(results) == 0:
                return AgentResponse(
                    success=True,
                    message="Query executed successfully, but returned no results",
                    data={"query_results": results}
                )
            
            return AgentResponse(
                success=True,
                message=f"Query executed successfully, returned {len(results)} rows",
                data={"query_results": results}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error executing query: {str(e)}"
            )
    
    def execute_sqlite_query(self, query: str, db_name: str) -> Optional[pd.DataFrame]:
        """
        Execute an SQL query against a SQLite database.
        
        Args:
            query: SQL query to execute
            db_name: SQLite database file path
            
        Returns:
            DataFrame with query results or None if execution fails
        """
        try:
            with sqlite3.connect(db_name) as conn:
                results = pd.read_sql_query(query, conn)
                print(f"Query executed successfully against SQLite database")
                return results
        except Exception as e:
            print(f"Error executing SQLite query: {e}")
            return None
    
    def execute_postgres_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Execute an SQL query against a MySQL database.
        
        Args:
            query: SQL query to execute
            
        Returns:
            DataFrame with query results or None if execution fails
        """
        try:
            if not self.engine:
                print("MySQL engine not initialized")
                return None
                
            # Remove any trailing "WHERE user_id = 'X'" conditions to avoid errors
            if query.rstrip().endswith(';'):
                # Remove the trailing semicolon before checking
                query_without_semicolon = query.rstrip(';')
                
                # Check for problematic "WHERE user_id = 'X'" pattern at the end
                if re.search(r'WHERE\s+user_id\s*=\s*[\'"].*?[\'"]$', query_without_semicolon, re.IGNORECASE):
                    # Remove the entire problematic WHERE clause
                    query = re.sub(r'WHERE\s+user_id\s*=\s*[\'"].*?[\'"]$', '', query_without_semicolon) + ';'
                    print(f"Removed trailing user_id filter from query")
                
                # Check for syntax error with multiple WHERE clauses
                where_count = query.upper().count("WHERE")
                if where_count > 1:
                    # Replace second WHERE with AND to fix syntax
                    first_where_index = query.upper().find("WHERE")
                    second_where_index = query.upper().find("WHERE", first_where_index + 5)
                    
                    if second_where_index != -1:
                        query = query[:second_where_index] + "AND" + query[second_where_index + 5:]
                        print(f"Fixed multiple WHERE clauses in query")
                
                # Make sure we don't accidentally append more conditions that could cause errors
                query = query.rstrip(';') + ';'
            
            # Check if the query contains a FROM clause without the user_id suffix in table name
            # This is a common issue where the LLM generates queries with just the base table name
            from_match = re.search(r'FROM\s+([`"]?)(\w+)([`"]?)', query, re.IGNORECASE)
            if from_match:
                table_name = from_match.group(2)
                # Check if this table exists in the database
                with self.engine.connect() as conn:
                    inspector = inspect(self.engine)
                    all_tables = inspector.get_table_names(schema='parseqri')
                    
                    # If the table doesn't exist, check if there's a version with user_id suffix
                    if table_name not in all_tables:
                        # Look for tables with this base name followed by underscore (potential user_id suffix)
                        potential_tables = [t for t in all_tables if t.startswith(f"{table_name}_")]
                        if potential_tables:
                            # Use the first matching table
                            corrected_table = potential_tables[0]
                            print(f"Table '{table_name}' not found, using '{corrected_table}' instead")
                            
                            # Replace the table name in the query
                            quote_start = from_match.group(1)
                            quote_end = from_match.group(3)
                            query = query.replace(
                                f"FROM {quote_start}{table_name}{quote_end}", 
                                f"FROM {quote_start}{corrected_table}{quote_end}"
                            )
                            print(f"Corrected query: {query}")
            
            # Print the final query for debugging
            print(f"Executing SQL query: {query}")
                
            # Execute query and fetch results
            with self.engine.connect() as conn:
                results = pd.read_sql_query(text(query), conn)
                print(f"Query executed successfully against MySQL database")
                return results
                
        except Exception as e:
            print(f"Error executing MySQL query: {e}")
            print(f"Query was: {query}")
            return None
    
    def _get_available_users(self):
        """Get list of users with data in MySQL"""
        try:
            if not self.engine:
                return []
                
            user_ids = set()
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                all_tables = inspector.get_table_names(schema='parseqri')
                
                # Extract user IDs from table names (format: user_id_tablename)
                for table in all_tables:
                    parts = table.split('_', 1)
                    if len(parts) > 1:
                        user_ids.add(parts[0])
                        
            return list(user_ids)
                
        except Exception as e:
            print(f"Error getting available users: {e}")
            return [] 