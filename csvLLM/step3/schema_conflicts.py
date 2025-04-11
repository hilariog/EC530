"""
schema_conflicts.py

This script loads a CSV file into a SQLite database while handling schema conflicts.
It dynamically infers the CSV schema and then:
  - Uses PRAGMA table_info() to detect the existing table schema.
  - For each column in the CSV schema, if the table already exists:
      * If a column is missing, it is automatically added.
      * If a column exists but with a different type, the user is prompted to choose:
           - (O)verwrite the entire table (drop and recreate),
           - (R)ename the new column (and update the CSV data accordingly), or
           - (S)kip inserting data for that column.
  - Errors and conflicts are logged to error_log.txt.
  - Finally, the CSV data is inserted.

Usage:
    python3 schema_conflicts.py <csv_path> <db_path> <table_name>
Example:
    python3 schema_conflicts.py sample_data.csv example.db data_table
"""

import os
import sys
import sqlite3
import pandas as pd
import logging

# Configure logging to file.
logging.basicConfig(filename='error_log.txt', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def map_dtype_to_sql(dtype):
    """
    Map a pandas dtype to a SQLite data type.
    """
    if pd.api.types.is_integer_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_float_dtype(dtype):
        return "REAL"
    elif pd.api.types.is_bool_dtype(dtype):
        return "INTEGER"
    elif pd.api.types.is_datetime64_any_dtype(dtype):
        return "DATETIME"
    else:
        return "TEXT"

def infer_schema_from_dataframe(df):
    """
    Infer a SQLite table schema from a pandas DataFrame.
    Returns both a string (for CREATE TABLE) and a dict mapping column names to SQL types.
    """
    columns = []
    schema_dict = {}
    for col in df.columns:
        sql_type = map_dtype_to_sql(df[col].dtype)
        columns.append(f"{col} {sql_type}")
        schema_dict[col] = sql_type
    schema_str = ", ".join(columns)
    return schema_str, schema_dict

def create_table_dynamically(db_path, table_name, schema_str):
    """
    Create a table in SQLite dynamically using the inferred schema.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema_str});"
    try:
        cursor.execute(create_table_sql)
        conn.commit()
    except Exception as e:
        logging.error("Error creating table: %s", e)
        print(f"Error creating table: {e}")
    finally:
        conn.close()

def table_exists(db_path, table_name):
    """
    Check if a table exists in the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def get_existing_schema(db_path, table_name):
    """
    Retrieve the existing schema of a table as a dictionary mapping column names to types.
    Uses PRAGMA table_info().
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    rows = cursor.fetchall()
    conn.close()
    # rows: (cid, name, type, notnull, dflt_value, pk)
    return {row[1]: row[2] for row in rows}

def drop_table(db_path, table_name):
    """
    Drop the table from the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    conn.commit()
    conn.close()
    print(f"Table '{table_name}' has been dropped.")

def prompt_conflict_resolution(conflict_col, existing_type, inferred_type):
    """
    Prompt the user regarding a schema conflict and return the chosen option.
    Options:
      O: Overwrite the entire table.
      R: Rename the new column.
      S: Skip inserting data for this column.
    """
    prompt = (f"Conflict for column '{conflict_col}': existing type '{existing_type}' vs "
              f"inferred type '{inferred_type}'. Choose an option:\n"
              "  [O]verwrite the entire table,\n"
              "  [R]ename the new column,\n"
              "  [S]kip this column\n"
              "Enter O, R, or S: ")
    while True:
        choice = input(prompt).strip().upper()
        if choice in ('O', 'R', 'S'):
            return choice
        else:
            print("Invalid input. Please enter O, R, or S.")

def handle_schema_conflicts_interactive(db_path, table_name, inferred_schema_dict, df):
    """
    Compare the inferred schema with the existing table schema and handle conflicts interactively.
    If a conflict is found for a column:
      - Prompt the user to either overwrite the table, rename the new column, or skip that column.
      - Overwriting means dropping the existing table and recreating it.
      - Renaming adds a new column with a provided name (and renames the dataframe column).
      - Skipping removes that column from the dataframe insertion.
    """
    existing_schema = get_existing_schema(db_path, table_name)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # We will collect columns to drop from the DataFrame if the user chooses "skip"
    cols_to_drop = []

    for col, inferred_type in inferred_schema_dict.items():
        if col in existing_schema:
            existing_type = existing_schema[col]
            if existing_type.upper() != inferred_type.upper():
                logging.error(f"Schema conflict for column '{col}': existing type '{existing_type}', inferred type '{inferred_type}'.")
                choice = prompt_conflict_resolution(col, existing_type, inferred_type)
                if choice == 'O':
                    # Overwrite: drop the table and return an indicator to recreate.
                    drop_table(db_path, table_name)
                    print("Overwriting the table with new schema...")
                    conn.close()
                    return "OVERWRITE"
                elif choice == 'R':
                    # Rename: prompt for a new column name and update both the table and dataframe.
                    new_name = input(f"Enter new name for the new column '{col}': ").strip()
                    # Check if new_name already exists in the table; if so, ask again.
                    if new_name in existing_schema:
                        print(f"Column name '{new_name}' already exists in table. Skipping rename.")
                        cols_to_drop.append(col)
                    else:
                        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {new_name} {inferred_type};"
                        try:
                            cursor.execute(alter_sql)
                            df.rename(columns={col: new_name}, inplace=True)
                            print(f"Column '{col}' will be inserted as '{new_name}'.")
                        except Exception as e:
                            logging.error("Error renaming column '%s': %s", col, e)
                            print(f"Error renaming column '{col}': {e}. Skipping column.")
                            cols_to_drop.append(col)
                elif choice == 'S':
                    # Skip: do not insert data for this column.
                    print(f"Skipping column '{col}' from insertion.")
                    cols_to_drop.append(col)
        # If column not exists, we'll add it automatically.
        else:
            try:
                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {col} {inferred_type};"
                cursor.execute(alter_sql)
                print(f"Automatically added missing column: {col} {inferred_type}")
            except Exception as e:
                logging.error("Error adding column '%s': %s", col, e)
                print(f"Error adding column '{col}': {e}")
    conn.commit()
    conn.close()

    # Remove columns from dataframe that the user chose to skip.
    if cols_to_drop:
        df.drop(columns=cols_to_drop, inplace=True)
    return "OK"

def load_csv_and_create_table_with_interactive_conflict(csv_path, db_path, table_name):
    """
    Load CSV into DataFrame, handle schema conflicts interactively, and insert data into SQLite.
    """
    # Load CSV into DataFrame.
    df = pd.read_csv(csv_path)
    schema_str, inferred_schema_dict = infer_schema_from_dataframe(df)

    # If the table exists, check for conflicts; otherwise, create the table.
    if table_exists(db_path, table_name):
        print(f"Table '{table_name}' exists. Checking for schema conflicts...")
        result = handle_schema_conflicts_interactive(db_path, table_name, inferred_schema_dict, df)
        if result == "OVERWRITE":
            # Recreate the table with new schema.
            create_table_dynamically(db_path, table_name, schema_str)
    else:
        create_table_dynamically(db_path, table_name, schema_str)
        print(f"Created table '{table_name}' with schema: {schema_str}")
        
    # Insert data into the table using 'append' mode.
    try:
        conn = sqlite3.connect(db_path)
        df.to_sql(table_name, conn, if_exists="append", index=False)
        conn.close()
        print("Data inserted successfully.")
    except Exception as e:
        logging.error("Error inserting data: %s", e)
        print(f"Error inserting data: {e}")

    return df

def run_basic_query(db_path, table_name, query):
    """
    Run a basic SQL query and return the results.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 csv_to_sqlite_dynamic_conflict_interactive.py <csv_path> <db_path> <table_name>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    db_path = sys.argv[2]
    table_name = sys.argv[3]
    
    if not os.path.exists(csv_path):
        print(f"CSV file '{csv_path}' not found.")
        sys.exit(1)
    
    print(f"Loading CSV file '{csv_path}' into database '{db_path}' with table '{table_name}' with interactive schema conflict handling.")
    load_csv_and_create_table_with_interactive_conflict(csv_path, db_path, table_name)
    
    # Run a basic query and display limited results.
    query = f"SELECT * FROM {table_name} LIMIT 5;"
    rows = run_basic_query(db_path, table_name, query)
    print("Query results:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
