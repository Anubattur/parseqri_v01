from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class UserDatabase(Base):
    __tablename__ = "user_databases"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    db_type = Column(String(50), nullable=False, default="mysql")  # mysql, postgres, mongodb
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    db_name = Column(String(255), nullable=False)
    db_user = Column(String(255), nullable=False)
    db_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())