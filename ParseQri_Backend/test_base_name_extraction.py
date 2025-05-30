import re

def extract_base_table_name(filename):
    """Extract a simplified base table name from a filename with UUID."""
    # Remove extension and clean special characters
    file_basename = os.path.splitext(filename)[0]
    file_basename = re.sub(r'[^a-zA-Z0-9_]', '_', file_basename)
    
    # Extract base name (first part before underscore if meaningful)
    if '_' in file_basename:
        parts = file_basename.split('_')
        if len(parts) > 1:
            # Use first part if it's meaningful (not just a number or single letter)
            if len(parts[0]) > 1 and not parts[0].isdigit():
                base_name = parts[0]
            else:
                base_name = file_basename
        else:
            base_name = file_basename
    else:
        base_name = file_basename
        
    return base_name.lower()

def find_matching_table(user_id, table_name, all_tables):
    """Find a matching table name from the database using intelligent matching."""
    # Try exact match first
    exact_match = f"{user_id}_{table_name}"
    if exact_match in all_tables:
        return exact_match
    
    # Try to extract the base name
    base_name = table_name
    if '_' in table_name:
        parts = table_name.split('_')
        if len(parts) > 1:
            base_name = parts[0]
    
    # Look for prefix matches
    for table in all_tables:
        # Match user_id_base_name pattern
        if table == f"{user_id}_{base_name}":
            return table
        
        # Match prefix for tables with UUIDs
        if table.startswith(f"{user_id}_{base_name}_"):
            return table
    
    return None

# Test cases
import os
test_filenames = [
    "customer_data.csv",
    "sales_report_12345.csv", 
    "customers_3_54b7092d-99ac-40cd-8b33-b040a9e7d813.csv",
    "3_territory_info.csv",
    "123_user_accounts.csv"
]

print("Testing base name extraction:")
print("-" * 50)
for filename in test_filenames:
    base_name = extract_base_table_name(filename)
    print(f"Original: '{filename}' -> Base name: '{base_name}'")

print("\nTesting table name matching:")
print("-" * 50)
# Mock database tables
mock_tables = [
    "3_customers", 
    "3_sales", 
    "3_territory", 
    "user1_products_abcd1234",
    "admin_sales_report"
]

test_cases = [
    ("3", "customers_3_54b7092d-99ac-40cd-8b33-b040a9e7d813"),
    ("3", "territory_info"),
    ("user1", "products_xyz"),
    ("admin", "unknown_table")
]

for user_id, table_name in test_cases:
    match = find_matching_table(user_id, table_name, mock_tables)
    print(f"User: '{user_id}', Table: '{table_name}' -> Match: '{match}'")
    
    # Show the base name extraction as well
    base_name = extract_base_table_name(table_name)
    base_match = find_matching_table(user_id, base_name, mock_tables)
    if base_match != match:
        print(f"  Base name: '{base_name}' -> Different match: '{base_match}'") 