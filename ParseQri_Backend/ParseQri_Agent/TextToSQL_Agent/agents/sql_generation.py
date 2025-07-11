import ollama
from typing import Dict, Any, Optional
from models.data_models import QueryContext, AgentResponse
import re
import json

class SQLGenerationAgent:
    """
    Agent responsible for generating SQL queries from natural language questions.
    Uses an LLM to translate user questions into executable SQL.
    """
    
    def __init__(self, llm_model="qwen2.5", api_base="http://localhost:11434"):
        """Initialize the SQL Generation Agent with the specified LLM model."""
        self.llm_model = llm_model
        ollama.api_base = api_base
    
    def process(self, context: QueryContext) -> AgentResponse:
        """Process the query context to generate a SQL query."""
        try:
            # Check if user_id is provided
            if not context.user_id:
                return AgentResponse(
                    success=False,
                    message="User ID is required for SQL generation",
                    data={}
                )
            
            # Check if we have the schema
            if not context.schema:
                return AgentResponse(
                    success=False,
                    message="Schema information is required for SQL generation"
                )
            
            # Generate SQL
            sql_query = self.generate_sql(context)
            
            if not sql_query:
                return AgentResponse(
                    success=False,
                    message="Failed to generate SQL query"
                )
            
            # Ensure the SQL query has user_id filter
            sql_query = self.ensure_user_filter(sql_query, context.user_id, context.table_name)
            
            return AgentResponse(
                success=True,
                message="SQL query generated successfully",
                data={"sql_query": sql_query}
            )
        except Exception as e:
            return AgentResponse(
                success=False,
                message=f"Error in SQL generation: {str(e)}"
            )
    
    def generate_sql(self, context: QueryContext) -> str:
        """
        Generate an SQL query based on the user's question and schema.
        
        Args:
            context: The query context containing user question and schema
            
        Returns:
            Generated SQL query
        """
        # Prepare schema information for prompt
        schema_info = "\n".join([f"- {col}: {dtype}" for col, dtype in context.schema.items()])
        
        # Get the relevant metadata if available
        relevant_metadata = None
        if hasattr(context, 'relevant_metadata') and context.relevant_metadata:
            relevant_metadata = context.relevant_metadata
        
        # Build a more detailed prompt with user context awareness
        prompt = self._build_sql_generation_prompt(
            context.user_question, 
            context.table_name,
            schema_info,
            context.user_id,
            relevant_metadata
        )
        
        # Call LLM for SQL generation
        response = ollama.chat(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Extract SQL from response
        sql_query = self._extract_sql_from_response(response['message']['content'])
        return sql_query
    
    def _build_sql_generation_prompt(self, question: str, table_name: str, 
                                    schema_info: str, user_id: str,
                                    relevant_metadata: Dict[str, Any] = None) -> str:
        """
        Build a detailed prompt for SQL generation with user context awareness.
        
        Args:
            question: User's natural language question
            table_name: Name of the database table
            schema_info: Table schema information
            
            relevant_metadata: Additional metadata about the table (optional)
            
        Returns:
            Prompt for SQL generation
        """
        # Add metadata insights if available
        metadata_context = ""
        if relevant_metadata:
            columns = relevant_metadata.get("columns", [])
            column_descriptions = relevant_metadata.get("column_descriptions", {})
            
            # Add descriptions for columns if available
            col_descriptions = []
            for col in columns:
                desc = column_descriptions.get(col, "")
                if desc:
                    col_descriptions.append(f"- {col}: {desc}")
            
            if col_descriptions:
                metadata_context = "Column descriptions from metadata:\n" + "\n".join(col_descriptions) + "\n\n"
        
        # Check if we're using an external database (like Sakila)
        # External databases use table names directly without user prefixes
        import os
        external_config_path = os.path.join(os.path.dirname(__file__), "..", "external_db_config.json")
        use_external_db = os.path.exists(external_config_path)
        
        if use_external_db:
            # For external databases, use table name directly
            fully_qualified_table = table_name
            database_note = "This is an external database (e.g., Sakila). Use table names directly."
        else:
            # For internal databases, use user-prefixed table names
            fully_qualified_table = f"{table_name}_{user_id}"
            database_note = "This is an internal database with user-specific tables."
        
        # Build the prompt with user context awareness
        return f"""
        Generate an SQL query to answer the following question: "{question}"
        
        Database information:
        - Table name: {fully_qualified_table}
        - IMPORTANT: You MUST use the exact table name "{fully_qualified_table}" in your SQL query
        - {database_note}
        
        Table schema:
        {schema_info}
        
        {metadata_context}
        
        IMPORTANT REQUIREMENTS:
        1. Use only columns that exist in the schema
        2. Return only the data that answers the user's question
        3. Use appropriate SQL functions for aggregation, filtering, etc.
        4. Ensure the query is valid MySQL syntax
        5. ALWAYS use the EXACT table name "{fully_qualified_table}" in your FROM clause
        6. For complex queries, you may need to join multiple tables based on the database schema and relationships
        
        Return only the SQL query, without comments, explanations, or markdown formatting.
        """
    
    def _extract_sql_from_response(self, response: str) -> str:
        """
        Extract clean SQL from the LLM response.
        
        Args:
            response: LLM response text
            
        Returns:
            Clean SQL query
        """
        # Remove markdown code blocks if present
        if "```sql" in response:
            start_idx = response.find("```sql") + 6
            end_idx = response.find("```", start_idx)
            sql = response[start_idx:end_idx].strip()
        elif "```" in response:
            start_idx = response.find("```") + 3
            end_idx = response.find("```", start_idx)
            sql = response[start_idx:end_idx].strip()
        else:
            # Just use the response as is
            sql = response.strip()
        
        return sql
    
    def ensure_user_filter(self, query: str, user_id: str, table_name: str) -> str:
        """
        Ensure the SQL query includes a filter for user_id.
        
        Args:
            query: The SQL query to modify
            user_id: User identifier
            table_name: Table name
        """
        # Check if we're using an external database
        import os
        external_config_path = os.path.join(os.path.dirname(__file__), "..", "external_db_config.json")
        use_external_db = os.path.exists(external_config_path)
        
        if use_external_db:
            # For external databases like Sakila, don't add user filter
            return query
            
        # For internal databases, add user filter
        if not query:
            return query
            
        # Original user filter logic for internal databases
        query = query.strip()
        if "WHERE" in query.upper():
            # Add user filter to existing WHERE clause
            query = query.replace("WHERE", f"WHERE user_id = '{user_id}' AND", 1)
        else:
            # Add WHERE clause with user filter
            query = f"{query} WHERE user_id = '{user_id}'"
            
        return query

    def sanitize_sql_query(self, sql_query: str) -> str:
        """
        Sanitize the SQL query by removing backticks and extracting only the valid SQL part.
        
        Args:
            sql_query: The raw SQL query from the LLM
            
        Returns:
            A cleaned SQL query
        """
        # Remove backticks that can cause syntax issues
        sql_query = sql_query.replace('`', '')
        
        # Extract the SQL query if wrapped in markdown code blocks
        sql_query = re.sub(r'```sql|```', '', sql_query).strip()
        
        # Replace any non-ASCII semicolons (like full-width Japanese/Chinese semicolons: ；) with standard ASCII semicolons
        sql_query = re.sub(r'[；｜;]', ';', sql_query)
        
        # Remove any duplicate semicolons
        sql_query = re.sub(r';;+', ';', sql_query)
        
        # Extract only the SQL query if extra text is present
        match = re.search(r"(SELECT .*?;)", sql_query, re.DOTALL | re.IGNORECASE)
        if match:
            sql_query = match.group(1).strip()
        
        # Ensure the query ends with exactly one semicolon
        sql_query = sql_query.rstrip(';') + ';'
        
        # Additional check for non-ASCII characters that might cause issues
        ascii_query = ""
        for char in sql_query:
            if ord(char) < 128:  # Keep only ASCII characters
                ascii_query += char
            elif char in '；｜':  # Known problematic characters
                ascii_query += ';'
            else:
                # For other non-ASCII characters, try to replace with closest ASCII equivalent
                # Or just skip if no good replacement
                pass
        
        # If our sanitization stripped too much, fall back to the original with just backtick removal
        if not ascii_query.strip() or 'SELECT' not in ascii_query.upper():
            return sql_query
            
        return ascii_query

    def explain_sql(self, sql_query: str) -> str:
        """
        Generate an explanation of the given SQL query in natural language.
        
        Args:
            sql_query: The SQL query to explain
            
        Returns:
            A natural language explanation of the query
        """
        prompt = (
            "Instructions: You are a helpful assistant that explains SQL queries in natural language. "
            "Explain the SQL query in a clear, step-by-step manner.\n\n"
            f"Explain the following SQL query:\n'{sql_query}'\n\n"
            "Provide a concise yet detailed explanation."
        )

        try:
            response = ollama.chat(model=self.llm_model, messages=[{
                "role": "user", 
                "content": prompt
            }])
            
            if response and 'message' in response and 'content' in response['message']:
                return response['message']['content'].strip()
            else:
                return "Could not generate explanation for the SQL query."
                
        except Exception as e:
            print(f"Error explaining SQL: {str(e)}")
            return f"Error occurred while explaining the query: {str(e)}" 