from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import subprocess
import sys
import json
from pathlib import Path
import os
from app.auth.routes import router as auth_router
from app.db.routes import router as db_router
from app.routes.data import router as data_router
from app.core.security import verify_token
from app.core.database import get_db
from sqlalchemy.orm import Session

# Main API router without a prefix - will use the prefixes defined in the individual routers
router = APIRouter()

# Include all sub-routers
router.include_router(auth_router)
router.include_router(db_router)
router.include_router(data_router)

# Text to SQL router with API prefix
text_to_sql_router = APIRouter(
    prefix="/api",
    tags=["api"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class TextToSQLQuery(BaseModel):
    query: str
    user_id: str = "default_user"
    visualization: bool = False

class TextToSQLResponse(BaseModel):
    answer: str
    sql_query: str
    data: list = []
    chart_type: str = "bar"
    question: str = ""

@text_to_sql_router.post("/text-to-sql", response_model=TextToSQLResponse)
async def process_text_to_sql(
    query_data: TextToSQLQuery, 
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Process a natural language query and convert it to SQL"""
    try:
        # Get user_id from the token - check both "user_id" and "sub" fields
        user_id = token.get("user_id") or token.get("sub")
        if user_id:
            # Override the user_id in the query data with the authenticated user's ID
            query_data.user_id = str(user_id)  # Convert to string to ensure compatibility
            print(f"Using authenticated user_id: {user_id}")
        else:
            print(f"Warning: No user_id found in token, using default: {query_data.user_id}")
            
        # Get user's connected database configuration
        from app.db.models import UserDatabase
        user_db_config = db.query(UserDatabase).filter(UserDatabase.user_id == user_id).first()
        
        if not user_db_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No database connection found for user. Please connect a database first."
            )
            
        # Get path to TextToSQL_Agent
        agent_dir = Path(__file__).parent.parent.parent / "ParseQri_Agent" / "TextToSQL_Agent"
        main_script = agent_dir / "main.py"
        
        if not main_script.exists():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"TextToSQL_Agent script not found at {main_script}"
            )
            
        # Get Python executable path
        python_executable = sys.executable
        
        # Prepare command with arguments
        cmd = [python_executable, str(main_script)]
        
        # Add the query as a positional argument
        cmd.append(query_data.query)
        
        # Add flags as separate arguments with correct format
        # VISUALIZATION TEMPORARILY DISABLED
        # if query_data.visualization:
        #     cmd.append("--viz")
        # Print message if visualization was requested but is disabled
        if query_data.visualization:
            print("Visualization requested but temporarily disabled")
            
        # Add user_id parameter if provided
        if query_data.user_id:
            cmd.append(f"--user={query_data.user_id}")
            
        # Add database configuration ID to tell the agent which database to use
        cmd.append(f"--db-id={user_db_config.id}")
        
        # Print the command being executed for debugging
        print(f"Running command: {' '.join(cmd)}")
        print(f"Working directory: {str(agent_dir)}")
        print(f"Using database: {user_db_config.db_name} ({user_db_config.db_type})")
            
        # Execute the command
        process = subprocess.run(
            cmd,
            cwd=str(agent_dir),
            text=True,
            capture_output=True
        )
        
        if process.returncode != 0:
            print(f"Process failed with error: {process.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Agent error: {process.stderr}"
            )
        
        # Print full process output for debugging
        print("Process stdout:")
        print(process.stdout)
        
        # Parse the output
        output = process.stdout
        
        # Extract SQL query
        sql_query = ""
        sql_start = output.find("\nSQL Query:")
        if sql_start != -1:
            sql_end = output.find("\n\nResponse:", sql_start)
            if sql_end != -1:
                sql_query = output[sql_start + 11:sql_end].strip()
                
        # Extract response
        response = ""
        response_start = output.find("\nResponse:")
        if response_start != -1:
            response = output[response_start + 10:].strip()
                
        # Determine if visualization data exists
        chart_type = "bar"  # Default
        if "Visualization response:" in output:
            chart_type = "bar"  # Default, could be improved to detect from output
            
        # Extract sample data for visualization
        # In a real implementation, this would parse actual data from the agent's output
        sample_data = []
        try:
            # Try to extract sample data from response
            if "rows" in response.lower() or "results" in response.lower():
                # Very simple parsing - in production would need a more robust approach
                sample_data = [
                    {"name": "Item 1", "value": 100},
                    {"name": "Item 2", "value": 200},
                    {"name": "Item 3", "value": 150}
                ]
        except Exception as e:
            print(f"Error parsing data: {e}")
            
        # Extract the question if available
        question = query_data.query
            
        return TextToSQLResponse(
            answer=response,
            sql_query=sql_query,
            data=sample_data,
            chart_type=chart_type,
            question=question
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

# Include the text-to-sql router
router.include_router(text_to_sql_router)