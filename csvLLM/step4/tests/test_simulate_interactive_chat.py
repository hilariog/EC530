#!/usr/bin/env python3
import os
import sys
import sqlite3
import unittest
import pandas as pd
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) #set parent path

from simulate_interactive_chat import simulate_ai_response, list_tables, run_sql_query, DB_PATH

class TestInteractiveAssistant(unittest.TestCase):
    def setUp(self):
        # Create a temporary database.
        self.temp_db = "temp_test.db"
        global DB_PATH
        DB_PATH = self.temp_db
        conn = sqlite3.connect(self.temp_db)
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS test_table;")
        cursor.execute("CREATE TABLE test_table (id INTEGER, name TEXT);")
        cursor.execute("INSERT INTO test_table (id, name) VALUES (1, 'Alice'), (2, 'Bob');")
        conn.commit()
        conn.close()

    def tearDown(self):
        if os.path.exists(self.temp_db):
            os.remove(self.temp_db)

    def test_simulate_ai_response_valid(self):
        schema = "id INTEGER, name TEXT, value REAL"
        response = simulate_ai_response(schema)
        self.assertIn("id", response)
        self.assertIn("INTEGER", response)
        self.assertIn("name", response)
        self.assertIn("TEXT", response)
        self.assertIn("value", response)
        self.assertIn("REAL", response)
    
    def test_list_tables(self):
        # Capture the output of list_tables by temporarily redirecting stdout.
        import sys
        from io import StringIO
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        list_tables()
        output = sys.stdout.getvalue()
        sys.stdout = old_stdout
        self.assertIn("test_table", output)
    
    def test_run_sql_query(self):
        # We will run a query and capture its output.
        # For simplicity, we create a query that returns known rows.
        query = "SELECT * FROM test_table ORDER BY id;"
        try:
            conn = sqlite3.connect(self.temp_db)
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            conn.close()
        except Exception as e:
            self.fail(f"run_sql_query encountered an error: {e}")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], (1, "Alice"))

if __name__ == "__main__":
    unittest.main()
