from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional

class DBType(str, Enum):
    mysql = "mysql"
    postgres = "postgres"
    mongodb = "mongodb"

class DBConfigCreate(BaseModel):
    host: str
    port: int
    db_name: str
    db_user: str
    db_password: str
    db_type: DBType = DBType.mysql  # Default to MySQL

class DBConfigOut(BaseModel):
    id: int
    user_id: int
    host: str
    port: int
    db_name: str
    db_user: str
    # Password is still included but should be encrypted in storage
    db_password: str
    db_type: DBType = DBType.mysql

    model_config = ConfigDict(from_attributes=True)

class DBConnectionTest(BaseModel):
    host: str
    port: int
    db_name: str
    db_user: str
    db_password: str
    db_type: DBType