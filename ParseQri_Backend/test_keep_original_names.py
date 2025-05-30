import re

def clean_table_name(name):
    """Clean table name to make it SQL-compliant but maintain original name."""
    # Replace spaces and special characters with underscores
    cleaned = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    # Convert to lowercase for consistency
    cleaned = cleaned.lower()
    # Ensure it's not empty
    if not cleaned:
        cleaned = 'data_table'
    return cleaned

def get_postgres_table_name(user_id, table_name):
    """Create a PostgreSQL table name with user ID prefix."""
    # Create the full table name
    full_table_name = f"{user_id}_{table_name}"
    return full_table_name

# Test cases for user IDs and table names
test_cases = [
    ("123", "territory_info"),  # User ID starts with a number
    ("user1", "456_data"),      # Table name starts with a number
    ("987", "654_info"),        # Both start with numbers
    ("admin", "sales_data"),    # Neither starts with a number
]

print("Testing simple table name generation:")
print("-" * 50)

for user_id, table_name in test_cases:
    # Clean the table name first (just replaces spaces and special chars)
    clean_table = clean_table_name(table_name)
    # Get the full PostgreSQL table name (just adds user_id prefix)
    postgres_table = get_postgres_table_name(user_id, clean_table)
    print(f"User ID: '{user_id}', Table: '{table_name}' -> Postgres Table: '{postgres_table}'") 