This is a project that ultimately aims to offer data entry, storage, and manipulation similar to a cell-type interface like sheets or excel, but through a chat-like UI.

The project is broken up into 5 steps:
Step 1:  Load CSV Files into SQLLite
Step 2:  Create Tables Dynamically from CSV
Step 3:  Handle Schema Conflicts
Step 4:  Simulate AI using input (the input to be schemas)
Step 5:  Add AI to generate SQL

*If using a oython venv:
>>python3 -m venv venv
>>source venv/bin/activate
>>pip install -r requirements.txt

# Step 1:
>> pip install requirements.txt

csv_to_sql.py: This script loads a CSV file into a SQLite database.
It manually creates a table, uses pandas.read_csv to load data,
inserts the data into SQLite via DataFrame.to_sql, and runs a basic query.
>> python3  step1/csv_to_sql.py
run tests
>> python3 step1/tests/test_csv_to_sql.py

# Step 2:
>> pip install requirements.txt 

dynamic_schema.py: This script loads a CSV file into a SQLite database by dynamically creating
the table based on the CSV schema. It performs the following:
1. Loads a CSV file using pandas.read_csv.
2. Infers each column's SQLite type from the DataFrame's dtypes.
3. Constructs and executes a CREATE TABLE statement dynamically.
4. Inserts the CSV data into the SQLite table using DataFrame.to_sql.
5. Runs a basic query to verify the inserted data.
Usage:
>> python3 step2/dynamic_schema.py <csv_path> <db_path> <table_name>
Test:
>> python3 step2/tests/test_dynamic_schema.py
Example:
    python3 step2/dynamic_schema.py sample_data.csv example.db dynamic_table

# Step 3
>> pip install requirements.txt 

schema_conflicts.py: This script loads a CSV file into a SQLite database while handling schema conflicts.
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
Test:
    python3 step3/tests/test_schema_conflicts.py

# Step 4
>> pip install requirements.txt 

simulate_interactive_chat.py: A simple, interactive CLI assistant that simulates an AI.
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

# Step 5
>>pip install requirements.txt

embedded_llm.py: This script enables interactive, plain-language querying of a SQLite database using AI to generate SQL.
It performs the following:
  1. Retrieves the table schema from the SQLite database using PRAGMA.
  2. Prompts the user for a plain‑language request (e.g., "show me all rows where value > 3").
  3. Constructs a prompt that combines the schema with the user request.
  4. Uses Google GenAI (Gemini API) via the google-genai package to generate a valid SQL query.
  5. Optionally displays the generated SQL.
  6. Executes the generated SQL against the database and displays the results.

Usage:
    python3 step5/embedded_llm.py <db_path> <table_name>
    
    Note: right now it uses the table name and schema given in the command line arguments. Alternatively I can changhe this to pass a database and then have a function that gets all tables and schemas in the database for more complex queries about the full db, the user would have to specify a table name in their query.
Test:
    python3 step5/tests/test_embedded_llm.py

Make sure to set your API key in environment:
    export GOOGLE_GENAI_API_KEY=your_api_key_here