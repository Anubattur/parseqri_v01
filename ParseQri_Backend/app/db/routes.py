from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.schemas.db import DBConfigCreate, DBConfigOut, DBConnectionTest
from .models import UserDatabase
from .connectors import DatabaseConnectorFactory, chroma_manager
from app.services.metadata_extraction import metadata_extraction_service
from typing import List, Dict, Any

router = APIRouter(prefix="/db", tags=["db"])

@router.post("/test-connection")
def test_database_connection(
    connection_data: DBConnectionTest,
    token: dict = Depends(verify_token)
):
    """Test database connection without saving configuration"""
    try:
        # Create a temporary config object for testing
        test_config = DBConfigOut(
            id=0,  # Temporary ID
            user_id=token.get("user_id"),
            host=connection_data.host,
            port=connection_data.port,
            db_name=connection_data.db_name,
            db_user=connection_data.db_user,
            db_password=connection_data.db_password,
            db_type=connection_data.db_type
        )
        
        # Test the connection
        is_connected = DatabaseConnectorFactory.test_connection(test_config)
        
        if is_connected:
            return {"status": "success", "message": "Database connection successful"}
        else:
            return {"status": "error", "message": "Failed to connect to database"}
            
    except Exception as e:
        return {"status": "error", "message": f"Connection test failed: {str(e)}"}

@router.post("/config", response_model=DBConfigOut)
def create_db_config(
    config: DBConfigCreate,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        user_id = token.get("user_id")
        db_config = UserDatabase(
            user_id=user_id,
            db_type=config.db_type,
            host=config.host,
            port=config.port,
            db_name=config.db_name,
            db_user=config.db_user,
            db_password=config.db_password
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        
        # Return a properly structured dictionary for the DBConfigOut model
        return {
            "id": db_config.id,
            "user_id": db_config.user_id,
            "db_type": db_config.db_type,
            "host": db_config.host,
            "port": db_config.port,
            "db_name": db_config.db_name,
            "db_user": db_config.db_user,
            "db_password": db_config.db_password
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating database configuration"
        )

@router.post("/extract-metadata/{config_id}")
async def extract_and_store_metadata(
    config_id: int,
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Extract metadata from external database and store in ChromaDB using Database_Agent_SQL"""
    try:
        user_id = token.get("user_id")
        
        # Get database configuration
        db_config = db.query(UserDatabase).filter(
            UserDatabase.id == config_id,
            UserDatabase.user_id == user_id
        ).first()
        
        if not db_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database configuration not found"
            )
        
        # Create config object
        config_obj = DBConfigOut(
            id=db_config.id,
            user_id=db_config.user_id,
            host=db_config.host,
            port=db_config.port,
            db_name=db_config.db_name,
            db_user=db_config.db_user,
            db_password=db_config.db_password,
            db_type=db_config.db_type
        )
        
        # Use the enhanced metadata extraction service
        result = await metadata_extraction_service.extract_metadata(config_obj, str(user_id))
        
        # Ensure consistent response format
        if result["status"] == "error":
            # Return error but with 200 status code to allow client to handle it
            return {
                "success": False,
                "status": "error",
                "message": result["message"],
                "metadata": result.get("metadata", [])
            }
        else:
            # Return success response
            return {
                "success": True,
                "status": "success",
                "message": result["message"],
                "metadata": result.get("metadata", []),
                "extraction_method": result.get("extraction_method", "unknown")
            }
        
    except HTTPException:
        raise
    except Exception as e:
        # Return error response with consistent format
        return {
            "success": False,
            "status": "error",
            "message": f"Failed to extract metadata: {str(e)}",
            "metadata": []
        }

@router.post("/default-config", response_model=DBConfigOut)
def create_default_db_config(
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Create a default database configuration for testing"""
    try:
        user_id = token.get("user_id")
        
        # Check if user already has a config
        existing_config = db.query(UserDatabase).filter(UserDatabase.user_id == user_id).first()
        if existing_config:
            return {
                "id": existing_config.id,
                "user_id": existing_config.user_id,
                "db_type": existing_config.db_type,
                "host": existing_config.host,
                "port": existing_config.port,
                "db_name": existing_config.db_name,
                "db_user": existing_config.db_user,
                "db_password": existing_config.db_password
            }
        
        # Create a default MySQL config
        db_config = UserDatabase(
            user_id=user_id,
            db_type="mysql",
            host="localhost",
            port=3306,
            db_name="parseqri",
            db_user="root",
            db_password="root"
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
        
        return {
            "id": db_config.id,
            "user_id": db_config.user_id,
            "db_type": db_config.db_type,
            "host": db_config.host,
            "port": db_config.port,
            "db_name": db_config.db_name,
            "db_user": db_config.db_user,
            "db_password": db_config.db_password
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating default database configuration: {str(e)}"
        )

@router.get("/config", response_model=list[DBConfigOut])
def get_db_configs(
    token: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    try:
        user_id = token.get("user_id")
        configs = db.query(UserDatabase).filter(UserDatabase.user_id == user_id).all()
        
        # Convert ORM objects to dictionaries for Pydantic validation
        result = []
        for config in configs:
            result.append({
                "id": config.id,
                "user_id": config.user_id,
                "db_type": config.db_type,
                "host": config.host,
                "port": config.port,
                "db_name": config.db_name,
                "db_user": config.db_user,
                "db_password": config.db_password
            })
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving database configurations"
        )

@router.get("/config/{config_id}", response_model=DBConfigOut)
def get_db_config_by_id(
    config_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific database configuration by ID (internal use - no auth required)"""
    try:
        db_config = db.query(UserDatabase).filter(UserDatabase.id == config_id).first()
        
        if not db_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Database configuration not found"
            )
        
        return {
            "id": db_config.id,
            "user_id": db_config.user_id,
            "db_type": db_config.db_type,
            "host": db_config.host,
            "port": db_config.port,
            "db_name": db_config.db_name,
            "db_user": db_config.db_user,
            "db_password": db_config.db_password
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while retrieving database configuration: {str(e)}"
        )

@router.get("/search-metadata")
def search_metadata(
    query: str,
    token: dict = Depends(verify_token),
    limit: int = 5
):
    """Search for relevant tables/collections based on query"""
    try:
        user_id = token.get("user_id")
        results = chroma_manager.search_relevant_tables(user_id, query, limit)
        
        return {
            "status": "success",
            "query": query,
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search metadata: {str(e)}"
        )