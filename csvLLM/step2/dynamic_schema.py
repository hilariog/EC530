#!/usr/bin/env python3
"""
csv_to_sqlite_dynamic.py

This script loads a CSV file into a SQLite database by dynamically creating
the table based on the CSV schema. It performs the following:
1. Loads a CSV file using pandas.read_csv.
2. Infers each column's SQLite type from the DataFrame's dtypes.
3. Constructs and executes a CREATE TABLE statement dynamically.
4. Inserts the CSV data into the SQLite table using DataFrame.to_sql.
5. Runs a basic query to verify the inserted data.
Usage:
    python3 csv_to_sqlite_dynamic.py <csv_path> <db_path> <table_name>
Example:
    python3 csv_to_sqlite_dynamic.py sample_data.csv example.db data_table
"""

import os
import sys
import sqlite3
import pandas as pd

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
        # Default for object and other types
        return "TEXT"

def infer_schema_from_dataframe(df): #basically just firmat mathces to sql schema definitions by using dtype to sql mapping function
    """
    Infer a SQLite table schema from a pandas DataFrame.
    Returns a string suitable for a CREATE TABLE statement.
    """
    columns = []
    for col in df.columns:
        sql_type = map_dtype_to_sql(df[col].dtype)
        columns.append(f"{col} {sql_type}")
    schema = ", ".join(columns)
    return schema

def create_table_dynamically(db_path, table_name, schema):
    """
    Create a table in SQLite dynamically using the inferred schema.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({schema});"
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()

def load_csv_and_create_table(csv_path, db_path, table_name):
    """
    Loads a CSV file into a DataFrame, infers the table schema,
    creates the table dynamically, and inserts the data.
    """
    # Load CSV file into DataFrame
    df = pd.read_csv(csv_path)
    
    # Infer schema from DataFrame
    schema = infer_schema_from_dataframe(df)
    print(f"Inferred schema for table '{table_name}': {schema}")
    
    # Create table dynamically in SQLite
    create_table_dynamically(db_path, table_name, schema)
    
    # Insert data into the SQLite table (using 'append' since table now exists)
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()
    
    return df

def run_basic_query(db_path, table_name, query):
    """
    Run a basic SQL query against the SQLite database.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 csv_to_sqlite_dynamic.py <csv_path> <db_path> <table_name>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    db_path = sys.argv[2]
    table_name = sys.argv[3]
    
    if not os.path.exists(csv_path):
        print(f"CSV file '{csv_path}' not found.")
        sys.exit(1)
    
    print(f"Loading CSV file '{csv_path}' into database '{db_path}' with table '{table_name}'")
    
    load_csv_and_create_table(csv_path, db_path, table_name)
    
    # Run a basic query: SELECT * FROM table LIMIT 5
    query = f"SELECT * FROM {table_name} LIMIT 5;"
    rows = run_basic_query(db_path, table_name, query)
    print("Query results:")
    for row in rows:
        print(row)

if __name__ == "__main__":
    main()
