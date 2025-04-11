"""
embedded_llm.py

This script enables interactive, plain-language querying of a SQLite database using AI to generate SQL.
It performs the following:
  1. Retrieves the table schema from the SQLite database using PRAGMA.
  2. Prompts the user for a plain‑language request (e.g., "show me all rows where value > 3").
  3. Constructs a prompt that combines the schema with the user request.
  4. Uses Google GenAI (Gemini API) via the google-genai package to generate a valid SQL query.
  5. Optionally displays the generated SQL.
  6. Executes the generated SQL against the database and displays the results.
  7. The CLI continues to run in a loop until the user chooses to exit.

Usage:
    python3 embedded_llm.py <db_path> <table_name>

Make sure to set your API key in environment:
    export GOOGLE_GENAI_API_KEY=your_api_key_here
"""

import os
import sys
import sqlite3
from google import genai

# Set up the Google GenAI client
API_KEY = os.environ.get("GOOGLE_GENAI_API_KEY")
if not API_KEY:
    print("Error: Please set your GOOGLE_GENAI_API_KEY environment variable.")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
MODEL_NAME = "gemini-2.0-flash"  # This is the model name; adjust as needed.

def get_table_schema(db_path, table_name):
    """
    Retrieve the table schema as a human-readable string from a SQLite database.
    Returns a string such as "id INTEGER, name TEXT, value REAL".
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return ""
    
        # Each row: (cid, name, type, notnull, dflt_value, pk)
        schema_items = []
        for row in rows:
            col_name, col_type = row[1], row[2]
            schema_items.append(f"{col_name} {col_type}")
        return ", ".join(schema_items)
    except Exception as e:
        print("Error retrieving schema:", e)
        return ""

def generate_sql_from_prompt(schema, user_request, table_name):
    """
    Construct a prompt using the table schema and the user’s plain-language request,
    then call the Google GenAI API to generate an SQL query.
    
    Returns:
      The generated SQL query as a string.
    """
    prompt = (
        "You are an SQL generation assistant. Given the following table schema for table '"
        f"{table_name}':\n{schema}\n"
        "and the following user request:\n"
        f"{user_request}\n"
        "Generate a valid SQL query for a SQLite database. If the user doesnt specify a table name in the query, ensure the query uses the table name and schema given above"
        f"'{table_name}' exactly. Do not include any commentary."
    )

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )
        # According to the Google GenAI docs, the response.text holds the answer.
        generated_text = response.text.strip()
    
        # A heuristic: if the prompt is echoed back, take the part after the prompt.
        if prompt in generated_text:
            sql_query = generated_text.split(prompt, 1)[1].strip()
        else:
            sql_query = generated_text

        return sql_query
    except Exception as e:
        print("Error generating SQL via GenAI:", e)
        return None

def execute_sql_query(db_path, query):
    """
    Execute the given SQL query against the SQLite database and return the results.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results
    except Exception as e:
        print("Error executing SQL query:", e)
        return None

def clean_sql_query(sql_query: str, table_name: str) -> str:
    """
    Remove markdown formatting and replace placeholder table names with the actual table name.
    """
    sql_query = sql_query.replace("```sql\n", "").replace("sqlite\n", "").replace("```", "").strip()
    sql_query = sql_query.replace("my_table", table_name)
    return sql_query

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 embedded_llm.py <db_path> <table_name>")
        sys.exit(1)

    db_path = sys.argv[1]
    table_name = sys.argv[2]

    # Retrieve the table schema once.
    schema = get_table_schema(db_path, table_name)
    if not schema:
        print(f"Could not find schema for table '{table_name}'.")
        sys.exit(1)
    
    print(f"Table '{table_name}' schema: {schema}\n")

    # Loop until user chooses to exit.
    while True:
        # Prompt the user for a plain-language query.
        user_request = input("Enter your plain-language query (or type 'exit' to quit): ").strip()
        if user_request.lower() in ("exit", "quit"):
            print("Exiting the assistant.")
            break

        print("\nGenerating SQL query from your request...")
        sql_query = generate_sql_from_prompt(schema, user_request, table_name)
        if not sql_query:
            print("Failed to generate SQL query.")
            continue

        sql_query = clean_sql_query(sql_query, table_name)

        print("\nGenerated SQL query:")
        print(sql_query)
        
        confirm = input("\nDo you want to execute this query? (y/n): ").strip().lower()
        if confirm != "y":
            print("Query execution cancelled.")
        else:
            results = execute_sql_query(db_path, sql_query)
            if results is None:
                print("Query execution failed.")
            else:
                print("\nQuery results:")
                if results:
                    for row in results:
                        print(row)
                else:
                    print("No rows returned.")
        
        # Optionally prompt for another query or to exit.
        cont = input("\nWould you like to issue another query? (y/n): ").strip().lower()
        if cont not in ("y", "yes"):
            print("Exiting the assistant.")
            break

if __name__ == "__main__":
    main()