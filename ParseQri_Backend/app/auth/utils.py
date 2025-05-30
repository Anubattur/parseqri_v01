from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .models import User

def get_user_by_username_or_email(db: Session, username_or_email: str) -> User:
    return db.query(User).filter(
        (User.username == username_or_email) | (User.email == username_or_email)
    ).first()