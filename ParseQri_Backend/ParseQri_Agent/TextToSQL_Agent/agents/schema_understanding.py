import sqlalchemy
from sqlalchemy import inspect, create_engine, text
from typing import Dict, Any, Optional, List
from models.data_models import QueryContext, AgentResponse
import ollama
import os
import chromadb
import uuid

class SchemaUnderstandingAgent:
    """
    Agent responsible for retrieving and processing database schema information.
    Provides context for SQL generation and other downstream tasks.
    """
    
    def __init__(self, llm_model="mistral", api_base="http://localhost:11434", 
                                 db_url="mysql+pymysql://root:root@localhost:3306/parseqri",
                schema="public",
                chroma_persist_dir="../data/db_storage"):
        """Initialize the Schema Understanding Agent with the specified LLM model."""
        self.llm_model = llm_model
        ollama.api_base = api_base
        self.db_url = db_url
        self.schema = schema
        self.chroma_persist_dir = chroma_persist_dir
        
        # Priority 1: Environment variables (highest priority)
        import os
        import json
        if os.getenv('EXTERNAL_DB_ENABLED', '').lower() == 'true' and os.getenv('EXTERNAL_DB_NAME'):
            external_db_name = os.getenv('EXTERNAL_DB_NAME') or os.getenv('EXTERNAL_DB_DATABASE')
            external_db_user = os.getenv('EXTERNAL_DB_USER', 'root')
            external_db_password = os.getenv('EXTERNAL_DB_PASSWORD', 'root')
            external_db_host = os.getenv('EXTERNAL_DB_HOST', 'localhost')
            external_db_port = os.getenv('EXTERNAL_DB_PORT', '3306')
            external_db_type = os.getenv('EXTERNAL_DB_TYPE', 'mysql')
            
            if external_db_type == 'mysql':
                self.db_url = f"mysql+pymysql://{external_db_user}:{external_db_password}@{external_db_host}:{external_db_port}/{external_db_name}"
            elif external_db_type == 'postgres':
                self.db_url = f"postgresql://{external_db_user}:{external_db_password}@{external_db_host}:{external_db_port}/{external_db_name}"
            
            self.schema = external_db_name
            print(f"Using external database from environment: {external_db_name}")
        else:
            # Priority 2: Configuration file (fallback)
            external_config_path = os.path.join(os.path.dirname(__file__), "..", "external_db_config.json")
            if os.path.exists(external_config_path):
                try:
                    with open(external_config_path, 'r') as f:
                        external_config = json.load(f)
                        external_db = external_config.get("external_database", {})
                        if external_db.get("enabled", False):
                            # Use external database configuration
                            self.db_url = f"mysql+pymysql://{external_db['user']}:{external_db['password']}@{external_db['host']}:{external_db['port']}/{external_db['database']}"
                            self.schema = external_db['database']  # Use database name as schema
                            print(f"Using external database from config file: {external_db['database']}")
                except Exception as e:
                    print(f"Warning: Could not load external database config: {e}")
        
        # Create SQLAlchemy engine
        try:
            self.engine = create_engine(self.db_url)
            print(f"MySQL connection established successfully for schema retrieval")
        except Exception as e:
            self.engine = None
            print(f"Error connecting to MySQL: {e}")
        
        # We'll create separate ChromaDB clients for each user as needed
        self.chroma_clients = {}
        self.collections = {}
        
        try:
            self.chroma_client = chromadb.Client()
        except Exception as e:
            print(f"Warning: ChromaDB initialization failed: {e}")
    
    def process(self, context: QueryContext) -> AgentResponse:
        """Process the query context and extract schema information"""
        try:
            # Ensure we have a user_id for ChromaDB lookup
            if not context.user_id:
                # Check available users in the storage directory
                user_dirs = self._get_available_users()
                if user_dirs:
                    context.user_id = user_dirs[0]  # Use first available user
                    print(f"No user ID provided, using first available user: {context.user_id}")
                else:
                    context.user_id = "default_user"
                    print("No user ID provided or available, using default_user")
            else:
                # Validate if user exists
                user_dirs = self._get_available_users()
                if user_dirs and context.user_id not in user_dirs:
                    print(f"Warning: User '{context.user_id}' not found. Available users: {', '.join(user_dirs)}")
                    if user_dirs:
                        context.user_id = user_dirs[0]
                        print(f"Using available user: {context.user_id}")
                        
            # If we don't have a table name yet, try to get it from relevant metadata
            if not context.table_name and hasattr(context, 'relevant_metadata') and context.relevant_metadata:
                # Extract the base table name without UUIDs or user IDs
                retrieved_table = context.relevant_metadata.get('table_name', '')
                
                # Skip empty or single-letter table names
                if len(retrieved_table) <= 1:
                    retrieved_table = ''
                    
                # If the table name contains underscores, extract the base name (first part)
                if '_' in retrieved_table and len(retrieved_table.split('_')) > 1:
                    # Extract the first part (likely the actual table name)
                    base_name = retrieved_table.split('_')[0]
                    context.table_name = base_name
                    print(f"Simplified table name from metadata: '{retrieved_table}' -> '{base_name}'")
                else:
                    context.table_name = retrieved_table
                    
                if context.table_name:
                    print(f"Found table name from relevant_metadata: {context.table_name}")
                
            # Check if we're using external database configuration
            import os
            # Priority 1: Environment variables
            use_external_db = (os.getenv('EXTERNAL_DB_ENABLED', '').lower() == 'true' and os.getenv('EXTERNAL_DB_NAME'))
            # Priority 2: Configuration file
            if not use_external_db:
                external_config_path = os.path.join(os.path.dirname(__file__), "..", "external_db_config.json")
                use_external_db = os.path.exists(external_config_path)
            
            if use_external_db:
                # For external databases, use intelligent table discovery
                if not context.table_name or len(context.table_name) <= 1:  # Skip single-letter table names
                    # Get all available tables from the database
                    available_tables = self._get_user_postgres_tables(context.user_id)
                    print(f"External database detected. Available tables: {', '.join(available_tables)}")
                    
                    if available_tables:
                        # For questions about customers, default to customer table
                        if 'customer' in context.user_question.lower():
                            context.table_name = 'customer'
                            print(f"Using customer table based on query context")
                        else:
                            # Use semantic search to find the most relevant table
                            relevant_table = self._find_relevant_table_by_query(context.user_question, available_tables)
                            if relevant_table:
                                context.table_name = relevant_table
                                print(f"Found semantically relevant table: {context.table_name}")
                            else:
                                # If no semantic match, use the first table as starting point
                                context.table_name = available_tables[0]
                                print(f"Using first available table: {context.table_name}")
                    else:
                        print("No tables found in external database")
                        return AgentResponse(
                            success=False,
                            message="No tables found in external database"
                        )
                
                # For external databases, use table name directly
                postgres_table_name = context.table_name
                print(f"Using external database table directly: {postgres_table_name}")
                
                # Verify the table exists
                available_tables = self._get_user_postgres_tables(context.user_id)
                if postgres_table_name not in available_tables:
                    print(f"Table {postgres_table_name} not found in external database {self.schema}")
                    print(f"Available tables: {', '.join(available_tables)}")
                    return AgentResponse(
                        success=False,
                        message=f"Table {postgres_table_name} not found in database {self.schema}"
                    )
                
            else:
                # Internal database logic (original)
                # If we still don't have a table name, try to find it from ChromaDB
                if not context.table_name:
                    # Search for relevant table in ChromaDB
                    relevant_table = self._find_relevant_table(context.user_id, context.user_question)
                    if relevant_table:
                        # Extract the base table name without UUIDs
                        if '_' in relevant_table and len(relevant_table.split('_')) > 1:
                            base_name = relevant_table.split('_')[0]
                            context.table_name = base_name
                            print(f"Simplified table name from ChromaDB: '{relevant_table}' -> '{base_name}'")
                        else:
                            context.table_name = relevant_table
                        print(f"Found relevant table from ChromaDB: {context.table_name}")
                    else:
                        print(f"No relevant table found in ChromaDB for user {context.user_id}")
                        
                        # Check if we have any tables for this user in MySQL
                        if self.engine:
                            postgres_tables = self._get_user_postgres_tables(context.user_id)
                            if postgres_tables:
                                # Get table name without user prefix
                                first_table = postgres_tables[0]
                                if first_table.startswith(f"{context.user_id}_"):
                                    context.table_name = first_table.replace(f"{context.user_id}_", "")
                                else:
                                    context.table_name = first_table
                                print(f"Using first available MySQL table: {context.table_name}")
                
                # Store the original table name for reference
                original_table_name = context.table_name
                
                # Ensure the table name is properly formatted for database queries
                # First check if the table name already follows expected patterns
                postgres_table_name = context.table_name
                
                # If table already has user_id as suffix, use it directly
                if postgres_table_name and postgres_table_name.endswith(f"_{context.user_id}"):
                    print(f"Table already has user_id as suffix: {postgres_table_name}")
                # If table already has user_id as prefix, use it directly
                elif postgres_table_name and postgres_table_name.startswith(f"{context.user_id}_"):
                    print(f"Table already has user_id as prefix: {postgres_table_name}")
                # Otherwise, add user_id as suffix
                elif postgres_table_name:
                    postgres_table_name = f"{postgres_table_name}_{context.user_id}"
                    print(f"Using table name with user_id suffix: {postgres_table_name}")
                    
                # If we still don't have a table name, check if there are any tables for this user
                if not context.table_name and self.engine:
                    postgres_tables = self._get_user_postgres_tables(context.user_id)
                    if postgres_tables:
                        # Use the first table found
                        first_table = postgres_tables[0]
                        # Check if it has user_id as suffix
                        if first_table.endswith(f"_{context.user_id}"):
                            # Strip the user_id suffix for the context table name
                            context.table_name = first_table[:-(len(context.user_id)+1)]
                            postgres_table_name = first_table
                        # Check if it has user_id as prefix
                        elif first_table.startswith(f"{context.user_id}_"):
                            # Strip the user_id prefix for the context table name
                            context.table_name = first_table[len(context.user_id)+1:]
                            postgres_table_name = first_table
                        else:
                            context.table_name = first_table
                            postgres_table_name = first_table
                        
                        print(f"No table specified, using first available table: {context.table_name} (DB: {postgres_table_name})")
            
            if not context.table_name:
                return AgentResponse(
                    success=False,
                    message=f"No table name found for query. Please upload data first or specify a table for user {context.user_id}."
                )
            
            # Get schema from MySQL using the properly prefixed table name
            schema = self.get_postgres_schema(postgres_table_name)
            
            # If schema not found, try with just the base table name (without UUIDs)
            if not schema and '_' in postgres_table_name:
                # Try to get the actual table name from the database
                actual_table = self._find_actual_table_name(context.user_id, postgres_table_name)
                if actual_table:
                    print(f"Found actual table in database: {actual_table}")
                    schema = self.get_postgres_schema(actual_table)
            
            if not schema:
                return AgentResponse(
                    success=False,
                    message=f"Failed to retrieve schema for table {postgres_table_name}. Make sure the table exists in MySQL."
                )
            
            cleaned_schema = self.clean_schema(schema)
            print(f"Successfully retrieved schema for table {postgres_table_name} with {len(cleaned_schema)} columns")
            
            # Get available tables
            available_tables = self._get_user_postgres_tables(context.user_id)
            
            # Get schemas for all tables
            table_schemas = {}
            for table in available_tables:
                schema = self.get_postgres_schema(table)
                if schema:
                    table_schemas[table] = schema
            
            # Generate schema linking reasoning
            schema_reasoning = self._generate_schema_linking_reasoning(
                context.user_question,
                available_tables,
                table_schemas
            )
            
            # Store the reasoning in the context for other agents
            context.schema_reasoning = schema_reasoning
            
            # Print the reasoning for transparency
            print("\nSchema Linking Reasoning:")
            print("<think>")
            print(schema_reasoning["think"])
            print("</think>")
            print("<answer>")
            print(f"Related_Tables: {';'.join(schema_reasoning['answer']['Related_Tables'])};")
            print(f"Related_Columns: {';'.join(schema_reasoning['answer']['Related_Columns'])};")
            print("</answer>\n")

            return AgentResponse(
                success=True,
                message="Schema retrieved successfully",
                data={"schema": cleaned_schema}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error in schema understanding: {str(e)}"
            )
    
    def _get_available_users(self):
        """Get available user IDs from storage directory"""
        storage_dir = os.path.join(self.chroma_persist_dir)
        if not os.path.exists(storage_dir):
            return []
        
        users = []
        for item in os.listdir(storage_dir):
            if os.path.isdir(os.path.join(storage_dir, item)):
                users.append(item)
        
        return users
    
    def _get_user_postgres_tables(self, user_id: str) -> List[str]:
        """Get all MySQL tables for a user"""
        try:
            if not self.engine:
                return []
                
            # Check if we're using external database configuration
            import os
            # Priority 1: Environment variables
            use_external_db = (os.getenv('EXTERNAL_DB_ENABLED', '').lower() == 'true' and os.getenv('EXTERNAL_DB_NAME'))
            # Priority 2: Configuration file
            if not use_external_db:
                external_config_path = os.path.join(os.path.dirname(__file__), "..", "external_db_config.json")
                use_external_db = os.path.exists(external_config_path)
                
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                all_tables = inspector.get_table_names(schema=self.schema)
                
                if use_external_db:
                    # For external databases, return all tables (no user filtering)
                    print(f"External database detected. Available tables: {', '.join(all_tables) if all_tables else 'None'}")
                    return all_tables
                else:
                    # For internal databases, filter by user_id
                    # Filter tables by user_id suffix instead of prefix
                    user_tables = [table for table in all_tables if table.endswith(f"_{user_id}")]
                    
                    # Print all found tables for debugging
                    if user_tables:
                        print(f"Found {len(user_tables)} tables for user {user_id}: {', '.join(user_tables)}")
                    else:
                        # Also look for tables with other patterns (for compatibility)
                        user_tables = [table for table in all_tables if f"_{user_id}_" in table or table.startswith(f"{user_id}_")]
                        if user_tables:
                            print(f"Found {len(user_tables)} tables with alternative patterns for user {user_id}: {', '.join(user_tables)}")
                        else:
                            # As a fallback, just list all available tables
                            print(f"No tables found for user {user_id}. Available tables: {', '.join(all_tables) if all_tables else 'None'}")
                    
                    return user_tables
                
        except Exception as e:
            print(f"Error getting user MySQL tables: {e}")
            return []
    
    def _get_user_collection(self, user_id):
        """Get or create a user-specific ChromaDB collection"""
        if user_id in self.collections:
            return self.collections[user_id]
            
        # Create user directory if it doesn't exist
        user_dir = os.path.join(self.chroma_persist_dir, user_id)
        os.makedirs(user_dir, exist_ok=True)
        
        # Create or get client for this user
        if user_id not in self.chroma_clients:
            self.chroma_clients[user_id] = chromadb.PersistentClient(path=user_dir)
        
        # Create or get collection for this user
        try:
            collection = self.chroma_clients[user_id].get_collection(f"{user_id}_metadata")
        except ValueError:
            # Collection doesn't exist yet
            return None
            
        self.collections[user_id] = collection
        return collection
    
    def _find_relevant_table(self, user_id: str, query_text: str) -> Optional[str]:
        """Find the most relevant table for a query using ChromaDB"""
        try:
            collection = self._get_user_collection(user_id)
            if not collection:
                print(f"No ChromaDB collection found for user {user_id}, checking MySQL tables directly")
                # If no ChromaDB collection exists, try to find tables in the database
                postgres_tables = self._get_user_postgres_tables(user_id)
                if postgres_tables:
                    # Just return the first table name since we can't do semantic relevance
                    first_table = postgres_tables[0]
                    # Remove user_id prefix if it exists
                    if first_table.startswith(f"{user_id}_"):
                        table_name = first_table[len(f"{user_id}_"):]
                    else:
                        table_name = first_table
                    
                    print(f"Using PostgreSQL table: {table_name}")
                    return table_name
                return None
                
            # Query ChromaDB for relevant tables
            try:
                results = collection.query(
                    query_texts=[query_text],
                    n_results=1,
                    where={"user_id": user_id}
                )
                
                if not results['ids'][0]:
                    return None
                    
                # Get the most relevant metadata
                metadata = results['metadatas'][0][0]
                table_name = metadata.get("table_name")
                
                # Extract just the base name if it contains UUIDs
                if table_name and '_' in table_name:
                    parts = table_name.split('_')
                    # If there are multiple parts, use just the first part (likely the actual table name)
                    if len(parts) > 1:
                        table_name = parts[0]
                        print(f"Simplified table name from ChromaDB: '{metadata.get('table_name')}' -> '{table_name}'")
                
                return table_name
            except Exception as query_error:
                print(f"Error querying ChromaDB: {query_error}, checking MySQL tables directly")
                # If ChromaDB query fails, try to find tables in the database
                postgres_tables = self._get_user_postgres_tables(user_id)
                if postgres_tables:
                    # Just return the first table name since we can't do semantic relevance
                    first_table = postgres_tables[0]
                    # Remove user_id prefix if it exists
                    if first_table.startswith(f"{user_id}_"):
                        table_name = first_table[len(f"{user_id}_"):]
                    else:
                        table_name = first_table
                    
                    print(f"Using PostgreSQL table: {table_name}")
                    return table_name
                return None
                
        except Exception as e:
            print(f"Error finding relevant table: {e}")
            # Try PostgreSQL as a last resort
            try:
                postgres_tables = self._get_user_postgres_tables(user_id)
                if postgres_tables:
                    # Remove user_id prefix if it exists
                    first_table = postgres_tables[0]
                    if first_table.startswith(f"{user_id}_"):
                        table_name = first_table[len(f"{user_id}_"):]
                    else:
                        table_name = first_table
                    
                    print(f"Using MySQL table as fallback: {table_name}")
                    return table_name
            except Exception as pg_error:
                print(f"Failed to fetch MySQL tables: {pg_error}")
            return None
    
    def _find_relevant_table_by_query(self, query_text: str, available_tables: List[str]) -> Optional[str]:
        """
        Find the most relevant table from available tables using semantic similarity.
        
        Args:
            query_text: The user's natural language query
            available_tables: List of available table names
            
        Returns:
            The most relevant table name or None if no good match found
        """
        if not available_tables:
            return None
            
        if len(available_tables) == 1:
            return available_tables[0]
        
        try:
            # Simple keyword-based relevance scoring
            query_lower = query_text.lower()
            query_words = set(query_lower.split())
            
            best_table = None
            best_score = 0
            
            for table in available_tables:
                score = 0
                table_lower = table.lower()
                table_words = set(table_lower.replace('_', ' ').split())
                
                # Direct table name mention gets highest priority
                if table_lower in query_lower:
                    score += 100
                
                # Word overlap scoring
                word_matches = len(query_words.intersection(table_words))
                score += word_matches * 10
                
                # Partial word matches
                for query_word in query_words:
                    for table_word in table_words:
                        if len(query_word) > 3 and query_word in table_word:
                            score += 5
                        elif len(table_word) > 3 and table_word in query_word:
                            score += 5
                
                # Boost score for common business entity names
                business_entities = {
                    'user', 'customer', 'client', 'person', 'people',
                    'order', 'sale', 'transaction', 'purchase',
                    'product', 'item', 'inventory', 'catalog',
                    'account', 'profile', 'data', 'record'
                }
                
                for entity in business_entities:
                    if entity in query_lower and entity in table_lower:
                        score += 15
                
                print(f"Table '{table}' scored {score} for query: {query_text}")
                
                if score > best_score:
                    best_score = score
                    best_table = table
            
            # Only return a table if we have a reasonable confidence (score > 5)
            if best_score > 5:
                print(f"Selected table '{best_table}' with score {best_score}")
                return best_table
            else:
                print(f"No table scored high enough (best: {best_score}), using first available")
                return available_tables[0]
                
        except Exception as e:
            print(f"Error in semantic table selection: {e}")
            return available_tables[0] if available_tables else None
    
    def get_postgres_schema(self, table_name: str) -> Dict[str, str]:
        """Retrieve the schema of the table from MySQL database"""
        try:
            if not self.engine:
                print("MySQL engine not initialized")
                return None
                
            # Check if we're using external database configuration
            import os
            external_config_path = os.path.join(os.path.dirname(__file__), "..", "external_db_config.json")
            use_external_db = os.path.exists(external_config_path)
                
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                
                # Get schema and table name parts
                if '.' in table_name:
                    schema_name, pure_table_name = table_name.split('.', 1)
                else:
                    schema_name = self.schema
                    pure_table_name = table_name
                
                # Check if table exists directly
                all_tables = inspector.get_table_names(schema=schema_name)
                
                # Debug output
                print(f"Searching for table: {pure_table_name}")
                print(f"Available tables: {', '.join(all_tables)}")
                
                if pure_table_name in all_tables:
                    # Direct match found
                    print(f"Found direct table match: {pure_table_name}")
                elif use_external_db:
                    # For external databases, try case-insensitive matching
                    found_table = None
                    for table in all_tables:
                        if table.lower() == pure_table_name.lower():
                            found_table = table
                            break
                    
                    if found_table:
                        pure_table_name = found_table
                        print(f"Found case-insensitive match: {pure_table_name}")
                    else:
                        print(f"Table {pure_table_name} not found in external database {schema_name}")
                        return None
                else:
                    # For internal databases, try user prefix/suffix patterns
                    print(f"Table {pure_table_name} not found in schema {schema_name}")
                    
                    # Try direct matches with common patterns
                    base_name = None
                    user_id = None
                    
                    # Extract potential user_id and base_name from table
                    if '_' in pure_table_name:
                        parts = pure_table_name.split('_')
                        if len(parts) >= 2:
                            # Check if it's in format base_name_user_id
                            user_id = parts[-1]
                            base_name = parts[0]
                            
                            # Try pattern: base_name_user_id
                            if f"{base_name}_{user_id}" in all_tables:
                                pure_table_name = f"{base_name}_{user_id}"
                                print(f"Found table with suffix format: {pure_table_name}")
                            
                            # Try pattern: user_id_base_name
                            elif f"{user_id}_{base_name}" in all_tables:
                                pure_table_name = f"{user_id}_{base_name}"
                                print(f"Found table with prefix format: {pure_table_name}")
                            
                            # Try partial matches
                            else:
                                for table in all_tables:
                                    # Match tables that start with base_name_ and end with _user_id
                                    if table.startswith(f"{base_name}_") and table.endswith(f"_{user_id}"):
                                        pure_table_name = table
                                        print(f"Found table with extended suffix: {pure_table_name}")
                                        break
                                    
                                    # Match tables that start with user_id_base_name_
                                    elif table.startswith(f"{user_id}_{base_name}_"):
                                        pure_table_name = table
                                        print(f"Found table with extended prefix: {pure_table_name}")
                                        break
                    
                    # If we still don't have a match, try all tables again
                    if pure_table_name not in all_tables:
                        # As a last resort, check if there's any table with a similar name
                        for table in all_tables:
                            parts_table = table.split('_')
                            parts_name = pure_table_name.split('_')
                            
                            # Check for common parts
                            if any(part in parts_table for part in parts_name):
                                pure_table_name = table
                                print(f"Found partially matching table: {pure_table_name}")
                                break
                                
                    # Final check
                    if pure_table_name not in all_tables:
                        return None
                
                # Get column info
                columns = inspector.get_columns(pure_table_name, schema=schema_name)
                schema = {col['name']: str(col['type']) for col in columns}
                return schema
                
        except Exception as e:
            print(f"Error retrieving MySQL schema: {e}")
            return None
    
    def clean_schema(self, schema: Dict[str, str]) -> Dict[str, str]:
        """Clean the schema by converting column names to lowercase and removing spaces"""
        cleaned_schema = {}
        for key, value in schema.items():
            cleaned_key = self.clean_column_name(key)
            cleaned_schema[cleaned_key] = value
        return cleaned_schema
    
    def clean_column_name(self, col_name: str) -> str:
        """Clean column names by converting to lowercase and replacing spaces with underscores"""
        col_name = col_name.lower().replace(' ', '_').replace('\n', '_').replace('/', '_')
        col_name = col_name.replace(',', '').replace('(', '').replace(')', '')
        return col_name
    
    def _find_actual_table_name(self, user_id: str, table_name: str) -> str:
        """
        Find the actual table name in the database by prefix matching.
        This helps when we have a table name with UUID but the actual database table uses a simpler name.
        
        Args:
            user_id: User identifier
            table_name: The table name to match (likely includes UUID)
            
        Returns:
            The actual table name from the database or None if not found
        """
        try:
            if not self.engine:
                return None
                
            with self.engine.connect() as conn:
                inspector = inspect(self.engine)
                all_tables = inspector.get_table_names(schema=self.schema)
                
                # Try to extract the base name (assuming format: base_name_uuid)
                base_parts = []
                if '_' in table_name:
                    parts = table_name.split('_')
                    # If the last part is the user ID, use parts before that
                    if parts[-1] == user_id and len(parts) > 1:
                        base_parts = [parts[0]]  # Use the first part
                    # If the first part is the user ID, use parts after that
                    elif parts[0] == user_id and len(parts) > 1:
                        base_parts = [parts[1]]  # Use the second part
                    else:
                        base_parts = [parts[0]]  # Use the first part
                else:
                    base_parts = [table_name]  # Use the whole name
                    
                # Create a simpler base name (just the main part without UUIDs)
                base_name = base_parts[0]
                
                # Look for tables that match the base name
                for table in all_tables:
                    # Perfect match
                    if table == table_name:
                        print(f"Found exact table match: {table}")
                        return table
                    
                    # Match on base_name_user_id pattern (suffix)
                    if table == f"{base_name}_{user_id}":
                        print(f"Found suffix match: {table}")
                        return table
                    
                    # Match on user_id_base_name pattern (prefix)
                    if table == f"{user_id}_{base_name}":
                        print(f"Found prefix match: {table}")
                        return table
                    
                    # Partial match on prefix (old pattern)
                    if table.startswith(f"{user_id}_{base_name}_"):
                        print(f"Found prefix pattern match: {table}")
                        return table
                    
                    # Partial match on suffix (new pattern)
                    if table.startswith(f"{base_name}_") and table.endswith(f"_{user_id}"):
                        print(f"Found suffix pattern match: {table}")
                        return table
                
                print(f"No matching table found for {table_name} or {base_name}")
                
                # As a fallback, list all available tables
                if all_tables:
                    print(f"Available tables: {', '.join(all_tables)}")
                
                return None
                
        except Exception as e:
            print(f"Error finding actual table name: {e}")
            return None
    
    def _generate_schema_linking_reasoning(self, query_text: str, available_tables: List[str], table_schemas: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Generate chain-of-thought reasoning for schema linking.
        
        Args:
            query_text: The user's question
            available_tables: List of available tables
            table_schemas: Dictionary of table schemas
            
        Returns:
            Dictionary containing reasoning and related tables/columns
        """
        try:
            # Build context about tables and their schemas
            schema_context = []
            for table in available_tables:
                if table in table_schemas:
                    columns = [col.get('name', '') for col in table_schemas[table].get('columns', [])]
                    schema_context.append(f"Table '{table}' has columns: {', '.join(columns)}")
            
            # Generate reasoning about schema linking
            reasoning = {
                "think": f"""
Analyzing the question: "{query_text}"
Available tables and their schemas:
{chr(10).join(schema_context)}

Step-by-step reasoning:
1. Examining the question to identify key entities and relationships
2. Looking for relevant tables based on the question context
3. Identifying potential column relationships between tables
""",
                "answer": {
                    "Related_Tables": [],
                    "Related_Columns": []
                }
            }
            
            # Find relevant tables based on query context
            relevant_tables = []
            for table in available_tables:
                # Simple keyword matching - can be enhanced with more sophisticated NLP
                if table.lower() in query_text.lower():
                    relevant_tables.append(table)
                    # Add columns from relevant tables
                    if table in table_schemas:
                        columns = [f"{table}.{col.get('name', '')}" 
                                 for col in table_schemas[table].get('columns', [])]
                        reasoning["answer"]["Related_Columns"].extend(columns)
            
            reasoning["answer"]["Related_Tables"] = relevant_tables
            
            # Store reasoning in ChromaDB for future reference
            if self.chroma_client:
                try:
                    collection = self.chroma_client.get_or_create_collection(
                        name="schema_reasoning"
                    )
                    collection.add(
                        documents=[reasoning["think"]],
                        metadatas=[{
                            "query": query_text,
                            "related_tables": ";".join(reasoning["answer"]["Related_Tables"]),
                            "related_columns": ";".join(reasoning["answer"]["Related_Columns"])
                        }],
                        ids=[str(uuid.uuid4())]
                    )
                except Exception as e:
                    print(f"Warning: Failed to store reasoning in ChromaDB: {e}")
            
            return reasoning
            
        except Exception as e:
            print(f"Error generating schema linking reasoning: {e}")
            return {
                "think": "Error generating reasoning",
                "answer": {
                    "Related_Tables": [],
                    "Related_Columns": []
                }
            } 