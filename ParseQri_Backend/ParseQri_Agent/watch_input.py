#!/usr/bin/env python3
"""
Script to continuously monitor the data/input folder for new PDF/image/CSV files.
Run this script in a separate terminal window to automatically process
files as they are added to the data/input folder.
"""
import os
import sys
import time
import subprocess
import re
import json
import pandas as pd
from pathlib import Path

# Define paths
ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
INPUT_DIR = ROOT_DIR / "data" / "input"
CSV_OUTPUT_DIR = ROOT_DIR / "data" / "csv_output"
DB_STORAGE_DIR = ROOT_DIR / "data" / "db_storage"
TEXTSQL_AGENT_DIR = ROOT_DIR / "TextToSQL_Agent"

def setup_directories():
    """Ensure all required directories exist"""
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    CSV_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DB_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    (ROOT_DIR / "data" / "query_logs").mkdir(parents=True, exist_ok=True)
    print(f"Monitoring directory: {INPUT_DIR}")

def check_for_new_files(processed_files):
    """Check for new PDF, image, or CSV files in the input directory"""
    if not INPUT_DIR.exists():
        return []
    
    # Find all PDF and image files
    pdf_files = list(INPUT_DIR.glob("*.pdf"))
    image_files = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.tiff", "*.bmp"]:
        image_files.extend(list(INPUT_DIR.glob(ext)))
    
    # Find all CSV files
    csv_files = list(INPUT_DIR.glob("*.csv"))
    
    all_files = pdf_files + image_files + csv_files
    new_files = [f for f in all_files if f.name not in processed_files]
    
    return new_files

def extract_user_id_from_filename(filename):
    """
    Extract user_id from the filename pattern.
    Expected format: originalname_userid_uuid.extension or originalname_uuid.extension
    """
    # Try to extract from pattern with user_id embedded (originalname_userid_uuid.extension)
    pattern = r"(.+?)_([^_]+)_([a-f0-9-]+)\.(csv|pdf|png|jpg|jpeg|tiff|bmp)$"
    match = re.match(pattern, filename)
    if match:
        return match.group(2)  # Return the user_id group
    
    # If no embedded user_id, use default
    return "default_user"

def suggest_table_name_from_csv(csv_path):
    """
    Analyze CSV content to suggest an appropriate table name.
    Returns both a suggested table name and database name.
    """
    try:
        # Read first few rows of CSV to analyze structure
        df = pd.read_csv(csv_path, nrows=5)
        
        # Basic approach: Use the filename without extension as base
        file_base = Path(csv_path).stem
        base_name = file_base.split('_')[0]  # Use first part before any underscore
        
        # Clean the name for database use
        clean_name = re.sub(r'[^\w]', '_', base_name).lower()
        
        # If name starts with a digit, prepend 't_'
        if clean_name and not clean_name[0].isalpha():
            clean_name = f"t_{clean_name}"
        
        # If empty or too short, use a generic name
        if len(clean_name) < 3:
            # Try to infer from column names
            if len(df.columns) > 0:
                # Look for common data themes in column names
                col_text = " ".join(df.columns).lower()
                
                if any(word in col_text for word in ['customer', 'client', 'user']):
                    clean_name = 'customer_data'
                elif any(word in col_text for word in ['product', 'item', 'inventory']):
                    clean_name = 'product_data'
                elif any(word in col_text for word in ['sale', 'order', 'transaction']):
                    clean_name = 'sales_data'
                elif any(word in col_text for word in ['finance', 'account', 'payment']):
                    clean_name = 'financial_data'
                else:
                    clean_name = 'data_table'
        
        # Create database name (SQLite database name needs .db extension)
        db_name = f"{clean_name}.db"
        
        return clean_name, db_name
    
    except Exception as e:
        print(f"Error suggesting table name: {e}")
        return "data_table", "data_table.db"

