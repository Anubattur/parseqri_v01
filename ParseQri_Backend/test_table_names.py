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

# Test cases
test_names = ['123test', 'test123', 'test-data', 'Sample Data', '']
for name in test_names:
    cleaned = clean_table_name(name)
    print(f"Original: '{name}', Cleaned: '{cleaned}'") 