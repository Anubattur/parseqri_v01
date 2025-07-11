#!/usr/bin/env python3
"""
Dynamic Database Configuration Tool for ParseQri TextToSQL Agent
This script allows you to configure database connections without manually editing files.
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any
import sys

def set_environment_variables(config: Dict[str, str]) -> None:
    """Set environment variables for the current session"""
    for key, value in config.items():
        os.environ[key] = str(value)
        print(f"✅ Set {key}={value}")

def create_env_file(config: Dict[str, str]) -> None:
    """Create a .env file with the configuration"""
    env_path = Path(".env")
    
    content = ["# ParseQri Dynamic Database Configuration"]
    content.append("# Generated automatically - feel free to modify")
    content.append("")
    
    for key, value in config.items():
        content.append(f"{key}={value}")
    
    try:
        with env_path.open('w') as f:
            f.write('\n'.join(content))
        print(f"✅ Created .env file at {env_path.absolute()}")
    except Exception as e:
        print(f"❌ Could not create .env file: {e}")

def update_external_config_file(db_config: Dict[str, Any]) -> None:
    """Update the external_db_config.json file"""
    config_path = Path("external_db_config.json")
    
    try:
        # Load existing config or create new
        if config_path.exists():
            with config_path.open('r') as f:
                config = json.load(f)
        else:
            config = {
                "user_mapping": {
                    "1": "external_user",
                    "default_user": "external_user"
                },
                "table_mapping": {
                    "direct_access": True,
                    "no_user_prefix": True
                }
            }
        
        # Update database config
        config["external_database"] = {
            "enabled": True,
            "type": db_config["type"],
            "host": db_config["host"],
            "port": int(db_config["port"]),
            "database": db_config["database"],
            "user": db_config["user"],
            "password": db_config["password"]
        }
        
        # Write back to file
        with config_path.open('w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Updated {config_path.absolute()}")
        
    except Exception as e:
        print(f"❌ Could not update config file: {e}")

def interactive_setup() -> Dict[str, str]:
    """Interactive setup for database configuration"""
    print("\n" + "="*60)
    print("🚀 ParseQri Dynamic Database Configuration")
    print("="*60)
    
    config = {}
    
    # Database type
    print("\nSelect database type:")
    print("1. MySQL (default)")
    print("2. PostgreSQL")
    
    choice = input("Enter choice (1-2) [1]: ").strip()
    if choice == "2":
        config["EXTERNAL_DB_TYPE"] = "postgres"
        default_port = "5432"
    else:
        config["EXTERNAL_DB_TYPE"] = "mysql"
        default_port = "3306"
    
    # Database connection details
    config["EXTERNAL_DB_HOST"] = input(f"Database host [localhost]: ").strip() or "localhost"
    config["EXTERNAL_DB_PORT"] = input(f"Database port [{default_port}]: ").strip() or default_port
    config["EXTERNAL_DB_DATABASE"] = input("Database name: ").strip()
    config["EXTERNAL_DB_USER"] = input("Database username [root]: ").strip() or "root"
    config["EXTERNAL_DB_PASSWORD"] = input("Database password [root]: ").strip() or "root"
    
    if not config["EXTERNAL_DB_DATABASE"]:
        print("❌ Database name is required!")
        return None
    
    config["EXTERNAL_DB_ENABLED"] = "true"
    
    return config

def command_line_setup(args) -> Dict[str, str]:
    """Setup from command line arguments"""
    config = {
        "EXTERNAL_DB_ENABLED": "true",
        "EXTERNAL_DB_TYPE": args.type,
        "EXTERNAL_DB_HOST": args.host,
        "EXTERNAL_DB_PORT": str(args.port),
        "EXTERNAL_DB_DATABASE": args.database,
        "EXTERNAL_DB_USER": args.user,
        "EXTERNAL_DB_PASSWORD": args.password
    }
    return config

def test_connection(config: Dict[str, str]) -> bool:
    """Test database connection with the provided configuration"""
    try:
        # Set environment variables temporarily
        original_env = {}
        for key, value in config.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value
        
        # Import and test connection
        sys.path.append('.')
        from main import Config
        
        if config["EXTERNAL_DB_TYPE"] == "mysql":
            import mysql.connector
            conn = mysql.connector.connect(
                host=config["EXTERNAL_DB_HOST"],
                port=int(config["EXTERNAL_DB_PORT"]),
                user=config["EXTERNAL_DB_USER"],
                password=config["EXTERNAL_DB_PASSWORD"],
                database=config["EXTERNAL_DB_DATABASE"]
            )
            conn.close()
        elif config["EXTERNAL_DB_TYPE"] == "postgres":
            import psycopg2
            conn = psycopg2.connect(
                host=config["EXTERNAL_DB_HOST"],
                port=int(config["EXTERNAL_DB_PORT"]),
                user=config["EXTERNAL_DB_USER"],
                password=config["EXTERNAL_DB_PASSWORD"],
                database=config["EXTERNAL_DB_DATABASE"]
            )
            conn.close()
        
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
        print("✅ Database connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Dynamic Database Configuration for ParseQri")
    
    # Command line options
    parser.add_argument("--type", choices=["mysql", "postgres"], default="mysql", help="Database type")
    parser.add_argument("--host", default="localhost", help="Database host")
    parser.add_argument("--port", type=int, help="Database port (3306 for MySQL, 5432 for PostgreSQL)")
    parser.add_argument("--database", help="Database name")
    parser.add_argument("--user", default="root", help="Database username")
    parser.add_argument("--password", default="root", help="Database password")
    parser.add_argument("--test-only", action="store_true", help="Only test connection, don't save config")
    parser.add_argument("--env-file", action="store_true", help="Create .env file instead of JSON config")
    
    args = parser.parse_args()
    
    # Set default port based on database type
    if not args.port:
        args.port = 3306 if args.type == "mysql" else 5432
    
    # Get configuration
    if args.database:
        # Use command line arguments
        config = command_line_setup(args)
        print(f"🔧 Configuring {args.type} database: {args.database}")
    else:
        # Interactive setup
        config = interactive_setup()
        if not config:
            return
    
    # Test connection
    print("\n🔍 Testing database connection...")
    if not test_connection(config):
        if input("\nConnection failed. Continue anyway? (y/N): ").lower() != 'y':
            return
    
    if args.test_only:
        print("✅ Test completed!")
        return
    
    # Save configuration
    print("\n💾 Saving configuration...")
    
    if args.env_file:
        create_env_file(config)
    else:
        # Update JSON config file
        db_config = {
            "type": config["EXTERNAL_DB_TYPE"],
            "host": config["EXTERNAL_DB_HOST"],
            "port": config["EXTERNAL_DB_PORT"],
            "database": config["EXTERNAL_DB_DATABASE"],
            "user": config["EXTERNAL_DB_USER"],
            "password": config["EXTERNAL_DB_PASSWORD"]
        }
        update_external_config_file(db_config)
    
    # Set environment variables for current session
    set_environment_variables(config)
    
    print("\n🎉 Configuration complete!")
    print("\nYou can now run queries with:")
    print("python main.py 'your question here' --user default_user")
    print("\nOr list tables with:")
    print("python main.py --list-tables --user default_user")

if __name__ == "__main__":
    main() 