def process_files(new_files):
    """Process the new files using the TextToSQL_Agent main.py"""
    if not new_files:
        return []
    
    print(f"\nFound {len(new_files)} new files to process:")
    for file in new_files:
        print(f"- {file.name}")
    
    # Separate files by type
    pdf_image_files = []
    csv_files = []
    
    for file in new_files:
        if file.suffix.lower() in ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            pdf_image_files.append(file)
        elif file.suffix.lower() == '.csv':
            csv_files.append(file)
    
    processed_files = []
    
    # Process PDFs and images
    if pdf_image_files:
        print(f"\nProcessing {len(pdf_image_files)} PDF/image files...")
        try:
            # Ensure the input directory exists in conversion_tool
            os.makedirs("../conversion_tool/pdfs", exist_ok=True)
            
            # Copy the files from data/input to conversion_tool/pdfs
            for file in pdf_image_files:
                target = Path("../conversion_tool/pdfs") / file.name
                with open(file, 'rb') as src, open(target, 'wb') as dst:
                    dst.write(src.read())
                print(f"Copied {file.name} to conversion tool")
            
            # Get the current Python interpreter path
            python_executable = sys.executable
            
            # Run the conversion tool
            conversion_result = subprocess.run(
                [python_executable, "../conversion_tool/main.py"],
                cwd="../conversion_tool",
                capture_output=True, 
                text=True
            )
            
            if conversion_result.returncode == 0:
                print("PDF/image conversion completed successfully!")
                print(conversion_result.stdout.strip())
                processed_files.extend([f.name for f in pdf_image_files])
                
                # Copy the CSV output to our data directory
                os.makedirs("../data/csv_output", exist_ok=True)
                for csv_file in Path("../conversion_tool/csv_output").glob("*.csv"):
                    target = Path("../data/csv_output") / csv_file.name
                    with open(csv_file, 'rb') as src, open(target, 'wb') as dst:
                        dst.write(src.read())
                    print(f"Copied {csv_file.name} to data/csv_output")
                    
                    # Also copy to input directory to process as a CSV
                    input_target = INPUT_DIR / csv_file.name
                    with open(csv_file, 'rb') as src, open(input_target, 'wb') as dst:
                        dst.write(src.read())
                    print(f"Copied {csv_file.name} to data/input for processing")
            else:
                print(f"Error processing PDF/image files: {conversion_result.stderr}")
        except Exception as e:
            print(f"Error during PDF/image conversion: {str(e)}")
    
    # Process CSV files directly with TextToSQL_Agent
    if csv_files:
        print(f"\nProcessing {len(csv_files)} CSV files...")
        try:
            # Get the current Python interpreter path
            python_executable = sys.executable
            
            for csv_file in csv_files:
                # Extract user ID from filename or use default
                user_id = extract_user_id_from_filename(csv_file.name)
                
                # Get suggested table and database names from CSV content
                table_name, db_name = suggest_table_name_from_csv(csv_file)
                
                print(f"\nProcessing CSV file: {csv_file.name}")
                print(f"User ID: {user_id}")
                print(f"Suggested Table Name: {table_name}")
                print(f"Database Name: {db_name}")
                
                # Check for database ID mapping
                db_id = None
                db_mapping_path = DB_STORAGE_DIR / user_id / "db_mapping.json"
                if db_mapping_path.exists():
                    try:
                        with open(db_mapping_path, 'r') as f:
                            db_mappings = json.load(f)
                            # Check if table exists in mappings
                            if table_name in db_mappings:
                                db_id = db_mappings[table_name].get("db_id")
                                print(f"Found database ID mapping: {db_id}")
                    except Exception as e:
                        print(f"Error reading database mappings: {str(e)}")
                
                # Additional command arguments for database ID if available
                cmd_args = [
                    python_executable, 
                    "main.py", 
                    "--upload", str(csv_file),
                    "--user", user_id,
                    "--table", table_name
                ]
                
                # Add database ID if available
                if db_id is not None:
                    cmd_args.extend(["--db-id", str(db_id)])
                
                # Run TextToSQL_Agent with the upload parameter
                upload_result = subprocess.run(
                    cmd_args,
                    cwd=str(TEXTSQL_AGENT_DIR),
                    capture_output=True,
                    text=True
                )
                
                if upload_result.returncode == 0:
                    print(f"CSV processing completed successfully!")
                    print(upload_result.stdout.strip())
                    
                    # Create user-specific directory
                    user_db_dir = DB_STORAGE_DIR / user_id
                    user_db_dir.mkdir(exist_ok=True)
                    
                    # Save metadata about the table in the user's directory
                    metadata = {
                        "file": csv_file.name,
                        "user_id": user_id,
                        "table_name": table_name,
                        "db_name": db_name,
                        "import_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "status": "success",
                        "output": upload_result.stdout.strip()
                    }
                    
                    # Add db_id if available
                    if db_id is not None:
                        metadata["db_id"] = db_id
                    
                    with open(user_db_dir / f"{table_name}_metadata.json", "w") as f:
                        json.dump(metadata, f, indent=2)
                    
                    # Add to processed files list
                    processed_files.append(csv_file.name)
                else:
                    print(f"Error processing CSV file: {upload_result.stderr}")
                    
                    # Log error to a file
                    user_db_dir = DB_STORAGE_DIR / user_id
                    user_db_dir.mkdir(exist_ok=True)
                    
                    # Save error metadata
                    error_metadata = {
                        "file": csv_file.name,
                        "user_id": user_id,
                        "table_name": table_name,
                        "db_name": db_name,
                        "import_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                        "status": "error",
                        "error": upload_result.stderr
                    }
                    
                    with open(user_db_dir / f"{table_name}_error.json", "w") as f:
                        json.dump(error_metadata, f, indent=2)
        except Exception as e:
            print(f"Error during CSV processing: {str(e)}")
            
    return processed_files

def main():
    """Main function to monitor the input directory"""
    setup_directories()
    
    processed_files = set()
    print("\nWatching for new files... (Press Ctrl+C to stop)")
    
    try:
        while True:
            new_files = check_for_new_files(processed_files)
            if new_files:
                newly_processed = process_files(new_files)
                processed_files.update(newly_processed)
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\nFile watching stopped by user.")
        
if __name__ == "__main__":
    main() 