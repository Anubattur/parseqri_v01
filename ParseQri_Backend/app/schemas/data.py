from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any
from app.schemas.db import DBType

class ColumnMetadata(BaseModel):
    name: str
    type: str
    
    model_config = ConfigDict(from_attributes=True)

class SchemaMetadata(BaseModel):
    table_name: str
    columns: List[ColumnMetadata]
    
    model_config = ConfigDict(from_attributes=True)