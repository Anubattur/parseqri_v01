from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional

class DBType(str, Enum):
    postgres = "postgres"

class DBConfigCreate(BaseModel):
    host: str
    port: int
    db_name: str
    db_user: str
    db_password: str
    
    # Default to PostgreSQL
    db_type: DBType = DBType.postgres

class DBConfigOut(BaseModel):
    id: int
    user_id: int
    host: str
    port: int
    db_name: str
    db_user: str
    # Password is still included but should be encrypted in storage
    db_password: str
    db_type: DBType = DBType.postgres

    model_config = ConfigDict(from_attributes=True)