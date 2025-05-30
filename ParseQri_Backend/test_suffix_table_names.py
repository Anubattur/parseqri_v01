import re

def extract_table_name(filename, user_id):
    """Extract table name from a filename and add user_id as suffix."""
    # Remove extension and clean special characters
    file_basename = filename.split('.')[0]
    file_basename = re.sub(r'[^a-zA-Z0-9_]', '_', file_basename)
    
    # Extract base name
    if '_' in file_basename:
        parts = file_basename.split('_')
        if len(parts) > 1:
            # Just use the first part for simplicity
            base_name = parts[0]
        else:
            base_name = file_basename
    else:
        base_name = file_basename
        
    # Add user_id as suffix
    return f"{base_name.lower()}_{user_id}"

def find_table(table_name, user_id, all_tables):
    """Find a table in the database using multiple matching strategies."""
    print(f"Looking for table with name: {table_name}, user_id: {user_id}")
    
    # Try exact match first
    if table_name in all_tables:
        print(f"Exact match found: {table_name}")
        return table_name
    
    # Try with user_id as suffix (new format)
    suffix_name = f"{table_name}_{user_id}"
    if suffix_name in all_tables:
        print(f"Suffix match found: {suffix_name}")
        return suffix_name
    
    # Try with user_id as prefix (old format)
    prefix_name = f"{user_id}_{table_name}"
    if prefix_name in all_tables:
        print(f"Prefix match found: {prefix_name}")
        return prefix_name
    
    # Try partial matches
    for table in all_tables:
        # With user_id as suffix
        if table.startswith(f"{table_name}_") and table.endswith(f"_{user_id}"):
            print(f"Extended suffix match found: {table}")
            return table
        
        # With user_id as prefix
        if table.startswith(f"{user_id}_{table_name}_"):
            print(f"Extended prefix match found: {table}")
            return table
    
    print(f"No matching table found for {table_name} with user_id {user_id}")
    return None

# Mock PostgreSQL tables in the database
mock_tables = [
    "customers_3",            # New format with user_id as suffix
    "3_territory",            # Old format with user_id as prefix
    "sales_report_3",         # New format with suffix
    "products_data_3",        # New format with suffix
    "3_users_data"            # Old format with prefix
]

# Test cases
test_cases = [
    ("customers.csv", "3"),  # Simple name
    ("territory_info.csv", "3"),  # Simple name
    ("sales_report_12345.csv", "3"),  # Name with extra identifiers
    ("random_file.csv", "3"),  # Name not in database
    ("products_data.csv", "3")  # Name with multiple parts
]

print("Testing table name generation with user_id as suffix:")
print("-" * 60)

for filename, user_id in test_cases:
    # Generate table name from filename
    table_name = extract_table_name(filename, user_id)
    print(f"\nFilename: '{filename}', User ID: '{user_id}' -> Table: '{table_name}'")
    
    # Try to find the table in the database
    found_table = find_table(table_name.replace(f"_{user_id}", ""), user_id, mock_tables)
    
    # Show result
    if found_table:
        print(f"✅ Successfully found table: {found_table}")
    else:
        print(f"❌ Table not found in database")
        print(f"Available tables: {', '.join(mock_tables)}")
        
print("\nAll tests completed.") 