"""
simulate_interactive_chat.py

A simple, interactive CLI assistant that simulates an AI.
The assistant lets you:
  1. Load a CSV file into a SQLite database.
  2. Run a custom SQL query.
  3. List tables in the SQLite database.
  4. Analyze a schema string (simulate an AI response).
  5. Exit.

It uses pandas to load CSV files and sqlite3 to manage the SQLite database.

Usage:
    python3 step4/interactive_assistant.py
    python3 step4/tests/test_interactive_assistant.py

"""

import os
import sqlite3
import pandas as pd

# Use this constant for our database.
DB_PATH = "assistant.db"

def load_csv_to_db():
    """Prompts user for CSV file path and table name; loads CSV data into the SQLite database."""
    csv_path = input("Enter the path to the CSV file: ").strip()
    if not os.path.exists(csv_path):
        print(f"Error: File '{csv_path}' does not exist.")
        return

    table_name = input("Enter the table name to store data (or press Enter for default 'data_table'): ").strip()
    if not table_name:
        table_name = "data_table"

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Show inferred schema.
    schema_elements = []
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):
            sql_type = "INTEGER"
        elif pd.api.types.is_float_dtype(df[col]):
            sql_type = "REAL"
        elif pd.api.types.is_bool_dtype(df[col]):
            sql_type = "INTEGER"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            sql_type = "DATETIME"
        else:
            sql_type = "TEXT"
        schema_elements.append(f"{col} {sql_type}")
    inferred_schema = ", ".join(schema_elements)
    print(f"\nInferred schema for '{table_name}':")
    print(inferred_schema)
    
    # For simplicity, if table exists, ask if the user wants to overwrite it.
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    exists = cursor.fetchone() is not None
    if exists:
        choice = input(f"Table '{table_name}' already exists. Overwrite? (y/n): ").strip().lower()
        if choice == "y":
            cursor.execute(f"DROP TABLE {table_name};")
            conn.commit()
            print(f"Existing table '{table_name}' dropped.")
        else:
            print("Appending data to the existing table.")
    conn.close()
    
    try:
        # This automatically creates the table if it does not exist.
        conn = sqlite3.connect(DB_PATH)
        df.to_sql(table_name, conn, if_exists="append", index=False)
        conn.close()
        print(f"Data from '{csv_path}' loaded into table '{table_name}'.")
    except Exception as e:
        print(f"Error inserting data into SQLite: {e}")

def run_sql_query():
    """Prompts the user for a SQL query, then executes and prints the results."""
    query = input("Enter your SQL query: ").strip()
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        if results:
            print("Query results:")
            # Print results row by row
            for row in results:
                print(row)
        else:
            print("No results returned or query executed successfully.")
    except Exception as e:
        print(f"Error executing query: {e}")

def list_tables():
    """Lists all tables in the SQLite database using sqlite_master."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        conn.close()
        if tables:
            print("Tables in the database:")
            for (tbl,) in tables:
                print(" -", tbl)
        else:
            print("No tables found in the database.")
    except Exception as e:
        print(f"Error listing tables: {e}")

def simulate_ai_response(schema_input: str) -> str:
    """
    Simulates an AI analysis of the provided schema.
    Splits the schema into column definitions and returns a simple analysis.
    """
    columns = schema_input.split(",")
    columns = [col.strip() for col in columns if col.strip()]
    
    if not columns:
        return "I couldn't detect any valid schema information. Please check your input."

    analysis = "Based on the schema provided, I see the following columns:\n"
    for col in columns:
        parts = col.split()
        if len(parts) >= 2:
            col_name = parts[0]
            col_type = parts[1]
            analysis += f" • Column '{col_name}' of type '{col_type}'\n"
        else:
            analysis += f" • Unrecognized format: {col}\n"
    analysis += "\nWould you like to generate some SQL queries based on this schema?"
    return analysis

def analyze_schema():
    """Prompts the user to input a schema string and simulates an AI response."""
    schema_input = input("Enter a schema description (e.g., 'id INTEGER, name TEXT, value REAL'): ")
    response = simulate_ai_response(schema_input)
    print("\nAI Analysis:")
    print(response)

def main_menu():
    """Main interactive loop for the assistant."""
    print("Welcome to the AI-Assisted SQLite Assistant.")
    print("I can help you load CSV data, run SQL queries, list tables, or even analyze a schema.\n")
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Load a CSV file into the database")
        print("2. Run an SQL query")
        print("3. List all tables in the database")
        print("4. Analyze a schema (simulate AI response)")
        print("5. Exit")
        choice = input("Enter your choice (1-5): ").strip()
        
        if choice == "1":
            load_csv_to_db()
        elif choice == "2":
            run_sql_query()
        elif choice == "3":
            list_tables()
        elif choice == "4":
            analyze_schema()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main_menu()
