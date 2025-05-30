from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import verify_token
from app.schemas.db import DBConfigCreate, DBConfigOut
from .models import UserDatabase

router = APIRouter(prefix="/db", tags=["db"])

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
        
        # Create a default PostgreSQL config
        db_config = UserDatabase(
            user_id=user_id,
            db_type="postgres",
            host="localhost",
            port=5432,
            db_name="parseqri",
            db_user="postgres",
            db_password="password"
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