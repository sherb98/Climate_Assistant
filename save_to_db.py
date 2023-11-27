import sqlite3

def create_table_for_yearly_data_insert(db_name, table_name, variants, nested_dict):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create a table for yearly data
    columns_sql = ', '.join([variant for variant in variants])
    table_creation_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        hour INTEGER PRIMARY KEY,
        {columns_sql}
    );
    """
    cursor.execute(table_creation_query)
    conn.commit()
    
    # Prepare SQL query for inserting data
    columns = ', '.join(variant for variant in variants)
    placeholders = ', '.join(['?'] * (len(variants) + 1)) # +1 for the hour column
    insert_query = f"INSERT INTO {table_name} (hour, {columns}) VALUES ({placeholders})"

    # Prepare the data for bulk insert
    num_hours = len(nested_dict[next(iter(nested_dict))])  # Assuming all variants have the same length
    data_for_insert = [
        [hour] + [nested_dict[variant].iloc[hour]['too_hot'] if variant in nested_dict else 0 for variant in variants]
        for hour in range(num_hours)
    ]

    # Perform bulk insert
    cursor.executemany(insert_query, data_for_insert)
 
    # Commit changes and close connection
    conn.commit()
    conn.close()
    print(f"Yearly data added successfully to table '{table_name}' in database '{db_name}'.")