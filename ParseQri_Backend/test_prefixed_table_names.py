import re

def clean_table_name(name):
    """Clean table name to make it SQL-compliant."""
    # Replace spaces and special characters with underscores
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Ensure it doesn't start with a number
    if cleaned and cleaned[0].isdigit():
        cleaned = 't_' + cleaned
    # Convert to lowercase for consistency
    cleaned = cleaned.lower()
    # Ensure it's not empty
    if not cleaned:
        cleaned = 'data_table'
    return cleaned

def get_postgres_table_name(user_id, table_name):
    """Create a PostgreSQL-compatible table name with user ID prefix."""
    # Check if user_id starts with a digit - if so, add 't_' prefix
    prefixed_user_id = user_id
    if prefixed_user_id and prefixed_user_id[0].isdigit():
        prefixed_user_id = f"t_{prefixed_user_id}"
        print(f"User ID starts with a digit, using prefixed ID: {prefixed_user_id}")
    
    # Create the full table name
    full_table_name = f"{prefixed_user_id}_{table_name}"
    
    # Ensure the full table name doesn't start with a digit
    if full_table_name and full_table_name[0].isdigit():
        full_table_name = f"t_{full_table_name}"
        print(f"Full table name starts with a digit, adding prefix: {full_table_name}")
    
    return full_table_name

# Test cases for user IDs and table names
test_cases = [
    ("123", "territory_info"),  # User ID starts with a number
    ("user1", "456_data"),      # Table name starts with a number
    ("987", "654_info"),        # Both start with numbers
    ("admin", "sales_data"),    # Neither starts with a number
]

print("Testing table name generation for PostgreSQL:")
print("-" * 50)

for user_id, table_name in test_cases:
    # Clean the table name first
    clean_table = clean_table_name(table_name)
    # Get the full PostgreSQL table name
    postgres_table = get_postgres_table_name(user_id, clean_table)
    print(f"User ID: '{user_id}', Table: '{table_name}' -> Postgres Table: '{postgres_table}'") 