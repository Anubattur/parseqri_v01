from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import subprocess
import threading
import sys
from pathlib import Path

from app.core.database import Base, engine
from app.routes.api import router
from app.auth.routes import router as auth_router
from app.routes.data import router as data_router, global_router as data_global_router, api_router as data_api_router
from app.db.routes import router as db_router

# OAuth2 scheme for Swagger UI authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI(
    title="ParseQri API",
    description="API for parsing and analyzing data with MySQL, PostgreSQL, and MongoDB support",
    version="1.0.0",
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,
        "persistAuthorization": True,  # Keep authorization data between refreshes
        "tryItOutEnabled": True,
        "displayRequestDuration": True,
    }
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],  # Add frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Create tables in the database
Base.metadata.create_all(bind=engine)

# Include routers
# Include API router last to avoid route overlaps
app.include_router(router)

# Include additional dataset routers for frontend compatibility
app.include_router(data_global_router)
app.include_router(data_api_router)

# Start the watch_input.py script that monitors the input directory
def start_watcher():
    """Start the watch_input.py script in a separate thread"""
    try:
        # Get path to watch_input.py
        agent_dir = Path(__file__).parent.parent / "ParseQri_Agent"
        watch_script = agent_dir / "watch_input.py"
        
        # Ensure script exists and is executable
        if not watch_script.exists():
            print(f"Warning: watch_input.py script not found at {watch_script}")
            return
            
        # Get Python executable path
        python_executable = sys.executable
        
        # Start the process with subprocess
        print(f"Starting input directory watcher in background...")
        
        # Using subprocess with Popen to run in background
        process = subprocess.Popen(
            [python_executable, str(watch_script)],
            cwd=str(agent_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Log startup
        print(f"Watcher started with PID: {process.pid}")
        
        # Start a thread to read and log output
        def log_output():
            for line in process.stdout:
                print(f"Watcher: {line.strip()}")
        
        threading.Thread(target=log_output, daemon=True).start()
        
    except Exception as e:
        print(f"Error starting watcher: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    # Create necessary directories
    os.makedirs("uploads", exist_ok=True)
    
    # Ensure ParseQri Agent directories exist
    agent_data_dir = Path(__file__).parent.parent / "ParseQri_Agent" / "data"
    agent_input_dir = agent_data_dir / "input"
    agent_db_storage_dir = agent_data_dir / "db_storage"
    
    os.makedirs(agent_input_dir, exist_ok=True)
    os.makedirs(agent_db_storage_dir, exist_ok=True)
    
    # Start the input directory watcher in a background thread
    threading.Thread(target=start_watcher, daemon=True).start()
    
    print("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("Application shutting down")

@app.get("/")
def read_root():
    return {
        "app": "ParseQri API",
        "version": "1.0.0",
        "documentation": "/docs",
        "database": "MySQL (with PostgreSQL and MongoDB support)",
        "features": ["Multi-database support", "ChromaDB integration", "File upload", "Natural language queries"]
    }

# Customize OpenAPI schema to add security
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes
    )
    
    # Add security scheme for Bearer token
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token from login response"
        }
    }
    
    # Apply security to all operations by default
    if "security" not in openapi_schema:
        openapi_schema["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)