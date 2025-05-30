from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.db.models import UserDatabase
from app.db.connectors import DatabaseConnector
from app.db.schema_manager import SchemaManager
from app.schemas.db import DBConfigOut
from app.schemas.data import SchemaMetadata, ColumnMetadata
import os
import uuid
import shutil
import traceback
import pandas as pd
import sys
import subprocess
from pathlib import Path
import json
import re

router = APIRouter(prefix="/data", tags=["data"])

def cleanup_temp_file(file_path: str):
    """Delete temporary file after processing."""
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing temp file {file_path}: {str(e)}")

@router.post("/upload/{db_id}", response_model=SchemaMetadata)
async def upload_csv(
    background_tasks: BackgroundTasks,
    db_id: int,
    file: UploadFile = File(...),
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Upload a CSV file and create a table in the database."""
    try:
        user_id = token.get("user_id")
        db_config = db.query(UserDatabase).filter(UserDatabase.id == db_id, UserDatabase.user_id == user_id).first()
        if not db_config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database config not found")
        
        # Make sure uploads directory exists for temporary processing
        os.makedirs("uploads", exist_ok=True)
        
        # Make sure ParseQri Agent input directory exists
        # Use absolute path for ParseQri_Agent directory
        agent_base_dir = Path(__file__).parent.parent.parent / "ParseQri_Agent"
        agent_input_dir = agent_base_dir / "data" / "input"
        os.makedirs(agent_input_dir, exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        # unique_id = uuid.uuid4()
        original_filename = file.filename
        file_extension = os.path.splitext(original_filename)[1]
        # safe_filename = f"{os.path.splitext(original_filename)[0]}_{user_id}_{unique_id}{file_extension}"
        safe_filename = f"{os.path.splitext(original_filename)[0]}_{user_id}{file_extension}"
        
        # Save CSV temporarily for validation
        temp_file_path = f"uploads/{safe_filename}"
        
        # Save permanent copy to ParseQri_Agent input directory
        agent_file_path = agent_input_dir / safe_filename
        
        try:
            # Save uploaded file to temporary location
            with open(temp_file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Schedule temp file cleanup
            background_tasks.add_task(cleanup_temp_file, temp_file_path)
            
            # Verify file was saved correctly
            if os.path.getsize(temp_file_path) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Uploaded file is empty"
                )
            
            # Try to read with pandas to validate CSV
            try:
                df = pd.read_csv(temp_file_path)
                if df.empty:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="CSV file contains no data"
                    )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Invalid CSV format: {str(e)}"
                )
            
            # Save permanent copy to ParseQri_Agent input directory for agent processing
            shutil.copy2(temp_file_path, agent_file_path)
            print(f"CSV file saved to ParseQri agent input directory: {agent_file_path}")
            
            # Create metadata file with db_id to ensure proper database association
            metadata_dir = agent_base_dir / "data" / "db_storage" / str(user_id)
            os.makedirs(metadata_dir, exist_ok=True)
            metadata_file_path = metadata_dir / "db_mapping.json"
            
            # Load existing mappings or create new if not exists
            db_mappings = {}
            if metadata_file_path.exists():
                try:
                    with open(metadata_file_path, 'r') as f:
                        db_mappings = json.load(f)
                except:
                    pass
            
            # Use the original table name without modifications
            file_basename = os.path.splitext(file.filename)[0]
            
            # Extract just the actual table name from the filename (without UUIDs)
            # First replace spaces and special characters
            file_basename = re.sub(r'[^a-zA-Z0-9_]', '_', file_basename)
            
            # If the name contains underscores, use just the first part as the base name
            if '_' in file_basename:
                parts = file_basename.split('_')
                if len(parts) > 1:
                    # Check if the first part is a meaningful name (not just a number or single letter)
                    if len(parts[0]) > 1 and not parts[0].isdigit():
                        table_name = parts[0]
                    else:
                        # Otherwise use the full name
                        table_name = file_basename
                else:
                    table_name = file_basename
            else:
                table_name = file_basename
                
            # Add user_id as suffix for the table name
            table_name = f"{table_name}_{user_id}"
                
            # Convert to lowercase for consistency
            table_name = table_name.lower()
            
            print(f"Using table name: {table_name} from file: {file.filename}")
            
            # Add new table mapping
            db_mappings[table_name] = {
                "db_id": db_id,
                "file_path": str(agent_file_path),
                "upload_time": pd.Timestamp.now().isoformat()
            }
            
            # Save updated mappings
            with open(metadata_file_path, 'w') as f:
                json.dump(db_mappings, f, indent=2)
            
            # Format DB config as a dictionary
            db_config_dict = {
                "id": db_config.id,
                "user_id": db_config.user_id,
                "db_type": db_config.db_type,
                "host": db_config.host,
                "port": db_config.port,
                "db_name": db_config.db_name,
                "db_user": db_config.db_user,
                "db_password": db_config.db_password
            }
            
            # Connect to database
            connector = DatabaseConnector(DBConfigOut(**db_config_dict))
            schema_manager = SchemaManager(connector)
            
            # Process CSV and create table
            metadata = schema_manager.create_table_from_csv(table_name, temp_file_path)
            
            # Run ParseQri agent processing in the background
            background_tasks.add_task(process_with_parseqri_agent, str(agent_file_path), str(user_id), table_name)
            
            return metadata
            
        except Exception as e:
            # Log the full error with traceback
            print(f"Error processing CSV: {str(e)}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process CSV: {str(e)}"
            )
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log any unexpected errors
        print(f"Unexpected error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

def process_with_parseqri_agent(csv_file_path: str, user_id: str, table_name: str):
    """
    Process the uploaded CSV file with the ParseQri agent.
    This runs in a background task.
    """
    try:
        print(f"Starting ParseQri agent processing for file: {csv_file_path}")
        
        # Verify file exists
        if not os.path.exists(csv_file_path):
            print(f"Error: File not found: {csv_file_path}")
            return
            
        # Get path to the ParseQri agent's TextToSQL_Agent directory
        agent_dir = Path(__file__).parent.parent.parent / "ParseQri_Agent" / "TextToSQL_Agent"
        
        # Get the current Python interpreter path
        python_executable = sys.executable
        
        # Get database ID from the mapping file if available
        db_id = None
        metadata_dir = Path(__file__).parent.parent.parent / "ParseQri_Agent" / "data" / "db_storage" / str(user_id)
        metadata_file_path = metadata_dir / "db_mapping.json"
        
        if metadata_file_path.exists():
            try:
                with open(metadata_file_path, 'r') as f:
                    db_mappings = json.load(f)
                    if table_name in db_mappings:
                        db_id = db_mappings[table_name].get("db_id")
                        print(f"Found database ID {db_id} for table {table_name}")
            except Exception as e:
                print(f"Error reading database mappings: {str(e)}")
        
        # Use absolute path for the CSV file
        csv_file_path = os.path.abspath(csv_file_path)
        
        # Build command with all available parameters
        command = [
            python_executable, 
            "main.py", 
            "--upload", csv_file_path,
            "--user", user_id,
            "--table", table_name
        ]
        
        # Add database ID if available
        if db_id is not None:
            command.extend(["--db-id", str(db_id)])
        
        print(f"Running command: {' '.join(command)}")
        print(f"Working directory: {agent_dir}")
        
        process = subprocess.run(
            command,
            cwd=str(agent_dir),
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            print(f"ParseQri agent processing completed successfully.")
            print(process.stdout)
        else:
            print(f"Error during ParseQri agent processing: {process.stderr}")
            
    except Exception as e:
        print(f"Error in ParseQri agent processing: {str(e)}")
        traceback.print_exc()

@router.get("/schema/{db_id}/{table_name}", response_model=SchemaMetadata)
def get_schema(
    db_id: int,
    table_name: str,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Get schema metadata for a table."""
    try:
        user_id = token.get("user_id")
        db_config = db.query(UserDatabase).filter(UserDatabase.id == db_id, UserDatabase.user_id == user_id).first()
        if not db_config:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database config not found")

        # Format DB config as a dictionary
        db_config_dict = {
            "id": db_config.id,
            "user_id": db_config.user_id,
            "db_type": db_config.db_type,
            "host": db_config.host,
            "port": db_config.port,
            "db_name": db_config.db_name,
            "db_user": db_config.db_user,
            "db_password": db_config.db_password
        }
        
        connector = DatabaseConnector(DBConfigOut(**db_config_dict))
        schema_manager = SchemaManager(connector)
        return schema_manager.get_schema_metadata(table_name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve schema: {str(e)}"
        )