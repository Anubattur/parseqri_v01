from fastapi import APIRouter, Depends, HTTPException, status, Form, Body, Security, Request, Header
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional, Union
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from app.schemas.auth import UserCreate, UserLogin, UserOut, Token
from .models import User
from .utils import get_user_by_username_or_email
from jose import JWTError, jwt
from app.core.config import settings
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["auth"])

# Get the OAuth2 scheme from main for documentation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
security = HTTPBearer()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if username exists
        db_user = get_user_by_username_or_email(db, user.username)
        if db_user:
            raise HTTPException(status_code=400, detail="Username already registered")
        
        # Check if email exists
        db_user = get_user_by_username_or_email(db, user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(user.password)
        db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Return a properly structured dictionary for the UserOut model
        return {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email
        }
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred during registration: {str(e)}")

# Regular API login endpoint
@router.post("/login", response_model=Token, tags=["auth"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    """
    Login with username/email and password for regular API clients using JSON
    """
    try:
        db_user = get_user_by_username_or_email(db, user.username_or_email)
        if not db_user or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"user_id": db_user.id})
        refresh_token = create_refresh_token(data={"user_id": db_user.id})
        
        # Return both access and refresh tokens in standard JWT format
        return {
            "access": access_token,
            "refresh": refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during login: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Token refresh endpoint
@router.post("/token/refresh/", response_model=Token)
async def refresh_token(refresh: Union[str, dict] = Body(...)):
    """
    Refresh an access token using a valid refresh token
    
    - Accept either a string token directly or an object with a refresh field
    - Returns a new access token
    """
    try:
        # Handle the case where the input is an object with a refresh field
        refresh_token = refresh.get("refresh") if isinstance(refresh, dict) else refresh
        
        if not refresh_token or not isinstance(refresh_token, str):
            raise HTTPException(status_code=422, detail="Invalid refresh token format")
            
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        # Create new access token
        access_token = create_access_token(data={"user_id": user_id})
        
        return {"access": access_token, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# Token verification endpoint
@router.post("/token/verify/")
async def verify_token(token: Union[str, dict] = Body(...)):
    """
    Verify if a token is valid
    
    - Accept either a string token directly or an object with a token field
    - Returns whether the token is valid or not
    """
    try:
        # Handle the case where the input is an object with a token field
        token_str = token.get("token") if isinstance(token, dict) else token
        
        if not token_str or not isinstance(token_str, str):
            raise HTTPException(status_code=422, detail="Invalid token format")
            
        payload = jwt.decode(token_str, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"valid": True}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)):
    """Helper function to get current user from Authorization header"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=404, detail="User ID not found in token")
        
        db_user = db.query(User).filter(User.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while authenticating",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me", response_model=UserOut, summary="Get current user details", 
           description="Requires authentication via Bearer token. Returns the current user's profile information.")
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information based on the JWT token.
    
    - **Authorization**: Requires a valid JWT token
    - **Returns**: User information including ID, username, and email
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }