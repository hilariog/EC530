#!/usr/bin/env python3
"""
csv_to_sql.py

This script loads a CSV file into a SQLite database.
It manually creates a table, uses pandas.read_csv to load data,
inserts the data into SQLite via DataFrame.to_sql, and runs a basic query.
"""

import os
import sqlite3
import pandas as pd

def create_table_manually(db_path, table_name, schema):#essentially get table shape
    """
    Create a table manually in the SQLite database using the given schema.
    
    Parameters:
        db_path (str): Path to the SQLite database.
        table_name (str): Name of the table to create.
        schema (str): A string defining the schema in SQL.
    """
    conn = sqlite3.connect(db_path) #connect to database
    cursor = conn.cursor()
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});"
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()

def load_csv_to_dataframe(csv_path):
    """
    Load a CSV file into a pandas DataFrame.
    
    Parameters:
        csv_path (str): Path to the CSV file.
    
    Returns:
        DataFrame: A pandas DataFrame containing the CSV data.
    """
    df = pd.read_csv(csv_path)
    return df

def load_dataframe_to_sqlite(df, db_path, table_name, if_exists='replace'):#get table data 
    """
    Insert a pandas DataFrame into a SQLite table.
    
    Parameters:
        df (DataFrame): The DataFrame to insert.
        db_path (str): Path to the SQLite database.
        table_name (str): Name of the target table.
        if_exists (str): Behavior if the table already exists (default 'replace').
    """
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()

def run_basic_query(db_path, table_name, query):
    """
    Run a basic SQL query and return the results.
    
    Parameters:
        db_path (str): Path to the SQLite database.
        table_name (str): Name of the table to query.
        query (str): The SQL query to execute.
    
    Returns:
        list: List of rows returned by the query.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    # Set file names and parameters
    csv_path = "sample_data.csv"
    db_path = "example.db"
    table_name = "data_table"
    
    # Sample schema assumes the CSV has columns: id (INTEGER), name (TEXT), value (REAL)
    sample_schema = "id INTEGER, name TEXT, value REAL"
    
    # Step 1: Manually create the table (if it does not exist)
    create_table_manually(db_path, table_name, sample_schema)
    print(f"Manually created table '{table_name}' in {db_path} (if not already present).")
    
    # Step 2: Load CSV into a DataFrame.
    # If the sample CSV does not exist, create one.
    if not os.path.exists(csv_path):
        sample_data = pd.DataFrame({
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [3.14, 2.71, 1.41]
        })
        sample_data.to_csv(csv_path, index=False)
        print(f"Created sample CSV file: {csv_path}")
    
    df = load_csv_to_dataframe(csv_path)
    print("Loaded CSV into DataFrame:")
    print(df.head())
    
    # Step 3: Insert the DataFrame into SQLite using to_sql.
    load_dataframe_to_sqlite(df, db_path, table_name, if_exists='replace')
    print(f"DataFrame successfully inserted into SQLite table '{table_name}'.")
    
    # Step 4: Run a basic query: SELECT * FROM table LIMIT 5.
    query = f"SELECT * FROM {table_name} LIMIT 5;"
    rows = run_basic_query(db_path, table_name, query)
    print("Query results:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
